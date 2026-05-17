@echo off
setlocal

set "PROJECT_ROOT=%~dp0"
set "PYTHONPATH=%PROJECT_ROOT%SRC;%PYTHONPATH%"

python -m foreign_worker_life_info_collector.crew_team.social.news_bot %*

endlocal
