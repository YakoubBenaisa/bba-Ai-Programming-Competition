import requests
import os
import sys

# Configuration
USERNAME = 'yakoub.benaissa'
PASSWORD = 'aLnmftOM'
COURSE_URL = 'https://elearning.univ-bba.dz/course/view.php?id=5873'  # The course URL you mentioned
API_BASE = 'http://127.0.0.1:8005/api'  # Update this to match your server port

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def test_auth_resources():
    """Test the auth-resources endpoint."""
    url = f"{API_BASE}/auth-resources/"
    
    # Prepare the payload
    payload = {
        "url": COURSE_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "download_pdf": True
    }
    
    debug(f"Sending POST request to {url} with payload: {payload}")
    
    # Send the request
    response = requests.post(url, json=payload)
    
    # Check the response
    debug(f"Response status code: {response.status_code}")
    debug(f"Response headers: {response.headers}")
    
    # Determine the content type
    content_type = response.headers.get('Content-Type', '')
    debug(f"Content type: {content_type}")
    
    if 'application/json' in content_type:
        # It's a JSON response
        try:
            data = response.json()
            print("JSON Response:")
            import json
            print(json.dumps(data, indent=2))
            
            # Check if resources were found
            if data.get('status') == 'success' and data.get('data'):
                print(f"Found {len(data['data'])} resources")
                for i, resource in enumerate(data['data'], 1):
                    print(f"Resource {i}:")
                    print(f"  Name: {resource.get('resource_name')}")
                    print(f"  URL: {resource.get('resource_url')}")
                    print(f"  PDF URL: {resource.get('pdf_url')}")
                    if resource.get('error'):
                        print(f"  Error: {resource.get('error')}")
            else:
                print("No resources found or error in response")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(response.text[:500])  # Print first 500 chars
    else:
        # It's a file download
        content_disposition = response.headers.get('Content-Disposition', '')
        filename = 'downloaded_file'
        
        if 'filename=' in content_disposition:
            import re
            match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if match:
                filename = match.group(1)
        
        # Save the file
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"File downloaded and saved as: {filename}")
        print(f"File size: {len(response.content)} bytes")

if __name__ == "__main__":
    test_auth_resources()
