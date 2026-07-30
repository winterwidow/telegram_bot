# Render Web Service Deployment

This bot can run on Render's free web service plan by using Telegram webhooks instead of background polling.

## 1. Push the repo to GitHub

Commit these files and push them to a GitHub repository.

## 2. Create a Render web service

In Render, create a new **Web Service** from the GitHub repository.

If Render detects `render.yaml`, use the blueprint settings. Otherwise use:

```bash
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 server:app
```

## 3. Set environment variables

Set these in Render:

```bash
TELEGRAM_BOT_TOKEN=your_botfather_token
AIPIPE_TOKEN=your_aipipe_token
WEBHOOK_URL=https://your-render-service-name.onrender.com
TELEGRAM_WEBHOOK_SECRET=any-long-random-string
KEEPALIVE_ENABLED=true
KEEPALIVE_INTERVAL_SECONDS=600
```

`WEBHOOK_URL` must be the public Render URL without a trailing slash.

## 4. Deploy

On startup, `server.py` calls Telegram's `setWebhook` API automatically:

```text
https://your-render-service-name.onrender.com/webhook
```

You can verify the service is up at:

```text
https://your-render-service-name.onrender.com/health
```

## Keepalive note

The app includes an internal pinger that calls `/health` every 10 minutes while the process is running. For better reliability on Render free services, also add an external monitor such as UptimeRobot or Better Stack to ping:

```text
https://your-render-service-name.onrender.com/health
```

every 5 minutes.
