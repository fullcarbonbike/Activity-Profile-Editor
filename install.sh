#!/usr/bin/env bash
#
# install.sh -- Setup script for the Garmin Edge 530 Activity Profile
# Screen Editor toolkit (macOS only -- device detection in
# garmin_device.py isn't implemented on Windows/Linux yet; see
# README.md).
#
# What this does:
#   1. Confirms you're on macOS.
#   2. Confirms Xcode Command Line Tools are installed -- required
#      before python3 (even Apple's built-in /usr/bin/python3) can
#      actually run on a fresh Mac.
#   3. Confirms python3 is present and new enough.
#   4. Creates (or reuses) a dedicated virtual environment in ./.venv,
#      so nothing is installed into your system or Homebrew Python.
#   5. Installs this toolkit's two external dependencies into that
#      venv: garmin-fit-sdk and wxPython.
#   6. Imports both back to confirm the install actually works.
#
# Usage:
#   ./install.sh              # normal run
#   ./install.sh --upgrade    # also upgrade already-installed packages
#   ./install.sh --help       # this text
#
# Safe to re-run any time -- it reuses the existing .venv and pip
# quietly no-ops on packages that are already satisfied (unless
# --upgrade is given).
#
# After it finishes:
#   source .venv/bin/activate
#   python3 garmin_device.py detect
#   python3 gui_app.py
#
# Note: on a fresh Mac that's never had Xcode Command Line Tools
# installed, running this script (or python3 directly) can pop up
# their install dialog. This script now checks for that up front and
# stops with clear instructions instead of failing partway through --
# let the install finish (or run `xcode-select --install` yourself),
# then re-run this script.

set -euo pipefail

# 1.0.2 -- real bug fix (2026-08-13): once past the Xcode CLT/python3
# checks on a real Mac (Homebrew python3 3.14, freshly installed),
# "Installing garmin-fit-sdk..." died with "PIP_EXTRA[@]: unbound
# variable." Cause: bash 3.2 (macOS's stock /bin/bash, confirmed
# that's really what runs this script) has a long-standing bug where
# expanding an EMPTY array under `set -u` throws unbound-variable
# instead of expanding to nothing -- fixed in bash 4.4+, so it never
# showed up in the bash 5 dev/test sandbox, only on real hardware.
# Replaced the PIP_EXTRA array with a small pip_install() wrapper
# function that branches on $UPGRADE directly -- no array, so the bug
# class is structurally impossible here now, not just avoided this one
# time. Prior entry (1.0.1): a fresh Mac with no Xcode Command Line
# Tools installed crashed silently right after "Found python3" --
# invoking python3 for its version triggered xcode-select's own
# "requesting install" note to stderr and a non-zero exit, which
# set -e then turned into an unexplained stop with no die() message.
# Added an explicit Command Line Tools check as its own step, before
# python3 is touched at all, plus defense-in-depth error handling
# around the version-check invocation itself. Prior entry (1.0.0):
# initial version.
SCRIPT_VERSION="1.0.2"

# ---- config ---------------------------------------------------------------
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=9      # hard floor -- toolkit code itself needs this much
RECOMMENDED_PYTHON_MINOR=10   # wxPython ships pre-built wheels from here up
VENV_DIR=".venv"

UPGRADE=0
for arg in "$@"; do
    case "$arg" in
        --upgrade)
            UPGRADE=1
            ;;
        -h|--help)
            sed -n '2,37p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        --version)
            echo "install.sh $SCRIPT_VERSION"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg (try --help)" >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ---- output helpers ---------------------------------------------------------
