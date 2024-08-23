import os
import requests
import time
import base64
import PyPDF2
from dotenv import load_dotenv

def pdf_to_base64_first_two_pages(pdf_file_path):
    # Read the PDF file
    with open(pdf_file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Create a PdfWriter object to hold the first two pages
        writer = PyPDF2.PdfWriter()

        # Add the first two pages to the writer
        for page_num in range(min(2, len(reader.pages))):  # Handle cases where the PDF has fewer than 2 pages
            writer.add_page(reader.pages[page_num])

        # Write the pages to a temporary in-memory buffer
        from io import BytesIO
        buffer = BytesIO()
        writer.write(buffer)
        buffer.seek(0)

        # Encode the buffer content to base64
        base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
        return base64_pdf

def create_searchable_pdf(file_path, endpoint, api_key):
    # Define the headers for the POST request
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Content-Type': 'application/json'  # Content-Type for PDF files
    }

    base64Source_data = pdf_to_base64_first_two_pages(file_path)

    # Send the POST request to initiate the OCR process
    post_url = f'{endpoint}/documentintelligence/documentModels/prebuilt-read:analyze?_overload=analyzeDocument&api-version=2024-07-31-preview&output=pdf'

    payload = {
        "base64Source": base64Source_data
    }

    post_response = requests.post(post_url, headers=headers, json=payload)

    if post_response.status_code != 202:
        raise Exception(f"POST request failed: {post_response.status_code} {post_response.text}")
    
    # Get the resultId from the POST response headers (if available)
    result_location = post_response.headers.get('Operation-Location')
    if not result_location:
        raise Exception("Operation-Location header not found in POST response.")

    # Extract the resultId from the result_location URL
    result_id = result_location.split('/')[-1].split('?')[0]
    # print(result_id) 
    # Poll the GET request until the operation is complete
    get_url = f'{endpoint}/documentintelligence/documentModels/prebuilt-read/analyzeResults/{result_id}'
    while True:
        get_response = requests.get(get_url + '?api-version=2024-07-31-preview', headers={'Ocp-Apim-Subscription-Key': api_key})
        if get_response.status_code == 200:
            print("Operation is complete")
            break  # Operation is complete
        elif get_response.status_code == 202:
            print("Processing... Please wait.")
            time.sleep(5)  # Wait for 5 seconds before polling again
        else:
            raise Exception(f"GET request failed: {get_response.status_code} {get_response.text}")

    # Retrieve the PDF as application/pdf
    pdf_url = f'{get_url}/pdf?api-version=2024-07-31-preview'
    print(pdf_url)
    pdf_response = requests.get(pdf_url, headers={'Ocp-Apim-Subscription-Key': api_key})
    if pdf_response.status_code == 200:
        # Save the PDF file
        output_pdf_path = file_path.replace('.pdf', '_searchable.pdf')
        with open(output_pdf_path, 'wb') as f:
            f.write(pdf_response.content)
        print(f"Searchable PDF saved as {output_pdf_path}")
    else:
        raise Exception(f"Failed to retrieve the PDF: {pdf_response.status_code} {pdf_response.text}")

# Example usage
if __name__ == "__main__":
    load_dotenv()
    # Define your Azure endpoint and API key
    azure_endpoint = os.environ.get("AZURE_ENDPOINT")
    azure_api_key = os.environ.get("AZURE_API_KEY")
    
    # Specify the path to the PDF file
    pdf_file_path = "SampleReadOnly_3.pdf"
    
    # Call the function to create a searchable PDF
    create_searchable_pdf(pdf_file_path, azure_endpoint, azure_api_key)
