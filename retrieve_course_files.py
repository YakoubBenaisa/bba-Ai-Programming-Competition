#!/usr/bin/env python3
"""
Moodle Course File Retriever - A script to retrieve files from a Moodle course URL.
"""

import argparse
import os
import sys
import requests
import json

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def retrieve_course_files(course_url, username, password, output_dir='.', api_base='http://127.0.0.1:8008/api'):
    """Retrieve files from a Moodle course URL."""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Endpoint for retrieving resources
    url = f"{api_base}/auth-resources/"
    
    # Prepare the payload
    payload = {
        "url": course_url,
        "username": username,
        "password": password,
        "download_file": False  # Get JSON first to see all resources
    }
    
    print(f"Retrieving resources from {course_url}...")
    
    try:
        # Send the request
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        if data.get('status') == 'success' and data.get('data'):
            resources = data.get('data')
            print(f"Found {len(resources)} resources")
            
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
            for i, resource in enumerate(resources, 1):
                resource_name = resource.get('resource_name', f"Resource {i}")
                resource_url = resource.get('resource_url')
                pdf_url = resource.get('pdf_url')
                pdf_name = resource.get('pdf_name', f"file_{i}")
                
                if not pdf_url:
                    print(f"No PDF URL found for {resource_name}")
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
            print("No resources found or error in response")
            print(json.dumps(data, indent=2))
            
            # Try to download a file directly
            print("Trying to download a file directly...")
            
            # Prepare the payload for direct download
            payload = {
                "url": course_url,
                "username": username,
                "password": password,
                "download_file": True  # Download the file directly
            }
            
            try:
                # Send the request
                response = requests.post(url, json=payload, timeout=60)
                response.raise_for_status()
                
                # Check if it's a file download
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' not in content_type:
                    # It's a file download
                    content_disposition = response.headers.get('Content-Disposition', '')
                    filename = 'downloaded_file'
                    
                    if 'filename=' in content_disposition:
                        import re
                        match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if match:
                            filename = match.group(1)
                    
                    # Save the file
                    file_path = os.path.join(output_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"Downloaded {filename} to {file_path}")
                else:
                    print("No file found for direct download")
                    print(json.dumps(response.json(), indent=2))
            except Exception as e:
                print(f"Error downloading file directly: {e}")
    except Exception as e:
        print(f"Error retrieving resources: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Retrieve files from a Moodle course URL.')
    parser.add_argument('course_url', help='The URL of the Moodle course')
    parser.add_argument('username', help='Your Moodle username')
    parser.add_argument('password', help='Your Moodle password')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory for downloaded files')
    parser.add_argument('-a', '--api-base', default='http://127.0.0.1:8008/api', help='Base URL of the API')
    
    args = parser.parse_args()
    
    retrieve_course_files(args.course_url, args.username, args.password, args.output_dir, args.api_base)

if __name__ == '__main__':
    main()
