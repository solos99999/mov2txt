@echo off
echo Video to Text Tool - Final Solution
echo ===================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import moviepy, speech_recognition, vosk" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install moviepy SpeechRecognition vosk
    if errorlevel 1 (
        echo Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Enter video file path:
set /p video_path=

if "%video_path%"=="" (
    echo Please enter video file path
    pause
    exit /b 1
)

if not exist "%video_path%" (
    echo File not found: %video_path%
    pause
    exit /b 1
)

echo.
echo Choose mode:
echo 1. Auto (recommended)
echo 2. Online only
echo 3. Offline only
echo.
set /p mode_choice=Enter choice (1-3): 

if "%mode_choice%"=="1" set mode=auto
if "%mode_choice%"=="2" set mode=online
if "%mode_choice%"=="3" set mode=offline
if "%mode%"=="" (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo Processing video: %video_path%
echo Mode: %mode%
echo.

python final_solution.py "%video_path%" --mode %mode%

echo.
echo Processing completed!
pause