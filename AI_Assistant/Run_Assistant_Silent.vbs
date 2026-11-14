Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath
Dim fso, pyExe
Set fso = CreateObject("Scripting.FileSystemObject")
If fso.FileExists(strPath & "\venv\Scripts\pythonw.exe") Then
    pyExe = strPath & "\venv\Scripts\pythonw.exe"
Else
    pyExe = "pythonw.exe"
End If
WshShell.Run """" & pyExe & """ """ & strPath & "\main.py""", 0, False
