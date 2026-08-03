@echo off
REM Moodify demo audio push (DSK-MFY-DEMO-001)
REM Copies demo songs into the app's demo folder so the app's
REM "演示音频" section lists them directly (like WeChat files).
REM Usage: demo_push.bat "path\to\song.wav" [more.wav ...]
chcp 65001 >nul
set ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe
if not exist "%ADB%" set ADB=C:\Users\Administrator\AppData\Local\Android\Sdk\platform-tools\adb.exe
set DEST=/sdcard/Android/data/com.moodify.app/files/demo
"%ADB%" shell mkdir -p %DEST%
if "%~1"=="" (
    echo No files given. Usage: demo_push.bat song1.wav song2.wav
    exit /b 1
)
for %%F in (%*) do (
    "%ADB%" push "%%F" %DEST%
)
echo.
echo Done. Open App - 处理 - 选择音频文件, the 演示音频 section lists the songs.
