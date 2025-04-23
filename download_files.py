import requests
import os
import sys

# Configuration
USERNAME = 'yakoub.benaissa'
PASSWORD = 'aLnmftOM'
COURSE_ID = '8527'  # The course ID you mentioned
API_BASE = 'http://127.0.0.1:8005/api'  # Update this to match your server port

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def download_files():
    """Download files from the course."""
    # First, get the list of files
    url = f"{API_BASE}/moodle-pdfs/"
    payload = {
        "course_id": COURSE_ID,
        "username": USERNAME,
        "password": PASSWORD
    }
    
    debug(f"Getting file list from {url}")
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    # Parse the JSON response
    data = response.json()
    
    if data.get('status') != 'success' or not data.get('pdfs'):
        print("No files found or error in response")
        print(data)
        return
    
    # Create a directory for the files
    os.makedirs('downloaded_files', exist_ok=True)
    
    # Download each file
    for i, file_info in enumerate(data['pdfs'], 1):
        file_url = file_info.get('url')
        file_name = file_info.get('name')
        
        if not file_url:
            print(f"File {i} has no URL")
            continue
        
        print(f"Downloading file {i}: {file_name}")
        
        # Use the session from the login to download the file
        session = requests.Session()
        
        # Login first
        login_url = f"{API_BASE}/moodle-login/"
        login_payload = {
            "username": USERNAME,
            "password": PASSWORD
        }
        
        login_response = session.post(login_url, json=login_payload)
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            continue
        
        # Now download the file directly from Moodle
        try:
            file_response = session.get(file_url, stream=True)
            file_response.raise_for_status()
            
            # Determine the filename
            content_disposition = file_response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                import re
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    file_name = match.group(1)
            
            # Save the file
            file_path = os.path.join('downloaded_files', file_name)
            with open(file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"File saved to {file_path}")
            print(f"File size: {os.path.getsize(file_path)} bytes")
            
        except Exception as e:
            print(f"Error downloading file: {e}")

if __name__ == "__main__":
    download_files()
