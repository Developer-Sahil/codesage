import os
import json
import tempfile
import shutil
import datetime
from pathlib import Path
import ast
import sys
import traceback

# Import CodeSage modules (assuming these exist and are in the path)
try:
    from filewalker import FileWalker
    from analyzer import CodeAnalyzer, FunctionInfo
    from refactorer import CodeRefactorer
    from main import CodeSageBackend
except ImportError as e:
    print(f"Error importing CodeSage modules: {e}")
    print("Please ensure the required modules (filewalker.py, analyzer.py, refactorer.py, main.py) are available.")
    sys.exit(1)


def create_sample_python_project():
    """Create a sample Python project for testing."""
    
    current_dir = os.getcwd()
    project_path = os.path.join(current_dir, "sample_project")
    
    if os.path.exists(project_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_path = os.path.join(current_dir, f"sample_project_{timestamp}")
    
    os.makedirs(project_path, exist_ok=True)
    
    main_py = '''import os,sys
import json
def process_data(x,y,z):
    if x>0:
        result=[]
        for i in range(100):
            if i%2==0:
                temp=i*2
                if temp>50:
                    for j in range(temp):
                        if j%3==0:
                            result.append(j)
                        else:
                            result.append(j*2)
                else:
                    result.append(temp)
        return result
    else:
        print("debug: x is not positive")
        return []

class DataProcessor:
    def __init__(self,data):
        self.data=data
    def process(self):
        return [x*2 for x in self.data]
'''
    
    utils_py = '''def calculate(a, b):
    return a + b * 2

def validate_input(data):
    if len(data) == 0:
        return False
    return True

class Helper:
    def format_output(self, result):
        return str(result)
    
    def save_to_file(self, data, filename):
        with open(filename, 'w') as f:
            f.write(data)
'''
    
    config_py = '''"""
Configuration module for the sample project.
"""

from typing import Dict, Any


class Config:
    """Configuration class with default settings."""
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.settings = {
            'debug': False,
            'max_workers': 4,
            'timeout': 30
        }
    
    def get_setting(self, key: str) -> Any:
        """
        Get configuration setting by key.
        
        Args:
            key: Setting key to retrieve
            
        Returns:
            Any: Setting value or None if not found
        """
        return self.settings.get(key)
    
    def update_settings(self, new_settings: Dict[str, Any]) -> None:
        """
        Update configuration settings.
        
        Args:
            new_settings: Dictionary of settings to update
        """
        self.settings.update(new_settings)
'''
    
    js_file = '''function calculateTotal(items,tax) {
var total=0;
for(var i=0;i<items.length;i++){
if(items[i].price>0)
total+=items[i].price
}
return total*(1+tax)
}

class ShoppingCart{
constructor(items){
this.items=items||[]
}
addItem(item){
this.items.push(item)
}
}
'''
    
    java_file = '''public class Calculator{
public int add(int a,int b){
return a+b;
}
public int multiply(int a,int b){
int result=0;
for(int i=0;i<b;i++){
result+=a;
}
return result;
}
}'''
    
    with open(os.path.join(project_path, "main.py"), 'w') as f:
        f.write(main_py)
    
    with open(os.path.join(project_path, "utils.py"), 'w') as f:
        f.write(utils_py)
    
    with open(os.path.join(project_path, "config.py"), 'w') as f:
        f.write(config_py)
    
    with open(os.path.join(project_path, "__init__.py"), 'w') as f:
        f.write('"""Sample project package."""\n')
    
    with open(os.path.join(project_path, "requirements.txt"), 'w') as f:
        f.write("requests>=2.25.0\nnumpy>=1.20.0\n")
    
    with open(os.path.join(project_path, "README.md"), 'w') as f:
        f.write("# Sample Project\n\nThis is a sample project for CodeSage testing.\n")
    
    with open(os.path.join(project_path, "shopping.js"), 'w') as f:
        f.write(js_file)
    
    with open(os.path.join(project_path, "Calculator.java"), 'w') as f:
        f.write(java_file)
    
    return project_path


def demonstrate_filewalker(project_path):
    """Demonstrate FileWalker functionality."""
    print("\n" + "="*60)
    print("FILEWALKER DEMONSTRATION")
    print("="*60)
    
    walker = FileWalker()
    file_tree = walker.map_directory(project_path)
    
    if not file_tree:
        print("✗ Failed to map directory")
        return None
        
    print(f"✓ Successfully mapped directory: {project_path}")
    print(f"└── Root: {file_tree['name']}")
    
    stats = file_tree.get('statistics', {})
    print(f"\nStatistics:")
    print(f"  Total files: {stats.get('total_files', 0)}")
    print(f"  Total lines: {stats.get('total_lines', 0)}")
    print(f"  Languages: {stats.get('languages', {})}")
    
    print(f"\nFile Tree:")
    def print_tree(node, indent=""):
        print(f"{indent}├── {node['name']}/" if node.get('type') == 'directory' else f"{indent}├── {node['name']}")
        if node.get('type') == 'file':
            lang = node.get('language', 'Unknown')
            lines = node.get('lines_of_code', 0)
            print(f"{indent}    └── {lang}, {lines} LOC")
        elif node.get('children'):
            for child in node['children']:
                print_tree(child, indent + "    ")
    
    if file_tree.get('children'):
        for child in file_tree['children']:
            print_tree(child)

    return file_tree


def demonstrate_analyzer(project_path):
    """Demonstrate CodeAnalyzer functionality."""
    print("\n" + "="*60)
    print("CODE ANALYZER DEMONSTRATION")
    print("="*60)
    
    walker = FileWalker()
    analyzer = CodeAnalyzer()
    
    file_tree = walker.map_directory(project_path)
    if not file_tree:
        print("✗ Failed to get file tree for analysis")
        return None
    
    analysis = analyzer.analyze_repository(project_path, file_tree)
    
    print(f"✓ Analyzed repository: {project_path}")
    print(f"  Total files: {analysis.total_files}")
    print(f"  Analyzed files: {analysis.analyzed_files}")
    print(f"  Overall complexity: {analysis.overall_complexity:.2f}")
    print(f"  Overall maintainability: {analysis.overall_maintainability:.2f}")
    
    print(f"\nFile Analysis:")
    for file_path, file_analysis in analysis.file_analyses.items():
        filename = os.path.basename(file_path)
        print(f"\n  📄 {filename} ({file_analysis.language})")
        print(f"    Classes: {len(file_analysis.classes)}")
        print(f"    Functions: {len(file_analysis.functions)}")
        print(f"    Dependencies: {len(file_analysis.dependencies)}")
        print(f"    Complexity: {file_analysis.complexity_score:.1f}")
        print(f"    Maintainability: {file_analysis.maintainability_index:.1f}")
        
        if file_analysis.functions:
            print(f"    Functions:")
            for func in file_analysis.functions[:3]:
                print(f"      - {func.name}() [lines {func.line_start}-{func.line_end}, complexity: {func.complexity}]")
        
        if file_analysis.classes:
            print(f"    Classes:")
            for cls in file_analysis.classes:
                print(f"      - {cls.name} [{len(cls.methods)} methods]")
    
    if analysis.code_smells:
        print(f"\n🚨 Code Smells Detected:")
        for smell in analysis.code_smells[:5]:
            print(f"    - {smell}")
    
    if analysis.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in analysis.recommendations:
            print(f"    - {rec}")
    
    return analysis


def demonstrate_refactorer(project_path, analysis):
    """Demonstrate CodeRefactorer functionality."""
    print("\n" + "="*60)
    print("CODE REFACTORER DEMONSTRATION")
    print("="*60)
    
    if not analysis:
        print("✗ No analysis available for refactoring")
        return None
    
    refactorer = CodeRefactorer()
    refactoring_result = refactorer.refactor_repository(project_path, analysis)
    
    print(f"✓ Refactoring completed")
    print(f"  Total files: {refactoring_result.total_files}")
    print(f"  Refactored files: {refactoring_result.refactored_files}")
    print(f"  Success rate: {refactoring_result.success_rate:.1%}")
    print(f"  Total actions: {refactoring_result.total_actions}")
    
    if refactoring_result.backup_directory:
        print(f"  Backup created: {refactoring_result.backup_directory}")
    
    print(f"\nRefactoring Actions:")
    for file_path, file_result in refactoring_result.file_results.items():
        if file_result.success and file_result.actions_applied:
            filename = os.path.basename(file_path)
            print(f"\n  📝 {filename}")
            
            for action in file_result.actions_applied[:5]:
                print(f"    ✨ {action.action_type}: {action.description}")
                print(f"      Confidence: {action.confidence:.1%}")
                if action.refactored_code.strip():
                    preview = action.refactored_code[:60].replace('\n', ' ') + "..." if len(action.refactored_code) > 60 else action.refactored_code.replace('\n', ' ')
                    print(f"      Preview: {preview}")
    
    summary = refactorer.get_refactoring_summary(refactoring_result)
    print(f"\n📊 Refactoring Summary:")
    print(f"    Actions by type: {summary['actions_by_type']}")
    
    return refactoring_result


def demonstrate_full_backend(project_path):
    """Demonstrate complete CodeSage backend workflow."""
    print("\n" + "="*60)
    print("FULL BACKEND DEMONSTRATION")
    print("="*60)
    
    backend = CodeSageBackend()
    result = backend.process_repository(
        source=project_path,
        source_type="local",
        analyze=True,
        refactor=True
    )
    
    if result.success:
        print(f"✓ Repository processing completed successfully")
        if result.repository_info:
            summary = backend.get_repository_summary(result.repository_info)
            print(f"\n📈 Repository Summary:")
            print(f"    Name: {summary['name']}")
            print(f"    Files: {summary['statistics']['total_files']}")
            print(f"    Lines: {summary['statistics']['total_lines']}")
            print(f"    Languages: {summary['statistics']['languages']}")
            print(f"    Analysis complete: {summary['analysis_complete']}")
            
        export_path = os.path.join(project_path, "codesage_results.json")
        if backend.export_results(result, export_path):
            print(f"    Results exported to: {export_path}")
    else:
        print(f"✗ Repository processing failed: {result.message}")
    
    return result


def show_before_after_comparison(project_path):
    """Show before/after code comparison."""
    print("\n" + "="*60)
    print("BEFORE/AFTER CODE COMPARISON")
    print("="*60)
    
    backup_dirs = [d for d in os.listdir(project_path) if d.startswith('.codesage_backup_')]
    if not backup_dirs:
        print("✗ No backup directory found")
        return
    
    backup_dir = os.path.join(project_path, backup_dirs[0])
    main_py_path = os.path.join(project_path, "main.py")
    backup_main_py_path = os.path.join(backup_dir, "main.py")
    
    if os.path.exists(main_py_path) and os.path.exists(backup_main_py_path):
        print(f"\n📄 Comparison: main.py")
        print(f"🔍 BEFORE (first 20 lines):")
        print("-" * 40)
        
        with open(backup_main_py_path, 'r') as f:
            before_lines = f.readlines()[:20]
            for i, line in enumerate(before_lines, 1):
                print(f"{i:2}: {line.rstrip()}")
        
        print(f"\n🔍 AFTER (first 20 lines):")
        print("-" * 40)
        
        with open(main_py_path, 'r') as f:
            after_lines = f.readlines()[:20]
            for i, line in enumerate(after_lines, 1):
                print(f"{i:2}: {line.rstrip()}")


def cleanup_sample_project(project_path):
    """Clean up the sample project directory."""
    try:
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
            print(f"\n🧹 Cleaned up sample project: {project_path}")
        else:
            print(f"\n⚠️  Project path not found: {project_path}")
    except Exception as e:
        print(f"⚠️  Failed to cleanup: {str(e)}")


def show_project_location(project_path):
    """Show the user where the project files are located."""
    print(f"\n📁 SAMPLE PROJECT LOCATION")
    print("="*60)
    print(f"Project created at: {project_path}")
    print(f"Relative path: ./{os.path.basename(project_path)}")
    
    if os.path.exists(project_path):
        print(f"\nFiles created:")
        for root, dirs, files in os.walk(project_path):
            level = root.replace(project_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}📂 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    print(f"{subindent}📄 {file} ({file_size} bytes)")
                except FileNotFoundError:
                    print(f"{subindent}📄 {file} (file not found)")
    
        backup_dirs = [d for d in os.listdir(project_path) if d.startswith('.codesage_backup_')]
        if backup_dirs:
            print(f"\nBackup directories:")
            for backup_dir in backup_dirs:
                print(f"  🗂️  {backup_dir}")
    
    print(f"\n💡 You can now:")
    print(f"  - Examine the refactored code")
    print(f"  - Compare original vs refactored files using the backup")
    print(f"  - Use the files as a reference for your own projects")
    print(f"  - Run CodeSage on your own projects!")


def demo_specific_features():
    """Demonstrate specific features of CodeSage."""
    print("\n" + "="*60)
    print("SPECIFIC FEATURES DEMONSTRATION")
    print("="*60)
    
    print("\n🔧 Testing FileWalker language detection:")
    walker = FileWalker()
    test_files = {
        "test.py": "Python",
        "test.js": "JavaScript", 
        "test.java": "Java",
        "test.cpp": "C++",
        "unknown.xyz": "Unknown"
    }
    
    for filename, expected_lang in test_files.items():
        detected_lang = walker._detect_language(filename)
        status = "✓" if detected_lang == expected_lang else "✗"
        print(f"    {status} {filename} -> {detected_lang} (expected: {expected_lang})")
    
    print(f"\n🔧 Testing CodeAnalyzer complexity calculation:")
    analyzer = CodeAnalyzer()
    
    test_function = """
def complex_function():
    if condition1:
        for i in range(10):
            if condition2:
                while condition3:
                    if condition4:
                        return True
    return False
"""
    
    try:
        tree = ast.parse(test_function)
        func_node = tree.body[0]
        complexity = analyzer._calculate_python_complexity(func_node)
        print(f"    ✓ Complex function complexity: {complexity}")
    except Exception as e:
        print(f"    ✗ Complexity calculation failed: {str(e)}")
    
    print(f"\n🔧 Testing CodeRefactorer docstring generation:")
    refactorer = CodeRefactorer()
    
    test_func_info = FunctionInfo(
        name="calculate_total",
        line_start=1,
        line_end=10,
        parameters=["items", "tax_rate", "discount"],
        return_type="float"
    )
    
    docstring = refactorer._generate_python_docstring(test_func_info)
    print(f"    ✓ Generated docstring:")
    for line in docstring.split('\n'):
        print(f"        {line}")


def main():
    """Run the complete CodeSage backend demonstration."""
    print("🚀 CODESAGE BACKEND DEMONSTRATION")
    print("="*80)
    print("This demo will:")
    print("1. Create a sample Python project with various code issues")
    print("2. Use FileWalker to map the project structure")
    print("3. Use CodeAnalyzer to analyze code quality and structure") 
    print("4. Use CodeRefactorer to improve code quality")
    print("5. Show the complete backend workflow")
    print("6. Display before/after comparisons")
    
    print(f"\n📁 Creating sample project...")
    project_path = create_sample_python_project()
    print(f"✓ Sample project created at: {project_path}")
    
    try:
        file_tree = demonstrate_filewalker(project_path)
        analysis = demonstrate_analyzer(project_path)
        refactoring_result = demonstrate_refactorer(project_path, analysis)
        full_result = demonstrate_full_backend(project_path)
        show_before_after_comparison(project_path)
        
        print("\n" + "="*80)
        print("🎉 DEMONSTRATION COMPLETE")
        print("="*80)
        print("CodeSage backend components demonstrated:")
        print("✓ FileWalker - Repository parsing and file tree mapping")
        print("✓ CodeAnalyzer - Code structure and quality analysis")
        print("✓ CodeRefactorer - Automated code improvement")
        print("✓ Main Backend - Complete workflow orchestration")
        
        if full_result and full_result.success:
            if full_result.analysis_results:
                print(f"\nKey Metrics:")
                print(f"  Overall complexity: {full_result.analysis_results.overall_complexity:.2f}")
                print(f"  Overall maintainability: {full_result.analysis_results.overall_maintainability:.2f}")
                print(f"  Architecture patterns: {full_result.analysis_results.architecture_patterns}")
            
            if full_result.refactoring_results:
                print(f"  Refactoring actions: {full_result.refactoring_results.total_actions}")
                print(f"  Success rate: {full_result.refactoring_results.success_rate:.1%}")
        
        show_project_location(project_path)
        
        keep_files = input(f"\n🗂️  Keep sample project files? (y/n): ").lower().strip()
        if keep_files != 'y':
            cleanup_sample_project(project_path)
        else:
            print(f"\n✅ Sample project preserved at: {project_path}")
            
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        traceback.print_exc()
        
        if 'project_path' in locals() and os.path.exists(project_path):
            print(f"\n📁 Sample project created at: {project_path}")
            keep_files = input(f"🗂️  Keep sample project files despite error? (y/n): ").lower().strip()
            if keep_files != 'y':
                cleanup_sample_project(project_path)
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--features":
        demo_specific_features()
    else:
        main()