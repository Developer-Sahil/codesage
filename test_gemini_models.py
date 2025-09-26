#!/usr/bin/env python3
"""
Test script to check which Gemini models are available with your API key.
Run this before using the main application to ensure model compatibility.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def test_gemini_models():
    """Test available Gemini models with your API key."""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        print("Please set your API key in .env file")
        return False
    
    # Configure Gemini
    genai.configure(api_key=api_key)
    
    print("🔍 Testing available Gemini models...")
    print("=" * 50)
    
    # List of models to test (Google AI Studio compatible names)
    # Updated model list to test:
    models_to_test = [
    "models/gemini-2.5-flash", 
    "models/gemini-2.5-flash-lite",
    "models/gemini-pro-latest", 
    "models/gemini-1.5-flash-8b"
    ]
    
    working_models = []
    failed_models = []
    
    for model_name in models_to_test:
        try:
            print(f"\n🧪 Testing: {model_name}")
            
            # Create model instance
            model = genai.GenerativeModel(model_name)
            
            # Test with a simple prompt
            response = model.generate_content(
                "Hello! Please respond with just 'Model working correctly.'",
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 20,
                }
            )
            
            if response.text:
                print(f"✅ {model_name}: Working")
                print(f"   Response: {response.text.strip()}")
                working_models.append(model_name)
            else:
                print(f"⚠️ {model_name}: No response received")
                failed_models.append(model_name)
                
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"❌ {model_name}: Model not found")
            elif "403" in error_msg:
                print(f"❌ {model_name}: Access denied")
            elif "quota" in error_msg.lower():
                print(f"❌ {model_name}: Quota exceeded")
            else:
                print(f"❌ {model_name}: {error_msg}")
            failed_models.append(model_name)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print("=" * 50)
    
    if working_models:
        print("✅ Working models:")
        for model in working_models:
            print(f"   • {model}")
        print(f"\n🎯 Recommended: Use '{working_models[0]}' in your config")
    else:
        print("❌ No working models found!")
        print("Possible issues:")
        print("   • Invalid API key")
        print("   • API key doesn't have access to these models") 
        print("   • Quota exceeded")
        print("   • Geographic restrictions")
    
    if failed_models:
        print("\n❌ Failed models:")
        for model in failed_models:
            print(f"   • {model}")
    
    return len(working_models) > 0

def list_available_models():
    """List all models available through the API."""
    try:
        print("\n🔍 Querying all available models...")
        models = genai.list_models()
        
        print("📋 All available models:")
        for model in models:
            print(f"   • {model.name}")
            if hasattr(model, 'display_name'):
                print(f"     Display name: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"     Description: {model.description}")
            print()
            
    except Exception as e:
        print(f"⚠️ Could not list models: {e}")

if __name__ == "__main__":
    print("🤖 Gemini Model Compatibility Test")
    print("=" * 50)
    
    success = test_gemini_models()
    
    if success:
        print("\n🎉 At least one model is working!")
        print("You can now use the refactoring agent.")
    else:
        print("\n💡 Troubleshooting steps:")
        print("1. Verify your API key at: https://aistudio.google.com/app/apikey")
        print("2. Check if your API key has the necessary permissions")
        print("3. Ensure you haven't exceeded your quota")
        print("4. Try creating a new API key")
    
    # Try to list all available models
    list_available_models()