import requests
import os
import sys
import json

# Configuration
USERNAME = 'yakoub.benaissa'
PASSWORD = 'aLnmftOM'
CATEGORY_ID = '795'  # The category ID you specified
API_BASE = 'http://127.0.0.1:8008/api'  # Update this to match your server port

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def test_category_courses():
    """Test the category courses endpoint."""
    url = f"{API_BASE}/category/{CATEGORY_ID}/courses/"
    
    debug(f"Sending GET request to {url}")
    
    # Send the request with a timeout
    try:
        response = requests.get(url, timeout=60)  # 60 seconds timeout
        
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
                
                # Check if courses were found
                if data.get('status') == 'success' and data.get('data'):
                    print(f"Found {len(data['data'])} courses")
                    for i, course in enumerate(data['data'], 1):
                        print(f"Course {i}:")
                        print(f"  Name: {course.get('name')}")
                        print(f"  URL: {course.get('url')}")
                        print(f"  ID: {course.get('id')}")
            except Exception as e:
                print(f"Error parsing JSON: {e}")
                print(response.text[:500])  # Print first 500 chars
        else:
            print(f"Unexpected content type: {content_type}")
            print(response.text[:500])  # Print first 500 chars
    except requests.exceptions.Timeout:
        print("Request timed out. The server might be busy or the category page is too large.")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    test_category_courses()
