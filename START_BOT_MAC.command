#!/bin/bash
# Double-click this file on Mac to start the Campaign Generator Slack bot.
# First time only: you may need to right-click → Open to bypass Gatekeeper.

cd "$(dirname "$0")"

echo "======================================"
echo "  Campaign Generator Bot — Starting"
echo "======================================"

# Install dependencies if needed
if ! python3 -c "import slack_bolt" 2>/dev/null; then
  echo "Installing dependencies (first time only)..."
  pip3 install -r requirements.txt
fi

# Check .env exists
if [ ! -f .env ]; then
  echo "ERROR: .env file not found."
  echo "Copy .env.example to .env and fill in your tokens."
  read -p "Press Enter to close..."
  exit 1
fi

echo ""
echo "Bot is running! Go to Slack and type /campaign"
echo "Press Ctrl+C to stop."
echo ""

python3 -m slack_bot.app
