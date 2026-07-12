@echo off
setlocal

pushd %~dp0

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    python run_tradovate.py
) else (
    python run_tradovate.py
)

popd
endlocal