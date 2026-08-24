@echo off
REM install_windows.bat -- Setup script for the Garmin Edge Activity
REM Profile Screen Editor toolkit (Windows).
REM
REM What this does:
REM   1. Confirms a usable Python (the "py" launcher, falling back to
REM      python.exe) is on PATH and at least version 3.10.
REM   2. Installs this toolkit's two dependencies directly into that
REM      Python -- garmin-fit-sdk and wxPython. Deliberately NO
REM      virtual environment (unlike install.sh on macOS): Doug's own
REM      confirmed real Windows 11 install (2026-08-19) skipped a
REM      venv entirely, and using one here would break the nice
REM      double-click-gui_app.py-in-File-Explorer behavior that
REM      install produced -- the python.org installer associates .py
REM      files with the SAME python "pip install" (run without a
REM      venv) puts packages into. A venv would need `python
REM      gui_app.py` from an activated shell instead.
REM   3. Imports both back to confirm the install actually works.
REM
REM Usage:
REM   install_windows.bat              normal run
REM   install_windows.bat --upgrade    also upgrade already-installed packages
REM   install_windows.bat --help       this text
REM   install_windows.bat --version    print this script's own version
REM
REM Safe to re-run any time -- pip quietly no-ops on packages already
REM satisfied (unless --upgrade is given).
REM
REM After it finishes:
REM   python garmin_device.py detect
REM   python gui_app.py                (or just double-click gui_app.py
REM                                      in File Explorer)
REM
REM NOTE: unlike install.sh (macOS), this script does NOT try to
REM install Python itself if it's missing or too old -- it detects and
REM guides instead (Doug's explicit call, 2026-08-20: no silent
REM installer download/elevation, matching install.sh's own
REM detect-and-guide treatment of missing Xcode Command Line Tools).
REM If Python isn't found, or is older than 3.10, this script prints
REM the python.org download page, opens it in your browser, and stops.
REM
REM NOTE: the 3.10 floor is a HARD requirement here, stricter than
REM install.sh's soft warn-and-offer-to-continue at the same
REM threshold on macOS. Reason: wxPython ships pre-built wheels for
REM 3.10+ on both platforms, but building it from source below that
REM needs a full C++ toolchain -- Xcode Command Line Tools (a free,
REM single command) on macOS, versus Visual Studio Build Tools (a
REM multi-GB, multi-step install) on Windows. "Continue anyway, pip
REM will build from source" is a reasonable offer on macOS and a bad
REM one on Windows for this toolkit's actual audience.
REM
REM 1.0.1 -- CONFIRMED via real Windows 11 hardware (2026-08-22,
REM Doug's own laptop). Test performed: uninstalled garmin-fit-sdk and
REM wxPython via "py -3 -m pip uninstall -y" (Python itself left in
REM place), confirmed both failed to import, then ran this script
REM fresh. Result: Python detection, version check, pip install of
REM both packages, and the post-install import verification all
REM worked cleanly against a real Python 3.14 install (prebuilt
REM wxPython 4.3.1 wheel available -- confirms the 3.10 floor's wheel-
REM availability assumption holds at the current end of that range
REM too). One benign pip warning seen and confirmed harmless: wx's
REM bundled demo/dev console scripts (helpviewer.exe, img2py.exe,
REM wxdemo.exe, etc.) installed to a Scripts folder not on PATH --
REM those aren't used by this toolkit (gui_app.py is launched via
REM "python gui_app.py" or a double-click, neither touches that
REM folder), no action needed. Double-click launch of gui_app.py in
REM File Explorer also reconfirmed working post-reinstall -- Windows
REM prompted a one-time "how do you want to open this file" dialog on
REM the very first double-click (Doug picked Python, checked "Always"),
REM which is normal first-use file-association behavior for any .py
REM file with nothing already claiming that extension, not something
REM this script causes or needs to handle; every double-click since has
REM launched directly with no dialog. No code changed -- confirmation-
REM only entry, this script is no longer "written blind." Prior entry
REM (1.0.0, initial version, 2026-08-20, Doug's go-ahead): scoped
REM directly against his own real, confirmed Windows 11 install
REM (README.md Doc rev 54): no venv, py.org installer, plain pip
REM install. Written blind with respect to Windows batch syntax --
REM unlike garmin_device.py's _find_garmin_root_windows() (headlessly
REM tested via ntpath-monkeypatched fake drive trees before Doug's
REM real hardware confirmed it), there was no way to dry-run cmd.exe
REM batch syntax in this project's dev sandbox (no cmd.exe available
REM at all) -- needed Doug's real run on the laptop before it could be
REM trusted, more so than any other single-platform code in this
REM toolkit at the time.

setlocal enabledelayedexpansion

set SCRIPT_VERSION=1.0.1
set MIN_PYTHON_MAJOR=3
set MIN_PYTHON_MINOR=10
set UPGRADE=0

REM Run from the script's own folder, not whatever the caller's cwd
REM happens to be -- matters if this is ever launched via "Run as
REM administrator" (which can start a batch file in
REM C:\Windows\System32 instead of the folder it lives in).
cd /d "%~dp0"

