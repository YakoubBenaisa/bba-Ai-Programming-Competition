# Moodle Login

A simple Node.js implementation for authenticating with Moodle LMS.

## Features

- Login to Moodle with username and password
- Simple API for integration into other applications
- Command-line interface for quick testing

## Installation

1. Make sure you have Node.js installed (version 14 or higher recommended)

2. Install the dependencies:
   ```bash
   npm install undici
   ```

## Usage

### As a module

```javascript
const { loginToMoodle } = require('./moodle_login');

async function example() {
    const result = await loginToMoodle('username', 'password');
    console.log('Login successful:', result.success);
    console.log('Message:', result.message);
}

example();
```

### Using the CLI

```bash
node moodle_login_cli.js <username> <password> [url]
```

Example:
```bash
node moodle_login_cli.js yakoub.benaissa aLnmftOM
```

## API Reference

### `loginToMoodle(username, password, url)`

Logs in to Moodle with the provided credentials.

- **Parameters**:
  - `username` (string): The Moodle username
  - `password` (string): The Moodle password
  - `url` (string, optional): The Moodle URL (default: 'https://elearning.univ-bba.dz')

- **Returns**: Promise resolving to an object with:
  - `success` (boolean): Whether the login was successful
  - `message` (string): Status message

## Security Note

This implementation requires your Moodle credentials. Make sure to:
- Never hardcode credentials in your code
- Use environment variables or secure credential storage
- Be careful when sharing your code to avoid exposing credentials

## License

MIT
