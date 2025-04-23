import requests
import logging
import json
import subprocess
import os
import re
from pathlib import Path
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup
except ImportError:
    # Install BeautifulSoup if not available
    import subprocess
    subprocess.check_call(["pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

def moodle_login(username, password, url='https://elearning.univ-bba.dz'):
    """
    Login to Moodle using the Node.js implementation

    Args:
        username (str): The username for Moodle
        password (str): The password for Moodle
        url (str): The Moodle URL

    Returns:
        dict: Login result containing success status, message, and session cookies
    """
    try:
        # Path to the Node.js script
        script_path = Path(__file__).parent.parent / 'moodle_login_cli.js'

        # Run the Node.js script
        process = subprocess.run(
            ['node', str(script_path), username, password, url],
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the output
        output = process.stdout
        logger.info(f"Login process output: {output}")

        # Check if login was successful
        if "Login successful: true" in output:
            # Extract cookies using direct HTTP request
            session = requests.Session()
            login_url = f"{url}/login/index.php"

            # Get login page to extract token
            response = session.get(login_url)

            # Extract login token
            import re
            token_match = re.search(r'name="logintoken" value="([^"]+)"', response.text)
            if not token_match:
                return {
                    'success': False,
                    'message': 'Login token not found',
                    'cookies': None
                }

            login_token = token_match.group(1)

            # Login with credentials
            login_data = {
                'username': username,
                'password': password,
                'logintoken': login_token,
                'anchor': ''
            }

            login_response = session.post(login_url, data=login_data)

            # Check if login was successful
            if login_response.url != login_url and 'loginerrors' not in login_response.text:
                return {
                    'success': True,
                    'message': 'Login successful',
                    'cookies': dict(session.cookies)
                }
            else:
                return {
                    'success': False,
                    'message': 'Login failed. Please check your credentials.',
                    'cookies': None
                }
        else:
            return {
                'success': False,
                'message': 'Login failed. Please check your credentials.',
                'cookies': None
            }
    except subprocess.CalledProcessError as e:
        logger.error(f"Login process error: {e.stderr}")
        return {
            'success': False,
            'message': f"Login process error: {e.stderr}",
            'cookies': None
        }
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return {
            'success': False,
            'message': f"Unexpected error: {str(e)}",
            'cookies': None
        }

def get_category_courses(category_id, username, password, url='https://elearning.univ-bba.dz'):
    """
    Retrieve courses from a Moodle category

    Args:
        category_id (str): The category ID to retrieve courses from
        username (str): The username for Moodle
        password (str): The password for Moodle
        url (str): The Moodle URL

    Returns:
        dict: Result containing success status, message, and list of courses
    """
    try:
        # Login to Moodle
        login_result = moodle_login(username, password, url)

        if not login_result.get('success'):
            return {
                'success': False,
                'message': login_result.get('message', 'Login failed'),
                'courses': []
            }

        # Create a session with the provided cookies
        session = requests.Session()
        for key, value in login_result.get('cookies', {}).items():
            session.cookies.set(key, value)

        # Get the category page
        category_url = f"{url}/course/index.php?categoryid={category_id}"
        logger.info(f"Fetching category page: {category_url}")
        category_response = session.get(category_url)

        # Log the response status and size
        logger.info(f"Category page response status: {category_response.status_code}")
        logger.info(f"Category page response size: {len(category_response.text)} bytes")

        if category_response.status_code != 200:
            return {
                'success': False,
                'message': f"Failed to access category page. Status code: {category_response.status_code}",
                'courses': []
            }

        # Check if we're actually logged in
        if 'loginerrors' in category_response.text or 'login/index.php' in category_response.url:
            return {
                'success': False,
                'message': "Not logged in or session expired",
                'courses': []
            }

        # Parse the category page

        soup = BeautifulSoup(category_response.text, 'html.parser')

        # Get category name
        category_name = soup.select_one('h1').text.strip() if soup.select_one('h1') else f"Category {category_id}"

        # Find all course links
        course_links = soup.select('a[href*="/course/view.php?id="]')

        if not course_links:
            return {
                'success': True,
                'message': f"No courses found in category {category_id}",
                'category_name': category_name,
                'courses': []
            }

        # Log the number of courses found
        logger.info(f"Found {len(course_links)} courses in category {category_id}")

        # Process each course link
        courses = []

        for link in course_links:
            course_name = link.text.strip()
            course_url = link.get('href')

            # Skip if no URL
            if not course_url:
                continue

            # Make sure URL is absolute
            if not course_url.startswith('http'):
                course_url = urljoin(url, course_url)

            # Extract course ID from URL
            import re
            course_id_match = re.search(r'id=([0-9]+)', course_url)
            if not course_id_match:
                continue

            course_id = course_id_match.group(1)

            # Add to the list of courses
            courses.append({
                'id': course_id,
                'name': course_name,
                'url': course_url
            })

            # Log the course
            logger.info(f"Found course: {course_name} (ID: {course_id})")

        return {
            'success': True,
            'message': f"Found {len(courses)} courses in category {category_id}",
            'category_name': category_name,
            'courses': courses
        }
    except Exception as e:
        logger.error(f"Unexpected error retrieving courses: {str(e)}")
        return {
            'success': False,
            'message': f"Unexpected error: {str(e)}",
            'courses': []
        }


def get_course_pdfs(course_id, username, password, url='https://elearning.univ-bba.dz'):
    """
    Retrieve PDF files from a Moodle course

    Args:
        course_id (str): The course ID to retrieve PDFs from
        username (str): The username for Moodle
        password (str): The password for Moodle
        url (str): The Moodle URL

    Returns:
        dict: Result containing success status, message, and list of PDF files
    """
    try:
        # Login to Moodle
        login_result = moodle_login(username, password, url)

        if not login_result.get('success'):
            return {
                'success': False,
                'message': login_result.get('message', 'Login failed'),
                'pdfs': []
            }

        # Create a session with the provided cookies
        session = requests.Session()
        for key, value in login_result.get('cookies', {}).items():
            session.cookies.set(key, value)

        # Get the course page
        course_url = f"{url}/course/view.php?id={course_id}"
        logger.info(f"Fetching course page: {course_url}")
        course_response = session.get(course_url)

        # Log the response status and size
        logger.info(f"Course page response status: {course_response.status_code}")
        logger.info(f"Course page response size: {len(course_response.text)} bytes")

        if course_response.status_code != 200:
            return {
                'success': False,
                'message': f"Failed to access course page. Status code: {course_response.status_code}",
                'pdfs': []
            }

        # Check if we're actually logged in
        if 'loginerrors' in course_response.text or 'login/index.php' in course_response.url:
            return {
                'success': False,
                'message': "Not logged in or session expired",
                'pdfs': []
            }

        # Parse the course page

        soup = BeautifulSoup(course_response.text, 'html.parser')

        # Get course name
        course_name = soup.select_one('h1').text.strip() if soup.select_one('h1') else f"Course {course_id}"

        # Find all resource links - look for various types of resource links
        resource_links = soup.select('a[href*="/mod/resource/view.php"], a[href*="/mod/folder/view.php"]')

        # Also look for links with aalink class (common in Moodle for resources)
        aalink_resources = soup.select('a.aalink')
        for link in aalink_resources:
            if link not in resource_links:
                resource_links.append(link)

        # Also look for direct PDF links in the course page
        direct_pdf_links = soup.select('a[href*=".pdf"], a[href*="pluginfile.php"]')

        # Add direct PDF links to resource links for processing
        for link in direct_pdf_links:
            if link not in resource_links:
                resource_links.append(link)

        # Log all found resource links for debugging
        for link in resource_links:
            href = link.get('href', '')
            text = link.text.strip()
            logger.info(f"Found resource link: {text} - {href}")

        if not resource_links:
            return {
                'success': True,
                'message': f"No resources found in course {course_id}",
                'course_name': course_name,
                'pdfs': []
            }

        # Log the number of resources found
        logger.info(f"Found {len(resource_links)} resources in course {course_id}")

        # Process each resource link to find PDFs
        pdfs = []

        for link in resource_links:
            resource_name = link.text.strip()
            resource_url = link.get('href')

            # Skip if no URL
            if not resource_url:
                continue

            # Make sure URL is absolute
            if not resource_url.startswith('http'):
                resource_url = urljoin(url, resource_url)

            # Check if this is a direct PDF link or a resource link that might be a PDF
            if resource_url.lower().endswith('.pdf') or 'pluginfile.php' in resource_url or '/mod/resource/view.php' in resource_url:
                # For resource links, we need to check if they directly download a PDF
                if '/mod/resource/view.php' in resource_url:
                    # Try a HEAD request first to see if it's a PDF
                    try:
                        logger.info(f"Checking if resource is a direct PDF download: {resource_url}")
                        head_response = session.head(resource_url, allow_redirects=True)

                        # Check the final URL after redirects
                        final_url = head_response.url
                        content_type = head_response.headers.get('Content-Type', '')
                        content_disposition = head_response.headers.get('Content-Disposition', '')

                        logger.info(f"Final URL: {final_url}")
                        logger.info(f"Content-Type: {content_type}")
                        logger.info(f"Content-Disposition: {content_disposition}")

                        # If it's a PDF content type or has a PDF extension or has a download disposition
                        is_pdf = ('application/pdf' in content_type or
                                 final_url.lower().endswith('.pdf') or
                                 'pluginfile.php' in final_url or
                                 ('attachment' in content_disposition and '.pdf' in content_disposition))

                        if is_pdf:
                            # This is a direct PDF download
                            pdf_url = resource_url
                            pdf_name = resource_name

                            # Try to get a better filename from Content-Disposition
                            if 'filename=' in content_disposition:
                                import re
                                filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                                if filename_match:
                                    pdf_name = filename_match.group(1)
                            # Or from the URL if it ends with .pdf
                            elif final_url.lower().endswith('.pdf'):
                                pdf_name = final_url.split('/')[-1]

                            # Add to the list of PDFs
                            pdfs.append({
                                'name': pdf_name,
                                'url': resource_url,  # Use the original URL for downloading
                                'resource_name': resource_name,
                                'resource_url': resource_url,
                                'type': 'resource_pdf'
                            })

                            # Log the resource PDF link
                            logger.info(f"Found resource that directly downloads a PDF: {resource_url}")
                            continue
                    except Exception as e:
                        logger.error(f"Error checking if resource is a PDF: {str(e)}")
                        # Continue with normal processing

                # For direct PDF links
                if resource_url.lower().endswith('.pdf') or 'pluginfile.php' in resource_url:
                    # This is likely a direct PDF link
                    pdf_url = resource_url
                    pdf_name = resource_name

                    # If URL ends with .pdf, extract the filename
                    if pdf_url.lower().endswith('.pdf'):
                        pdf_name = pdf_url.split('/')[-1]

                    # Add to the list of PDFs
                    pdfs.append({
                        'name': pdf_name,
                        'url': pdf_url,
                        'resource_name': resource_name,
                        'resource_url': resource_url,
                        'type': 'direct_link'
                    })

                    # Log the direct PDF link
                    logger.info(f"Found direct PDF link: {pdf_url}")
                    continue

            try:
                # Fetch the resource page
                logger.info(f"Fetching resource: {resource_url}")
                resource_response = session.get(resource_url)

                if resource_response.status_code != 200:
                    logger.warning(f"Failed to access resource {resource_name}. Status code: {resource_response.status_code}")
                    continue

                # Parse the resource page
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                # Check if this is a folder
                if '/mod/folder/view.php' in resource_url:
                    # This is a folder, look for PDF links in the folder
                    folder_pdf_links = resource_soup.select('a[href*=".pdf"], a[href*="pluginfile.php"]')

                    for pdf_link in folder_pdf_links:
                        pdf_url = pdf_link.get('href')
                        if not pdf_url:
                            continue

                        # Make sure URL is absolute
                        if not pdf_url.startswith('http'):
                            pdf_url = urljoin(url, pdf_url)

                        # Get the PDF name
                        pdf_name = pdf_link.text.strip()
                        if not pdf_name or pdf_name == '':
                            # If no text, try to get the filename from the URL
                            if pdf_url.lower().endswith('.pdf'):
                                pdf_name = pdf_url.split('/')[-1]
                            else:
                                pdf_name = f"File in {resource_name}"

                        # Add to the list of PDFs
                        pdfs.append({
                            'name': pdf_name,
                            'url': pdf_url,
                            'resource_name': resource_name,
                            'resource_url': resource_url,
                            'type': 'folder'
                        })

                        # Log the folder PDF link
                        logger.info(f"Found PDF in folder: {pdf_url}")

                    # If we found PDFs in the folder, continue to the next resource
                    if folder_pdf_links:
                        continue

                # Look for PDF links - try different patterns
                pdf_links = (
                    resource_soup.select('a[href*=".pdf"]') or
                    resource_soup.select('a[href*="pluginfile.php"]') or
                    resource_soup.select('iframe[src*=".pdf"]') or
                    resource_soup.select('object[data*=".pdf"]') or
                    resource_soup.select('embed[src*=".pdf"]') or
                    # Also look for resource links that might lead to PDFs
                    resource_soup.select('a[href*="/mod/resource/view.php"]')
                )

                # If we didn't find any PDF links but the page has a div with resourcecontent class
                # (common for embedded resources), this might be a PDF displayed inline
                if not pdf_links and resource_soup.select_one('div.resourcecontent'):
                    # This might be an embedded PDF, check for object or iframe tags
                    embedded_pdfs = (
                        resource_soup.select('object[type="application/pdf"]') or
                        resource_soup.select('iframe[src*="pluginfile.php"]') or
                        resource_soup.select('embed[type="application/pdf"]')
                    )

                    if embedded_pdfs:
                        pdf_links = embedded_pdfs
                    else:
                        # If still no PDF links found, check if there's a download button
                        download_links = resource_soup.select('a.resourcelinkdetails')
                        if download_links:
                            pdf_links = download_links

                # Also check for redirects to PDF files
                meta_refresh = resource_soup.select_one('meta[http-equiv="refresh"]')
                if meta_refresh and 'content' in meta_refresh.attrs:
                    refresh_content = meta_refresh['content']
                    url_match = re.search(r'URL=([^"]+)', refresh_content)
                    if url_match:
                        redirect_url = url_match.group(1)
                        if redirect_url.lower().endswith('.pdf') or 'pluginfile.php' in redirect_url:
                            # This is a redirect to a PDF
                            pdf_links = [{'href': redirect_url}]

                # If we still don't have PDF links, check for a direct download link
                if not pdf_links:
                    # Look for any button or link that might be a download button
                    download_buttons = resource_soup.select('a.btn, button.btn, a[role="button"]')
                    for button in download_buttons:
                        button_text = button.text.lower()
                        if 'download' in button_text or 'télécharger' in button_text:
                            href = button.get('href')
                            if href:
                                pdf_links = [{'href': href}]
                                break

                if pdf_links:
                    # Get the first PDF link
                    pdf_element = pdf_links[0]
                    pdf_url = pdf_element.get('href') or pdf_element.get('src') or pdf_element.get('data')

                    if not pdf_url:
                        continue

                    # Make sure URL is absolute
                    if not pdf_url.startswith('http'):
                        pdf_url = urljoin(url, pdf_url)

                    # Try to get the PDF filename
                    pdf_name = resource_name

                    # If URL ends with .pdf, extract the filename
                    if pdf_url.lower().endswith('.pdf'):
                        pdf_name = pdf_url.split('/')[-1]

                    # Add to the list of PDFs
                    pdfs.append({
                        'name': pdf_name,
                        'url': pdf_url,
                        'resource_name': resource_name,
                        'resource_url': resource_url,
                        'type': 'resource'
                    })

                    # Log the resource PDF link
                    logger.info(f"Found PDF in resource: {pdf_url}")
            except Exception as e:
                logger.error(f"Error processing resource {resource_name}: {str(e)}")
                continue

        return {
            'success': True,
            'message': f"Found {len(pdfs)} PDF files in course {course_id}",
            'course_name': course_name,
            'pdfs': pdfs
        }
    except Exception as e:
        logger.error(f"Unexpected error retrieving PDFs: {str(e)}")
        return {
            'success': False,
            'message': f"Unexpected error: {str(e)}",
            'pdfs': []
        }


def upload_file_to_course(username, password, course_id, file_path, file_name=None, url='https://elearning.univ-bba.dz'):
    """
    Upload a file to a Moodle course

    Args:
        username (str): The username for Moodle
        password (str): The password for Moodle
        course_id (str): The course ID to upload to
        file_path (str): Path to the file to upload
        file_name (str, optional): Name to use for the file (defaults to original filename)
        url (str): The Moodle URL

    Returns:
        dict: Upload result containing success status and message
    """
    try:
        if not file_name:
            file_name = os.path.basename(file_path)

        # Login to Moodle
        login_result = moodle_login(username, password, url)

        if not login_result.get('success'):
            return {
                'success': False,
                'message': login_result.get('message', 'Login failed')
            }

        # Create a session with the provided cookies
        session = requests.Session()
        for key, value in login_result.get('cookies', {}).items():
            session.cookies.set(key, value)

        # Get the course page to find the section to upload to
        course_url = f"{url}/course/view.php?id={course_id}"
        course_response = session.get(course_url)

        if course_response.status_code != 200:
            return {
                'success': False,
                'message': f"Failed to access course page. Status code: {course_response.status_code}"
            }

        # Check if we're actually logged in
        if 'loginerrors' in course_response.text or 'login/index.php' in course_response.url:
            return {
                'success': False,
                'message': "Not logged in or session expired"
            }

        # Find the upload form or link

        soup = BeautifulSoup(course_response.text, 'html.parser')

        # Look for the "Add an activity or resource" button
        add_resource_links = soup.select('a.section-modchooser-link')

        if not add_resource_links:
            return {
                'success': False,
                'message': "Could not find 'Add an activity or resource' button. You might not have permission to add resources."
            }

        # Get the first section's add resource link
        add_resource_url = add_resource_links[0].get('href')
        if not add_resource_url.startswith('http'):
            add_resource_url = f"{url}{add_resource_url}"

        # Get the resource selection page
        resource_selection_response = session.get(add_resource_url)

        # Find the link to add a file resource
        soup = BeautifulSoup(resource_selection_response.text, 'html.parser')
        file_resource_link = soup.select_one('a[href*="resource"]')

        if not file_resource_link:
            return {
                'success': False,
                'message': "Could not find file resource option"
            }

        file_resource_url = file_resource_link.get('href')
        if not file_resource_url.startswith('http'):
            file_resource_url = f"{url}{file_resource_url}"

        # Get the file upload form
        file_form_response = session.get(file_resource_url)

        # Extract the form token
        soup = BeautifulSoup(file_form_response.text, 'html.parser')
        form_token = soup.select_one('input[name="sesskey"]')

        if not form_token:
            return {
                'success': False,
                'message': "Could not find form token"
            }

        sesskey = form_token.get('value')

        # Find the file upload area
        file_manager_element = soup.select_one('div[data-fieldtype="filemanager"]')

        if not file_manager_element:
            return {
                'success': False,
                'message': "Could not find file upload area"
            }

        item_id = file_manager_element.get('id')

        # Prepare the file upload request
        upload_url = f"{url}/repository/repository_ajax.php?action=upload"

        # Prepare the file upload form data
        with open(file_path, 'rb') as f:
            files = {
                'repo_upload_file': (file_name, f, 'application/pdf')
            }

            form_data = {
                'sesskey': sesskey,
                'repo_id': '4',  # This might need to be adjusted based on the Moodle instance
                'itemid': item_id,
                'author': 'API Upload',
                'title': file_name,
                'filearea': 'content',
                'filepath': '/',
                'filename': file_name,
                'ctx_id': course_id
            }

            # Upload the file
            upload_response = session.post(upload_url, data=form_data, files=files)

            if upload_response.status_code != 200:
                return {
                    'success': False,
                    'message': f"File upload failed. Status code: {upload_response.status_code}"
                }

            # Parse the response
            try:
                upload_result = upload_response.json()

                if 'error' in upload_result:
                    return {
                        'success': False,
                        'message': f"File upload error: {upload_result['error']}"
                    }

                # Submit the form to save the resource
                form_action = soup.select_one('form').get('action')

                form_data = {
                    'name': file_name,
                    'introeditor[text]': f"Uploaded file: {file_name}",
                    'introeditor[format]': '1',
                    'introeditor[itemid]': item_id,
                    'showdescription': '0',
                    'display': '0',
                    'showsize': '0',
                    'showtype': '0',
                    'showdate': '0',
                    'filterfiles': '0',
                    'printintro': '0',
                    'showresourceoptions': '1',
                    'sesskey': sesskey,
                    'course': course_id,
                    'section': '0',
                    'module': '17',  # This might need to be adjusted
                    'modulename': 'resource',
                    'instance': '0',
                    'add': 'resource',
                    'update': '0',
                    'return': '0',
                    'sr': '0',
                    'submitbutton': 'Save and return to course'
                }

                save_response = session.post(form_action, data=form_data)

                if save_response.status_code != 200:
                    return {
                        'success': False,
                        'message': f"Failed to save resource. Status code: {save_response.status_code}"
                    }

                return {
                    'success': True,
                    'message': f"File '{file_name}' uploaded successfully to course {course_id}"
                }

            except json.JSONDecodeError:
                return {
                    'success': False,
                    'message': "Failed to parse upload response"
                }
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {str(e)}")
        return {
            'success': False,
            'message': f"Unexpected error: {str(e)}"
        }


def get_direct_file_url(resource_url, session):
    """
    Get the direct file URL from a Moodle resource URL

    Args:
        resource_url (str): The resource URL
        session (requests.Session): The authenticated session

    Returns:
        dict: Result containing success status, message, and direct URL
    """
    try:
        logger.info(f"Getting direct file URL from: {resource_url}")

        # If this is a resource URL, try to add a special parameter to force download
        if '/mod/resource/view.php' in resource_url:
            # Add forcedownload=1 parameter
            if '?' in resource_url:
                direct_url = resource_url + '&forcedownload=1'
            else:
                direct_url = resource_url + '?forcedownload=1'

            logger.info(f"Added forcedownload parameter: {direct_url}")
            return {
                'success': True,
                'message': 'Added forcedownload parameter',
                'url': direct_url
            }

        # Get the resource page
        response = session.get(resource_url, timeout=30, allow_redirects=True)
        response.raise_for_status()

        # Log the HTML content for debugging
        logger.info(f"Resource page HTML (first 500 chars): {response.text[:500]}")

        # Check if we're redirected to a file
        if 'pluginfile.php' in response.url or 'webservice' in response.url:
            logger.info(f"Redirected to direct file URL: {response.url}")
            return {
                'success': True,
                'message': 'Redirected to direct file URL',
                'url': response.url
            }

        # Parse the HTML to find the file URL
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for common file link patterns
        file_links = soup.select('a[href*=".pdf"], a[href*="pluginfile.php"], a[href*="webservice"], a[href*=".docx"], a[href*=".xlsx"], a[href*=".pptx"], a[href*="mod/resource/view.php"]')

        # Log all found links for debugging
        all_links = soup.select('a[href]')
        logger.info(f"Found {len(all_links)} links in the page")
        for link in all_links[:10]:  # Log first 10 links
            href = link.get('href')
            text = link.text.strip()
            logger.info(f"Link: {text} - {href}")

        if file_links:
            direct_url = file_links[0].get('href')
            if not direct_url.startswith('http'):
                direct_url = urljoin(resource_url, direct_url)

            logger.info(f"Found direct file URL in HTML: {direct_url}")
            return {
                'success': True,
                'message': 'Found direct file URL in HTML',
                'url': direct_url
            }

        # Look for iframe sources
        iframes = soup.select('iframe[src*="pluginfile.php"], iframe[src*="webservice"]')
        if iframes:
            direct_url = iframes[0].get('src')
            if not direct_url.startswith('http'):
                direct_url = urljoin(resource_url, direct_url)

            logger.info(f"Found direct file URL in iframe: {direct_url}")
            return {
                'success': True,
                'message': 'Found direct file URL in iframe',
                'url': direct_url
            }

        # Look for resource object data
        objects = soup.select('object[data*="pluginfile.php"], object[data*="webservice"]')
        if objects:
            direct_url = objects[0].get('data')
            if not direct_url.startswith('http'):
                direct_url = urljoin(resource_url, direct_url)

            logger.info(f"Found direct file URL in object: {direct_url}")
            return {
                'success': True,
                'message': 'Found direct file URL in object',
                'url': direct_url
            }

        # Look for download buttons
        download_buttons = soup.select('a.resourcelinkdetails, a.btn-primary, a.btn-secondary, a.btn-default, a.btn')
        for button in download_buttons:
            if 'download' in button.text.lower() or 'télécharger' in button.text.lower():
                direct_url = button.get('href')
                if not direct_url.startswith('http'):
                    direct_url = urljoin(resource_url, direct_url)

                logger.info(f"Found direct file URL in download button: {direct_url}")
                return {
                    'success': True,
                    'message': 'Found direct file URL in download button',
                    'url': direct_url
                }

        # Look for resource content frame
        resource_frame = soup.select_one('div.resourceworkaround')
        if resource_frame:
            logger.info("Found resource content frame")
            # Try to find the resource object or iframe inside
            resource_object = resource_frame.select_one('object, iframe, embed')
            if resource_object:
                data_attr = resource_object.get('data') or resource_object.get('src')
                if data_attr:
                    if not data_attr.startswith('http'):
                        data_attr = urljoin(resource_url, data_attr)

                    logger.info(f"Found direct file URL in resource frame: {data_attr}")
                    return {
                        'success': True,
                        'message': 'Found direct file URL in resource frame',
                        'url': data_attr
                    }

        # Look for resource content div
        resource_content = soup.select_one('div.resourcecontent')
        if resource_content:
            logger.info("Found resource content div")
            # Try to find any links inside
            content_links = resource_content.select('a[href]')
            if content_links:
                direct_url = content_links[0].get('href')
                if not direct_url.startswith('http'):
                    direct_url = urljoin(resource_url, direct_url)

                logger.info(f"Found direct file URL in resource content: {direct_url}")
                return {
                    'success': True,
                    'message': 'Found direct file URL in resource content',
                    'url': direct_url
                }

            # Try to find any objects or iframes inside
            content_objects = resource_content.select('object, iframe, embed')
            if content_objects:
                data_attr = content_objects[0].get('data') or content_objects[0].get('src')
                if data_attr:
                    if not data_attr.startswith('http'):
                        data_attr = urljoin(resource_url, data_attr)

                    logger.info(f"Found direct file URL in resource content object: {data_attr}")
                    return {
                        'success': True,
                        'message': 'Found direct file URL in resource content object',
                        'url': data_attr
                    }

        # If we can't find a direct URL, return the original URL
        logger.warning(f"Could not find direct file URL in: {resource_url}")
        return {
            'success': False,
            'message': 'Could not find direct file URL',
            'url': resource_url
        }
    except Exception as e:
        logger.error(f"Error getting direct file URL: {str(e)}")
        return {
            'success': False,
            'message': f"Error getting direct file URL: {str(e)}",
            'url': resource_url
        }
