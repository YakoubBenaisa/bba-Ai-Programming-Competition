# Elearning Scraper API Documentation

This document provides detailed information about the API endpoints for scraping the elearning.univ-bba.dz website.

## Base URL

All endpoints are relative to the base URL:

```
http://127.0.0.1:8000/api/
```

## Authentication

The API itself does not require authentication to use. However, the elearning.univ-bba.dz website requires authentication to access most resources.

For endpoints that need to access authenticated content on the elearning website, you can provide your elearning credentials in the request body. These credentials are only used to authenticate with the elearning website and are not stored by the API.

Alternatively, you can use the `/moodle-login/` endpoint to obtain a session that can be used for subsequent requests.

## Endpoints

### 1. Get All Courses

Retrieves all courses from the elearning.univ-bba.dz website.

- **URL**: `/courses/`
- **Method**: `GET`
- **URL Parameters**: None
- **Data Parameters**: None

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "name": "Course Name",
      "url": "https://elearning.univ-bba.dz/course/view.php?id=1234",
      "image": "https://elearning.univ-bba.dz/path/to/image.jpg",
      "summary": "Course summary text",
      "teachers": ["Teacher 1", "Teacher 2"]
    },
    // More courses...
  ]
}
```

### 2. Get All Departments

Retrieves all departments from the elearning.univ-bba.dz website.

- **URL**: `/departments/`
- **Method**: `GET`
- **URL Parameters**: None
- **Data Parameters**: None

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "id": "department_id",
      "name": "Department Name",
      "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=123"
    },
    // More departments...
  ]
}
```

### 3. Get Courses by Category

Retrieves courses from a specific category.

- **URL**: `/category/:category_id/courses/`
- **Method**: `GET`
- **URL Parameters**:
  - `category_id`: The ID of the category to retrieve courses from

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "category_id": "162",
  "count": 12,
  "data": [
    {
      "text": "Thermodynamique Appliquée",
      "href": "https://elearning.univ-bba.dz/course/view.php?id=1280",
      "course_id": "1280"
    },
    // More courses...
  ]
}
```

### 4. Extract Links from URL

Extracts links with the 'aalink' class from a provided URL.

- **URL**: `/links/`
- **Method**: `POST`
- **URL Parameters**: None
- **Data Parameters**:
  - `url`: The URL to extract links from

#### Request Example

```json
{
  "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=162"
}
```

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "count": 12,
  "data": [
    {
      "text": "Thermodynamique Appliquée",
      "href": "https://elearning.univ-bba.dz/course/view.php?id=1280",
      "course_id": "1280"
    },
    // More links...
  ]
}
```

### 5. Get Course Resources by ID

Retrieves resources and PDF links from a specific course page by ID.

- **URL**: `/course/:course_id/resources/`
- **Method**: `GET`
- **URL Parameters**:
  - `course_id`: The ID of the course to retrieve resources from

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "course_id": "1280",
  "course_url": "https://elearning.univ-bba.dz/course/view.php?id=1280",
  "count": 3,
  "data": [
    {
      "resource_name": "Resource Name",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=1496",
      "pdf_url": "https://elearning.univ-bba.dz/pluginfile.php/4326/mod_resource/content/1/document.pdf",
      "pdf_name": "document.pdf"
    },
    // More resources...
  ]
}
```

### 6. Extract Resources from Course URL

Extracts resources and PDF links from a provided course URL.

- **URL**: `/resources/`
- **Method**: `POST`
- **URL Parameters**: None
- **Data Parameters**:
  - `url`: The course URL to extract resources from

#### Request Example

```json
{
  "url": "https://elearning.univ-bba.dz/course/view.php?id=1280"
}
```

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "course_url": "https://elearning.univ-bba.dz/course/view.php?id=1280",
  "count": 3,
  "data": [
    {
      "resource_name": "Resource Name",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=1496",
      "pdf_url": "https://elearning.univ-bba.dz/pluginfile.php/4326/mod_resource/content/1/document.pdf",
      "pdf_name": "document.pdf"
    },
    // More resources...
  ]
}
```

### 7. Extract Resources with Authentication

Extracts resources and PDF links from a provided course URL using authentication credentials for the elearning website.

