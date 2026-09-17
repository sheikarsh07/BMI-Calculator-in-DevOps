@echo off
title DevOps Pipeline Validator & Simulator
color 0B
echo ============================================================
echo   DEVOPS PIPELINE - ONE-CLICK VERIFICATION & SIMULATOR
echo ============================================================
echo.
echo Running automated validation across all components...
echo [1] Flask BMI Application & /health Probe
echo [2] Dockerfile & Container Architecture
echo [3] Ansible Playbook & Trivy Vulnerability Scan
echo [4] Terraform Infrastructure as Code Configuration
echo [5] Kubernetes Deployment & NodePort Service Manifests
echo.

py test_project.py
if %ERRORLEVEL% NEQ 0 (
    python test_project.py
)

echo.
echo ============================================================
echo To run the full live pipeline on Linux / WSL2:
echo   bash setup_and_run.sh
echo ============================================================
echo.
pause
