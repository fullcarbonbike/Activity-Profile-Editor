#!/usr/bin/env python3
__version__ = "0.12.8"  # New feature, Doug's go-ahead (2026-08-25): backup retention/pruning. New prune_old_backups(working_dir, older_than_days, dry_run=True) deletes (or, dry_run, just reports) entire working_dir/backups/<timestamp>/ folders older than older_than_days -- decided by the folder's OWN NAME (its "%Y%m%d_%H%M%S" timestamp), not filesystem mtime, since mtime can reset on a copy/restore of the working directory while the embedded name is always correct by construction. Design chosen from three options put to Doug: time-based folder deletion [CHOSEN, this], keep-latest-N-per-profile (rejected -- each backups/<timestamp>/ folder snapshots EVERY profile together via backup_profiles(), not one folder per profile, so per-profile retention would mean deleting individual files out of a shared folder rather than whole folders), and keep-only-the-single-latest-backup (rejected -- cuts against Restore-from-Backup's whole reason for existing, and Doug's own real usage numbers, ~1098 backed-up .fit files / ~4-5GB over this project's entire prior history, confirmed disk space was never the actual constraint that would justify losing all older restore points). Manual-only, Doug's explicit choice -- no automatic/silent pruning on launch or anywhere else; the only entry points are a deliberate user action (this module's new `prune-backups` CLI subcommand, or gui_app.py's new "Clean Up Old Backups..." dialog, v0.19.19), same posture as every other destructive action already in this toolkit. New `prune-backups <working_dir> [--older-than-days N] [--dry-run] [--yes]` CLI subcommand (default 30 days, matching the GUI dialog's own default): always previews the folder list + total size first, then -- unless --dry-run -- prompts an interactive [y/N] confirm before deleting (same style as eject_device()'s own confirm), skippable via --yes for scripting. New _format_bytes() helper (plain stdlib, no new dependency), shared by the CLI summary and gui_app.py's dialog. Any folder whose name doesn't parse as the expected timestamp format is left alone entirely, not counted, not touched -- defensive against anything unexpected ever ending up in backups/. Headlessly verified: a fake working_dir with folders at several ages (90/45/31/10/0 days) plus one non-timestamp junk folder correctly identifies only the >=30-day folders for both dry-run preview and real deletion, leaves recent/today/junk untouched, and a second run against an already-pruned tree correctly reports nothing left to prune; the CLI subcommand exercised end-to-end (dry-run, --yes deletion, re-run confirms empty) against a real temp directory. Prior entry (v0.12.7): Real safety fix, Doug's go-ahead (2026-08-24): write_to_newfiles() gained an optional working_dir parameter -- if given, and a profile currently exists on the device under target_profile_filename, it's backed up to working_dir/backups/<timestamp>/ (same naming convention as backup_profiles(), so it's immediately browsable via the normal Restore-from-Backup picker) BEFORE being overwritten. Closes a real gap flagged while scoping "Import an external profile" (see PROJECT_NOTES.md Open Items): every GUI-driven write already gets this protection for free, since visiting the profile list always runs backup_profiles() first -- but a bare CLI `deploy` call bypassed that entirely, meaning `garmin_device.py deploy <patched> <existing_filename>` with no prior `backup` call would overwrite a live profile with zero safety net. Deliberately NOT a hard block or an interactive confirm -- overwriting the target filename is the normal, intended outcome of every deploy (that's how an edit gets written back), so blocking or prompting would break the core workflow for no benefit; the fix is a silent, automatic backup instead, same posture as every other write path in this toolkit. working_dir stays optional (not required) so existing callers/scripts that don't pass one keep working exactly as before -- omitting it just means no backup is attempted, matching the old behavior precisely. CLI `deploy` subcommand gained a new optional `--working-dir DIR` flag wired straight through; omitting it now prints a one-line NOTE to stderr explaining the profile will be overwritten with no backup, rather than staying silent about the gap. gui_app.py's DeployPanel (the single GUI call site for write_to_newfiles(), covering every write path -- edit, Clone, Restore, and the planned Import) now passes frame.working_dir too, for defense-in-depth on top of the profile-list backup it already gets. Headlessly verified: a fake garmin_root with an existing target profile correctly gets backed up before overwrite (byte-identical backup, correct timestamp folder, browsable via list_backup_history()); omitting working_dir is a no-op, byte-identical to pre-fix behavior; a target filename with no existing profile on the device correctly skips the backup attempt (nothing to back up). Prior entry (v0.12.6): CONFIRMED on real Windows 11 hardware (2026-08-19, Doug): _find_garmin_root_windows() (v0.12.5) works correctly against a real Edge 530 -- `detect` printed the same device info the Mac shows, `screens` worked from both this file and fit_dump.py, and the full GUI workflow (add a screen to the Sandbox profile, deploy, restart, NewFiles round-trip) completed cleanly, all with zero code changes -- copying the toolkit's .py files to the Windows laptop was sufficient. Doug's D:\Garmin has Sports/NewFiles flat at the drive root, so this run exercised Level 1 of the function's two-level check; the Level 2 (one-subfolder-deep) branch, kept for parity with the macOS half, is still unexercised on real hardware but has no reason to behave differently. No Linux testing has been done. Doc-only/confirmation entry -- no code changed. Prior entry (v0.12.5, 2026-08-17): New feature, Doug's go-ahead: _find_garmin_root_windows() filled in -- Windows support's single deliberately-stubbed function, per this file's own module docstring ("find_garmin_root() is the ONLY function that needs a platform-specific implementation"). Scans drive letters C: through Z: (A:/B: skipped, historically floppy drives) for the same Sports/+NewFiles/ structure check _find_garmin_root_macos() uses, at both the drive root AND one level of subfolder -- mirrors the macOS two-level check exactly, since real Edge 530 hardware nests Sports/NewFiles one folder down under the mounted volume on Doug's Mac; whether Windows exposes the same nesting or puts them flat at the drive letter was UNCONFIRMED pending real hardware testing at the time (now resolved above: flat, on Doug's test laptop). Deliberately uses plain os.path.exists()/os.listdir() drive-letter iteration rather than a Windows API (e.g. win32api.GetLogicalDriveStrings()) -- avoids adding a new dependency (pywin32) beyond what install.sh already installs. OSError from an inaccessible/empty drive (e.g. a card reader with no media) is caught and skipped per-letter, same defensive posture as the macOS half's PermissionError handling. New `string` import (ascii_uppercase for the drive-letter loop). find_garmin_root() itself needed no change -- it already dispatched to this function by platform.system(); this was purely filling in the stub. Headlessly verified via ntpath-monkeypatched fake drive trees (can't test real Windows drive letters in this dev sandbox): nested-structure case, flat-structure case, no-device-present case, and a flaky/inaccessible drive case all behave correctly; confirmed A:/B: are skipped and C: through Z: are checked in order; confirmed find_garmin_root() correctly dispatches to this function when platform.system() == "Windows". Prior entry (v0.12.4): Real bug fix, Doug's report from actually using the GUI (2026-08-16, same-day follow-up to v0.12.3): even after v0.12.3's smart-char fix, 3 literal "?" kept reappearing at the very front of startup.txt's preserved header comment line -- invisible in the GUI (which only shows the editable message text), found by Doug opening the raw file in BBEdit. Different mechanism from v0.12.3: read_startup_txt() decodes raw bytes as ASCII with errors="replace", so a leading UTF-8 BOM (3 bytes, EF BB BF, each individually invalid for ASCII) decodes to 3 U+FFFD characters, which ride through the "preserve header byte-for-byte" split/rejoin (preserved from the decoded string, not the raw bytes) and get re-encoded to 3 literal "?" bytes on every save -- self-perpetuating once a BOM is present, since the header is never regenerated, only carried forward. read_startup_txt() now strips a leading UTF-8 BOM before decoding, so it's a silent no-op instead. Matches Doug's own observation exactly: manually removing the "?" via BBEdit and re-saving (no BOM) stopped them from reappearing on the next gui_app edit. BOM's original source still unknown/unconfirmed. Headlessly verified: a fake garmin_root with a BOM-prefixed startup.txt now reads back with zero "?"/U+FFFD in the header; a file with no BOM is a byte-identical no-op (unaffected). Prior entry (v0.12.3): a routine startup.txt edit came back with three "?" characters added on one line and "..." replaced by a SINGLE "?" on another, even though Doug never typed a "?" anywhere. Root cause: write_startup_txt() has always encoded with content.encode("ascii", errors="replace"), and wx.TextCtrl on macOS is backed by Cocoa's NSTextView, which silently auto-substitutes typed text by default -- three periods become one U+2026 ellipsis character, straight quotes become curly ones, a double hyphen becomes an em dash, etc, all as you type. Each of those single Unicode characters then hit the ASCII-only encode and became exactly one "?" -- matching the reported pattern precisely (the ellipsis became ONE "?", not three, which rules out a byte-level/UTF-8 explanation and points straight at one non-ASCII CHARACTER per substitution). Not independently byte-confirmed via a hex dump of Doug's exact before/after files, but this mechanism reproduces the reported symptom pattern exactly and is directly traceable to this file's own encode call. New _SMART_CHAR_REPLACEMENTS table + _normalize_smart_chars(), applied to content inside write_startup_txt() immediately before the ascii encode -- reverses the common Cocoa smart-substitution characters (curly single/double quotes, en dash, em dash, ellipsis) back to their plain-ASCII originals, so typed text round-trips correctly regardless of which substitution macOS silently applied. Any character NOT in the table is still replaced with "?" on write, unchanged, honest fallback for a genuinely unsupported character -- the GUI's existing non-ASCII warning (StartupTxtPanel._update_warning(), gui_app.py) still flags anything that slips through. Single shared fix point -- both the GUI (StartupTxtPanel.on_save()) and the `startup-txt --write` CLI subcommand funnel through this same write_startup_txt(), so both get the fix with no gui_app.py change needed. Headlessly verified: an ellipsis, curly quotes, and an en/em dash all round-trip to their exact ASCII originals with zero "?" in the encoded output; a genuinely unmapped non-ASCII character (e.g. an accented letter) still degrades honestly to "?", confirming the fallback behavior is unchanged for anything outside the table. Prior entry (v0.12.2): New feature, Doug's go-ahead (2026-08-15): backend for "Restore a Deleted Profile" (see PROJECT_NOTES.md Open Items). New list_backed_up_profile_filenames(working_dir) -- returns every .fit filename seen across ANY working_dir/backups/<timestamp>/ folder, regardless of whether it's still on the device; the GUI/CLI subtract the currently-live profile list to find candidates. Filters to ".fit" only (list_profiles()'s own convention) specifically because write_startup_txt() (v0.12.0) backs startup.txt up into this SAME backups/ folder structure -- without the filter, a boot-message backup would get mistaken for a deleted profile. New `deleted-profiles` CLI subcommand (needs a connected device, to know what's currently live). The one real risk this feature depends on -- whether NewFiles can actually RECREATE a profile deleted from Sports/, not just replace an existing one -- was already CONFIRMED via a direct on-device test back on 2026-08-11 (garmin_device.py deploy against a deliberately-deleted profile's backup); this entry is purely the missing discovery-side function, no new write-path risk. Headlessly verified: a fake backups/ tree with two historical profiles (one still "live," one not) and a startup.txt backup mixed in correctly returns only the non-live profile, with startup.txt correctly excluded; the `deleted-profiles` CLI subcommand exercised end-to-end via a monkeypatched find_garmin_root(). Backs gui_app.py's new RestoreDeletedPanel. Prior entry (v0.12.1): Real bug fix, Doug's report from actually using the GUI (2026-08-14): StartupTxtPanel's message editor showed a blank line between every real line of Doug's own existing message, even though the same file opened with no blank lines in BBEdit and vi. read_startup_txt() now normalizes line endings ('\r\n' and lone '\r' both collapsed to plain '\n') immediately after decoding, before the content is ever split/displayed. Best-evidenced explanation (not independently byte-confirmed via a hex dump of the real file, flagged honestly): the file is likely CRLF-terminated, which BBEdit/vi both silently auto-normalize on open (so it LOOKS identical to an LF file in either), but wx.TextCtrl's SetValue() has documented bad behavior when fed a string containing embedded '\r\n' -- each '\r' can contribute its own line break on top of the following '\n', producing exactly a blank-line-per-line rendering. Normalizing at the single read entry point fixes the display regardless of which theory is exactly right, and is a safe no-op for a file that was already LF-only (headlessly verified both ways: a simulated CRLF file round-trips through parse_startup_txt()/build_startup_txt() with zero blank lines and zero stray '\r' bytes; the original all-LF round-trip test is unaffected, still byte-identical). Side effect, noted in the function's own docstring: any file edited and saved through this toolkit from now on gets its line endings normalized to LF, even if it started out CRLF -- not expected to matter to the device's own boot-message renderer (no evidence either way), but a real, deliberate behavior change from a plain byte-for-byte round-trip, worth remembering if a future report ever hinges on exact original byte content. Prior entry (v0.12.0): New feature, Doug's go-ahead (2026-08-14): startup.txt (custom boot message) read/parse/build/write support. New STARTUP_TXT_FILENAME/STARTUP_TXT_MAX_CHARS/STARTUP_TXT_MAX_LINES constants and read_startup_txt()/parse_startup_txt()/build_startup_txt()/write_startup_txt(), plus a new `startup-txt` CLI subcommand (view, or --write FILE to overwrite). CONFIRMED path (Doug's own real Edge 530, direct ls -l/cat, 2026-08-14): startup.txt sits at garmin_root itself (same level as Sports/NewFiles/Settings), not inside Sports/ -- no find_garmin_root() change needed, it already resolves there. CONFIRMED write mechanism, via the file's own on-device comment ("Allow one full power cycle after editing for your message to be updated"): a DIRECT overwrite while mounted, NOT a NewFiles import -- write_startup_txt() backs up any existing file into the SAME working_dir/backups/<timestamp>/ folder structure backup_profiles() uses (harmless overlap -- list_backup_history() only ever looks for one specific filename per folder) before overwriting. parse_startup_txt()/build_startup_txt() split/rejoin the file at the LAST '-->' in the content -- Garmin's own instructional <!-- --> comments + the <display=N> directive (header) stay byte-for-byte untouched except for a possible display-seconds substitution, while the free-form message text (message) is the only part meant to be freely edited; this split point is generic (works on any file matching Garmin's own template shape, not hardcoded to Doug's specific message content), and headlessly round-trip-tested byte-for-byte against Doug's real file. STARTUP_TXT_MAX_CHARS=256/STARTUP_TXT_MAX_LINES=6 are the developer-documented (gplama.com, via DC Rainmaker) reference limits -- explicitly NOT enforced as a hard block anywhere in this file (Doug, 2026-08-14: character-width-dependent wrapping means these are typing guidance only, not a real validation the toolkit can perform). Headlessly verified: parse/build round-trip is byte-identical on Doug's real file content; write_startup_txt() backup-then-overwrite behavior confirmed via a fake filesystem garmin_root (no real device needed, since this is plain file I/O, unlike every other write in this file); `startup-txt` CLI subcommand exercised end-to-end (view + --write) via a monkeypatched find_garmin_root(). Backs gui_app.py's new StartupTxtPanel (v0.18.0). Prior entry (v0.11.0): add list_backup_history() -- lists every backup of one profile under working_dir/backups/<timestamp>/, newest first, de-duplicating consecutive byte-identical entries (backup_profiles() runs on every visit to the GUI's profile list, not just on real changes, so an untouched profile accumulates many identical timestamped backups per session). Backs the GUI's "Restore from Backup..." picker (gui_app.py v0.15.0) and a new `backup-history` CLI subcommand. Prior entry (v0.10.0): add get_device_info() reading Device.fit -- for the GUI's initial detect screen, before profile selection. See git log once initialized
"""
garmin_device.py -- detect a mounted Garmin Edge, back up its Activity
Profiles, stage an edit, and push a patched profile back via NewFiles.

This is a REUSABLE LIBRARY LAYER, independent of any GUI -- it wraps
the platform-specific "find the device" logic behind one function
(find_garmin_root) so everything downstream (backup, staging, write,
eject, remount-wait) works identically regardless of OS. Both the
macOS and Windows halves of find_garmin_root are now implemented (see
_find_garmin_root_windows(), added 2026-08-17) -- nothing else in this
file needed to change to support it, confirming the design's original
premise. The Windows half is NOT YET independently confirmed against
real hardware (Doug has Windows 11 access lined up for testing) --
see that function's own docstring for what's still open.

Automates the exact manual sequence used throughout this project's
testing: detect device -> back up Sports/*.fit -> let the user pick a
profile -> dump its current screens -> stage a patched copy -> verify
the device is still mounted -> write to NewFiles -> prompt eject ->
wait for remount -> (caller can then re-dump to verify).

Design choices, and why:
- Backups and staged edits live under a caller-supplied working
  directory (NOT /tmp) so they survive reboots and are easy to find
  again -- matches the user's explicit request.
- Every staged edit is tagged with which backup it was derived from
  (a small .lineage.json sidecar) -- this project hit a real bug
  earlier (v5/v6 chaining mistake) from losing track of which pulled
  copy a patch was built against. This makes that mistake structurally
  harder to repeat.
- Ejecting the device is NEVER done silently -- see eject_device().
  Given how much this project has driven home the stakes of a bad
  device write, the tool confirms the write succeeded and tells the
  user it's safe to eject, rather than running diskutil on its own
  initiative without an explicit confirmation step.
- write_to_newfiles() always reads back what it just wrote and confirms
  it's byte-for-byte identical before returning success -- catches
  filesystem/USB corruption before it ever reaches the device's own
  NewFiles import logic.
"""
import os
import re
import sys
import shutil
import time
import json
import string
import platform
import subprocess
from datetime import datetime, timedelta

