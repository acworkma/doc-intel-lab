#!/usr/bin/env python3
"""
Azure Storage Account connectivity test.
This script tests connectivity to Azure Storage and validates container access.
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError


def test_storage_configuration():
    """Test if storage configuration is present and valid."""
    print("🔍 Validating Storage Configuration...")
    
    # Load environment variables
    load_dotenv()
    
    storage_account = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    source_container = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
    output_container = os.getenv('AZURE_STORAGE_OUTPUT_CONTAINER')
    
    issues = []
    
    if not storage_account or storage_account == 'your_storage_account_name':
        issues.append("AZURE_STORAGE_ACCOUNT_NAME is not configured")
    else:
        print(f"✅ Storage Account: {storage_account}")
    
    if not source_container:
        issues.append("AZURE_STORAGE_CONTAINER_NAME is not configured")
    else:
        print(f"✅ Source Container: {source_container}")
        
    if not output_container:
        issues.append("AZURE_STORAGE_OUTPUT_CONTAINER is not configured")
    else:
        print(f"✅ Output Container: {output_container}")
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False, None, None, None
    
    return True, storage_account, source_container, output_container


def test_storage_authentication():
    """Test authentication to Azure Storage."""
    print("\n🔐 Testing Storage Authentication...")
    
    try:
        # Get configuration
        config_ok, storage_account, source_container, output_container = test_storage_configuration()
        
        if not config_ok:
            return False, None
        
        # Create credential and storage client
        credential = DefaultAzureCredential()
        account_url = f"https://{storage_account}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)
        
        print(f"🧪 Connecting to: {account_url}")
        
        # Test basic connectivity by listing containers
        containers = []
        for container in blob_service_client.list_containers():
            containers.append(container)
            if len(containers) >= 5:  # Limit to first 5 containers
                break
        
        container_names = [container.name for container in containers]
        
        print(f"✅ Successfully connected to storage account!")
        print(f"   Found {len(containers)} containers: {', '.join(container_names)}")
        
        return True, blob_service_client
        
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("   Make sure you've run 'az login' and have Storage Blob Data Contributor role")
        return False, None
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("   Check your storage account name and network connectivity")
        return False, None


def test_container_access(blob_service_client, container_name, container_type):
    """Test access to a specific container."""
    print(f"\n📁 Testing {container_type} Container: {container_name}")
    
    try:
        container_client = blob_service_client.get_container_client(container_name)
        
        # Check if container exists
        properties = container_client.get_container_properties()
        print(f"✅ Container exists and is accessible")
        print(f"   Last modified: {properties.last_modified}")
        
        # List some blobs to test read access
        blobs = []
        for blob in container_client.list_blobs():
            blobs.append(blob)
            if len(blobs) >= 5:  # Limit to first 5 blobs
                break
        print(f"   Contains {len(blobs)} files")
        
        if blobs:
            print("   Sample files:")
            for i, blob in enumerate(blobs[:3], 1):
                size_mb = blob.size / (1024 * 1024) if blob.size else 0
                print(f"      {i}. {blob.name} ({size_mb:.1f} MB)")
        
        # Test write access (create a small test blob)
        test_blob_name = f"test-access-{container_type}.txt"
        test_content = f"Test file created by storage test - {container_type}"
        
        test_blob_client = container_client.get_blob_client(test_blob_name)
        test_blob_client.upload_blob(test_content, overwrite=True)
        print(f"✅ Write access confirmed (created test file: {test_blob_name})")
        
        # Clean up test file
        test_blob_client.delete_blob()
        print(f"✅ Test file cleaned up")
        
        return True
        
    except ResourceNotFoundError:
        print(f"❌ Container '{container_name}' does not exist")
        print(f"   Please create the container in your storage account")
        return False
    except Exception as e:
        print(f"❌ Container access failed: {str(e)}")
        print(f"   Check permissions for container '{container_name}'")
        return False


def test_pdf_files(blob_service_client, source_container):
    """Test for PDF files in the source container."""
    print(f"\n📄 Checking for PDF files in: {source_container}")
    
    try:
        container_client = blob_service_client.get_container_client(source_container)
        
        # List all blobs and filter for PDFs
        all_blobs = list(container_client.list_blobs())
        pdf_blobs = [blob for blob in all_blobs if blob.name.lower().endswith('.pdf')]
        
        print(f"   Total files: {len(all_blobs)}")
        print(f"   PDF files: {len(pdf_blobs)}")
        
        if pdf_blobs:
            print("✅ Found PDF files ready for processing:")
            for i, blob in enumerate(pdf_blobs[:5], 1):  # Show first 5
                size_mb = blob.size / (1024 * 1024) if blob.size else 0
                print(f"      {i}. {blob.name} ({size_mb:.1f} MB)")
            
            if len(pdf_blobs) > 5:
                print(f"      ... and {len(pdf_blobs) - 5} more PDF files")
                
            return True
        else:
            print("⚠️  No PDF files found in source container")
            print("   Upload some PDF files to test the processing")
            return False
            
    except Exception as e:
        print(f"❌ Error checking PDF files: {str(e)}")
        return False


def main():
    """Run storage connectivity tests."""
    print("🔧 Azure Storage Connectivity Test")
    print("=" * 60)
    
    try:
        # Test configuration
        config_ok, storage_account, source_container, output_container = test_storage_configuration()
        
        if not config_ok:
            print("\n❌ Configuration issues detected. Please fix your .env file.")
            return 1
        
        # Test authentication and basic connectivity
        auth_ok, blob_service_client = test_storage_authentication()
        
        if not auth_ok:
            print("\n❌ Storage authentication failed.")
            return 1
        
        # Test container access
        source_ok = test_container_access(blob_service_client, source_container, "source")
        output_ok = test_container_access(blob_service_client, output_container, "output")
        
        # Test for PDF files
        pdf_ok = test_pdf_files(blob_service_client, source_container)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Storage Test Summary:")
        print(f"   Configuration: {'✅ OK' if config_ok else '❌ Failed'}")
        print(f"   Authentication: {'✅ OK' if auth_ok else '❌ Failed'}")
        print(f"   Source Container: {'✅ OK' if source_ok else '❌ Failed'}")
        print(f"   Output Container: {'✅ OK' if output_ok else '❌ Failed'}")
        print(f"   PDF Files: {'✅ Found' if pdf_ok else '⚠️  None found'}")
        
        if config_ok and auth_ok and source_ok and output_ok:
            print("\n🎉 Storage connectivity test passed!")
            if pdf_ok:
                print("✅ Ready for PDF processing!")
            else:
                print("⚠️  Upload some PDF files to the source container to start processing")
            return 0
        else:
            print("\n❌ Some storage tests failed. Please resolve the issues above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
