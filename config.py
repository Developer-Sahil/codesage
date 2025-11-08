# /code-refactoring-agent/config.py

import os
from typing import Set, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the refactoring agent (multi-model)."""
    
    # ===============================
    # 🔑 API KEYS AND MODEL SETTINGS
    # ===============================
    
    # --- Gemini (Google AI Studio) ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    GEMINI_MAX_RETRIES = int(os.getenv("GEMINI_MAX_RETRIES", "3"))
    GEMINI_REQUEST_TIMEOUT = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "30"))

    # --- GPT (OpenAI) ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

    # --- Claude (Anthropic) ---
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")

    # --- Grok / Groq ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "grok-4-latest")

    # All supported model identifiers (for CLI dropdown)
    SUPPORTED_MODELS = {
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-pro",
        "gpt-4o",
        "gpt-3.5-turbo",
        "gpt-5-nano",
        "gpt-4-turbo",
        "gpt-4o-mini",
        "grok-4-latest",
        "claude-3-sonnet",
        "claude-3-opus",
        "grok-2",
        "grok-4-fast-reasoning"
    }

    # ===============================
    # ⚙️ FILE AND SYSTEM SETTINGS
    # ===============================

    MAX_FILE_SIZE_FOR_REFACTORING = int(os.getenv("MAX_FILE_SIZE_FOR_REFACTORING", "15000"))
    MAX_FILE_SIZE_FOR_ANALYSIS = int(os.getenv("MAX_FILE_SIZE_FOR_ANALYSIS", "12000"))
    GIT_CLONE_TIMEOUT = int(os.getenv("GIT_CLONE_TIMEOUT", "60"))

    IGNORE_PATTERNS: Set[str] = {
        ".git", ".svn", "__pycache__", "venv", ".idea", ".vscode", "node_modules",
        "*.pyc", "*.log", "dist", "build", "tmp", "temp", ".DS_Store"
    }

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs", ".swift", ".php",
        ".html", ".css", ".sh", ".r", ".sql", ".json", ".xml"
    }

    FILE_ICONS: Dict[str, str] = {
        '.py': '🐍', '.js': '🟨', '.java': '☕', '.cpp': '⚙️', '.html': '🌐',
        '.css': '🎨', '.sh': '🐚', '.r': '📊', '.go': '🐹', '.rs': '🦀'
    }

    # ===============================
    # 🤖 MODEL CONFIGURATIONS
    # ===============================

    GEMINI_SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    GEMINI_GENERATION_CONFIG = {
        "temperature": GEMINI_TEMPERATURE,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
    }

    # ===============================
    # 💬 SYSTEM PROMPTS
    # ===============================

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

    # ===============================
    # ✅ VALIDATION & HELPERS
    # ===============================

    @classmethod
    def validate(cls) -> bool:
        """Validate all necessary API keys."""
        if not any([cls.GEMINI_API_KEY, cls.OPENAI_API_KEY, cls.ANTHROPIC_API_KEY, cls.GROQ_API_KEY]):
            print("❌ No API keys found. Please set at least one in your .env file.")
            return False
        return True

    @classmethod
    def get_file_icon(cls, extension: str) -> str:
        """Return emoji icon for file type."""
        return cls.FILE_ICONS.get(extension.lower(), '📄')

    @classmethod
    def is_supported_file(cls, filename: str) -> bool:
        """Check if file extension is supported."""
        return any(filename.lower().endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS)

    @classmethod
    def should_ignore(cls, name: str) -> bool:
        """Ignore temp/build/version control files."""
        return name in cls.IGNORE_PATTERNS or any(
            name.endswith(pattern.lstrip('*')) for pattern in cls.IGNORE_PATTERNS if pattern.startswith('*')
        )
