# Moodle API Postman Collection Guide

This guide explains how to use the Postman collection for testing and interacting with the Moodle API.

## Getting Started

1. **Install Postman**: Download and install Postman from [postman.com](https://www.postman.com/downloads/).

2. **Import the Collection**:
   - Open Postman
   - Click on "Import" in the top left corner
   - Select the `moodle_api_postman_collection.json` file
   - Click "Import"

3. **Set the Base URL**:
   - The collection uses a variable `{{base_url}}` for the base URL
   - By default, it's set to `http://localhost:8001`
   - You can change this in the collection's variables if your server is running on a different host or port

## Collection Structure

The collection is organized into the following folders:

1. **Authentication**: Endpoints for logging in to Moodle
2. **Courses**: Endpoints for retrieving course information
3. **Departments**: Endpoints for retrieving department information
4. **Resources**: Endpoints for retrieving course resources
5. **PDFs**: Endpoints for retrieving PDF files from courses
6. **Links**: Endpoints for extracting links

## Authentication Flow

To use the authenticated endpoints, you need to:

1. Call the **Moodle Login** endpoint first
2. Copy the session cookies from the response
3. Use these cookies in subsequent requests that require authentication

### Example Authentication Flow:

1. Send a request to `POST {{base_url}}/api/moodle-login/` with your credentials
2. From the response, copy the `session` object
3. Use this session object in the "Get Course PDFs with Session (POST)" request

## Key Endpoints

### 1. Moodle Login

- **Endpoint**: `POST {{base_url}}/api/moodle-login/`
- **Description**: Authenticates with Moodle and returns session cookies
- **Request Body**:
  ```json
  {
      "username": "your_username",
      "password": "your_password",
      "url": "https://elearning.univ-bba.dz"
  }
  ```
- **Response**: Session cookies for use in subsequent requests

### 2. Get Course PDFs

#### Using Credentials (POST)

- **Endpoint**: `POST {{base_url}}/api/moodle-pdfs/`
- **Description**: Retrieves PDF files from a course using credentials
- **Request Body**:
  ```json
  {
      "course_id": "1280",
      "username": "your_username",
      "password": "your_password",
      "url": "https://elearning.univ-bba.dz"
  }
  ```

#### Using Credentials (GET)

- **Endpoint**: `GET {{base_url}}/api/moodle-pdfs/1280/?username=your_username&password=your_password`
- **Description**: Retrieves PDF files from a course using credentials as query parameters

#### Using Session (POST)

- **Endpoint**: `POST {{base_url}}/api/moodle-pdfs/`
- **Description**: Retrieves PDF files from a course using a session from a previous login
- **Request Body**:
  ```json
  {
      "course_id": "1280",
      "session": {
          "MoodleSession": "session_cookie_value",
          "MOODLEID1_": "another_cookie_value"
      },
      "url": "https://elearning.univ-bba.dz"
  }
  ```

## Tips for Using the Collection

1. **Environment Variables**: You can create an environment in Postman to store variables like `base_url`, `username`, and `password` for easier testing.

2. **Chaining Requests**: You can use Postman's Tests tab to automatically extract the session from the login response and set it as a variable for use in subsequent requests.

3. **Saving Responses**: Postman allows you to save responses for future reference. This can be useful for comparing results between different API calls.

4. **Request History**: Postman keeps a history of your requests, making it easy to go back to previous calls without having to recreate them.

## Troubleshooting

- If you get a "Connection refused" error, make sure your server is running and the base URL is correct.
- If you get authentication errors, check that your username and password are correct.
- If you're not getting any PDFs in the response, try different course IDs as not all courses may have PDF resources.

## Additional Resources

- [Postman Documentation](https://learning.postman.com/docs/getting-started/introduction/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Moodle API Documentation](https://docs.moodle.org/dev/Web_service_API_functions)
