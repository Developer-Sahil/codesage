"""
CodeSage Backend - Code Analyzer Module
Analyzes code to identify classes, functions, dependencies, and code quality metrics.
"""

import os
import ast
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class FunctionInfo:
    """Data class for function information."""
    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    complexity: int = 1
    is_async: bool = False
    decorators: List[str] = None
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class ClassInfo:
    """Data class for class information."""
    name: str
    line_start: int
    line_end: int
    methods: List[FunctionInfo]
    base_classes: List[str]
    docstring: Optional[str] = None
    decorators: List[str] = None
    is_abstract: bool = False
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []


@dataclass
class FileAnalysis:
    """Data class for file analysis results."""
    file_path: str
    language: str
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[str]
    dependencies: List[str]
    complexity_score: float
    maintainability_index: float
    issues: List[str]
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


@dataclass
class RepositoryAnalysis:
    """Data class for repository analysis results."""
    total_files: int
    analyzed_files: int
    file_analyses: Dict[str, FileAnalysis]
    overall_complexity: float
    overall_maintainability: float
    architecture_patterns: List[str]
    dependency_graph: Dict[str, List[str]]
    code_smells: List[str]
    recommendations: List[str]


class CodeAnalyzer:
    """
    Code analyzer class for extracting classes, functions, and dependencies
    from various programming languages.
    """
    
    def __init__(self):
        """Initialize the CodeAnalyzer."""
        self.supported_languages = {
            'Python': self._analyze_python_file,
            'JavaScript': self._analyze_javascript_file,
            'TypeScript': self._analyze_typescript_file,
            'Java': self._analyze_java_file
        }
    
    def analyze_repository(self, repo_path: str, file_tree: Dict) -> RepositoryAnalysis:
        """
        Analyze entire repository for code structure and quality.
        
        Args:
            repo_path: Path to repository
            file_tree: File tree structure from FileWalker
            
        Returns:
            RepositoryAnalysis containing comprehensive analysis
        """
        file_analyses = {}
        total_files = 0
        analyzed_files = 0
        total_complexity = 0.0
        total_maintainability = 0.0
        all_dependencies = set()
        code_smells = []
        
        # Collect all code files
        code_files = self._collect_code_files(file_tree)
        total_files = len(code_files)
        
        for file_info in code_files:
            file_path = file_info['path']
            language = file_info['language']
            
            if language in self.supported_languages:
                try:
                    analysis = self._analyze_file(file_path, language)
                    if analysis:
                        file_analyses[file_path] = analysis
                        analyzed_files += 1
                        total_complexity += analysis.complexity_score
                        total_maintainability += analysis.maintainability_index
                        all_dependencies.update(analysis.dependencies)
                        code_smells.extend(analysis.issues)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {str(e)}")
        
        # Calculate overall metrics
        overall_complexity = total_complexity / max(analyzed_files, 1)
        overall_maintainability = total_maintainability / max(analyzed_files, 1)
        
        # Generate dependency graph
        dependency_graph = self._build_dependency_graph(file_analyses)
        
        # Detect architecture patterns
        architecture_patterns = self._detect_architecture_patterns(file_analyses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            file_analyses, overall_complexity, overall_maintainability
        )
        
        return RepositoryAnalysis(
            total_files=total_files,
            analyzed_files=analyzed_files,
            file_analyses=file_analyses,
            overall_complexity=overall_complexity,
            overall_maintainability=overall_maintainability,
            architecture_patterns=architecture_patterns,
            dependency_graph=dependency_graph,
            code_smells=list(set(code_smells)),  # Remove duplicates
            recommendations=recommendations
        )
    
    def _collect_code_files(self, file_tree: Dict) -> List[Dict]:
        """Collect all code files from file tree."""
        code_files = []
        
        def collect_recursive(node):
            if node.get('type') == 'file':
                language = node.get('language', 'Unknown')
                if language in self.supported_languages:
                    code_files.append({
                        'path': node['path'],
                        'language': language
                    })
            elif node.get('children'):
                for child in node['children']:
                    collect_recursive(child)
        
        collect_recursive(file_tree)
        return code_files
    
    def _analyze_file(self, file_path: str, language: str) -> Optional[FileAnalysis]:
        """Analyze a single file based on its language."""
        if language not in self.supported_languages:
            return None
        
        analyzer_func = self.supported_languages[language]
        return analyzer_func(file_path)
    
    def _analyze_python_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze Python file using AST parsing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            dependencies = []
            complexity_score = 1.0
            issues = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_python_class(node, content)
                    classes.append(class_info)
                    complexity_score += len(class_info.methods) * 0.5
                
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    # Only count top-level functions
                    if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                        func_info = self._extract_python_function(node, content)
                        functions.append(func_info)
                        complexity_score += func_info.complexity * 0.3
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = self._extract_python_import(node)
                    imports.extend(import_info)
                    dependencies.extend(import_info)
            
            # Calculate maintainability index (simplified)
            maintainability = max(0, 171 - 5.2 * complexity_score - 0.23 * len(functions) - 16.2)
            
            # Detect code smells
            issues = self._detect_python_code_smells(tree, content)
            
            return FileAnalysis(
                file_path=file_path,
                language='Python',
                classes=classes,
                functions=functions,
                imports=imports,
                dependencies=dependencies,
                complexity_score=complexity_score,
                maintainability_index=maintainability,
                issues=issues
            )
            
        except Exception as e:
            return None
    
    def _extract_python_class(self, node: ast.ClassDef, content: str) -> ClassInfo:
        """Extract class information from Python AST node."""
        methods = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_python_function(item, content)
                methods.append(method_info)
        
        base_classes = [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
        
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        return ClassInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            methods=methods,
            base_classes=base_classes,
            docstring=docstring,
            decorators=decorators,
            is_abstract='ABC' in base_classes or 'abstractmethod' in str(decorators)
        )
    
    def _extract_python_function(self, node: ast.FunctionDef, content: str) -> FunctionInfo:
        """Extract function information from Python AST node."""
        parameters = [arg.arg for arg in node.args.args]
        
        # Calculate cyclomatic complexity
        complexity = self._calculate_python_complexity(node)
        
        decorators = [dec.id if isinstance(dec, ast.Name) else str(dec) for dec in node.decorator_list]
        
        docstring = None
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and 
            isinstance(node.body[0].value.value, str)):
            docstring = node.body[0].value.value
        
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
        
        return FunctionInfo(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            complexity=complexity,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            decorators=decorators
        )
    
    def _calculate_python_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for Python function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                ast.With, ast.AsyncWith, ast.Try, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _extract_python_import(self, node: ast.Import | ast.ImportFrom) -> List[str]:
        """Extract import information from Python AST node."""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module.split('.')[0])
        
        return imports
    
    def _detect_python_code_smells(self, tree: ast.AST, content: str) -> List[str]:
        """Detect code smells in Python code."""
        issues = []
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            # Long functions
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and (node.end_lineno - node.lineno) > 50:
                    issues.append(f"Long function: {node.name} ({node.end_lineno - node.lineno} lines)")
            
            # Too many parameters
            if isinstance(node, ast.FunctionDef) and len(node.args.args) > 6:
                issues.append(f"Too many parameters in function: {node.name} ({len(node.args.args)} parameters)")
            
            # Nested functions (high complexity)
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_python_complexity(node)
                if complexity > 10:
                    issues.append(f"High complexity function: {node.name} (complexity: {complexity})")
        
        # Check for long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"Long line at line {i} ({len(line)} characters)")
        
        return issues
    
    def _analyze_javascript_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze JavaScript file using regex patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = self._extract_js_functions(content)
            classes = self._extract_js_classes(content)
            imports = self._extract_js_imports(content)
            dependencies = imports.copy()
            
            complexity_score = len(functions) * 1.2 + len(classes) * 2.0
            maintainability = max(0, 171 - 5.2 * (complexity_score / 10) - 0.23 * len(functions))
            
            issues = self._detect_js_code_smells(content)
            
            return FileAnalysis(
                file_path=file_path,
                language='JavaScript',
                classes=classes,
                functions=functions,
                imports=imports,
                dependencies=dependencies,
                complexity_score=complexity_score,
                maintainability_index=maintainability,
                issues=issues
            )
            
        except Exception:
            return None
    
    def _extract_js_functions(self, content: str) -> List[FunctionInfo]:
        """Extract JavaScript functions using regex."""
        functions = []
        
        # Function declarations
        func_pattern = r'(?:function\s+|const\s+|let\s+|var\s+)(\w+)\s*(?:=\s*(?:async\s+)?function)?\s*\([^)]*\)\s*(?:=>)?\s*{'
        
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            
            functions.append(FunctionInfo(
                name=name,
                line_start=line_start,
                line_end=line_start,  # Simplified
                parameters=[],  # Would need more complex parsing
                complexity=1
            ))
        
        return functions
    
    def _extract_js_classes(self, content: str) -> List[ClassInfo]:
        """Extract JavaScript classes using regex."""
        classes = []
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?\s*{'
        
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            name = match.group(1)
            base_class = match.group(2) if match.group(2) else None
            line_start = content[:match.start()].count('\n') + 1
            
            classes.append(ClassInfo(
                name=name,
                line_start=line_start,
                line_end=line_start,  # Simplified
                methods=[],  # Would need more complex parsing
                base_classes=[base_class] if base_class else []
            ))
        
        return classes
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript imports using regex."""
        imports = []
        
        # ES6 imports
        import_pattern = r'import\s+.*?\s+from\s+[\'"]([^\'\"]+)[\'"]'
        # CommonJS requires
        require_pattern = r'require\s*\(\s*[\'"]([^\'\"]+)[\'"]\s*\)'
        
        for pattern in [import_pattern, require_pattern]:
            for match in re.finditer(pattern, content):
                module = match.group(1).split('/')[0]
                if module and module not in imports:
                    imports.append(module)
        
        return imports
    
    def _detect_js_code_smells(self, content: str) -> List[str]:
        """Detect JavaScript code smells."""
        issues = []
        lines = content.split('\n')
        
        # Long lines
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(f"Long line at line {i}")
        
        # TODO: Add more JavaScript-specific code smell detection
        
        return issues
    
    def _analyze_typescript_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze TypeScript file (similar to JavaScript)."""
        # For now, use JavaScript analyzer as base
        analysis = self._analyze_javascript_file(file_path)
        if analysis:
            analysis.language = 'TypeScript'
        return analysis
    
    def _analyze_java_file(self, file_path: str) -> Optional[FileAnalysis]:
        """Analyze Java file using regex patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            classes = self._extract_java_classes(content)
            functions = self._extract_java_methods(content)
            imports = self._extract_java_imports(content)
            dependencies = imports.copy()
            
            complexity_score = len(functions) * 1.5 + len(classes) * 2.5
            maintainability = max(0, 171 - 5.2 * (complexity_score / 10) - 0.23 * len(functions))
            
            issues = []  # Simplified for now
            
            return FileAnalysis(
                file_path=file_path,
                language='Java',
                classes=classes,
                functions=functions,
                imports=imports,
                dependencies=dependencies,
                complexity_score=complexity_score,
                maintainability_index=maintainability,
                issues=issues
            )
            
        except Exception:
            return None
    
    def _extract_java_classes(self, content: str) -> List[ClassInfo]:
        """Extract Java classes using regex."""
        classes = []
        
        class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?'
        
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            name = match.group(1)
            base_class = match.group(2) if match.group(2) else None
            line_start = content[:match.start()].count('\n') + 1
            
            classes.append(ClassInfo(
                name=name,
                line_start=line_start,
                line_end=line_start,  # Simplified
                methods=[],
                base_classes=[base_class] if base_class else []
            ))
        
        return classes
    
    def _extract_java_methods(self, content: str) -> List[FunctionInfo]:
        """Extract Java methods using regex."""
        methods = []
        
        method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)\s*{'
        
        for match in re.finditer(method_pattern, content, re.MULTILINE):
            name = match.group(1)
            line_start = content[:match.start()].count('\n') + 1
            
            methods.append(FunctionInfo(
                name=name,
                line_start=line_start,
                line_end=line_start,  # Simplified
                parameters=[],
                complexity=1
            ))
        
        return methods
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract Java imports using regex."""
        imports = []
        
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        
        for match in re.finditer(import_pattern, content):
            import_path = match.group(1).strip()
            package = import_path.split('.')[0]
            if package and package not in imports:
                imports.append(package)
        
        return imports
    
    def _build_dependency_graph(self, file_analyses: Dict[str, FileAnalysis]) -> Dict[str, List[str]]:
        """Build dependency graph from file analyses."""
        dependency_graph = {}
        
        for file_path, analysis in file_analyses.items():
            file_name = os.path.basename(file_path)
            dependency_graph[file_name] = analysis.dependencies[:5]  # Limit for readability
        
        return dependency_graph
    
    def _detect_architecture_patterns(self, file_analyses: Dict[str, FileAnalysis]) -> List[str]:
        """Detect common architecture patterns."""
        patterns = []
        
        # Look for common file/class name patterns
        file_names = [os.path.basename(path).lower() for path in file_analyses.keys()]
        
        # MVC pattern
        if any('controller' in name for name in file_names) and \
           any('model' in name for name in file_names) and \
           any('view' in name for name in file_names):
            patterns.append('MVC (Model-View-Controller)')
        
        # Repository pattern
        if any('repository' in name for name in file_names):
            patterns.append('Repository Pattern')
        
        # Factory pattern
        if any('factory' in name for name in file_names):
            patterns.append('Factory Pattern')
        
        # Service pattern
        if any('service' in name for name in file_names):
            patterns.append('Service Layer Pattern')
        
        return patterns
    
    def _generate_recommendations(self, 
                                file_analyses: Dict[str, FileAnalysis], 
                                overall_complexity: float, 
                                overall_maintainability: float) -> List[str]:
        """Generate code improvement recommendations."""
        recommendations = []
        
        # Complexity recommendations
        if overall_complexity > 15:
            recommendations.append("High overall complexity detected. Consider refactoring complex functions.")
        
        # Maintainability recommendations
        if overall_maintainability < 60:
            recommendations.append("Low maintainability index. Focus on reducing complexity and improving documentation.")
        
        # File-specific recommendations
        high_complexity_files = [
            os.path.basename(path) for path, analysis in file_analyses.items()
            if analysis.complexity_score > 20
        ]
        
        if high_complexity_files:
            recommendations.append(f"High complexity files need refactoring: {', '.join(high_complexity_files[:3])}")
        
        # Documentation recommendations
        poorly_documented_files = [
            os.path.basename(path) for path, analysis in file_analyses.items()
            if not any(func.docstring for func in analysis.functions) and len(analysis.functions) > 0
        ]
        
        if poorly_documented_files:
            recommendations.append(f"Add documentation to: {', '.join(poorly_documented_files[:3])}")
        
        return recommendations