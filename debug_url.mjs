import { URL } from 'url';

try {
    const url = new URL('https://elearning.univ-bba.dz');
    console.log('URL is valid:', url.toString());
    console.log('Protocol:', url.protocol);
    console.log('Host:', url.host);
    console.log('Pathname:', url.pathname);
} catch (error) {
    console.error('URL is invalid:', error.message);
}

// Try with different formats
try {
    const url2 = new URL('http://elearning.univ-bba.dz');
    console.log('\nURL2 is valid:', url2.toString());
} catch (error) {
    console.error('\nURL2 is invalid:', error.message);
}

try {
    const url3 = new URL('elearning.univ-bba.dz');
    console.log('\nURL3 is valid:', url3.toString());
} catch (error) {
    console.error('\nURL3 is invalid:', error.message);
}
