const { Moodle } = require('moodle-scrape');
const { fetch } = require('undici');

async function testMoodleScrape() {
    try {
        // Create a new Moodle instance with fetch and URL
        const moodle = new Moodle(fetch, 'https://elearning.univ-bba.dz');

        // Test login
        const loginSuccess = await moodle.login('yakoub.benaissa', 'aLnmftOM');
        console.log('Login successful:', loginSuccess);

        // Test getting courses
        console.log('Courses found:', moodle.courses.length);
        if (moodle.courses.length > 0) {
            console.log('First course:', moodle.courses[0]);
        }

    } catch (error) {
        console.error('Test failed:', error.message);
    }
}

testMoodleScrape();
