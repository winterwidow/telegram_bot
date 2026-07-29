#!/usr/bin/env python3
"""
Quick setup script for the Data Analyst Telegram Bot.
Run this to interactively configure your bot.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def get_input(prompt, default=None):
    """Get user input with optional default."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    value = input(prompt).strip()
    return value or default


def create_env_file():
    """Create .env file interactively."""
    print_header("Data Analyst Telegram Bot - Setup")
    
    print("\n📝 Let's configure your bot. You'll need:")
    print("  1. Telegram Bot Token (from @BotFather)")
    print("  2. Anthropic API Key (from console.anthropic.com)")
    print("  3. Server URL (your deployment domain)")
    
    # Get Telegram Token
    print("\n" + "-"*60)
    print("Step 1: Telegram Bot Token")
    print("-"*60)
    telegram_token = get_input(
        "Enter your Telegram bot token (from @BotFather)\n"
        "Format: 123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh"
    )
    
    if not telegram_token or ":" not in telegram_token:
        print("❌ Invalid token format. Please try again.")
        return False
    
    # Get aipipe Token
    print("\n" + "-"*60)
    print("Step 2: aipipe API Token")
    print("-"*60)
    aipipe_key = get_input(
        "Enter your aipipe API token (your token from aipipe)"
    )
    
    if not aipipe_key or len(aipipe_key) < 10:
        print("❌ Invalid token. Please try again.")
        return False
    
    # Get Server URL
    print("\n" + "-"*60)
    print("Step 3: Server Configuration")
    print("-"*60)
    print("\nChoose your deployment method:")
    print("  1. Local testing (http://localhost:5000)")
    print("  2. Replit (https://your-bot.username.repl.co)")
    print("  3. Railway (https://your-bot.up.railway.app)")
    print("  4. Custom domain")
    
    deployment = get_input("Choose (1-4)", "1")
    
    if deployment == "1":
        log_url = "http://localhost:5000"
        port = "5000"
    elif deployment == "2":
        log_url = get_input("Enter your Replit URL\nFormat: https://your-bot.username.repl.co")
        port = "5000"
    elif deployment == "3":
        log_url = get_input("Enter your Railway domain\nFormat: https://your-bot.up.railway.app")
        port = "5000"
    elif deployment == "4":
        log_url = get_input("Enter your custom domain\nFormat: https://your-domain.com")
        port = get_input("Enter port number", "5000")
    else:
        log_url = "http://localhost:5000"
        port = "5000"
    
    # Create .env file
    print("\n" + "-"*60)
    print("Creating .env file...")
    print("-"*60)
    
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN={telegram_token}

# aipipe API Configuration
AIPIPE_TOKEN={aipipe_key}

# Server Configuration
LOG_SERVER_URL={log_url}
PORT={port}

# Deployment
FLASK_ENV=production
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    # Install dependencies
    print("\n" + "-"*60)
    print("Installing dependencies...")
    print("-"*60)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
        else:
            print("⚠️  Some dependencies failed to install. Try manual install:")
            print(f"   pip install -r requirements.txt")
    except Exception as e:
        print(f"⚠️  Could not auto-install dependencies: {e}")
        print("   Please run: pip install -r requirements.txt")
    
    # Print next steps
    print("\n" + "="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    if deployment == "1":
        print("\n  1. Test locally:")
        print("     python bot.py")
        print("\n  2. Send your bot a message on Telegram")
        print("  3. Verify the response is valid JSON")
    else:
        print("\n  1. Push your code to GitHub:")
        print("     git init")
        print("     git add .")
        print("     git commit -m 'Initial commit'")
        print("     git remote add origin https://github.com/YOUR_USERNAME/my_data_bot.git")
        print("     git push -u origin main")
        print("\n  2. Deploy to your platform (Replit/Railway/etc)")
        print("\n  3. Test by sending your bot a message on Telegram")
    
    print("\n📚 For more help, see: SETUP_GUIDE.md")
    print("\n" + "="*60)
    
    return True


if __name__ == "__main__":
    try:
        success = create_env_file()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
