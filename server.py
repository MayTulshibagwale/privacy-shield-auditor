# ======================================================================
#  Privacy Shield Auditor — Backend API
# ======================================================================
import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Keywords we search for in page links to find privacy policy disclosures
KEYWORDS = ["privacy", "policy", "cookie", "terms"]

# CSV log file names — every scan is saved here automatically
LINKS_LOG_FILE   = "privacy_links_log.csv"
COOKIES_LOG_FILE = "tracking_cookies_log.csv"

# Fake browser identity so websites don't block our requests
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Known tracking cookie name prefixes and which company they belong to
KNOWN_TRACKERS = {
    "_ga":                  "Google Analytics",
    "_gid":                 "Google Analytics",
    "_gcl_au":              "Google Ads",
    "IDE":                  "Google DoubleClick",
    "NID":                  "Google",
    "__utma":               "Google Analytics (Legacy)",
    "__utmb":               "Google Analytics (Legacy)",
    "__utmz":               "Google Analytics (Legacy)",
    "_fbp":                 "Facebook Pixel",
    "_fbc":                 "Facebook Click ID",
    "fr":                   "Facebook",
    "datr":                 "Facebook",
    "MUID":                 "Microsoft",
    "MR":                   "Microsoft",
    "_pin_unauth":          "Pinterest",
    "twid":                 "Twitter / X",
    "guest_id":             "Twitter / X",
    "bcookie":              "LinkedIn",
    "bscookie":             "LinkedIn",
    "li_sugr":              "LinkedIn",
    "UserMatchHistory":     "LinkedIn",
    "AnalyticsSyncHistory": "LinkedIn",
}

# Common URL paths where privacy policies hide on JavaScript-heavy sites
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


# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------

def normalize_url(raw_url):
    """Adds https:// if the URL is missing it."""
    cleaned_url = raw_url.strip()
    if not cleaned_url.startswith("http://") and not cleaned_url.startswith("https://"):
        cleaned_url = "https://" + cleaned_url
    return cleaned_url


def check_https(url):
    """Returns True if the site uses HTTPS, False if not."""
    if url.startswith("https://"):
        return True
    return False


def find_compliance_links(all_links):
    """Scans all page links and returns the ones matching our privacy keywords."""
    matched_links = []
    for link in all_links:
        link_text = link.get_text().lower().strip()
        link_url  = (link.get("href") or "").lower().strip()

        # Combine visible text and href into one searchable string
        searchable_text = link_text + " " + link_url

        for keyword in KEYWORDS:
            if keyword in searchable_text:
                matched_links.append({
                    "keyword": keyword,
                    "text":    link_text,
                    "url":     link_url
                })
                break  # Stop at the first keyword match for this link
    return matched_links


def check_common_privacy_urls(target_url):
    """
    Fallback for JavaScript-heavy sites like Instagram that load footer
    links dynamically. Sends a lightweight HEAD request to common privacy
    URL patterns to check if the page exists without downloading it.
    """
    # Strip down to just the base domain e.g. "https://www.instagram.com"
    base = target_url.replace("http://", "https://")
    base = base.split("//")[1]
    base = base.split("/")[0]
    base = "https://" + base

    for path in COMMON_PRIVACY_PATHS:
        try:
            resp = requests.head(base + path, headers=REQUEST_HEADERS, timeout=5, verify=False, allow_redirects=True)
            if resp.status_code == 200:
                print(f"[+] Privacy URL found via fallback: {base + path}")
                return [{"keyword": "privacy", "text": path.strip("/").replace("-", " "), "url": base + path}]
        except Exception:
            continue  # Move to the next path if this one fails

    return []  # Nothing found


def classify_cookies(response):
    """
    Reads cookies from the response and checks each one against
    KNOWN_TRACKERS to identify which company dropped it.
    Returns only name and tracker — the two fields the popup uses.
    """
    classified = []
    for cookie in response.cookies:
        # Check if this cookie name matches any known tracker prefix
        tracker_owner = None
        for known_prefix in KNOWN_TRACKERS:
            if cookie.name.startswith(known_prefix):
                tracker_owner = KNOWN_TRACKERS[known_prefix]
                break

        classified.append({
            "name":    cookie.name,
            "domain":  cookie.domain,   # kept for CSV logging
            "tracker": tracker_owner    # None if unknown, company name if recognized
        })
    return classified


def log_data_to_csv(file_path, header_row, rows_to_write):
    """Saves rows to a CSV file in append mode — never erases old scans."""
    # Write the header row only if the file is brand new or empty
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        with open(file_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(header_row)

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows_to_write:
            writer.writerow(row)


# ----------------------------------------------------------------------
# API ENDPOINT
# ----------------------------------------------------------------------

@app.route("/api/audit", methods=["POST"])
def audit():
    # 1. Get the URL from the extension
    payload = request.get_json(silent=True)
    if not payload or "url" not in payload:
        return jsonify({"status": "error", "message": "Missing target URL."}), 400

    target_url = normalize_url(payload["url"])
    print(f"[*] Scanning: {target_url}")

    # 2. Check HTTPS before connecting
    is_https = check_https(target_url)

    # 3. Fetch the page HTML
    try:
        response = requests.get(target_url, headers=REQUEST_HEADERS, timeout=10, verify=False)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not reach site: {str(e)}"}), 502

    # 4. Parse HTML and find privacy links
    soup      = BeautifulSoup(response.text, "html.parser")
    all_links = soup.find_all("a")
    matched_links = find_compliance_links(all_links)

    # 5. If no links found in HTML, try common privacy URL patterns as fallback
    if len(matched_links) == 0:
        print("[*] No links found in HTML — trying common URL fallback...")
        matched_links = check_common_privacy_urls(target_url)

    # 6. Classify cookies and identify known trackers
    cookies = classify_cookies(response)

    # 7. Save everything to CSV logs
    timestamp   = datetime.now().isoformat(timespec="seconds")
    link_rows   = [[timestamp, target_url, l["keyword"], l["text"], l["url"]] for l in matched_links]
    cookie_rows = [[timestamp, target_url, c["name"], c["domain"], c["tracker"]] for c in cookies]

    log_data_to_csv(LINKS_LOG_FILE,   ["timestamp", "target_url", "keyword", "text", "url"],         link_rows)
    log_data_to_csv(COOKIES_LOG_FILE, ["timestamp", "target_url", "name", "domain", "tracker"],      cookie_rows)

    # 8. Calculate compliance grade
    total_links   = len(matched_links)
    total_cookies = len(cookies)
    known_tracker_count = sum(1 for c in cookies if c["tracker"] != None)

    if is_https == False and total_cookies > 0:
        grade = "F"  # Tracking over an insecure connection
    elif total_links == 0 and total_cookies > 0:
        grade = "F"  # Dropping cookies with zero privacy disclosure
    elif total_cookies > 7 or total_links == 0:
        grade = "D"
    elif total_cookies > 3 or known_tracker_count > 2:
        grade = "C"
    elif total_cookies > 0:
        grade = "B"
    else:
        grade = "A"

    # 9. Send back only what the extension popup needs
    return jsonify({
        "status":              "success",
        "audit_timestamp":     timestamp,
        "is_https":            is_https,
        "total_links_found":   total_links,
        "total_cookies_found": total_cookies,
        "compliance_grade":    grade,
        "cookies":             cookies
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)