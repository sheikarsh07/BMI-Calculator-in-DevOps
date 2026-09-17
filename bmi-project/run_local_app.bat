@echo off
title BMI Calculator - Local Test Runner
color 0A
echo ============================================================
echo   BMI CALCULATOR - LOCAL RUNNER (ONE-CLICK)
echo ============================================================
echo.
echo Starting Flask BMI Application on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server anytime.
echo.

start http://127.0.0.1:5000

py app/app.py
if %ERRORLEVEL% NEQ 0 (
    python app/app.py
)

pause
