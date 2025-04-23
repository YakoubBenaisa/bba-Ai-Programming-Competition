const { fetch } = require('undici');

async function testMoodleFetch() {
    try {
        const url = 'https://elearning.univ-bba.dz';
        
        console.log(`Fetching ${url}...`);
        
        // Fetch the main page
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const html = await response.text();
        
        console.log('Response status:', response.status);
        console.log('Response size:', html.length);
        console.log('First 200 characters:', html.substring(0, 200));
        
        // Check if it's a Moodle site
        if (html.includes('Moodle')) {
            console.log('This is a Moodle site!');
        } else {
            console.log('This might not be a Moodle site.');
        }
        
    } catch (error) {
        console.error('Fetch failed:', error.message);
    }
}

testMoodleFetch();
