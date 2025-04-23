const { fetch } = require('undici');

async function loginToMoodle(username, password) {
    try {
        const baseUrl = 'https://elearning.univ-bba.dz';
        const loginUrl = `${baseUrl}/login/index.php`;
        
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
        console.log('Response URL:', responseUrl);
        
        if (loginSuccess) {
            // Fetch the dashboard to get courses
            console.log('Fetching dashboard...');
            const dashboardResponse = await fetch(`${baseUrl}/my/`, {
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
            if (courseLinks.length > 0) {
                console.log('First few courses:');
                courseLinks.slice(0, 3).forEach(course => {
                    console.log(`- ${course.name} (ID: ${course.id})`);
                });
            }
            
            return {
                success: true,
                cookies: cookieJar.join('; '),
                courses: courseLinks
            };
        }
        
        return {
            success: false,
            message: 'Login failed. Please check your credentials.'
        };
        
    } catch (error) {
        console.error('Login failed:', error.message);
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
    if (result.success) {
        console.log(`Found ${result.courses.length} courses`);
    } else {
        console.log('Error:', result.message);
    }
}

testLogin();
