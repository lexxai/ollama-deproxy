@echo off
setlocal

echo ==========================
echo Building ollama-deproxy
echo ==========================

REM activate venv if exists
REM Check if .venv-build exists
if exist .venv-build\Scripts\activate (
    echo Using existing venv
    call .venv-build\Scripts\activate
) else (
    echo Creating new venv
    uv venv .venv-build -p 3.13
    call .venv-build\Scripts\activate
)

uv sync --dev --active

set PYTHONPATH=src


echo Starting  build...



echo.
echo ==========================
echo Build finished
echo ==========================
echo Binary should be in:
echo dist\ollama-deproxy.exe

pause