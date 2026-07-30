# aipipe Integration Guide

## Changes Made

All code has been updated to use your **aipipe token** instead of direct Anthropic API access.

---

## What Changed?

### 1. **Environment Variables**

**Before:**
```bash
ANTHROPIC_API_KEY=sk-ant-v1-xxxxx
```

**After:**
```bash
AIPIPE_TOKEN=your_aipipe_token
```

### 2. **Python Packages**

**Removed:**
- `anthropic==0.32.1` (no longer needed)

**Still Required:**
- `requests==2.31.0` (for making HTTP calls to aipipe)

Update via:
```bash
pip install -r requirements.txt
```

### 3. **Code Changes**

#### bot.py
- Removed: `from anthropic import Anthropic`
- Added: `import requests`
- Changed: API calls now use HTTP POST to aipipe endpoint
- Updated: Authentication uses Bearer token in headers

#### server.py
- Same changes as bot.py
- Flask server now forwards requests to aipipe API

#### setup.py
- Updated: Now asks for "aipipe API token" instead of "Anthropic API key"
- Changed: No validation of token format (accepts any non-empty string)

#### test_bot.py
- Updated: API connection test now calls aipipe endpoint
- Changed: Uses HTTP requests instead of Anthropic SDK

#### .env.example
- Changed: Shows `AIPIPE_TOKEN=` instead of `ANTHROPIC_API_KEY=`

#### requirements.txt
- Removed: `anthropic==0.32.1`
- Kept: `requests==2.31.0` (already there for HTTP calls)

---

## How It Works Now

### Request Flow

```
User (Telegram)
    ↓
Bot (bot.py or server.py)
    ↓
aipipe API (via HTTP POST with Bearer token)
    ↓
Claude Model
    ↓
JSON Response
    ↓
Telegram User
```

### API Endpoint

All requests go to:
```
POST https://api.aipipe.io/v1/messages
```

### Headers

```python
headers = {
    "Authorization": f"Bearer {AIPIPE_TOKEN}",
    "Content-Type": "application/json"
}
```

### Payload Format

```python
{
    "model": "claude-opus-4-1",
    "max_tokens": 2048,
    "system": "Your system prompt...",
    "messages": [
        {
            "role": "user",
            "content": "User question..."
        }
    ]
}
```

---

## Setup Instructions

### Step 1: Get Your aipipe Token

You already have this! Keep it safe.

### Step 2: Run Setup

```bash
python setup.py
```

Enter:
- **Telegram Bot Token**: From @BotFather
- **aipipe Token**: Your aipipe token (the one you already have)

This creates `.env` file with:
```
TELEGRAM_BOT_TOKEN=your_telegram_token
AIPIPE_TOKEN=your_aipipe_token
LOG_SERVER_URL=http://localhost:5000
PORT=5000
```

### Step 3: Test

```bash
python test_bot.py
```

This will:
- ✅ Test aipipe API connection
- ✅ Test question processing
- ✅ Test JSON response format

### Step 4: Run

```bash
python bot.py
```

---

## Key Differences

| Aspect | Before (Direct API) | After (aipipe) |
|--------|-------------------|----------------|
| Authentication | Direct API key | Bearer token |
| Endpoint | Anthropic servers | aipipe proxy |
| Library | `anthropic` SDK | `requests` HTTP |
| Setup | Anthropic key | aipipe token |
| Response Parsing | SDK handles it | Manual JSON parse |

---

## Troubleshooting

### "aipipe API error: 401"
- Check your aipipe token is correct
- Verify token is not expired
- Token should be set in AIPIPE_TOKEN env var

### "aipipe API error: 429"
- Rate limit hit
- Wait a moment and retry
- Check your aipipe account limits

### "Empty response from API"
- aipipe returned no content
- Check if your token allows this model
- Try with a simpler question first

### "API request timeout"
- aipipe taking too long
- Network issue
- Try again - may be temporary

### "AIPIPE_TOKEN not set"
- Run `python setup.py` to create .env
- Or manually set: `export AIPIPE_TOKEN=your_token`

---

## File-by-File Changes

### bot.py (~10% changed)
- Imports: Removed `Anthropic`, added `requests`
- Class init: Changed parameter from `anthropic_api_key` to `aipipe_token`
- `_analyze_question()`: Complete rewrite to use HTTP requests
- `main()`: Changed env var from `ANTHROPIC_API_KEY` to `AIPIPE_TOKEN`

### server.py (~10% changed)
- Same changes as bot.py
- Global init: Uses `aipipe_token` instead of client

### setup.py (~5% changed)
- Prompt for aipipe token instead of Anthropic API key
- Token validation simplified (any non-empty string)
- .env file generation updated

### test_bot.py (~15% changed)
- Imports: Changed from Anthropic to requests
- `test_api_connection()`: Now calls aipipe endpoint
- `test_question_processing()`: Updated to use HTTP requests

### requirements.txt (1 line changed)
- Removed: `anthropic==0.32.1`

### .env.example (1 line changed)
- Changed: ANTHROPIC_API_KEY → AIPIPE_TOKEN

---

## Complete Working Example

```python
import requests
import json

AIPIPE_TOKEN = "your_aipipe_token"
AIPIPE_API_URL = "https://api.aipipe.io/v1/messages"

def ask_question(question):
    headers = {
        "Authorization": f"Bearer {AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "claude-opus-4-1",
        "max_tokens": 2048,
        "system": "You are a data analyst. Return only JSON.",
        "messages": [{"role": "user", "content": question}]
    }
    
    response = requests.post(AIPIPE_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        answer = data["content"][0]["text"]
        return json.loads(answer)
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
result = ask_question("What is 2+2?")
print(result)
# Output: {"answer": "4", "log_url": "..."}
```

---

## API Response Format

aipipe returns:
```json
{
  "content": [
    {
      "type": "text",
      "text": "{\"answer\": \"...\", \"log_url\": \"...\"}"
    }
  ],
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 50
  }
}
```

The bot automatically extracts the `text` field and parses the JSON.

---

## Verification Checklist

After setup, verify:

- [ ] .env file exists with AIPIPE_TOKEN
- [ ] `python test_bot.py` passes all tests
- [ ] `python bot.py` runs without errors
- [ ] Bot responds on Telegram with JSON
- [ ] Logs are saved to logs/ folder
- [ ] JSONL log format is correct

---

## Support

If you encounter issues:

1. Check that aipipe token is valid
2. Run `python test_bot.py` for detailed error info
3. Check logs in `logs/` folder
4. Verify network connectivity to `api.aipipe.io`
5. Review the error messages for specific guidance

---

## Summary

✅ All code updated to use aipipe  
✅ No Anthropic SDK dependency  
✅ Simpler HTTP-based approach  
✅ Ready to deploy  

You're all set! Just run `python setup.py` with your aipipe token.
