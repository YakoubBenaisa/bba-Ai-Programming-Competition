#!/usr/bin/env python3
"""
Moodle File Retriever - A script to retrieve files from Moodle courses.
"""

import argparse
import os
import sys
import requests
import json

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def retrieve_files(course_id, username, password, output_dir='.', api_base='http://127.0.0.1:8008/api'):
    """Retrieve files from a Moodle course."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Endpoint for retrieving PDFs
    url = f"{api_base}/moodle-pdfs/"
    
    # Prepare the payload
    payload = {
        "course_id": course_id,
        "username": username,
        "password": password
    }
    
    print(f"Retrieving files from course {course_id}...")
    
    try:
        # Send the request
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        if data.get('status') == 'success' and data.get('pdfs'):
            pdfs = data.get('pdfs')
            print(f"Found {len(pdfs)} files in course {course_id}")
            
            # Create a session for downloading files
            session = requests.Session()
            
            # Login to Moodle
            login_url = f"{api_base}/moodle-login/"
            login_payload = {
                "username": username,
                "password": password
            }
            
            login_response = session.post(login_url, json=login_payload)
            if login_response.status_code != 200:
                print("Failed to login to Moodle")
                return
            
            # Download each file
            for i, pdf in enumerate(pdfs, 1):
                pdf_url = pdf.get('url')
                pdf_name = pdf.get('name', f"file_{i}")
                resource_name = pdf.get('resource_name', f"Resource {i}")
                
                if not pdf_url:
                    print(f"No URL found for {resource_name}")
                    continue
                
                print(f"Downloading {pdf_name} from {resource_name}...")
                
                try:
                    # Download the file
                    file_response = session.get(pdf_url, stream=True, timeout=60)
                    file_response.raise_for_status()
                    
                    # Determine the filename
                    filename = pdf_name
                    content_disposition = file_response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        import re
                        match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if match:
                            filename = match.group(1)
                    
                    # Save the file
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, 'wb') as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"Downloaded {filename} to {file_path}")
                except Exception as e:
                    print(f"Error downloading {pdf_name}: {e}")
            
            print(f"All files downloaded to {output_dir}")
        else:
            print("No files found or error in response")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error retrieving files: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Retrieve files from Moodle courses.')
    parser.add_argument('course_id', help='The ID of the Moodle course')
    parser.add_argument('username', help='Your Moodle username')
    parser.add_argument('password', help='Your Moodle password')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory for downloaded files')
    parser.add_argument('-a', '--api-base', default='http://127.0.0.1:8008/api', help='Base URL of the API')
    
    args = parser.parse_args()
    
    retrieve_files(args.course_id, args.username, args.password, args.output_dir, args.api_base)

if __name__ == '__main__':
    main()