SPORTS_SUBDIR = "Sports"
NEWFILES_SUBDIR = "NewFiles"
BACKUPS_SUBDIR = "Backups"  # lives inside Sports on the device itself


class GarminDeviceError(Exception):
    pass


# --- Platform-specific device discovery ------------------------------
#
# find_garmin_root() is the ONLY function that needs a platform-specific
# implementation. Everything else in this file operates purely on the
# resolved root path and has no OS-specific logic at all.

def _has_expected_structure(path):
    sports = os.path.join(path, SPORTS_SUBDIR)
    newfiles = os.path.join(path, NEWFILES_SUBDIR)
    return os.path.isdir(sports) and os.path.isdir(newfiles)


def _find_garmin_root_macos():
    """
    Scan /Volumes for a mounted volume with the expected Garmin
    structure (a Sports/ and a NewFiles/ directory). Structure-based
    rather than name-based, so it works regardless of what the user
    has named the volume.

    Checks TWO levels: some devices expose Sports/NewFiles directly at
    the volume root; others (confirmed via real hardware -- an Edge
    530 mounted as /Volumes/GARMIN/Garmin/Sports, one extra nesting
    level) put them inside an intermediate subfolder. Rather than
    hardcode that subfolder's name (it might not always be "Garmin"
    on every model), this checks every immediate subdirectory of each
    candidate volume generically.
    """
    volumes_dir = "/Volumes"
    if not os.path.isdir(volumes_dir):
        return None
    for name in os.listdir(volumes_dir):
        candidate = os.path.join(volumes_dir, name)
        if not os.path.isdir(candidate):
            continue

        # Level 1: Sports/NewFiles directly at the volume root
        if _has_expected_structure(candidate):
            return candidate

        # Level 2: Sports/NewFiles one level down, inside any subfolder
        # (e.g. /Volumes/GARMIN/Garmin/Sports on this project's actual
        # test hardware -- an Edge 530)
        try:
            subentries = os.listdir(candidate)
        except PermissionError:
            continue
        for sub in subentries:
            sub_path = os.path.join(candidate, sub)
            if os.path.isdir(sub_path) and _has_expected_structure(sub_path):
                return sub_path

    return None


