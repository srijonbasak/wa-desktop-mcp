import os
import time
import logging
import webview
from .config import load_config, save_config, SESSION_PATH

import threading

logger = logging.getLogger("wa-desktop-mcp.gui")

# Reference to the PyWebView window instance
window = None

class JSAPI:
    def get_mode(self) -> str:
        config = load_config()
        return config.get("mode", "web")

    def set_mode(self, mode: str) -> None:
        config = load_config()
        config["mode"] = mode
        save_config(config)
        
        # Defer redirection in a background thread so the JS context
        # callback has time to safely resolve before the page unloads.
        def defer_redirect():
            time.sleep(0.1)
            global window
            if window:
                if mode == "web":
                    window.load_url("https://web.whatsapp.com")
                else:
                    window.load_url("http://127.0.0.1:48211")
        
        threading.Thread(target=defer_redirect, daemon=True).start()

def _inject_settings_button():
    """
    Injects a settings toggle button ('⚙️ MCP Config') once the page loads.
    """
    global window
    try:
        if window:
            url = window.get_current_url()
            if url and "whatsapp.com" in url:
                js = """
                (function() {
                    if (document.getElementById('mcp-settings-btn')) return;
                    const btn = document.createElement('button');
                    btn.id = 'mcp-settings-btn';
                    btn.innerHTML = '⚙️ MCP Config';
                    btn.style.position = 'fixed';
                    btn.style.bottom = '15px';
                    btn.style.left = '15px';
                    btn.style.zIndex = '999999';
                    btn.style.backgroundColor = '#1e293b';
                    btn.style.color = '#f8fafc';
                    btn.style.border = '1px solid #334155';
                    btn.style.padding = '8px 12px';
                    btn.style.borderRadius = '6px';
                    btn.style.cursor = 'pointer';
                    btn.style.fontWeight = 'bold';
                    btn.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.5)';
                    btn.onclick = function() {
                        window.pywebview.api.set_mode('setup');
                    };
                    document.body.appendChild(btn);
                })();
                """
                window.evaluate_js(js)
    except Exception as e:
        logger.debug(f"Failed to inject settings button: {e}")

def get_asset_path(filename):
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'asset', filename)
    # If running locally from source
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'asset', filename)

def start_gui():
    global window
    config = load_config()
    mode = config.get("mode", "setup")
    
    if mode == "web":
        start_url = "https://web.whatsapp.com"
    else:
        start_url = "http://127.0.0.1:48211"
        
    logger.info("Initializing PyWebView wrapper window...")
    js_api = JSAPI()
    window = webview.create_window(
        "WhatsApp Local MCP Companion",
        url=start_url,
        js_api=js_api,
        width=1150,
        height=780,
        minimized=True
    )
    
    # Bind the injection logic to trigger natively when the page loads
    window.events.loaded += _inject_settings_button
    
    # Enable session cookies & local storage inside local .wa_session/ path
    webview.start(private_mode=False, storage_path=SESSION_PATH, icon=get_asset_path('logo.ico'))
