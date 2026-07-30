# aipipe Quick Start

## What Changed?

✅ **Now using aipipe token** instead of Anthropic API key  
✅ **All code updated** - no changes needed by you  
✅ **Ready to use** - just provide your token  

---

## 3-Step Setup

### Step 1: Run Setup
```bash
python setup.py
```

When prompted:
- **Telegram Bot Token**: Get from @BotFather (`/newbot`)
- **aipipe Token**: Enter your aipipe token (you already have this)

### Step 2: Test
```bash
python test_bot.py
```

Should see: ✅ All tests passed

### Step 3: Deploy
```bash
python bot.py
```

Test on Telegram, then deploy to cloud.

---

## Environment Variables

**Old:**
```bash
ANTHROPIC_API_KEY=sk-ant-v1-xxxxx
```

**New:**
```bash
AIPIPE_TOKEN=your_aipipe_token
```

---

## Updated Files

| File | Change |
|------|--------|
| bot.py | Uses aipipe API (HTTP requests) |
| server.py | Uses aipipe API (HTTP requests) |
| setup.py | Asks for aipipe token |
| test_bot.py | Tests aipipe connection |
| .env.example | AIPIPE_TOKEN instead of ANTHROPIC_API_KEY |
| requirements.txt | Removed anthropic SDK |

---

## API Details

```
Endpoint: https://api.aipipe.io/v1/messages
Method: POST
Auth: Bearer token in header
Response: JSON with Claude's answer
```

---

## Example Request

```python
import requests

headers = {
    "Authorization": f"Bearer {AIPIPE_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "model": "claude-opus-4-1",
    "max_tokens": 2048,
    "messages": [{"role": "user", "content": "What is 2+2?"}]
}

response = requests.post(
    "https://api.aipipe.io/v1/messages",
    headers=headers,
    json=payload
)

answer = response.json()["content"][0]["text"]
```

---

## Key Points

✅ Use your aipipe token directly  
✅ No more Anthropic SDK dependency  
✅ Same Claude models available  
✅ Same JSON response format  
✅ Ready for deployment  

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| `AIPIPE_TOKEN not set` | Run `python setup.py` |
| `API error 401` | Check token is correct |
| `API error 429` | Rate limited - wait & retry |
| `Empty response` | Check token permissions |

---

## That's It!

Your bot now uses aipipe. Everything else stays the same:
- Same project structure
- Same bot functionality
- Same JSON responses
- Same deployment options

Just run: `python setup.py` with your aipipe token

Ready to go! 🚀
