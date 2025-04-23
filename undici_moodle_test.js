const { Moodle } = require('moodle-scrape');
const { fetch } = require('undici');

async function testMoodleScrape() {
    try {
        const url = 'https://elearning.univ-bba.dz';
        const username = 'yakoub.benaissa';
        const password = 'aLnmftOM';

        console.log(`Connecting to Moodle at: ${url}`);
        
        // Create a new Moodle instance
        const moodle = new Moodle(fetch, url);

        // Test login
        console.time('Login time');
        const loginSuccess = await moodle.login(username, password, {
            refresh: false,
            loginFormPath: 'login/index.php',
        });
        console.timeEnd('Login time');
        
        console.log('Login successful:', loginSuccess);

        if (!loginSuccess) {
            return console.log('Login failed. Please check your credentials.');
        }

        // Test getting courses
        console.time('Get info time');
        await moodle.refresh(undefined, { navCourses: false });
        console.timeEnd('Get info time');
        
        console.log('User:', moodle.user);
        console.log('Courses found:', moodle.courses.length);
        
        if (moodle.courses.length > 0) {
            console.log('First course:', moodle.courses[0]);
        }
        
        console.log('Tasks found:', moodle.tasks.length);
        
        if (moodle.tasks.length > 0) {
            console.log('First task:', moodle.tasks[0]);
        }

    } catch (error) {
        console.error('Test failed:', error.message);
    }
}

testMoodleScrape();
