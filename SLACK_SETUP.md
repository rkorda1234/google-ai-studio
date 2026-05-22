# Slack Bot Setup Guide

Follow these steps once and you'll be able to type `/campaign` in Slack to generate full marketing campaigns.

---

## Step 1 — Create a Slack App

1. Go to **https://api.slack.com/apps**
2. Click **"Create New App"**
3. Choose **"From scratch"**
4. Name it: `Campaign Generator`
5. Pick your Slack workspace → click **"Create App"**

---

## Step 2 — Enable Socket Mode

Socket Mode means no public URL or server is needed — the bot connects outward to Slack.

1. In the left sidebar click **"Socket Mode"**
2. Toggle it **ON**
3. It will ask you to create an App-Level Token:
   - Token name: `campaign-bot-token`
   - Add scope: `connections:write`
   - Click **"Generate"**
4. **Copy the token** — it starts with `xapp-` — save it for later

---

## Step 3 — Add Bot Permissions

1. In the left sidebar click **"OAuth & Permissions"**
2. Scroll down to **"Bot Token Scopes"** and add these:

| Scope | Why |
|-------|-----|
| `chat:write` | Post messages |
| `chat:write.public` | Post in channels without joining |
| `commands` | Handle slash commands |
| `im:write` | Send DMs to users |
| `channels:read` | Read channel list |
| `files:write` | Upload campaign files to Slack |

3. Scroll back up and click **"Install to Workspace"**
4. **Copy the Bot User OAuth Token** — it starts with `xoxb-`

---

## Step 4 — Add the Slash Command

1. In the left sidebar click **"Slash Commands"**
2. Click **"Create New Command"**
3. Fill in:
   - **Command:** `/campaign`
   - **Request URL:** `https://placeholder.com` *(Socket Mode ignores this)*
   - **Short Description:** `Generate a full marketing campaign`
   - **Usage Hint:** `[business description]`
4. Click **"Save"**

---

## Step 5 — Enable Event Subscriptions (for `help` message)

1. In the left sidebar click **"Event Subscriptions"**
2. Toggle **ON**
3. Under **"Subscribe to bot events"** add: `message.im`
4. Click **"Save Changes"**
5. Reinstall the app if prompted

---

## Step 6 — Get Your Signing Secret

1. In the left sidebar click **"Basic Information"**
2. Scroll to **"App Credentials"**
3. Copy the **Signing Secret**

---

## Step 7 — Configure Your .env File

Open the `.env` file in the project folder and fill in:

```
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
SLACK_BOT_TOKEN=xoxb-YOUR_BOT_TOKEN
SLACK_APP_TOKEN=xapp-YOUR_APP_TOKEN
SLACK_SIGNING_SECRET=YOUR_SIGNING_SECRET
```

Also fill in your other keys (GHL, Meta, Google Ads, n8n) for live integrations.
The bot works without them in demo mode.

---

## Step 8 — Run the Bot

### Option A: On your computer

```bash
# Install dependencies (one time)
pip install -r requirements.txt

# Start the bot
python -m slack_bot.app
```

You'll see: `🤖 Campaign Generator Bot starting (Socket Mode)…`

### Option B: Keep it running 24/7 (Railway / Render / any server)

1. Push the repo to GitHub
2. Go to **https://railway.app** (free tier available)
3. Create new project → Deploy from GitHub repo
4. Add your environment variables in Railway's dashboard
5. Set the start command to: `python -m slack_bot.app`
6. Deploy — it stays running forever

---

## Step 9 — Use It!

In any Slack channel (or DM to the bot), type:

```
/campaign
```

A form pops up. Fill it in, click **Generate 🚀** and the bot will:
- Post a progress update in your DMs
- Update it as each step completes
- Post the full campaign summary when done (3–5 min)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `/campaign` not found | Reinstall the app to your workspace after adding the command |
| Bot doesn't respond | Check that `SLACK_APP_TOKEN` starts with `xapp-` and `SLACK_BOT_TOKEN` starts with `xoxb-` |
| Generation fails | Check `ANTHROPIC_API_KEY` is valid — run `python main.py research` to test |
| No DM from bot | Make sure `im:write` scope is added and app is reinstalled |
