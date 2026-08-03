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

### Manual Testing
1. Send the bot a message
2. Verify response is valid JSON
3. Check if logs are accessible on GitHub

### Automated Testing
```bash
python test_bot.py
```

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