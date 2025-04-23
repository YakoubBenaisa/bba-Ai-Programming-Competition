const { fetch } = require('undici');

/**
 * Login to Moodle and retrieve courses
 * @param {string} username - The username for Moodle
 * @param {string} password - The password for Moodle
 * @param {string} url - The Moodle URL (default: https://elearning.univ-bba.dz)
 * @returns {Promise<Object>} - Object containing login status and courses
 */
async function loginAndGetCourses(username, password, url = 'https://elearning.univ-bba.dz') {
    try {
        const loginUrl = `${url}/login/index.php`;
        
        console.log(`Fetching login page from ${loginUrl}...`);
        
        // Create a cookie jar
        const cookieJar = [];
        
        // Fetch the login page to get the login token
        const loginPageResponse = await fetch(loginUrl);
        
        if (!loginPageResponse.ok) {
            throw new Error(`HTTP error! Status: ${loginPageResponse.status}`);
        }
        
        // Store cookies
        const cookies = loginPageResponse.headers.get('set-cookie');
        if (cookies) {
            cookieJar.push(...cookies.split(',').map(cookie => cookie.split(';')[0]));
        }
        
        const loginPageHtml = await loginPageResponse.text();
        
        // Extract login token
        const tokenMatch = loginPageHtml.match(/name="logintoken" value="([^"]+)"/);
        if (!tokenMatch) {
            throw new Error('Login token not found');
        }
        
        const loginToken = tokenMatch[1];
        console.log('Login token:', loginToken);
        
        // Prepare login form data
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('logintoken', loginToken);
        formData.append('anchor', '');
        
        // Submit login form
        console.log('Submitting login form...');
        const loginResponse = await fetch(loginUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookieJar.join('; ')
            },
            body: formData.toString(),
            redirect: 'follow'
        });
        
        // Store cookies from login response
        const loginCookies = loginResponse.headers.get('set-cookie');
        if (loginCookies) {
            cookieJar.push(...loginCookies.split(',').map(cookie => cookie.split(';')[0]));
        }
        
        if (!loginResponse.ok) {
            throw new Error(`HTTP error! Status: ${loginResponse.status}`);
        }
        
        const responseUrl = loginResponse.url;
        const responseHtml = await loginResponse.text();
        
        // Check if login was successful
        const loginSuccess = !responseHtml.includes('Invalid login') && 
                            !responseHtml.includes('loginerrors') &&
                            responseUrl !== loginUrl;
        
        console.log('Login successful:', loginSuccess);
        
        if (!loginSuccess) {
            return {
                success: false,
                message: 'Login failed. Please check your credentials.',
                courses: []
            };
        }
        
        // Fetch the dashboard to get courses
        console.log('Fetching dashboard...');
        const dashboardResponse = await fetch(`${url}/my/`, {
            headers: {
                'Cookie': cookieJar.join('; ')
            }
        });
        
        if (!dashboardResponse.ok) {
            throw new Error(`HTTP error! Status: ${dashboardResponse.status}`);
        }
        
        const dashboardHtml = await dashboardResponse.text();
        
        // Extract course links
        const courseLinks = [];
        const courseRegex = /<a[^>]*href="[^"]*\/course\/view\.php\?id=(\d+)"[^>]*>([^<]+)<\/a>/g;
        let match;
        
        while ((match = courseRegex.exec(dashboardHtml)) !== null) {
            courseLinks.push({
                id: match[1],
                name: match[2].trim()
            });
        }
        
        console.log('Courses found:', courseLinks.length);
        
        return {
            success: true,
            message: 'Login successful',
            courses: courseLinks,
            cookies: cookieJar.join('; ')
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
 * Get course details
 * @param {string} cookies - The cookies from a successful login
 * @param {string} courseId - The course ID to retrieve
 * @param {string} url - The Moodle URL (default: https://elearning.univ-bba.dz)
 * @returns {Promise<Object>} - Object containing course details
 */
async function getCourseDetails(cookies, courseId, url = 'https://elearning.univ-bba.dz') {
    try {
        const courseUrl = `${url}/course/view.php?id=${courseId}`;
        
        console.log(`Fetching course details from ${courseUrl}...`);
        
        // Fetch the course page
        const courseResponse = await fetch(courseUrl, {
            headers: {
                'Cookie': cookies
            }
        });
        
        if (!courseResponse.ok) {
            throw new Error(`HTTP error! Status: ${courseResponse.status}`);
        }
        
        const courseHtml = await courseResponse.text();
        
        // Extract course name
        const courseNameMatch = courseHtml.match(/<h1[^>]*>([^<]+)<\/h1>/);
        const courseName = courseNameMatch ? courseNameMatch[1].trim() : `Course ${courseId}`;
        
        // Extract sections
        const sections = [];
        const sectionRegex = /<li[^>]*id="section-(\d+)"[^>]*>[\s\S]*?<div[^>]*class="content"[^>]*>([\s\S]*?)<\/div>[\s\S]*?<\/li>/g;
        let sectionMatch;
        
        while ((sectionMatch = sectionRegex.exec(courseHtml)) !== null) {
            const sectionId = sectionMatch[1];
            const sectionContent = sectionMatch[2];
            
            // Extract section name
            const sectionNameMatch = sectionContent.match(/<h3[^>]*>([^<]+)<\/h3>/);
            const sectionName = sectionNameMatch ? sectionNameMatch[1].trim() : `Section ${sectionId}`;
            
            // Extract resources
            const resources = [];
            const resourceRegex = /<a[^>]*href="([^"]*\/mod\/resource\/view\.php\?id=\d+)"[^>]*>([^<]+)<\/a>/g;
            let resourceMatch;
            
            while ((resourceMatch = resourceRegex.exec(sectionContent)) !== null) {
                resources.push({
                    url: resourceMatch[1],
                    name: resourceMatch[2].trim()
                });
            }
            
            sections.push({
                id: sectionId,
                name: sectionName,
                resources: resources
            });
        }
        
        return {
            success: true,
            message: 'Course details retrieved successfully',
            course: {
                id: courseId,
                name: courseName,
                sections: sections
            }
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
