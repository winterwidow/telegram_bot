#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the bot in polling mode
echo "Starting bot in polling mode..."
python bot.py