def _find_garmin_root_windows():
    """
    Scan available drive letters (C: through Z: -- A:/B: skipped,
    historically floppy drives, essentially never relevant on modern
    hardware and safe to skip) for the same Sports/ + NewFiles/
    structure check _find_garmin_root_macos() uses, at both the drive
    root and one level of subfolder (mirroring macOS's own two-level
    check, since real Edge 530 hardware nests Sports/NewFiles one
    folder down under a mounted volume there -- confirmed via Doug's
    real Mac; whether Windows exposes the same nesting or puts them
    flat at the drive letter is unconfirmed, hence checking both).

    Deliberately uses plain os.path.exists()/os.listdir() drive-letter
    iteration rather than a Windows-specific API (e.g.
    win32api.GetLogicalDriveStrings()) -- avoids adding a new
    dependency (pywin32) beyond what install.sh already installs
    (garmin-fit-sdk, wxPython), at the minor cost of checking 24 drive
    letters unconditionally instead of only the ones actually in use.
    That's a handful of cheap filesystem stat calls, not a real
    performance concern.

    A drive letter with a card reader/similar and no media inserted
    can raise OSError on access on some systems rather than just
    failing os.path.exists() cleanly -- caught and skipped like any
    other inaccessible drive, same defensive posture as
    _find_garmin_root_macos()'s PermissionError handling.

    NOT YET independently confirmed against real Windows hardware --
    Doug has Windows 11 access lined up for testing (2026-08-17). This
    function's actual behavior on a real Edge 530 plugged into a real
    Windows machine -- including the flat-vs-nested question above --
    is the first thing that testing pass should establish.
    """
    for letter in string.ascii_uppercase:
        if letter in ("A", "B"):
            continue
        drive = f"{letter}:\\"
        try:
            if not os.path.exists(drive):
                continue
        except OSError:
            continue

        # Level 1: Sports/NewFiles directly at the drive root
        if _has_expected_structure(drive):
            return drive

        # Level 2: Sports/NewFiles one level down, inside any subfolder
        # -- mirrors _find_garmin_root_macos()'s own two-level check
        try:
            subentries = os.listdir(drive)
        except OSError:
            continue
        for sub in subentries:
            sub_path = os.path.join(drive, sub)
            try:
                if os.path.isdir(sub_path) and _has_expected_structure(sub_path):
                    return sub_path
            except OSError:
                continue

    return None


