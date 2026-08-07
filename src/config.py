import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("wa-desktop-mcp.config")

# Project Directory references
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SRC_DIR)

# Writable User Data Directory (%LOCALAPPDATA%\WhatsApp MCP Companion)
LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
USER_DATA_DIR = os.path.join(LOCAL_APP_DATA, "WhatsApp MCP Companion")
os.makedirs(USER_DATA_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(USER_DATA_DIR, "config.json")
MESSAGES_LOG_PATH = os.path.join(USER_DATA_DIR, "local_messages.json")
CRM_DB_PATH = os.path.join(USER_DATA_DIR, "crm.json")
SESSION_PATH = os.path.join(USER_DATA_DIR, ".wa_session")

DEFAULT_CONFIG = {
    "mode": "setup",  # 'setup', 'web', or 'api'
    "meta_phone_number_id": "",
    "meta_waba_id": "",
    "meta_access_token": "",
    "webhook_verify_token": "wa_mcp_local_verify",
    "ngrok_auth_token": "",
    "ngrok_domain": ""
}

# Runtime public URL (in-memory only, not persisted to config file)
PUBLIC_TUNNEL_URL = ""

def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config, returning defaults: {e}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
