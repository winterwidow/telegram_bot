# Quick Reference Card - Data Analyst Bot

## 🚀 Get Started in 4 Steps

```bash
# Step 1: Setup (creates .env)
python setup.py

# Step 2: Test
python test_bot.py

# Step 3: Run locally
python bot.py

# Step 4: Deploy
# See SETUP_GUIDE.md for Replit/Railway/Docker
```

---

## 📋 Essential Commands

| Command | Purpose | When |
|---------|---------|------|
| `python setup.py` | Create .env file | First time setup |
| `python test_bot.py` | Run test suite | Before deployment |
| `python bot.py` | Run bot locally | Local testing |
| `pip install -r requirements.txt` | Install dependencies | If needed |
| `git push origin main` | Push to GitHub | Before deployment |

---

## 🔑 Where to Get Credentials

| Credential | Source | Format |
|-----------|--------|--------|
| Telegram Bot Token | @BotFather on Telegram | `123456789:ABCdefGHIjklmno...` |
| Anthropic API Key | https://console.anthropic.com | `sk-ant-v1-xxxxxxxxxxxxx` |
| Bot Username | You create it | Must end with `_bot` |
| Server URL | Your deployment domain | `https://your-domain.com` |

---

## 📝 .env File Template

```bash
TELEGRAM_BOT_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_api_key_here
LOG_SERVER_URL=http://localhost:5000
PORT=5000
```

---

## ✅ Before Submitting

- [ ] `python test_bot.py` passes all tests
- [ ] Bot responds with valid JSON on Telegram
- [ ] Logs are accessible at log_url
- [ ] GitHub repo is PUBLIC
- [ ] `.env` NOT in GitHub (use .gitignore)
- [ ] All files present in repo
- [ ] Deployed to cloud (Replit/Railway)

---

## 🎯 Expected JSON Response

```json
{
  "answer": "Your solution here",
  "log_url": "https://your-domain.com/logs/123456789.jsonl"
}
```

**Keys must be exact:**
- `"answer"` - The solution
- `"log_url"` - Public URL to JSONL logs

---

## 📊 Expected Log Format (JSONL)

One JSON object per line:
```
{"timestamp": "2024-01-15T10:30:45", "type": "user_question", "content": "What is 2+2?"}
{"timestamp": "2024-01-15T10:30:46", "type": "agent_response", "content": "{\"answer\": \"4\", ...}"}
```

---

## 🌐 Deployment Options Quick Comparison

| Platform | Setup Time | Cost | Skill Level |
|----------|-----------|------|------------|
| **Replit** | 5 min | Free | Beginner |
| **Railway** | 10 min | Free tier | Intermediate |
| **Docker** | 15 min | Varies | Advanced |

**Recommended for beginners:** Replit or Railway

---

## 🔧 Troubleshooting Cheat Sheet

| Problem | Solution |
|---------|----------|
| `No module named 'anthropic'` | `pip install -r requirements.txt` |
| `TELEGRAM_BOT_TOKEN not set` | Run `python setup.py` |
| `Invalid JSON response` | Run `python test_bot.py` to debug |
| `Bot not responding` | Check `.env` has correct token |
| `Can't access logs` | Verify `LOG_SERVER_URL` is correct |

---

## 📁 File Checklist for GitHub

```
✅ bot.py
✅ server.py
✅ requirements.txt
✅ setup.py
✅ test_bot.py
✅ Dockerfile
✅ README.md
✅ SETUP_GUIDE.md
✅ FILES_SUMMARY.md
✅ .env.example
✅ .gitignore
❌ .env (DO NOT COMMIT)
❌ logs/ (DO NOT COMMIT)
```

---

## 🎓 Grading Requirements

Your submission needs:

1. **Public GitHub Repository**
   - Contains all bot code
   - URL format: `https://github.com/USERNAME/repo-name`

2. **Active Telegram Bot**
   - Username ends with `_bot`
   - Responds to messages
   - Returns valid JSON

3. **Working Logs**
   - JSONL format
   - Publicly accessible via log_url
   - Contains timestamps and responses

4. **Correct JSON Format**
   - Exactly two keys: `answer` and `log_url`
   - No extra keys or formatting

---

## 💡 Pro Tips

1. **Use Replit or Railway** - Easier than Docker
2. **Test locally first** - Catch errors early
3. **Read the logs** - Logs show exactly what went wrong
4. **Keep .env private** - Use environment variables in production
5. **Test JSON format** - Use `python test_bot.py`

---

## 📞 Quick Help

**Bot not working?**
1. Check `.env` file exists
2. Run `python test_bot.py`
3. Check bot logs in `logs/` folder

**Need to deploy?**
1. Push to GitHub
2. Choose platform (Replit/Railway)
3. Follow steps in SETUP_GUIDE.md

**Ready to submit?**
1. Verify all tests pass
2. Check GitHub is public
3. Register on the grading form

---

## 🔗 Important Links

- Telegram Bot Docs: https://core.telegram.org/bots
- Anthropic Docs: https://docs.anthropic.com
- Replit: https://replit.com
- Railway: https://railway.app
- GitHub: https://github.com

---

## 📈 Success Checklist

```
Setup Phase:
  ✅ Credentials obtained (Telegram + Anthropic)
  ✅ python setup.py runs successfully
  ✅ .env file created

Testing Phase:
  ✅ python test_bot.py passes all tests
  ✅ Bot responds on Telegram
  ✅ Response is valid JSON

Deployment Phase:
  ✅ Code pushed to GitHub
  ✅ Bot deployed to cloud
  ✅ Logs accessible at log_url

Submission Phase:
  ✅ GitHub repo public
  ✅ Bot username confirmed
  ✅ Ready for grading
```

---

## 🎉 You're Ready!

If you can check all items in the success checklist above, you're ready to submit.

**Estimated time:** 20-30 minutes start to finish

**Next step:** Run `python setup.py`

Good luck! 🚀
