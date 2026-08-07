import logging
import asyncio
from typing import List, Dict, Any
from fastmcp import FastMCP
from .config import load_config
from .database import load_messages, save_messages, load_crm_data, save_crm_data
from . import gui
from .whatsapp.automation import (
    JS_SCRAPE_CHATS,
    JS_GET_ACTIVE_CHAT,
    JS_CLICK_CHAT,
    JS_SCRAPE_BUBBLES,
    JS_SEND_MESSAGE,
    JS_DRAFT_MESSAGE
)
from .whatsapp.api import send_api_message

logger = logging.getLogger("wa-desktop-mcp.mcp")

mcp = FastMCP("wa-desktop-mcp")

async def _ensure_active_chat(chat_name: str) -> bool:
    """Helper to select a chat in the UI or deep-link if missing."""
    if not gui.window:
        return False
        
    active_chat = gui.window.evaluate_js(JS_GET_ACTIVE_CHAT)
    if active_chat == chat_name:
        return True
        
    clicked = gui.window.evaluate_js(JS_CLICK_CHAT.replace("{chat_name}", chat_name))
    if not clicked:
        clean_phone = "".join(c for c in chat_name if c.isdigit() or c == '+')
        phone_digits = clean_phone.replace("+", "")
        
        # BD local number formatting: e.g. 01303126776 -> 8801303126776
        if len(phone_digits) == 11 and phone_digits.startswith("01"):
            phone_digits = "88" + phone_digits
        
        if len(phone_digits) >= 7 and phone_digits.isdigit():
            logger.info(f"Contact '{chat_name}' not found. Opening deep-link: {phone_digits}...")
            send_url = f"https://web.whatsapp.com/send?phone={phone_digits}"
            gui.window.load_url(send_url)
            await asyncio.sleep(7.0)
            return True
        else:
            return False
    else:
        await asyncio.sleep(1.5)
        return True


@mcp.tool(annotations={"readOnlyHint": True})
async def read_chats() -> List[Dict[str, Any]]:
    """
    Lists recent active chats, including sender name, last message summary, and unread counts.
    """
    config = load_config()
    mode = config.get("mode", "web")

    crm_data = load_crm_data()

    if mode == "web":
        if not gui.window:
            return [{"error": "WebView window not initialized"}]
        # Evaluate JS to get chats list
        res = gui.window.evaluate_js(JS_SCRAPE_CHATS)
        chats = res or []
        for c in chats:
            name = c.get("name", "")
            contact_crm = crm_data.get(name, {})
            c["crm_stage"] = contact_crm.get("stage", "Lead")
            c["crm_tags"] = contact_crm.get("tags", [])
            c["crm_notes"] = contact_crm.get("notes", "")
        return chats
    else:
        # API mode: Group local messages by sender
        msgs = load_messages()
        chats_dict = {}
        for m in msgs:
            phone = m["phone"]
            name = m["name"]
            if phone not in chats_dict:
                chats_dict[phone] = {
                    "name": name,
                    "phone": phone,
                    "last_message": m["text"],
                    "unread_count": 1 if not m.get("read", False) else 0
                }
            else:
                chats_dict[phone]["last_message"] = m["text"]
                if not m.get("read", False):
                    chats_dict[phone]["unread_count"] += 1
        for c in chats_dict.values():
            contact_crm = crm_data.get(c["phone"], {})
            c["crm_stage"] = contact_crm.get("stage", "Lead")
            c["crm_tags"] = contact_crm.get("tags", [])
            c["crm_notes"] = contact_crm.get("notes", "")
        return list(chats_dict.values())

@mcp.tool(annotations={"readOnlyHint": True})
async def get_chat_history(chat_name: str) -> List[Dict[str, Any]]:
    """
    Retrieves the last 15 messages in the chat history for a specific contact name or phone number.
    Args:
        chat_name: The contact name (for Web mode) or the phone number in international format (for API mode).
    """
    config = load_config()
    mode = config.get("mode", "web")

    if mode == "web":
        if not gui.window:
            return [{"error": "WebView window not initialized"}]
        
        # Verify if the chat is already active
        if not await _ensure_active_chat(chat_name):
            return [{"error": f"Failed to select contact '{chat_name}'"}]
        
        # Scrape messages
        res = gui.window.evaluate_js(JS_SCRAPE_BUBBLES)
        return res or []
    else:
        # API mode
        msgs = load_messages()
        history = []
        for m in msgs:
            if m["phone"] == chat_name or m["name"] == chat_name:
                history.append({
                    "sender": "customer" if m["type"] == "incoming" else "me",
                    "text": m["text"]
                })
                m["read"] = True
        save_messages(msgs)
        return history[-15:]

