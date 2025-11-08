#!/usr/bin/env python3
"""
Test script to check which models are available with your API keys.
Supports: OpenAI GPT, Anthropic Claude, Grok
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ===============================
# OpenAI GPT Test
# ===============================
def test_openai_models():
    import openai

    openai_api_key = os.getenv("OPENAI_API_KEY")
    model_names = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ]

    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    openai.api_key = openai_api_key
    print("\n🤖 Testing OpenAI GPT models...")
    for model in model_names:
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'Model working correctly.'"}],
                temperature=0
            )
            output = response.choices[0].message.content.strip()
            print(f"✅ {model}: Working | Response: {output}")
        except Exception as e:
            print(f"❌ {model}: {e}")

# ===============================
# Anthropic Claude Test
# ===============================
def test_claude_models():
    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    model_names = [
        "claude-3",
        "claude-3-100k",
        "claude-3-sonnet-20240229"
    ]

    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return

    client = anthropic.Anthropic(api_key=api_key)
    print("\n🤖 Testing Anthropic Claude models...")
    for model in model_names:
        try:
            response = client.completions.create(
                model=model,
                prompt="Say 'Model working correctly.'",
                max_tokens_to_sample=20
            )
            output = response.completion.strip()
            print(f"✅ {model}: Working | Response: {output}")
        except Exception as e:
            print(f"❌ {model}: {e}")

# ===============================
# Grok / Groq Test
# ===============================
def test_grok_models():
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    model_names = [
        "grok-4-latest",
        "grok-3.5",
        "grok-3-latest",
        "grok-4-fast-reasoning"
    ]

    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return

    client = Groq(api_key=api_key)
    print("\n🤖 Testing Grok models...")
    for model in model_names:
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'Model working correctly.'"}]
            )
            output = completion.choices[0].message.content.strip()
            print(f"✅ {model}: Working | Response: {output}")
        except Exception as e:
            print(f"❌ {model}: {e}")

# ===============================
# Main
# ===============================
if __name__ == "__main__":
    print("="*50)
    print("🎯 Model Connectivity Test")
    print("="*50)

    test_openai_models()
    test_claude_models()
    test_grok_models()
