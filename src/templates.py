HTML_CONFIG_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp Local MCP Setup</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #10b981;
            --primary-hover: #059669;
            --border: #334155;
        }
        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
        }
        .container {
            width: 100%;
            max-width: 600px;
            background-color: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 2.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        }
        h1 {
            font-size: 1.8rem;
            margin-top: 0;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        .subtitle {
            color: var(--text-muted);
            text-align: center;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }
        .mode-toggle {
            display: flex;
            background-color: var(--bg-color);
            padding: 0.25rem;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin-bottom: 2rem;
        }
        .mode-btn {
            flex: 1;
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 0.75rem;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .mode-btn.active {
            background-color: var(--primary);
            color: white;
        }
        .form-group {
            margin-bottom: 1.25rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            font-size: 0.9rem;
            color: var(--text-muted);
        }
        input {
            width: 100%;
            padding: 0.75rem;
            background-color: var(--bg-color);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: white;
            box-sizing: border-box;
            font-size: 0.95rem;
        }
        input:focus {
            outline: none;
            border-color: var(--primary);
        }
        .btn-submit {
            width: 100%;
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 0.85rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 1rem;
            transition: background-color 0.2s;
        }
        .btn-submit:hover {
            background-color: var(--primary-hover);
        }
        .info-card {
            background-color: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #34d399;
            padding: 1rem;
            border-radius: 8px;
            font-size: 0.9rem;
            line-height: 1.4;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>WhatsApp MCP Companion</h1>
        <div class="subtitle">Select your connection mode and configure details</div>
        
        <div class="mode-toggle">
            <button class="mode-btn" id="btn-web" onclick="setMode('web')">WhatsApp Web (QR Code)</button>
            <button class="mode-btn" id="btn-api" onclick="setMode('api')">Meta Cloud API</button>
        </div>

        <form action="/save-config" method="POST" id="config-form">
            <input type="hidden" name="mode" id="mode-input" value="web">

            <!-- WhatsApp Web Mode Helper Info -->
            <div id="web-info" class="info-card">
                <strong>WhatsApp Web Mode Active:</strong><br>
                When you click save, the window will redirect to WhatsApp Web. Scan the QR code with your phone to login. Your login session will be saved locally.
            </div>

            <!-- API Configuration Fields -->
            <div id="api-fields" style="display: none;">
                <div class="form-group">
                    <label for="meta_phone_number_id">Meta Phone Number ID</label>
                    <input type="text" name="meta_phone_number_id" id="meta_phone_number_id" value="$meta_phone_number_id">
                </div>
                <div class="form-group">
                    <label for="meta_waba_id">WhatsApp Business Account (WABA) ID</label>
                    <input type="text" name="meta_waba_id" id="meta_waba_id" value="$meta_waba_id">
                </div>
                <div class="form-group">
                    <label for="meta_access_token">System User Access Token</label>
                    <input type="password" name="meta_access_token" id="meta_access_token" value="$meta_access_token">
                </div>
                <div class="form-group">
                    <label for="webhook_verify_token">Webhook Verification Token (For Meta webhook config)</label>
                    <input type="text" name="webhook_verify_token" id="webhook_verify_token" value="$webhook_verify_token">
                </div>
                <div class="info-card" style="background-color: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.2); color: #60a5fa;">
                    <strong>Webhook Receiver:</strong><br>
                    Expose local port 8000 using ngrok and configure your webhook endpoint in Meta Developer Console pointing to: <code>https://&lt;ngrok-url&gt;/webhook</code>
                </div>
            </div>

            <!-- Ngrok Tunnel Configuration -->
            <div style="margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1.5rem;">
                <div class="form-group">
                    <label for="ngrok_auth_token">Ngrok Authtoken (Required to auto-expose public Spark App link)</label>
                    <input type="password" name="ngrok_auth_token" id="ngrok_auth_token" value="$ngrok_auth_token">
                </div>
                <div class="form-group">
                    <label for="ngrok_domain">Ngrok Custom Domain (Optional - e.g. your-domain.ngrok-free.dev)</label>
                    <input type="text" name="ngrok_domain" id="ngrok_domain" value="$ngrok_domain">
                </div>
                $tunnel_info_card
            </div>

            <button type="submit" class="btn-submit">Save & Connect</button>
        </form>
    </div>

    <script>
        const activeMode = "$current_mode" || "web";
        
        function setMode(mode) {
            document.getElementById('mode-input').value = mode;
            
            const btnWeb = document.getElementById('btn-web');
            const btnApi = document.getElementById('btn-api');
            const webInfo = document.getElementById('web-info');
            const apiFields = document.getElementById('api-fields');
            
            if (mode === 'web') {
                btnWeb.classList.add('active');
                btnApi.classList.remove('active');
                webInfo.style.display = 'block';
                apiFields.style.display = 'none';
            } else {
                btnWeb.classList.remove('active');
                btnApi.classList.add('active');
                webInfo.style.display = 'none';
                apiFields.style.display = 'block';
            }
        }
        
        // Init state
        setMode(activeMode === 'setup' ? 'web' : activeMode);

        function copyMcpLink() {
            const text = document.getElementById('mcp-link-text').innerText;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => {
                    alert('Copied link: ' + text);
                }).catch(err => {
                    fallbackCopy(text);
                });
            } else {
                fallbackCopy(text);
            }
        }
        
        function fallbackCopy(text) {
            const el = document.createElement('textarea');
            el.value = text;
            el.style.position = 'absolute';
            el.style.left = '-9999px';
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            alert('Copied link: ' + text);
        }
    </script>
</body>
</html>
"""
