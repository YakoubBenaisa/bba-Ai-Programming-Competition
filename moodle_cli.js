#!/usr/bin/env node
const { loginAndGetCourses, getCourseDetails } = require('./moodle_scraper');

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

async function main() {
    if (!command) {
        console.log('Usage:');
        console.log('  node moodle_cli.js login <username> <password> [url]');
        console.log('  node moodle_cli.js course <username> <password> <courseId> [url]');
        return;
    }

    try {
        if (command === 'login') {
            const username = args[1];
            const password = args[2];
            const url = args[3] || 'https://elearning.univ-bba.dz';

            if (!username || !password) {
                console.log('Error: Username and password are required');
                return;
            }

            console.log(`Logging in as ${username}...`);
            const result = await loginAndGetCourses(username, password, url);
            
            console.log('Login successful:', result.success);
            console.log('Message:', result.message);
            console.log('Courses found:', result.courses.length);
            
            if (result.courses.length > 0) {
                console.log('\nCourses:');
                result.courses.forEach((course, index) => {
                    console.log(`${index + 1}. ${course.name} (ID: ${course.id})`);
                });
            }
        } else if (command === 'course') {
            const username = args[1];
            const password = args[2];
            const courseId = args[3];
            const url = args[4] || 'https://elearning.univ-bba.dz';

            if (!username || !password || !courseId) {
                console.log('Error: Username, password, and courseId are required');
                return;
            }

            console.log(`Getting details for course ${courseId}...`);
            const result = await getCourseDetails(username, password, courseId, url);
            
            console.log('Course details retrieval successful:', result.success);
            console.log('Message:', result.message);
            
            if (result.success && result.course) {
                console.log('\nCourse Details:');
                console.log(`Name: ${result.course.name}`);
                console.log(`ID: ${result.course.id}`);
                console.log(`Sections: ${result.course.sections.length}`);
                
                if (result.course.sections.length > 0) {
                    console.log('\nSections:');
                    result.course.sections.forEach((section, index) => {
                        console.log(`${index + 1}. ${section.name}`);
                        if (section.modules.length > 0) {
                            console.log('   Modules:');
                            section.modules.forEach((module, moduleIndex) => {
                                console.log(`   ${moduleIndex + 1}. ${module.name} (${module.modname})`);
                            });
                        }
                    });
                }
            }
        } else {
            console.log(`Unknown command: ${command}`);
            console.log('Available commands: login, course');
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
