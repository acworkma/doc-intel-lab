#!/usr/bin/env python3
"""
Comprehensive test runner for all Azure Document Intelligence PDF Processor components.
This script runs all tests in sequence and provides a complete status report.
"""

import sys
import subprocess
import time
from datetime import datetime


def run_test(test_name, script_name, description):
    """Run a single test and return the result."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}")
    print(f"   {description}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              timeout=120)  # 2 minute timeout
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {test_name} PASSED ({duration:.1f}s)")
            return True, duration, None
        else:
            print(f"\n❌ {test_name} FAILED ({duration:.1f}s)")
            return False, duration, f"Exit code: {result.returncode}"
            
    except subprocess.TimeoutExpired:
        print(f"\n⏰ {test_name} TIMEOUT")
        return False, 120, "Test timed out after 2 minutes"
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n💥 {test_name} ERROR ({duration:.1f}s)")
        return False, duration, str(e)


def main():
    """Run all tests and provide comprehensive report."""
    print("🔧 Azure Document Intelligence PDF Processor - Full Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Define all tests
    tests = [
        ("Setup Validation", "test_setup.py", "Validates project setup and Python dependencies"),
        ("Azure CLI Authentication", "test_auth.py", "Tests Azure CLI authentication and permissions"),
        ("Storage Connectivity", "test_storage.py", "Tests Azure Storage account access and container permissions"),
        ("Document Intelligence", "test_document_intelligence.py", "Tests Azure Document Intelligence service connectivity"),
    ]
    
    # Run all tests
    results = []
    total_duration = 0
    
    for test_name, script_name, description in tests:
        passed, duration, error = run_test(test_name, script_name, description)
        results.append((test_name, passed, duration, error))
        total_duration += duration
        
        # Small delay between tests
        time.sleep(1)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST REPORT")
    print('='*80)
    
    passed_tests = sum(1 for _, passed, _, _ in results if passed)
    total_tests = len(results)
    
    print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
    print(f"Total Duration: {total_duration:.1f} seconds")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n📋 Individual Test Results:")
    print("-" * 60)
    
    for test_name, passed, duration, error in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status:<8} ({duration:>5.1f}s)")
        if error and not passed:
            print(f"                          Error: {error}")
    
    # Detailed analysis
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Your Azure Document Intelligence PDF Processor is ready to use!")
        print("\nNext steps:")
        print("   1. Upload PDF files to your source container")
        print("   2. Run the main application: python3 main.py")
        print("   3. Check the output container for processed PDFs")
        
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        print("Please resolve the issues before running the main application:")
        
        # Provide specific guidance based on which tests failed
        failed_tests = [name for name, passed, _, _ in results if not passed]
        
        if "Setup Validation" in failed_tests:
            print("   - Fix Python dependencies: pip install -r requirements.txt")
            
        if "Azure CLI Authentication" in failed_tests:
            print("   - Run: az login")
            print("   - Ensure you have appropriate Azure permissions")
            
        if "Storage Connectivity" in failed_tests:
            print("   - Check storage account name in .env file")
            print("   - Verify containers exist")
            print("   - Ensure you have Storage Blob Data Contributor role")
            
        if "Document Intelligence" in failed_tests:
            print("   - Check Document Intelligence endpoint and key in .env file")
            print("   - Ensure you have Cognitive Services User role")
    
    # Performance insights
    print(f"\n⚡ Performance Insights:")
    slowest_test = max(results, key=lambda x: x[2])
    fastest_test = min(results, key=lambda x: x[2])
    
    print(f"   Slowest test: {slowest_test[0]} ({slowest_test[2]:.1f}s)")
    print(f"   Fastest test: {fastest_test[0]} ({fastest_test[2]:.1f}s)")
    
    if total_duration > 60:
        print(f"   Note: Total test time was {total_duration/60:.1f} minutes")
    
    # Return appropriate exit code
    return 0 if passed_tests == total_tests else 1


if __name__ == "__main__":
    exit_code = main()
    print(f"\nTest suite completed with exit code: {exit_code}")
    sys.exit(exit_code)
