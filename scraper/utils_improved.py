import requests
from bs4 import BeautifulSoup
import logging
import time
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)

def scrape_elearning_courses():
    """
    Scrape courses from the elearning.univ-bba.dz website.

    Returns:
        list: A list of dictionaries containing course information.
    """
    url = "https://elearning.univ-bba.dz/course/index.php"

    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Send a GET request to the URL with headers
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log the response status and content length for debugging
        logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # If login is required, we might see a login form
        login_form = soup.select_one('form#login')
        if login_form:
            logger.warning("Login form detected. Authentication might be required.")
            # For demonstration, return a sample course indicating login required
            return [{
                'name': 'Authentication Required',
                'url': url,
                'image': None,
                'summary': 'Login is required to access the courses. Please authenticate first.',
                'teachers': []
            }]

        # Try different selectors for course elements
        course_elements = soup.select('.coursebox') or soup.select('.course-card') or soup.select('.course-item')

        # If no course elements found, try to extract any useful information
        if not course_elements:
            logger.warning("No course elements found with standard selectors. Trying alternative approach.")
            # Look for any links that might be courses
            potential_courses = soup.select('a[href*="course/view.php"]')

            courses = []
            for link in potential_courses:
                course_data = {
                    'name': link.text.strip(),
                    'url': link['href'],
                    'image': None,
                    'summary': 'Course details not available',
                    'teachers': []
                }
                courses.append(course_data)

            # If still no courses found, return a message
            if not courses:
                return [{
                    'name': 'No Courses Found',
                    'url': url,
                    'image': None,
                    'summary': 'Could not find any courses on the page. The website structure might have changed.',
                    'teachers': []
                }]

            return courses

        courses = []
        for course in course_elements:
            try:
                # Extract course name - try different selectors
                course_name_element = (course.select_one('.coursename a') or
                                      course.select_one('.course-title') or
                                      course.select_one('h3 a'))
                course_name = course_name_element.text.strip() if course_name_element else "Unknown Course"

                # Extract course URL
                course_url = course_name_element['href'] if course_name_element and 'href' in course_name_element.attrs else None

                # Extract course image if available - try different selectors
                course_image = None
                img_element = (course.select_one('.courseimage img') or
                              course.select_one('.course-image img') or
                              course.select_one('img'))
                if img_element and 'src' in img_element.attrs:
                    course_image = img_element['src']

                # Extract course summary if available - try different selectors
                course_summary = ""
                summary_element = (course.select_one('.summary') or
                                 course.select_one('.course-summary') or
                                 course.select_one('.description'))
                if summary_element:
                    course_summary = summary_element.text.strip()

                # Extract teacher information if available - try different selectors
                teachers = []
                teacher_elements = (course.select('.teachers li') or
                                  course.select('.teacher') or
                                  course.select('.instructor'))
                for teacher in teacher_elements:
                    teachers.append(teacher.text.strip())

                # Create a course dictionary
                course_data = {
                    'name': course_name,
                    'url': course_url,
                    'image': course_image,
                    'summary': course_summary,
                    'teachers': teachers
                }

                courses.append(course_data)
            except Exception as e:
                logger.error(f"Error parsing course: {e}")
                continue

        return courses

    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        # Return a message about the error
        return [{
            'name': 'Error Fetching Data',
            'url': url,
            'image': None,
            'summary': f'Error fetching data from the website: {str(e)}',
            'teachers': []
        }]
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Return a message about the error
        return [{
            'name': 'Unexpected Error',
            'url': url,
            'image': None,
            'summary': f'An unexpected error occurred: {str(e)}',
            'teachers': []
        }]