@mcp.tool(annotations={"readOnlyHint": True})
async def send_message(chat_name: str, text: str) -> Dict[str, Any]:
    """
    Sends a WhatsApp message to a specific contact.
    Args:
        chat_name: The contact's name (for Web mode) or the phone number (for API mode).
        text: The message body text.
    """
    config = load_config()
    mode = config.get("mode", "web")

    if mode == "web":
        if not gui.window:
            return {"error": "WebView window not initialized"}
        
        # Open chat first
        if not await _ensure_active_chat(chat_name):
            return {"error": f"Failed to select contact '{chat_name}'"}

        # Trigger message send
        js_code = JS_SEND_MESSAGE.replace("{text}", text.replace('"', '\\"').replace('\n', '\\n'))
        res = gui.window.evaluate_js(js_code)
        return res or {"status": "success"}
    else:
        # API mode: call Meta Cloud API helper
        return await send_api_message(chat_name, text)

@mcp.tool(annotations={"readOnlyHint": True})
async def send_bulk_messages(chat_names: List[str], text: str) -> Dict[str, Any]:
    """
    Sends the same message text to multiple contact names or phone numbers.
    Args:
        chat_names: List of recipient contact names or phone numbers.
        text: The message body text to send.
    """
    results = {}
    for chat_name in chat_names:
        try:
            logger.info(f"Bulk Send: Sending message to {chat_name}...")
            res = await send_message(chat_name=chat_name, text=text)
            results[chat_name] = res
            # Randomized delay between bulk messages to protect account from auto-blocking on WhatsApp Web
            await asyncio.sleep(4.0)
        except Exception as e:
            logger.error(f"Bulk Send failed for {chat_name}: {e}")
            results[chat_name] = {"status": "error", "message": str(e)}
    return {"status": "completed", "results": results}

@mcp.tool(annotations={"readOnlyHint": True})
async def draft_message(chat_name: str, text: str) -> Dict[str, Any]:
    """
    Drafts a WhatsApp message to a specific contact without sending it.
    The message is left in the WhatsApp Web input box for the user to review and manually click Send.
    Args:
        chat_name: The contact's name.
        text: The message body text to draft.
    """
    config = load_config()
    mode = config.get("mode", "web")

    if mode == "web":
        if not gui.window:
            return {"error": "WebView window not initialized"}
        
        # Open chat first
        if not await _ensure_active_chat(chat_name):
            return {"error": f"Failed to select contact '{chat_name}'"}

        js_code = JS_DRAFT_MESSAGE.replace("{text}", text.replace('"', '\\"').replace('\n', '\\n'))
        res = gui.window.evaluate_js(js_code)
        return res or {"status": "success"}
    else:
        return {"error": "Drafting is not supported in API mode."}

@mcp.tool(annotations={"readOnlyHint": True})
async def update_crm_contact(chat_name: str, stage: str = None, tags: List[str] = None, notes: str = None) -> Dict[str, Any]:
    """
    Updates the local CRM data (deal stage, tags, and notes) for a specific contact.
    Args:
        chat_name: The contact's name or phone number.
        stage: The deal stage (e.g., Lead, Negotiating, Won, Lost).
        tags: List of descriptive tags for this contact.
        notes: Arbitrary notes or summaries about this contact.
    """
    crm_data = load_crm_data()
    if chat_name not in crm_data:
        crm_data[chat_name] = {"stage": "Lead", "tags": [], "notes": ""}
    
    if stage is not None:
        crm_data[chat_name]["stage"] = stage
    if tags is not None:
        crm_data[chat_name]["tags"] = tags
    if notes is not None:
        crm_data[chat_name]["notes"] = notes
        
    save_crm_data(crm_data)
    return {"status": "success", "contact": crm_data[chat_name]}

