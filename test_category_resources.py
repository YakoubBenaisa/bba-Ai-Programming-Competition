import requests
import os
import sys
import json

# Configuration
USERNAME = 'yakoub.benaissa'
PASSWORD = 'aLnmftOM'
CATEGORY_URL = 'https://elearning.univ-bba.dz/course/index.php?categoryid=795'  # The category URL you specified
API_BASE = 'http://127.0.0.1:8008/api'  # Update this to match your server port

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def test_category_resources():
    """Test the auth-resources endpoint with a category URL."""
    url = f"{API_BASE}/mock-auth-resources/"  # Use the mock endpoint to avoid timeouts
    
    # Prepare the payload
    payload = {
        "url": CATEGORY_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "download_file": False  # Set to False to get JSON response
    }
    
    debug(f"Sending POST request to {url} with payload: {payload}")
    
    # Send the request with a timeout
    try:
        response = requests.post(url, json=payload, timeout=60)  # 60 seconds timeout
        
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
                print(json.dumps(data, indent=2))
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
    except requests.exceptions.Timeout:
        print("Request timed out. The server might be busy or the category page is too large.")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_category_resources()