def extract_departments():
    """
    Extract department information from the elearning.univ-bba.dz website.

    Returns:
        list: A list of dictionaries containing department information.
    """
    url = "https://elearning.univ-bba.dz/course/index.php"

    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log the response status and content length for debugging
        logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # If login is required, we might see a login form
        login_form = soup.select_one('form#login')
        if login_form:
            logger.warning("Login form detected. Authentication might be required.")
            # For demonstration, return a message indicating login required
            return [{
                'id': 'auth_required',
                'name': 'Authentication Required',
                'url': url
            }]

        # Find the select element with name="jump"
        select_element = soup.find('select', attrs={'name': 'jump'})
        if not select_element:
            logger.warning("No select element with name='jump' found.")
            return [{
                'id': 'not_found',
                'name': 'No Departments Found',
                'url': url
            }]

        # Extract all option tags within the select element
        options = select_element.find_all('option')
        departments = []

        # Iterate over options to get value and text
        for option in options:
            value = option.get('value')
            if value:  # Ensure the option has a value attribute
                full_url = urljoin(url, value)  # Convert relative URL to absolute
                text = option.text.strip()      # Remove extra whitespace from text

                # Create a department dictionary
                department_data = {
                    'id': value,
                    'name': text,
                    'url': full_url
                }

                departments.append(department_data)

        return departments

    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        # Return a message about the error
        return [{
            'id': 'error',
            'name': f'Error fetching data: {str(e)}',
            'url': url
        }]
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Return a message about the error
        return [{
            'id': 'error',
            'name': f'Unexpected error: {str(e)}',
            'url': url
        }]


def extract_aalinks(url):
    """
    Extract links with the 'aalink' class from a given URL.

    Args:
        url (str): The URL to scrape for links.

    Returns:
        list: A list of dictionaries containing link information (text and href).
    """
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Log the response status and content length for debugging
        logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # If login is required, we might see a login form
        login_form = soup.select_one('form#login')
        if login_form:
            logger.warning("Login form detected. Authentication might be required.")
            # For demonstration, return a message indicating login required
            return [{
                'text': 'Authentication Required',
                'href': url,
                'error': 'Login is required to access this page.'
            }]

        # Find all links with the 'aalink' class
        aalinks = soup.select('a.aalink')

        if not aalinks:
            logger.warning(f"No links with 'aalink' class found at {url}")
            return [{
                'text': 'No Links Found',
                'href': url,
                'error': "No links with 'aalink' class found on the page."
            }]

        # Extract information from each link
        links_data = []
        for link in aalinks:
            href = link.get('href')
            text = link.text.strip()

            # Skip empty links
            if not text or not href:
                continue

            # Get course ID from href if available
            course_id = None
            if 'id=' in href:
                try:
                    course_id = href.split('id=')[1].split('&')[0]
                except (IndexError, ValueError):
                    pass

            # Create a link dictionary
            link_data = {
                'text': text,
                'href': href if href.startswith('http') else urljoin(url, href)
            }

            # Add course ID if available
            if course_id:
                link_data['course_id'] = course_id

            links_data.append(link_data)

        return links_data

    except requests.RequestException as e:
        logger.error(f"Error fetching data from {url}: {e}")
        # Return a message about the error
        return [{
            'text': 'Error Fetching Data',
            'href': url,
            'error': f'Error fetching data from the website: {str(e)}'
        }]
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        # Return a message about the error
        return [{
            'text': 'Unexpected Error',
            'href': url,
            'error': f'An unexpected error occurred: {str(e)}'
        }]


def login_to_elearning(username, password):
    """
    Login to the elearning.univ-bba.dz website and return a session object.

    Args:
        username (str): The username for the elearning website.
        password (str): The password for the elearning website.

    Returns:
        requests.Session: A session object with authentication cookies.
    """
    login_url = "https://elearning.univ-bba.dz/login/index.php"

    # Create a session object to maintain cookies
    session = requests.Session()

    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    session.headers.update(headers)

    # Set a timeout for all requests
    timeout = 30  # 30 seconds timeout

    try:
        # First, get the login page to retrieve the login token
        logger.info(f"Fetching login page: {login_url}")
        response = session.get(login_url, timeout=timeout)
        response.raise_for_status()

        # Parse the login page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the login token
        login_token = soup.select_one('input[name="logintoken"]')
        if not login_token:
            logger.error("Could not find login token on the login page.")
            return None

        login_token = login_token.get('value')
        logger.info(f"Found login token: {login_token}")

        # Prepare login data
        login_data = {
            'username': username,
            'password': password,
            'logintoken': login_token,
            'anchor': ''
        }

        # Submit the login form
        logger.info("Submitting login form")
        login_response = session.post(login_url, data=login_data, timeout=timeout)
        login_response.raise_for_status()

        # Check if login was successful
        if 'loginerrors' in login_response.text or 'Invalid login' in login_response.text:
            logger.error("Login failed. Invalid credentials.")
            return None

        logger.info(f"Login successful. Redirected to: {login_response.url}")
        return session

    except requests.exceptions.Timeout:
        logger.error("Connection to the server timed out during login")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Connection error during login. The server might be down or unreachable.")
        return None
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return None


