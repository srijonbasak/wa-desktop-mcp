import threading
import logging
import uvicorn
from src.server import app
from src.gui import start_gui

# Initialize logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("wa-desktop-mcp.bootstrap")

def start_fastapi():
    logger.info("Starting background FastAPI server on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def main():
    # 1. Start FastAPI server thread
    server_thread = threading.Thread(target=start_fastapi, daemon=True)
    server_thread.start()

    # (Settings button is now injected via window.events.loaded in gui.py)

    # 3. Start the embedded ngrok tunnel if configured
    from src.tunnel import start_tunnel, stop_tunnel
    start_tunnel()

    # 4. Launch PyWebView window wrapper (blocking main GUI thread)
    try:
        start_gui()
    finally:
        logger.info("Application shutting down, releasing active tunnels...")
        stop_tunnel()

if __name__ == "__main__":
    main()
