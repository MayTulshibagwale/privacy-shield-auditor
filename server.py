# ======================================================================
#  Enterprise Data Privacy & Tracker Compliance Console -- Backend API
# ======================================================================
import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}) # Allows your browser extension/website to talk to this script safely

# Configuration settings
KEYWORDS = ["privacy", "policy", "cookie", "terms"]
LINKS_LOG_FILE = "privacy_links_log.csv"
COOKIES_LOG_FILE = "tracking_cookies_log.csv"

# Common URL paths where privacy policies hide on JavaScript-heavy sites like Instagram.
# We try these as a fallback when the HTML scan finds nothing.
COMMON_PRIVACY_PATHS = [
    "/privacy",
    "/privacy-policy",
    "/legal/privacy",
    "/legal",
    "/terms",
    "/cookie-policy",
    "/about/privacy",
    "/policies/privacy",
    "/en/privacy",
]

# Standard browser fake identity card so websites don't block us
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ----------------------------------------------------------------------
# HELPER FUNCTIONS (The modular puzzle pieces)
# ----------------------------------------------------------------------

def normalize_url(raw_url):
    """Adds https:// to the front of a website text string if it's missing."""
    cleaned_url = raw_url.strip()
    if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
        cleaned_url = "https://" + cleaned_url
    return cleaned_url


def find_compliance_links(all_links):
    """Loops through all links and grabs the ones matching our privacy keywords."""
    matched_links = []
    for link in all_links:
        link_text = link.get_text().lower().strip()
        link_url = (link.get("href") or "").lower().strip()
        
        # Combine visible text and hidden link into one searchable sentence
        searchable_text = link_text + " " + link_url

        # Check if any of our keywords sit inside that text sentence
        for keyword in KEYWORDS:
            if keyword in searchable_text:
                matched_links.append({
                    "keyword": keyword,
                    "text": link_text,
                    "url": link_url
                })
                break # Stop checking other keywords for this link to prevent duplicates
    return matched_links


def check_common_privacy_urls(target_url):
    """
    Fallback for JavaScript-heavy sites like Instagram that load their
    footer links dynamically. If the HTML scan found nothing, we try
    sending a quick HEAD request to common privacy URL patterns on that domain.
    A HEAD request only checks if the page exists — it doesn't download the whole page,
    so it's fast and lightweight.
    """
    # Strip the URL down to just the base domain
    # e.g. "https://www.instagram.com/explore" → "https://www.instagram.com"
    base = target_url.replace("http://", "https://")
    base = base.split("//")[1]        # remove "https://"
    base = base.split("/")[0]         # remove any path after the domain
    base = "https://" + base

    found_links = []

    # Try each common path one at a time
    for path in COMMON_PRIVACY_PATHS:
        test_url = base + path
        try:
            # HEAD request = "does this page exist?" without downloading content
            resp = requests.head(test_url, headers=REQUEST_HEADERS, timeout=5, verify=False, allow_redirects=True)

            if resp.status_code == 200:
                print(f"[+] Found privacy URL via fallback: {test_url}")
                found_links.append({
                    "keyword": "privacy",
                    "text":    path.strip("/").replace("-", " "),  # e.g. "/privacy-policy" → "privacy policy"
                    "url":     test_url
                })
                break  # One confirmed link is enough, stop checking

        except Exception:
            continue  # If a path times out or errors, just move to the next one

    return found_links


def extract_cookies(response):
    """Extracts basic token names and domains from network headers."""
    captured_cookies = []
    for cookie in response.cookies:
        captured_cookies.append({
            "name": cookie.name,
            "domain": cookie.domain
        })
    return captured_cookies


def log_data_to_csv(file_path, header_row, rows_to_write):
    """Opens a spreadsheet file in append mode and saves rows without erasing old logs."""
    # Write column titles ONLY if the file is brand new or empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header_row)

    # Drop down to the bottom line and write the new data row safely
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows_to_write:
            writer.writerow(row)


# ----------------------------------------------------------------------
# REST API ENDPOINT (The active listener waiting for the Extension)
# ----------------------------------------------------------------------

@app.route("/api/audit", methods=["POST"])
def audit():
    # 1. Grab and unpack the shipping box parameter from the network loop pipeline
    payload = request.get_json(silent=True)
    if not payload or "url" not in payload:
        return jsonify({"status": "error", "message": "Missing target URL parameter."}), 400

    target_url = normalize_url(payload["url"])
    print(f"[*] Actively auditing compliance for: {target_url}")

    # 2. Asynchronously connect to the live target website frame
    try:
        response = requests.get(target_url, headers=REQUEST_HEADERS, timeout=10, verify=False)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not reach site: {str(e)}"}), 502

    # 3. Use BeautifulSoup knife to slice up the HTML layout tree
    soup = BeautifulSoup(response.text, "html.parser")
    all_links = soup.find_all("a")

    # 4. Extract cookies and privacy links through our analytic loops
    matched_links = find_compliance_links(all_links)

    # NEW FALLBACK: If HTML scan found zero policy links, the site probably
    # loads its footer with JavaScript. Try common privacy URL patterns instead.
    if len(matched_links) == 0:
        print("[*] No links found in HTML — trying common privacy URL fallback...")
        matched_links = check_common_privacy_urls(target_url)

    cookies = extract_cookies(response)

    # 5. Permanent database ledger storage tracking
    timestamp = datetime.now().isoformat(timespec="seconds")
    
    link_rows = [[timestamp, target_url, l["keyword"], l["text"], l["url"]] for l in matched_links]
    cookie_rows = [[timestamp, target_url, c["name"], c["domain"]] for c in cookies]
    
    log_data_to_csv(LINKS_LOG_FILE, ["timestamp", "target_url", "keyword", "text", "url"], link_rows)
    log_data_to_csv(COOKIES_LOG_FILE, ["timestamp", "target_url", "name", "domain"], cookie_rows)

    # 6. CALCULATE THE COMPLIANCE GRADE ALGORITHM
    total_links = len(matched_links)
    total_cookies = len(cookies)
    
    if total_links == 0 and total_cookies > 0:
        grade = "F"  # Severe Risk: dropped trackers with zero user consent notification links!
    elif total_cookies > 7 or total_links == 0:
        grade = "D"
    elif total_cookies > 3:
        grade = "C"
    elif total_cookies > 0:
        grade = "B"
    else:
        grade = "A"  # Beautiful privacy protection metrics!

    # 7. Package up the response packet tray and ship it back out across port 5000
    return jsonify({
        "status": "success",
        "url": target_url,
        "audit_timestamp": timestamp,
        "total_links_found": total_links,
        "total_cookies_found": total_cookies,
        "compliance_grade": grade,
        "links": matched_links,
        "cookies": cookies
    }), 200


if __name__ == "__main__":
    # Force Flask to accept localhost connections cleanly
    app.run(host="127.0.0.1", port=5000, debug=True)