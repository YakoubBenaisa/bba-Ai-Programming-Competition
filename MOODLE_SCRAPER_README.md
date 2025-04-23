# Moodle Scraper

A Node.js implementation for scraping course information from Moodle using the moodle-scrape library.

## Features

- Login to Moodle
- Retrieve course list
- Get detailed course information including sections and modules

## Installation

1. Make sure you have Node.js installed (version 14 or higher recommended)

2. Install the dependencies:
   ```bash
   npm install
   ```

## Usage

### As a module

```javascript
const { loginAndGetCourses, getCourseDetails } = require('./moodle_scraper');

// Login and get courses
async function example() {
    const result = await loginAndGetCourses('username', 'password');
    console.log('Login successful:', result.success);
    console.log('Courses found:', result.courses.length);
    
    // Get details for a specific course
    if (result.courses.length > 0) {
        const courseId = result.courses[0].id;
        const courseDetails = await getCourseDetails('username', 'password', courseId);
        console.log('Course details:', courseDetails.course);
    }
}
```

### Using the CLI

The package includes a command-line interface for easy usage:

1. Login and list courses:
   ```bash
   node moodle_cli.js login <username> <password> [url]
   ```

2. Get course details:
   ```bash
   node moodle_cli.js course <username> <password> <courseId> [url]
   ```

### Running the test script

```bash
npm test
```
or
```bash
node test_moodle_scraper.js
```

## API Reference

### `loginAndGetCourses(username, password, url)`

Logs in to Moodle and retrieves the list of courses.

- **Parameters**:
  - `username` (string): The Moodle username
  - `password` (string): The Moodle password
  - `url` (string, optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')

- **Returns**: Promise resolving to an object with:
  - `success` (boolean): Whether the login was successful
  - `message` (string): Status message
  - `courses` (array): List of courses

### `getCourseDetails(username, password, courseId, url)`

Gets detailed information about a specific course.

- **Parameters**:
  - `username` (string): The Moodle username
  - `password` (string): The Moodle password
  - `courseId` (string): The ID of the course to retrieve
  - `url` (string, optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')

- **Returns**: Promise resolving to an object with:
  - `success` (boolean): Whether the operation was successful
  - `message` (string): Status message
  - `course` (object): Course details including sections and modules

## Security Note

This implementation requires your Moodle credentials. Make sure to:
- Never hardcode credentials in your code
- Use environment variables or secure credential storage
- Be careful when sharing your code to avoid exposing credentials

## License

MIT
