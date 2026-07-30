# Data Analyst Telegram Bot - Complete Setup Guide

## Overview
This is a production-ready Telegram bot that uses Claude AI to answer data-analysis questions and reply with JSON responses containing the answer and a URL to execution logs.

## Prerequisites
- Python 3.9+
- Telegram Bot Token (from BotFather)
- Anthropic API Key
- Git account (for hosting the code)
- Server/hosting for deployment (Replit, Railway, Heroku, or your own VPS)

---

## Part 1: Getting Your Credentials

### 1.1 Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/start` and follow instructions
3. Send `/newbot` to create a new bot
4. Give it a name and username (must end with `_bot`)
5. BotFather will give you a token like: `123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh`
6. **Save this token securely**

### 1.2 Get Your Anthropic API Key
1. Go to https://console.anthropic.com
2. Sign in or create an account
3. Navigate to "API Keys"
4. Create a new API key
5. **Copy and save it securely**

---

## Part 2: Local Setup (Testing)

### 2.1 Clone/Setup the Project
```bash
# Create a new directory
mkdir data-analyst-bot
cd data-analyst-bot

# Initialize git (optional, for version control)
git init

# Copy all the provided files into this directory
# - bot.py
# - server.py
# - requirements.txt
# - .env.example
# - Dockerfile
# - SETUP_GUIDE.md
```

### 2.2 Create Environment File
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials
# Use your favorite editor (nano, vim, etc.)
nano .env
```

Your `.env` should look like:
```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh
ANTHROPIC_API_KEY=sk-ant-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
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

## Part 3: Deployment Options

### Option A: Replit (Easiest for Beginners)

1. **Create a Replit Account**
   - Go to https://replit.com
   - Sign up with GitHub or email

2. **Create a New Replit**
   - Click "Create" → "Python"
   - Give it a name

3. **Upload Your Code**
   - Click the file icon on the left
   - Upload these files:
     - `bot.py`
     - `server.py`
     - `requirements.txt`
     - `.env` (with your real credentials)

4. **Set Secrets (Safe Way to Store Credentials)**
   - Click the lock icon on the left sidebar
   - Add secrets:
     - `TELEGRAM_BOT_TOKEN` = your token
     - `ANTHROPIC_API_KEY` = your key
     - `LOG_SERVER_URL` = your Replit URL (see step 6)

5. **Create run.sh**
   - Create a file called `run.sh`:
   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   python server.py
   ```

6. **Click "Run"**
   - Replit will show you a URL like `https://my-bot.username.repl.co`
   - This is your `LOG_SERVER_URL`

7. **Update Telegram Webhook** (Optional, for faster response)
   - If you want to use webhook instead of polling:
   ```bash
   curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"https://my-bot.username.repl.co/webhook\"}"
   ```

---

### Option B: Railway (Recommended)

1. **Create a Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "Create New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your repository with the bot code

3. **Set Environment Variables**
   - In Railway dashboard, go to "Variables"
   - Add:
     - `TELEGRAM_BOT_TOKEN` = your token
     - `ANTHROPIC_API_KEY` = your key
     - `LOG_SERVER_URL` = your Railway domain
     - `PORT` = 5000

4. **Deploy**
   - Railway automatically deploys on push to GitHub
   - Go to "Settings" → "Domains" to get your public URL

5. **Set Telegram Webhook**
   ```bash
   curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
     -H "Content-Type: application/json" \
     -d "{\"url\": \"https://your-railway-domain.up.railway.app/webhook\"}"
   ```

---

### Option C: Docker (For VPS/Self-Hosting)

1. **Build the Docker Image**
   ```bash
   docker build -t data-analyst-bot .
   ```

2. **Run the Container**
   ```bash
   docker run -d \
     -e TELEGRAM_BOT_TOKEN="your_token" \
     -e ANTHROPIC_API_KEY="your_key" \
     -e LOG_SERVER_URL="https://your-domain.com" \
     -e PORT=5000 \
     -p 5000:5000 \
     -v ./logs:/app/logs \
     --name data-analyst-bot \
     data-analyst-bot
   ```

