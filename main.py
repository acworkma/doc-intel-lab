#!/usr/bin/env python3
"""
Azure Document Intelligence PDF Processor

This application processes PDF files stored in Azure Storage using Azure Document Intelligence
to create searchable PDFs. It uses Azure SDK for authentication and provides real-time progress updates.

Usage:
    python main.py

Make sure to configure your .env file with the required Azure credentials and endpoints.
"""

import os
import sys
import time
from dotenv import load_dotenv
from src.azure_client import AzureClients
from src.pdf_processor import PDFProcessor
from src.utils import print_header, print_section, format_duration


def load_environment():
    """Load environment variables from .env file."""
    # Try to load .env file
    env_file = '.env'
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"✅ Loaded configuration from {env_file}")
    else:
        print(f"⚠️  No .env file found. Using environment variables or system defaults.")
        print(f"   Copy .env.example to .env and configure your Azure settings.")


def print_configuration():
    """Print current configuration (without secrets)."""
    print_section("Configuration")
    
    config_items = [
        ("Storage Account", os.getenv('AZURE_STORAGE_ACCOUNT_NAME', 'Not set')),
        ("Source Container", os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'Not set')),
        ("Output Container", os.getenv('AZURE_STORAGE_OUTPUT_CONTAINER', 'Not set')),
        ("Document Intelligence Endpoint", os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', 'Not set')),
        ("Max Concurrent Operations", os.getenv('MAX_CONCURRENT_OPERATIONS', '5')),
        ("Polling Interval (seconds)", os.getenv('POLLING_INTERVAL_SECONDS', '5')),
        ("Use Managed Identity", os.getenv('AZURE_USE_MANAGED_IDENTITY', 'false')),
    ]
    
    for label, value in config_items:
        print(f"  {label:.<30} {value}")


def main():
    """Main application entry point."""
    start_time = time.time()
    
    print_header("Azure Document Intelligence PDF Processor")
    print("🚀 Starting PDF processing application...")
    
    try:
        # Load environment configuration
        load_environment()
        print_configuration()
        
        # Initialize Azure clients
        print_section("Initializing Azure Connections")
        azure_clients = AzureClients()
        
        # Test connections
        if not azure_clients.test_connections():
            print("\n❌ Failed to connect to Azure services. Please check your configuration.")
            return 1
        
        # Initialize PDF processor
        print_section("Initializing PDF Processor")
        pdf_processor = PDFProcessor(azure_clients)
        
        # Validate output container
        if not pdf_processor.validate_output_container():
            return 1
        
        # Discover PDF files
        print_section("Discovering PDF Files")
        pdf_files = pdf_processor.discover_pdf_files()
        
        if not pdf_files:
            print("📭 No PDF files found in the source container.")
            print("   Please upload some PDF files and try again.")
            return 0
        
        # Check for existing processed files
        print_section("Checking Existing Files")
        files_to_process, files_already_processed = pdf_processor.check_existing_files(pdf_files)
        
        if not files_to_process:
            print("✅ All PDF files have already been processed!")
            return 0
        
        # Confirm processing
        print_section("Starting Processing")
        print(f"📋 Ready to process {len(files_to_process)} PDF files")
        
        # Process all PDFs
        pdf_processor.process_all_pdfs(files_to_process)
        
        # Print final summary
        total_time = time.time() - start_time
        print_section("Summary")
        print(f"🎉 Application completed successfully in {format_duration(total_time)}")
        print(f"📊 Total files discovered: {len(pdf_files)}")
        print(f"✅ Files processed: {len(files_to_process)}")
        print(f"⏭️  Files skipped (already processed): {len(files_already_processed)}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user (Ctrl+C)")
        return 1
        
    except Exception as e:
        print(f"\n❌ Application failed with error: {str(e)}")
        print(f"   Please check your configuration and try again.")
        
        # Print additional debugging information in case of error
        print("\n--- Debug Information ---")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.executable}")
        print(f"Environment file exists: {os.path.exists('.env')}")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
