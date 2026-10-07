Option Explicit
Dim shell, fso, root, scriptPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
scriptPath = fso.BuildPath(root, "production\site_admin\launch.ps1")
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & scriptPath & """", 0, False
