#!/usr/bin/env python3
"""
Test client for the Data Analyst Telegram Bot.
Tests the bot's ability to handle questions and return valid JSON responses.
"""

import json
import os
import sys
import requests
from pathlib import Path

AIPIPE_API_URL = "https://aipipe.org/openai/v1/chat/completions"
AIPIPE_MODEL = "gpt-4.1-mini"


def load_env():
    """Load environment variables from .env file."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Run 'python setup.py' first.")
        return False
    
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()
    
    return True


def test_api_connection():
    """Test if aipipe API token is valid."""
    print("\n" + "="*60)
    print("  Testing API Connections")
    print("="*60)
    
    # Test aipipe connection
    print("\n1️⃣  Testing aipipe API...")
    aipipe_token = os.getenv("AIPIPE_TOKEN")
    
    if not aipipe_token:
        print("❌ AIPIPE_TOKEN not set in .env")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {aipipe_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": AIPIPE_MODEL,
            "max_tokens": 100,
            "messages": [{"role": "user", "content": "Say 'Hello' in JSON format only: {\"message\": \"Hello\"}"}]
        }
        
        # Try to reach aipipe API
        response = requests.post(
            AIPIPE_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ aipipe API connection successful!")
            return True
        else:
            print(f"❌ aipipe API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ aipipe API error: {e}")
        return False


def test_question_processing():
    """Test the bot's ability to process and answer questions."""
    print("\n" + "="*60)
    print("  Testing Question Processing")
    print("="*60)
    
    aipipe_token = os.getenv("AIPIPE_TOKEN")
    if not aipipe_token:
        print("❌ AIPIPE_TOKEN not set")
        return False
    
    test_questions = [
        "What is 2 + 2?",
        "Classify the state 'Tamil Nadu' as 'South' or 'North': answer in JSON",
        "What is the capital of France?",
    ]
    
    print("\nTesting questions:")
    all_passed = True
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: \"{question}\"")
        
        system_prompt = """You are a data analyst AI. Answer the question and return ONLY a valid JSON object:
{
  "answer": "your answer here",
  "log_url": "https://example.com/logs/123.jsonl"
}
Do not include any other text, markdown, or code blocks."""
        
        try:
            headers = {
                "Authorization": f"Bearer {aipipe_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": AIPIPE_MODEL,
                "max_tokens": 500,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ]
            }
            
            response = requests.post(
                AIPIPE_API_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ❌ API error: {response.status_code}")
                all_passed = False
                continue
            
            response_data = response.json()
            response_text = (
                response_data
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            
            # Try to parse as JSON
            try:
                json_response = json.loads(response_text)
                
                # Validate JSON structure
                if "answer" in json_response and "log_url" in json_response:
                    print(f"   ✅ Valid response")
                    print(f"      Answer: {json_response['answer']}")
                    print(f"      Log URL: {json_response['log_url']}")
                else:
                    print(f"   ⚠️  Missing required keys")
                    print(f"      Response: {json_response}")
                    all_passed = False
                    
            except json.JSONDecodeError:
                print(f"   ❌ Invalid JSON response")
                print(f"      Response: {response_text[:200]}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    return all_passed


def test_log_structure():
    """Test JSONL log file creation."""
    print("\n" + "="*60)
    print("  Testing Log Structure")
    print("="*60)
    
    print("\nCreating test log file...")
    
    os.makedirs("logs", exist_ok=True)
    
    test_logs = [
        {
            "timestamp": "2024-01-15T10:30:45.123456",
            "type": "user_question",
            "content": "What is 2+2?"
        },
        {
            "timestamp": "2024-01-15T10:30:46.234567",
            "type": "agent_response",
            "content": '{"answer": "4", "log_url": "https://example.com/logs/123.jsonl"}'
        }
    ]
    
    try:
        log_file = "logs/test_123456.jsonl"
        with open(log_file, "w") as f:
            for log in test_logs:
                f.write(json.dumps(log) + "\n")
        
        # Verify the file
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        if len(lines) == 2:
            print(f"✅ JSONL log structure is valid")
            print(f"   File: {log_file}")
            print(f"   Lines: {len(lines)}")
            return True
        else:
            print(f"❌ JSONL log structure is incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Error creating log file: {e}")
        return False


def print_summary(results):
    """Print test summary."""
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your bot is ready to deploy.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  Data Analyst Bot - Test Suite")
    print("="*60)
    
    # Load environment
    if not load_env():
        return 1
    
    print("\n✅ Environment loaded from .env")
    
    results = {}
    
    # Run tests
    results["API Connection"] = test_api_connection()
    results["Question Processing"] = test_question_processing()
    results["Log Structure"] = test_log_structure()
    
    # Print summary
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
