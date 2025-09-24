#!/usr/bin/env python3
"""
CodeSage Backend Setup Script
Helps users set up and verify the CodeSage installation.
"""

import os
import sys
import subprocess


def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"Error: Python 3.7+ required. Current version: {sys.version}")
        return False
    print(f"Python version: {sys.version.split()[0]} - OK")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    
    try:
        # Install basic requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "aiohttp>=3.8.0"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Core dependencies installed successfully")
        else:
            print(f"Warning: Failed to install dependencies: {result.stderr}")
            print("You may need to install manually: pip install aiohttp")
    
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("Please install manually: pip install -r requirements.txt")


def check_files():
    """Check if all required files exist."""
    required_files = [
        'main.py',
        'filewalker.py', 
        'analyzer.py',
        'refactorer.py',
        'quickstart.py',
        'test.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"Found: {file}")
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        print("Please ensure all CodeSage files are in the current directory.")
        return False
    
    return True


def setup_environment():
    """Help user set up environment variables."""
    print("\nEnvironment Setup:")
    
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print("GROQ_API_KEY is set - AI features will be available")
    else:
        print("GROQ_API_KEY not found")
        print("To enable AI features:")
        print("  Linux/Mac: export GROQ_API_KEY='your_key_here'")
        print("  Windows: set GROQ_API_KEY=your_key_here")
        print("  Or add to your shell profile for persistence")
    
    # Create workspace directory
    workspace = "./codesage_workspace"
    if not os.path.exists(workspace):
        os.makedirs(workspace)
        print(f"Created workspace directory: {workspace}")


def run_tests():
    """Run the test suite."""
    print("\nRunning tests...")
    
    try:
        result = subprocess.run([sys.executable, "test.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def show_usage_examples():
    """Show usage examples."""
    print("\nUsage Examples:")
    print("-" * 40)
    print("Basic analysis:")
    print("  python quickstart.py ./your_project")
    print()
    print("With refactoring:")
    print("  python quickstart.py --refactor ./your_project")
    print()
    print("AI-powered analysis (requires GROQ_API_KEY):")
    print("  python quickstart.py --ai ./your_project")
    print()
    print("Full workflow:")
    print("  python quickstart.py --full ./your_project")
    print()
    print("Direct usage:")
    print("  python main.py")
    print()
    print("Test installation:")
    print("  python test.py")


def main():
    """Main setup function."""
    print("CodeSage Backend Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check files
    print("\nChecking files...")
    if not check_files():
        return False
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Run tests
    if run_tests():
        print("\nSetup completed successfully!")
        show_usage_examples()
        return True
    else:
        print("\nSetup completed with warnings.")
        print("Some tests failed, but basic functionality should work.")
        show_usage_examples()
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        print("\nFor help, check the README.md file or run individual components.")
    sys.exit(0 if success else 1)