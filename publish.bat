@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo.
echo ============================================================
echo   TgtoDrive Plugins - Publish All
echo   package plugins / refresh plugins.json / commit + push
echo ============================================================
echo.

rem ------------------------------------------------------------
rem  1. locate Python (py launcher -> python -> bundled runtime)
rem     NOTE: keep this file ASCII-only. cmd.exe parses .bat files
rem     using the system ANSI code page, so UTF-8 Chinese here would
rem     break the script. All human-readable output comes from
rem     scripts/publish_all.py instead.
rem ------------------------------------------------------------
set "PYTHON_EXE="
where py >nul 2>nul && set "PYTHON_EXE=py -3"
if defined PYTHON_EXE goto :python_ready
where python >nul 2>nul && set "PYTHON_EXE=python"
if defined PYTHON_EXE goto :python_ready
if exist "%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe" set "PYTHON_EXE=%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if defined PYTHON_EXE goto :python_ready
echo [ERROR] Python not found. Install Python 3.9+ and add it to PATH.
goto :failed

:python_ready
echo Python: %PYTHON_EXE%

rem ------------------------------------------------------------
rem  2. check git
rem ------------------------------------------------------------
where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] git not found. Install Git for Windows and add it to PATH.
  goto :failed
)

rem ------------------------------------------------------------
rem  3. run the publish script (arguments are passed through,
rem     e.g.  publish.bat -m "message"  /  publish.bat --no-push)
rem ------------------------------------------------------------
%PYTHON_EXE% "scripts\publish_all.py" %*
if errorlevel 1 goto :failed

echo.
echo Done.
pause
exit /b 0

:failed
echo.
echo Failed. See the messages above.
pause
exit /b 1
