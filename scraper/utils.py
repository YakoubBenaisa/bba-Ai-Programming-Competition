import requests
from bs4 import BeautifulSoup
import logging
import time
from urllib.parse import urljoin

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


def extract_course_resources(course_url):
    """
    Extract resource links from a course page and find PDF links.

    Args:
        course_url (str): The URL of the course page.

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

    try:
        # Fetch the course page
        response = requests.get(course_url, headers=headers, timeout=15)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Log the response status and content length for debugging
        logger.info(f"Response status: {response.status_code}, Content length: {len(response.text)}")

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

        # Find all resource links with multiple selectors
        resource_links = (
            soup.select('a.aalink[href*="resource/view.php"]') or
            soup.select('a[href*="resource/view.php"]') or
            soup.select('a[onclick*="resource/view.php"]') or
            soup.select('a[href*="pluginfile.php"]') or
            soup.select('a[href*=".pdf"]')
        )

        if not resource_links:
            logger.warning(f"No resource links found at {course_url}")
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

            # Try to fetch the resource page to find PDF links
            try:
                # Fetch the resource page
                resource_response = requests.get(resource_url, headers=headers, timeout=15)
                resource_response.raise_for_status()

                # Parse the resource page
                resource_soup = BeautifulSoup(resource_response.text, 'html.parser')

                # Look for PDF links
                pdf_links = resource_soup.select('a[href*=".pdf"]')

                if pdf_links:
                    # Get the first PDF link
                    pdf_url = pdf_links[0].get('href')
                    if not pdf_url.startswith('http'):
                        pdf_url = urljoin(resource_url, pdf_url)

                    resource_data['pdf_url'] = pdf_url
                    resource_data['pdf_name'] = pdf_links[0].text.strip()
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
