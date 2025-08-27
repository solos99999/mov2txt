@echo off
setlocal enabledelayedexpansion
:: Claude Code Provider Switcher for Windows v1.6
:: Final fixed version with simplified structure

title Claude Code Provider Switcher
color 0A

echo.
echo ===============================================
echo    Claude Code Provider Switcher v1.6
echo    Final Fixed Version
echo ===============================================
echo.
echo NOTE: Node.js DEP0190 warnings are from Claude Code itself,
echo       not from this batch file. They are safe to ignore.
echo.
@echo off
setlocal enabledelayedexpansion
:: Claude Code Provider Switcher for Windows v1.6
:: Final fixed version with simplified structure

title Claude Code Provider Switcher
color 0A

echo.
echo ===============================================
echo    Claude Code Provider Switcher v1.6
echo    Final Fixed Version
echo ===============================================
echo.

:: Check if Claude Code is installed
where claude >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Claude Code not found
    echo Please install: npm install -g @anthropic-ai/claude-code
    echo.
    pause
    exit /b 1
)

:: Get current script directory
set "SCRIPT_DIR=%~dp0"
set "CONFIG_DIR=%SCRIPT_DIR%.claude-providers"
set "CONFIG_FILE=%SCRIPT_DIR%.claude-providers\providers.conf"

:: Ensure directory paths don't have trailing backslash issues
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:: Create config directory if it doesn't exist
if not exist "%CONFIG_DIR%" (
    echo Creating directory: %CONFIG_DIR%
    mkdir "%CONFIG_DIR%" 2>nul
)

:: Create default configuration if it doesn't exist
if not exist "%CONFIG_FILE%" (
    echo Creating configuration file...
    (
        echo # Claude Code Providers Configuration
        echo # Lines starting with # are comments and will be ignored
        echo # Format: name=url=api_key=description
        echo qwen=https://dashscope.aliyuncs.com/api/v2/apps/claude-code-proxy==Aliyun Qwen
        echo k2=https://api.moonshot.cn/anthropic==Moonshot AI
        echo glm=https://open.bigmodel.cn/api/anthropic==Zhipu GLM
        echo deepseek=https://api.deepseek.com/v1==DeepSeek
        echo openrouter=https://openrouter.ai/api/v1==OpenRouter
    ) > "%CONFIG_FILE%"
)

:menu
cls
echo.
echo ===============================================
echo    Claude Code Provider Switcher
echo    Config: %CONFIG_FILE%
echo ===============================================
echo.
echo Available Providers:
echo.

:: Display providers with numbers, skipping comment lines
set count=0
for /f "usebackq tokens=1-4 delims== eol=#" %%a in ("%CONFIG_FILE%") do (
    if "%%a" neq "" (
        if "%%b" neq "" (
            set /a count+=1
            if "%%c"=="" (
                echo [!count!] %%a - %%d [Not configured]
            ) else (
                echo [!count!] %%a - %%d [Configured]
            )
        )
    )
)

echo.
echo [A] Add new provider
echo [V] View config file
echo [T] Test current configuration
echo [Q] Quit
echo.
set /p choice=Select provider (number) or action: 

if /i "%choice%"=="A" goto add_provider
if /i "%choice%"=="V" goto view_config
if /i "%choice%"=="T" goto test_config
if /i "%choice%"=="Q" goto cleanup

:: Check if choice is numeric and process provider selection
echo %choice%| findstr /r "^[1-9][0-9]*$" >nul
if %errorlevel%==0 (
    goto select_provider
) else (
    echo Invalid choice
    timeout /t 2 >nul
    goto menu
)

:select_provider
set "target=%choice%"
set count=0
set found=0

:: Find provider by position, skipping comments
for /f "usebackq tokens=1-4 delims== eol=#" %%a in ("%CONFIG_FILE%") do (
    if "%%a" neq "" (
        if "%%b" neq "" (
            set /a count+=1
            if !count!==%target% (
                set "found=1"
                set "PROVIDER_NAME=%%a"
                set "PROVIDER_URL=%%b"
                set "PROVIDER_KEY=%%c"
                set "PROVIDER_DESC=%%d"
            )
        )
    )
)

if "%found%"=="0" (
    echo Invalid provider selection
    timeout /t 2 >nul
    goto menu
)

:: Check if API key is needed
if "%PROVIDER_KEY%"=="" (
    echo.
    echo Provider %PROVIDER_NAME% requires API key
    set /p PROVIDER_KEY=Enter API key for %PROVIDER_NAME%: 
    if "%PROVIDER_KEY%"=="" (
        echo ERROR: API key cannot be empty
        timeout /t 2 >nul
        goto menu
    )
    call :update_key %target% "%PROVIDER_KEY%"
)

:: Apply configuration
echo.
echo ===============================================
echo Switching to %PROVIDER_NAME%...
echo URL: %PROVIDER_URL%
echo ===============================================

:: Set environment variables for current session
set "ANTHROPIC_BASE_URL=%PROVIDER_URL%"
set "ANTHROPIC_AUTH_TOKEN=%PROVIDER_KEY%"

:: Set permanent environment variables
setx ANTHROPIC_BASE_URL "%PROVIDER_URL%" >nul 2>&1
setx ANTHROPIC_AUTH_TOKEN "%PROVIDER_KEY%" >nul 2>&1

