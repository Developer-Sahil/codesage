# /code-refactoring-agent/main.py

import os
import sys
import argparse
import shutil
from dotenv import load_dotenv

from agent import RefactoringAgent
from utils import is_git_repo, clone_repo, display_directory_tree, validate_source_directory
from config import Config

def main():
    """
    Main entry point for the codebase refactoring agent using Google Gemini.
    """
    parser = argparse.ArgumentParser(
        description="Codebase Refactoring Agent using Google Gemini AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py /path/to/local/project
  python main.py https://github.com/user/repo.git
  python main.py https://github.com/user/repo --output-dir my_refactored_code
  python main.py /path/to/project --model gemini-2.5-flash-lite
        """
    )
    parser.add_argument(
        "path", 
        help="Path to a local codebase folder or a public GitHub repository URL."
    )
    parser.add_argument(
        "--output-dir", 
        default="refactored_codebase", 
        help="The directory to save the refactored code. Defaults to 'refactored_codebase'."
    )
    parser.add_argument(
        "--model",
        choices=["gemini-2.5-flash-lite", "gemini-1.5-flash-8b", "gemini-pro", "gemini-pro-vision"],
        default="gemini-2.5-flash-lite", 
        help="The Gemini model to use for all API calls. Defaults to 'gemini-2.5-flash-lite'."
    )
    parser.add_argument(
        "--skip-analysis",
        action="store_true",
        help="Skip the analysis phase and only perform refactoring."
    )
    parser.add_argument(
        "--skip-refactoring",
        action="store_true",
        help="Skip the refactoring phase and only perform analysis."
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay in seconds between API calls to respect rate limits. Default: 2"
    )
    
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Override model if specified
    if hasattr(args, 'model'):
        Config.GEMINI_MODEL = args.model
    
    # Validate API key
    if not Config.validate():
        print("❌ Error: GEMINI_API_KEY not found. Please set it in your .env file.")
        print("Example .env file content:")
        print("GEMINI_API_KEY=your_api_key_here")
        print("\nGet your API key from: https://aistudio.google.com/app/apikey")
        return 1

    source_path = args.path
    temp_dir = None

    # Handle GitHub repository URLs
    if is_git_repo(source_path):
        temp_dir = clone_repo(source_path)
        if not temp_dir:
            print("❌ Failed to clone repository. Exiting.")
            return 1
        source_path = temp_dir
    
    # Validate source directory
    if not validate_source_directory(source_path):
        if temp_dir:
            shutil.rmtree(temp_dir)
        return 1

    # Clean up existing output directory if it exists
    if os.path.exists(args.output_dir):
        print(f"🧹 Output directory '{args.output_dir}' already exists. Removing it.")
        try:
            shutil.rmtree(args.output_dir)
        except Exception as e:
            print(f"❌ Error removing output directory: {e}")
            if temp_dir:
                shutil.rmtree(temp_dir)
            return 1

    try:
        # Initialize the agent (no client parameter needed for Gemini)
        agent = RefactoringAgent(source_path, args.output_dir)
        
        # Validate conflicting flags
        if args.skip_analysis and args.skip_refactoring:
            print("❌ Error: Cannot skip both analysis and refactoring.")
            return 1
            
        if args.skip_analysis:
            print("⚠️ Skipping analysis phase as requested.")
            # TODO: Implement refactor-only mode
        elif args.skip_refactoring:
            print("⚠️ Skipping refactoring phase as requested.")
            # TODO: Implement analysis-only mode
        
        print(f"🤖 Using Gemini model: {Config.GEMINI_MODEL}")
        print(f"⏱️ Rate limit delay: {args.delay} seconds between requests")
        
        # Run the main process
        agent.run()
        print("\n🎉 Codebase refactoring process completed successfully!")

        # Display the directory tree of the refactored project
        if not args.skip_refactoring and os.path.exists(args.output_dir):
            print("\n" + "="*50)
            display_directory_tree(args.output_dir)
            print("="*50)
        
        # Generate and display interview questions if analysis was performed
        if not args.skip_analysis and agent.analysis_results:
            agent.generate_interview_questions()

        return 0

    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user.")
        return 1
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        print("If you're getting rate limit errors, try:")
        print("1. Increasing the --delay parameter")
        print("2. Using --skip-analysis or --skip-refactoring to reduce API calls")
        print("3. Processing smaller codebases")
        return 1
    finally:
        # Clean up temporary directory
        if temp_dir:
            print(f"\n🧹 Cleaning up temporary repository directory: {temp_dir}")
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️ Warning: Could not clean up temporary directory: {e}")

if __name__ == "__main__":
    sys.exit(main())