info()  { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
warn()  { printf '\033[1;33m!!\033[0m  %s\n' "$1"; }
error() { printf '\033[1;31mERROR:\033[0m %s\n' "$1" >&2; }
die()   { error "$1"; exit 1; }

# ---- 1. platform check --------------------------------------------------
info "install.sh v$SCRIPT_VERSION"
info "Checking platform..."
if [[ "$(uname -s)" != "Darwin" ]]; then
    die "This install script currently supports macOS only -- device detection (garmin_device.py) isn't implemented on Windows or Linux yet. See README.md."
fi
MAC_VERSION="$(sw_vers -productVersion 2>/dev/null || echo unknown)"
info "macOS $MAC_VERSION detected ($(uname -m))"

# ---- 2. Xcode Command Line Tools present? --------------------------------
# Required before python3 -- even Apple's built-in /usr/bin/python3 -- can
# actually execute on a Mac that's never had them installed. Checking this
# FIRST, before touching python3 at all, avoids a confusing half-triggered
# install prompt followed by a silent script failure (real-world case: a
# fresh Mac ran this script, xcode-select printed its own "requesting
# install" note to stderr the moment python3 was invoked, python3 exited
# non-zero, and the script stopped right there with no explanation).
info "Checking for Xcode Command Line Tools..."
if ! xcode-select -p >/dev/null 2>&1; then
    warn "Xcode Command Line Tools aren't installed."
    warn "macOS may have just opened an install dialog on its own (checking for the tools can trigger it). If so, let that finish, then re-run this script."
    warn "If no dialog appeared, run this yourself: xcode-select --install"
    die "Re-run ./install.sh once Command Line Tools finish installing (confirm with: xcode-select -p)."
fi
info "Xcode Command Line Tools found: $(xcode-select -p)"

# ---- 3. python3 present? -------------------------------------------------
info "Checking for python3..."
if ! command -v python3 >/dev/null 2>&1; then
    die "python3 not found. Install it via Homebrew (brew install python3) or https://www.python.org/downloads/macos/, then re-run this script."
fi
PYTHON_BIN="$(command -v python3)"
info "Found python3: $PYTHON_BIN"

# ---- 4. python3 version check --------------------------------------------
if ! PY_VER="$("$PYTHON_BIN" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>&1)"; then
    die "python3 ($PYTHON_BIN) failed to run: $PY_VER"
fi
PY_MAJOR="${PY_VER%%.*}"
PY_MINOR="${PY_VER##*.}"
info "python3 version: $PY_VER"

if (( PY_MAJOR < MIN_PYTHON_MAJOR || (PY_MAJOR == MIN_PYTHON_MAJOR && PY_MINOR < MIN_PYTHON_MINOR) )); then
    die "Python $PY_VER is too old -- this toolkit needs Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR or newer. Install a newer python3 (Homebrew: brew install python3) and re-run."
fi

if (( PY_MINOR < RECOMMENDED_PYTHON_MINOR )); then
    warn "Python $PY_VER has no pre-built wxPython wheel on PyPI as of this writing -- pip will build wxPython from source, which can take 10-20 minutes (Command Line Tools are already confirmed present above, so the build itself should at least be able to start)."
    warn "For a faster install, consider a newer python3 instead, e.g.: brew install python3"
    read -r -p "Continue anyway? [y/N] " REPLY
    case "$REPLY" in
        [Yy]*) ;;
        *) die "Aborted -- install Python $MIN_PYTHON_MAJOR.$RECOMMENDED_PYTHON_MINOR+ (recommended) and re-run." ;;
    esac
fi

# ---- 5. venv module present? --------------------------------------------
info "Checking for the venv module..."
if ! "$PYTHON_BIN" -m venv --help >/dev/null 2>&1; then
    die "python3's built-in 'venv' module isn't available. If this is a Homebrew python3, try: brew reinstall python3"
fi

# ---- 6. create / reuse venv ----------------------------------------------
if [[ -d "$VENV_DIR" ]]; then
    info "Reusing existing virtual environment: $VENV_DIR"
else
    info "Creating virtual environment: $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

VENV_PY="$VENV_DIR/bin/python3"
VENV_PIP="$VENV_DIR/bin/pip3"

# ---- 7. upgrade pip inside the venv --------------------------------------
info "Upgrading pip inside the virtual environment..."
"$VENV_PY" -m pip install --upgrade pip --quiet

# ---- 8. install dependencies ----------------------------------------------
# NOTE: deliberately not using a bash array for the optional --upgrade flag.
# bash 3.2 (macOS's stock /bin/bash -- what this script actually runs under
# on a real Mac) has a long-standing bug where expanding an EMPTY array
# under `set -u` throws "unbound variable" instead of silently expanding to
# nothing (fixed in bash 4.4+). Confirmed the hard way on real hardware --
# the dev/test sandbox runs bash 5, which doesn't have this bug, so it
# passed there and failed on the first real macOS run. A tiny wrapper
# function sidesteps the whole array-under-set-u issue.
pip_install() {
    if (( UPGRADE )); then
        "$VENV_PIP" install --upgrade "$1"
    else
        "$VENV_PIP" install "$1"
    fi
}

info "Installing garmin-fit-sdk..."
pip_install garmin-fit-sdk

info "Installing wxPython (this can take a few minutes, longer if building from source)..."
pip_install wxPython

# ---- 9. verify everything imports ----------------------------------------
info "Verifying installed packages import cleanly..."
"$VENV_PY" - <<'PYEOF'
import sys
ok = True
try:
    import garmin_fit_sdk
    print("  garmin_fit_sdk OK (%s)" % getattr(garmin_fit_sdk, "__version__", "version unknown"))
except Exception as e:
    ok = False
    print("  garmin_fit_sdk FAILED: %s" % e)
try:
    import wx
    print("  wx OK (%s)" % wx.version())
except Exception as e:
    ok = False
    print("  wx FAILED: %s" % e)
sys.exit(0 if ok else 1)
PYEOF

info "Setup complete."
cat <<EOF

Next steps:
  source $VENV_DIR/bin/activate
  python3 garmin_device.py detect      # CLI: confirm the device is seen
  python3 gui_app.py                   # GUI

(Run 'deactivate' to leave the virtual environment when you're done.
Re-run this script any time -- it's safe to run repeatedly.)
EOF