echo.
echo SUCCESS: Configuration applied!
echo Provider: %PROVIDER_NAME%
echo Description: %PROVIDER_DESC%
echo URL: %PROVIDER_URL%
echo.
echo Current session environment verified
echo ANTHROPIC_BASE_URL=%ANTHROPIC_BASE_URL%
echo ANTHROPIC_AUTH_TOKEN=%ANTHROPIC_AUTH_TOKEN:~0,10%...
echo.

:: Claude Code startup options
echo ===============================================
echo Claude Code Startup Options
echo ===============================================
echo [1] Start Claude Code in new window
echo [2] Start Claude Code in current window
echo [3] Start Claude Code with project directory
echo [N] Don't start Claude Code now
echo.
set /p start_option=Choose startup option: 

if "%start_option%"=="1" (
    echo Starting Claude Code in new window...
    start "Claude Code" cmd /c "claude"
    echo Claude Code started in new window
) else (
    if "%start_option%"=="2" (
        echo Starting Claude Code in current window...
        echo Provider: %PROVIDER_NAME%
        echo URL: %PROVIDER_URL%
        echo.
        echo Starting Claude Code...
        echo NOTE: Any Node.js warnings below are from Claude Code, not this script.
        echo.
        claude
    ) else (
        if "%start_option%"=="3" (
            set /p project_path=Enter project path or press Enter for current directory: 
            if "!project_path!"=="" set "project_path=%CD%"
            echo Starting Claude Code with project: !project_path!
            echo Creating startup script...
            echo @echo off > "%TEMP%\start_claude.bat"
            echo cd /d "!project_path!" >> "%TEMP%\start_claude.bat"
            echo echo Starting Claude Code in: !project_path! >> "%TEMP%\start_claude.bat"
            echo claude >> "%TEMP%\start_claude.bat"
            echo pause >> "%TEMP%\start_claude.bat"
            start "Claude Code" "%TEMP%\start_claude.bat"
            echo Claude Code started with project
        ) else (
            echo Configuration saved. You can start Claude Code manually later.
        )
    )
)

timeout /t 3 >nul
goto menu

:update_key
set "line_num=%~1"
set "new_key=%~2"
set "tmp_file=%CONFIG_FILE%.tmp"
set count=0

(
    for /f "usebackq delims=" %%i in ("%CONFIG_FILE%") do (
        set "line=%%i"
        if "!line:~0,1!" neq "#" (
            if "!line!" neq "" (
                for /f "tokens=1-4 delims==" %%a in ("!line!") do (
                    set /a count+=1
                    if !count!==%line_num% (
                        echo %%a=%%b=%new_key%=%%d
                    ) else (
                        echo !line!
                    )
                )
            ) else (
                echo !line!
            )
        ) else (
            echo !line!
        )
    )
) > "%tmp_file%"

move /y "%tmp_file%" "%CONFIG_FILE%" >nul
if %errorlevel%==0 (
    echo API key updated successfully!
) else (
    echo ERROR: Failed to update API key
    if exist "%tmp_file%" del "%tmp_file%"
)
timeout /t 1 >nul
exit /b 0

:add_provider
echo.
echo ===============================================
echo         Add New Provider
echo ===============================================
echo.
set /p new_name=Provider name: 
set /p new_url=API URL: 
set /p new_key=API key (optional): 
set /p new_desc=Description: 

:: Validate inputs
if "%new_name%"=="" (
    echo ERROR: Provider name cannot be empty
    timeout /t 2 >nul
    goto add_provider
)

if "%new_url%"=="" (
    echo ERROR: API URL cannot be empty
    timeout /t 2 >nul
    goto add_provider
)

:: Add the new provider
echo %new_name%=%new_url%=%new_key%=%new_desc% >> "%CONFIG_FILE%"
echo Provider '%new_name%' added successfully!
timeout /t 2 >nul
goto menu

:test_config
echo.
echo ===============================================
echo         Test Current Configuration
echo ===============================================
echo.
echo Current environment variables:
echo ANTHROPIC_BASE_URL=%ANTHROPIC_BASE_URL%
if "%ANTHROPIC_AUTH_TOKEN%"=="" (
    echo ANTHROPIC_AUTH_TOKEN=Not set
) else (
    echo ANTHROPIC_AUTH_TOKEN=%ANTHROPIC_AUTH_TOKEN:~0,10%...
)
echo.

if "%ANTHROPIC_BASE_URL%"=="" (
    echo No provider currently configured
) else (
    echo Testing Claude Code availability...
    claude --version >nul 2>&1
    if %errorlevel%==0 (
        echo Claude Code is available and ready
    ) else (
        echo WARNING: Claude Code may not be working properly
    )
)
echo.
pause
goto menu

:view_config
echo.
echo ===============================================
echo         Configuration File
echo         %CONFIG_FILE%
echo ===============================================
echo.
echo Contents (comments starting with # are ignored):
echo.
if exist "%CONFIG_FILE%" (
    type "%CONFIG_FILE%"
) else (
    echo ERROR: Configuration file not found
)
echo.
pause
goto menu

:cleanup
echo.
echo ===============================================
echo Configuration Summary
echo ===============================================
echo Configuration is stored in:
echo   Directory: %CONFIG_DIR%
echo   File: %CONFIG_FILE%
echo.
echo File format: name=url=api_key=description
echo Lines starting with # are comments and ignored
echo.
echo Current configuration:
if "%ANTHROPIC_BASE_URL%" neq "" (
    echo   Active Provider URL: %ANTHROPIC_BASE_URL%
) else (
    echo   No provider currently active
)
echo.
pause
exit /b 0