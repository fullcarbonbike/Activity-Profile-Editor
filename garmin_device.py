#!/usr/bin/env python3
__version__ = "0.11.0"  # add list_backup_history() -- lists every backup of one profile under working_dir/backups/<timestamp>/, newest first, de-duplicating consecutive byte-identical entries (backup_profiles() runs on every visit to the GUI's profile list, not just on real changes, so an untouched profile accumulates many identical timestamped backups per session). Backs the GUI's "Restore from Backup..." picker (gui_app.py v0.15.0) and a new `backup-history` CLI subcommand. Prior entry (v0.10.0): add get_device_info() reading Device.fit -- for the GUI's initial detect screen, before profile selection. See git log once initialized
"""
garmin_device.py -- detect a mounted Garmin Edge, back up its Activity
Profiles, stage an edit, and push a patched profile back via NewFiles.

This is a REUSABLE LIBRARY LAYER, independent of any GUI -- it wraps
the platform-specific "find the device" logic behind one function
(find_garmin_root) so everything downstream (backup, staging, write,
eject, remount-wait) works identically regardless of OS. Only the
macOS half of find_garmin_root is implemented; the Windows half is a
clearly-marked stub for whoever picks that up (see WindowsNotImplemented
below) -- nothing else in this file should need to change to support it.

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
import sys
import shutil
import time
import json
import platform
import subprocess
from datetime import datetime

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
    TODO (Windows support -- not yet implemented, needs testing on
    real Windows hardware): scan available drive letters (A: through
    Z:, e.g. via `win32api.GetLogicalDriveStrings()` or plain
    `os.path.exists(f"{letter}:\\")` iteration) for the same Sports/ +
    NewFiles/ structure check used on macOS. Nothing else in this file
    should need to change -- find_garmin_root() just needs this
    function filled in.
    """
    raise NotImplementedError(
        "Windows device detection not yet implemented. "
        "See _find_garmin_root_windows() docstring for what's needed -- "
        "everything else in garmin_device.py is OS-agnostic and should "
        "work unchanged once this one function is filled in."
    )


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

def write_to_newfiles(garmin_root, patched_path, target_profile_filename):
    """
    Copy patched_path into the device's NewFiles/ folder, using the
    EXACT filename of the profile being replaced (this matters -- the
    device matches by filename during import). Reads the file back
    immediately afterward and confirms it's byte-for-byte identical to
    what was written, to catch USB/filesystem corruption before it
    ever reaches the device's own import logic. Raises GarminDeviceError
    on any mismatch or if the device disconnects mid-write.
    """
    if find_garmin_root() != garmin_root:
        raise GarminDeviceError(
            "Device is no longer at the expected mount point -- "
            "was it disconnected? Re-run detection before writing."
        )

    newfiles_dir = os.path.join(garmin_root, NEWFILES_SUBDIR)
    dest_path = os.path.join(newfiles_dir, target_profile_filename)

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
        write_to_newfiles(root, args.patched_path, args.target_profile_filename)
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


if __name__ == "__main__":
    _cli()
