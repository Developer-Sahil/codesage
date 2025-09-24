"""
CodeSage Backend - Test Script
Quick test to verify all modules work correctly.
"""

import os
import sys
import tempfile


def test_imports():
    """Test module imports."""
    print("Testing imports...")
    
    modules = [
        ('filewalker', 'FileWalker'),
        ('analyzer', 'CodeAnalyzer'),
        ('refactorer', 'CodeRefactorer'),
        ('main', 'CodeSageBackend')
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            getattr(module, class_name)
            print(f"  {class_name} imported successfully")
        except ImportError as e:
            print(f"  {class_name} import failed: {e}")
            return False
        except AttributeError as e:
            print(f"  {class_name} not found in module: {e}")
            return False
    
    # Test optional AI import
    try:
        from llm_orchestrator import GroqLLMOrchestrator
        print("  AI features available")
    except ImportError:
        print("  AI features not available (optional)")
    
    return True


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")
    
    # Test FileWalker
    try:
        from filewalker import FileWalker
        walker = FileWalker()
        
        # Test language detection
        if walker._detect_language("test.py") == "Python":
            print("  FileWalker works")
        else:
            print("  FileWalker language detection failed")
            return False
    except Exception as e:
        print(f"  FileWalker test failed: {e}")
        return False
    
    # Test CodeAnalyzer
    try:
        from analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        
        if 'Python' in analyzer.supported_languages:
            print("  CodeAnalyzer works")
        else:
            print("  CodeAnalyzer missing Python support")
            return False
    except Exception as e:
        print(f"  CodeAnalyzer test failed: {e}")
        return False
    
    # Test CodeRefactorer
    try:
        from refactorer import CodeRefactorer
        refactorer = CodeRefactorer()
        
        if 'Python' in refactorer.refactoring_rules:
            print("  CodeRefactorer works")
        else:
            print("  CodeRefactorer missing Python rules")
            return False
    except Exception as e:
        print(f"  CodeRefactorer test failed: {e}")
        return False
    
    # Test main backend
    try:
        from main import CodeSageBackend
        backend = CodeSageBackend()
        
        if hasattr(backend, 'process_repository'):
            print("  CodeSageBackend works")
        else:
            print("  CodeSageBackend missing methods")
            return False
    except Exception as e:
        print(f"  CodeSageBackend test failed: {e}")
        return False
    
    return True


def test_sample_analysis():
    """Test analysis on sample code."""
    print("\nTesting sample analysis...")
    
    sample_code = '''"""Sample module."""

def hello_world():
    """Print hello world."""
    print("Hello, World!")
    return "success"

class Calculator:
    """Simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
'''
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_code)
            temp_file = f.name
        
        # Test analysis
        from analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        
        analysis = analyzer._analyze_python_file(temp_file)
        
        if analysis and len(analysis.functions) > 0 and len(analysis.classes) > 0:
            print(f"  Found {len(analysis.functions)} functions and {len(analysis.classes)} classes")
        else:
            print("  Analysis failed to find code elements")
            return False
        
        # Cleanup
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"  Sample analysis failed: {e}")
        if 'temp_file' in locals():
            try:
                os.unlink(temp_file)
            except:
                pass
        return False
    
    return True


def test_full_workflow():
    """Test complete workflow."""
    print("\nTesting full workflow...")
    
    try:
        from main import CodeSageBackend
        
        # Test with current directory
        backend = CodeSageBackend()
        result = backend.process_repository(
            source=".",
            source_type="local",
            analyze=True,
            refactor=False
        )
        
        if result.success:
            print("  Full workflow successful")
            if result.repository_info:
                print(f"    Files: {result.repository_info.total_files}")
                print(f"    Lines: {result.repository_info.total_lines}")
            return True
        else:
            print(f"  Workflow failed: {result.message}")
            return False
    
    except Exception as e:
        print(f"  Workflow test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("CODESAGE BACKEND TEST SUITE")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_basic_functionality,
        test_sample_analysis,
        test_full_workflow
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"TEST RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("All tests passed! CodeSage is ready to use.")
        print("\nNext steps:")
        print("  python quickstart.py ./your_project")
        print("  python main.py")
        return True
    else:
        print("Some tests failed. Check error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)