REM ---- parse the one optional argument -------------------------------
set ARG=%~1
if "%ARG%"=="" goto :main
if /I "%ARG%"=="--upgrade" (
    set UPGRADE=1
    goto :main
)
if /I "%ARG%"=="--help" goto :show_help
if /I "%ARG%"=="-h" goto :show_help
if /I "%ARG%"=="--version" (
    echo install_windows.bat %SCRIPT_VERSION%
    exit /b 0
)
echo Unknown option: %ARG% ^(try --help^)
exit /b 1

:show_help
echo install_windows.bat -- Setup script for the Garmin Edge Activity
echo Profile Screen Editor toolkit (Windows).
echo.
echo Usage:
echo   install_windows.bat              normal run
echo   install_windows.bat --upgrade    also upgrade already-installed packages
echo   install_windows.bat --help       this text
echo   install_windows.bat --version    print this script's own version
echo.
echo Checks for Python 3.10+ (py launcher, falling back to python.exe),
echo then installs garmin-fit-sdk and wxPython directly into it -- no
echo virtual environment. If Python isn't found or is too old, this
echo prints instructions instead of installing anything.
exit /b 0

:main
echo ==^> install_windows.bat v%SCRIPT_VERSION%
echo ==^> Checking for Python...

REM Prefer the "py" launcher -- it's registered more reliably across
REM python.org installs than python.exe itself, and "py -3" pins
REM Python 3 explicitly regardless of what's set as the launcher's
REM own default.
set PY=
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 --version >nul 2>&1
    if !errorlevel!==0 set PY=py -3
)
if "%PY%"=="" (
    where python >nul 2>&1
    if !errorlevel!==0 set PY=python
)

if "%PY%"=="" (
    echo.
    echo ERROR: No Python found on PATH.
    echo.
    echo Install Python from https://www.python.org/downloads/windows/
    echo IMPORTANT: on the installer's first screen, check "Add
    echo python.exe to PATH" before clicking Install -- without that,
    echo this script and the toolkit's own double-click launch won't
    echo find it either.
    echo.
    echo Then re-run this script.
    start https://www.python.org/downloads/windows/
    pause
    exit /b 1
)
echo Found Python: %PY%

REM ---- version check --------------------------------------------------
for /f "tokens=1,2" %%a in ('%PY% -c "import sys;print(sys.version_info[0],sys.version_info[1])"') do (
    set PYMAJOR=%%a
    set PYMINOR=%%b
)
echo Python version: %PYMAJOR%.%PYMINOR%

set TOO_OLD=0
if %PYMAJOR% LSS %MIN_PYTHON_MAJOR% set TOO_OLD=1
if %PYMAJOR%==%MIN_PYTHON_MAJOR% if %PYMINOR% LSS %MIN_PYTHON_MINOR% set TOO_OLD=1

if %TOO_OLD%==1 (
    echo.
    echo ERROR: Python %PYMAJOR%.%PYMINOR% is too old -- this toolkit
    echo needs Python %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% or newer.
    echo.
    echo Reason: wxPython only ships pre-built Windows wheels from
    echo %MIN_PYTHON_MAJOR%.%MIN_PYTHON_MINOR% up -- building it from
    echo source below that needs Visual Studio Build Tools, a much
    echo bigger install than this toolkit is worth.
    echo.
    echo Install a newer Python from https://www.python.org/downloads/windows/
    echo IMPORTANT: check "Add python.exe to PATH" on the installer's
    echo first screen.
    echo.
    echo Then re-run this script.
    start https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

REM ---- install dependencies -------------------------------------------
set PIP_UPGRADE_FLAG=
if %UPGRADE%==1 set PIP_UPGRADE_FLAG=--upgrade

echo ==^> Upgrading pip...
%PY% -m pip install --upgrade pip --quiet
if errorlevel 1 goto :pip_failed

echo ==^> Installing garmin-fit-sdk...
%PY% -m pip install %PIP_UPGRADE_FLAG% garmin-fit-sdk
if errorlevel 1 goto :pip_failed

echo ==^> Installing wxPython (this can take a few minutes)...
%PY% -m pip install %PIP_UPGRADE_FLAG% wxPython
if errorlevel 1 goto :pip_failed

REM ---- verify everything imports ---------------------------------------
echo ==^> Verifying installed packages import cleanly...
set VERIFY_FAILED=0

%PY% -c "import garmin_fit_sdk; print('  garmin_fit_sdk OK', getattr(garmin_fit_sdk, '__version__', 'version unknown'))"
if errorlevel 1 (
    echo   garmin_fit_sdk FAILED to import
    set VERIFY_FAILED=1
)

%PY% -c "import wx; print('  wx OK', wx.version())"
if errorlevel 1 (
    echo   wx FAILED to import
    set VERIFY_FAILED=1
)

if %VERIFY_FAILED%==1 (
    echo.
    echo ERROR: one or more packages failed to import after install.
    echo See the output above for details.
    pause
    exit /b 1
)

echo.
echo ==^> Setup complete.
echo.
echo Next steps:
echo   python garmin_device.py detect      (CLI: confirm the device is seen)
echo   python gui_app.py                   (or double-click gui_app.py in File Explorer)
echo.
echo Re-run this script any time -- it's safe to run repeatedly.
echo.
pause
exit /b 0

:pip_failed
echo.
echo ERROR: pip install failed. See the output above for details.
pause
exit /b 1