def find_garmin_root():
    """
    Return the filesystem root of the mounted Garmin device, or None if
    no device is currently connected. Raises GarminDeviceError on an
    unsupported platform.
    """
    system = platform.system()
    if system == "Darwin":
        return _find_garmin_root_macos()
    elif system == "Windows":
        return _find_garmin_root_windows()
    else:
        raise GarminDeviceError(f"Unsupported platform: {system!r}")


def is_device_connected():
    return find_garmin_root() is not None


# --- Profile listing ---------------------------------------------------

def list_profiles(garmin_root):
    """Return a sorted list of .fit profile filenames in Sports/ (live device, not a backup)."""
    sports_dir = os.path.join(garmin_root, SPORTS_SUBDIR)
    return sorted(f for f in os.listdir(sports_dir) if f.lower().endswith(".fit"))


DEVICE_INFO_FILENAME = "Device.fit"  # sits at garmin_root top level, NOT inside Sports/


def get_device_info(garmin_root):
    """
    Read Device.fit (top-level, separate from any profile) for device
    identification -- manufacturer, product, software version, serial
    number if present. Intended for display on the initial detect
    screen, BEFORE any profile is selected, so a user with more than
    one Garmin can confirm they've connected the right one.

    Returns a dict, e.g.:
        {'manufacturer': 'garmin', 'garmin_product': 'edge_530',
         'software_version': 981, 'serial_number': 1234567890}
    Missing fields are simply absent from the dict rather than raising.
    Returns None if Device.fit doesn't exist at the expected path (in
    case some device/firmware doesn't have one -- unconfirmed, only
    tested against Doug's real hardware so far).
    """
    device_fit_path = os.path.join(garmin_root, DEVICE_INFO_FILENAME)
    if not os.path.exists(device_fit_path):
        return None

    # Imported here, not at module level, so garmin_device.py's other
    # functions (detect/backup/stage/deploy/eject) don't require the
    # SDK to be installed just to be importable -- only this one does.
    from fit_dump import decode_file

    messages = decode_file(device_fit_path)
    info = {}

    file_id = messages.get("file_id_mesgs")
    if file_id:
        m = file_id[0]
        for key in ("manufacturer", "garmin_product", "serial_number"):
            if key in m:
                info[key] = m[key]

    file_creator = messages.get("file_creator_mesgs")
    if file_creator:
        m = file_creator[0]
        if "software_version" in m:
            info["software_version"] = m["software_version"]

    return info


# --- startup.txt (custom boot message) ----------------------------------
#
# CONFIRMED via Doug's own real Edge 530 (2026-08-14, direct ls -l/cat of
# the mounted device): startup.txt sits directly in the Garmin folder --
# i.e. at garmin_root itself, the SAME level as Sports/NewFiles/Settings,
# no extra nesting. Unlike every other write in this file, it does NOT
# go through NewFiles at all -- it's a plain direct overwrite while the
# device is mounted. The file's own on-device comment confirms this:
# "Allow one full power cycle after editing for your message to be
# updated" -- a full power cycle (off, then on), not just an eject/
# remount, since a boot-time message can't re-render without an actual
# boot. Independently corroborated by a DC Rainmaker how-to
# (dcrainmaker.com, 2013) describing the identical edit-and-save
# workflow with no eject step at all beyond a normal safe-remove.
#
# NOT a .fit file -- plain text, Garmin's own template shipping with
# HTML-style <!-- --> instructional comments above a <display=N>
# directive (minimum seconds the message is shown) and the free-form
# message text itself. The device is documented (developer reference,
# gplama.com, cited independently in a 2020 DC Rainmaker comment) to
# cap this at 256 characters, 7-bit ASCII only, and roughly 5-7 visible
# lines depending on model/firmware -- NOT independently confirmed on
# real hardware by this project, and Doug has separately noted that
# different-width characters wrap at different character counts, so
# character/line counts here are a rough typing aid, not a guarantee
# of how the device will actually render the message.

STARTUP_TXT_FILENAME = "startup.txt"  # lives at garmin_root itself, NOT inside Sports/
STARTUP_TXT_MAX_CHARS = 256           # developer-documented reference limit, not confirmed on real hardware by this project
STARTUP_TXT_MAX_LINES = 6             # ditto -- rough guide, actual wrap point is character-width-dependent (Doug, 2026-08-14)

_DISPLAY_DIRECTIVE_RE = re.compile(r"<display\s*=\s*(\d+)\s*>")


