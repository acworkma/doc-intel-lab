#!/usr/bin/env python3
"""
Quick authentication test for Azure CLI credentials.
This script tests Azure CLI authentication (requires 'az login' to be run first).
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError


def check_azure_cli():
    """Check if Azure CLI is installed and user is logged in."""
    print("� Checking Azure CLI status...")
    
    try:
        # Check if Azure CLI is installed
        result = subprocess.run(['az', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Azure CLI is not installed or not working")
            print("   Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
        
        print("✅ Azure CLI is installed")
        
        # Check if user is logged in
        result = subprocess.run(['az', 'account', 'show'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Not logged in to Azure CLI")
            print("   Please run: az login")
            return False
        
        # Parse the account info
        import json
        account_info = json.loads(result.stdout)
        print(f"✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
        print(f"   Subscription: {account_info.get('name', 'Unknown')} ({account_info.get('id', 'Unknown')})")
        print(f"   Tenant: {account_info.get('tenantId', 'Unknown')}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Azure CLI command timed out")
        return False
    except FileNotFoundError:
        print("❌ Azure CLI is not installed")
        print("   Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    except json.JSONDecodeError:
        print("❌ Could not parse Azure CLI output")
        return False
    except Exception as e:
        print(f"❌ Error checking Azure CLI: {str(e)}")
        return False


def test_authentication():
    """Test Azure authentication with DefaultAzureCredential."""
    print("\n🔐 Testing Azure Authentication...")
    print("=" * 50)
    
    try:
        print("🧪 Testing DefaultAzureCredential...")
        
        # Create credential object (this will use Azure CLI auth)
        credential = DefaultAzureCredential()
        
        # Try to get a token for Azure Resource Manager
        token = credential.get_token("https://management.azure.com/.default")
        
        if token and token.token:
            print("✅ Authentication successful!")
            print(f"   Token type: Azure CLI")
            print(f"   Token expires: {token.expires_on}")
            return True
        else:
            print("❌ Authentication failed: No token received")
            return False
            
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("\nPossible solutions:")
        print("   - Run 'az login' to authenticate")
        print("   - Check if your Azure CLI session has expired")
        print("   - Verify you have access to the subscription")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print("\nPossible solutions:")
        print("   - Run 'az login' to authenticate")
        print("   - Make sure Azure CLI is installed and working")
        return False


def test_credentials_format():
    """Check if required configuration (non-auth) is present."""
    print("\n🔍 Validating configuration...")
    
    # Load environment variables
    load_dotenv()
    
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    source_container = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    output_container = os.getenv('AZURE_STORAGE_OUTPUT_CONTAINER')
    doc_intel_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    doc_intel_key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    issues = []
    
    # Check required configuration
    if not storage_account or storage_account == 'your_storage_account_name':
        issues.append("AZURE_STORAGE_ACCOUNT_NAME needs to be configured")
    else:
        print("✅ Storage account name is configured")
    
    if not source_container:
        issues.append("AZURE_STORAGE_CONTAINER_NAME needs to be configured")
    else:
        print("✅ Source container name is configured")
        
    if not output_container:
        issues.append("AZURE_STORAGE_OUTPUT_CONTAINER needs to be configured")
    else:
        print("✅ Output container name is configured")
    
    if not doc_intel_endpoint or doc_intel_endpoint == 'https://your_region.cognitiveservices.azure.com/':
        issues.append("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT needs to be configured")
    else:
        print("✅ Document Intelligence endpoint is configured")
        
    if not doc_intel_key or doc_intel_key == 'your_document_intelligence_key':
        issues.append("AZURE_DOCUMENT_INTELLIGENCE_KEY needs to be configured")
    else:
        print("✅ Document Intelligence key is configured")
    
    if issues:
        print("⚠️  Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n   Note: Authentication issues are checked separately via Azure CLI")
        return False
    
    return True


def main():
    """Run authentication tests."""
    print("🔧 Azure CLI Authentication Test")
    print("This will test Azure CLI authentication (make sure you've run 'az login' first).\n")
    
    try:
        # Check Azure CLI status
        cli_ok = check_azure_cli()
        
        if not cli_ok:
            print("\n❌ Azure CLI issues detected. Please resolve them and try again.")
            return 1
        
        # Test configuration (non-auth settings)
        config_ok = test_credentials_format()
        
        # Test actual authentication
        auth_ok = test_authentication()
        
        if auth_ok:
            print("\n🎉 Authentication test passed! Azure CLI authentication is working.")
            if config_ok:
                print("✅ All configuration looks good. You're ready to run the main application!")
                print("\nNext steps:")
                print("   python3 main.py")
            else:
                print("⚠️  Please complete the configuration in your .env file before running the main application.")
            return 0
        else:
            print("\n❌ Authentication test failed. Please check the suggestions above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
