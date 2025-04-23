from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from django.http import FileResponse, HttpResponse
import requests
import io
import os
from .utils_improved import scrape_elearning_courses, extract_departments, extract_aalinks, extract_course_resources, login_to_elearning
from .serializers import CourseSerializer, DepartmentSerializer, LinkSerializer, ResourceSerializer
from .moodle_auth import moodle_login, get_course_pdfs, get_category_courses

class CourseListAPIView(APIView):
    """
    API view to retrieve courses from elearning.univ-bba.dz
    """
    def get(self, request):
        # Scrape courses from the website
        courses = scrape_elearning_courses()

        # Serialize the data
        serializer = CourseSerializer(courses, many=True)

        return Response({
            'status': 'success',
            'count': len(courses),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class DepartmentListAPIView(APIView):
    """
    API view to retrieve departments from elearning.univ-bba.dz
    """
    def get(self, request):
        # Extract departments from the website
        departments = extract_departments()

        # Serialize the data
        serializer = DepartmentSerializer(departments, many=True)

        return Response({
            'status': 'success',
            'count': len(departments),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class LinkExtractAPIView(APIView):
    """
    API view to extract links with 'aalink' class from a provided URL
    """
    def post(self, request):
        # Get the URL from the request data
        url = request.data.get('url')

        if not url:
            return Response({
                'status': 'error',
                'message': 'URL is required in the request body'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract links from the provided URL
        links = extract_aalinks(url)

        # Serialize the data
        serializer = LinkSerializer(links, many=True)

        return Response({
            'status': 'success',
            'count': len(links),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class CategoryCoursesAPIView(APIView):
    """
    API view to extract courses from a specific category
    """
    def get(self, request, category_id):
        # Construct the URL with the category ID
        url = f"https://elearning.univ-bba.dz/course/index.php?categoryid={category_id}"

        # Extract links from the URL
        links = extract_aalinks(url)

        # Serialize the data
        serializer = LinkSerializer(links, many=True)

        return Response({
            'status': 'success',
            'category_id': category_id,
            'count': len(links),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class CourseResourcesAPIView(APIView):
    """
    API view to extract resources and PDF links from a course page
    """
    def get(self, request, course_id):
        # Construct the course URL with the course ID
        course_url = f"https://elearning.univ-bba.dz/course/view.php?id={course_id}"

        # Extract resources from the course page
        resources = extract_course_resources(course_url)

        # Serialize the data
        serializer = ResourceSerializer(resources, many=True)

        return Response({
            'status': 'success',
            'course_id': course_id,
            'course_url': course_url,
            'count': len(resources),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # Get the course URL from the request data
        course_url = request.data.get('url')

        if not course_url:
            return Response({
                'status': 'error',
                'message': 'Course URL is required in the request body'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract resources from the course page
        resources = extract_course_resources(course_url)

        # Serialize the data
        serializer = ResourceSerializer(resources, many=True)

        return Response({
            'status': 'success',
            'course_url': course_url,
            'count': len(resources),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class AuthenticatedResourcesAPIView(APIView):
    """
    API view to extract resources and PDF links from a course page with authentication
    and return the actual files
    """
    def post(self, request):
        import logging
        import re
        from urllib.parse import urlparse, parse_qs
        logger = logging.getLogger(__name__)

        # Get the course URL, username, and password from the request data
        course_url = request.data.get('url')
        username = request.data.get('username')
        password = request.data.get('password')
        download_file = request.data.get('download_file', True)  # Default to True to download files

        logger.info(f"Received request for URL: {course_url}")
        logger.info(f"Download file flag: {download_file}")

        if not course_url:
            return Response({
                'status': 'error',
                'message': 'Course URL is required in the request body'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password are required for authentication'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if it's a category URL or a course URL
        parsed_url = urlparse(course_url)
        query_params = parse_qs(parsed_url.query)
        is_category = 'categoryid' in query_params
        is_course = 'id' in query_params and 'course/view.php' in course_url

        if is_category:
            category_id = query_params['categoryid'][0]
            logger.info(f"Detected category URL with ID: {category_id}")
        elif is_course:
            course_id = query_params['id'][0]
            logger.info(f"Detected course URL with ID: {course_id}")
        else:
            logger.warning(f"URL type not recognized: {course_url}")

        # Login to the elearning website
        logger.info(f"Attempting to login with username: {username}")
        session = login_to_elearning(username, password)

        if not session:
            logger.error("Authentication failed")
            return Response({
                'status': 'error',
                'message': 'Authentication failed. Please check your credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        logger.info("Authentication successful")

        # For category URLs, we need to get the courses first
        if is_category:
            try:
                # Get the courses in the category
                from .moodle_auth import get_category_courses
                courses_result = get_category_courses(category_id, username, password)

                if not courses_result.get('success'):
                    logger.error(f"Failed to get courses in category: {courses_result.get('message')}")
                    return Response({
                        'status': 'error',
                        'message': f"Failed to get courses in category: {courses_result.get('message')}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                courses = courses_result.get('courses', [])
                logger.info(f"Found {len(courses)} courses in category {category_id}")

                # If no courses found, return empty response
                if not courses:
                    return Response({
                        'status': 'success',
                        'course_url': course_url,
                        'authenticated': True,
                        'count': 0,
                        'data': []
                    }, status=status.HTTP_200_OK)

                # Get the first course
                course = courses[0]
                course_id = course.get('id')
                course_url = course.get('url')
                logger.info(f"Using first course: {course.get('name')} (ID: {course_id})")

                # Now we can proceed with the course URL
                is_category = False
                is_course = True
            except Exception as e:
                logger.error(f"Error processing category: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': f"Error processing category: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # For course URLs, we can use the moodle_auth.get_course_pdfs function
        if is_course:
            try:
                from .moodle_auth import get_course_pdfs
                pdfs_result = get_course_pdfs(course_id, username, password)

                if not pdfs_result.get('success'):
                    logger.error(f"Failed to get PDFs from course: {pdfs_result.get('message')}")
                    return Response({
                        'status': 'error',
                        'message': f"Failed to get PDFs from course: {pdfs_result.get('message')}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                pdfs = pdfs_result.get('pdfs', [])
                logger.info(f"Found {len(pdfs)} files in course {course_id}")

                # Convert PDFs to resources format
                resources = []
                for pdf in pdfs:
                    resources.append({
                        'resource_name': pdf.get('resource_name', ''),
                        'resource_url': pdf.get('resource_url', ''),
                        'pdf_url': pdf.get('url', ''),
                        'pdf_name': pdf.get('name', '')
                    })

                # If no resources found, return empty response
                if not resources:
                    return Response({
                        'status': 'success',
                        'course_url': course_url,
                        'authenticated': True,
                        'count': 0,
                        'data': []
                    }, status=status.HTTP_200_OK)

                # If download_file is False, return JSON response
                if not download_file:
                    serializer = ResourceSerializer(resources, many=True)
                    return Response({
                        'status': 'success',
                        'course_url': course_url,
                        'authenticated': True,
                        'count': len(resources),
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)

                # If download_file is True, download the first file
                resource = resources[0]
                download_url = resource.get('pdf_url')
                resource_name = resource.get('pdf_name') or resource.get('resource_name') or 'document'

                if not download_url:
                    logger.error("No download URL found in resource")
                    return Response({
                        'status': 'error',
                        'message': 'No download URL found in resource'
                    }, status=status.HTTP_404_NOT_FOUND)

                logger.info(f"Downloading file from: {download_url}")

                try:
                    # Download the file with a timeout
                    # First, try to get the direct file URL
                    from .moodle_auth import get_direct_file_url
                    direct_url_result = get_direct_file_url(download_url, session)

                    if direct_url_result.get('success'):
                        direct_url = direct_url_result.get('url')
                        logger.info(f"Got direct file URL: {direct_url}")

                        # Try downloading with the direct URL
                        file_response = session.get(direct_url, stream=True, timeout=30, allow_redirects=True)
                        file_response.raise_for_status()

                        # Get the content type
                        content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                        logger.info(f"File content type: {content_type}")

                        # Check if we got HTML instead of a file
                        if 'text/html' in content_type and '<html' in file_response.text[:1000].lower():
                            logger.warning("Received HTML from direct URL. Falling back to original URL.")
                            # Try with the original URL
                            file_response = session.get(download_url, stream=True, timeout=30, allow_redirects=True)
                            file_response.raise_for_status()

                            # Get the content type
                            content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                            logger.info(f"File content type: {content_type}")
                    else:
                        # Try with the original URL
                        logger.info(f"No direct URL found, using original URL: {download_url}")
                        file_response = session.get(download_url, stream=True, timeout=30, allow_redirects=True)
                        file_response.raise_for_status()

                        # Get the content type
                        content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                        logger.info(f"File content type: {content_type}")

                    # Check if we got HTML instead of a file
                    if 'text/html' in content_type and '<html' in file_response.text[:1000].lower():
                        logger.warning("Received HTML instead of file. Trying to extract file URL from HTML...")

                        # Try to find a download link in the HTML
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(file_response.text, 'html.parser')

                        # Look for download links
                        download_links = soup.select('a[href*=".pdf"], a[href*="pluginfile.php"], a[href*="webservice"], a[href*=".docx"], a[href*=".xlsx"], a[href*=".pptx"]')
                        if download_links:
                            new_url = download_links[0].get('href')
                            if not new_url.startswith('http'):
                                from urllib.parse import urljoin
                                new_url = urljoin(download_url, new_url)

                            logger.info(f"Found download link in HTML: {new_url}")

                            # Try downloading again with the new URL
                            file_response = session.get(new_url, stream=True, timeout=30, allow_redirects=True)
                            file_response.raise_for_status()

                            # Update content type
                            content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                            logger.info(f"New file content type: {content_type}")
                        else:
                            # If we can't find a download link, return the HTML as JSON
                            logger.warning("Could not find download link in HTML. Returning resources as JSON.")
                            serializer = ResourceSerializer(resources, many=True)
                            return Response({
                                'status': 'success',
                                'course_url': course_url,
                                'authenticated': True,
                                'count': len(resources),
                                'data': serializer.data
                            }, status=status.HTTP_200_OK)

                    # Get the filename from Content-Disposition header or URL
                    filename = resource_name
                    content_disposition = file_response.headers.get('Content-Disposition', '')

                    if 'filename=' in content_disposition:
                        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if filename_match:
                            filename = filename_match.group(1)
                    elif download_url.split('/')[-1].split('?')[0]:
                        filename = download_url.split('/')[-1].split('?')[0]

                    # Add file extension if missing
                    if '.' not in filename:
                        if 'pdf' in content_type.lower():
                            filename += '.pdf'
                        elif 'word' in content_type.lower():
                            filename += '.docx'
                        elif 'excel' in content_type.lower():
                            filename += '.xlsx'
                        elif 'powerpoint' in content_type.lower():
                            filename += '.pptx'
                        elif 'text' in content_type.lower():
                            filename += '.txt'

                    logger.info(f"Using filename: {filename}")

                    # Create a file-like object from the content
                    file_content = io.BytesIO(file_response.content)

                    # Save the file to disk for debugging
                    import os
                    debug_dir = '/tmp/moodle_files'
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_path = os.path.join(debug_dir, filename)
                    with open(debug_path, 'wb') as f:
                        f.write(file_response.content)
                    logger.info(f"Saved file to {debug_path} for debugging")

                    # Return the file
                    if 'pdf' in content_type.lower() or filename.lower().endswith('.pdf'):
                        response = FileResponse(file_content, content_type='application/pdf')
                    else:
                        response = FileResponse(file_content, content_type=content_type)

                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response

                except Exception as e:
                    logger.error(f"Error downloading file: {e}")
                    # Add the error to the resource
                    resource['error'] = f"Error downloading file: {str(e)}"

                    # Return JSON response with error
                    serializer = ResourceSerializer(resources, many=True)
                    return Response({
                        'status': 'error',
                        'message': f"Error downloading file: {str(e)}",
                        'course_url': course_url,
                        'authenticated': True,
                        'count': len(resources),
                        'data': serializer.data
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as e:
                logger.error(f"Error processing course: {str(e)}")
                return Response({
                    'status': 'error',
                    'message': f"Error processing course: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If we get here, we need to use the extract_course_resources function
        logger.info(f"Extracting resources from URL: {course_url}")
        try:
            # Set a timeout for the extraction to prevent hanging
            import threading
            import queue

            result_queue = queue.Queue()

            def extract_with_timeout():
                try:
                    resources = extract_course_resources(course_url, session)
                    result_queue.put((True, resources))
                except Exception as e:
                    logger.error(f"Error extracting resources: {e}")
                    result_queue.put((False, str(e)))

            # Start the extraction in a separate thread
            extraction_thread = threading.Thread(target=extract_with_timeout)
            extraction_thread.daemon = True
            extraction_thread.start()

            # Wait for the extraction to complete with a timeout
            try:
                success, result = result_queue.get(timeout=30)  # 30 seconds timeout
                if not success:
                    logger.error(f"Extraction failed: {result}")
                    return Response({
                        'status': 'error',
                        'message': f'Error extracting resources: {result}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                resources = result
                logger.info(f"Found {len(resources)} resources")
            except queue.Empty:
                logger.error("Extraction timed out")
                return Response({
                    'status': 'error',
                    'message': 'Extraction timed out. The course page might be too large or the server is busy.'
                }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}")
            return Response({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If no resources found, return a JSON response
        if not resources:
            logger.info("No resources found")
            return Response({
                'status': 'success',
                'course_url': course_url,
                'authenticated': True,
                'count': 0,
                'data': []
            }, status=status.HTTP_200_OK)

        # Check if we should download the file
        if download_file:
            # First, look for resources with a direct PDF URL
            downloadable_resources = [r for r in resources if r.get('pdf_url')]

            # If no direct PDF URLs, look for resources with a resource URL
            if not downloadable_resources:
                downloadable_resources = [r for r in resources if r.get('resource_url')]

            if downloadable_resources:
                # Get the first downloadable resource
                resource = downloadable_resources[0]

                # Determine the URL to download from
                download_url = resource.get('pdf_url') or resource.get('resource_url')
                resource_name = resource.get('pdf_name') or resource.get('resource_name') or 'document'

                if not download_url:
                    logger.error("No download URL found in resource")
                    return Response({
                        'status': 'error',
                        'message': 'No download URL found in resource'
                    }, status=status.HTTP_404_NOT_FOUND)

                logger.info(f"Downloading file from: {download_url}")

                try:
                    # Download the file with a timeout
                    # First, try to get the direct file URL
                    from .moodle_auth import get_direct_file_url
                    direct_url_result = get_direct_file_url(download_url, session)

                    if direct_url_result.get('success'):
                        direct_url = direct_url_result.get('url')
                        logger.info(f"Got direct file URL: {direct_url}")

                        # Try downloading with the direct URL
                        file_response = session.get(direct_url, stream=True, timeout=30, allow_redirects=True)
                        file_response.raise_for_status()

                        # Get the content type
                        content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                        logger.info(f"File content type: {content_type}")

                        # Check if we got HTML instead of a file
                        if 'text/html' in content_type and '<html' in file_response.text[:1000].lower():
                            logger.warning("Received HTML from direct URL. Falling back to original URL.")
                            # Try with the original URL
                            file_response = session.get(download_url, stream=True, timeout=30, allow_redirects=True)
                            file_response.raise_for_status()

                            # Get the content type
                            content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                            logger.info(f"File content type: {content_type}")
                    else:
                        # Try with the original URL
                        logger.info(f"No direct URL found, using original URL: {download_url}")
                        file_response = session.get(download_url, stream=True, timeout=30, allow_redirects=True)
                        file_response.raise_for_status()

                        # Get the content type
                        content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                        logger.info(f"File content type: {content_type}")

                    # Check if we got HTML instead of a file
                    if 'text/html' in content_type and '<html' in file_response.text[:1000].lower():
                        logger.warning("Received HTML instead of file. Trying to extract file URL from HTML...")

                        # Try to find a download link in the HTML
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(file_response.text, 'html.parser')

                        # Look for download links
                        download_links = soup.select('a[href*=".pdf"], a[href*="pluginfile.php"], a[href*="webservice"], a[href*=".docx"], a[href*=".xlsx"], a[href*=".pptx"]')
                        if download_links:
                            new_url = download_links[0].get('href')
                            if not new_url.startswith('http'):
                                from urllib.parse import urljoin
                                new_url = urljoin(download_url, new_url)

                            logger.info(f"Found download link in HTML: {new_url}")

                            # Try downloading again with the new URL
                            file_response = session.get(new_url, stream=True, timeout=30, allow_redirects=True)
                            file_response.raise_for_status()

                            # Update content type
                            content_type = file_response.headers.get('Content-Type', 'application/octet-stream')
                            logger.info(f"New file content type: {content_type}")
                        else:
                            # If we can't find a download link, return the HTML as JSON
                            logger.warning("Could not find download link in HTML. Returning resources as JSON.")
                            serializer = ResourceSerializer(resources, many=True)
                            return Response({
                                'status': 'success',
                                'course_url': course_url,
                                'authenticated': True,
                                'count': len(resources),
                                'data': serializer.data
                            }, status=status.HTTP_200_OK)

                    # Get the filename from Content-Disposition header or URL
                    filename = resource_name
                    content_disposition = file_response.headers.get('Content-Disposition', '')

                    if 'filename=' in content_disposition:
                        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if filename_match:
                            filename = filename_match.group(1)
                    elif download_url.split('/')[-1].split('?')[0]:
                        filename = download_url.split('/')[-1].split('?')[0]

                    # Add file extension if missing
                    if '.' not in filename:
                        if 'pdf' in content_type.lower():
                            filename += '.pdf'
                        elif 'word' in content_type.lower():
                            filename += '.docx'
                        elif 'excel' in content_type.lower():
                            filename += '.xlsx'
                        elif 'powerpoint' in content_type.lower():
                            filename += '.pptx'
                        elif 'text' in content_type.lower():
                            filename += '.txt'

                    logger.info(f"Using filename: {filename}")

                    # Create a file-like object from the content
                    file_content = io.BytesIO(file_response.content)

                    # Save the file to disk for debugging
                    import os
                    debug_dir = '/tmp/moodle_files'
                    os.makedirs(debug_dir, exist_ok=True)
                    debug_path = os.path.join(debug_dir, filename)
                    with open(debug_path, 'wb') as f:
                        f.write(file_response.content)
                    logger.info(f"Saved file to {debug_path} for debugging")

                    # Return the file
                    if 'pdf' in content_type.lower() or filename.lower().endswith('.pdf'):
                        response = FileResponse(file_content, content_type='application/pdf')
                    else:
                        response = FileResponse(file_content, content_type=content_type)

                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response

                except Exception as e:
                    logger.error(f"Error downloading file: {e}")
                    # Add the error to the resource
                    resource['error'] = f"Error downloading file: {str(e)}"

        # If no file downloaded or download_file is False, return the JSON response
        logger.info("Returning JSON response with resources")
        serializer = ResourceSerializer(resources, many=True)

        return Response({
            'status': 'success',
            'course_url': course_url,
            'authenticated': True,
            'count': len(resources),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class MoodleCoursesAPIView(APIView):
    """
    API view to retrieve courses from Moodle
    """
    def post(self, request):
        # Get username and password from request data
        username = request.data.get('username')
        password = request.data.get('password')
        url = request.data.get('url', 'https://elearning.univ-bba.dz')

        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to login
        login_result = moodle_login(username, password, url)

        if not login_result['success']:
            return Response({
                'status': 'error',
                'message': login_result['message']
            }, status=status.HTTP_401_UNAUTHORIZED)

        # For now, just return a success message
        # In a real implementation, we would retrieve the courses from Moodle
        return Response({
            'status': 'success',
            'message': 'Login successful, but course retrieval is not implemented yet',
            'session': login_result['cookies']
        }, status=status.HTTP_200_OK)


class MoodleLoginAPIView(APIView):
    """
    API view for Moodle login
    """
    def post(self, request):
        # Get username and password from request data
        username = request.data.get('username')
        password = request.data.get('password')
        url = request.data.get('url', 'https://elearning.univ-bba.dz')

        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Attempt to login
        login_result = moodle_login(username, password, url)

        if not login_result['success']:
            return Response({
                'status': 'error',
                'message': login_result['message']
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Return the login result with cookies for subsequent requests
        return Response({
            'status': 'success',
            'message': login_result['message'],
            'session': login_result['cookies']
        }, status=status.HTTP_200_OK)


class MoodleCoursePDFsAPIView(APIView):
    """
    API view for retrieving PDF files from Moodle courses
    """
    def post(self, request):
        # Get the course ID and session cookies
        course_id = request.data.get('course_id')
        session_cookies = request.data.get('session')
        username = request.data.get('username')
        password = request.data.get('password')
        url = request.data.get('url', 'https://elearning.univ-bba.dz')

        # Check if course ID is provided
        if not course_id:
            return Response({
                'status': 'error',
                'message': 'Course ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if we have session cookies or credentials
        if not session_cookies and (not username or not password):
            return Response({
                'status': 'error',
                'message': 'Either session cookies or username/password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # If no session cookies but credentials provided, login first
        if not session_cookies and username and password:
            login_result = moodle_login(username, password, url)
            if not login_result['success']:
                return Response({
                    'status': 'error',
                    'message': f"Login failed: {login_result['message']}"
                }, status=status.HTTP_401_UNAUTHORIZED)

            session_cookies = login_result['cookies']

        # Retrieve PDFs from the course
        pdf_result = get_course_pdfs(session_cookies, course_id, url)

        if not pdf_result['success']:
            return Response({
                'status': 'error',
                'message': pdf_result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'success',
            'message': pdf_result['message'],
            'course_name': pdf_result['course_name'],
            'count': len(pdf_result['pdfs']),
            'pdfs': pdf_result['pdfs']
        }, status=status.HTTP_200_OK)

    def get(self, request, course_id=None):
        # Check if course ID is provided
        if not course_id:
            return Response({
                'status': 'error',
                'message': 'Course ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get credentials from query parameters
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        url = request.query_params.get('url', 'https://elearning.univ-bba.dz')

        # Check if credentials are provided
        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password are required as query parameters'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Login first
        login_result = moodle_login(username, password, url)
        if not login_result['success']:
            return Response({
                'status': 'error',
                'message': f"Login failed: {login_result['message']}"
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve PDFs from the course
        pdf_result = get_course_pdfs(login_result['cookies'], course_id, url)

        if not pdf_result['success']:
            return Response({
                'status': 'error',
                'message': pdf_result['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'success',
            'message': pdf_result['message'],
            'course_name': pdf_result['course_name'],
            'count': len(pdf_result['pdfs']),
            'pdfs': pdf_result['pdfs']
        }, status=status.HTTP_200_OK)
