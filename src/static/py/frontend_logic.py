from pyscript import document, window
from pyscript import when
import asyncio
from pyodide.ffi import create_proxy

tunnel_ready = window.tunnelCardVisible == "true"

@when("click", "#btn-web")
def set_mode_web(event):
    document.getElementById("mode-in").value = "web"
    
    # Toggle button active state
    web_btn = document.getElementById("btn-web")
    api_btn = document.getElementById("btn-api")
    
    web_btn.classList.add("text-white", "bg-white/5", "shadow-[0_1px_4px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.06)]")
    web_btn.classList.remove("text-zinc-400")
    
    api_btn.classList.remove("text-white", "bg-white/5", "shadow-[0_1px_4px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.06)]")
    api_btn.classList.add("text-zinc-400")
    
    document.getElementById("web-info").style.display = "block"
    document.getElementById("api-fields").style.display = "none"

@when("click", "#btn-api")
def set_mode_api(event):
    document.getElementById("mode-in").value = "api"
    
    web_btn = document.getElementById("btn-web")
    api_btn = document.getElementById("btn-api")
    
    api_btn.classList.add("text-white", "bg-white/5", "shadow-[0_1px_4px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.06)]")
    api_btn.classList.remove("text-zinc-400")
    
    web_btn.classList.remove("text-white", "bg-white/5", "shadow-[0_1px_4px_rgba(0,0,0,0.3),inset_0_1px_0_rgba(255,255,255,0.06)]")
    web_btn.classList.add("text-zinc-400")
    
    document.getElementById("web-info").style.display = "none"
    document.getElementById("api-fields").style.display = "block"

def show_guide(ev, gid):
    # Reset all tabs
    for b in document.querySelectorAll(".tb"):
        b.classList.remove("text-white", "bg-accent-dim", "border-accent/30")
        b.classList.add("text-zinc-400", "border-transparent")
    
    # Hide all guide panels
    for p in document.querySelectorAll(".gp"):
        p.classList.remove("block")
        p.classList.add("hidden")
    
    # Activate clicked tab
    ev.currentTarget.classList.add("text-white", "bg-accent-dim", "border-accent/30")
    ev.currentTarget.classList.remove("text-zinc-400", "border-transparent")
    
    # Show corresponding guide panel
    panel = document.getElementById(f"guide-{gid}")
    if panel:
        panel.classList.remove("hidden")
        panel.classList.add("block")

@when("click", ".tb")
def tab_clicked(event):
    text = event.currentTarget.innerText.lower()
    if "gemini" in text:
        show_guide(event, "gemini")
    elif "claude" in text:
        show_guide(event, "claude")
    else:
        show_guide(event, "cursor")

@when("click", "#copy-btn")
def copy_mcp_link(event):
    el = document.getElementById("mcp-link-text")
    if not el: return
    txt = el.value or el.innerText or ""
    
    async def write_clipboard():
        try:
            await window.navigator.clipboard.writeText(txt)
            btn = document.getElementById("copy-btn")
            if btn:
                original = btn.innerHTML
                btn.innerHTML = '<span class="shrink-0 flex items-center justify-center w-5 h-5 rounded-full bg-black/20 mr-2"><svg width="10" height="10" viewBox="0 0 12 12" fill="none"><path d="M10 3L5 8.5L2 5.5" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span> Copied'
                btn.classList.add("bg-emerald-600")
                
                async def reset_btn():
                    await asyncio.sleep(2.2)
                    btn.innerHTML = original
                    btn.classList.remove("bg-emerald-600")
                asyncio.ensure_future(reset_btn())
                
            toast = document.getElementById("toast")
            if toast:
                toast.classList.remove("opacity-0", "translate-y-4", "pointer-events-none")
                async def reset_toast():
                    await asyncio.sleep(2.5)
                    toast.classList.add("opacity-0", "translate-y-4", "pointer-events-none")
                asyncio.ensure_future(reset_toast())
        except Exception as e:
            print("Clipboard error:", e)
            
    asyncio.ensure_future(write_clipboard())

async def poll_tunnel():
    if tunnel_ready:
        return
    
    attempts = 0
    while attempts <= 60:
        attempts += 1
        await asyncio.sleep(3)
        try:
            resp = await window.fetch("/tunnel-status")
            data = await resp.json()
            if data and data.tunnel_url:
                window.location.reload()
                break
        except Exception as e:
            pass

# Start the poller
asyncio.ensure_future(poll_tunnel())



# Setup initial mode
current_mode = window.currentMode or "web"
if current_mode == "api":
    set_mode_api(None)
else:
    set_mode_web(None)
