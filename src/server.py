import logging
import asyncio
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from .config import load_config, save_config
from .database import load_messages, save_messages


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

from fastapi.templating import Jinja2Templates
import pathlib
from fastapi.staticfiles import StaticFiles

_src_dir = pathlib.Path(__file__).resolve().parent
_asset_dir = _src_dir.parent / "asset"
if _asset_dir.is_dir():
    app.mount("/asset", StaticFiles(directory=str(_asset_dir)), name="asset")

_static_dir = _src_dir / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

templates = Jinja2Templates(directory=str(_src_dir / "templates"))

@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    from . import config as config_mod
    config = load_config()
    
    # Generate tunnel status card HTML
    tunnel_url = config_mod.PUBLIC_TUNNEL_URL
    if tunnel_url:
        tunnel_info_card = f"""
        <div class="bg-accent/5 border border-accent/30 rounded-2xl p-1 mb-7 shadow-[0_0_24px_rgba(16,185,129,0.08),inset_0_1px_0_rgba(255,255,255,0.05)] transition-shadow duration-500">
            <div class="bg-canvas border border-white/5 rounded-[14px] p-5 shadow-[inset_0_1px_4px_rgba(0,0,0,0.5)]">
                <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
                    <span class="text-[11px] font-bold tracking-[0.1em] uppercase text-zinc-400">Public MCP SSE Endpoint</span>
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-mono text-[10px] font-semibold tracking-wide shadow-[0_0_12px_rgba(16,185,129,0.15)]">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Connected
                    </span>
                </div>
                <div class="flex flex-col sm:flex-row items-stretch gap-2">
                    <input type="text" readonly id="mcp-link-text" class="flex-1 bg-surface-3 border border-white/10 rounded-xl px-4 py-3 font-mono text-[13px] text-emerald-300 shadow-[inset_0_2px_4px_rgba(0,0,0,0.2)] focus:outline-none min-w-0 text-ellipsis whitespace-nowrap" value="{tunnel_url}/sse">
                    <button type="button" id="copy-btn" class="inline-flex items-center justify-center gap-2 bg-accent text-white border-none rounded-xl px-4 py-3 font-sans text-sm font-semibold cursor-pointer whitespace-nowrap shadow-[inset_0_1px_0_rgba(255,255,255,0.2),0_2px_8px_rgba(16,185,129,0.3)] hover:bg-accent-hover hover:shadow-[0_4px_12px_rgba(16,185,129,0.4)] hover:-translate-y-px active:translate-y-px active:scale-[0.98] transition-all">
                        <span class="shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-black/15 group-hover:translate-x-px group-hover:scale-105 transition-transform"><svg width="12" height="12" viewBox="0 0 24 24" fill="none"><rect x="9" y="9" width="13" height="13" rx="2" stroke="#fff" stroke-width="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="#fff" stroke-width="2"/></svg></span> Copy URL
                    </button>
                    <button type="button" onclick="fetch('/tunnel-disconnect', {{method: 'POST'}}).then(() => window.location.reload())" class="inline-flex items-center justify-center gap-2 bg-red-500/10 text-red-400 border border-red-500/20 rounded-xl px-4 py-3 font-sans text-sm font-semibold cursor-pointer whitespace-nowrap hover:bg-red-500/20 hover:text-red-300 hover:border-red-500/30 active:scale-[0.98] transition-all">
                        Disconnect
                    </button>
                </div>
            </div>
        </div>
        """
        tunnel_card_visible = "true"
    else:
        tunnel_info_card = """
        <div class="bg-surface-3/50 border border-white/5 rounded-2xl p-1 mb-7 transition-shadow duration-500" id="ep-waiting">
            <div class="bg-canvas border border-white/5 rounded-[14px] p-5 shadow-[inset_0_1px_4px_rgba(0,0,0,0.5)]">
                <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
                    <span class="text-[11px] font-bold tracking-[0.1em] uppercase text-zinc-500">Public MCP SSE Endpoint</span>
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 font-mono text-[10px] font-semibold tracking-wide shadow-[0_0_12px_rgba(239,68,68,0.1)]">
                        <span class="w-1.5 h-1.5 rounded-full bg-red-500"></span> Disconnected
                    </span>
                </div>
                <div class="flex flex-col sm:flex-row items-stretch gap-2">
                    <input type="text" readonly id="mcp-link-text" class="flex-1 bg-surface-3/50 border border-white/5 rounded-xl px-4 py-3 font-mono text-[13px] text-zinc-500 shadow-inner focus:outline-none min-w-0 text-ellipsis whitespace-nowrap" value="Waiting for configuration...">
                    <button type="button" disabled class="inline-flex items-center justify-center gap-2 bg-zinc-800 text-zinc-500 border border-transparent rounded-xl px-4 py-3 font-sans text-sm font-semibold cursor-not-allowed whitespace-nowrap">
                        <span class="shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-black/20"><svg width="12" height="12" viewBox="0 0 24 24" fill="none"><rect x="9" y="9" width="13" height="13" rx="2" stroke="currentColor" stroke-width="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" stroke="currentColor" stroke-width="2"/></svg></span> Copy URL
                    </button>
                </div>
            </div>
        </div>
        """
        tunnel_card_visible = "false"

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "current_mode": config.get("mode", "web"),
            "meta_phone_number_id": config.get("meta_phone_number_id", ""),
            "meta_waba_id": config.get("meta_waba_id", ""),
            "meta_access_token": config.get("meta_access_token", ""),
            "webhook_verify_token": config.get("webhook_verify_token", "wa_mcp_local_verify"),
            "tunnel_info_card": tunnel_info_card,
            "tunnel_card_visible": tunnel_card_visible,
            "meta_client_id": config.get("meta_client_id", ""),
            "meta_client_secret": config.get("meta_client_secret", ""),
            "ngrok_auth_token": config.get("ngrok_auth_token", ""),
            "ngrok_domain": config.get("ngrok_domain", "")
        }
    )

@app.get("/tunnel-status")
def get_tunnel_status():
    """Returns current tunnel URL for frontend auto-update polling."""
    from . import config as config_mod
    url = config_mod.PUBLIC_TUNNEL_URL
    return JSONResponse({"tunnel_url": f"{url}/sse" if url else None})

@app.post("/tunnel-disconnect")
def post_tunnel_disconnect():
    """Manually disconnects the running ngrok tunnel."""
    from . import tunnel
    tunnel.stop_tunnel()
    return JSONResponse({"status": "disconnected"})

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
            gui.window.load_url("http://127.0.0.1:48211")

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
