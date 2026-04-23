; Inno Setup installer script for Browser Move Automation
; Targets Windows 7 SP1 and newer.

#define MyAppName "Browser Move Automation"
#define MyAppExeName "browser_move.exe"
#define MyPublisher "Browser Move Automation"

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#ifndef DistDir
  #define DistDir AddBackslash(SourcePath) + "..\dist\browser_move"
#endif

#ifndef OutputDir
  #define OutputDir AddBackslash(SourcePath) + "..\dist\installer"
#endif

[Setup]
AppId={{6B171D1C-4D62-4471-A3BF-5A2EF7F0F804}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#MyPublisher}
DefaultDirName={localappdata}\BrowserMoveAutomation
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir={#OutputDir}
OutputBaseFilename=BrowserMoveAutomation-{#AppVersion}-win7plus
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=6.1sp1
DisableProgramGroupPage=yes
ArchitecturesAllowed=x86 x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile={#AddBackslash(SourcePath) + "..\icon.ico"}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "autostart"; Description: "Start with Windows"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
Source: "{#DistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
