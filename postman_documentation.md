# Moodle Resources API Documentation

This document provides information about the API endpoints available for retrieving resources from the Moodle e-learning platform.

## Base URL

```
http://localhost:8008/api/
```

## Authentication

Most endpoints require authentication with Moodle credentials. These should be provided in the request body.

## Endpoints

### 1. Authenticated Resources

Retrieves resources from a course or category with authentication and optionally downloads files.

**Endpoint:** `POST /api/auth-resources/`

**Request Body:**

```json
{
  "url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
  "username": "your_username",
  "password": "your_password",
  "download_file": false
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| url | string | Yes | URL of the course or category page |
| username | string | Yes | Moodle username |
| password | string | Yes | Moodle password |
| download_file | boolean | No | Whether to download the first file found (default: false) |

**Response (JSON - when download_file is false):**

```json
{
  "status": "success",
  "course_url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
  "authenticated": true,
  "count": 2,
  "data": [
    {
      "resource_name": "Techniques d'Analyse Physico-chimique II Fichier",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
      "pdf_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
      "pdf_name": "Techniques d'Analyse Physico-chimique II.docx"
    },
    {
      "resource_name": "Techniques d'Analyse Physico-chimique II TD2 Fichier",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131856",
      "pdf_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131856",
      "pdf_name": "TD Corrigé.docx"
    }
  ]
}
```

**Response (File - when download_file is true):**

When `download_file` is set to `true`, the API will return the first file found as a downloadable file with appropriate content type and filename.

### 2. Category Courses

Retrieves courses from a specific category.

**Endpoint:** `POST /api/auth-resources/`

**Request Body:**

```json
{
  "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795",
  "username": "your_username",
  "password": "your_password",
  "download_file": false
}
```

**Response:**

```json
{
  "status": "success",
  "course_url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795",
  "authenticated": true,
  "count": 5,
  "data": [
    {
      "id": "8527",
      "name": "Techniques d'Analyse Physico-chimique II",
      "url": "https://elearning.univ-bba.dz/course/view.php?id=8527"
    },
    {
      "id": "8528",
      "name": "Chimie Organique II",
      "url": "https://elearning.univ-bba.dz/course/view.php?id=8528"
    }
    // More courses...
  ]
}
```

### 3. Course List

Retrieves all courses from the e-learning platform.

**Endpoint:** `GET /api/courses/`

**Response:**

```json
{
  "status": "success",
  "count": 150,
  "data": [
    {
      "id": "8527",
      "name": "Techniques d'Analyse Physico-chimique II",
      "url": "https://elearning.univ-bba.dz/course/view.php?id=8527"
    },
    // More courses...
  ]
}
```

### 4. Department List

Retrieves all departments from the e-learning platform.

**Endpoint:** `GET /api/departments/`

**Response:**

```json
{
  "status": "success",
  "count": 15,
  "data": [
    {
      "id": "795",
      "name": "Chemistry Department",
      "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795"
    },
    // More departments...
  ]
}
```

### 5. Course Resources

Retrieves resources from a specific course without authentication.

**Endpoint:** `GET /api/resources/{course_id}/`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| course_id | string | Yes | ID of the course |

**Response:**

```json
{
  "status": "success",
  "course_id": "8527",
  "course_url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
  "count": 2,
  "data": [
    {
      "resource_name": "Techniques d'Analyse Physico-chimique II Fichier",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
      "pdf_url": "",
      "pdf_name": ""
    },
    // More resources...
  ]
}
```

**Alternative Endpoint:** `POST /api/resources/`

**Request Body:**

```json
{
  "url": "https://elearning.univ-bba.dz/course/view.php?id=8527"
}
```

### 6. Moodle Login

Tests authentication with Moodle credentials.

**Endpoint:** `POST /api/login/`

**Request Body:**

```json
{
  "username": "your_username",
  "password": "your_password",
  "url": "https://elearning.univ-bba.dz"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Login successful",
  "session": {
    "MoodleSession": "abc123def456",
    // Other cookies...
  }
}
```

### 7. Course PDFs

Retrieves PDF files from a specific course with authentication.

**Endpoint:** `POST /api/course-pdfs/`

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
  "message": "Found 2 PDF files in course",
  "course_name": "Techniques d'Analyse Physico-chimique II",
  "count": 2,
  "pdfs": [
    {
      "resource_name": "Techniques d'Analyse Physico-chimique II Fichier",
      "resource_url": "https://elearning.univ-bba.dz/mod/resource/view.php?id=131855",
      "url": "https://elearning.univ-bba.dz/pluginfile.php/123456/mod_resource/content/1/document.pdf",
      "name": "Techniques d'Analyse Physico-chimique II.pdf"
    },
    // More PDFs...
  ]
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "status": "error",
  "message": "Error message describing what went wrong"
}
```

Common error status codes:
- 400: Bad Request (missing required parameters)
- 401: Unauthorized (invalid credentials)
- 404: Not Found (resource not found)
- 500: Internal Server Error (server-side error)
- 504: Gateway Timeout (request timed out)

## Examples

### Example 1: Get resources from a course

```bash
curl -X POST \
  http://localhost:8008/api/auth-resources/ \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
    "username": "your_username",
    "password": "your_password",
    "download_file": false
  }'
```

### Example 2: Download a file from a course

```bash
curl -X POST \
  http://localhost:8008/api/auth-resources/ \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://elearning.univ-bba.dz/course/view.php?id=8527",
    "username": "your_username",
    "password": "your_password",
    "download_file": true
  }' \
  -o downloaded_file.pdf
```

### Example 3: Get courses from a category

```bash
curl -X POST \
  http://localhost:8008/api/auth-resources/ \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://elearning.univ-bba.dz/course/index.php?categoryid=795",
    "username": "your_username",
    "password": "your_password",
    "download_file": false
  }'
```
