# Example Usage and Output

## Running the Application

Once you've configured your `.env` file with valid Azure credentials:

```bash
python3 main.py
```

## Expected Output

Here's what you can expect to see when running the application:

```
============================================================
  Azure Document Intelligence PDF Processor
============================================================
🚀 Starting PDF processing application...
✅ Loaded configuration from .env

--- Configuration ---
  Storage Account.............. mystorageaccount
  Source Container............. pdfs
  Output Container............. processed-pdfs
  Document Intelligence Endpoint https://eastus.cognitiveservices.azure.com/
  Max Concurrent Operations.... 3
  Polling Interval (seconds)... 5
  Use Managed Identity......... false

--- Initializing Azure Connections ---
🔐 Using service principal for authentication
🧪 Testing Azure Storage connection...
✅ Storage connection successful. Found 2 containers.
🧪 Testing Document Intelligence connection...
✅ Document Intelligence client initialized successfully.

--- Initializing PDF Processor ---
🔧 Configured for 3 concurrent operations
🔧 Polling interval: 5 seconds
✅ Output container 'processed-pdfs' is accessible

--- Discovering PDF Files ---
🔍 Discovering PDF files in storage container...
📄 Found 5 PDF files:
    1. document1.pdf (2.3 MB)
    2. report_2024.pdf (5.1 MB)
    3. manual.pdf (12.8 MB)
    4. invoice_001.pdf (1.2 MB)
    5. presentation.pdf (8.7 MB)

--- Checking Existing Files ---
🔍 Checking for existing processed files...
⏭️  Found 1 already processed files:
     - document1.pdf
   (These will be skipped)
📋 4 files need processing

--- Starting Processing ---
📋 Ready to process 4 files

🚀 Starting concurrent processing of 4 PDF files...
🔧 Using 3 concurrent operations

🔄 Starting processing: report_2024.pdf
🔄 Starting processing: manual.pdf
🔄 Starting processing: invoice_001.pdf
📥 Downloaded report_2024.pdf (5.1 MB)
📥 Downloaded invoice_001.pdf (1.2 MB)
📥 Downloaded manual.pdf (12.8 MB)
🧠 Analyzing document with Document Intelligence: report_2024.pdf
🧠 Analyzing document with Document Intelligence: invoice_001.pdf
🧠 Analyzing document with Document Intelligence: manual.pdf
⏳ Document analysis started for invoice_001.pdf, waiting for completion...
⏳ Document analysis started for report_2024.pdf, waiting for completion...
⏳ Document analysis started for manual.pdf, waiting for completion...
✅ Document analysis completed for invoice_001.pdf
📤 Uploaded processed PDF: invoice_001_searchable.pdf (1.3 MB)
✅ Successfully processed: invoice_001.pdf -> invoice_001_searchable.pdf
📊 PDF Processing: 1/4 (25.0%) - ✅ 1 completed - 15.2 seconds
🔄 Starting processing: presentation.pdf
📥 Downloaded presentation.pdf (8.7 MB)
🧠 Analyzing document with Document Intelligence: presentation.pdf
⏳ Document analysis started for presentation.pdf, waiting for completion...
✅ Document analysis completed for report_2024.pdf
📤 Uploaded processed PDF: report_2024_searchable.pdf (5.2 MB)
✅ Successfully processed: report_2024.pdf -> report_2024_searchable.pdf
📊 PDF Processing: 2/4 (50.0%) - ✅ 2 completed - 28.7 seconds
✅ Document analysis completed for presentation.pdf
📤 Uploaded processed PDF: presentation_searchable.pdf (8.9 MB)
✅ Successfully processed: presentation.pdf -> presentation_searchable.pdf
📊 PDF Processing: 3/4 (75.0%) - ✅ 3 completed - 42.1 seconds
✅ Document analysis completed for manual.pdf
📤 Uploaded processed PDF: manual_searchable.pdf (13.1 MB)
✅ Successfully processed: manual.pdf -> manual_searchable.pdf
📊 PDF Processing: 4/4 (100.0%) - ✅ 4 completed - 58.3 seconds

🏁 PDF Processing completed in 58.3 seconds
   ✅ Successful: 4
   ❌ Failed: 0
   📊 Total: 4

🎉 Batch processing completed in 58.3 seconds
📊 Average processing time per file: 14.6 seconds

--- Summary ---
🎉 Application completed successfully in 58.3 seconds
📊 Total files discovered: 5
✅ Files processed: 4
⏭️  Files skipped (already processed): 1
```

## Error Handling Example

If there are errors, you'll see detailed information:

```
❌ Error discovering PDF files: The specified container does not exist.
   Please check your configuration and try again.

--- Debug Information ---
Current working directory: /home/user/doc-intel-lab
Python path: /usr/bin/python3
Environment file exists: True
```

## Configuration Tips

1. **Container Names**: Make sure your storage containers exist
2. **Permissions**: Ensure your service principal has the right roles
3. **Endpoints**: Verify your Document Intelligence endpoint URL format
4. **File Size**: Large PDFs take longer to process
5. **Concurrency**: Adjust `MAX_CONCURRENT_OPERATIONS` based on your service tier

## Monitoring Progress

The application provides:
- Real-time progress updates
- File-by-file status
- Error details if processing fails
- Performance metrics
- Final summary report
