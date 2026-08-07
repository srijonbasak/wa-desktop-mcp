import os
import sys
import shutil
import winreg
import subprocess

APP_NAME = "WhatsApp MCP Companion"
APP_DIR_NAME = "WhatsApp MCP Companion"
EXE_NAME = "WhatsApp_MCP_Companion.exe"

def get_install_dir():
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    return os.path.join(local_app_data, "Programs", APP_DIR_NAME)

def create_shortcut(target_path, shortcut_path, description=""):
    ps_command = f"""
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
    $Shortcut.TargetPath = '{target_path}'
    $Shortcut.WorkingDirectory = '{os.path.dirname(target_path)}'
    $Shortcut.Description = '{description}'
    $Shortcut.Save()
    """
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

def register_uninstall(install_dir, exe_path):
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\WhatsAppMCPCompanion"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Srijon Basak")
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
    except Exception as e:
        print("[WARNING] Could not register uninstall key:", e)

def install():
    print("==================================================")
    print("      Installing WhatsApp MCP Companion")
    print("==================================================")
    
    install_dir = get_install_dir()
    print(f"[1/4] Target Directory: {install_dir}")
    os.makedirs(install_dir, exist_ok=True)
    
    # 1. Compile --onedir bundle into target directory directly
    print("[2/4] Building production application folder...")
    cmd_app = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--noconsole",
        "--distpath", install_dir,
        "--name", "app",
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
    
    subprocess.run(cmd_app, check=True)
    
    # Move files from install_dir/app to install_dir
    app_folder = os.path.join(install_dir, "app")
    target_exe = os.path.join(install_dir, EXE_NAME)
    
    if os.path.exists(app_folder):
        for item in os.listdir(app_folder):
            src_item = os.path.join(app_folder, item)
            dst_item = os.path.join(install_dir, "app.exe" if item == "app.exe" else item)
            if os.path.exists(dst_item):
                if os.path.isdir(dst_item):
                    shutil.rmtree(dst_item)
                else:
                    os.remove(dst_item)
            shutil.move(src_item, dst_item)
        os.rmdir(app_folder)
        
        # Rename app.exe -> WhatsApp_MCP_Companion.exe
        old_exe = os.path.join(install_dir, "app.exe")
        if os.path.exists(old_exe):
            if os.path.exists(target_exe):
                os.remove(target_exe)
            os.rename(old_exe, target_exe)

    # 2. Create Shortcuts
    print("[3/4] Creating Desktop & Start Menu shortcuts...")
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{APP_NAME}.lnk")
    create_shortcut(target_exe, desktop_path, "WhatsApp Desktop Companion & MCP Server")
    
    start_menu_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
    if os.path.exists(start_menu_dir):
        start_menu_lnk = os.path.join(start_menu_dir, f"{APP_NAME}.lnk")
        create_shortcut(target_exe, start_menu_lnk, "WhatsApp Desktop Companion & MCP Server")

    # 3. Register System Integration
    print("[4/4] Registering in Windows Add/Remove Programs...")
    register_uninstall(install_dir, target_exe)
    
    # Cleanup build artifacts
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
    if os.path.exists("app.spec"):
        os.remove("app.spec")

    print("\n==================================================")
    print(" SUCCESS! Installed into system successfully!")
    print(f" Executable: {target_exe}")
    print(" Shortcuts created on Desktop and Start Menu.")
    print("==================================================")

if __name__ == "__main__":
    install()
