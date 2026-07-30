import json
import logging
import os
import threading
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

session_logs = {}

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
aipipe_token = os.getenv("AIPIPE_TOKEN")
public_url = (
    os.getenv("WEBHOOK_URL")
    or os.getenv("RENDER_EXTERNAL_URL")
    or os.getenv("LOG_SERVER_URL")
    or "http://localhost:5000"
).rstrip("/")
log_server_url = public_url
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
keepalive_enabled = os.getenv("KEEPALIVE_ENABLED", "true").lower() == "true"
keepalive_interval = int(os.getenv("KEEPALIVE_INTERVAL_SECONDS", "600"))

AIPIPE_API_URL = "https://aipipe.org/openai/v1/chat/completions"


def send_telegram_message(chat_id: int, text: str) -> dict:
    """Send a Telegram message using the Bot API."""
    response = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def delete_telegram_message(chat_id: int, message_id: int) -> None:
    """Delete a Telegram message if the bot is allowed to."""
    response = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/deleteMessage",
        json={"chat_id": chat_id, "message_id": message_id},
        timeout=20,
    )
    if not response.ok:
        logger.info("Could not delete Telegram message: %s", response.text)


def handle_text_message(user_id: int, chat_id: int, question: str) -> None:
    """Handle incoming messages and respond with data analysis."""
    try:
        logger.info("User %s asked: %s", user_id, question)

        if user_id not in session_logs:
            session_logs[user_id] = []

        session_logs[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": "user_question",
            "content": question,
        })

        thinking_msg = send_telegram_message(chat_id, "Analyzing your question...")
        response = analyze_question(question, user_id)

        session_logs[user_id].append({
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response",
            "content": response,
        })

        save_session_logs(user_id)

        try:
            response_json = json.loads(response)
        except json.JSONDecodeError:
            response_json = {
                "answer": response,
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
            }

        if "log_url" not in response_json:
            response_json["log_url"] = f"{log_server_url}/logs/{user_id}.jsonl"

        try:
            message_id = thinking_msg.get("result", {}).get("message_id")
            if message_id:
                delete_telegram_message(chat_id, message_id)
        except Exception:
            pass

        send_telegram_message(chat_id, json.dumps(response_json, indent=2))
    except Exception as e:
        logger.error("Error handling message: %s", e)
        try:
            send_telegram_message(chat_id, f"Error: {str(e)}")
        except Exception:
            pass


