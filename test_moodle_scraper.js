const { loginAndGetCourses, getCourseDetails } = require('./final_moodle_scraper');

async function testMoodleScrape() {
    try {
        // Test login and get courses
        console.log('Testing login and course retrieval...');
        const result = await loginAndGetCourses('yakoub.benaissa', 'aLnmftOM');

        console.log('Login successful:', result.success);
        console.log('Message:', result.message);
        console.log('Courses found:', result.courses.length);

        if (result.courses.length > 0) {
            console.log('First course:', result.courses[0]);

            // Test getting course details for the first course
            console.log('\nTesting course details retrieval...');
            const courseId = result.courses[0].id;
            const courseDetails = await getCourseDetails(result.cookies, courseId);

            console.log('Course details retrieval successful:', courseDetails.success);
            console.log('Message:', courseDetails.message);

            if (courseDetails.success) {
                console.log('Course name:', courseDetails.course.name);
                console.log('Sections count:', courseDetails.course.sections.length);

                if (courseDetails.course.sections.length > 0) {
                    const firstSection = courseDetails.course.sections[0];
                    console.log('First section name:', firstSection.name);
                    console.log('Resources count:', firstSection.resources.length);

                    if (firstSection.resources.length > 0) {
                        console.log('First resource:', firstSection.resources[0]);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Test failed:', error.message);
    }
}

// Run the test
testMoodleScrape();
