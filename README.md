# Elearning Scraper API

A Django REST API for scraping course information, resources, and PDF links from the elearning.univ-bba.dz website.

## Features

- Scrape courses from the main page
- Extract departments from the website
- Get courses by category
- Extract links with the 'aalink' class from any page
- Get resources and PDF links from course pages
- Handle authentication requirements detection
- Robust error handling

## Installation

### Prerequisites

- Python 3.8+
- pip
- virtualenv

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd aiHackathon
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install django djangorestframework requests beautifulsoup4
```

4. Run migrations:

```bash
cd myproject
python manage.py migrate
```

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## API Documentation

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

A Postman collection is also provided in the file `elearning_scraper_api.postman_collection.json`.

## Usage Examples

### Get courses from a specific category:

```bash
curl -X GET http://127.0.0.1:8000/api/category/162/courses/
```

### Extract resources from a course page:

```bash
curl -X GET http://127.0.0.1:8000/api/course/1280/resources/
```

### Extract resources from any course URL:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"url": "https://elearning.univ-bba.dz/course/view.php?id=1280"}' http://127.0.0.1:8000/api/resources/
```

## Authentication Note

The API itself does not require authentication, but the elearning.univ-bba.dz website requires authentication to access most resources. The API will detect when authentication is required and return an appropriate message.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)
- [Requests](https://requests.readthedocs.io/)