- **URL**: `/auth-resources/`
- **Method**: `POST`
- **URL Parameters**: None
- **Data Parameters**:
  - `url`: The course URL to extract resources from
  - `username`: Your elearning website username
  - `password`: Your elearning website password

#### Request Example

```json
{
  "url": "https://elearning.univ-bba.dz/course/view.php?id=5873",
  "username": "your_username",
  "password": "your_password"
}
```

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "course_url": "https://elearning.univ-bba.dz/course/view.php?id=5873",
  "authenticated": true,
  "count": 3,
  "data": [
    {
      "resource_name": "Resource Name",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=1496",
      "pdf_url": "https://elearning.univ-bba.dz/pluginfile.php/4326/mod_resource/content/1/document.pdf",
      "pdf_name": "document.pdf"
    },
    // More resources...
  ]
}
```

#### Error Response - Authentication Failed

- **Code**: 401 Unauthorized
- **Content Example**:

```json
{
  "status": "error",
  "message": "Authentication failed. Please check your credentials."
}
```

### 8. Moodle Login

Authenticate with the Moodle site and get a session that can be used for subsequent requests.

- **URL**: `/moodle-login/`
- **Method**: `POST`
- **URL Parameters**: None
- **Data Parameters**:
  - `username`: Your Moodle username
  - `password`: Your Moodle password
  - `url` (optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')

#### Request Example

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "message": "Login successful",
  "session": {
    "MoodleSession": "abc123def456",
    "MOODLEID1_": "xyz789"
  }
}
```

#### Error Response - Authentication Failed

- **Code**: 401 Unauthorized
- **Content Example**:

```json
{
  "status": "error",
  "message": "Login failed. Please check your credentials."
}
```

### 9. Get Course PDFs

Retrieve all PDF files from a Moodle course.

- **URL**: `/moodle-pdfs/` or `/moodle-pdfs/:course_id/`
- **Method**: `POST` or `GET`
- **URL Parameters** (for GET):
  - `course_id`: The ID of the course to retrieve PDFs from
- **Query Parameters** (for GET):
  - `username`: Your Moodle username
  - `password`: Your Moodle password
  - `url` (optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')
- **Data Parameters** (for POST):
  - `course_id`: The ID of the course to retrieve PDFs from
  - `session`: Session cookies from a successful login
  - OR
  - `username`: Your Moodle username
  - `password`: Your Moodle password
  - `url` (optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')

#### Request Example (POST)

```json
{
  "course_id": "1280",
  "username": "your_username",
  "password": "your_password"
}
```

#### Success Response

- **Code**: 200 OK
- **Content Example**:

```json
{
  "status": "success",
  "message": "Found 5 PDF files in course 1280",
  "course_name": "Thermodynamique Appliquée",
  "count": 5,
  "pdfs": [
    {
      "name": "lecture1.pdf",
      "url": "https://elearning.univ-bba.dz/pluginfile.php/4326/mod_resource/content/1/lecture1.pdf",
      "resource_name": "Lecture 1",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=1496"
    },
    // More PDFs...
  ]
}
```

#### Error Response - Authentication Failed

- **Code**: 401 Unauthorized
- **Content Example**:

```json
{
  "status": "error",
  "message": "Login failed: Authentication failed. Please check your credentials."
}
```

## Error Handling

All endpoints return appropriate error messages in case of failure. The general format for error responses is:

```json
{
  "status": "error",
  "message": "Error message describing what went wrong"
}
```

## Authentication Requirements

Note that many resources on the elearning.univ-bba.dz website require authentication. If authentication is required, the API will return a response indicating this:

```json
{
  "status": "success",
  "count": 1,
  "data": [
    {
      "resource_name": "Authentication Required",
      "resource_url": "https://elearning.univ-bba.dz/course/view.php?id=1280",
      "pdf_url": null,
      "error": "Login is required to access the course page."
    }
  ]
}
```

## Importing the Postman Collection

A Postman collection file (`elearning_scraper_api.postman_collection.json`) is provided with this API. To use it:

1. Open Postman
2. Click on "Import" in the top left
3. Select the `elearning_scraper_api.postman_collection.json` file
4. The collection will be imported with all the endpoints ready to use

## Running the API Server

To run the API server:

```bash
# Activate the virtual environment
source venv/bin/activate

# Navigate to the project directory
cd myproject

# Run the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.
