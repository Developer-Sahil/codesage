"""
CodeSage Backend - File Walker Module
Handles repository parsing and file tree mapping with metadata.
"""

import os
import mimetypes
import subprocess
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import hashlib


class FileWalker:
    """
    File walker class for mapping repository structure with metadata.
    Analyzes file types, counts lines of code, and identifies dependencies.
    """
    
    # Common programming language extensions
    LANGUAGE_EXTENSIONS = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.jsx': 'React JSX',
        '.tsx': 'React TSX',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.h': 'C/C++ Header',
        '.hpp': 'C++ Header',
        '.cs': 'C#',
        '.php': 'PHP',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.rs': 'Rust',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.sh': 'Shell',
        '.bash': 'Bash',
        '.zsh': 'Zsh',
        '.sql': 'SQL',
        '.html': 'HTML',
        '.htm': 'HTML',
        '.css': 'CSS',
        '.scss': 'SCSS',
        '.sass': 'Sass',
        '.less': 'Less',
        '.xml': 'XML',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.toml': 'TOML',
        '.ini': 'INI',
        '.cfg': 'Config',
        '.conf': 'Config',
        '.md': 'Markdown',
        '.rst': 'reStructuredText',
        '.txt': 'Text',
        '.r': 'R',
        '.R': 'R',
        '.m': 'MATLAB/Objective-C',
        '.pl': 'Perl',
        '.lua': 'Lua',
        '.dart': 'Dart',
        '.vim': 'Vim Script'
    }
    
    # Files and directories to ignore
    IGNORE_PATTERNS = {
        # Version control
        '.git', '.svn', '.hg', '.bzr',
        # Dependencies
        'node_modules', 'vendor', '__pycache__', '.venv', 'venv', 'env',
        # Build outputs
        'build', 'dist', 'target', 'out', 'bin', 'obj',
        # IDE/Editor files
        '.vscode', '.idea', '.vs', '.sublime-text', '*.swp', '*.swo',
        # OS files
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        # Temporary files
        '*.tmp', '*.temp', '*.cache',
        # Logs
        '*.log', 'logs',
        # Archives
        '*.zip', '*.tar', '*.gz', '*.rar', '*.7z'
    }
    
    # Binary file extensions
    BINARY_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o', '.a', '.lib',
        '.jar', '.war', '.ear', '.class', '.pyc', '.pyo', '.pyd',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.svg', '.ico',
        '.mp3', '.mp4', '.avi', '.mov', '.wav', '.flv', '.wmv',
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2'
    }
    
    def __init__(self):
        """Initialize the FileWalker."""
        self.file_count = 0
        self.total_lines = 0
        self.language_stats = {}
    
    def map_directory(self, directory_path: str, max_depth: int = 10) -> Optional[Dict]:
        """
        Map directory structure with metadata.
        
        Args:
            directory_path: Path to directory to map
            max_depth: Maximum depth to traverse
            
        Returns:
            Dictionary representing file tree with metadata
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return None
        
        # Reset counters
        self.file_count = 0
        self.total_lines = 0
        self.language_stats = {}
        
        try:
            root_node = self._map_node(directory_path, 0, max_depth)
            
            # Add summary statistics
            root_node['statistics'] = {
                'total_files': self.file_count,
                'total_lines': self.total_lines,
                'languages': dict(self.language_stats)
            }
            
            return root_node
            
        except Exception as e:
            print(f"Error mapping directory: {str(e)}")
            return None
    
    def _map_node(self, path: str, current_depth: int, max_depth: int) -> Dict:
        """
        Recursively map a file system node.
        
        Args:
            path: Current path to map
            current_depth: Current recursion depth
            max_depth: Maximum allowed depth
            
        Returns:
            Dictionary representing the node
        """
        node = {
            'name': os.path.basename(path),
            'path': os.path.abspath(path),
            'type': 'directory' if os.path.isdir(path) else 'file',
            'size': self._get_size(path),
            'modified': self._get_modified_time(path)
        }
        
        if os.path.isfile(path):
            # File node
            self.file_count += 1
            file_metadata = self._analyze_file(path)
            node.update(file_metadata)
            
            if file_metadata.get('lines_of_code', 0) > 0:
                self.total_lines += file_metadata['lines_of_code']
            
            language = file_metadata.get('language', 'Unknown')
            self.language_stats[language] = self.language_stats.get(language, 0) + 1
            
        elif os.path.isdir(path) and current_depth < max_depth:
            # Directory node
            if not self._should_ignore(os.path.basename(path)):
                children = []
                try:
                    for item in sorted(os.listdir(path)):
                        if not self._should_ignore(item):
                            item_path = os.path.join(path, item)
                            child_node = self._map_node(item_path, current_depth + 1, max_depth)
                            children.append(child_node)
                    
                    node['children'] = children
                    node['child_count'] = len(children)
                    
                except PermissionError:
                    node['error'] = 'Permission denied'
                    node['children'] = []
        
        return node
    
    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file and extract metadata.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {
            'extension': self._get_extension(file_path),
            'language': self._detect_language(file_path),
            'is_binary': self._is_binary_file(file_path),
            'lines_of_code': 0,
            'blank_lines': 0,
            'comment_lines': 0,
            'file_hash': self._calculate_file_hash(file_path),
            'encoding': 'unknown'
        }
        
        # If not binary, analyze content
        if not metadata['is_binary']:
            content_analysis = self._analyze_file_content(file_path)
            metadata.update(content_analysis)
        
        return metadata
    
    def _analyze_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze file content for lines of code, encoding, etc.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with content analysis
        """
        analysis = {
            'lines_of_code': 0,
            'blank_lines': 0,
            'comment_lines': 0,
            'encoding': 'utf-8',
            'dependencies': []
        }
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        analysis['encoding'] = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                return analysis
            
            lines = content.split('\n')
            language = self._detect_language(file_path)
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    analysis['blank_lines'] += 1
                elif self._is_comment_line(stripped, language):
                    analysis['comment_lines'] += 1
                else:
                    analysis['lines_of_code'] += 1
            
            # Extract dependencies/imports
            analysis['dependencies'] = self._extract_dependencies(content, language)
            
        except Exception:
            # If file can't be read, treat as binary
            analysis['lines_of_code'] = 0
        
        return analysis
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        extension = self._get_extension(file_path).lower()
        return self.LANGUAGE_EXTENSIONS.get(extension, 'Unknown')
    
    def _get_extension(self, file_path: str) -> str:
        """Get file extension."""
        return os.path.splitext(file_path)[1].lower()
    
    def _is_binary_file(self, file_path: str) -> bool:
        """Check if file is binary based on extension or content."""
        extension = self._get_extension(file_path)
        if extension in self.BINARY_EXTENSIONS:
            return True
        
        # Check file content for null bytes (binary indicator)
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except Exception:
            return True  # Assume binary if can't read
    
    def _should_ignore(self, name: str) -> bool:
        """Check if file/directory should be ignored."""
        return any(
            name == pattern or name.startswith(pattern.replace('*', ''))
            for pattern in self.IGNORE_PATTERNS
        )
    
    def _get_size(self, path: str) -> int:
        """Get file or directory size in bytes."""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            elif os.path.isdir(path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except (OSError, FileNotFoundError):
                            continue
                return total_size
        except (OSError, FileNotFoundError):
            return 0
        return 0
    
    def _get_modified_time(self, path: str) -> str:
        """Get file modification time as ISO string."""
        try:
            import datetime
            timestamp = os.path.getmtime(path)
            return datetime.datetime.fromtimestamp(timestamp).isoformat()
        except (OSError, FileNotFoundError):
            return ""
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()[:16]  # First 16 chars for brevity
        except Exception:
            return ""
    
    def _is_comment_line(self, line: str, language: str) -> bool:
        """Check if line is a comment based on language."""
        comment_patterns = {
            'Python': ['#'],
            'JavaScript': ['//', '/*', '*/', '*'],
            'TypeScript': ['//', '/*', '*/', '*'],
            'Java': ['//', '/*', '*/', '*'],
            'C': ['//', '/*', '*/', '*'],
            'C++': ['//', '/*', '*/', '*'],
            'C#': ['//', '/*', '*/', '*'],
            'PHP': ['//', '#', '/*', '*/', '*'],
            'Ruby': ['#'],
            'Go': ['//'],
            'Rust': ['//', '/*', '*/', '*'],
            'Swift': ['//', '/*', '*/', '*'],
            'Kotlin': ['//', '/*', '*/', '*'],
            'Scala': ['//', '/*', '*/', '*'],
            'Shell': ['#'],
            'Bash': ['#'],
            'SQL': ['--', '/*', '*/', '*'],
            'HTML': ['<!--', '-->', '<!'],
            'CSS': ['/*', '*/', '*'],
            'XML': ['<!--', '-->', '<!']
        }
        
        patterns = comment_patterns.get(language, [])
        return any(line.startswith(pattern) for pattern in patterns)
    
    def _extract_dependencies(self, content: str, language: str) -> List[str]:
        """Extract import/dependency statements from file content."""
        dependencies = []
        lines = content.split('\n')
        
        if language == 'Python':
            import_patterns = ['import ', 'from ']
            for line in lines:
                stripped = line.strip()
                for pattern in import_patterns:
                    if stripped.startswith(pattern):
                        # Extract module name
                        if pattern == 'import ':
                            module = stripped[7:].split()[0].split('.')[0]
                        else:  # 'from '
                            module = stripped[5:].split()[0].split('.')[0]
                        if module and module not in dependencies:
                            dependencies.append(module)
        
        elif language in ['JavaScript', 'TypeScript']:
            import_patterns = ['import ', 'require(', 'from ']
            for line in lines:
                stripped = line.strip()
                if any(pattern in stripped for pattern in import_patterns):
                    # Simple extraction - could be improved
                    if 'from ' in stripped:
                        parts = stripped.split('from ')
                        if len(parts) > 1:
                            module = parts[-1].strip().strip('\'"').split('/')[0]
                            if module and module not in dependencies:
                                dependencies.append(module)
        
        elif language == 'Java':
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('import '):
                    package = stripped[7:].strip().rstrip(';').split('.')[0]
                    if package and package not in dependencies:
                        dependencies.append(package)
        
        # Limit to first 10 dependencies for brevity
        return dependencies[:10]
    
    def get_file_tree_summary(self, file_tree: Dict) -> Dict[str, Any]:
        """
        Generate a summary of the file tree.
        
        Args:
            file_tree: File tree dictionary
            
        Returns:
            Summary statistics
        """
        if not file_tree:
            return {}
        
        return file_tree.get('statistics', {})
    
    def find_files_by_language(self, file_tree: Dict, language: str) -> List[str]:
        """
        Find all files of a specific language in the tree.
        
        Args:
            file_tree: File tree dictionary
            language: Language to search for
            
        Returns:
            List of file paths
        """
        files = []
        
        def search_node(node):
            if node.get('type') == 'file' and node.get('language') == language:
                files.append(node['path'])
            elif node.get('children'):
                for child in node['children']:
                    search_node(child)
        
        search_node(file_tree)
        return files