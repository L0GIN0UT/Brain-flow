@echo off
cd /d "%windir%\system32\drivers\etc"

attrib -R -S -H hosts

REM Удалить текущий файл hosts
del hosts

REM Восстановить файл hosts из резервной копии
rename hosts.bak hosts

attrib +R +S +H hosts

pause
