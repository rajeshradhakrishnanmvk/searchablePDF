# Creating Searchable PDFs with Azure AI Services: A Comprehensive Guide

In today's digital world, managing and accessing documents efficiently is crucial. One of the challenges many organizations face is converting scanned-image PDFs—often generated from physical documents—into searchable formats. This transformation enables deep text searches, making document retrieval and analysis far more efficient. Microsoft Azure AI Services offers a powerful solution through its Document Intelligence capabilities, specifically with the **Searchable PDF** functionality. This blog will guide you through the process of using Azure's Document Intelligence to convert analog PDFs into searchable ones, providing code examples, explanations, and insights into the challenges and solutions.

## What is a Searchable PDF?

A searchable PDF is a document that combines the visual representation of the original file with an underlying text layer. This text layer is generated through Optical Character Recognition (OCR), allowing users to search for and copy text directly from the document. This capability is particularly valuable for scanned documents where text isn't natively selectable or searchable.

Azure AI Services' Document Intelligence enables the conversion of scanned PDFs into searchable PDFs by overlaying detected text on top of the original image files. The resulting document is fully searchable and can be indexed for quick retrieval in large document management systems.

## Relevance of Searchable PDFs

Searchable PDFs are indispensable in various scenarios:

1. **Legal and Compliance**: Quick text searches in large legal documents can save hours of manual review.
2. **Archiving**: Digital archives benefit from searchable PDFs by making old, scanned documents accessible.
3. **Research**: Researchers can find specific information quickly in historical documents, enhancing productivity.
4. **Business Operations**: Companies can streamline document management processes, improving overall efficiency.

## Step-by-Step Guide to Creating a Searchable PDF Using Azure AI Services

### Prerequisites

To follow along with this guide, ensure you have the following:

- **Microsoft Azure Subscription**: Access to Azure AI Services.
- **Azure AI Services Endpoint and API Key**: You can obtain these from the Azure portal.
- **Python Installed**: The script provided requires Python 3.x and a few additional libraries.

### Setting Up the Environment

First, install the necessary Python libraries:

```bash
pip install requests PyPDF2 python-dotenv
```

Create a `.env` file in your project directory and add your Azure endpoint and API key:

```plaintext
AZURE_ENDPOINT="your_azure_endpoint"
AZURE_API_KEY="your_azure_api_key"
```

### The Python Script

The following script converts a scanned PDF into a searchable PDF using Azure's Document Intelligence service:

```python
import os
import requests
import time
import base64
import PyPDF2
from dotenv import load_dotenv

def pdf_to_base64_first_two_pages(pdf_file_path):
    with open(pdf_file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        for page_num in range(min(2, len(reader.pages))):
            writer.add_page(reader.pages[page_num])
        from io import BytesIO
        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
        return base64_pdf

def create_searchable_pdf(file_path, endpoint, api_key):
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'
    }

    base64Source_data = pdf_to_base64_first_two_pages(file_path)

    post_url = f'{endpoint}/documentintelligence/documentModels/prebuilt-read:analyze?_overload=analyzeDocument&api-version=2024-07-31-preview&output=pdf'

    payload = {
        "base64Source": base64Source_data
    }

    post_response = requests.post(post_url, headers=headers, json=payload)

    if post_response.status_code != 202:
        raise Exception(f"POST request failed: {post_response.status_code} {post_response.text}")
    
    result_location = post_response.headers.get('Operation-Location')
    if not result_location:
        raise Exception("Operation-Location header not found in POST response.")

    result_id = result_location.split('/')[-1].split('?')[0]

    get_url = f'{endpoint}/documentintelligence/documentModels/prebuilt-read/analyzeResults/{result_id}'
    while True:
        get_response = requests.get(get_url + '?api-version=2024-07-31-preview', headers={'Ocp-Apim-Subscription-Key': api_key})
        if get_response.status_code == 200:
            print("Operation is complete")
            break
        elif get_response.status_code == 202:
            print("Processing... Please wait.")
            time.sleep(5)
        else:
            raise Exception(f"GET request failed: {get_response.status_code} {get_response.text}")

    pdf_url = f'{get_url}/pdf?api-version=2024-07-31-preview'
    pdf_response = requests.get(pdf_url, headers={'Ocp-Apim-Subscription-Key': api_key})
    if pdf_response.status_code == 200:
        output_pdf_path = file_path.replace('.pdf', '_searchable.pdf')
        with open(output_pdf_path, 'wb') as f:
            f.write(pdf_response.content)
        print(f"Searchable PDF saved as {output_pdf_path}")
    else:
        raise Exception(f"Failed to retrieve the PDF: {pdf_response.status_code} {pdf_response.text}")

if __name__ == "__main__":
    load_dotenv()
    azure_endpoint = os.environ.get("AZURE_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_API_KEY")
    pdf_file_path = "SampleReadOnly_3.pdf"
    create_searchable_pdf(pdf_file_path, azure_endpoint, azure_api_key)
```

### How to Run the Script

1. Save the script in a `.py` file.
2. Ensure that your environment variables (`AZURE_ENDPOINT` and `AZURE_API_KEY`) are correctly set in the `.env` file.
3. Run the script in your terminal:

```bash
python script_name.py
```

Upon successful execution, the script will convert the input PDF (`SampleReadOnly_3.pdf`) into a searchable PDF (`SampleReadOnly_3_searchable.pdf`).

## Challenges and Solutions

### 1. **Handling Large PDFs**
   - **Challenge**: Processing large PDFs can be time-consuming and may lead to timeouts.
   - **Solution**: The script processes the first two pages of the PDF for simplicity. For large documents, consider splitting the PDF into smaller chunks before processing.

### 2. **Polling for Completion**
   - **Challenge**: Determining when the OCR process is complete can be tricky.
   - **Solution**: The script uses a polling mechanism that checks the operation status every five seconds until the process is complete. This ensures that the final PDF is fully processed before retrieval.

### 3. **API Limitations**
   - **Challenge**: Azure’s Document Intelligence API has rate limits and size restrictions.
   - **Solution**: Manage API usage by processing documents in batches and handling exceptions to retry failed operations.

## Outcome and Benefits

By following this guide, you’ve now created a script that transforms scanned PDFs into searchable documents using Azure AI Services. This solution significantly enhances document accessibility and management by enabling deep text search capabilities. The searchable PDFs can be indexed, searched, and archived more efficiently, saving time and resources in various professional settings.

This approach leverages Azure’s robust AI capabilities, ensuring accurate text recognition and seamless integration into existing document management workflows. The end result is a highly searchable and user-friendly document repository that meets modern demands for efficiency and accessibility.

## References

For more detailed information and further customization, refer to the official Microsoft documentation:

- [Azure Document Intelligence: Concept Read](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-read?view=doc-intel-4.0.0&tabs=sample-code#supported-languages-and-locales)
- [Azure Document Intelligence: Analyze Result PDF](https://learn.microsoft.com/en-us/rest/api/aiservices/document-models/get-analyze-result-pdf?view=rest-aiservices-v4.0%20(2024-07-31-preview)&tabs=HTTP)

By utilizing the resources and guidance provided, you can further optimize and expand the capabilities of your document processing workflows.
