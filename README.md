# 🔍 Privacy Shield Auditor

A Chrome extension + Python backend that automatically scans any website for privacy compliance — detecting tracking cookies, checking HTTPS security, finding policy links, and grading the site from A to F in real time.

Built as a portfolio project demonstrating web scraping, REST API design, and browser extension development.

---

## 📸 Screenshots

> Drop your own screenshots here after uploading to GitHub!

| Extension Popup | Help Guide |
|---|---|
| *(screenshot here)* | *(screenshot here)* |

---

## ✨ Features

- 🔒 **HTTPS Detection** — flags whether the site uses a secure connection
- ⚖️ **Policy Link Scanner** — finds Privacy Policy, Cookie Notice, and Terms of Service links
- 🍪 **Cookie Tracker** — counts and identifies all cookies the site drops
- 🎯 **Known Tracker Detection** — recognizes 25+ trackers from Google, Facebook, LinkedIn, Twitter, and more
- 🌍 **First vs Third-Party Classification** — tells you who actually set each cookie
- 📊 **Compliance Grade (A–F)** — instant letter grade with animated emoji and risk bar
- 📁 **CSV Audit Logs** — every scan is saved locally to spreadsheet files
- 🔁 **JavaScript Fallback** — checks common privacy URL patterns for sites that load links dynamically

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Scraping | Requests, BeautifulSoup4 |
| Frontend | Chrome Extension (Manifest V3), HTML, CSS, JavaScript |
| Logging | Python CSV module |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/privacy-shield-auditor.git
cd privacy-shield-auditor
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the backend server

**Windows** — just double-click:
```
start.bat
```

**Mac / Linux:**
```bash
python server.py
```

Keep this terminal window open while using the extension.

> 💡 **Tip for Windows users:** Set up Windows Task Scheduler to run `start.bat` on login so the server starts automatically every time you turn on your computer.

### 4. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Turn on **Developer Mode** (toggle in the top right)
3. Click **"Load unpacked"**
4. Select this project folder
5. The 🔍 Privacy Shield Auditor icon will appear in your toolbar

---

## 🚀 How to Use

1. Make sure the backend server is running (`start.bat`)
2. Navigate to any website in Chrome
3. Click the **Privacy Shield Auditor** extension icon
4. The extension automatically scans the current page and shows:
   - A compliance grade (A–F) with animated emoji
   - HTTPS status
   - Number of policy links and cookies found
   - List of recognized third-party trackers
5. Click **? Help** for a full explanation of what each score means

---

## 📊 Grading System

| Grade | Emoji | Meaning |
|---|---|---|
| A | 😊 | Safe — HTTPS, has policy links, zero cookies |
| B | 🙂 | Good — has policy links, few cookies |
| C | 😬 | Moderate — several cookies or multiple known trackers |
| D | 😨 | Warning — heavy cookie load or missing policy links |
| F | 😱 | Severe — no privacy disclosure while dropping cookies, or no HTTPS |

---

## 📁 Project Structure

```
privacy-shield-auditor/
│
├── server.py              # Flask REST API backend
├── auditor.py             # Standalone Python scraper (original script)
├── start.bat              # Windows auto-start script
├── requirements.txt       # Python dependencies
│
├── manifest.json          # Chrome extension config
├── popup.html             # Extension popup UI
├── popup.js               # Extension popup logic
├── index.html             # Full web dashboard (optional)
├── help.html              # User-friendly help & glossary page
│
├── privacy_links_log.csv  # Auto-generated audit log for policy links
└── tracking_cookies_log.csv # Auto-generated audit log for cookies
```

---

## 📋 API Reference

The backend exposes a single endpoint:

**POST** `/api/audit`

**Request body:**
```json
{
  "url": "https://instagram.com"
}
```

**Response:**
```json
{
  "status": "success",
  "url": "https://instagram.com",
  "audit_timestamp": "2024-01-15T14:32:07",
  "is_https": true,
  "total_links_found": 1,
  "total_cookies_found": 2,
  "known_tracker_count": 0,
  "compliance_grade": "B",
  "links": [...],
  "cookies": [...]
}
```

---

## ⚠️ Known Limitations

- The scraper uses `requests` which does not execute JavaScript. Sites that load all content dynamically may return fewer links than expected. A common privacy URL fallback is included to partially address this.
- Cookie detection only captures cookies set during the initial page load, not cookies set after user interaction.
- Results may vary depending on the user's location due to region-specific cookie consent banners.

---

## 🔮 Possible Future Improvements

- [ ] Selenium integration for full JavaScript rendering
- [ ] Scan multiple pages per domain, not just the homepage
- [ ] Cookie expiry detection (session vs persistent)
- [ ] GDPR / CCPA compliance checklist
- [ ] Historical scan comparison — track how a site's privacy grade changes over time

---

## 👩‍💻 Author

Built by **Mrunmayee** as a portfolio project.  
Feel free to fork, star ⭐, or reach out with feedback!
