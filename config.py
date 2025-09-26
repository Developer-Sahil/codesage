# /code-refactoring-agent/config.py

import os
from typing import Set, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the refactoring agent."""
    
    # API Configuration - Gemini (Google AI Studio)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")  # or "models/gemini-1.5-flash-8b"
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    GEMINI_REQUEST_TIMEOUT = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "30"))  # seconds
    
    # File processing limits (adjusted for Gemini's context limits)
    MAX_FILE_SIZE_FOR_REFACTORING = int(os.getenv("MAX_FILE_SIZE_FOR_REFACTORING", "15000"))  # characters
    MAX_FILE_SIZE_FOR_ANALYSIS = int(os.getenv("MAX_FILE_SIZE_FOR_ANALYSIS", "12000"))  # characters
    
    # Git configuration
    GIT_CLONE_TIMEOUT = int(os.getenv("GIT_CLONE_TIMEOUT", "60"))  # seconds
    
    # Directories and files to ignore
    IGNORE_PATTERNS: Set[str] = {
        # Version control
        ".git", ".svn", ".hg",
        # Python
        "__pycache__", "*.pyc", "*.pyo", "*.pyd", ".Python",
        "venv", "env", ".venv", ".env", "ENV", "env.bak", "venv.bak",
        ".pytest_cache", ".coverage", "htmlcov", ".tox",
        # Node.js
        "node_modules", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
        ".npm", ".yarn-integrity",
        # IDEs
        ".idea", ".vscode", "*.swp", "*.swo", "*~",
        # Build outputs
        "dist", "build", "out", "target", "bin", "obj",
        # OS files
        ".DS_Store", "Thumbs.db", "desktop.ini",
        # Logs
        "*.log", "logs",
        # Temporary files
        "tmp", "temp", ".tmp", ".temp"
    }
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS: Set[str] = {
        # Python
        ".py", ".pyx", ".pyi",
        # JavaScript/TypeScript
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
        # Web technologies
        ".html", ".htm", ".css", ".scss", ".sass", ".less",
        # Java
        ".java", ".scala", ".kt", ".groovy",
        # C/C++
        ".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx",
        # C#
        ".cs", ".vb",
        # Systems programming
        ".go", ".rs", ".zig",
        # Mobile
        ".swift", ".m", ".mm",
        # Scripting
        ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
        # Data & Config
        ".sql", ".r", ".R", ".matlab", ".m",
        # Other languages
        ".php", ".rb", ".pl", ".lua", ".dart", ".elm"
    }
    
    # File type icons for display
    FILE_ICONS: Dict[str, str] = {
        '.py': '🐍', '.pyx': '🐍', '.pyi': '🐍',
        '.js': '🟨', '.jsx': '⚛️', '.ts': '🔷', '.tsx': '⚛️',
        '.mjs': '🟨', '.cjs': '🟨',
        '.html': '🌐', '.htm': '🌐',
        '.css': '🎨', '.scss': '🎨', '.sass': '🎨', '.less': '🎨',
        '.json': '📋', '.jsonc': '📋',
        '.md': '📝', '.markdown': '📝',
        '.txt': '📄', '.text': '📄',
        '.yml': '⚙️', '.yaml': '⚙️',
        '.xml': '📰', '.xsl': '📰',
        '.sql': '🗃️', '.db': '🗃️',
        '.java': '☕', '.scala': '🔺', '.kt': '🟢', '.groovy': '🐘',
        '.cpp': '⚙️', '.cxx': '⚙️', '.cc': '⚙️',
        '.c': '⚙️', '.h': '📋', '.hpp': '📋', '.hxx': '📋',
        '.cs': '🔹', '.vb': '🔹',
        '.go': '🐹', '.rs': '🦀', '.zig': '⚡',
        '.php': '🐘', '.rb': '💎', '.pl': '🐪', '.lua': '🌙',
        '.swift': '🍎', '.m': '🍎', '.mm': '🍎',
        '.dart': '🎯', '.elm': '🌳',
        '.r': '📊', '.R': '📊', '.matlab': '📊',
        '.sh': '🐚', '.bash': '🐚', '.zsh': '🐚', '.fish': '🐠',
        '.ps1': '💙', '.bat': '⚫', '.cmd': '⚫',
        '.env': '🔐', '.gitignore': '🚫', '.dockerignore': '🚫',
        '.dockerfile': '🐳', '.docker-compose.yml': '🐳',
        '.makefile': '🔨', '.cmake': '🔨',
        '.toml': '⚙️', '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️'
    }
    
    # Gemini safety settings
    GEMINI_SAFETY_SETTINGS = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        }
    ]
    
    # Generation config for Gemini
    GEMINI_GENERATION_CONFIG = {
        "temperature": GEMINI_TEMPERATURE,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }
    
    # Analysis prompts templates
    ANALYSIS_SYSTEM_PROMPT = (
        "You are a senior software engineer specializing in code quality analysis. "
        "Analyze the provided code and give a concise, structured report on its quality. "
        "Focus on actionable insights and be specific about issues found."
    )
    
    REFACTORING_SYSTEM_PROMPT = (
        "You are an expert code refactoring assistant. Your task is to rewrite the given code to improve "
        "its readability, maintainability, and adherence to best practices without altering its core functionality. "
        "Add appropriate comments and docstrings. Ensure the code follows language-specific conventions. "
        "Return only the refactored code in a markdown code block without explanations."
    )
    
    RECOMMENDATIONS_SYSTEM_PROMPT = (
        "You are a principal software architect. Based on the analysis reports of multiple files from a codebase, "
        "provide high-level, actionable recommendations for improving the entire project. "
        "Focus on patterns, architectural issues, and strategic improvements."
    )
    
    INTERVIEW_QUESTIONS_SYSTEM_PROMPT = (
        "You are a senior software engineer and technical interviewer. "
        "Create insightful technical interview questions based on the codebase analysis. "
        "Questions should assess understanding of software design, problem-solving, and coding practices. "
        "Make questions specific to the analyzed code but also test general programming knowledge."
    )
    
    @classmethod
    def validate(cls) -> bool:
        """Validate the configuration."""
        if not cls.GEMINI_API_KEY:
            return False
        return True
    
    @classmethod
    def get_file_icon(cls, extension: str) -> str:
        """Get the appropriate icon for a file extension."""
        return cls.FILE_ICONS.get(extension.lower(), '📄')
    
    @classmethod
    def is_supported_file(cls, filename: str) -> bool:
        """Check if a file is supported based on its extension."""
        return any(filename.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)
    
    @classmethod
    def should_ignore(cls, name: str) -> bool:
        """Check if a file or directory should be ignored."""
        return name in cls.IGNORE_PATTERNS or any(
            name.endswith(pattern.lstrip('*')) for pattern in cls.IGNORE_PATTERNS 
            if pattern.startswith('*')
        )