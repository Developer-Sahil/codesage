#!/usr/bin/env python3
"""
CodeSage Backend - Quick Start Script
Analyze any directory with CodeSage backend.

Usage:
    python quickstart.py [directory_path]
    python quickstart.py --analyze [directory_path] 
    python quickstart.py --refactor [directory_path]
    python quickstart.py --full [directory_path]
    python quickstart.py --ai [directory_path]

Examples:
    python quickstart.py ./my_project
    python quickstart.py --refactor ./src
    python quickstart.py --ai ../other_project
"""

import sys
import os
from main import CodeSageBackend


def print_usage():
    """Print usage instructions."""
    print(__doc__)


def analyze_project(project_path, mode='analyze'):
    """Analyze a project using CodeSage backend."""
    
    if not os.path.exists(project_path):
        print(f"Error: Directory '{project_path}' does not exist.")
        return False
    
    if not os.path.isdir(project_path):
        print(f"Error: '{project_path}' is not a directory.")
        return False
    
    # Determine settings based on mode
    settings = {
        'analyze': {'analyze': True, 'refactor': False, 'use_ai': False},
        'refactor': {'analyze': True, 'refactor': True, 'use_ai': False},
        'full': {'analyze': True, 'refactor': True, 'use_ai': False},
        'ai': {'analyze': True, 'refactor': False, 'use_ai': True}
    }
    
    config = settings.get(mode, settings['analyze'])
    
    print(f"CODESAGE ANALYSIS")
    print("=" * 50)
    print(f"Project: {os.path.abspath(project_path)}")
    print(f"Mode: {mode}")
    
    # Initialize backend
    backend = CodeSageBackend(use_ai=config['use_ai'])
    
    # Process repository
    result = backend.process_repository(
        source=project_path,
        source_type="local",
        analyze=config['analyze'],
        refactor=config['refactor'],
        use_ai=config['use_ai']
    )
    
    if not result.success:
        print(f"Analysis failed: {result.message}")
        return False
    
    print("Analysis completed successfully!")
    
    # Show results
    _show_results(result, backend)
    
    # Export results
    results_file = os.path.join(project_path, "codesage_results.json")
    if backend.export_results(result, results_file):
        print(f"\nResults exported to: {results_file}")
    
    print("\nAnalysis complete!")
    return True


def _show_results(result, backend):
    """Display analysis results."""
    # Repository summary
    if result.repository_info:
        summary = backend.get_repository_summary(result.repository_info)
        print(f"\nREPOSITORY SUMMARY")
        print("-" * 30)
        print(f"Name: {summary['name']}")
        print(f"Files: {summary['statistics']['total_files']}")
        print(f"Lines: {summary['statistics']['total_lines']}")
        print(f"Languages: {summary['statistics']['languages']}")
    
    # Analysis results
    if result.analysis_results:
        analysis = result.analysis_results
        print(f"\nCODE ANALYSIS")
        print("-" * 30)
        print(f"Files analyzed: {analysis.analyzed_files}/{analysis.total_files}")
        print(f"Complexity: {analysis.overall_complexity:.2f}")
        print(f"Maintainability: {analysis.overall_maintainability:.2f}")
        
        if analysis.code_smells:
            print(f"\nTop Issues:")
            for i, issue in enumerate(analysis.code_smells[:3], 1):
                print(f"  {i}. {issue}")
        
        if analysis.recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(analysis.recommendations[:3], 1):
                print(f"  {i}. {rec}")
    
    # AI results
    if result.ai_insights:
        ai = result.ai_insights
        print(f"\nAI INSIGHTS")
        print("-" * 30)
        print(f"Quality Score: {ai['avg_quality']}/10")
        print(f"Complexity Score: {ai['avg_complexity']}/10")
        
        if ai['top_suggestions']:
            print(f"Top AI Suggestion: {ai['top_suggestions'][0]}")
    
    # Refactoring results
    if result.refactoring_results:
        refact = result.refactoring_results
        print(f"\nREFACTORING")
        print("-" * 30)
        print(f"Files refactored: {refact.refactored_files}/{refact.total_files}")
        print(f"Actions applied: {refact.total_actions}")
        print(f"Success rate: {refact.success_rate:.1%}")
        
        if refact.backup_directory:
            print(f"Backup: {refact.backup_directory}")


def main():
    """Main function."""
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help', 'help']:
        print_usage()
        return
    
    # Parse arguments
    mode = 'analyze'
    project_path = '.'
    
    for arg in args:
        if arg.startswith('--'):
            mode = arg[2:]  # Remove --
        elif not arg.startswith('-'):
            project_path = arg
    
    # Validate mode
    valid_modes = ['analyze', 'refactor', 'full', 'ai']
    if mode not in valid_modes:
        print(f"Invalid mode: {mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        return
    
    # Run analysis
    success = analyze_project(project_path, mode)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()