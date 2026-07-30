# Data Analyst Telegram Bot 🤖

A production-ready Telegram bot that uses Claude AI to answer data-analysis questions and reply with JSON responses containing answers and execution logs.

## Quick Start (5 minutes)

### 1. Get Your Credentials
- **Telegram Bot Token**: Message `@BotFather` on Telegram → `/newbot` → save the token
- **Anthropic API Key**: Get from https://console.anthropic.com → "API Keys"

### 2. Run Setup
```bash
python setup.py
```
This will interactively create your `.env` file with all configuration.

### 3. Test Locally
```bash
python bot.py
```
Then message your bot on Telegram and verify it responds with JSON.

### 4. Run Tests
```bash
python test_bot.py
```

### 5. Deploy
See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed deployment instructions:
- **Easiest**: Replit (1 click)
- **Recommended**: Railway (GitHub integration)
- **Advanced**: Docker (self-hosted VPS)

---

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
├── SETUP_GUIDE.md         # Detailed setup guide
└── README.md              # This file
```

---

## How It Works

1. **User sends a question** via Telegram
   - Example: "Classify state Assam as North/South"

2. **Bot receives the message** and logs it

3. **Claude AI processes** the question
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

## Configuration

Edit `.env` with:
```bash
# Your Telegram bot token
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh

# Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-v1-xxxxxxxxxxxxx

# Your deployment URL
LOG_SERVER_URL=http://localhost:5000
PORT=5000
```

---

## Deployment Options

### Local Testing
```bash
python bot.py
```
Uses polling (slower but requires no setup)

### Production with Webhook
```bash
python server.py
```
Uses Flask + webhook (faster, requires public URL)

### Replit (Recommended for Beginners)
1. Create account at https://replit.com
2. Create new Python project
3. Upload all files
4. Add secrets: TELEGRAM_BOT_TOKEN, ANTHROPIC_API_KEY
5. Click "Run"

### Railway
1. Push code to GitHub
2. Connect to Railway
3. Add environment variables
4. Deploy automatically

### Docker
```bash
docker build -t data-analyst-bot .
docker run -e TELEGRAM_BOT_TOKEN="..." -e ANTHROPIC_API_KEY="..." -p 5000:5000 data-analyst-bot
```

---

## Testing

### Manual Testing
1. Send your bot a message
2. Verify response is valid JSON
3. Check logs are accessible

### Automated Testing
```bash
python test_bot.py
```

Tests:
- ✅ API connections (Anthropic)
- ✅ Question processing
- ✅ JSON response format
- ✅ Log file structure

---

## Required Files for Grading

When submitting, ensure your GitHub repository contains:
- `bot.py` - Main bot code
- `server.py` - Server for production
- `requirements.txt` - Dependencies
- `.env.example` - Configuration template
- `README.md` - Documentation

Register with:
- **GitHub Repo URL**: `https://github.com/YOUR_USERNAME/my_data_bot`
- **Telegram Bot Username**: `@your_bot_name_bot`

---

## Troubleshooting

**Bot not responding?**
- Check TELEGRAM_BOT_TOKEN is correct
- Verify bot is running: `ps aux | grep bot.py`
- Check logs in `logs/` directory

**Invalid JSON responses?**
- Verify API key works: `python test_bot.py`
- Check Claude is formatting response correctly
- Look for errors in logs

**Can't access logs?**
- Verify `log_url` is publicly accessible
- Check LOG_SERVER_URL in `.env`
- Ensure server.py is running if using Flask

**API errors?**
- Verify Anthropic API key is valid
- Check you have API credits
- Review API documentation

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
**Question**: "List all states in the South region"
```json
{
  "answer": ["Tamil Nadu", "Karnataka", "Andhra Pradesh", "Telangana"],
  "log_url": "https://your-domain.com/logs/123456.jsonl"
}
```

---

## API Documentation

### Incoming Message Format
Telegram sends plain text to your bot.

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

## Security

- Never commit `.env` to GitHub
- Use environment variables for secrets
- Keep API keys private
- Use `.env.example` for templates
- Rotate keys if compromised

---

## Performance Tips

- Claude Opus 4.1 is recommended for accuracy
- Response time: ~2-5 seconds typically
- Logs are stored locally and served over HTTP
- Use caching for repeated questions

---

## Support

- **Telegram Bot Docs**: https://core.telegram.org/bots
- **Anthropic API**: https://docs.anthropic.com
- **Railway Docs**: https://docs.railway.app
- **Replit Docs**: https://docs.replit.com

---

## License

This project is provided as-is for the IITM Data Science program.

---

## Next Steps

1. ✅ Run `python setup.py`
2. ✅ Test with `python test_bot.py`
3. ✅ Deploy to your platform
4. ✅ Register on the grading form
5. ✅ Wait for grading!

Good luck! 🚀
