import subprocess
import sys
import os

def build():
    print("[BUILD] Installing PyInstaller in current environment...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    print("[BUILD] Compiling wa-desktop-mcp into standalone WhatsApp_MCP_Companion...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",  # Recommended for fast startup with PyWebView and web assets
        "--name", "WhatsApp_MCP_Companion",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols",
        "--hidden-import", "uvicorn.protocols.http",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.lifespan",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "fastmcp",
        "--hidden-import", "webview",
        "run.py"
    ]
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("\n[SUCCESS] Build succeeded! Executable folder created at:")
        print(os.path.abspath("dist/WhatsApp_MCP_Companion"))
    else:
        print("\n[ERROR] Build failed with exit code:", res.returncode)

if __name__ == "__main__":
    build()
