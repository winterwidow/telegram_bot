import json
import logging
import os
import threading
import time
import base64
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
run_log_lock = threading.Lock()
pending_run_entries = []

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
aipipe_token = os.getenv("AIPIPE_TOKEN")
public_url = (
    os.getenv("WEBHOOK_URL")
    or os.getenv("RENDER_EXTERNAL_URL")
    or os.getenv("LOG_SERVER_URL")
    or "http://localhost:5000"
).rstrip("/")
log_url = os.getenv("LOG_URL", f"{public_url}/run.jsonl").rstrip("/")
webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
keepalive_enabled = os.getenv("KEEPALIVE_ENABLED", "true").lower() == "true"
keepalive_interval = int(os.getenv("KEEPALIVE_INTERVAL_SECONDS", "600"))
github_token = os.getenv("GITHUB_TOKEN")
github_repo = os.getenv("GITHUB_REPO", "winterwidow/telegram_bot")
github_branch = os.getenv("GITHUB_BRANCH", "main")
github_log_path = os.getenv("GITHUB_LOG_PATH", "run.jsonl")
github_contents_url = f"https://api.github.com/repos/{github_repo}/contents/{github_log_path}"

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

        user_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "type": "user_question",
            "content": question,
        }
        session_logs[user_id].append(user_entry)
        append_run_log(user_entry)

        thinking_msg = send_telegram_message(chat_id, "Analyzing your question...")
        response = analyze_question(question, user_id)

        response_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "type": "agent_response",
            "content": response,
        }
        session_logs[user_id].append(response_entry)
        append_run_log(response_entry)

        save_session_logs(user_id)
        publish_run_log()

        response_json = build_final_reply(response)

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


def build_final_reply(response: str) -> dict:
    """Return the required two-key answer and public JSONL log URL."""
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        parsed = {"answer": response}

    if isinstance(parsed, dict) and "answer" in parsed and len(parsed) <= 2:
        answer = parsed["answer"]
    else:
        answer = parsed
    return {"answer": answer, "log_url": log_url}


def analyze_question(question: str, user_id: int) -> str:
    """Use aipipe to analyze the data question and return JSON response."""
    system_prompt = f"""You are a data analyst AI assistant. Your job is to:
1. Receive a data analysis question
2. Analyze the question and provide a solution
3. Return ONLY a valid JSON object with exactly these two keys:
   - "answer": the answer, shaped exactly as the user requests
   - "log_url": "{log_url}"

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
            return json.dumps({"error": f"API returned {response.status_code}"})

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
            return json.dumps({"error": "Empty response from API"})

        try:
            json.loads(response_text)
        except json.JSONDecodeError:
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                response_text = json.dumps({"answer": response_text})

        return response_text
    except requests.exceptions.Timeout:
        logger.error("aipipe API request timeout")
        return json.dumps({"error": "API request timeout"})
    except Exception as e:
        logger.error("Error calling aipipe API: %s", e)
        return json.dumps({"error": f"Error processing question: {str(e)}"})


def save_session_logs(user_id: int) -> str:
    """Save session logs to a JSONL file."""
    os.makedirs("logs", exist_ok=True)
    log_file_path = f"logs/{user_id}.jsonl"

    with open(log_file_path, "w") as f:
        for log_entry in session_logs[user_id]:
            f.write(json.dumps(log_entry) + "\n")

    return log_file_path


def append_run_log(entry: dict) -> None:
    """Append one JSON object to the stable public run log."""
    os.makedirs("logs", exist_ok=True)
    with run_log_lock, open("run.jsonl", "a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        pending_run_entries.append(entry)


def publish_run_log() -> None:
    """Append pending log entries to the public GitHub JSONL file."""
    if not github_token:
        return

    with run_log_lock:
        if not pending_run_entries:
            return

        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {github_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            params = {"ref": github_branch}
            existing = requests.get(
                github_contents_url, headers=headers, params=params, timeout=20
            )

            sha = None
            existing_text = ""
            if existing.status_code == 200:
                existing_data = existing.json()
                sha = existing_data.get("sha")
                existing_text = base64.b64decode(
                    existing_data.get("content", "").replace("\n", "")
                ).decode("utf-8")
            elif existing.status_code != 404:
                existing.raise_for_status()

            new_lines = "".join(
                json.dumps(entry, ensure_ascii=False) + "\n"
                for entry in pending_run_entries
            )
            content = existing_text + new_lines
            payload = {
                "message": "Update bot run log",
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "branch": github_branch,
            }
            if sha:
                payload["sha"] = sha

            response = requests.put(
                github_contents_url, headers=headers, json=payload, timeout=30
            )
            response.raise_for_status()
            pending_run_entries.clear()
            logger.info("Published %s log entries to GitHub", len(new_lines.splitlines()))
        except Exception as e:
            logger.warning("Could not publish run log to GitHub: %s", e)


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


@app.route("/run.jsonl", methods=["GET"])
def get_run_log():
    """Serve the aggregate JSONL run log as a public downloadable file."""
    os.makedirs("logs", exist_ok=True)
    path = "run.jsonl"
    if not os.path.exists(path):
        open(path, "a", encoding="utf-8").close()
    return send_file(path, mimetype="application/jsonl", as_attachment=False,
                     download_name="run.jsonl")


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "ok", "health": f"{public_url}/health", "log_url": log_url}), 200


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
