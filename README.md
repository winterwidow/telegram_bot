# Data Analyst Telegram Bot

A Telegram bot that answers data-analysis questions through aipipe and returns structured JSON responses with execution log links.

## Features

- Handles plain-text Telegram messages and ignores commands.
- Uses aipipe chat completions with the `gpt-4.1-mini` model.
- Returns JSON shaped as:

```json
{
  "answer": "...",
  "log_url": "..."
}
```

- Keeps per-user session logs in memory and writes them to `logs/<user_id>.jsonl`.
- Writes an aggregate `run.jsonl` public log for the full bot run.
- Supports local polling mode in `bot.py`.
- Supports webhook deployment in `server.py`.
- Can auto-configure the Telegram webhook on startup when a public URL is available.
- Can verify incoming webhook requests with `TELEGRAM_WEBHOOK_SECRET`.
- Exposes health and log endpoints for deployment monitoring.
- Can publish `run.jsonl` to GitHub when GitHub credentials are configured.
- Includes a keepalive pinger to reduce idle timeouts on hosted platforms.

## Project Structure

```text
telegram_bot/
├── bot.py
├── server.py
├── requirements.txt
├── setup.py
├── test_bot.py
├── Dockerfile
├── render.yaml
├── README.md
└── logs/
```

## How It Works

1. A user sends a plain-text question in Telegram.
2. The bot logs the message with a timestamp.
3. The question is sent to AIpipe (ChatGPT) for analysis.
4. The model is instructed to return JSON only.
5. The bot saves the response, updates JSONL logs, and returns the final JSON payload.

## Log Format

Each user log is JSONL, one JSON object per line. This is automatically updated in the GitHub repository.

```json
{"timestamp":"2024-01-15T10:30:45","type":"user_question","content":"What is 2+2?"}
{"timestamp":"2024-01-15T10:30:46","type":"agent_response","content":"{\"answer\":\"4\",\"log_url\":\"https://example.com/logs/123.jsonl\"}"}
```

## Testing

The bot is called from Telegram: @n_data_bot


## License

This project is provided as-is for the IITM Data Science program.
