# Moodle File Retriever API Documentation

This document provides detailed information about the API endpoints for retrieving files from Moodle courses.

## Base URL

The base URL for all API endpoints is:

```
http://localhost:8000
```

You can change this in the Postman collection variables.

## Authentication

### Login to Moodle

**Endpoint:** `/api/moodle-login/`

**Method:** POST

**Description:** Login to Moodle and get session cookies for subsequent requests.

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Login successful",
    "session": {
        "MoodleSession": "session_cookie_value",
        "MOODLEID1_": "another_cookie_value"
    }
}
```

**Status Codes:**
- 200: Success
- 401: Authentication failed

## Course Resources

### Get Course PDFs (POST)

**Endpoint:** `/api/moodle-pdfs/`

**Method:** POST

**Description:** Get PDF files and other downloadable resources from a specific course using authentication.

**Request Body:**
```json
{
    "course_id": "8527",
    "username": "your_username",
    "password": "your_password",
    "url": "https://elearning.univ-bba.dz"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Found 2 PDF files in course 8527",
    "course_name": "Course Name",
    "count": 2,
    "pdfs": [
        {
            "name": "file1.docx",
            "url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
            "resource_name": "Resource Name",
            "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
            "type": "resource_pdf"
        },
        {
            "name": "file2.docx",
            "url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131856",
            "resource_name": "Resource Name 2",
            "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131856",
            "type": "resource_pdf"
        }
    ]
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed

### Get Course PDFs (GET)

**Endpoint:** `/api/moodle-pdfs/{course_id}/`

**Method:** GET

**Description:** Get PDF files and other downloadable resources from a specific course using authentication.

**URL Parameters:**
- `course_id`: The ID of the course

**Query Parameters:**
- `username`: Your Moodle username
- `password`: Your Moodle password
- `url` (optional): The base URL of the Moodle site (default: https://elearning.univ-bba.dz)

**Response:** Same as the POST method.

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed

### Get Course PDFs with Session (POST)

**Endpoint:** `/api/moodle-pdfs/`

**Method:** POST

**Description:** Get PDF files from a specific course using a session from a previous login.

**Request Body:**
```json
{
    "course_id": "8527",
    "session": {
        "MoodleSession": "session_cookie_value",
        "MOODLEID1_": "another_cookie_value"
    },
    "url": "https://elearning.univ-bba.dz"
}
```

**Response:** Same as the regular POST method.

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed

### Get Course Resources (URL-based)

**Endpoint:** `/api/auth-resources/`

**Method:** POST

**Description:** Get resources from a course URL. Set download_file to false to get JSON metadata.

**Request Body:**
```json
{
    "url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
    "username": "your_username",
    "password": "your_password",
    "download_file": false
}
```

**Response:**
```json
{
    "status": "success",
    "course_url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
    "authenticated": true,
    "count": 2,
    "data": [
        {
            "resource_name": "Resource Name",
            "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
            "pdf_url": "https://elearning.univ-bba.dz/pluginfile.php/123456/mod_resource/content/1/file1.docx",
            "pdf_name": "file1.docx"
        },
        {
            "resource_name": "Resource Name 2",
            "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131856",
            "pdf_url": "https://elearning.univ-bba.dz/pluginfile.php/123457/mod_resource/content/1/file2.docx",
            "pdf_name": "file2.docx"
        }
    ]
}
```

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed

### Download Course File (URL-based)

**Endpoint:** `/api/auth-resources/`

**Method:** POST

**Description:** Download a file directly from a course URL. Set download_file to true to get the file content.

**Request Body:**
```json
{
    "url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
    "username": "your_username",
    "password": "your_password",
    "download_file": true
}
```

**Response:** The file content with appropriate headers for download.

**Headers:**
- Content-Type: The MIME type of the file (e.g., application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document)
- Content-Disposition: attachment; filename="filename.ext"

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed
- 404: File not found

## Category Resources

### Get Category Courses

**Endpoint:** `/api/category/{category_id}/courses/`

**Method:** GET

**Description:** Get all courses in a specific category.

**URL Parameters:**
- `category_id`: The ID of the category

**Response:**
```json
{
    "status": "success",
    "message": "Found 5 courses in category 795",
    "count": 5,
    "data": [
        {
            "id": "8527",
            "name": "Course Name 1",
            "url": "https://elearning.univ-bba.dz/course/view.php?id=8527"
        },
        {
            "id": "8528",
            "name": "Course Name 2",
            "url": "https://elearning.univ-bba.dz/course/view.php?id=8528"
        },
        ...
    ]
}
```

**Status Codes:**
- 200: Success
- 404: Category not found

### Get Category Resources

**Endpoint:** `/api/auth-resources/`

**Method:** POST

**Description:** Get resources from a category URL. Set download_file to false to get JSON metadata.

**Request Body:**
```json
{
    "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795",
    "username": "your_username",
    "password": "your_password",
    "download_file": false
}
```

**Response:** Similar to the course resources response, but may include resources from multiple courses.

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed

### Download Category File

**Endpoint:** `/api/auth-resources/`

**Method:** POST

**Description:** Download a file directly from a category URL. Set download_file to true to get the file content.

**Request Body:**
```json
{
    "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795",
    "username": "your_username",
    "password": "your_password",
    "download_file": true
}
```

**Response:** The file content with appropriate headers for download.

**Headers:**
- Content-Type: The MIME type of the file
- Content-Disposition: attachment; filename="filename.ext"

**Status Codes:**
- 200: Success
- 400: Bad request (missing parameters)
- 401: Authentication failed
- 404: File not found

## Moodle Courses

### Get All Courses

**Endpoint:** `/api/moodle-courses/`

**Method:** GET

**Description:** Get all available courses from Moodle.

**Response:**
```json
{
    "status": "success",
    "message": "Found 100 courses",
    "count": 100,
    "data": [
        {
            "id": "8527",
            "name": "Course Name 1",
            "url": "https://elearning.univ-bba.dz/course/view.php?id=8527"
        },
        {
            "id": "8528",
            "name": "Course Name 2",
            "url": "https://elearning.univ-bba.dz/course/view.php?id=8528"
        },
        ...
    ]
}
```

**Status Codes:**
- 200: Success

### Get Departments

**Endpoint:** `/api/departments/`

**Method:** GET

**Description:** Get all departments from Moodle.

**Response:**
```json
{
    "status": "success",
    "message": "Found 20 departments",
    "count": 20,
    "data": [
        {
            "id": "795",
            "name": "Department Name 1",
            "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795"
        },
        {
            "id": "796",
            "name": "Department Name 2",
            "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=796"
        },
        ...
    ]
}
```

**Status Codes:**
- 200: Success

## Error Handling

All endpoints return appropriate HTTP status codes and error messages in case of failure.

Example error response:
```json
{
    "status": "error",
    "message": "Authentication failed. Please check your credentials."
}
```

## Rate Limiting

To prevent abuse, the API may implement rate limiting. If you exceed the rate limit, you will receive a 429 Too Many Requests response.

## Notes

- The API requires valid Moodle credentials to authenticate and retrieve files.
- Files are downloaded with their original names when possible.
- The API can handle both course IDs and course URLs.
- For category URLs, the API will retrieve resources from all courses in the category.
- The `download_file` parameter in the `/api/auth-resources/` endpoint determines whether to return JSON metadata or the actual file content.
- When downloading files, the API will set appropriate Content-Type and Content-Disposition headers.
