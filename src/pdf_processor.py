"""
PDF processing module using Azure Document Intelligence.
Handles the conversion of PDFs to searchable PDFs.
"""

import io
import time
import asyncio
from typing import List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat
from azure.core.exceptions import HttpResponseError
from .azure_client import AzureClients
from .utils import (
    format_bytes, get_timestamp, get_output_filename, 
    format_duration, ProgressTracker, retry_with_backoff,
    get_config_int
)


class PDFProcessor:
    """Handles PDF processing using Azure Document Intelligence."""
    
    def __init__(self, azure_clients: AzureClients):
        """Initialize PDF processor with Azure clients."""
        self.azure_clients = azure_clients
        self.doc_intel_client = azure_clients.doc_intel_client
        self.source_container = azure_clients.get_source_container_client()
        self.output_container = azure_clients.get_output_container_client()
        
        # Configuration
        self.max_concurrent_operations = get_config_int('MAX_CONCURRENT_OPERATIONS', 5)
        self.polling_interval = get_config_int('POLLING_INTERVAL_SECONDS', 5)
        
        print(f"🔧 Configured for {self.max_concurrent_operations} concurrent operations")
        print(f"🔧 Polling interval: {self.polling_interval} seconds")
    
    def discover_pdf_files(self) -> List[str]:
        """Discover all PDF files in the source container."""
        print("🔍 Discovering PDF files in storage container...")
        
        try:
            blobs = list(self.source_container.list_blobs())
            pdf_files = [blob.name for blob in blobs if blob.name.lower().endswith('.pdf')]
            
            print(f"📄 Found {len(pdf_files)} PDF files:")
            for i, pdf_file in enumerate(pdf_files, 1):
                blob_client = self.source_container.get_blob_client(pdf_file)
                properties = blob_client.get_blob_properties()
                size_str = format_bytes(properties.size)
                print(f"   {i:2d}. {pdf_file} ({size_str})")
            
            return pdf_files
            
        except Exception as e:
            print(f"❌ Error discovering PDF files: {str(e)}")
            raise
    
    def process_single_pdf(self, blob_name: str) -> Tuple[bool, str]:
        """Process a single PDF file."""
        try:
            print(f"🔄 Starting processing: {blob_name}")
            
            # Download the PDF from storage
            blob_client = self.source_container.get_blob_client(blob_name)
            pdf_data = blob_client.download_blob().readall()
            
            print(f"📥 Downloaded {blob_name} ({format_bytes(len(pdf_data))})")
            
            # Process with Document Intelligence
            searchable_pdf_data = self._process_with_document_intelligence(pdf_data, blob_name)
            
            # Upload the processed PDF
            output_filename = get_output_filename(blob_name)
            self._upload_processed_pdf(searchable_pdf_data, output_filename)
            
            print(f"✅ Successfully processed: {blob_name} -> {output_filename}")
            return True, f"Successfully processed {blob_name}"
            
        except Exception as e:
            error_msg = f"Failed to process {blob_name}: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def _process_with_document_intelligence(self, pdf_data: bytes, filename: str) -> bytes:
        """Process PDF data with Azure Document Intelligence."""
        print(f"🧠 Analyzing document with Document Intelligence: {filename}")
        
        def analyze_document():
            # Start the analysis operation
            analyze_request = AnalyzeDocumentRequest(bytes_source=pdf_data)
            
            poller = self.doc_intel_client.begin_analyze_document(
                "prebuilt-layout",  # Use prebuilt layout model for OCR
                analyze_request,
                output_content_format=ContentFormat.PDF,  # Request PDF output
                polling_interval=self.polling_interval
            )
            
            print(f"⏳ Document analysis started for {filename}, waiting for completion...")
            
            # Poll for completion
            result = poller.result()
            return result
        
        # Retry the analysis with backoff in case of transient errors
        result = retry_with_backoff(analyze_document, max_retries=3, base_delay=2.0)
        
        if hasattr(result, 'content') and result.content:
            print(f"✅ Document analysis completed for {filename}")
            # The result.content should contain the searchable PDF bytes
            return result.content
        else:
            raise ValueError(f"Document Intelligence did not return PDF content for {filename}")
    
    def _upload_processed_pdf(self, pdf_data: bytes, output_filename: str) -> None:
        """Upload processed PDF to output container."""
        try:
            output_blob_client = self.output_container.get_blob_client(output_filename)
            
            # Upload with PDF content type
            output_blob_client.upload_blob(
                pdf_data,
                blob_type="BlockBlob",
                content_type="application/pdf",
                overwrite=True
            )
            
            print(f"📤 Uploaded processed PDF: {output_filename} ({format_bytes(len(pdf_data))})")
            
        except Exception as e:
            raise Exception(f"Failed to upload {output_filename}: {str(e)}")
    
    def process_all_pdfs(self, pdf_files: List[str]) -> None:
        """Process all PDF files concurrently."""
        if not pdf_files:
            print("📭 No PDF files to process.")
            return
        
        print(f"\n🚀 Starting concurrent processing of {len(pdf_files)} PDF files...")
        print(f"🔧 Using {self.max_concurrent_operations} concurrent operations")
        
        progress_tracker = ProgressTracker(len(pdf_files), "PDF Processing")
        start_time = time.time()
        
        # Process files concurrently
        with ThreadPoolExecutor(max_workers=self.max_concurrent_operations) as executor:
            # Submit all tasks
            future_to_filename = {
                executor.submit(self.process_single_pdf, pdf_file): pdf_file
                for pdf_file in pdf_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_filename):
                filename = future_to_filename[future]
                try:
                    success, message = future.result()
                    progress_tracker.update(failed=not success)
                    
                    if not success:
                        print(f"⚠️  Processing failed for {filename}: {message}")
                        
                except Exception as e:
                    progress_tracker.update(failed=True)
                    print(f"❌ Unexpected error processing {filename}: {str(e)}")
        
        # Print final summary
        progress_tracker.finish()
        total_time = time.time() - start_time
        
        print(f"\n🎉 Batch processing completed in {format_duration(total_time)}")
        if progress_tracker.completed_items > 0:
            avg_time = total_time / progress_tracker.completed_items
            print(f"📊 Average processing time per file: {format_duration(avg_time)}")
    
    def validate_output_container(self) -> bool:
        """Validate that the output container exists and is accessible."""
        try:
            # Try to list blobs in the output container
            list(self.output_container.list_blobs(max_results=1))
            print(f"✅ Output container '{self.azure_clients.output_container_name}' is accessible")
            return True
        except Exception as e:
            print(f"❌ Cannot access output container '{self.azure_clients.output_container_name}': {str(e)}")
            return False
    
    def check_existing_files(self, pdf_files: List[str]) -> Tuple[List[str], List[str]]:
        """Check which files already exist in the output container."""
        print("🔍 Checking for existing processed files...")
        
        try:
            # Get list of existing files in output container
            existing_blobs = {blob.name for blob in self.output_container.list_blobs()}
            
            files_to_process = []
            files_already_processed = []
            
            for pdf_file in pdf_files:
                output_filename = get_output_filename(pdf_file)
                if output_filename in existing_blobs:
                    files_already_processed.append(pdf_file)
                else:
                    files_to_process.append(pdf_file)
            
            if files_already_processed:
                print(f"⏭️  Found {len(files_already_processed)} already processed files:")
                for file in files_already_processed:
                    print(f"     - {file}")
                print("   (These will be skipped)")
            
            if files_to_process:
                print(f"📋 {len(files_to_process)} files need processing")
            else:
                print("✅ All files have already been processed!")
            
            return files_to_process, files_already_processed
            
        except Exception as e:
            print(f"⚠️  Could not check existing files: {str(e)}")
            print("   Proceeding to process all files...")
            return pdf_files, []
