#!/usr/bin/env python3
"""
Test script to retrieve files using the mock endpoint.
"""

import os
import sys
import requests
import json

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def test_mock_endpoint():
    """Test retrieving files using the mock endpoint."""
    # Configuration
    username = 'yakoub.benaissa'
    password = 'aLnmftOM'
    course_url = 'https://elearning.univ-bba.dz/course/view.php?id=8527'
    api_base = 'http://127.0.0.1:8008/api'
    output_dir = 'mock_downloads'
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Endpoint for retrieving resources
    url = f"{api_base}/mock-auth-resources/"
    
    # Test 1: Get JSON response
    print("Test 1: Get JSON response")
    payload = {
        "url": course_url,
        "username": username,
        "password": password,
        "download_file": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response status: {data.get('status')}")
        print(f"Found {len(data.get('data', []))} resources")
        
        # Print the first resource
        if data.get('data'):
            resource = data.get('data')[0]
            print(f"First resource: {resource.get('resource_name')}")
            print(f"PDF URL: {resource.get('pdf_url')}")
    except Exception as e:
        print(f"Error in Test 1: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Test 2: Download a file directly
    print("Test 2: Download a file directly")
    payload = {
        "url": course_url,
        "username": username,
        "password": password,
        "download_file": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        # Check if it's a file download
        content_type = response.headers.get('Content-Type', '')
        print(f"Content type: {content_type}")
        
        if 'application/json' not in content_type:
            # It's a file download
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"Content disposition: {content_disposition}")
            
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
            print(f"File size: {len(response.content)} bytes")
        else:
            print("Response is not a file download")
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error in Test 2: {e}")
    
    print("\n" + "-" * 50 + "\n")
    
    # Test 3: Test with category URL
    print("Test 3: Test with category URL")
    category_url = 'https://elearning.univ-bba.dz/course/index.php?categoryid=795'
    payload = {
        "url": category_url,
        "username": username,
        "password": password,
        "download_file": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        print(f"Response status: {data.get('status')}")
        print(f"Found {len(data.get('data', []))} resources")
        
        # Print the first resource
        if data.get('data'):
            resource = data.get('data')[0]
            print(f"First resource: {resource.get('resource_name')}")
            print(f"PDF URL: {resource.get('pdf_url')}")
    except Exception as e:
        print(f"Error in Test 3: {e}")

if __name__ == '__main__':
    test_mock_endpoint()
