const { Moodle } = require('moodle-scrape');
// Add node-fetch for Node.js environment
const fetch = require('node-fetch');
global.fetch = fetch;

/**
 * Login to Moodle and retrieve courses
 * @param {string} username - The username for Moodle
 * @param {string} password - The password for Moodle
 * @param {string} url - The Moodle URL (default: https://elearning.univ-bba.dz)
 * @returns {Promise<Object>} - Object containing login status and courses
 */
async function loginAndGetCourses(username, password, url = 'https://elearning.univ-bba.dz') {
    try {
        // Ensure URL has proper format
        if (!url.startsWith('http')) {
            url = 'https://' + url;
        }

        console.log(`Connecting to Moodle at: ${url}`);

        // Create a new Moodle instance
        const moodle = new Moodle(fetch, url);

        // Attempt to login
        const loginSuccess = await moodle.login(username, password);

        if (!loginSuccess) {
            return {
                success: false,
                message: 'Login failed. Please check your credentials.',
                courses: []
            };
        }

        // Return login status and courses
        return {
            success: true,
            message: 'Login successful',
            courses: moodle.courses
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
            courses: []
        };
    }
}

/**
 * Get course details including sections and modules
 * @param {string} username - The username for Moodle
 * @param {string} password - The password for Moodle
 * @param {string} courseId - The course ID to retrieve
 * @param {string} url - The Moodle URL (default: https://elearning.univ-bba.dz)
 * @returns {Promise<Object>} - Object containing course details
 */
async function getCourseDetails(username, password, courseId, url = 'https://elearning.univ-bba.dz') {
    try {
        // Ensure URL has proper format
        if (!url.startsWith('http')) {
            url = 'https://' + url;
        }

        console.log(`Connecting to Moodle at: ${url}`);

        // Create a new Moodle instance
        const moodle = new Moodle(fetch, url);

        // Attempt to login
        const loginSuccess = await moodle.login(username, password);

        if (!loginSuccess) {
            return {
                success: false,
                message: 'Login failed. Please check your credentials.',
                course: null
            };
        }

        // Find the course by ID
        const course = moodle.courses.find(c => c.id === courseId);

        if (!course) {
            return {
                success: false,
                message: `Course with ID ${courseId} not found`,
                course: null
            };
        }

        // Get course details
        const courseDetails = await moodle.getCourse(course);

        return {
            success: true,
            message: 'Course details retrieved successfully',
            course: courseDetails
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`,
            course: null
        };
    }
}

// Export the functions
module.exports = {
    loginAndGetCourses,
    getCourseDetails
};
