import os
import sys
import shutil
import winreg
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

APP_NAME = "WhatsApp MCP Companion"
APP_DIR_NAME = "WhatsApp MCP Companion"
EXE_NAME = "WhatsApp_MCP_Companion.exe"

def get_install_dir():
    local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    return os.path.join(local_app_data, "Programs", APP_DIR_NAME)

def create_shortcut(target_path, shortcut_path, description=""):
    """Uses PowerShell to create a native Windows .lnk shortcut."""
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
    """Registers app in Windows Add/Remove Programs (Control Panel & Settings)."""
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
        print("Registry warning:", e)

class SetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} Setup")
        self.root.geometry("540x360")
        self.root.resizable(False, False)
        
        # Color Palette - Professional Slate & Emerald Theme
        self.bg_color = "#0b0f19"       # Deep slate black
        self.card_color = "#161e2e"     # Dark card background
        self.border_color = "#273549"   # Subtle slate border
        self.accent_color = "#059669"   # Production Emerald green
        self.accent_hover = "#047857"   # Hover state
        self.fg_color = "#f8fafc"       # High contrast text
        self.muted_color = "#94a3b8"    # Muted secondary text
        
        self.root.configure(bg=self.bg_color)
        self.install_dir = get_install_dir()
        
        # Apply TTK styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Emerald.Horizontal.TProgressbar", 
                             troughcolor="#1e293b", 
                             background="#10b981", 
                             thickness=8, 
                             borderwidth=0)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Top Header Banner
        header_frame = tk.Frame(self.root, bg=self.card_color, height=80, highlightthickness=1, highlightbackground=self.border_color)
        header_frame.pack(fill="x", side="top")
        
        header_container = tk.Frame(header_frame, bg=self.card_color)
        header_container.pack(fill="both", expand=True, padx=24, pady=16)
        
        # App Badge / Icon
        badge_label = tk.Label(header_container, text="💬", font=("Segoe UI Emoji", 24), bg=self.card_color)
        badge_label.pack(side="left", padx=(0, 14))
        
        text_container = tk.Frame(header_container, bg=self.card_color)
        text_container.pack(side="left", fill="y")
        
        title_label = tk.Label(text_container, text=APP_NAME, font=("Segoe UI", 13, "bold"), bg=self.card_color, fg=self.fg_color)
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(text_container, text="Desktop Companion & Headless AI CRM Server", font=("Segoe UI", 9), bg=self.card_color, fg=self.muted_color)
        subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Main Form Body
        self.body_frame = tk.Frame(self.root, bg=self.bg_color)
        self.body_frame.pack(fill="both", expand=True, padx=24, pady=20)
        
        dir_label = tk.Label(self.body_frame, text="Installation Location", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg=self.fg_color)
        dir_label.pack(anchor="w", pady=(0, 6))
        
        dir_frame = tk.Frame(self.body_frame, bg=self.bg_color)
        dir_frame.pack(fill="x", pady=(0, 16))
        
        dir_entry = tk.Entry(dir_frame, font=("Segoe UI", 9), bg="#1e293b", fg=self.fg_color, relief="flat", highlightthickness=1, highlightbackground=self.border_color, insertbackground="white")
        dir_entry.insert(0, self.install_dir)
        dir_entry.config(state="readonly")
        dir_entry.pack(fill="x", ipady=7)
        
        self.progress_label = tk.Label(self.body_frame, text="Ready to install. Click 'Install Application' to begin.", font=("Segoe UI", 9), bg=self.bg_color, fg=self.muted_color)
        self.progress_label.pack(anchor="w", pady=(0, 6))
        
        self.progress_bar = ttk.Progressbar(self.body_frame, style="Emerald.Horizontal.TProgressbar", mode="determinate", maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 16))
        
        # Checkbox
        self.launch_var = tk.BooleanVar(value=True)
        self.launch_chk = tk.Checkbutton(self.body_frame, text="Launch WhatsApp MCP Companion automatically after setup", variable=self.launch_var, bg=self.bg_color, fg=self.fg_color, selectcolor=self.card_color, activebackground=self.bg_color, activeforeground=self.fg_color, font=("Segoe UI", 9), cursor="hand2")
        self.launch_chk.pack(anchor="w")
        
        # Action Buttons Footer
        footer_frame = tk.Frame(self.root, bg=self.bg_color)
        footer_frame.pack(fill="x", side="bottom", padx=24, pady=(0, 20))
        
        self.install_btn = tk.Button(footer_frame, text="Install Application", font=("Segoe UI", 9, "bold"), bg=self.accent_color, fg="white", activebackground=self.accent_hover, activeforeground="white", relief="flat", padx=22, pady=7, cursor="hand2", command=self.start_installation)
        self.install_btn.pack(side="right")
        
        self.cancel_btn = tk.Button(footer_frame, text="Cancel", font=("Segoe UI", 9), bg="#334155", fg="white", activebackground="#475569", activeforeground="white", relief="flat", padx=16, pady=7, cursor="hand2", command=self.root.quit)
        self.cancel_btn.pack(side="right", padx=(0, 10))

    def start_installation(self):
        self.install_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        self.root.after(100, self.perform_install)

    def perform_install(self):
        try:
            self.progress_label.config(text="Creating installation directory...")
            self.progress_bar["value"] = 20
            self.root.update()
            
            os.makedirs(self.install_dir, exist_ok=True)
            
            # Locate bundled payload binary
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            src_exe = os.path.join(base_dir, EXE_NAME)
            target_exe = os.path.join(self.install_dir, EXE_NAME)
            
            if not os.path.exists(src_exe):
                # Fallback check dist directory during testing
                alt_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", EXE_NAME)
                if os.path.exists(alt_exe):
                    src_exe = alt_exe
                else:
                    raise FileNotFoundError(f"Bundled binary '{EXE_NAME}' not found in setup package.")

            self.progress_label.config(text="Copying application binaries...")
            self.progress_bar["value"] = 50
            self.root.update()
            
            shutil.copy2(src_exe, target_exe)
            
            self.progress_label.config(text="Creating Start Menu & Desktop shortcuts...")
            self.progress_bar["value"] = 80
            self.root.update()
            
            # Desktop Shortcut
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", f"{APP_NAME}.lnk")
            create_shortcut(target_exe, desktop_path, "WhatsApp Desktop Companion & MCP Server")
            
            # Start Menu Shortcut
            start_menu_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
            if os.path.exists(start_menu_dir):
                start_menu_lnk = os.path.join(start_menu_dir, f"{APP_NAME}.lnk")
                create_shortcut(target_exe, start_menu_lnk, "WhatsApp Desktop Companion & MCP Server")

            self.progress_label.config(text="Registering Windows application integration...")
            register_uninstall(self.install_dir, target_exe)
            
            self.progress_bar["value"] = 100
            self.progress_label.config(text="Installation finished successfully!")
            self.root.update()
            
            if self.launch_var.get():
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                subprocess.Popen([target_exe], cwd=self.install_dir, creationflags=flags, close_fds=True)
                
            self.root.after(500, self.root.destroy)
            
        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred during setup:\n{str(e)}")
            self.install_btn.config(state="normal")
            self.cancel_btn.config(state="normal")

def main():
    root = tk.Tk()
    app = SetupWizard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
