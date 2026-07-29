import os
import json
import logging
from flask import Flask, request, send_file, jsonify
from datetime import datetime
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import requests
import threading
import io
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Global state
session_logs = {}
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
aipipe_token = os.getenv("AIPIPE_TOKEN")
log_server_url = os.getenv("LOG_SERVER_URL", "http://localhost:5000")

# aipipe configuration
AIPIPE_API_URL = "https://aipipe.org/openai/v1/chat/completions"

# Initialize Telegram application
application = None


def init_telegram_app():
    """Initialize the Telegram bot application."""
    global application
    if application is None:
        application = Application.builder().token(telegram_token).build()
    return application


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages and respond with data analysis."""
    try:
        user_id = update.effective_user.id
        question = update.message.text
        
        logger.info(f"User {user_id} asked: {question}")
        
        # Initialize session log for this user if needed
        if user_id not in session_logs:
            session_logs[user_id] = []
        
        # Log the incoming question
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "user_question",
            "content": question
        }
        session_logs[user_id].append(log_entry)
        
        # Send a thinking message
        thinking_msg = await update.message.reply_text("🤔 Analyzing your question...")
        
        # Get response from Claude
        response = analyze_question(question, user_id)
        
        # Log the agent's response
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_response",
            "content": response
        }
        session_logs[user_id].append(log_entry)
        
        # Save logs to file
        save_session_logs(user_id)
        
        # Parse the response as JSON
        try:
            response_json = json.loads(response)
        except json.JSONDecodeError:
            response_json = {
                "answer": response,
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
            }
        
        # Ensure log_url is set
        if "log_url" not in response_json:
            response_json["log_url"] = f"{log_server_url}/logs/{user_id}.jsonl"
        
        # Send the response
        try:
            await thinking_msg.delete()
        except:
            pass
        
        await update.message.reply_text(
            json.dumps(response_json, indent=2),
            parse_mode=None
        )
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        try:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        except:
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
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4.1-mini",
            "max_tokens": 2048,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
        
        response = requests.post(
            AIPIPE_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"aipipe API error: {response.status_code} - {response.text}")
            return json.dumps({
                "answer": f"Error: API returned {response.status_code}",
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
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
                "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
            })
        
        # Ensure it's valid JSON
        try:
            json.loads(response_text)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                response_text = json.dumps({
                    "answer": response_text,
                    "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
                })
        
        return response_text
        
    except requests.exceptions.Timeout:
        logger.error("aipipe API request timeout")
        return json.dumps({
            "answer": "Error: API request timeout",
            "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
        })
    except Exception as e:
        logger.error(f"Error calling aipipe API: {e}")
        return json.dumps({
            "answer": f"Error processing question: {str(e)}",
            "log_url": f"{log_server_url}/logs/{user_id}.jsonl"
        })


def save_session_logs(user_id: int) -> str:
    """Save session logs to a JSONL file."""
    os.makedirs("logs", exist_ok=True)
    log_file_path = f"logs/{user_id}.jsonl"
    
    with open(log_file_path, "w") as f:
        for log_entry in session_logs[user_id]:
            f.write(json.dumps(log_entry) + "\n")
    
    return log_file_path


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming Telegram updates via webhook."""
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        
        # Add message handler to application
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        
        # Process the update
        await application.process_update(update)
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
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
            download_name=f"{user_id}.jsonl"
        )
    except Exception as e:
        logger.error(f"Error serving logs: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/logs", methods=["GET"])
def list_logs():
    """List all available logs."""
    os.makedirs("logs", exist_ok=True)
    log_files = os.listdir("logs")
    return jsonify({"logs": log_files}), 200


def main():
    """Main entry point for Flask server."""
    if not telegram_token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
    if not aipipe_token:
        raise ValueError("AIPIPE_TOKEN environment variable not set")
    
    # Initialize Telegram app
    init_telegram_app()
    
    # Start Flask server
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
