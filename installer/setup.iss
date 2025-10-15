[Setup]
AppName=AluguelFácil
AppVersion=1.0
DefaultDirName={autopf}\AluguelFacil
DefaultGroupName=AluguelFácil
OutputDir=Output
OutputBaseFilename=AluguelFacil_Instalador
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "AluguelFacil.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\AluguelFácil"; Filename: "{app}\AluguelFacil.exe"
Name: "{autodesktop}\AluguelFácil"; Filename: "{app}\AluguelFacil.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AluguelFacil.exe"; Description: "Executar AluguelFácil"; Flags: postinstall nowait skipifsilent