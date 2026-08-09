import os
import subprocess
import sys
from pathlib import Path

def main():
    root_dir = Path(__file__).parent
    
    print("Starting PyInstaller Build (--onedir)...")
    
    # Run PyInstaller to build --onedir
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "WhatsApp_MCP_Companion",
        "--windowed",  # No console
        "--noconfirm", # Overwrite output
        "--onedir",    # Output as a directory (needed for InnoSetup later)
        "--icon", "asset/logo.ico",
        "--add-data", f"src/templates{os.pathsep}src/templates",
        "--add-data", f"src/static{os.pathsep}src/static",
        "--add-data", f"asset{os.pathsep}asset",
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
        "--copy-metadata", "fastmcp",
        "--copy-metadata", "mcp",
        str(root_dir / "run.py")
    ]
    
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("PyInstaller build complete!")
    
    # Check if ISCC is installed and run Inno Setup if found
    iscc_paths = [
        r"C:\Users\Srijon\AppData\Local\Programs\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    ]
    
    iscc_bin = None
    for path in iscc_paths:
        if os.path.exists(path):
            iscc_bin = path
            break
            
    if iscc_bin:
        print(f"Found Inno Setup Compiler at: {iscc_bin}")
        print("Compiling setup.iss into builds/WhatsApp_MCP_Setup.exe...")
        subprocess.run([iscc_bin, "setup.iss"], check=True)
        print("Inno Setup compilation complete! Output: builds/WhatsApp_MCP_Setup.exe")
    else:
        print("\n[NOTE] Inno Setup Compiler (ISCC.exe) not found in standard paths.")
        print("To generate builds/WhatsApp_MCP_Setup.exe like yolo_editor, compile setup.iss using Inno Setup!")

if __name__ == "__main__":
    main()
