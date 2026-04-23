; Inno Setup installer script for ScreenHop
; Targets Windows 7 SP1 and newer.

#define MyAppName "ScreenHop"
#define MyAppExeName "ScreenHop.exe"

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

#ifndef AppPublisher
  #define AppPublisher "ScreenHop"
#endif

#ifndef DistDir
  #define DistDir AddBackslash(SourcePath) + "..\dist\ScreenHop"
#endif

#ifndef OutputDir
  #define OutputDir AddBackslash(SourcePath) + "..\dist\installer"
#endif

[Setup]
; Keep the existing AppId so ScreenHop upgrades prior Browser Move builds cleanly.
AppId={{6B171D1C-4D62-4471-A3BF-5A2EF7F0F804}
AppName={#MyAppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\ScreenHop
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir={#OutputDir}
OutputBaseFilename=ScreenHop-{#AppVersion}-win7plus
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
