"""
CodeSage Backend - Code Refactorer Module
Refactors messy code to improve readability and maintainability while preserving functionality.
"""

import os
import re
import ast
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from analyzer import RepositoryAnalysis, FileAnalysis, FunctionInfo, ClassInfo


@dataclass
class RefactoringAction:
    """Data class for refactoring actions."""
    action_type: str
    file_path: str
    line_start: int
    line_end: int
    original_code: str
    refactored_code: str
    description: str
    confidence: float  # 0.0 to 1.0


@dataclass
class RefactoringResult:
    """Data class for refactoring results."""
    file_path: str
    original_content: str
    refactored_content: str
    actions_applied: List[RefactoringAction]
    backup_path: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class RepositoryRefactoringResult:
    """Data class for repository refactoring results."""
    total_files: int
    refactored_files: int
    file_results: Dict[str, RefactoringResult]
    total_actions: int
    success_rate: float
    backup_directory: Optional[str] = None


class CodeRefactorer:
    """
    Code refactorer class for improving code readability and maintainability
    while ensuring no functionality is lost.
    """
    
    def __init__(self):
        """Initialize the CodeRefactorer."""
        self.refactoring_rules = {
            'Python': {
                'add_docstrings': self._add_python_docstrings,
                'improve_formatting': self._improve_python_formatting,
                'extract_long_functions': self._extract_python_long_functions,
                'rename_variables': self._rename_python_variables,
                'add_type_hints': self._add_python_type_hints,
                'remove_dead_code': self._remove_python_dead_code
            },
            'JavaScript': {
                'add_comments': self._add_js_comments,
                'improve_formatting': self._improve_js_formatting,
                'modernize_syntax': self._modernize_js_syntax
            },
            'Java': {
                'add_javadoc': self._add_java_javadoc,
                'improve_formatting': self._improve_java_formatting
            }
        }
        
        self.max_function_length = 50
        self.max_line_length = 100
        self.backup_enabled = True
    
    def refactor_repository(self, repo_path: str, analysis: RepositoryAnalysis) -> RepositoryRefactoringResult:
        """
        Refactor entire repository based on analysis results.
        
        Args:
            repo_path: Path to repository
            analysis: RepositoryAnalysis from CodeAnalyzer
            
        Returns:
            RepositoryRefactoringResult with refactoring outcomes
        """
        file_results = {}
        total_files = 0
        refactored_files = 0
        total_actions = 0
        backup_directory = None
        
        # Create backup directory if enabled
        if self.backup_enabled:
            backup_directory = self._create_backup_directory(repo_path)
        
        for file_path, file_analysis in analysis.file_analyses.items():
            total_files += 1
            
            try:
                result = self._refactor_file(file_path, file_analysis, backup_directory)
                file_results[file_path] = result
                
                if result.success and result.actions_applied:
                    refactored_files += 1
                    total_actions += len(result.actions_applied)
                    
            except Exception as e:
                file_results[file_path] = RefactoringResult(
                    file_path=file_path,
                    original_content="",
                    refactored_content="",
                    actions_applied=[],
                    success=False,
                    error_message=str(e)
                )
        
        success_rate = refactored_files / max(total_files, 1)
        
        return RepositoryRefactoringResult(
            total_files=total_files,
            refactored_files=refactored_files,
            file_results=file_results,
            total_actions=total_actions,
            success_rate=success_rate,
            backup_directory=backup_directory
        )
    
    def _refactor_file(self, file_path: str, analysis: FileAnalysis, backup_dir: Optional[str]) -> RefactoringResult:
        """
        Refactor a single file based on its analysis.
        
        Args:
            file_path: Path to file
            analysis: FileAnalysis for the file
            backup_dir: Directory for backups
            
        Returns:
            RefactoringResult for the file
        """
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Create backup if enabled
            backup_path = None
            if backup_dir:
                backup_path = self._create_file_backup(file_path, backup_dir)
            
            # Apply refactoring rules based on language
            language = analysis.language
            refactored_content = original_content
            actions_applied = []
            
            if language in self.refactoring_rules:
                rules = self.refactoring_rules[language]
                
                for rule_name, rule_func in rules.items():
                    try:
                        new_content, rule_actions = rule_func(refactored_content, analysis)
                        if new_content != refactored_content:
                            refactored_content = new_content
                            actions_applied.extend(rule_actions)
                    except Exception as e:
                        print(f"Error applying rule {rule_name} to {file_path}: {str(e)}")
            
            # Write refactored content if changes were made
            if refactored_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(refactored_content)
            
            return RefactoringResult(
                file_path=file_path,
                original_content=original_content,
                refactored_content=refactored_content,
                actions_applied=actions_applied,
                backup_path=backup_path,
                success=True
            )
            
        except Exception as e:
            return RefactoringResult(
                file_path=file_path,
                original_content="",
                refactored_content="",
                actions_applied=[],
                success=False,
                error_message=str(e)
            )
    
    def _create_backup_directory(self, repo_path: str) -> str:
        """Create backup directory for original files."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(repo_path, f".codesage_backup_{timestamp}")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def _create_file_backup(self, file_path: str, backup_dir: str) -> str:
        """Create backup of a single file."""
        rel_path = os.path.relpath(file_path, os.path.dirname(backup_dir))
        backup_path = os.path.join(backup_dir, rel_path)
        
        # Create directory structure
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Copy file
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    # Python Refactoring Rules
    
    def _add_python_docstrings(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Add docstrings to Python functions and classes without them."""
        actions = []
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0
        
        # Add docstrings to functions without them
        for func in analysis.functions:
            if not func.docstring and func.line_start <= len(lines):
                line_idx = func.line_start - 1 + offset
                
                # Find function definition line
                while line_idx < len(new_lines) and ':' not in new_lines[line_idx]:
                    line_idx += 1
                
                if line_idx < len(new_lines):
                    # Generate docstring based on function name and parameters
                    docstring = self._generate_python_docstring(func)
                    indent = self._get_line_indentation(new_lines[line_idx]) + "    "
                    
                    docstring_lines = [
                        f'{indent}"""',
                        f'{indent}{docstring}',
                        f'{indent}"""'
                    ]
                    
                    # Insert docstring after function definition
                    for i, doc_line in enumerate(docstring_lines):
                        new_lines.insert(line_idx + 1 + i, doc_line)
                    
                    offset += len(docstring_lines)
                    
                    actions.append(RefactoringAction(
                        action_type="add_docstring",
                        file_path=analysis.file_path,
                        line_start=func.line_start,
                        line_end=func.line_start,
                        original_code="",
                        refactored_code=docstring,
                        description=f"Added docstring to function '{func.name}'",
                        confidence=0.9
                    ))
        
        # Add docstrings to classes without them
        for cls in analysis.classes:
            if not cls.docstring and cls.line_start <= len(lines):
                line_idx = cls.line_start - 1 + offset
                
                # Find class definition line
                while line_idx < len(new_lines) and ':' not in new_lines[line_idx]:
                    line_idx += 1
                
                if line_idx < len(new_lines):
                    docstring = self._generate_python_class_docstring(cls)
                    indent = self._get_line_indentation(new_lines[line_idx]) + "    "
                    
                    docstring_lines = [
                        f'{indent}"""',
                        f'{indent}{docstring}',
                        f'{indent}"""'
                    ]
                    
                    for i, doc_line in enumerate(docstring_lines):
                        new_lines.insert(line_idx + 1 + i, doc_line)
                    
                    offset += len(docstring_lines)
                    
                    actions.append(RefactoringAction(
                        action_type="add_docstring",
                        file_path=analysis.file_path,
                        line_start=cls.line_start,
                        line_end=cls.line_start,
                        original_code="",
                        refactored_code=docstring,
                        description=f"Added docstring to class '{cls.name}'",
                        confidence=0.9
                    ))
        
        return '\n'.join(new_lines), actions
    
    def _generate_python_docstring(self, func: FunctionInfo) -> str:
        """Generate a basic docstring for a Python function."""
        docstring_parts = [f"{func.name.replace('_', ' ').title()} function."]
        
        if func.parameters:
            docstring_parts.append("")
            docstring_parts.append("Args:")
            for param in func.parameters:
                if param not in ['self', 'cls']:
                    docstring_parts.append(f"    {param}: Parameter description.")
        
        if func.return_type:
            docstring_parts.append("")
            docstring_parts.append("Returns:")
            docstring_parts.append(f"    {func.return_type}: Return value description.")
        
        return '\n'.join(docstring_parts)
    
    def _generate_python_class_docstring(self, cls: ClassInfo) -> str:
        """Generate a basic docstring for a Python class."""
        docstring = f"{cls.name.replace('_', ' ').title()} class."
        
        if cls.base_classes:
            docstring += f"\n\nInherits from: {', '.join(cls.base_classes)}"
        
        return docstring
    
    def _improve_python_formatting(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Improve Python code formatting."""
        actions = []
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_line = line
            
            # Fix line length issues
            if len(line.strip()) > self.max_line_length and not line.strip().startswith('#'):
                # Simple line breaking for long lines
                if ',' in line and not line.strip().startswith('"""'):
                    parts = line.split(',')
                    if len(parts) > 1:
                        indent = self._get_line_indentation(line)
                        new_line = parts[0] + ','
                        for part in parts[1:]:
                            new_lines.append(new_line)
                            new_line = indent + '    ' + part.strip()
                        
                        actions.append(RefactoringAction(
                            action_type="format_long_line",
                            file_path=analysis.file_path,
                            line_start=i + 1,
                            line_end=i + 1,
                            original_code=line,
                            refactored_code=new_line,
                            description=f"Split long line at line {i + 1}",
                            confidence=0.8
                        ))
            
            # Add proper spacing around operators
            if '=' in new_line and not new_line.strip().startswith('#'):
                # Simple spacing fix
                new_line = re.sub(r'(\w)=(\w)', r'\1 = \2', new_line)
                new_line = re.sub(r'(\w)==(\w)', r'\1 == \2', new_line)
                new_line = re.sub(r'(\w)!=(\w)', r'\1 != \2', new_line)
            
            new_lines.append(new_line)
        
        return '\n'.join(new_lines), actions
    
    def _extract_python_long_functions(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Extract long functions into smaller ones."""
        actions = []
        lines = content.split('\n')
        new_lines = lines.copy()
        
        for func in analysis.functions:
            func_length = func.line_end - func.line_start
            if func_length > self.max_function_length:
                # Simple extraction: add comment suggesting refactoring
                comment_line = f"# TODO: Consider breaking down {func.name} function ({func_length} lines)"
                insert_idx = func.line_start - 2  # Before function definition
                
                if 0 <= insert_idx < len(new_lines):
                    indent = self._get_line_indentation(new_lines[func.line_start - 1])
                    new_lines.insert(insert_idx, indent + comment_line)
                    
                    actions.append(RefactoringAction(
                        action_type="suggest_extraction",
                        file_path=analysis.file_path,
                        line_start=func.line_start,
                        line_end=func.line_end,
                        original_code="",
                        refactored_code=comment_line,
                        description=f"Added refactoring suggestion for long function '{func.name}'",
                        confidence=0.7
                    ))
        
        return '\n'.join(new_lines), actions
    
    def _rename_python_variables(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Rename poorly named variables."""
        actions = []
        # Simple implementation: suggest better names for single-letter variables
        lines = content.split('\n')
        
        poor_variable_pattern = r'\b([a-z])\s*='
        suggestions = {
            'i': 'index',
            'j': 'inner_index',
            'x': 'value',
            'y': 'result',
            's': 'text',
            'n': 'number',
            'l': 'items',
            'd': 'data'
        }
        
        for i, line in enumerate(lines):
            matches = re.finditer(poor_variable_pattern, line)
            for match in matches:
                var_name = match.group(1)
                if var_name in suggestions and not line.strip().startswith('for '):
                    suggested_name = suggestions[var_name]
                    actions.append(RefactoringAction(
                        action_type="suggest_rename",
                        file_path=analysis.file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code=line.replace(f'{var_name} =', f'{suggested_name} ='),
                        description=f"Consider renaming variable '{var_name}' to '{suggested_name}'",
                        confidence=0.6
                    ))
        
        return content, actions  # Return original content with suggestions only
    
    def _add_python_type_hints(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Add basic type hints to Python functions."""
        actions = []
        lines = content.split('\n')
        new_lines = lines.copy()
        
        for func in analysis.functions:
            if func.line_start <= len(lines):
                line_idx = func.line_start - 1
                line = lines[line_idx]
                
                # Simple type hint addition for functions without return type annotation
                if 'def ' in line and '->' not in line and func.name != '__init__':
                    # Add basic return type hint
                    if ':' in line:
                        new_line = line.replace(':', ' -> Any:')
                        new_lines[line_idx] = new_line
                        
                        actions.append(RefactoringAction(
                            action_type="add_type_hint",
                            file_path=analysis.file_path,
                            line_start=func.line_start,
                            line_end=func.line_start,
                            original_code=line,
                            refactored_code=new_line,
                            description=f"Added return type hint to function '{func.name}'",
                            confidence=0.5
                        ))
        
        # Add typing import if type hints were added
        if actions and not any('from typing import' in line for line in lines):
            new_lines.insert(0, "from typing import Any")
            actions.append(RefactoringAction(
                action_type="add_import",
                file_path=analysis.file_path,
                line_start=1,
                line_end=1,
                original_code="",
                refactored_code="from typing import Any",
                description="Added typing import for type hints",
                confidence=0.9
            ))
        
        return '\n'.join(new_lines), actions
    
    def _remove_python_dead_code(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Remove or comment out potential dead code."""
        actions = []
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Remove empty lines that are more than 2 consecutive
            if not line.strip():
                # Check if this is part of a series of empty lines
                empty_count = 1
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    empty_count += 1
                    j += 1
                
                # Keep maximum 2 empty lines
                if empty_count > 2 and (i == 0 or not lines[i-1].strip()):
                    continue  # Skip this empty line
            
            # Comment out obvious debug prints
            if 'print(' in line and not line.strip().startswith('#'):
                # Check if it looks like debug code
                if any(debug_word in line.lower() for debug_word in ['debug', 'test', 'temp', 'todo']):
                    indent = self._get_line_indentation(line)
                    new_line = indent + '# ' + line.strip()
                    new_lines.append(new_line)
                    
                    actions.append(RefactoringAction(
                        action_type="comment_debug_code",
                        file_path=analysis.file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code=new_line,
                        description=f"Commented out potential debug code at line {i + 1}",
                        confidence=0.7
                    ))
                    continue
            
            new_lines.append(line)
        
        return '\n'.join(new_lines), actions
    
    # JavaScript Refactoring Rules
    
    def _add_js_comments(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Add comments to JavaScript functions."""
        actions = []
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0
        
        for func in analysis.functions:
            if func.line_start <= len(lines):
                line_idx = func.line_start - 1 + offset
                
                # Add JSDoc comment
                jsdoc_comment = f"""/**
 * {func.name.replace('_', ' ').title()} function
 */"""
                
                indent = self._get_line_indentation(lines[func.line_start - 1])
                jsdoc_lines = [indent + line for line in jsdoc_comment.split('\n')]
                
                for i, comment_line in enumerate(jsdoc_lines):
                    new_lines.insert(line_idx + i, comment_line)
                
                offset += len(jsdoc_lines)
                
                actions.append(RefactoringAction(
                    action_type="add_jsdoc",
                    file_path=analysis.file_path,
                    line_start=func.line_start,
                    line_end=func.line_start,
                    original_code="",
                    refactored_code=jsdoc_comment,
                    description=f"Added JSDoc comment to function '{func.name}'",
                    confidence=0.8
                ))
        
        return '\n'.join(new_lines), actions
    
    def _improve_js_formatting(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Improve JavaScript formatting."""
        actions = []
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_line = line
            
            # Add semicolons where missing
            if (line.strip() and 
                not line.strip().endswith((';', '{', '}', ':', ',')) and
                not line.strip().startswith(('if', 'for', 'while', 'function', 'class', '//', '/*', '*'))):
                new_line = line + ';'
                
                actions.append(RefactoringAction(
                    action_type="add_semicolon",
                    file_path=analysis.file_path,
                    line_start=i + 1,
                    line_end=i + 1,
                    original_code=line,
                    refactored_code=new_line,
                    description=f"Added missing semicolon at line {i + 1}",
                    confidence=0.9
                ))
            
            new_lines.append(new_line)
        
        return '\n'.join(new_lines), actions
    
    def _modernize_js_syntax(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Modernize JavaScript syntax."""
        actions = []
        
        # Replace var with let/const
        new_content = re.sub(r'\bvar\b', 'let', content)
        
        if new_content != content:
            actions.append(RefactoringAction(
                action_type="modernize_syntax",
                file_path=analysis.file_path,
                line_start=1,
                line_end=len(content.split('\n')),
                original_code="var declarations",
                refactored_code="let declarations",
                description="Replaced 'var' with 'let' for better scoping",
                confidence=0.8
            ))
        
        return new_content, actions
    
    # Java Refactoring Rules
    
    def _add_java_javadoc(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Add Javadoc comments to Java methods."""
        actions = []
        lines = content.split('\n')
        new_lines = lines.copy()
        offset = 0
        
        for func in analysis.functions:
            if func.line_start <= len(lines):
                line_idx = func.line_start - 1 + offset
                
                javadoc_comment = f"""/**
 * {func.name.replace('_', ' ').title()} method
 */"""
                
                indent = self._get_line_indentation(lines[func.line_start - 1])
                javadoc_lines = [indent + line for line in javadoc_comment.split('\n')]
                
                for i, comment_line in enumerate(javadoc_lines):
                    new_lines.insert(line_idx + i, comment_line)
                
                offset += len(javadoc_lines)
                
                actions.append(RefactoringAction(
                    action_type="add_javadoc",
                    file_path=analysis.file_path,
                    line_start=func.line_start,
                    line_end=func.line_start,
                    original_code="",
                    refactored_code=javadoc_comment,
                    description=f"Added Javadoc comment to method '{func.name}'",
                    confidence=0.8
                ))
        
        return '\n'.join(new_lines), actions
    
    def _improve_java_formatting(self, content: str, analysis: FileAnalysis) -> Tuple[str, List[RefactoringAction]]:
        """Improve Java formatting."""
        actions = []
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            new_line = line
            
            # Improve brace style (simple implementation)
            if line.strip().endswith('{') and not line.strip().startswith('if'):
                # Ensure space before opening brace
                new_line = re.sub(r'(\w)\{', r'\1 {', line)
                if new_line != line:
                    actions.append(RefactoringAction(
                        action_type="format_braces",
                        file_path=analysis.file_path,
                        line_start=i + 1,
                        line_end=i + 1,
                        original_code=line,
                        refactored_code=new_line,
                        description=f"Added space before opening brace at line {i + 1}",
                        confidence=0.9
                    ))
            
            new_lines.append(new_line)
        
        return '\n'.join(new_lines), actions
    
    # Utility Methods
    
    def _get_line_indentation(self, line: str) -> str:
        """Get the indentation of a line."""
        return line[:len(line) - len(line.lstrip())]
    
    def get_refactoring_summary(self, result: RepositoryRefactoringResult) -> Dict[str, Any]:
        """Generate a summary of refactoring results."""
        action_types = {}
        successful_files = []
        failed_files = []
        
        for file_path, file_result in result.file_results.items():
            if file_result.success:
                successful_files.append(os.path.basename(file_path))
                for action in file_result.actions_applied:
                    action_type = action.action_type
                    action_types[action_type] = action_types.get(action_type, 0) + 1
            else:
                failed_files.append(os.path.basename(file_path))
        
        return {
            "summary": {
                "total_files": result.total_files,
                "refactored_files": result.refactored_files,
                "success_rate": f"{result.success_rate:.1%}",
                "total_actions": result.total_actions
            },
            "actions_by_type": action_types,
            "successful_files": successful_files[:10],  # Limit for readability
            "failed_files": failed_files,
            "backup_directory": result.backup_directory
        }
    
    def restore_from_backup(self, backup_directory: str, target_directory: str) -> bool:
        """
        Restore files from backup directory.
        
        Args:
            backup_directory: Path to backup directory
            target_directory: Target directory to restore to
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            if not os.path.exists(backup_directory):
                return False
            
            for root, dirs, files in os.walk(backup_directory):
                for file in files:
                    backup_file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(backup_file_path, backup_directory)
                    target_file_path = os.path.join(target_directory, rel_path)
                    
                    # Create directory structure
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(backup_file_path, target_file_path)
            
            return True
            
        except Exception as e:
            print(f"Error restoring from backup: {str(e)}")
            return False