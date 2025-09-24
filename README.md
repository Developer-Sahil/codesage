# CodeSage Backend

An AI-powered codebase analysis and refactoring system that helps improve code quality, maintainability, and generates insights about your projects.

## Features

- **Codebase Analysis**: Analyzes code structure, complexity, and quality metrics
- **AI-Powered Insights**: Uses Groq API for intelligent code analysis and suggestions
- **Code Refactoring**: Automated code improvements while preserving functionality
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, and more
- **Repository Mapping**: Complete file tree analysis with metadata
- **Backup & Restore**: Safe refactoring with automatic backups

## Quick Start

### Installation

1. Download all CodeSage files to a directory
2. Run setup script:
```bash
python setup.py
```

3. Set up Groq API key for AI features:
```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

### Basic Usage

**Analysis Only:**
```bash
python quickstart.py ./your_project
```

**Analysis with Refactoring:**
```bash
python quickstart.py --refactor ./your_project
```

**AI-Powered Analysis:**
```bash
python quickstart.py --ai ./your_project
```

**Full Analysis + Refactoring + Backup:**
```bash
python quickstart.py --full ./your_project
```

**Test Installation:**
```bash
python test.py
```

## What Each Mode Does

### `--full` Mode (Comprehensive Workflow)
When you run `python quickstart.py --full ./project_directory_path`, the system:

1. **Scans Directory Structure**: Maps all files, identifies languages, counts lines of code
2. **Analyzes Code Quality**: 
   - Calculates complexity scores for functions and classes
   - Measures maintainability index
   - Detects code smells (long functions, duplicate code, etc.)
   - Identifies architectural patterns
3. **Creates Safety Backup**: Makes complete backup in `.codesage_backup_[timestamp]` folder
4. **Applies Refactoring**:
   - Adds missing docstrings to functions/classes
   - Improves code formatting and spacing
   - Suggests variable name improvements
   - Adds type hints where beneficial
   - Comments out obvious debug code
5. **Exports Results**: Saves detailed report to `codesage_results.json`

**Example Output:**
```
CODESAGE ANALYSIS
==================================================
Project: /path/to/your/project
Mode: full

Analysis completed successfully!

REPOSITORY SUMMARY
Files: 25
Lines: 3,450
Languages: {'Python': 15, 'JavaScript': 8, 'JSON': 2}

CODE ANALYSIS
Files analyzed: 23/25
Complexity: 6.8
Maintainability: 72.5

Top Issues:
  1. Long function: process_data (85 lines)
  2. High complexity function: calculate_metrics (complexity: 12)
  3. Too many parameters in function: initialize_system (8 parameters)

REFACTORING
Files refactored: 15/25
Actions applied: 47
Success rate: 88.0%
Backup: /path/to/project/.codesage_backup_20241223_143022

Results exported to: /path/to/your/project/codesage_results.json
```

### Other Modes
- `--analyze`: Analysis only, no code changes
- `--refactor`: Analysis + refactoring with backup
- `--ai`: Uses AI for enhanced insights (requires GROQ_API_KEY)

## Core Components

### 1. FileWalker (`filewalker.py`)
Maps repository structure and analyzes file metadata:
```python
from filewalker import FileWalker

walker = FileWalker()
file_tree = walker.map_directory("./my_project")
```

### 2. CodeAnalyzer (`analyzer.py`)
Analyzes code structure and quality:
```python
from analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()
analysis = analyzer.analyze_repository(path, file_tree)
```

### 3. CodeRefactorer (`refactorer.py`)
Refactors code with automatic backups:
```python
from refactorer import CodeRefactorer

refactorer = CodeRefactorer()
result = refactorer.refactor_repository(path, analysis)
```

### 4. LLM Orchestrator (`llm_orchestrator.py`)
AI-powered analysis using Groq API:
```python
from llm_orchestrator import GroqLLMOrchestrator

llm = GroqLLMOrchestrator(api_key="your_key")
ai_analysis = await llm.analyze_code_with_llm(code, "Python", file_path)
```

### 5. Main Backend (`main.py`)
Orchestrates all components:
```python
from main import CodeSageBackend

backend = CodeSageBackend(use_ai=True)
result = backend.process_repository("./project", "local")
```

## API Reference

### CodeSageBackend

Main class for processing repositories:

```python
backend = CodeSageBackend(
    workspace_dir="./workspace",  # Working directory
    use_ai=True                   # Enable AI features
)

result = backend.process_repository(
    source="./project",           # Path to analyze
    source_type="local",          # "local", "zip", or "github"
    analyze=True,                 # Perform analysis
    refactor=False,               # Perform refactoring
    use_ai=None                   # Use AI (None = use default)
)
```

### Analysis Results

The system provides comprehensive analysis results:

```python
if result.success:
    # Repository information
    repo_info = result.repository_info
    print(f"Files: {repo_info.total_files}")
    print(f"Lines: {repo_info.total_lines}")
    print(f"Languages: {repo_info.languages}")
    
    # Analysis results
    analysis = result.analysis_results
    print(f"Complexity: {analysis.overall_complexity}")
    print(f"Maintainability: {analysis.overall_maintainability}")
    print(f"Issues: {analysis.code_smells}")
    
    # AI insights (if enabled)
    if result.ai_insights:
        ai = result.ai_insights
        print(f"AI Quality Score: {ai['avg_quality']}")
        print(f"Top Suggestions: {ai['top_suggestions']}")
```

## Configuration

### Environment Variables

- `GROQ_API_KEY`: Required for AI features
- `CODESAGE_WORKSPACE`: Optional workspace directory

### Supported Languages

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C/C++ (.c, .cpp)
- And many more...

## Examples

### Analyze Current Directory
```python
from main import CodeSageBackend

backend = CodeSageBackend()
result = backend.process_repository(".", "local", analyze=True)
```

### Batch Analysis with AI
```python
backend = CodeSageBackend(use_ai=True)
result = backend.process_repository(
    source="./large_project", 
    source_type="local",
    analyze=True, 
    use_ai=True
)

# Export results
backend.export_results(result, "analysis_report.json")
```

### Safe Refactoring
```python
backend = CodeSageBackend()
result = backend.process_repository(
    source="./project", 
    source_type="local",
    analyze=True, 
    refactor=True
)

# Backup is automatically created
if result.refactoring_results:
    print(f"Backup: {result.refactoring_results.backup_directory}")
```

## Error Handling

The system includes comprehensive error handling:

```python
result = backend.process_repository("./project", "local")

if not result.success:
    print(f"Error: {result.message}")
else:
    print("Analysis completed successfully!")
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all files are in the same directory
2. **AI Features Not Working**: Check GROQ_API_KEY environment variable
3. **Permission Errors**: Ensure write permissions for workspace directory

### Debug Mode

Run tests to verify setup:
```bash
python test.py
```

### Verbose Logging

For detailed logging, check the console output during processing.

## Contributing

1. Fork the repository
2. Create feature branches
3. Test thoroughly
4. Submit pull requests

## License

This project is open source. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite
3. Review example usage
4. Check error messages for guidance

---

**Note**: AI features require a valid Groq API key. The system works without AI but provides enhanced insights when enabled.