# Azure Document Intelligence PDF Processor

This Python application processes PDF files stored in Azure Storage using Azure Document Intelligence to create searchable PDFs. It authenticates using Azure SDK and processes files concurrently for optimal performance.

## Features

- 🔐 **Azure CLI Authentication** - Uses your Azure CLI login session (run `az login` first)
- 📁 **Azure Storage Integration** - Reads from and writes to Azure Storage containers
- 🔍 **PDF Processing** - Converts regular PDFs to searchable PDFs using Azure Document Intelligence
- 📊 **Progress Tracking** - Real-time progress updates with detailed logging
- ⚡ **Concurrent Processing** - Processes multiple files simultaneously for better performance
- 🛡️ **Error Handling** - Robust error handling and retry mechanisms

## Prerequisites

- Python 3.8 or higher
- Azure CLI installed and configured
- Azure Storage Account
- Azure Document Intelligence resource
- Appropriate Azure permissions for your user account

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd doc-intel-lab
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Login to Azure:
```bash
az login
```

5. Configure environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your Azure configuration details.

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Name of your Azure Storage account | Yes |
| `AZURE_STORAGE_CONTAINER_NAME` | Source container with PDF files | Yes |
| `AZURE_STORAGE_OUTPUT_CONTAINER` | Output container for processed PDFs | Yes |
| `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` | Document Intelligence service endpoint | Yes |
| `AZURE_DOCUMENT_INTELLIGENCE_KEY` | Document Intelligence service key | Yes |
| `MAX_CONCURRENT_OPERATIONS` | Maximum concurrent file processing | No (default: 5) |
| `POLLING_INTERVAL_SECONDS` | Polling interval for operation status | No (default: 5) |

**Note**: Authentication is handled via Azure CLI. Run `az login` before using the application.

### Azure Setup

1. **Create Azure Storage Account:**
   - Create a storage account in Azure portal
   - Create containers for source and output files
   - Note down the storage account name

2. **Create Document Intelligence Resource:**
   - Create a Document Intelligence resource in Azure portal
   - Note down the endpoint and key

3. **Setup Authentication:**
   
   **Azure CLI (Recommended)**
   - Install Azure CLI if not already installed
   - Run `az login` to authenticate
   - Ensure your account has appropriate permissions:
     - `Storage Blob Data Contributor` role on the storage account
     - `Cognitive Services User` role on the Document Intelligence resource

   **Alternative: Service Principal**
   - Create an Azure AD application registration
   - Create a client secret
   - Update .env file with service principal credentials
   - Assign appropriate roles to the service principal

   **Alternative: Managed Identity**
   - Enable managed identity on your Azure resource (VM, App Service, etc.)
   - Assign the same roles as above to the managed identity
   - Set `AZURE_USE_MANAGED_IDENTITY=true` in .env

## Usage

First, make sure you're logged into Azure:

```bash
az login
```

Then run the application:

```bash
python main.py
```

The application will:

1. Connect to Azure Storage and list all PDF files in the source container
2. Process each PDF through Azure Document Intelligence to create searchable versions
3. Save the processed PDFs to the output container
4. Display progress and status information

## Project Structure

```
doc-intel-lab/
├── main.py                 # Main application entry point
├── src/
│   ├── __init__.py
│   ├── azure_client.py     # Azure service clients and authentication
│   ├── pdf_processor.py    # PDF processing logic
│   └── utils.py           # Utility functions and helpers
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Error Handling

The application includes comprehensive error handling for:

- Authentication failures
- Network connectivity issues
- File access problems
- Document Intelligence service errors
- Storage account access issues

All errors are logged with detailed information for troubleshooting.

## Performance Considerations

- Adjust `MAX_CONCURRENT_OPERATIONS` based on your Document Intelligence service tier
- Monitor your Azure service quotas and limits
- Large files may take longer to process

## Troubleshooting

### Common Issues

1. **Authentication Errors:**
   - Verify your service principal credentials
   - Check role assignments on Azure resources
   - Ensure the tenant ID is correct

2. **Storage Access Errors:**
   - Verify storage account name and container names
   - Check storage account access keys or role assignments
   - Ensure containers exist

3. **Document Intelligence Errors:**
   - Verify the endpoint URL format
   - Check the service key
   - Ensure you have sufficient quota

### Logging

The application provides detailed logging output including:
- File discovery and processing status
- Azure service operation results
- Error details and stack traces
- Performance metrics

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Azure service documentation
- Create an issue in this repository
