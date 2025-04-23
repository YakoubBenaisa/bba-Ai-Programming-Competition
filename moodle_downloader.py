#!/usr/bin/env python3
"""
Moodle Downloader - A script to download files from Moodle courses or categories.
"""

import argparse
import json
import os
import re
import sys
import requests
from urllib.parse import urlparse, parse_qs

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

def extract_id_from_url(url):
    """Extract the ID from a Moodle URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'id' in query_params:
        return query_params['id'][0]
    elif 'categoryid' in query_params:
        return query_params['categoryid'][0]
    
    return None

def download_file(session, url, output_dir='.'):
    """Download a file from a URL."""
    try:
        response = session.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        # Get the filename from Content-Disposition header or URL
        filename = url.split('/')[-1].split('?')[0]
        content_disposition = response.headers.get('Content-Disposition', '')
        
        if 'filename=' in content_disposition:
            match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if match:
                filename = match.group(1)
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def download_moodle_files(url, username, password, output_dir='.', api_base='http://127.0.0.1:8008/api'):
    """Download files from a Moodle course or category."""
    # Determine if it's a course or category URL
    if 'course/view.php' in url:
        url_type = 'course'
        id_value = extract_id_from_url(url)
        if id_value:
            print(f"Detected course URL with ID: {id_value}")
        else:
            print("Could not extract course ID from URL")
            return
    elif 'course/index.php' in url:
        url_type = 'category'
        id_value = extract_id_from_url(url)
        if id_value:
            print(f"Detected category URL with ID: {id_value}")
        else:
            print("Could not extract category ID from URL")
            return
    else:
        print("Unsupported URL type. Please provide a Moodle course or category URL.")
        return
    
    # Create a session
    session = requests.Session()
    
    # First, try to use the mock endpoint for testing
    try:
        mock_url = f"{api_base}/mock-auth-resources/"
        payload = {
            "url": url,
            "username": username,
            "password": password,
            "download_file": False  # Get JSON response first to see available files
        }
        
        print(f"Fetching resources from {url}...")
        response = session.post(mock_url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'success' and data.get('data'):
            resources = data.get('data')
            print(f"Found {len(resources)} resources")
            
            # Create a directory for the files
            if url_type == 'course':
                output_subdir = f"course_{id_value}"
            else:
                output_subdir = f"category_{id_value}"
            
            output_path = os.path.join(output_dir, output_subdir)
            os.makedirs(output_path, exist_ok=True)
            
            # Download each file
            for i, resource in enumerate(resources, 1):
                resource_name = resource.get('resource_name', f"Resource {i}")
                pdf_url = resource.get('pdf_url')
                
                if pdf_url:
                    print(f"Downloading {resource_name}...")
                    
                    # Try to download the file directly
                    file_path = download_file(session, pdf_url, output_path)
                    
                    if file_path:
                        print(f"Downloaded to {file_path}")
                    else:
                        print(f"Failed to download {resource_name}")
                else:
                    print(f"No download URL found for {resource_name}")
            
            print(f"All files downloaded to {output_path}")
        else:
            print("No resources found or error in response")
            print(json.dumps(data, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")
        
        # If the mock endpoint fails, try the real endpoint
        try:
            if url_type == 'course':
                real_url = f"{api_base}/moodle-pdfs/"
                payload = {
                    "course_id": id_value,
                    "username": username,
                    "password": password
                }
            else:
                # For categories, we need to get the courses first
                courses_url = f"{api_base}/category/{id_value}/courses/"
                courses_response = session.get(courses_url, timeout=60)
                courses_response.raise_for_status()
                
                courses_data = courses_response.json()
                
                if courses_data.get('status') == 'success' and courses_data.get('data'):
                    courses = courses_data.get('data')
                    print(f"Found {len(courses)} courses in category {id_value}")
                    
                    # Create a directory for the category
                    output_path = os.path.join(output_dir, f"category_{id_value}")
                    os.makedirs(output_path, exist_ok=True)
                    
                    # Download files from each course
                    for course in courses:
                        course_id = course.get('id')
                        course_name = course.get('name', f"Course {course_id}")
                        
                        print(f"Processing course: {course_name} (ID: {course_id})")
                        
                        # Create a directory for the course
                        course_path = os.path.join(output_path, f"course_{course_id}")
                        os.makedirs(course_path, exist_ok=True)
                        
                        # Get the PDFs for this course
                        real_url = f"{api_base}/moodle-pdfs/"
                        payload = {
                            "course_id": course_id,
                            "username": username,
                            "password": password
                        }
                        
                        pdf_response = session.post(real_url, json=payload, timeout=60)
                        pdf_response.raise_for_status()
                        
                        pdf_data = pdf_response.json()
                        
                        if pdf_data.get('status') == 'success' and pdf_data.get('pdfs'):
                            pdfs = pdf_data.get('pdfs')
                            print(f"Found {len(pdfs)} files in course {course_name}")
                            
                            # Download each file
                            for pdf in pdfs:
                                pdf_url = pdf.get('url')
                                pdf_name = pdf.get('name', "Unknown")
                                
                                print(f"Downloading {pdf_name}...")
                                
                                # Try to download the file
                                file_path = download_file(session, pdf_url, course_path)
                                
                                if file_path:
                                    print(f"Downloaded to {file_path}")
                                else:
                                    print(f"Failed to download {pdf_name}")
                        else:
                            print(f"No files found in course {course_name}")
                    
                    print(f"All files downloaded to {output_path}")
                    return
                else:
                    print("No courses found in category or error in response")
                    print(json.dumps(courses_data, indent=2))
                    return
            
            # For course URLs, continue with the real endpoint
            if url_type == 'course':
                print(f"Fetching files from course {id_value}...")
                response = session.post(real_url, json=payload, timeout=60)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('status') == 'success' and data.get('pdfs'):
                    pdfs = data.get('pdfs')
                    print(f"Found {len(pdfs)} files")
                    
                    # Create a directory for the files
                    output_path = os.path.join(output_dir, f"course_{id_value}")
                    os.makedirs(output_path, exist_ok=True)
                    
                    # Download each file
                    for pdf in pdfs:
                        pdf_url = pdf.get('url')
                        pdf_name = pdf.get('name', "Unknown")
                        
                        print(f"Downloading {pdf_name}...")
                        
                        # Try to download the file
                        file_path = download_file(session, pdf_url, output_path)
                        
                        if file_path:
                            print(f"Downloaded to {file_path}")
                        else:
                            print(f"Failed to download {pdf_name}")
                    
                    print(f"All files downloaded to {output_path}")
                else:
                    print("No files found or error in response")
                    print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error with real endpoint: {e}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Download files from Moodle courses or categories.')
    parser.add_argument('url', help='The URL of the Moodle course or category')
    parser.add_argument('username', help='Your Moodle username')
    parser.add_argument('password', help='Your Moodle password')
    parser.add_argument('-o', '--output-dir', default='.', help='Output directory for downloaded files')
    parser.add_argument('-a', '--api-base', default='http://127.0.0.1:8008/api', help='Base URL of the API')
    
    args = parser.parse_args()
    
    download_moodle_files(args.url, args.username, args.password, args.output_dir, args.api_base)

if __name__ == '__main__':
    main()
