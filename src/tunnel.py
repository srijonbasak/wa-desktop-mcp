import logging
import time
from pyngrok import ngrok
from . import config

logger = logging.getLogger("wa-desktop-mcp.tunnel")

# Store active ngrok tunnel object reference
active_tunnel = None

def start_tunnel():
    """
    Configures and starts the embedded Ngrok tunnel on port 8000.
    Stores the public URL in config.PUBLIC_TUNNEL_URL.
    """
    global active_tunnel
    conf = config.load_config()
    token = conf.get("ngrok_auth_token", "").strip()
    
    # Always stop any existing active tunnel before starting a new one
    stop_tunnel()
    
    if not token:
        logger.info("No Ngrok Authtoken configured. Skipping embedded tunnel.")
        config.PUBLIC_TUNNEL_URL = ""
        return
        
    try:
        logger.info("Initializing Ngrok authtoken...")
        ngrok.set_auth_token(token)
        
        logger.info("Starting HTTP tunnel on port 8000...")
        domain = conf.get("ngrok_domain", "").strip()
        if domain:
            # Strip protocol prefix if pasted
            domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
            logger.info(f"Binding tunnel to custom domain: {domain}")
            active_tunnel = ngrok.connect(8000, domain=domain)
        else:
            active_tunnel = ngrok.connect(8000)
            
        config.PUBLIC_TUNNEL_URL = active_tunnel.public_url
        logger.info(f"Ngrok tunnel established successfully. Public URL: {config.PUBLIC_TUNNEL_URL}")
    except Exception as e:
        logger.error(f"Failed to establish Ngrok tunnel: {e}")
        config.PUBLIC_TUNNEL_URL = ""

def stop_tunnel():
    """
    Kills the running Ngrok tunnel and releases system process.
    """
    global active_tunnel
    if active_tunnel:
        try:
            logger.info("Disconnecting Ngrok tunnel...")
            ngrok.disconnect(active_tunnel.public_url)
            ngrok.kill()
        except Exception as e:
            logger.error(f"Error while disconnecting Ngrok: {e}")
        active_tunnel = None
        config.PUBLIC_TUNNEL_URL = ""
