; Script created for Crunchy
; To create a release, modify the AppVerName and OutputBaseFilename variables
;
; See http://crunchy.sourceforge.net

[Setup]
AppName=Crunchy
AppVerName=Crunchy 0.9.1
; AppPublisher=
AppPublisherURL=http://crunchy.sourceforge.net
VersionInfoVersion=0.9.1
AppSupportURL=http://crunchy.sourceforge.net
AppUpdatesURL=http://crunchy.sourceforge.net
DefaultDirName={pf}\Crunchy
DefaultGroupName=Crunchy
DisableProgramGroupPage=no
LicenseFile=LICENSE.txt
; InfoBeforeFile=README.txt
OutputDir=.
OutputBaseFilename=crunchy-0.9.1-setup
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[INI]
Filename: "{app}\crunchy.url"; Section: "InternetShortcut"; Key: "URL"; String: "http://crunchy.sourceforge.net"

[Icons]
Name: "{group}\Crunchy"; WorkingDir: "{app}"; Filename: "{app}\crunchy.exe"
Name: "{group}\{cm:ProgramOnTheWeb,Crunchy}"; Filename: "{app}\crunchy.url"
Name: "{group}\{cm:UninstallProgram,Crunchy}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Crunchy"; WorkingDir: "{app}"; Filename: "{app}\crunchy.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\crunchy.exe"; Description: "{cm:LaunchProgram,Crunchy}"; Flags: shellexec postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\crunchy.url"
