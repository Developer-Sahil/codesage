# /code-refactoring-agent/utils.py

import os
import re
import shutil
import subprocess
import tempfile

def is_git_repo(path: str) -> bool:
    """Check if the given path is a valid GitHub repository URL."""
    # Support both .git and non-.git GitHub URLs
    return (path.startswith("https://github.com/") and 
           (path.endswith(".git") or len(path.split("/")) >= 5))

def clone_repo(repo_url: str) -> str:
    """
    Clones a public GitHub repository into a temporary directory.
    Returns the path to the temporary directory or None if failed.
    """
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix="temp_repo_")
        print(f"🔄 Cloning {repo_url} into {temp_dir}...")
        
        # Ensure URL ends with .git for git clone
        if not repo_url.endswith(".git"):
            repo_url += ".git"
            
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            capture_output=True,
            text=True,
            timeout=60  # Add timeout to prevent hanging
        )
        print("✅ Repository cloned successfully.")
        return temp_dir
    except subprocess.TimeoutExpired:
        print("❌ Error: Repository cloning timed out.")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning repository: {e.stderr}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None
    except FileNotFoundError:
        print("❌ Error: 'git' command not found. Please ensure Git is installed and in your PATH.")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None
    except Exception as e:
        print(f"❌ Unexpected error during cloning: {e}")
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None

def extract_code_from_markdown(markdown_text: str) -> str:
    """
    Extracts the first code block from a markdown-formatted string.
    """
    if not markdown_text or markdown_text.startswith("Error:"):
        return ""
    
    # Regex to find code blocks, tolerant to variations in language specifier
    code_block_regex = re.compile(r"```(?:\w+)?\s*\n(.*?)\n```", re.DOTALL)
    match = code_block_regex.search(markdown_text)
    if match:
        return match.group(1).strip()
    
    # Try without newlines after opening ```
    code_block_regex_alt = re.compile(r"```(?:\w+)?(.*?)```", re.DOTALL)
    match = code_block_regex_alt.search(markdown_text)
    if match:
        return match.group(1).strip()
    
    # If no code block is found, assume the whole text is the code
    return markdown_text.strip()

def display_directory_tree(root_dir: str):
    """
    Displays a visual tree of the specified directory.
    """
    print(f"🗺️ Project Directory Map for: {root_dir}")
    
    if not os.path.exists(root_dir):
        print(f"❌ Directory {root_dir} does not exist.")
        return
    
    # Collect all files and directories first
    items = []
    
    for root, dirs, files in os.walk(root_dir):
        # Ignore specified patterns at any level
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", ".idea", ".vscode", "node_modules", "venv"}]
        
        level = root.replace(root_dir, '').count(os.sep)
        
        # Add directory
        if level == 0:
            items.append((level, os.path.basename(root_dir), "dir", True))  # root
        else:
            dir_name = os.path.basename(root)
            items.append((level, dir_name, "dir", False))
        
        # Add files
        for file in sorted(files):
            items.append((level + 1, file, "file", False))
    
    # Print the tree
    for i, (level, name, item_type, is_root) in enumerate(items):
        if is_root:
            print(f"📁 {name}/")
            continue
            
        indent = "    " * (level - 1) if level > 1 else ""
        
        if item_type == "dir":
            print(f"{indent}├── 📁 {name}/")
        else:
            # Determine file icon based on extension
            ext = os.path.splitext(name)[1].lower()
            icon = get_file_icon(ext)
            print(f"{indent}├── {icon} {name}")

def get_file_icon(extension: str) -> str:
    """
    Returns an appropriate emoji icon for different file types.
    """
    icon_map = {
        '.py': '🐍',
        '.js': '🟨',
        '.jsx': '⚛️',
        '.ts': '🔷',
        '.tsx': '⚛️',
        '.html': '🌐',
        '.css': '🎨',
        '.json': '📋',
        '.md': '📝',
        '.txt': '📄',
        '.yml': '⚙️',
        '.yaml': '⚙️',
        '.xml': '📰',
        '.sql': '🗃️',
        '.java': '☕',
        '.cpp': '⚙️',
        '.c': '⚙️',
        '.h': '📋',
        '.cs': '🔹',
        '.go': '🐹',
        '.rs': '🦀',
        '.php': '🐘',
        '.rb': '💎',
        '.swift': '🍎',
        '.kt': '🟢',
        '.scala': '🔺',
        '.r': '📊',
        '.sh': '🐚',
        '.env': '🔐',
    }
    return icon_map.get(extension, '📄')

def validate_source_directory(source_path: str) -> bool:
    """
    Validates that the source directory exists and contains files.
    """
    if not os.path.exists(source_path):
        print(f"❌ Error: Source path '{source_path}' does not exist.")
        return False
    
    if not os.path.isdir(source_path):
        print(f"❌ Error: '{source_path}' is not a directory.")
        return False
    
    # Check if directory has any files (recursively)
    has_files = False
    for root, dirs, files in os.walk(source_path):
        if files:
            has_files = True
            break
    
    if not has_files:
        print(f"⚠️ Warning: Directory '{source_path}' appears to be empty.")
        return False
    
    return True