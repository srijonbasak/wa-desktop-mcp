import logging
from typing import Dict, Any
import httpx
from ..config import load_config
from ..database import load_messages, save_messages
import time

logger = logging.getLogger("wa-desktop-mcp.api")

async def send_api_message(phone: str, text: str) -> Dict[str, Any]:
    """
    Sends a WhatsApp message to a phone number using Meta's Cloud API.
    Logs outbound messages to local messages database.
    """
    config = load_config()
    token = config.get("meta_access_token")
    phone_id = config.get("meta_phone_number_id")

    if not token or not phone_id:
        return {"error": "Meta API credentials are not configured"}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    }
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Meta API send failed: {resp.text}")
                return {"status": "error", "message": resp.text}
            
            # Log to local history
            stored = load_messages()
            msg_id = resp.json().get("messages", [{}])[0].get("id")
            stored.append({
                "message_id": msg_id,
                "phone": phone,
                "name": phone,
                "text": text,
                "timestamp": str(int(time.time())),
                "type": "outgoing",
                "read": True
            })
            save_messages(stored)
            logger.info(f"Meta API message sent successfully to {phone}, message_id: {msg_id}")
            return {"status": "success", "message_id": msg_id}
    except Exception as e:
        logger.error(f"Exception sending Meta API message: {e}")
        return {"status": "error", "message": str(e)}
