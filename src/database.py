import os
import json
import logging
from typing import List, Dict, Any
from .config import MESSAGES_LOG_PATH

logger = logging.getLogger("wa-desktop-mcp.database")

def load_messages() -> List[Dict[str, Any]]:
    if not os.path.exists(MESSAGES_LOG_PATH):
        return []
    try:
        with open(MESSAGES_LOG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load messages database: {e}")
        return []

def save_messages(messages: List[Dict[str, Any]]) -> None:
    try:
        with open(MESSAGES_LOG_PATH, "w") as f:
            json.dump(messages, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save messages database: {e}")

def load_crm_data() -> Dict[str, Dict[str, Any]]:
    from .config import CRM_DB_PATH
    if not os.path.exists(CRM_DB_PATH):
        return {}
    try:
        with open(CRM_DB_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load CRM database: {e}")
        return {}

def save_crm_data(crm_data: Dict[str, Dict[str, Any]]) -> None:
    from .config import CRM_DB_PATH
    try:
        with open(CRM_DB_PATH, "w") as f:
            json.dump(crm_data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save CRM database: {e}")
