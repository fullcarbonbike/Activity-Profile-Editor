#!/bin/bash
#
# launch_gui.command -- double-clickable launcher for gui_app.py on macOS.
#
# Why this exists: double-clicking gui_app.py directly doesn't work
# usefully on macOS the way it does on Windows -- there's no built-in
# file association that would run it with THIS toolkit's own .venv
# (where wxPython/garmin-fit-sdk actually live); at best it runs
# whatever python3 macOS happens to resolve by default, which almost
# never has those packages installed. See PROJECT_NOTES.md ("macOS
# double-click launcher") for the full story, including the real
# install.sh-vs-Windows no-venv contrast that causes this.
#
# Setup (once, from Terminal, inside this folder):
#   ./install.sh
#
# After that: just double-click this file in Finder.
#
# First-launch note: macOS Gatekeeper will likely refuse a plain
# double-click the very first time ("cannot be opened because it is
# from an unidentified developer") -- right-click (or Control-click)
# this file and choose Open instead, once. Every launch after that
# works with a normal double-click. This is standard macOS behavior for
# any downloaded/unsigned script, not specific to this toolkit.

# 1.0.0 -- initial version, Doug's go-ahead (2026-08-30). Mirrors
# Windows' double-click-gui_app.py convenience (see install_windows.bat)
# using the mechanism macOS actually supports for this: a .command file,
# which Finder runs directly in Terminal.app, with the executable bit
# set (install.sh now chmod's this defensively, in case a download
# method ever drops it). Deliberately does NOT try to make gui_app.py
# itself double-clickable (no file association trick, no shebang
# tomfoolery) -- that's the Windows-only convenience python.org's
# installer creates by associating .py with the SAME python pip
# installs into; macOS's install path uses an isolated .venv on
# purpose (README.md/PROJECT_NOTES.md's own established reasoning), so
# a separate launcher script is the correct fix here, not a workaround.
SCRIPT_VERSION="1.0.0"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

VENV_PY="$SCRIPT_DIR/.venv/bin/python3"

if [[ ! -x "$VENV_PY" ]]; then
    echo "ERROR: No virtual environment found at .venv"
    echo
    echo "Run ./install.sh first (from Terminal, inside this folder),"
    echo "then double-click this file again."
    echo
    read -r -p "Press Return to close this window... " _
    exit 1
fi

"$VENV_PY" "$SCRIPT_DIR/gui_app.py"
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
    echo
    echo "gui_app.py exited with an error (status $STATUS) -- see any messages above."
    read -r -p "Press Return to close this window... " _
fi

exit $STATUS
