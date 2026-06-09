@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "ADMIN_UI_DIR=%PROJECT_ROOT%SRC\foreign_worker_life_info_collector\admin_ui"
set "PYTHONPATH=%PROJECT_ROOT%SRC;%PYTHONPATH%"
set "ADMIN_API_HOST=127.0.0.1"
set "ADMIN_API_PORT=8765"
set "ADMIN_WEB_HOST=127.0.0.1"
set "ADMIN_WEB_PORT=5173"

if "%PGDATABASE%"=="" set "PGDATABASE=foreign_worker_job_info"
if "%PGHOST%"=="" set "PGHOST=localhost"
if "%PGPORT%"=="" set "PGPORT=5432"
if "%PGUSER%"=="" set "PGUSER=postgres"

if not exist "%ADMIN_UI_DIR%\package.json" (
    echo Admin UI package.json not found: "%ADMIN_UI_DIR%\package.json"
    exit /b 1
)

echo Stopping existing WorkConnect admin API processes ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"name = 'python.exe'\" | Where-Object { $_.CommandLine -like '*foreign_worker_life_info_collector.api.admin_server*' -or $_.CommandLine -like '*foreign_worker_life_info_collector.api.admin_dev_server*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }"

echo Starting admin API server on http://%ADMIN_API_HOST%:%ADMIN_API_PORT% ...
start "WorkConnect Admin API" /D "%PROJECT_ROOT%" cmd /k python -m foreign_worker_life_info_collector.api.admin_dev_server --host %ADMIN_API_HOST% --port %ADMIN_API_PORT% %*

echo Starting admin web server on http://%ADMIN_WEB_HOST%:%ADMIN_WEB_PORT% ...
start "WorkConnect Admin Web" /D "%ADMIN_UI_DIR%" cmd /k npm run dev -- --host %ADMIN_WEB_HOST% --port %ADMIN_WEB_PORT%

echo.
echo PostgreSQL: %PGHOST%:%PGPORT% database=%PGDATABASE%
echo Admin API:  http://%ADMIN_API_HOST%:%ADMIN_API_PORT%
echo Admin Web:  http://%ADMIN_WEB_HOST%:%ADMIN_WEB_PORT%

endlocal
