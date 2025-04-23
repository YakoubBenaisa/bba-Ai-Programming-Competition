#!/usr/bin/env python3
"""
Moodle API Client - A script to demonstrate how to use the Moodle File Retriever API.
"""

import argparse
import json
import os
import sys
import requests
from urllib.parse import urlparse, parse_qs

def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)

class MoodleAPIClient:
    """Client for the Moodle File Retriever API."""
    
    def __init__(self, api_base='http://localhost:8000/api', username=None, password=None):
        """Initialize the client."""
        self.api_base = api_base
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session_cookies = None
    
    def login(self):
        """Login to Moodle and get session cookies."""
        if not self.username or not self.password:
            raise ValueError("Username and password are required for login")
        
        url = f"{self.api_base}/moodle-login/"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'success':
                self.session_cookies = data.get('session')
                return True
            else:
                print(f"Login failed: {data.get('message')}")
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def get_course_pdfs(self, course_id):
        """Get PDF files from a course."""
        url = f"{self.api_base}/moodle-pdfs/"
        
        # Use session cookies if available, otherwise use username/password
        if self.session_cookies:
            payload = {
                "course_id": course_id,
                "session": self.session_cookies
            }
        else:
            if not self.username or not self.password:
                raise ValueError("Username and password are required")
            
            payload = {
                "course_id": course_id,
                "username": self.username,
                "password": self.password
            }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting course PDFs: {e}")
            return None
    
    def get_course_resources(self, course_url):
        """Get resources from a course URL."""
        url = f"{self.api_base}/auth-resources/"
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
        
        payload = {
            "url": course_url,
            "username": self.username,
            "password": self.password,
            "download_file": False
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting course resources: {e}")
            return None
    
    def download_file(self, course_url, output_path):
        """Download a file from a course URL."""
        url = f"{self.api_base}/auth-resources/"
        
        if not self.username or not self.password:
            raise ValueError("Username and password are required")
        
        payload = {
            "url": course_url,
            "username": self.username,
            "password": self.password,
            "download_file": True
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Check if it's a file download
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                # It's a JSON response, not a file
                data = response.json()
                print(f"Error downloading file: {data.get('message')}")
                return False
            
            # Get the filename from Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            filename = 'downloaded_file'
            
            if 'filename=' in content_disposition:
                import re
                match = re.search(r'filename="?([^"]+)"?', content_disposition)
                if match:
                    filename = match.group(1)
            
            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save the file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"File downloaded to {output_path}")
            return True
        except Exception as e:
            print(f"Error downloading file: {e}")
            return False
    
    def get_category_courses(self, category_id):
        """Get courses in a category."""
        url = f"{self.api_base}/category/{category_id}/courses/"
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting category courses: {e}")
            return None
    
    def get_all_courses(self):
        """Get all courses."""
        url = f"{self.api_base}/moodle-courses/"
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting all courses: {e}")
            return None
    
    def get_departments(self):
        """Get all departments."""
        url = f"{self.api_base}/departments/"
        
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error getting departments: {e}")
            return None

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Moodle API Client')
    parser.add_argument('--api-base', default='http://localhost:8000/api', help='Base URL of the API')
    parser.add_argument('--username', required=True, help='Your Moodle username')
    parser.add_argument('--password', required=True, help='Your Moodle password')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Login command
    login_parser = subparsers.add_parser('login', help='Login to Moodle')
    
    # Get course PDFs command
    course_pdfs_parser = subparsers.add_parser('course-pdfs', help='Get PDFs from a course')
    course_pdfs_parser.add_argument('course_id', help='The ID of the course')
    
    # Get course resources command
    course_resources_parser = subparsers.add_parser('course-resources', help='Get resources from a course URL')
    course_resources_parser.add_argument('course_url', help='The URL of the course')
    
    # Download file command
    download_parser = subparsers.add_parser('download', help='Download a file from a course URL')
    download_parser.add_argument('course_url', help='The URL of the course')
    download_parser.add_argument('output_path', help='The path to save the file')
    
    # Get category courses command
    category_courses_parser = subparsers.add_parser('category-courses', help='Get courses in a category')
    category_courses_parser.add_argument('category_id', help='The ID of the category')
    
    # Get all courses command
    subparsers.add_parser('all-courses', help='Get all courses')
    
    # Get departments command
    subparsers.add_parser('departments', help='Get all departments')
    
    args = parser.parse_args()
    
    # Create the client
    client = MoodleAPIClient(api_base=args.api_base, username=args.username, password=args.password)
    
    # Execute the command
    if args.command == 'login':
        if client.login():
            print("Login successful")
            print(f"Session cookies: {json.dumps(client.session_cookies, indent=2)}")
        else:
            print("Login failed")
    
    elif args.command == 'course-pdfs':
        pdfs = client.get_course_pdfs(args.course_id)
        if pdfs:
            print(json.dumps(pdfs, indent=2))
        else:
            print("Failed to get course PDFs")
    
    elif args.command == 'course-resources':
        resources = client.get_course_resources(args.course_url)
        if resources:
            print(json.dumps(resources, indent=2))
        else:
            print("Failed to get course resources")
    
    elif args.command == 'download':
        if client.download_file(args.course_url, args.output_path):
            print(f"File downloaded to {args.output_path}")
        else:
            print("Failed to download file")
    
    elif args.command == 'category-courses':
        courses = client.get_category_courses(args.category_id)
        if courses:
            print(json.dumps(courses, indent=2))
        else:
            print("Failed to get category courses")
    
    elif args.command == 'all-courses':
        courses = client.get_all_courses()
        if courses:
            print(json.dumps(courses, indent=2))
        else:
            print("Failed to get all courses")
    
    elif args.command == 'departments':
        departments = client.get_departments()
        if departments:
            print(json.dumps(departments, indent=2))
        else:
            print("Failed to get departments")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
