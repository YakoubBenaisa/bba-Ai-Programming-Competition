import requests
from bs4 import BeautifulSoup
import os
import sys

# ——— CONFIGURATION ———
USERNAME    = 'yakoub.benaissa'
PASSWORD    = 'aLnmftOM'
MOODLE_BASE = 'https://elearning.univ-bba.dz'
LOGIN_URL   = MOODLE_BASE + '/login/index.php'
COURSE_URL  = MOODLE_BASE + '/course/view.php?id=5873'

LOCAL_API   = 'http://127.0.0.1:8005/api/auth-resources/'


def debug(msg):
    """Simple debug printer."""
    print(f'[DEBUG] {msg}', file=sys.stderr)


def login(session):
    """Log in to Moodle and return True on success."""
    # 1) GET login page, scrape the logintoken
    resp = session.get(LOGIN_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    token_input = soup.find('input', attrs={'name': 'logintoken'})
    if not token_input or not token_input.get('value'):
        debug("Could not find login token on the page")
        return False
    token = token_input['value']
    debug(f"Found logintoken: {token}")

    # 2) POST credentials + token
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'logintoken': token
    }
    post = session.post(LOGIN_URL, data=data)
    post.raise_for_status()

    # 3) Check whether login succeeded by seeing if we're redirected away from login page
    if post.url == LOGIN_URL:
        # still on login page → login probably failed
        debug("Still on login page after POST; login failed")
        return False

    debug("Login appears successful")
    return True


def find_pdfs(session):
    """Return a list of absolute URLs to PDF files on the course page."""
    resp = session.get(COURSE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    pdfs = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.lower().endswith('.pdf'):
            # make absolute
            if href.startswith('/'):
                href = MOODLE_BASE + href
            pdfs.append(href)
    return list(set(pdfs))


def download_pdfs(session, urls, out_dir='pdfs'):
    """Download each PDF URL into out_dir/"""
    if not urls:
        print("No PDF links found.")
        return
    os.makedirs(out_dir, exist_ok=True)
    for url in urls:
        debug(f"Downloading {url}")
        r = session.get(url)
        r.raise_for_status()
        name = url.split('/')[-1].split('?')[0]
        path = os.path.join(out_dir, name)
        with open(path, 'wb') as f:
            f.write(r.content)
        print(f"Saved {path}")


def call_local_api():
    """Send your credentials & course URL to local API and save returned file."""
    payload = {
        "url":    COURSE_URL,
        "username": USERNAME,
        "password": PASSWORD,
        "download_pdf": True
    }
    debug(f"Posting to local API {LOCAL_API} with payload {payload}")
    r = requests.post(LOCAL_API, json=payload)
    
    if r.status_code != 200:
        print(f"Local API returned status {r.status_code}")
        print(r.text)
        return
        
    # Check the content type
    content_type = r.headers.get('Content-Type', '')
    debug(f"Response content type: {content_type}")
    
    # Check if it's a file download
    if 'application/json' in content_type:
        # It's JSON, print the response
        print("API returned JSON response:")
        print(r.json())
    else:
        # It's a file download, save it
        # Try to get the filename from Content-Disposition
        filename = 'downloaded_file'
        content_disposition = r.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            import re
            filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
            if filename_match:
                filename = filename_match.group(1)
        
        # Save the file
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"File saved as {filename}")


def main():
    session = requests.Session()
    if not login(session):
        print("Login failed; please check your credentials or token parsing.", file=sys.stderr)
        sys.exit(1)

    # Part A: direct scrape & download
    pdf_urls = find_pdfs(session)
    print(f"Found {len(pdf_urls)} PDF(s) on course page:")
    for u in pdf_urls:
        print("  -", u)
    download_pdfs(session, pdf_urls)

    # Part B: hit your local API
    call_local_api()


if __name__ == '__main__':
    main()
