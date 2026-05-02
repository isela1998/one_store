Set WinScriptHost = CreateObject("WScript.Shell")
WinScriptHost.Run "cmd.exe /c cd /d C:\SistemaFacturacion\app && py manage.py runserver 0.0.0.0:8000", 0
Set WinScriptHost = Nothing