def analyze_question(question: str, user_id: int) -> str:
    """Use aipipe to analyze the data question and return JSON response."""
    system_prompt = """You are a data analyst AI assistant. Your job is to:
1. Receive a data analysis question
2. Analyze the question and provide a solution
3. Return ONLY a valid JSON object with exactly these keys:
   - "answer": your solution (shaped exactly as the question asks for)
   - "log_url": the URL to your execution logs

The answer should be technically accurate and directly address the question.
For classification/prediction tasks, provide the result in the format requested.
For state analysis, provide structured output (state names, metrics, etc.).
For data queries, provide the data in the requested format.

Return ONLY valid JSON. Do not include any markdown, code blocks, or extra text."""

    try:
        headers = {
            "Authorization": f"Bearer {aipipe_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-4.1-mini",
            "max_tokens": 2048,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        }

        response = requests.post(
            AIPIPE_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != 200:
            logger.error("aipipe API error: %s - %s", response.status_code, response.text)
            return json.dumps({
                "answer": f"Error: API returned {response.status_code}",
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
            })

        response_data = response.json()
        response_text = (
            response_data
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not response_text:
            logger.error("Empty response from aipipe API")
            return json.dumps({
                "answer": "Error: Empty response from API",
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
            })

        try:
            json.loads(response_text)
        except json.JSONDecodeError:
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                response_text = json.dumps({
                    "answer": response_text,
                    "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
                })

        return response_text
    except requests.exceptions.Timeout:
        logger.error("aipipe API request timeout")
        return json.dumps({
            "answer": "Error: API request timeout",
            "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
        })
    except Exception as e:
        logger.error("Error calling aipipe API: %s", e)
        return json.dumps({
            "answer": f"Error processing question: {str(e)}",
            "log_url": f"{log_server_url}/logs/{user_id}.jsonl",
        })


def save_session_logs(user_id: int) -> str:
    """Save session logs to a JSONL file."""
    os.makedirs("logs", exist_ok=True)
    log_file_path = f"logs/{user_id}.jsonl"

    with open(log_file_path, "w") as f:
        for log_entry in session_logs[user_id]:
            f.write(json.dumps(log_entry) + "\n")

    return log_file_path


def process_telegram_update(data: dict) -> None:
    """Process one Telegram webhook update."""
    message = data.get("message") or data.get("edited_message")
    if not message:
        logger.info("Ignoring update without message")
        return

    question = message.get("text")
    if not question or question.startswith("/"):
        logger.info("Ignoring unsupported update type")
        return

    user_id = message.get("from", {}).get("id")
    chat_id = message.get("chat", {}).get("id")
    if not user_id or not chat_id:
        logger.info("Ignoring message without user_id or chat_id")
        return

    handle_text_message(user_id, chat_id, question)


@app.route(webhook_path, methods=["POST"])
def webhook():
    """Handle incoming Telegram updates via webhook."""
    try:
        if webhook_secret:
            received_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if received_secret != webhook_secret:
                return jsonify({"ok": False, "error": "unauthorized"}), 401

        data = request.get_json()
        if not data:
            return jsonify({"ok": False, "error": "empty update"}), 400

        process_telegram_update(data)
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error("Error processing webhook: %s", e)
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/logs/<int:user_id>.jsonl", methods=["GET"])
def get_logs(user_id: int):
    """Serve JSONL logs for a user."""
    log_file_path = f"logs/{user_id}.jsonl"

    if not os.path.exists(log_file_path):
        return jsonify({"error": "Logs not found"}), 404

    try:
        return send_file(
            log_file_path,
            mimetype="application/jsonl",
            as_attachment=True,
            download_name=f"{user_id}.jsonl",
        )
    except Exception as e:
        logger.error("Error serving logs: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "webhook": f"{public_url}{webhook_path}"}), 200


@app.route("/logs", methods=["GET"])
def list_logs():
    """List all available logs."""
    os.makedirs("logs", exist_ok=True)
    log_files = os.listdir("logs")
    return jsonify({"logs": log_files}), 200


def configure_telegram_webhook() -> None:
    """Register this Render web service as Telegram's webhook target."""
    if not telegram_token or public_url.startswith("http://localhost"):
        logger.info("Skipping webhook setup until TELEGRAM_BOT_TOKEN and public URL are configured")
        return

    webhook_url = f"{public_url}{webhook_path}"
    payload = {
        "url": webhook_url,
        "allowed_updates": json.dumps(["message"]),
    }
    if webhook_secret:
        payload["secret_token"] = webhook_secret

    response = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/setWebhook",
        data=payload,
        timeout=20,
    )
    response.raise_for_status()
    logger.info("Telegram webhook configured: %s", webhook_url)


def start_keepalive_pinger() -> None:
    """Ping the public health endpoint periodically while the process is alive."""
    if not keepalive_enabled or public_url.startswith("http://localhost"):
        return

    def ping_loop():
        health_url = f"{public_url}/health"
        while True:
            time.sleep(keepalive_interval)
            try:
                requests.get(health_url, timeout=15)
                logger.info("Keepalive ping sent to %s", health_url)
            except Exception as e:
                logger.warning("Keepalive ping failed: %s", e)

    thread = threading.Thread(target=ping_loop, daemon=True)
    thread.start()


if telegram_token:
    try:
        configure_telegram_webhook()
    except Exception as e:
        logger.warning("Could not configure Telegram webhook on startup: %s", e)
    start_keepalive_pinger()


def main():
    """Main entry point for Flask server."""
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    if not aipipe_token:
        raise ValueError("AIPIPE_TOKEN environment variable not set")

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
