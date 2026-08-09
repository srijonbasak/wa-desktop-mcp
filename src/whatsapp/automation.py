# JavaScript injection macros for WhatsApp Web DOM interaction

JS_SCRAPE_CHATS = """
(function() {
    try {
        const rows = document.querySelectorAll('div[role="row"]');
        const chats = [];
        rows.forEach(row => {
            const titleEl = row.querySelector('span[title]');
            if (!titleEl) return;
            const name = titleEl.getAttribute('title');
            
            const msgEl = row.querySelector('span[dir="ltr"]');
            const last_msg = msgEl ? msgEl.textContent : "";
            
            // Check for unread indicators
            const badgeEl = row.querySelector('span[aria-label*="unread"], span._ak8q, div._ak8q');
            let unread_count = 0;
            if (badgeEl) {
                const countText = badgeEl.textContent.trim();
                if (countText && !isNaN(countText)) {
                    unread_count = parseInt(countText);
                } else {
                    unread_count = 1;
                }
            }
            chats.push({
                "name": name,
                "last_message": last_msg,
                "unread_count": unread_count
            });
        });
        return chats;
    } catch(e) {
        return [];
    }
})()
"""

JS_GET_ACTIVE_CHAT = """
(function() {
    try {
        const header = document.querySelector('header');
        if (!header) return null;
        const titleEl = header.querySelector('span[title]');
        return titleEl ? titleEl.getAttribute('title') : null;
    } catch(e) {
        return null;
    }
})()
"""

JS_CLICK_CHAT = """
(function(targetName) {
    try {
        const rows = document.querySelectorAll('div[role="row"]');
        let foundRow = null;
        rows.forEach(row => {
            const titleEl = row.querySelector('span[title]');
            if (titleEl && titleEl.getAttribute('title') === targetName) {
                foundRow = row;
            }
        });
        if (foundRow) {
            foundRow.click();
            return true;
        }
        return false;
    } catch(e) {
        return false;
    }
})("{chat_name}")
"""

JS_SCRAPE_BUBBLES = """
(function() {
    try {
        const bubbles = document.querySelectorAll('div.message-in, div.message-out');
        const history = [];
        bubbles.forEach(b => {
            const isIncoming = b.classList.contains('message-in');
            const textSpan = b.querySelector('span.selectable-text');
            const text = textSpan ? textSpan.textContent : b.textContent;
            if (text) {
                history.push({
                    "sender": isIncoming ? "customer" : "me",
                    "text": text.trim()
                });
            }
        });
        return history.slice(-15);
    } catch(e) {
        return [];
    }
})()
"""

JS_SEND_MESSAGE = """
(function(textVal) {
    try {
        const inputEl = document.querySelector('div[contenteditable="true"]');
        if (!inputEl) return { "status": "error", "message": "Input field not found" };
        
        inputEl.focus();
        
        // Simulates keyboard insertion to trigger react events
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, textVal);
        
        // Force React to recognize the input change (swapping microphone icon to send button)
        inputEl.dispatchEvent(new Event('input', { bubbles: true }));
        inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Defer querying and clicking the send button to allow React DOM update to finish rendering it
        setTimeout(() => {
            const selectors = [
                'button[aria-label="Send"]',
                'button[data-testid="send"]',
                'span[data-icon="send"]',
                'span[data-testid="send"]',
                'button span[data-icon="send"]'
            ];
            
            let sendBtn = null;
            for (const s of selectors) {
                sendBtn = document.querySelector(s);
                if (sendBtn) break;
            }
            
            if (sendBtn) {
                const clickTarget = sendBtn.closest('button') || sendBtn;
                clickTarget.click();
            } else {
                // Fallback: Dispatch Enter key event
                const enterDown = new KeyboardEvent('keydown', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                });
                const enterUp = new KeyboardEvent('keyup', {
                    key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                });
                inputEl.dispatchEvent(enterDown);
                inputEl.dispatchEvent(enterUp);
            }
        }, 150);
        
        return { "status": "success" };
    } catch(e) {
        return { "status": "error", "message": e.message };
    }
})("{text}")
"""

JS_DRAFT_MESSAGE = """
(function(textVal) {
    try {
        const inputEl = document.querySelector('div[contenteditable="true"]');
        if (!inputEl) return { "status": "error", "message": "Input field not found" };
        
        inputEl.focus();
        
        // Simulates keyboard insertion to trigger react events
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, textVal);
        
        // Force React to recognize the input change
        inputEl.dispatchEvent(new Event('input', { bubbles: true }));
        inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Unlike SEND_MESSAGE, we do NOT click the send button or dispatch Enter.
        // We leave the text in the input box for the user to review and send.
        
        return { "status": "success" };
    } catch(e) {
        return { "status": "error", "message": e.message };
    }
})("{text}")
"""

JS_NAVIGATE_CHAT = """
(function(phone) {
    try {
        window.history.pushState(null, "", "/send?phone=" + phone);
        window.dispatchEvent(new PopStateEvent("popstate"));
        return true;
    } catch(e) {
        return false;
    }
})("{phone}")
"""