def read_startup_txt(garmin_root):
    """
    Read startup.txt from garmin_root (device root, not Sports/). Returns
    the raw text content, or None if the file doesn't exist (not
    guaranteed present on every device/firmware -- unconfirmed either
    way beyond Doug's own Edge 530). Decoded as 7-bit ASCII with
    errors='replace' so a read can never raise on an unexpected byte --
    this is a read/display path, not a validation path.

    A leading UTF-8 BOM (the 3-byte sequence EF BB BF), if present, is
    stripped BEFORE decoding -- real reported bug (2026-08-16, Doug):
    even after the smart-char fix below, 3 literal "?" characters kept
    reappearing at the very front of the file's first (preserved,
    never-retyped) header comment line, invisible in the GUI's own
    message editor since that only shows the editable message text,
    only found by opening the raw file in BBEdit. Root cause: decoding
    with errors='replace' turns each of the BOM's 3 individually-
    invalid-for-ASCII bytes into its own U+FFFD replacement character;
    those 3 characters then ride along through parse_startup_txt()'s
    "preserve header byte-for-byte" split (preserved from the DECODED
    string, not the raw bytes -- there was never a byte-for-byte
    guarantee against something already corrupted at decode time), and
    write_startup_txt()'s ASCII-only encode turns each into a literal
    "?" byte on save -- exactly 3, exactly at the start of the file,
    matching Doug's report precisely. This is a DIFFERENT mechanism
    from the smart-quote bug (which affects freshly-TYPED text); the
    smart-char fix correctly stopped NEW corruption from typing, but
    couldn't clean up a BOM already sitting in the file from an earlier
    save (e.g. an editor that defaults to "UTF-8 with BOM"), and since
    the header is carried forward unchanged on every subsequent write,
    that one BOM would otherwise keep re-manifesting as the same 3
    "?" forever. Doug confirmed manually removing the "?" via BBEdit
    and re-saving stopped them from reappearing on a later gui_app
    edit -- consistent with this theory (a clean re-save with no BOM
    breaks the cycle) but the BOM's original source is still unknown.
    Stripping it here means a BOM in the source file is now a silent
    no-op rather than a self-perpetuating corruption once this file
    passes through this toolkit at all, whether or not the BOM's cause
    is ever pinned down.

    Line endings are normalized to plain '\\n' (CRLF and lone CR both
    collapsed) before returning -- real reported bug (2026-08-14): the
    GUI's message editor showed a blank line between every real line of
    Doug's own existing message, even though the same file opened
    cleanly with no blank lines in BBEdit and vi. Both of those editors
    (like most modern text editors) silently auto-detect and normalize
    CRLF line endings on open, so a CRLF file looks identical to an LF
    file in either one -- this project has no independent byte-level
    confirmation the file is actually CRLF (no hex dump taken), but
    it's the single explanation that fits both halves of the report
    (invisible everywhere except this one widget) and matches a
    well-documented wx.TextCtrl behavior: feeding it a string that
    already contains '\\r\\n' can result in each embedded '\\r'
    contributing its own line break on top of the '\\n' that follows
    it, i.e. exactly a blank-line-per-line rendering. Normalizing here,
    at the single read entry point, fixes the display regardless of
    which theory is exactly right, and is safe either way -- a file
    that was already LF-only is completely unaffected (the replace()
    calls below are then a no-op). NOTE: saving via write_startup_txt()
    always writes '\\n' line endings from this point on (build_startup_
    txt() has always joined with '\\n'), so any file edited and saved
    through this toolkit gets its line endings normalized to LF as a
    side effect, even if it started out CRLF -- not expected to matter
    to the device's own boot-message renderer, but flagged here since
    it's a real (harmless, in all evidence so far) behavior change from
    a plain byte-for-byte round-trip.
    """
    path = os.path.join(garmin_root, STARTUP_TXT_FILENAME)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    if data.startswith(b"\xef\xbb\xbf"):  # UTF-8 BOM -- see docstring
        data = data[3:]
    text = data.decode("ascii", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_startup_txt(content):
    """
    Split raw startup.txt content into (header, display_seconds, message)
    for a friendlier edit form. Garmin's own template always places one
    final "Type your message on the next line" comment immediately
    before the free-form message text (confirmed against Doug's own
    real startup.txt, 2026-08-14) -- so splitting at the LAST '-->' in
    the file cleanly separates Garmin's own instructional comments +
    the <display=N> directive (header, preserved byte-for-byte) from
    the actual message (message, the only part meant to be freely
    edited).

    display_seconds is pulled out of header via regex; None if no
    <display=N> directive is found (an unrecognized template shape) --
    callers should leave it unset/unchanged in that case rather than
    guessing a value.

    Never raises: an unparseable file (no '-->' anywhere) just yields
    header == "" and message == the whole file, so the caller still has
    something usable, only degraded to "edit the whole thing as one
    blob" rather than the split view.
    """
    last_comment_end = content.rfind("-->")
    if last_comment_end == -1:
        return "", None, content
    split_at = last_comment_end + len("-->")
    header = content[:split_at]
    message = content[split_at:].lstrip("\n")
    match = _DISPLAY_DIRECTIVE_RE.search(header)
    display_seconds = int(match.group(1)) if match else None
    return header, display_seconds, message


def build_startup_txt(header, display_seconds, message):
    """
    Reassemble startup.txt content from parse_startup_txt()'s pieces.
    display_seconds (if not None) is spliced back into the EXACT header
    text via the same directive regex -- everything else in header
    (comment wording, spacing, blank lines) is preserved byte-for-byte
    from what was originally read. message is appended after a SINGLE
    newline (no blank line) -- matching Garmin's own real template
    exactly (confirmed against Doug's actual startup.txt, 2026-08-14:
    the message starts on the very next line after the last comment,
    no gap), not just an assumed format. Headlessly round-trip-tested:
    parse_startup_txt() followed by build_startup_txt() with no changes
    reproduces the original file byte-for-byte.
    """
    if display_seconds is not None:
        header = _DISPLAY_DIRECTIVE_RE.sub(f"<display = {display_seconds}>", header, count=1)
    return header.rstrip("\n") + "\n" + message.rstrip("\n") + "\n"


# Common Cocoa/macOS "smart" text substitutions (smart quotes, smart
# dashes, smart ellipsis) mapped back to their plain-ASCII equivalents.
# Real reported bug (2026-08-16, Doug): after a routine startup.txt
# edit, three "?" characters appeared on one line and "..." on another
# line was replaced with a SINGLE "?" -- even though Doug never typed
# a "?" anywhere. Root cause: write_startup_txt() below has always
# encoded with content.encode("ascii", errors="replace"), and
# wx.TextCtrl on macOS is backed by Cocoa's NSTextView, which silently
# auto-substitutes typed text by default -- three periods "..." become
# a single U+2026 ellipsis character as you type, straight quotes
# become curly ones, a double hyphen becomes an em dash, etc. Each of
# those single Unicode characters then hit the ASCII-only encode and
# became exactly one "?" -- matching the reported pattern precisely
# (the ellipsis became ONE "?", not three, ruling out a byte-level/
# UTF-8 explanation and pointing straight at one non-ASCII CHARACTER
# per substitution). Not independently byte-confirmed via a hex dump
# of Doug's exact before/after files, but this mechanism reproduces
# the reported symptom pattern exactly and is directly traceable to
# this file's own encode call, so it's treated as confirmed. Applied
# in write_startup_txt() below -- the single write entry point shared
# by the GUI (StartupTxtPanel.on_save()) and the `startup-txt --write`
# CLI subcommand -- so typed text round-trips correctly regardless of
# which smart substitution macOS silently applied. Any character NOT
# in this table is still replaced with "?" on write, unchanged, honest
# fallback for a genuinely unsupported character -- the GUI's existing
# non-ASCII warning (StartupTxtPanel._update_warning()) still flags
# anything that slips through this table.
_SMART_CHAR_REPLACEMENTS = {
    "‘": "'",    # left single quotation mark
    "’": "'",    # right single quotation mark / apostrophe
    "“": '"',    # left double quotation mark
    "”": '"',    # right double quotation mark
    "–": "-",    # en dash
    "—": "--",   # em dash
    "…": "...",  # horizontal ellipsis
}


def _normalize_smart_chars(text):
    """Reverse common macOS smart-substitution characters back to their
    plain-ASCII originals -- see _SMART_CHAR_REPLACEMENTS above."""
    for smart, plain in _SMART_CHAR_REPLACEMENTS.items():
        text = text.replace(smart, plain)
    return text


def write_startup_txt(garmin_root, content, working_dir):
    """
    Overwrite startup.txt directly on the device -- NOT a NewFiles
    write (see the section comment above for why: this file's own
    on-device text confirms a direct overwrite + full power cycle is
    the real mechanism, no import step involved). Backs up any existing
    file first into working_dir/backups/<timestamp>/startup.txt,
    matching this project's general backup-before-overwrite discipline
    -- reuses the SAME backups/ folder structure backup_profiles() uses
    (list_backup_history() only ever looks for a specific filename
    within each timestamped folder, so mixing a startup.txt backup in
    alongside profile backups is harmless).

    content is passed through _normalize_smart_chars() before encoding
    (v0.12.3, real bug fix -- see that function's comment) so common
    macOS smart-substitution characters (curly quotes, en/em dash,
    ellipsis) round-trip as their original ASCII characters instead of
    silently becoming "?" on write.

    Returns the backup path, or None if there was no existing file to
    back up (e.g. this is the very first time startup.txt is ever set
    by this tool).
    """
    path = os.path.join(garmin_root, STARTUP_TXT_FILENAME)
    backup_path = None
    if os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(working_dir, "backups", timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, STARTUP_TXT_FILENAME)
        shutil.copy2(path, backup_path)

    with open(path, "wb") as f:
        f.write(_normalize_smart_chars(content).encode("ascii", errors="replace"))

    return backup_path


# --- Backup -------------------------------------------------------------

def backup_profiles(garmin_root, working_dir):
    """
    Copy every profile in Sports/ (top-level only -- does NOT descend
    into the device's own Sports/Backups/) to a fresh timestamped
    folder under working_dir/backups/. Returns {profile_filename: backup_path}.
    """
    sports_dir = os.path.join(garmin_root, SPORTS_SUBDIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(working_dir, "backups", timestamp)
    os.makedirs(backup_dir, exist_ok=True)

    result = {}
    for filename in list_profiles(garmin_root):
        src = os.path.join(sports_dir, filename)
        dst = os.path.join(backup_dir, filename)
        shutil.copy2(src, dst)
        result[filename] = dst

    print(f"Backed up {len(result)} profile(s) to {backup_dir}", file=sys.stderr)
    return result


def list_backup_history(working_dir, profile_filename):
    """
    List every backup of profile_filename found under
    working_dir/backups/<timestamp>/, newest first -- the data behind
    the GUI's "Restore from Backup..." picker. Each backup_profiles()
    call creates one fresh timestamped folder containing ALL profiles
    backed up at that moment, so this walks every such folder and
    picks out the ones that actually contain profile_filename (an
    older timestamp might predate that profile existing on the
    device, or backup_profiles() might have been called while a
    different set of profiles was present).

    De-duplicates consecutive entries with IDENTICAL bytes: since
    backup_profiles() runs on every visit to the GUI's profile list
    (not just when something changed), a profile that hasn't been
    touched on the device accumulates many byte-identical timestamped
    backups over the course of a session. Collapsing runs of identical
    bytes down to just the newest one keeps the history meaningful --
    one entry per REAL change -- without ever losing a genuinely
    distinct backup.

    Returns a list of (timestamp_str, backup_path) tuples, newest
    first. timestamp_str is backup_profiles()'s own
    "%Y%m%d_%H%M%S" folder name -- sorts correctly as a plain string,
    no parsing needed for ordering.
    """
    backups_root = os.path.join(working_dir, "backups")
    if not os.path.isdir(backups_root):
        return []

    candidates = []
    for entry in os.listdir(backups_root):
        path = os.path.join(backups_root, entry, profile_filename)
        if os.path.isfile(path):
            candidates.append((entry, path))
    candidates.sort(key=lambda t: t[0], reverse=True)  # newest first

    deduped = []
    last_bytes = None
    for timestamp, path in candidates:
        with open(path, "rb") as f:
            data = f.read()
        if data != last_bytes:
            deduped.append((timestamp, path))
            last_bytes = data
    return deduped


def list_backed_up_profile_filenames(working_dir):
    """
    Return the set of every .fit profile filename that appears in ANY
    backup folder under working_dir/backups/ -- i.e. every profile
    this toolkit has ever backed up, regardless of whether it's still
    present on the device right now. Backs the GUI's "Restore a
    Deleted Profile..." entry point: the caller subtracts whatever
    list_profiles(garmin_root) (or the GUI's already-fresh
    frame.known_profiles) currently returns, and whatever's left is a
    profile that used to exist and might be worth restoring.

    Filters to filenames ending in ".fit" (list_profiles()'s own
    convention) -- write_startup_txt() backs up startup.txt into this
    SAME working_dir/backups/<timestamp>/ folder structure, so without
    this filter a boot-message backup would get mistaken for a deleted
    profile.
    """
    backups_root = os.path.join(working_dir, "backups")
    if not os.path.isdir(backups_root):
        return set()

    names = set()
    for entry in os.listdir(backups_root):
        folder = os.path.join(backups_root, entry)
        if not os.path.isdir(folder):
            continue
        for filename in os.listdir(folder):
            if filename.lower().endswith(".fit"):
                names.add(filename)
    return names


def _format_bytes(n):
    """Plain human-readable byte count (e.g. "12.3 MB") -- no dependency, used by
    both the CLI's prune-backups summary and gui_app.py's cleanup dialog."""
    size = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024


def prune_old_backups(working_dir, older_than_days, dry_run=True):
    """
    Delete (or, if dry_run, just report) every working_dir/backups/
    <timestamp>/ folder whose OWN timestamp -- parsed from its folder
    name, not filesystem mtime -- is older than older_than_days from
    now. Backup retention/pruning, Doug's go-ahead (2026-08-25):
    backups accumulate indefinitely with nothing to clean them up (see
    PROJECT_NOTES.md Open Items "Backup retention/pruning" -- flagged
    since v0.11.0, deliberately deferred out of MVP). Doug's own real
    usage numbers (~1098 backed-up .fit files, ~4-5GB, over this
    project's entire prior history) confirmed disk footprint was never
    the real problem -- staleness/tidiness over a long project lifetime
    is. Design chosen from three options put to Doug: (1) time-based
    folder deletion [CHOSEN], (2) keep-latest-N-per-profile, (3)
    keep-only-the-single-latest-backup. (2) was rejected as needlessly
    complex -- each backups/<timestamp>/ folder is a full snapshot
    across EVERY profile present at that moment (see backup_profiles()),
    not one folder per profile, so per-profile retention would mean
    deleting individual files out of a shared folder rather than whole
    folders, plus awkward interaction with list_backup_history()'s
    existing consecutive-byte-identical display dedup. (3) was rejected
    as cutting against this toolkit's whole safety-net design --
    Restore-from-Backup exists specifically to go back further than
    "the most recent one," and Doug's own numbers showed disk space
    was never the actual constraint that would justify it. Deliberately
    NOT automatic -- Doug's choice: manual-only, triggered by a real
    user action (gui_app.py's "Clean Up Old Backups..." button, or this
    module's own `prune-backups` CLI subcommand), same posture as every
    other destructive action in this toolkit (Restore, permanent Remove,
    Favorite overwrite) -- no silent background deletion of backup
    history, ever.

    Uses the folder's NAME (backup_profiles()'s own "%Y%m%d_%H%M%S"
    convention) rather than filesystem mtime to decide age -- more
    robust, since mtime can be reset by anything that copies/restores
    the working directory (a fresh git checkout, a Time Machine
    restore, etc.), while the embedded timestamp is always correct by
    construction. Any folder whose name DOESN'T parse as that format is
    left alone entirely -- skipped, not counted, not touched --
    defensive against anything unexpected ever ending up in this
    directory.

    Returns a list of (folder_name, size_bytes) tuples for every folder
    that was (dry_run=False) or would be (dry_run=True, the default)
    removed, oldest first. Each folder is deleted as a single atomic
    unit (shutil.rmtree) -- it's a self-contained point-in-time
    snapshot, so there's no partial-folder bookkeeping to get wrong.
    """
    backups_root = os.path.join(working_dir, "backups")
    if not os.path.isdir(backups_root):
        return []

    cutoff = datetime.now() - timedelta(days=older_than_days)
    candidates = []
    for entry in os.listdir(backups_root):
        path = os.path.join(backups_root, entry)
        if not os.path.isdir(path):
            continue
        try:
            folder_time = datetime.strptime(entry, "%Y%m%d_%H%M%S")
        except ValueError:
            continue  # not one of ours -- skip, don't touch
        if folder_time >= cutoff:
            continue  # not old enough yet
        size = sum(
            os.path.getsize(os.path.join(dirpath, f))
            for dirpath, _, filenames in os.walk(path)
            for f in filenames
        )
        candidates.append((entry, size))

    candidates.sort(key=lambda t: t[0])  # oldest first

    if not dry_run:
        for entry, _ in candidates:
            shutil.rmtree(os.path.join(backups_root, entry))

    return candidates


# --- Staging for edit (with lineage tracking) ---------------------------

def stage_for_edit(profile_filename, backup_path, working_dir):
    """
    Copy a backed-up profile into working_dir/staging/ as the starting
    point for a patch, tagged with a .lineage.json sidecar recording
    exactly which backup it came from. This is the fix for the v5/v6
    chaining mistake from earlier in this project -- it should not be
    possible to lose track of which pulled copy a patch was built on.
    Returns the staged file path.
    """
    staging_dir = os.path.join(working_dir, "staging")
    os.makedirs(staging_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem, ext = os.path.splitext(profile_filename)
    staged_name = f"{stem}_staged_{timestamp}{ext}"
    staged_path = os.path.join(staging_dir, staged_name)
    shutil.copy2(backup_path, staged_path)

    lineage = {
        "profile_filename": profile_filename,
        "source_backup": os.path.abspath(backup_path),
        "staged_at": datetime.now().isoformat(),
    }
    with open(staged_path + ".lineage.json", "w") as f:
        json.dump(lineage, f, indent=2)

    print(f"Staged {profile_filename} for editing: {staged_path}", file=sys.stderr)
    print(f"  (lineage: derived from {lineage['source_backup']})", file=sys.stderr)
    return staged_path


def check_lineage(patched_path, expected_source_backup):
    """
    Sanity check before writing to the device: does this patched file's
    lineage sidecar (if present) actually trace back to the backup we
    expect? Returns True if OK, False if there's a mismatch or no
    lineage info at all. Caller decides whether a False result should
    block the write or just warn.
    """
    lineage_path = patched_path + ".lineage.json"
    if not os.path.exists(lineage_path):
        # also check if it was derived from a staged file with its own lineage
        return None  # unknown -- no lineage info available at all
    with open(lineage_path) as f:
        lineage = json.load(f)
    return os.path.abspath(lineage["source_backup"]) == os.path.abspath(expected_source_backup)


# --- Write to device via NewFiles ---------------------------------------

def write_to_newfiles(garmin_root, patched_path, target_profile_filename,
                       working_dir=None):
    """
    Copy patched_path into the device's NewFiles/ folder, using the
    EXACT filename of the profile being replaced (this matters -- the
    device matches by filename during import). Reads the file back
    immediately afterward and confirms it's byte-for-byte identical to
    what was written, to catch USB/filesystem corruption before it
    ever reaches the device's own import logic. Raises GarminDeviceError
    on any mismatch or if the device disconnects mid-write.

    Safety net (working_dir, optional): if a profile currently exists
    on the device under target_profile_filename, it is backed up to
    working_dir/backups/<timestamp>/ BEFORE being overwritten -- same
    folder-naming convention backup_profiles() uses, so this backup is
    immediately browsable via the normal Restore-from-Backup picker,
    not a separate parallel mechanism. Every GUI-driven write already
    gets this protection for free (visiting the profile list always
    runs backup_profiles() first), but a bare CLI `deploy` call bypasses
    that -- this closes the one real gap: deploying straight to an
    existing filename with no prior `backup` call would otherwise
    overwrite that profile with no safety net at all. If working_dir is
    omitted, behavior is unchanged from before (no backup attempted) --
    kept optional rather than required so existing scripts/callers
    don't break.
    """
    if find_garmin_root() != garmin_root:
        raise GarminDeviceError(
            "Device is no longer at the expected mount point -- "
            "was it disconnected? Re-run detection before writing."
        )

    newfiles_dir = os.path.join(garmin_root, NEWFILES_SUBDIR)
    dest_path = os.path.join(newfiles_dir, target_profile_filename)

    if working_dir is not None:
        sports_dir = os.path.join(garmin_root, SPORTS_SUBDIR)
        current_path = os.path.join(sports_dir, target_profile_filename)
        if os.path.isfile(current_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(working_dir, "backups", timestamp)
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, target_profile_filename)
            shutil.copy2(current_path, backup_path)
            print(f"Backed up existing {target_profile_filename} before "
                  f"overwrite -> {backup_path}", file=sys.stderr)

    with open(patched_path, "rb") as f:
        intended_bytes = f.read()

    shutil.copy2(patched_path, dest_path)

    with open(dest_path, "rb") as f:
        written_bytes = f.read()

    if written_bytes != intended_bytes:
        raise GarminDeviceError(
            f"Write verification FAILED -- {dest_path} does not match what "
            f"was sent. Do not eject the device. Try the write again."
        )

    print(f"Wrote and verified {target_profile_filename} -> {dest_path} "
          f"({len(written_bytes)} bytes, byte-for-byte confirmed)", file=sys.stderr)
    return dest_path


# --- Eject / remount ------------------------------------------------------

def _volume_mount_point(path):
    """
    Given any path under /Volumes/<X>/..., return /Volumes/<X> -- the
    actual disk volume mount point, which is what `diskutil eject`
    needs. This can genuinely differ from garmin_root: on real
    hardware, garmin_root is /Volumes/GARMIN/Garmin (the Sports/
    NewFiles structure sits one level deeper than the volume itself),
    but the actual ejectable volume is /Volumes/GARMIN. Confirmed via
    real testing -- `diskutil eject` on the deeper garmin_root path
    does not work; only the volume root does.
    """
    parts = path.split(os.sep)
    # parts[0] is '' (path starts with /), parts[1] should be 'Volumes'
    if len(parts) >= 3 and parts[1] == "Volumes":
        return os.sep.join(parts[:3])
    return path  # not a /Volumes path (e.g. non-macOS) -- best effort fallback


def eject_device(garmin_root, auto_eject=False):
    """
    Tell the user it's safe to eject, and optionally (only with
    explicit confirmation, never silently) actually run the eject
    command on their behalf. Ejects the actual VOLUME mount point
    (see _volume_mount_point), not garmin_root directly -- those can
    differ when the Garmin structure is nested inside the volume.
    """
    print()
    print("Write complete and verified. It is now safe to eject the Garmin.")
    print("The device will automatically restart once ejected, which is")
    print("when the NewFiles import actually happens.")
    print()
    print(">>> IMPORTANT (confirmed via real device testing): once that")
    print(">>> automatic restart finishes, the device does NOT remount as")
    print(">>> storage on its own -- it needs ONE PRESS of the power button")
    print(">>> to bring it back into mass-storage mode. Without that press,")
    print(">>> it settles into charging mode instead and will never remount.")
    print()

    eject_target = _volume_mount_point(garmin_root) if platform.system() == "Darwin" else garmin_root

    if not auto_eject:
        print(f"Eject '{eject_target}' yourself (Finder, or `diskutil eject "
              f"\"{eject_target}\"`) whenever you're ready.")
        return False

    answer = input(f"Eject '{eject_target}' now? [y/N] ").strip().lower()
    if answer != "y":
        print("Not ejecting -- eject manually whenever you're ready.")
        return False

    if platform.system() == "Darwin":
        subprocess.run(["diskutil", "eject", eject_target], check=True)
        print("Ejected.")
        return True
    else:
        raise GarminDeviceError("Auto-eject only implemented for macOS -- eject manually.")


def wait_for_remount(timeout_seconds=180, poll_interval=2):
    """
    Poll for the Garmin device to reappear after a restart (e.g. after
    ejecting to trigger a NewFiles import). Returns the new root path,
    or None if it doesn't reappear within timeout_seconds.
    """
    print("Waiting for the Garmin to reconnect...", file=sys.stderr)
    print("(Once its automatic restart finishes, press the power button ONCE", file=sys.stderr)
    print(" to bring it back into mass-storage mode -- confirmed via real", file=sys.stderr)
    print(" device testing that it does NOT remount on its own, and instead", file=sys.stderr)
    print(" settles into charging mode without that press.)", file=sys.stderr)
    print(f"Polling for up to {timeout_seconds}s...", file=sys.stderr)
    elapsed = 0
    while elapsed < timeout_seconds:
        root = find_garmin_root()
        if root is not None:
            print(f"Reconnected at {root}", file=sys.stderr)
            return root
        time.sleep(poll_interval)
        elapsed += poll_interval
    print("Timed out waiting for the device to reconnect -- if you haven't", file=sys.stderr)
    print("pressed the power button yet, that's likely why. Try again.", file=sys.stderr)
    return None


# --- CLI -------------------------------------------------------------------

def _cli():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("detect", help="Check whether a Garmin device is currently connected")

    p_list = sub.add_parser("list", help="List profiles on the connected device")

    p_backup = sub.add_parser("backup", help="Back up all profiles to a working directory")
    p_backup.add_argument("working_dir")

    p_stage = sub.add_parser("stage", help="Stage a backed-up profile for editing")
    p_stage.add_argument("profile_filename")
    p_stage.add_argument("backup_path")
    p_stage.add_argument("working_dir")

    p_deploy = sub.add_parser("deploy", help="Write a patched profile to NewFiles and prompt eject")
    p_deploy.add_argument("patched_path")
    p_deploy.add_argument("target_profile_filename")
    p_deploy.add_argument("--working-dir", default=None,
                           help="If given, back up whatever profile currently "
                                "exists under target_profile_filename to "
                                "working_dir/backups/<timestamp>/ before "
                                "overwriting it. Omit to skip this safety net "
                                "(e.g. if you already ran a manual `backup`).")
    p_deploy.add_argument("--auto-eject", action="store_true",
                           help="Offer to eject automatically (still asks for confirmation)")

    p_screens = sub.add_parser("screens", help="Show current screens for a profile directly "
                                                  "from the connected device (read-only, no "
                                                  "backup/staging needed)")
    p_screens.add_argument("profile_filename")
    p_screens.add_argument("-v", "--verbose", action="store_true")

    p_wait = sub.add_parser("wait-for-remount", help="Poll for the device to reconnect")
    p_wait.add_argument("--timeout", type=int, default=180)

    p_history = sub.add_parser("backup-history", help="List backup history for one profile "
                                                         "(newest first, de-duplicated)")
    p_history.add_argument("profile_filename")
    p_history.add_argument("working_dir")

    p_startup = sub.add_parser("startup-txt", help="View, or overwrite (--write), the "
                                                      "device's startup.txt boot message")
    p_startup.add_argument("working_dir", help="Used for the pre-write backup only; ignored when just viewing")
    p_startup.add_argument("--write", metavar="FILE",
                            help="Overwrite startup.txt with the contents of FILE "
                                 "(backs up the existing file first)")

    p_deleted = sub.add_parser("deleted-profiles", help="List profile filenames backed up "
                                                           "before but no longer present on "
                                                           "the connected device")
    p_deleted.add_argument("working_dir")

    p_prune = sub.add_parser("prune-backups", help="Delete backups/<timestamp>/ folders "
                                                      "older than a given number of days")
    p_prune.add_argument("working_dir")
    p_prune.add_argument("--older-than-days", type=int, default=30,
                          help="Delete backup folders older than this many days (default: 30)")
    p_prune.add_argument("--dry-run", action="store_true",
                          help="Report what would be deleted without deleting anything")
    p_prune.add_argument("--yes", action="store_true",
                          help="Skip the interactive confirmation prompt")

    args = parser.parse_args()

    if args.command == "detect":
        root = find_garmin_root()
        if root:
            print(f"Garmin device found at: {root}")
            info = get_device_info(root)
            if info is None:
                print(f"  (no {DEVICE_INFO_FILENAME} found -- device info unavailable)")
            else:
                for key, label in [("manufacturer", "Manufacturer"),
                                    ("garmin_product", "Product"),
                                    ("serial_number", "Serial"),
                                    ("software_version", "Software version")]:
                    if key in info:
                        print(f"  {label}: {info[key]}")
        else:
            print("No Garmin device currently connected.")
            sys.exit(1)

    elif args.command == "list":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        for name in list_profiles(root):
            print(name)

    elif args.command == "backup":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        backup_profiles(root, args.working_dir)

    elif args.command == "stage":
        stage_for_edit(args.profile_filename, args.backup_path, args.working_dir)

    elif args.command == "deploy":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        if args.working_dir is None:
            print("NOTE: no --working-dir given -- if a profile already "
                  "exists on the device under this filename, it will be "
                  "overwritten with NO automatic backup. Pass --working-dir "
                  "(or run `backup` yourself first) to get the same safety "
                  "net every GUI-driven write already has.", file=sys.stderr)
        write_to_newfiles(root, args.patched_path, args.target_profile_filename,
                           working_dir=args.working_dir)
        eject_device(root, auto_eject=args.auto_eject)

    elif args.command == "screens":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        live_path = os.path.join(root, SPORTS_SUBDIR, args.profile_filename)
        if not os.path.exists(live_path):
            print(f"No such profile on device: {args.profile_filename}", file=sys.stderr)
            sys.exit(1)
        # Reuse fit_dump.py's already-validated screens display directly, rather
        # than reimplementing it -- this reads the LIVE file in place, read-only.
        fit_dump_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_dump.py")
        cmd = [sys.executable, fit_dump_path, "screens", live_path]
        if args.verbose:
            cmd.append("-v")
        subprocess.run(cmd)

    elif args.command == "wait-for-remount":
        wait_for_remount(timeout_seconds=args.timeout)

    elif args.command == "backup-history":
        history = list_backup_history(args.working_dir, args.profile_filename)
        if not history:
            print(f"No backups of {args.profile_filename} found under "
                  f"{args.working_dir}/backups/", file=sys.stderr)
        for timestamp, path in history:
            print(f"{timestamp}  {path}")

    elif args.command == "startup-txt":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        if args.write:
            with open(args.write, "r") as f:
                new_content = f.read()
            backup_path = write_startup_txt(root, new_content, args.working_dir)
            if backup_path:
                print(f"Wrote startup.txt (previous version backed up to {backup_path})")
            else:
                print("Wrote startup.txt (no previous file existed to back up)")
            print()
            print("Safely eject the device, then allow ONE FULL POWER CYCLE "
                  "(off, then on) for the new message to take effect -- "
                  "confirmed via the file's own on-device comment; this is "
                  "a direct overwrite, not a NewFiles import, so no eject-"
                  "triggered restart happens on its own.")
        else:
            content = read_startup_txt(root)
            if content is None:
                print("No startup.txt found on this device.", file=sys.stderr)
                sys.exit(1)
            print(content, end="")

    elif args.command == "deleted-profiles":
        root = find_garmin_root()
        if not root:
            print("No Garmin device currently connected.", file=sys.stderr)
            sys.exit(1)
        live = set(list_profiles(root))
        backed_up = list_backed_up_profile_filenames(args.working_dir)
        deleted = sorted(backed_up - live)
        if not deleted:
            print("No backed-up profiles found that are missing from the device.", file=sys.stderr)
        for name in deleted:
            print(name)

    elif args.command == "prune-backups":
        candidates = prune_old_backups(args.working_dir, args.older_than_days, dry_run=True)
        if not candidates:
            print(f"Nothing to prune -- no backups/<timestamp>/ folders older "
                  f"than {args.older_than_days} day(s).")
        else:
            total_bytes = sum(size for _, size in candidates)
            print(f"{len(candidates)} backup folder(s) older than "
                  f"{args.older_than_days} day(s), {_format_bytes(total_bytes)} total:")
            for entry, size in candidates:
                print(f"  {entry}  ({_format_bytes(size)})")
            if args.dry_run:
                print("\n(--dry-run: nothing deleted)")
            else:
                if not args.yes:
                    answer = input(
                        f"\nDelete these {len(candidates)} folder(s), freeing "
                        f"{_format_bytes(total_bytes)}? [y/N] "
                    ).strip().lower()
                    if answer != "y":
                        print("Not deleting -- no changes made.")
                        sys.exit(0)
                prune_old_backups(args.working_dir, args.older_than_days, dry_run=False)
                print(f"\nDeleted {len(candidates)} folder(s), freed {_format_bytes(total_bytes)}.")


if __name__ == "__main__":
    _cli()
