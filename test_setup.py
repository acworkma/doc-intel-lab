#!/usr/bin/env python3
"""
Test script to verify the Azure Document Intelligence PDF Processor setup.
This script checks if all dependencies are properly installed and configurations are valid.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing Python package imports...")
    
    required_packages = [
        ("azure.identity", "DefaultAzureCredential"),
        ("azure.storage.blob", "BlobServiceClient"),
        ("azure.ai.documentintelligence", "DocumentIntelligenceClient"),
        ("azure.core.credentials", "AzureKeyCredential"),
        ("dotenv", "load_dotenv")
    ]
    
    failed_imports = []
    
    for package_name, class_name in required_packages:
        try:
            module = __import__(package_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {package_name}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {package_name}.{class_name} - {str(e)}")
            failed_imports.append(package_name)
        except AttributeError as e:
            print(f"  ❌ {package_name}.{class_name} - {str(e)}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("   Please run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages imported successfully!")
        return True

def test_environment_file():
    """Test if .env file exists and has basic structure."""
    print("\n🧪 Testing environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Please copy .env.example to .env and configure it.")
        return False
    
    print("✅ .env file exists")
    
    # Check if .env file has content
    try:
        with open(env_file, 'r') as f:
            content = f.read().strip()
            if not content:
                print("⚠️  .env file is empty")
                return False
            
            # Count non-comment, non-empty lines
            config_lines = [line for line in content.split('\n') 
                          if line.strip() and not line.strip().startswith('#')]
            print(f"✅ .env file has {len(config_lines)} configuration lines")
            
    except Exception as e:
        print(f"❌ Error reading .env file: {str(e)}")
        return False
    
    return True

def test_project_structure():
    """Test if project structure is correct."""
    print("\n🧪 Testing project structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".env.example",
        "src/__init__.py",
        "src/azure_client.py",
        "src/pdf_processor.py",
        "src/utils.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present!")
        return True

def test_basic_functionality():
    """Test basic functionality without Azure credentials."""
    print("\n🧪 Testing basic application functionality...")
    
    try:
        # Try to import our modules
        sys.path.insert(0, os.getcwd())
        from src.utils import format_bytes, get_timestamp, ProgressTracker
        
        # Test utility functions
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1048576) == "1.0 MB"
        
        timestamp = get_timestamp()
        assert len(timestamp) > 10  # Basic timestamp validation
        
        # Test progress tracker
        tracker = ProgressTracker(10, "Test")
        tracker.update()
        tracker.finish()
        
        print("✅ Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🔧 Azure Document Intelligence PDF Processor - Setup Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment File", test_environment_file),
        ("Project Structure", test_project_structure),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"🏁 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Configure your .env file with Azure credentials")
        print("2. Run the application: python main.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above and fix them.")
        print("\nCommon solutions:")
        print("- Run: pip install -r requirements.txt")
        print("- Copy .env.example to .env")
        print("- Make sure all project files are present")
        return 1

if __name__ == "__main__":
    sys.exit(main())
