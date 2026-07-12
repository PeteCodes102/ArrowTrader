Set shell = CreateObject("WScript.Shell")
currentDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
pythonExe = currentDir & "\.venv\Scripts\pythonw.exe"
scriptPath = currentDir & "\run_tradovate.py"

If Not CreateObject("Scripting.FileSystemObject").FileExists(pythonExe) Then
    pythonExe = "pythonw.exe"
End If

shell.CurrentDirectory = currentDir
shell.Run Chr(34) & pythonExe & Chr(34) & " " & Chr(34) & scriptPath & Chr(34), 0, False
