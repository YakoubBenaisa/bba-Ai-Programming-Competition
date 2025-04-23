#!/usr/bin/env node
const { loginToMoodle } = require('./moodle_login');

// Parse command line arguments
const args = process.argv.slice(2);
const username = args[0];
const password = args[1];
const url = args[2] || 'https://elearning.univ-bba.dz';

if (!username || !password) {
    console.log('Usage: node moodle_login_cli.js <username> <password> [url]');
    process.exit(1);
}

async function main() {
    try {
        console.log(`Attempting to login to ${url} as ${username}...`);
        
        const result = await loginToMoodle(username, password, url);
        
        console.log('Login result:', result.success);
        console.log('Message:', result.message);
        
        process.exit(result.success ? 0 : 1);
    } catch (error) {
        console.error('Error:', error.message);
        process.exit(1);
    }
}

main();