def extract_course_resources(course_url, session=None):
    """
    Extract resource links from a course page and find PDF links.

    Args:
        course_url (str): The URL of the course page.
        session (requests.Session, optional): A session object with authentication cookies.

    Returns:
        list: A list of dictionaries containing resource information.
    """
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    # Set a timeout for all requests
    timeout = 15  # 15 seconds timeout

    try:
        # Fetch the course page using the session if provided, otherwise use a regular request
        if session:
            response = session.get(course_url, timeout=timeout)
        else:
            response = requests.get(course_url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Log the response status and content length for debugging
        logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for login form
        login_form = soup.select_one('form#login')
        if login_form:
            logger.warning("Login form detected. Authentication might be required.")
            return [{
                'resource_name': 'Authentication Required',
                'resource_url': course_url,
                'pdf_url': None,
                'error': 'Login is required to access the course page.'
            }]

        # Try different selectors for resource links
        resource_links = (
            soup.select('a.aalink[href*="resource/view.php"]') or
            soup.select('a[href*="resource/view.php"]') or
            soup.select('a[onclick*="resource/view.php"]') or
            soup.select('a[href*="pluginfile.php"]') or
            soup.select('a[href*=".pdf"]')
        )

        # Also look for any links with specific text that might indicate downloadable files
        # BeautifulSoup doesn't support :contains() selector, so we need to filter manually
        if not resource_links:
            all_links = soup.find_all('a', href=True)
            file_keywords = ['fichier', 'file', 'document', 'pdf', 'download', 'télécharger']

            filtered_links = []
            for link in all_links:
                link_text = link.text.lower()
                # Check if any of the keywords are in the link text
                if any(keyword in link_text for keyword in file_keywords):
                    filtered_links.append(link)

            if filtered_links:
                resource_links = filtered_links

        # If no resource links found, try to extract any useful information
        if not resource_links:
            logger.warning(f"No resource links found at {course_url}")

            # Look for any content that might indicate resources
            content_section = soup.select_one('.course-content')
            if content_section:
                logger.info("Found course content section, but no resource links.")
                return [{
                    'resource_name': 'Course Content Found',
                    'resource_url': course_url,
                    'pdf_url': None,
                    'error': 'Course content found, but no resource links detected. The course might use a different format for resources.'
                }]

            return [{
                'resource_name': 'No Resources Found',
                'resource_url': course_url,
                'pdf_url': None,
                'error': 'No resource links found on the course page.'
            }]

        resources = []

        # Process each resource link
        for link in resource_links:
            resource_url = link.get('href')
            onclick = link.get('onclick')

            # Try to extract URL from onclick attribute if href is not available
            if not resource_url and onclick:
                url_match = re.search(r"window\.open\('([^']+)'", onclick)
                if url_match:
                    resource_url = url_match.group(1)
                    # Remove any JS parameters
                    if '&amp;' in resource_url:
                        resource_url = resource_url.split('&amp;')[0]

            resource_name = link.text.strip()

            # Skip empty links
            if not resource_url or not resource_name:
                continue

            # Ensure absolute URL
            if not resource_url.startswith('http'):
                resource_url = urljoin(course_url, resource_url)

            # Create a resource entry
            resource_data = {
                'resource_name': resource_name,
                'resource_url': resource_url,
                'pdf_url': None
            }

            # If the URL already points to a PDF, use it directly
            if resource_url.lower().endswith('.pdf'):
                resource_data['pdf_url'] = resource_url
                resource_data['pdf_name'] = resource_name
                resources.append(resource_data)
                continue

            # Try to fetch the resource page to find PDF links
            try:
                # First, try a HEAD request to check if it's a direct download
                if session:
                    head_response = session.head(resource_url, timeout=timeout, allow_redirects=True)
                else:
                    head_response = requests.head(resource_url, headers=headers, timeout=timeout, allow_redirects=True)

                # Check if it's a direct download based on Content-Type or Content-Disposition
                content_type = head_response.headers.get('Content-Type', '')
                content_disposition = head_response.headers.get('Content-Disposition', '')

                # If it's a PDF or has a download disposition, use it directly
                if ('application/pdf' in content_type or
                    'application/octet-stream' in content_type or
                    'attachment' in content_disposition or
                    'filename=' in content_disposition):

                    # This is likely a direct download
                    resource_data['pdf_url'] = resource_url

                    # Try to get the filename from Content-Disposition
                    if 'filename=' in content_disposition:
                        import re
                        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
                        if filename_match:
                            resource_data['pdf_name'] = filename_match.group(1)
                        else:
                            resource_data['pdf_name'] = resource_name
                    else:
                        resource_data['pdf_name'] = resource_name

                    logger.info(f"Found direct download: {resource_url} with content type {content_type}")
                    continue

                # If not a direct download, fetch the full page
                if session:
                    resource_response = session.get(resource_url, timeout=timeout)
                else:
                    resource_response = requests.get(resource_url, headers=headers, timeout=timeout)
                resource_response.raise_for_status()

                # Log the response status and content length for debugging
                logger.info(f"Resource response status: {resource_response.status_code}, Content length: {len(resource_response.text)}")

                # Parse the resource page
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                # Look for PDF links with different selectors
                pdf_links = (
                    resource_soup.select('a[href*=".pdf"]') or
                    resource_soup.select('a[href*="pluginfile.php"]') or
                    resource_soup.select('iframe[src*=".pdf"]') or
                    resource_soup.select('object[data*=".pdf"]') or
                    resource_soup.select('embed[src*=".pdf"]')
                )

                if pdf_links:
                    # Get the first PDF link
                    pdf_element = pdf_links[0]
                    pdf_url = pdf_element.get('href') or pdf_element.get('src') or pdf_element.get('data')

                    if not pdf_url:
                        continue

                    if not pdf_url.startswith('http'):
                        pdf_url = urljoin(resource_url, pdf_url)

                    resource_data['pdf_url'] = pdf_url
                    resource_data['pdf_name'] = pdf_element.text.strip() if pdf_element.text.strip() else resource_name
                else:
                    # If no PDF links found, check if the page itself is a redirect to a PDF
                    meta_refresh = resource_soup.select_one('meta[http-equiv="refresh"]')
                    if meta_refresh:
                        content = meta_refresh.get('content', '')
                        if 'url=' in content.lower():
                            redirect_url = content.split('url=')[1].strip()
                            if redirect_url.lower().endswith('.pdf') or 'pluginfile.php' in redirect_url:
                                if not redirect_url.startswith('http'):
                                    redirect_url = urljoin(resource_url, redirect_url)
                                resource_data['pdf_url'] = redirect_url
                                resource_data['pdf_name'] = resource_name

                    # If still no PDF links found, check for download buttons
                    if not resource_data.get('pdf_url'):
                        # Look for download buttons or links
                        download_links = resource_soup.find_all('a', href=True)
                        for link in download_links:
                            link_text = link.text.lower()
                            if 'download' in link_text or 'télécharger' in link_text:
                                download_url = link.get('href')
                                if download_url:
                                    if not download_url.startswith('http'):
                                        download_url = urljoin(resource_url, download_url)
                                    resource_data['pdf_url'] = download_url
                                    resource_data['pdf_name'] = link.text.strip() if link.text.strip() else resource_name
                                    break
            except Exception as e:
                logger.error(f"Error fetching resource page {resource_url}: {e}")
                resource_data['error'] = f"Error fetching resource page: {str(e)}"

            resources.append(resource_data)

        return resources

    except requests.RequestException as e:
        logger.error(f"Error fetching data from {course_url}: {e}")
        return [{
            'resource_name': 'Error Fetching Data',
            'resource_url': course_url,
            'pdf_url': None,
            'error': f'Error fetching data from the course page: {str(e)}'
        }]
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return [{
            'resource_name': 'Unexpected Error',
            'resource_url': course_url,
            'pdf_url': None,
            'error': f'An unexpected error occurred: {str(e)}'
        }]
