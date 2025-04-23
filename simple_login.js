const { fetch } = require('undici');

/**
 * Login to Moodle
 * @param {string} username - The username for Moodle
 * @param {string} password - The password for Moodle
 * @param {string} url - The Moodle URL (default: https://elearning.univ-bba.dz)
 * @returns {Promise<Object>} - Object containing login status
 */
async function loginToMoodle(username, password, url = 'https://elearning.univ-bba.dz') {
    try {
        const loginUrl = `${url}/login/index.php`;
        
        console.log(`Fetching login page from ${loginUrl}...`);
        
        // Fetch the login page to get the login token
        const loginPageResponse = await fetch(loginUrl);
        
        if (!loginPageResponse.ok) {
            throw new Error(`HTTP error! Status: ${loginPageResponse.status}`);
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
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString(),
            redirect: 'follow'
        });
        
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
        
        return {
            success: loginSuccess,
            message: loginSuccess ? 'Login successful' : 'Login failed. Please check your credentials.'
        };
    } catch (error) {
        return {
            success: false,
            message: `Error: ${error.message}`
        };
    }
}

// Test the login function
async function testLogin() {
    const result = await loginToMoodle('yakoub.benaissa', 'aLnmftOM');
    console.log('Login result:', result.success);
    console.log('Message:', result.message);
}

testLogin();
