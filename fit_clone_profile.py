#!/usr/bin/env python3
__version__ = "1.0.1"  # New constant, Doug's real on-device test (2026-08-19): PROFILE_NAME_MAX_CHARS = 15 -- Garmin's own Activity Profile name editor hard-blocks typing a 16th character (confirmed directly: typing past 15 switches straight to the checkmark/complete control instead of accepting more input). This is a real, CONFIRMED device UI limit -- distinct from, and much stricter than, NAME_FIELD_SIZE's 31-usable-byte storage capacity below, which patch_profile_name() already enforces safely (raises ValueError, never corrupts). A name between 16 and 31 bytes patches through this tool's raw byte write with no error -- Garmin's own software could never have produced one, so how the device actually renders it (visually truncated? something worse?) is untested territory this toolkit has no reason to create. Backs gui_app.py's new ClonePanel hard block (v0.19.9) -- Doug's explicit call, not a guess: this mirrors an independently-confirmed on-device fact the exact same way NO_SHOW_TOGGLE_TYPES (fit_patch.py) does, so it's enforced the same way (a real block, not soft guidance like startup.txt's character/line counts, which were never independently confirmed on real hardware). No functional change to patch_profile_name() itself -- this is a new reference constant only, the GUI does the enforcing. Prior entry (v1.0.0): initial version.
"""
fit_clone_profile.py -- patch an Activity Profile's display name
(sport_mesgs[0].name, mesg_num=12, field 3), for cloning a profile
under a new identity.

Separate tool from fit_patch.py because this touches a completely
different message (sport_mesgs, mesg_num=12 -- a standard, SDK-known
message, unlike data_screen). Same design principle throughout this
project: locate exact byte offsets, patch only what's changing,
recompute the trailing CRC, leave everything else untouched.

Intended workflow for cloning a profile under a new name:
    1. Back up / stage a copy of an existing profile (garmin_device.py)
    2. python3 fit_clone_profile.py staged.fit cloned.fit --name "NewName"
    3. garmin_device.py deploy cloned.fit <NEW_FILENAME>.fit
       -- IMPORTANT: use a filename that does NOT match any existing
       profile on the device. Deploying under an EXISTING profile's
       filename overwrites that profile; a genuinely new filename is
       what (hopefully) creates a new profile via NewFiles import.
    4. Restart, check whether the device created a real new profile
       or did something else -- this exact behavior is UNTESTED as of
       this writing, that's the point of trying it.
"""
import sys
import struct

from fit_raw_walk import parse_fit
from fit_crc import fit_crc

SPORT_MESG_NUM = 12
NAME_FIELD_DEF_NUM = 3
NAME_FIELD_SIZE = 32  # fixed-width, confirmed via real file inspection

# CONFIRMED via direct on-device testing (Doug, 2026-08-19): Garmin's own
# Activity Profile name editor hard-blocks typing a 16th character --
# typing past this limit switches straight to the checkmark/complete
# control instead of accepting more input. This is a real device UI
# limit, not a guess or a developer-documented reference figure -- and
# it's much stricter than NAME_FIELD_SIZE's 31-usable-byte storage
# capacity above (which patch_profile_name() already enforces safely).
# A name between 16 and 31 bytes patches through this tool's raw byte
# write with no error at all -- Garmin's own software could never have
# produced one, so nothing has ever tested how the device renders it.
# gui_app.py's ClonePanel hard-blocks Create Clone past this length,
# for that reason -- not just a courtesy warning.
PROFILE_NAME_MAX_CHARS = 15


def find_sport_message(messages):
    for m in messages:
        if m["kind"] == "data" and m.get("mesg_num") == SPORT_MESG_NUM:
            return m
    return None


def field_byte_range(msg, field_def_num):
    cursor = msg["start"] + 1  # skip record header byte
    for (def_num, size, base_type, raw) in msg["fields"]:
        if def_num == field_def_num:
            return (cursor, cursor + size)
        cursor += size
    raise KeyError(f"field {field_def_num} not present in this message")


def patch_profile_name(input_path, output_path, new_name):
    """
    Patch sport_mesgs[0].name to new_name. Raises ValueError if
    new_name (UTF-8 encoded) doesn't fit in the fixed 32-byte field
    (31 usable bytes + a null terminator, matching how the device's
    own null-padded string storage works).
    """
    encoded = new_name.encode("utf-8")
    if len(encoded) > NAME_FIELD_SIZE - 1:
        raise ValueError(
            f"Name {new_name!r} is {len(encoded)} bytes encoded -- "
            f"must fit in {NAME_FIELD_SIZE - 1} bytes (the field is a "
            f"fixed {NAME_FIELD_SIZE}-byte null-padded string)."
        )
    padded = encoded + b"\x00" * (NAME_FIELD_SIZE - len(encoded))

    with open(input_path, "rb") as f:
        data = bytearray(f.read())

    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_sport_message(messages)
    if msg is None:
        raise ValueError(f"No sport_mesgs (mesg_num={SPORT_MESG_NUM}) found in {input_path}")

    start, end = field_byte_range(msg, NAME_FIELD_DEF_NUM)
    if end - start != NAME_FIELD_SIZE:
        raise ValueError(
            f"Unexpected name field size ({end - start} bytes, expected "
            f"{NAME_FIELD_SIZE}) -- refusing to patch, file structure may "
            f"differ from what this tool assumes."
        )

    old_bytes = bytes(data[start:end])
    data[start:end] = padded

    body = bytes(data[:-2])
    new_crc = fit_crc(body)
    data[-2:] = struct.pack("<H", new_crc)

    with open(output_path, "wb") as f:
        f.write(data)

    old_name = old_bytes.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
    print(f"Patched profile name: {old_name!r} -> {new_name!r}", file=sys.stderr)
    return output_path


def _cli():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--name", required=True, help="new profile display name")
    args = parser.parse_args()

    try:
        patch_profile_name(args.input_file, args.output_file, args.name)
    except (ValueError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
