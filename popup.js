document.addEventListener('DOMContentLoaded', async () => {

    // Grab all the UI elements we need to update
    const gradeBox     = document.getElementById('gradeBox');
    const riskLabel    = document.getElementById('riskLabel');
    const riskBar      = document.getElementById('riskBar');
    const emojiBox     = document.getElementById('emojiBox');
    const statusMsg    = document.getElementById('statusMsg');
    const linksCount   = document.getElementById('linksCount');
    const cookiesCount = document.getElementById('cookiesCount');
    const httpsValue   = document.getElementById('httpsValue');
    const trackerBox   = document.getElementById('trackerBox');
    const scanTime     = document.getElementById('scanTime');
    const helpBtn      = document.getElementById('helpBtn');

    // When the user clicks "? Help", open the help page in a new browser tab
    if (helpBtn) {
        helpBtn.addEventListener('click', () => {
            chrome.tabs.create({ url: chrome.runtime.getURL('help.html') });
        });
    }

    // Each grade maps to: a color, a label, a risk bar fill amount, an emoji, and an animation class
    const GRADE_CONFIG = {
        "A": { color: "#3fb950", label: "Safe: Minimal Tracking Detected",     barWidth: "10%",  emoji: "😊", animClass: "anim-bounce"     },
        "B": { color: "#58a6ff", label: "Good: Compliant Public Notice",        barWidth: "35%",  emoji: "🙂", animClass: "anim-pulse"      },
        "C": { color: "#d29922", label: "Moderate Risk: Active Data Gathering", barWidth: "60%",  emoji: "😬", animClass: "anim-wobble"     },
        "D": { color: "#ff7b72", label: "Warning: Loose Transparency Anchors",  barWidth: "80%",  emoji: "😨", animClass: "anim-shake"      },
        "F": { color: "#f85149", label: "Severe Risk: Non-Consensual Tracking", barWidth: "100%", emoji: "😱", animClass: "anim-shake-fast" }
    };

    // Ask Chrome which tab the user has open right now
    chrome.tabs.query({ active: true, currentWindow: true }, async (tabs) => {
        const activeTab = tabs[0];

        // If user is on a non-web page (like chrome:// settings), show a safe message
        if (!activeTab || !activeTab.url || !activeTab.url.startsWith('http')) {
            if (statusMsg)  statusMsg.innerText  = "Navigate to a live web page to run audit.";
            if (gradeBox)   { gradeBox.innerText  = "N/A"; gradeBox.style.color = "#8b949e"; }
            if (emojiBox)   emojiBox.innerText    = "🌐";
            if (riskLabel)  riskLabel.innerText   = "No Active Web Page";
            if (trackerBox) trackerBox.innerHTML  = '<div class="tracker-empty">Open a website first.</div>';
            return;
        }

        if (statusMsg) statusMsg.innerText = "Scanning...";
        if (emojiBox)  emojiBox.innerText  = "🔍";

        try {
            // Send the active tab URL to our Flask backend for analysis
            const response = await fetch('http://127.0.0.1:5000/api/audit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: activeTab.url })
            });

            const data = await response.json();

            // If the server returned an error message, show it
            if (data.status === 'error') {
                if (statusMsg) statusMsg.innerText = "Audit failed: " + data.message;
                if (gradeBox)  { gradeBox.innerText = "ERR"; gradeBox.style.color = "#f85149"; }
                if (emojiBox)  emojiBox.innerText   = "⚠️";
                if (riskLabel) riskLabel.innerText  = "Processing Error";
                return;
            }

            // --- Update the 3 stat cards ---
            if (linksCount)   linksCount.innerText   = data.total_links_found;
            if (cookiesCount) cookiesCount.innerText = data.total_cookies_found;

            // HTTPS badge: green checkmark if secure, red X if not
            if (httpsValue) {
                if (data.is_https == true) {
                    httpsValue.innerText = "✓";
                    httpsValue.className = "stat-value secure";
                } else {
                    httpsValue.innerText = "✗";
                    httpsValue.className = "stat-value insecure";
                }
            }

            // --- Update grade banner: emoji + grade letter + risk bar ---
            const config = GRADE_CONFIG[data.compliance_grade];

            if (config) {
                // Set the animated emoji — the CSS class controls which animation plays
                if (emojiBox) {
                    emojiBox.innerText = config.emoji;
                    emojiBox.className = config.animClass;
                }

                if (gradeBox) {
                    gradeBox.innerText   = data.compliance_grade;
                    gradeBox.style.color = config.color;
                }

                if (riskLabel) {
                    riskLabel.innerText    = config.label;
                    riskLabel.style.color  = config.color;
                }

                if (riskBar) {
                    riskBar.style.width           = config.barWidth;
                    riskBar.style.backgroundColor = config.color;
                }
            }

            // --- Build the Known Trackers list ---
            if (trackerBox) {
                trackerBox.innerHTML = "";

                // Only show cookies that our server recognized as known trackers
                const knownTrackers = [];
                for (let i = 0; i < data.cookies.length; i++) {
                    if (data.cookies[i].tracker != null) {
                        knownTrackers.push(data.cookies[i]);
                    }
                }

                if (knownTrackers.length == 0) {
                    trackerBox.innerHTML = '<div class="tracker-empty">✓ No known trackers detected</div>';
                } else {
                    for (let i = 0; i < knownTrackers.length; i++) {
                        const row = document.createElement('div');
                        row.className = 'tracker-row';
                        row.innerHTML =
                            '<span class="tracker-name">' + knownTrackers[i].name + '</span>' +
                            '<span class="tracker-badge">' + knownTrackers[i].tracker + '</span>';
                        trackerBox.appendChild(row);
                    }
                }
            }

            // --- Update the footer ---
            if (statusMsg) statusMsg.innerText = "Audit complete. Ledger updated.";

            // Show just the time part from the ISO timestamp e.g. "14:32:07"
            if (scanTime && data.audit_timestamp) {
                scanTime.innerText = data.audit_timestamp.split("T")[1];
            }

        } catch (err) {
            // This fires when server.py is not running at all
            if (statusMsg)  statusMsg.innerText = "Backend offline. Double-click start.bat to fix.";
            if (gradeBox)   { gradeBox.innerText = "OFF"; gradeBox.style.color = "#6e7681"; }
            if (emojiBox)   { emojiBox.innerText = "😴"; emojiBox.className = ""; }
            if (riskLabel)  riskLabel.innerText  = "Server Not Running";
            if (trackerBox) trackerBox.innerHTML = '<div class="tracker-empty">Run start.bat then reload the extension.</div>';
            console.error(err);
        }
    });
});