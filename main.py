#!/usr/bin/env python3
"""
CodeSage Backend - Main Application Module
A comprehensive backend system for analyzing and refactoring codebases.
"""

import os
import json
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from env_loader import load_env_file
    load_env_file()
except ImportError:
    pass

try:
    from filewalker import FileWalker
    from analyzer import CodeAnalyzer
    from refactorer import CodeRefactorer
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all CodeSage modules are in the same directory.")
    exit(1)

# Optional AI import
try:
    from llm_orchestrator import GroqLLMOrchestrator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


@dataclass
class RepositoryInfo:
    """Repository information."""
    name: str
    path: str
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    created_at: str
    analysis_complete: bool = False
    ai_analysis_complete: bool = False


@dataclass
class ProcessingResult:
    """Processing results."""
    success: bool
    message: str
    repository_info: Optional[RepositoryInfo] = None
    file_tree: Optional[Dict] = None
    analysis_results: Optional[Any] = None
    refactoring_results: Optional[Any] = None
    ai_analysis_results: Optional[Dict] = None
    ai_insights: Optional[Dict] = None


class CodeSageBackend:
    """Main backend class for CodeSage application."""
    
    def __init__(self, workspace_dir: str = "./codesage_workspace", use_ai: bool = False):
        """Initialize the CodeSage backend."""
        self.workspace_dir = workspace_dir
        self.use_ai = use_ai and AI_AVAILABLE
        self.file_walker = FileWalker()
        self.analyzer = CodeAnalyzer()
        self.refactorer = CodeRefactorer()
        self.llm_orchestrator = None
        
        if self.use_ai:
            self._initialize_ai()
        
        os.makedirs(workspace_dir, exist_ok=True)
    
    def _initialize_ai(self):
        """Initialize AI features."""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                self.llm_orchestrator = GroqLLMOrchestrator(api_key=api_key)
                print("AI features enabled")
            except Exception as e:
                print(f"AI initialization failed: {str(e)}")
                self.use_ai = False
        else:
            print("GROQ_API_KEY not found. AI features disabled.")
            self.use_ai = False
    
    def process_repository(self, 
                         source: str, 
                         source_type: str = "local",
                         analyze: bool = True,
                         refactor: bool = False,
                         use_ai: bool = None) -> ProcessingResult:
        """Process a repository from various sources."""
        if use_ai is None:
            use_ai = self.use_ai
        
        try:
            # Extract repository
            repo_path = self._extract_repository(source, source_type)
            if not repo_path:
                return ProcessingResult(False, "Failed to extract repository")
            
            # Map file tree
            file_tree = self.file_walker.map_directory(repo_path)
            if not file_tree:
                return ProcessingResult(False, "Failed to map file tree")
            
            repo_info = self._create_repository_info(repo_path, file_tree)
            
            # Analysis
            analysis_results = None
            if analyze:
                analysis_results = self.analyzer.analyze_repository(repo_path, file_tree)
                repo_info.analysis_complete = True
            
            # AI analysis
            ai_analysis_results = None
            ai_insights = None
            if use_ai and self.llm_orchestrator:
                print("Running AI analysis...")
                ai_analysis_results = self._run_ai_analysis(repo_path, file_tree)
                if ai_analysis_results:
                    repo_info.ai_analysis_complete = True
                    ai_insights = self._get_ai_insights(ai_analysis_results)
            
            # Refactoring
            refactoring_results = None
            if refactor and analysis_results:
                refactoring_results = self.refactorer.refactor_repository(repo_path, analysis_results)
            
            return ProcessingResult(
                success=True,
                message="Repository processed successfully" + (" with AI" if use_ai else ""),
                repository_info=repo_info,
                file_tree=file_tree,
                analysis_results=analysis_results,
                refactoring_results=refactoring_results,
                ai_analysis_results=ai_analysis_results,
                ai_insights=ai_insights
            )
            
        except Exception as e:
            return ProcessingResult(False, f"Error processing repository: {str(e)}")
    
    def _extract_repository(self, source: str, source_type: str) -> Optional[str]:
        """Extract repository from different sources."""
        if source_type == "local":
            return source if os.path.exists(source) else None
        elif source_type == "zip":
            return self._extract_zip_repository(source)
        elif source_type == "github":
            return self._clone_github_repository(source)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _extract_zip_repository(self, zip_path: str) -> Optional[str]:
        """Extract repository from ZIP file."""
        import zipfile
        
        if not os.path.exists(zip_path):
            return None
        
        repo_name = os.path.splitext(os.path.basename(zip_path))[0]
        extract_path = os.path.join(self.workspace_dir, repo_name)
        
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            return extract_path
        except zipfile.BadZipFile:
            return None
    
    def _clone_github_repository(self, github_url: str) -> Optional[str]:
        """Clone repository from GitHub URL."""
        import subprocess
        
        try:
            repo_name = github_url.split("/")[-1].replace(".git", "")
            clone_path = os.path.join(self.workspace_dir, repo_name)
            
            if os.path.exists(clone_path):
                shutil.rmtree(clone_path)
            
            result = subprocess.run([
                "git", "clone", github_url, clone_path
            ], capture_output=True, text=True, timeout=300)
            
            return clone_path if result.returncode == 0 else None
                
        except Exception:
            return None
    
    def _run_ai_analysis(self, repo_path: str, file_tree: Dict) -> Optional[Dict]:
        """Run AI analysis on repository files."""
        if not self.llm_orchestrator:
            return None
        
        try:
            code_files = []
            self._collect_code_files(file_tree, code_files)
            
            if not code_files:
                return None
            
            # Limit files for efficiency
            code_files = code_files[:5]
            
            files_data = []
            for file_info in code_files:
                try:
                    with open(file_info['path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                    files_data.append((file_info['path'], content, file_info['language']))
                except Exception:
                    continue
            
            if files_data:
                return self.llm_orchestrator.analyze_files_batch(files_data)
            
        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            return None
        
        return None
    
    def _collect_code_files(self, node: Dict, code_files: List[Dict]):
        """Collect code files from file tree."""
        if node.get('type') == 'file':
            language = node.get('language', 'Unknown')
            if language in ['Python', 'JavaScript', 'TypeScript', 'Java'] and node.get('lines_of_code', 0) > 10:
                code_files.append({
                    'path': node['path'],
                    'language': language,
                    'lines': node.get('lines_of_code', 0)
                })
        elif node.get('children'):
            for child in node['children']:
                self._collect_code_files(child, code_files)
    
    def _get_ai_insights(self, ai_results: Dict) -> Dict:
        """Generate insights from AI analysis results."""
        if not ai_results:
            return {}
        
        total_files = len(ai_results)
        avg_complexity = sum(r.ai_complexity_score for r in ai_results.values()) / total_files
        avg_quality = sum(r.ai_quality_score for r in ai_results.values()) / total_files
        
        all_issues = []
        all_suggestions = []
        for analysis in ai_results.values():
            all_issues.extend(analysis.code_smells)
            all_suggestions.extend(analysis.improvement_suggestions)
        
        return {
            "files_analyzed": total_files,
            "avg_complexity": round(avg_complexity, 2),
            "avg_quality": round(avg_quality, 2),
            "top_issues": list(set(all_issues))[:10],
            "top_suggestions": list(set(all_suggestions))[:10]
        }
    
    def _create_repository_info(self, repo_path: str, file_tree: Dict) -> RepositoryInfo:
        """Create repository information from file tree."""
        repo_name = os.path.basename(repo_path)
        
        total_files = 0
        total_lines = 0
        languages = {}
        
        def count_recursive(node):
            nonlocal total_files, total_lines
            if node.get("type") == "file":
                total_files += 1
                total_lines += node.get("lines_of_code", 0)
                lang = node.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
            elif node.get("children"):
                for child in node["children"]:
                    count_recursive(child)
        
        count_recursive(file_tree)
        
        return RepositoryInfo(
            name=repo_name,
            path=repo_path,
            total_files=total_files,
            total_lines=total_lines,
            languages=languages,
            created_at=datetime.now().isoformat()
        )
    
    def get_repository_summary(self, repo_info: RepositoryInfo) -> Dict[str, Any]:
        """Generate a summary of the repository."""
        return {
            "name": repo_info.name,
            "statistics": {
                "total_files": repo_info.total_files,
                "total_lines": repo_info.total_lines,
                "languages": repo_info.languages
            },
            "analysis_complete": repo_info.analysis_complete,
            "ai_analysis_complete": repo_info.ai_analysis_complete,
            "created_at": repo_info.created_at
        }
    
    def export_results(self, result: ProcessingResult, output_path: str) -> bool:
        """Export processing results to JSON file."""
        try:
            export_data = {
                "success": result.success,
                "message": result.message,
                "repository_info": asdict(result.repository_info) if result.repository_info else None,
                "file_tree": result.file_tree,
                "analysis_results": self._serialize_analysis(result.analysis_results),
                "refactoring_results": self._serialize_refactoring(result.refactoring_results),
                "ai_analysis_results": self._serialize_ai_analysis(result.ai_analysis_results),
                "ai_insights": result.ai_insights,
                "exported_at": datetime.now().isoformat(),
                "ai_enabled": self.use_ai
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Export failed: {str(e)}")
            return False
    
    def _serialize_analysis(self, analysis):
        """Serialize analysis results for JSON export."""
        if not analysis:
            return None
        return {
            "total_files": analysis.total_files,
            "analyzed_files": analysis.analyzed_files,
            "overall_complexity": analysis.overall_complexity,
            "overall_maintainability": analysis.overall_maintainability,
            "code_smells": analysis.code_smells[:10],
            "recommendations": analysis.recommendations
        }
    
    def _serialize_refactoring(self, refactoring):
        """Serialize refactoring results for JSON export."""
        if not refactoring:
            return None
        return {
            "total_files": refactoring.total_files,
            "refactored_files": refactoring.refactored_files,
            "success_rate": refactoring.success_rate,
            "total_actions": refactoring.total_actions
        }
    
    def _serialize_ai_analysis(self, ai_analysis):
        """Serialize AI analysis results for JSON export."""
        if not ai_analysis:
            return None
        
        serialized = {}
        for file_path, analysis in ai_analysis.items():
            serialized[file_path] = {
                "complexity_score": analysis.ai_complexity_score,
                "quality_score": analysis.ai_quality_score,
                "code_smells": analysis.code_smells[:5],
                "suggestions": analysis.improvement_suggestions[:5],
                "technical_debt": analysis.estimated_technical_debt
            }
        
        return serialized
    
    def is_ai_enabled(self) -> bool:
        """Check if AI features are enabled."""
        return self.use_ai and self.llm_orchestrator is not None


def main():
    """Example usage of CodeSage backend."""
    print("CodeSage Backend")
    print("-" * 30)
    
    # Check AI availability
    ai_key = os.getenv("GROQ_API_KEY")
    use_ai = bool(ai_key and AI_AVAILABLE)
    
    print(f"AI Features: {'Available' if use_ai else 'Not Available'}")
    if not use_ai and not ai_key:
        print("   Set GROQ_API_KEY to enable AI features")
    
    # Initialize backend
    backend = CodeSageBackend(use_ai=use_ai)
    
    # Test with current directory
    source_path = "."
    if os.path.exists(source_path):
        print(f"\nProcessing: {source_path}")
        
        result = backend.process_repository(
            source=source_path,
            source_type="local",
            analyze=True,
            refactor=False,
            use_ai=use_ai
        )
        
        if result.success:
            print("Success!")
            if result.repository_info:
                summary = backend.get_repository_summary(result.repository_info)
                print(f"   Files: {summary['statistics']['total_files']}")
                print(f"   Lines: {summary['statistics']['total_lines']}")
                print(f"   Languages: {summary['statistics']['languages']}")
                
            # Export results
            export_file = "codesage_results.json"
            if backend.export_results(result, export_file):
                print(f"   Exported: {export_file}")
        else:
            print(f"Failed: {result.message}")


if __name__ == "__main__":
    main()