[Setup]
AppName=WhatsApp MCP Companion
AppVersion=1.0.0
AppPublisher=Srijon Basak
AppCopyright=Copyright (C) 2026 Srijon Basak
DefaultDirName={autopf}\WhatsApp MCP Companion
DefaultGroupName=WhatsApp MCP Companion
UninstallDisplayIcon={app}\WhatsApp_MCP_Companion.exe
Compression=lzma2
SolidCompression=yes
OutputDir=builds
OutputBaseFilename=WhatsApp_MCP_Setup
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist\WhatsApp_MCP_Companion\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\WhatsApp MCP Companion"; Filename: "{app}\WhatsApp_MCP_Companion.exe"
Name: "{autodesktop}\WhatsApp MCP Companion"; Filename: "{app}\WhatsApp_MCP_Companion.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WhatsApp_MCP_Companion.exe"; Description: "Launch WhatsApp MCP Companion"; Flags: nowait postinstall skipifsilent
