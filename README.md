# Data Analyst Telegram Bot 

A Telegram bot that uses ChatGPT to answer data-analysis questions and reply with JSON responses containing answers and execution logs.

## Project Structure

```
data-analyst-bot/
├── bot.py                 # Main bot (polling mode for local testing)
├── server.py              # Flask server (for webhook/production)
├── requirements.txt       # Python dependencies
├── setup.py               # Interactive setup script
├── test_bot.py            # Test suite
├── Dockerfile             # Docker configuration
├── .env.example           # Example environment variables
└── README.md              # This file
```

---

## How It Works

1. **User sends a question** via Telegram
   - Example: "Classify state Assam as North/South"

2. **Bot receives the message** and logs it

3. **ChatGPT processes** the question
   - Analyzes data
   - Computes results
   - Formats response as JSON

4. **Bot returns JSON** with two keys:
   ```json
   {
     "answer": "North",
     "log_url": "https://your-domain.com/logs/123456.jsonl"
   }
   ```

5. **Execution logs stored** as JSONL (JSON Lines)
   - One JSON object per line
   - Includes timestamps, question, and response

---

## Testing

### 1 Clone/Setup the Project
```bash
# Create a new directory
mkdir data-analyst-bot
cd data-analyst-bot

# Initialize git (for version control)
git init

# Copy all the provided files into this directory
# - bot.py
# - server.py
# - requirements.txt
# - .env.example
# - Dockerfile
```

### 2 Create Environment File
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
```

Your `.env` should look like:
```
TELEGRAM_BOT_TOKEN=YOUR TOKEN
OPENAI_API_KEY=YOUR API KEY
LOG_SERVER_URL=http://localhost:5000
PORT=5000
```

### 2.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 2.4 Run the Bot Locally (Polling Mode)
```bash
python bot.py
```

The bot will now poll Telegram for messages. Test it by:
1. Finding your bot on Telegram (search for its username)
2. Send it a message like: "What is 2+2?"
3. The bot should reply with a JSON object

---

Tests:
- ✅ API connections 
- ✅ Question processing
- ✅ JSON response format
- ✅ Log file structure

---

## Example Responses

### Data Classification
**Question**: "Is Assam a Northeast state?"
```json
{
  "answer": "Yes",
  "log_url": "https://your-domain.com/logs/123456.jsonl"
}
```

### Calculation
**Question**: "What is 2 + 2?"
```json
{
  "answer": "4",
  "log_url": "https://your-domain.com/logs/123456.jsonl"
}
```

### State Analysis
**Question**: "List all states in South India"
```json
{
  "answer": ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana", "Kerala"],
  "log_url": "https://your-domain.com/logs/123456.jsonl"
}
```

---

## API Documentation

### Incoming Message Format
Telegram sends plain text to the bot.

### Response Format
Must return exactly:
```json
{
  "answer": "<solution shaped as question asks>",
  "log_url": "<public URL to JSONL logs>"
}
```

### Log Format (JSONL)
```
{"timestamp": "2024-01-15T10:30:45", "type": "user_question", "content": "..."}
{"timestamp": "2024-01-15T10:30:46", "type": "agent_response", "content": "..."}
```

---
## License

This project is provided as-is for the IITM Data Science program.