# Quick Start Guide

## 1. Install Dependencies

Run the setup script:
```bash
./setup.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Login to Azure

```bash
az login
```

## 3. Configure Azure Settings

Edit the `.env` file with your Azure configuration:
```bash
nano .env
```

Required settings:
- `AZURE_STORAGE_ACCOUNT_NAME`: Your storage account name
- `AZURE_STORAGE_CONTAINER_NAME`: Container with PDF files
- `AZURE_STORAGE_OUTPUT_CONTAINER`: Container for processed PDFs
- `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`: Document Intelligence endpoint
- `AZURE_DOCUMENT_INTELLIGENCE_KEY`: Document Intelligence key

**Note**: No authentication credentials needed in .env - uses your Azure CLI login.

## 4. Test Setup

```bash
python test_auth.py
```

## 5. Run the Application

```bash
python3 main.py
```

## Azure Setup Requirements

### 1. Storage Account
- Create containers for source PDFs and output
- Your user account needs `Storage Blob Data Contributor` role

### 2. Document Intelligence
- Create Document Intelligence resource
- Note the endpoint and key
- Your user account needs `Cognitive Services User` role

### 3. Authentication
- Run `az login` to authenticate
- Ensure you have the required role assignments above

## Troubleshooting

- Run `az login` if you get authentication errors
- Check that containers exist in your storage account
- Verify you have the correct role assignments
- Ensure Document Intelligence resource is in the same region as specified in endpoint
- Check that PDF files exist in the source container
