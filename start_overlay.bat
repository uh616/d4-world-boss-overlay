@echo off
setlocal

:: Get the directory of this batch file
set "DIR=%~dp0"

:: Find pythonw.exe next to python.exe
for /f "delims=" %%i in ('where python 2^>nul') do (
    set "PYTHONDIR=%%~dpi"
    goto :run
)

:run
if exist "%PYTHONDIR%pythonw.exe" (
    "%PYTHONDIR%pythonw.exe" "%DIR%overlay.py"
) else (
    python "%DIR%overlay.py"
)
