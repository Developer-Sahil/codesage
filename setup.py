#!/usr/bin/env python3
"""
Setup script for the AI-Powered Codebase Refactoring Agent (Gemini version).
This script helps users set up the environment and dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_git_installation():
    """Check if Git is installed and accessible."""
    try:
        result = subprocess.run(
            ["git", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(f"✅ Git found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Git not found. GitHub repository cloning will not work.")
        print("Install Git from: https://git-scm.com/downloads")
        return False

def install_dependencies():
    """Install required Python packages."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_env_file():
    """Set up the environment file."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists.")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("📝 Created .env file from .env.example")
        print("⚠️ Please edit .env file and add your GEMINI_API_KEY")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return True
    else:
        # Create a basic .env file
        with open(env_file, 'w') as f:
            f.write("# Google Gemini API Configuration\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
            f.write("\n# Optional: Model configuration\n")
            f.write("# GEMINI_MODEL=gemini-1.5-flash\n")
            f.write("# GEMINI_TEMPERATURE=0.2\n")
        print("📝 Created basic .env file")
        print("⚠️ Please edit .env file and add your GEMINI_API_KEY")
        return True

def run_test():
    """Run a basic test to verify installation."""
    print("\n🧪 Running basic functionality test...")
    try:
        # Test imports
        import google.generativeai as genai
        from dotenv import load_dotenv
        print("✅ All modules imported successfully.")
        
        # Check if .env can be loaded
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ GEMINI_API_KEY not set in .env file")
            print("Please add your API key to continue")
            return False
        else:
            print("✅ Environment configuration loaded.")
            
            # Test API connection (without actually making a call)
            try:
                genai.configure(api_key=api_key)
                print("✅ Gemini API configured successfully.")
                return True
            except Exception as e:
                print(f"⚠️ Could not configure Gemini API: {e}")
                print("Please check your API key")
                return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def display_usage_examples():
    """Display usage examples."""
    print("\n" + "="*50)
    print("📚 Usage Examples:")
    print("="*50)
    print("Basic usage:")
    print("  python main.py /path/to/project")
    print("  python main.py https://github.com/user/repo.git")
    print()
    print("Advanced options:")
    print("  python main.py /path/to/project --model gemini-1.5-pro")
    print("  python main.py /path/to/project --output-dir my_output")
    print("  python main.py /path/to/project --delay 5  # 5 sec delay between calls")
    print("  python main.py /path/to/project --skip-refactoring  # analysis only")
    print()
    print("Model options:")
    print("  • gemini-1.5-flash: Faster, good for most tasks")
    print("  • gemini-1.5-pro: More capable, better for complex refactoring")

def main():
    """Main setup function."""
    print("🚀 AI-Powered Codebase Refactoring Agent Setup (Gemini)")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check Git installation
    check_git_installation()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation.")
        sys.exit(1)
    
    # Setup environment file
    setup_env_file()
    
    # Run basic test
    test_passed = run_test()
    
    # Display usage examples
    display_usage_examples()
    
    print("\n" + "="*60)
    if test_passed:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. ✅ Your GEMINI_API_KEY is configured")
        print("2. Run: python main.py --help")
        print("3. Try analyzing a project: python main.py /path/to/project")
    else:
        print("⚠️ Setup completed with warnings.")
        print("Please check the issues above and resolve them.")
        print("\nTo get your Gemini API key:")
        print("1. Visit: https://aistudio.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Add it to your .env file: GEMINI_API_KEY=your_key_here")
        
    print("\n🆘 If you need help:")
    print("• Check the README.md file")
    print("• Make sure you have a valid Gemini API key")
    print("• For rate limits, use --delay parameter or process smaller codebases")

if __name__ == "__main__":
    main()