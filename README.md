# 🔍 Privacy Shield Auditor

Ever wondered how much a website is tracking you? **Privacy Shield Auditor** is a Chrome extension that scans any website you visit and gives it a privacy grade from A to F — instantly telling you how safe your data is.

Built as a portfolio project demonstrating web scraping, REST API design, and Chrome extension development.

---

## ✨ What It Does

- 🔒 **Checks if the site is secure** — verifies the website uses HTTPS encryption
- ⚖️ **Finds privacy disclosures** — looks for Privacy Policy, Cookie Notice, and Terms of Service links
- 🍪 **Counts tracking cookies** — identifies every cookie the site drops on your browser
- 🎯 **Names the trackers** — recognizes 22+ known trackers from Google, Facebook, LinkedIn, Twitter, and more
- 📊 **Gives an instant grade (A–F)** — with an animated emoji and colour-coded risk bar
- 📁 **Saves a local audit log** — every scan is automatically recorded to a spreadsheet on your computer
- 🔍 **Smart fallback scanning** — if a website hides its privacy links, the tool finds them another way

---

## 📊 Grading System

| Grade | Emoji | What It Means |
|---|---|---|
| A | 😊 | Safe — the site is secure, has a privacy policy, and drops zero cookies |
| B | 🙂 | Good — has a privacy policy and only a few cookies |
| C | 😬 | Moderate — several cookies or multiple known ad trackers detected |
| D | 😨 | Warning — too many cookies or missing privacy disclosures |
| F | 😱 | Severe — tracking you with no privacy notice, or using an insecure connection |

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

### Before you start
Make sure you have **Python** installed on your computer. You can download it from [python.org](https://python.org).

### 1. Clone the repository
```bash
git clone https://github.com/MayTulshibagwale/privacy-shield-auditor.git
cd privacy-shield-auditor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the backend server

**Windows** — just double-click:
```
start.bat
```
> 💡 **Tip:** Set up Windows Task Scheduler to run `start.bat` on login so the server starts automatically every time you turn on your computer — no terminal needed!

**Mac / Linux** — run in terminal:
```bash
chmod +x start.sh
./start.sh
```

Keep this window open while using the extension.

### 4. Load the Chrome Extension

1. Open Chrome and go to `chrome://extensions`
2. Turn on **Developer Mode** (toggle in the top right)
3. Click **"Load unpacked"**
4. Select this project folder
5. The 🔍 Privacy Shield Auditor icon will appear in your toolbar

---

## 🚀 How to Use

1. Start the backend server (`start.bat` on Windows)
2. Go to any website in Chrome
3. Click the **Privacy Shield Auditor** icon in your toolbar
4. The extension automatically scans the page and shows:
   - A privacy grade (A–F) with animated emoji
   - Whether the site uses a secure connection
   - How many privacy policy links and cookies were found
   - A list of any recognized third-party trackers
5. Click **? Help** inside the extension for plain-English explanations of every term

---

## 📁 Project Structure

```
privacy-shield-auditor/
│
├── server.py              # Python backend — does all the scanning
├── auditor.py             # Original prototype script (Phase 1)
├── start.bat              # Windows auto-start script
├── start.sh               # Mac / Linux auto-start script
├── requirements.txt       # Python libraries needed to run the project
│
├── manifest.json          # Chrome extension configuration
├── popup.html             # Extension popup — what you see when you click the icon
├── popup.js               # Extension logic — connects popup to the backend
├── index.html             # Full web dashboard version
├── help.html              # Built-in help page explaining every term
```

---

## ⚠️ Known Limitations

- Some websites load their content dynamically after the page opens, so the scanner may not see everything. A fallback check on common privacy URL patterns helps reduce this.
- Cookies are only detected on the initial page load — not after you click around or log in.
- Results may vary by location since some sites show different cookie banners depending on your country.

---

## 🔮 Possible Future Improvements

- [ ] Full JavaScript rendering — scan what the page looks like after it fully loads
- [ ] Scan multiple pages per site, not just the homepage
- [ ] Detect how long each cookie lasts (session vs permanent)
- [ ] Check against GDPR and CCPA legal requirements
- [ ] Track how a site's privacy grade changes over time

---

## 👩‍💻 Author

Built by **Mrunmayee** as a portfolio project.  
Feel free to fork, star ⭐, or reach out with feedback!

---

## 🖼️ Preview

To see the extension in action, check out the screenshots folder:  
👉 [View Screenshots](https://github.com/MayTulshibagwale/privacy-shield-auditor/tree/main/screenshots)
