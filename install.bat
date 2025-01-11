@echo off

:: Check if Python is installed
python --version >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python from the official website:
    echo https://www.python.org/downloads/
    pause
    exit /b
)

:: Install required libraries
echo Installing required libraries...
pip install pycryptodome pyperclip pywin32 pillow pycountry pyzipper psutil requests cryptography base64 pyinstaller

:: Run the setup.py script
python setup.py

:: Wait until script.py is created
echo Waiting for script.py to be created...
:waitForFile
if exist script.py (
    echo Found script.py, opening it...
    start script.py
    exit /b
) else (
    timeout /t 2 >nul
    goto waitForFile
)

cls
