import subprocess
import sys
import os
import shutil

def main():
    print("[STEP 1/2] Compiling WhatsApp_MCP_Companion.exe binary...")
    
    cmd_app = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
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
        "--copy-metadata", "fastmcp",
        "--copy-metadata", "mcp",
        "run.py"
    ]
    
    res1 = subprocess.run(cmd_app)
    if res1.returncode != 0:
        print("[ERROR] Failed to compile main app binary.")
        sys.exit(1)
        
    app_bin_path = os.path.abspath("dist/WhatsApp_MCP_Companion.exe")
    print(f"[SUCCESS] App binary created at: {app_bin_path}")
    
    print("\n[STEP 2/2] Bundling app into WhatsApp_MCP_Setup.exe Installer...")
    
    cmd_setup = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--noconsole",
        "--name", "WhatsApp_MCP_Setup",
        "--add-data", f"{app_bin_path};.",
        "installer_gui.py"
    ]
    
    res2 = subprocess.run(cmd_setup)
    if res2.returncode == 0:
        setup_exe_path = os.path.abspath("dist/WhatsApp_MCP_Setup.exe")
        
        # Cleanup intermediate build artifacts so user gets strictly ONE installer file
        print("\n[CLEANUP] Removing intermediate build directories and payload binaries...")
        try:
            if os.path.exists("build"):
                shutil.rmtree("build")
            if os.path.exists("dist/WhatsApp_MCP_Companion.exe"):
                os.remove("dist/WhatsApp_MCP_Companion.exe")
            if os.path.exists("WhatsApp_MCP_Companion.spec"):
                os.remove("WhatsApp_MCP_Companion.spec")
            if os.path.exists("WhatsApp_MCP_Setup.spec"):
                os.remove("WhatsApp_MCP_Setup.spec")
        except Exception as e:
            print(f"[CLEANUP WARNING] {e}")

        print("\n=======================================================")
        print(" SUCCESS! Your Single 1-Click Installer is ready:")
        print(f" -> {setup_exe_path}")
        print("=======================================================")
    else:
        print("[ERROR] Failed to compile WhatsApp_MCP_Setup.exe")

if __name__ == "__main__":
    main()
