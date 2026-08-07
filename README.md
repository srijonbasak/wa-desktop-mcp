# 🚀 WhatsApp Desktop MCP & Headless AI CRM Companion

> An all-in-one local desktop companion that connects your WhatsApp Web directly to Google Gemini, Claude, Cursor, and other AI tools over the **Model Context Protocol (MCP)**. Features an **invisible local AI CRM** with automated pipeline tracking and a human-in-the-loop "Draft & Approve" workflow.

---

## ✨ Features

- 📱 **Zero API Key Setup**: Uses an embedded PyWebView browser wrapper to log in to WhatsApp Web directly. No Meta Cloud API setup or paid developer keys required!
- 🤖 **Headless AI CRM**: Automatically tracks contacts, tags, and deal stages (`Lead` -> `Negotiating` -> `Won`) in a local, private JSON database (`crm.json`).
- ✍️ **Draft & Approve Workflow**: AI can draft intelligent responses directly inside your WhatsApp Web chat input box without hitting send. You retain 100% control to review and approve with one click.
- ⚡ **High Context Density**: The `read_chats` tool automatically attaches CRM tags, notes, and pipeline stages in one single request—minimizing tool calling overhead.
- 🌐 **Remote Tunnel Integration**: Built-in `ngrok` tunneling for connecting external AI models securely via HTTPS / Server-Sent Events (SSE).
- 🔒 **100% Local & Private**: All session cookies, message logs, and CRM data remain strictly on your local computer (`.wa_session/`).

---

## 🛠️ How to Work & Installation

### Option A: 1-Click Windows Setup Installer (Recommended)

1. Download `WhatsApp_MCP_Setup.exe` from the [Releases](https://github.com/your-username/wa-desktop-mcp/releases) page.
2. Double-click `WhatsApp_MCP_Setup.exe` to launch the Setup Wizard.
3. Click **Install Now**. The installer will automatically:
   - Install the application to `%LOCALAPPDATA%\Programs\WhatsApp MCP Companion`.
   - Create a **Desktop Shortcut** (`WhatsApp MCP Companion`).
   - Create a **Start Menu Entry** in Windows Start Menu.
   - Register the application in Windows Settings (Add/Remove Programs).
4. On launch, log in to WhatsApp Web by scanning the QR code with your phone. Your companion server will start running locally at `http://127.0.0.1:8000`.

### Option B: Running from Source (Developer Setup)

#### Prerequisites
- **Python 3.10+** installed on Windows.

#### Installation Steps
```bash
# 1. Clone the repository
git clone https://github.com/your-username/wa-desktop-mcp.git
cd wa-desktop-mcp

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Launch the companion app
python run.py
```

---

## 🔌 Connecting to Gemini / Claude / Cursor

### 1. Connecting via SSE Endpoint
In your MCP client settings (e.g. Gemini, Claude Desktop, or Cursor):
- **Transport Type**: `sse`
- **Server URL**: `http://127.0.0.1:8000/sse` (or your public ngrok URL if using remote tunneling).

---

## 🛠️ Available MCP Tools

| Tool Name | Type | Description |
|---|---|---|
| `read_chats` | Read | Lists active WhatsApp chats merged with local CRM deal stages and tags. |
| `get_chat_history` | Read | Scrapes the last 15 messages in the chat history for a specific contact. |
| `draft_message` | Write (Draft) | Types an AI-generated reply into the WhatsApp input box without sending it (Approve flow). |
| `send_message` | Write (Instant) | Sends a message directly to a target contact or phone number. |
| `send_bulk_messages` | Write (Bulk) | Sends rate-limited bulk messages across multiple recipients. |
| `update_crm_contact` | CRM | Updates a contact's deal stage (`Lead`, `Negotiating`, `Won`), tags, or notes in `crm.json`. |

---

## 📜 Building the Executable (.exe)

To compile the application into a single standalone `.exe` for distribution:

```bash
# 1. Install PyInstaller inside your virtual environment
pip install pyinstaller

# 2. Run the build script
python build_exe.py
```
The standalone executable will be generated at `dist/WhatsApp_MCP_Companion.exe`.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](./LICENSE) for more details.
