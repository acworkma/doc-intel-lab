"""
Azure client configuration and authentication module.
Handles connection to Azure Storage and Document Intelligence services.
"""

import os
from typing import Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


class AzureClients:
    """Manages Azure service clients and authentication."""
    
    def __init__(self):
        """Initialize Azure clients with appropriate authentication."""
        self.storage_account_name = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
        self.storage_container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME')
        self.output_container_name = os.getenv('AZURE_STORAGE_OUTPUT_CONTAINER')
        self.doc_intel_endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.doc_intel_key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        # Validate required environment variables
        self._validate_config()
        
        # Initialize credentials and clients
        self.credential = self._get_azure_credential()
        self.blob_service_client = self._get_blob_service_client()
        self.doc_intel_client = self._get_document_intelligence_client()
        
    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        required_vars = [
            'AZURE_STORAGE_ACCOUNT_NAME',
            'AZURE_STORAGE_CONTAINER_NAME', 
            'AZURE_STORAGE_OUTPUT_CONTAINER',
            'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT',
            'AZURE_DOCUMENT_INTELLIGENCE_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        # No need to check authentication variables - DefaultAzureCredential handles this
    
    def _get_azure_credential(self):
        """Get Azure credential using DefaultAzureCredential (Azure CLI authentication)."""
        print("🔐 Using Azure CLI authentication (DefaultAzureCredential)")
        print("    Make sure you've run 'az login' first")
        return DefaultAzureCredential()
    
    def _get_blob_service_client(self) -> BlobServiceClient:
        """Initialize and return Azure Blob Storage client."""
        account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
        return BlobServiceClient(account_url=account_url, credential=self.credential)
    
    def _get_document_intelligence_client(self) -> DocumentIntelligenceClient:
        """Initialize and return Azure Document Intelligence client."""
        return DocumentIntelligenceClient(
            endpoint=self.doc_intel_endpoint,
            credential=AzureKeyCredential(self.doc_intel_key)
        )
    
    def test_connections(self) -> bool:
        """Test connections to all Azure services."""
        try:
            print("🧪 Testing Azure Storage connection...")
            # Test storage connection by listing containers
            containers = list(self.blob_service_client.list_containers(max_results=1))
            print(f"✅ Storage connection successful. Found {len(list(self.blob_service_client.list_containers()))} containers.")
            
            # Check if required containers exist
            container_names = [container.name for container in self.blob_service_client.list_containers()]
            
            if self.storage_container_name not in container_names:
                print(f"⚠️  Source container '{self.storage_container_name}' not found. Available containers: {container_names}")
                return False
                
            if self.output_container_name not in container_names:
                print(f"⚠️  Output container '{self.output_container_name}' not found. Available containers: {container_names}")
                return False
            
            print("🧪 Testing Document Intelligence connection...")
            # Test document intelligence connection
            # We can't easily test without sending a document, so we'll just verify the client was created
            if self.doc_intel_client:
                print("✅ Document Intelligence client initialized successfully.")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False
    
    def get_source_container_client(self):
        """Get the source container client."""
        return self.blob_service_client.get_container_client(self.storage_container_name)
    
    def get_output_container_client(self):
        """Get the output container client."""
        return self.blob_service_client.get_container_client(self.output_container_name)
