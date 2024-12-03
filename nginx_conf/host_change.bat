@echo off
cd /d "%windir%\system32\drivers\etc"

REM Создать резервную копию файла hosts
copy hosts hosts.bak

Call :GetLocalIP
Call :GrantAccess hosts
attrib -R -S -H hosts
echo %LocalIP% brain-flow.com>>hosts
attrib +R +S +H hosts
pause
goto :eof

:GetLocalIP
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4 Address"') do set LocalIP=%%i
set LocalIP=%LocalIP:~1%
goto :eof

:GrantAccess
takeown /f "%~1"
echo y|cacls "%~1" /g %username%:f
exit /b