3. **Check Logs**
   ```bash
   docker logs -f data-analyst-bot
   ```

---

## Part 4: GitHub Setup (Required for Grading)

### 4.1 Create GitHub Repository

1. Go to https://github.com/new
2. Create a repository named `my_data_bot` (or similar)
3. Make it **PUBLIC** (important for graders)

### 4.2 Push Your Code

```bash
# Initialize git if you haven't
git init
git add .
git commit -m "Initial commit: Data Analyst Telegram Bot"

# Add your GitHub repo as remote
git remote add origin https://github.com/YOUR_USERNAME/my_data_bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

Your repo structure should look like:
```
my_data_bot/
├── bot.py
├── server.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── SETUP_GUIDE.md
└── logs/
```

---

## Part 5: Testing Before Submission

### 5.1 Test Questions
The grading system will send questions like:

**Example 1: Simple Calculation**
```
What is the sum of 15 and 25?
```

**Expected Response:**
```json
{
  "answer": "40",
  "log_url": "https://your-domain.com/logs/123456789.jsonl"
}
```

**Example 2: State Classification**
```
Classify the state Assam as 'Northeast' or 'Other'
```

**Expected Response:**
```json
{
  "answer": "Northeast",
  "log_url": "https://your-domain.com/logs/123456789.jsonl"
}
```

### 5.2 Manual Testing
1. Send your bot a message on Telegram
2. Verify the response is valid JSON
3. Check that `log_url` is publicly accessible
4. Download the JSONL logs and verify the format

### 5.3 Verify Log Format
JSONL files should look like:
```
{"timestamp": "2024-01-15T10:30:45.123456", "type": "user_question", "content": "What is 2+2?"}
{"timestamp": "2024-01-15T10:30:46.234567", "type": "agent_response", "content": "{\"answer\": \"4\", \"log_url\": \"...\"}"}
```

---

## Part 6: Submit for Grading

When you're ready, register on the assignment form with:
1. **GitHub Repo URL**: `https://github.com/YOUR_USERNAME/my_data_bot`
2. **Telegram Bot Username**: `@your_bot_name` (must end with `_bot`)

Example:
- GitHub: `https://github.com/naija/my_data_bot`
- Telegram: `@my_data_analyzer_bot`

---

## Troubleshooting

### Bot Not Responding
- Check that TELEGRAM_BOT_TOKEN is correct
- Verify the bot is running: `ps aux | grep bot.py`
- Check logs: `cat logs/*.jsonl`

### Invalid JSON Response
- Ensure Claude's response is wrapped in JSON
- Check that `log_url` key exists
- Look at the bot logs for parsing errors

### Can't Access Logs
- Verify the log file exists in `logs/` directory
- Check the URL is publicly accessible
- Ensure `LOG_SERVER_URL` matches your actual domain

### API Rate Limiting
- Add delays between requests if needed
- Check Anthropic dashboard for usage

### Environment Variables Not Loading
- Ensure `.env` file exists in the same directory
- Use `export $(cat .env | grep -v '#' | xargs)` before running
- Or set them manually: `export TELEGRAM_BOT_TOKEN="..."`

---

## Security Notes
⚠️ **Important:**
- Never commit `.env` to GitHub (use `.env.example` instead)
- Keep API keys secret - use environment variables or platform secrets
- Make the GitHub repo public for grading, but keep credentials private
- Rotate API keys if compromised

---

## Additional Resources
- Telegram Bot API: https://core.telegram.org/bots/api
- Anthropic API Docs: https://docs.anthropic.com
- Railway Docs: https://docs.railway.app
- Replit Docs: https://docs.replit.com

---

## Support
If you encounter issues:
1. Check the troubleshooting section above
2. Review logs in `logs/` directory
3. Verify all environment variables are set correctly
4. Test locally with `python bot.py` first before deploying
