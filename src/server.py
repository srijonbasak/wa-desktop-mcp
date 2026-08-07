import logging
import asyncio
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .config import load_config, save_config
from .database import load_messages, save_messages
from .templates import HTML_CONFIG_PAGE

logger = logging.getLogger("wa-desktop-mcp.server")

from .mcp_server import mcp
mcp_app = mcp.http_app(transport="streamable-http", path="/sse")

app = FastAPI(title="WhatsApp Local MCP Backend", lifespan=mcp_app.lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from string import Template

@app.get("/", response_class=HTMLResponse)
def get_home():
    from . import config as config_mod
    config = load_config()
    
    # Generate tunnel status card HTML
    tunnel_url = config_mod.PUBLIC_TUNNEL_URL
    if tunnel_url:
        tunnel_info_card = f"""
        <div class="info-card" style="background-color: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.2); color: #34d399; margin-top: 1rem;">
            <strong>Active Public Tunnel Running:</strong><br>
            Use this Custom App link in Spark/Gemini:<br>
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                <code id="mcp-link-text" style="word-break: break-all; flex-grow: 1; background: #0f172a; padding: 0.35rem 0.5rem; border-radius: 4px; border: 1px solid #334155;">{tunnel_url}/sse</code>
                <button type="button" onclick="copyMcpLink()" style="background: #10b981; border: none; color: white; padding: 0.35rem 0.75rem; border-radius: 4px; cursor: pointer; font-size: 0.85rem; font-weight: bold; white-space: nowrap;">Copy</button>
            </div>
        </div>
        """
    else:
        tunnel_info_card = """
        <div class="info-card" style="background-color: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.2); color: #fbbf24; margin-top: 1rem;">
            <strong>No Public Tunnel Active:</strong><br>
            To auto-start a public tunnel for Spark/Gemini, paste your Ngrok Authtoken below and save settings.
        </div>
        """

    tpl = Template(HTML_CONFIG_PAGE)
    return tpl.safe_substitute(
        current_mode=config.get("mode", "web"),
        meta_phone_number_id=config.get("meta_phone_number_id", ""),
        meta_waba_id=config.get("meta_waba_id", ""),
        meta_access_token=config.get("meta_access_token", ""),
        webhook_verify_token=config.get("webhook_verify_token", "wa_mcp_local_verify"),
        ngrok_auth_token=config.get("ngrok_auth_token", ""),
        ngrok_domain=config.get("ngrok_domain", ""),
        tunnel_info_card=tunnel_info_card
    )

@app.post("/save-config")
def post_save_config(
    mode: str = Form(...),
    meta_phone_number_id: str = Form(""),
    meta_waba_id: str = Form(""),
    meta_access_token: str = Form(""),
    webhook_verify_token: str = Form("wa_mcp_local_verify"),
    ngrok_auth_token: str = Form(""),
    ngrok_domain: str = Form("")
):
    config = {
        "mode": mode,
        "meta_phone_number_id": meta_phone_number_id,
        "meta_waba_id": meta_waba_id,
        "meta_access_token": meta_access_token,
        "webhook_verify_token": webhook_verify_token,
        "ngrok_auth_token": ngrok_auth_token.strip(),
        "ngrok_domain": ngrok_domain.strip()
    }
    save_config(config)
    logger.info(f"Configuration saved successfully. Mode set to: {mode}")

    # Start or restart ngrok tunnel asynchronously in the background
    from . import tunnel
    import threading
    threading.Thread(target=tunnel.start_tunnel, daemon=True).start()

    # Trigger redirect in WebView
    from . import gui
    if gui.window:
        if mode == "web":
            gui.window.load_url("https://web.whatsapp.com")
        else:
            gui.window.load_url("http://127.0.0.1:8000")

    return HTMLResponse("<h2>Config Saved! Redirecting WebView window...</h2><script>setTimeout(() => window.location.href='/', 1500)</script>")

@app.get("/webhook")
def get_webhook_verification(request: Request):
    config = load_config()
    verify_token = config.get("webhook_verify_token", "wa_mcp_local_verify")
    params = request.query_params
    mode = params.get("hub.mode")
    challenge = params.get("hub.challenge")
    token = params.get("hub.verify_token")

    if mode == "subscribe" and token == verify_token:
        logger.info("Webhook verification succeeded.")
        return HTMLResponse(challenge, media_type="text/plain")
    logger.warn("Webhook verification failed.")
    return JSONResponse(status_code=403, content={"error": "Verification failed"})

@app.post("/webhook")
async def post_webhook_events(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received webhook event: {body}")
        
        # Extract messages from Meta payload
        entry_list = body.get("entry", [])
        for entry in entry_list:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])
                
                if messages:
                    stored_messages = load_messages()
                    for idx, msg in enumerate(messages):
                        contact = contacts[idx] if idx < len(contacts) else (contacts[0] if contacts else {})
                        
                        sender_phone = msg.get("from")
                        sender_name = contact.get("profile", {}).get("name", sender_phone)
                        msg_text = msg.get("text", {}).get("body", "")
                        msg_id = msg.get("id")
                        msg_timestamp = msg.get("timestamp")

                        # Append to local message storage
                        new_msg_record = {
                            "message_id": msg_id,
                            "phone": sender_phone,
                            "name": sender_name,
                            "text": msg_text,
                            "timestamp": msg_timestamp,
                            "type": "incoming",
                            "read": False
                        }
                        stored_messages.append(new_msg_record)
                        logger.info(f"Logged new message from {sender_name}: {msg_text}")
                    save_messages(stored_messages)
        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        logger.error(f"Error processing incoming webhook: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# RFC 9728 - OAuth 2.0 Protected Resource Metadata discovery for Google validation
@app.get("/.well-known/oauth-protected-resource")
@app.get("/.well-known/oauth-protected-resource/{resource_path:path}")
def oauth_protected_resource(request: Request):
    # Dynamically resolve host from request headers
    host = request.headers.get("host", "melanie-phytographic-makhi.ngrok-free.dev")
    scheme = "https" if "ngrok-free" in host else "http"
    base_url = f"{scheme}://{host}"
    
    return JSONResponse({
        "resource": f"{base_url}/sse",
        "authorization_servers": [base_url],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["wa-desktop-mcp"]
    })

# Mock OAuth 2.0 endpoints to satisfy Google Account Linking (GAL) for Gemini Spark
@app.get("/authorize")
def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    state: str = None,
    scope: str = None
):
    logger.info(f"OAuth authorization requested. Redirecting to Google redirect_uri: {redirect_uri}")
    # Return code and preserve the state parameter exactly
    redirect_url = f"{redirect_uri}?code=mock_auth_code_123&state={state}"
    return RedirectResponse(url=redirect_url)

@app.post("/token")
async def oauth_token(request: Request):
    logger.info("OAuth token exchange requested by Google backend")
    return JSONResponse({
        "access_token": "mock_access_token_123",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "mock_refresh_token_123"
    })

@app.head("/sse")
def head_sse():
    # Return 200 OK for Google's validation HEAD requests
    return Response(status_code=200)

# Mount the FastMCP server application to FastAPI root
app.mount("/", mcp_app)
