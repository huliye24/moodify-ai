@echo off
REM Moodify demo USB bridge (DSK-MFY-DEMO-001)
REM Forwards phone 127.0.0.1:8000 -> PC 8000 so the app reaches the API
REM over USB with no firewall/LAN config.
chcp 65001 >nul
set ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
if not exist "%ADB%" set ADB=C:\Users\Administrator\AppData\Local\Android\Sdk\platform-tools\adb.exe
"%ADB%" reverse tcp:8000 tcp:8000
"%ADB%" devices
echo.
echo Phone can now reach the API at http://127.0.0.1:8000
