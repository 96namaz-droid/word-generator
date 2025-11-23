@echo off
chcp 65001 >nul
cd /d "%~dp0"
python view_logs.py -f
pause

