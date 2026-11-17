#!/usr/bin/env python3
__version__ = "1.1.2"  # RIDE_TYPES IS NOT PER-MODEL (2026-11-16, section D1). The nine ride types were read off an 840 and the #171 scope said that if the 530 differed, this table would be per-model "like so much else here" -- the field-ID work (#165) having established that data FIELDS vary by model. Doug checked: the 530 offers THE SAME NINE, including the later enum additions Gravel (46), Emountain (47), Commute (48) and Tour (49), on the OLDER of the two devices. So the comment no longer reads as a provisional 840 observation and nothing in the picker needs qualifying by model. Two models, one owner, one account -- not asserted as universal for a 540/1040/1050, but no longer known-dubious either. Comment only; no code change. Prior entry (1.1.1): RIDE_TYPES CARRIES THE DEVICE FILENAME SEGMENT (2026-11-11, Doug's bench finding, #171 section A). A fourth column, plus filename_prefix_for(), so the GUI's clone-filename suggestion can follow the DESTINATION ride type instead of the source's filename -- see gui_app 0.34.1 for the bug. All nine segments are OBSERVED, not inferred: Road, Mountain, Indoor and Cyclocross from the profile corpus; Gravel and Ebike from rev 205; Commute, Tour and Emountain from rev 206, where three profiles were created from the 840's own templates to settle exactly this. FIVE OF THE NINE ARE EMPTY and they split cleanly by enum value -- the firmware has a filename label for sub_sports 6, 7, 8 and 11 and none for 28, 46, 47, 48 or 49, all later additions to the SDK enum, so its label table was evidently never extended past the original cycling types. No behaviour change to any write path; the generated file is still byte-identical to the hand-patched one that passed all ten hardware steps. Prior entry (1.1.0): RIDE TYPE IS NOW CLONEABLE (2026-11-09, #171). patch_profile() replaces patch_profile_name() as the write path and can set sub_sport (mesg 12 field 1) as well as the display name, in ONE pass with ONE CRC recompute; patch_profile_name() stays as a delegating wrapper so there is one write path, and its output is byte-identical to the old code across 25 corpus profiles. PROVEN ON HARDWARE BEFORE BUILT, which is why this is a feature and not an experiment: a hand-patched GRAVEL profile was accepted by an Edge 840, kept its sub_sport across a restart, labelled the ride it recorded, and Garmin Connect filed that ride under Gravel in both Reports and Goals (Doc revs 204-212, all ten steps of TEST_PLAN_171_sub_sport.md). The generated file is byte-identical to the hand-patched one that passed. RIDE_TYPES IS A TABLE, NOT A RULE: the device's nine Ride Types map to SDK names that only follow "<label>_cycling" twice out of nine -- road, mountain and cyclocross are bare nouns, commuting/mixed_surface/e_bike_fitness/e_bike_mountain are different words entirely -- so deriving the name from the label would silently write the wrong number, the same failure shape as the field-ID batch error in revs 83-84. NINE, NOT THE SDK'S EIGHTEEN: spin, downhill, recumbent, hand_cycling, track_cycling, bmx, esport, enduro and e_bike_enduro are cycling sub_sports the 840's menu does not offer, and writing one would make a profile whose type the device's own settings UI cannot express. --sub-sport takes the SDK name because a wrong integer is silent and a wrong name is caught; the device's menu label is accepted too, with a note saying which spelling is canonical. NEVER A SIDE EFFECT: sub_sport is written only when explicitly asked for, because a wrong value silently reroutes which Connect goal a profile's rides count against. Every byte range is resolved before any byte is written, so an unexpected layout is refused outright rather than left half-patched (same discipline as fit_odometer.py's resolve_plan). Prior entry (1.0.2): read_profile_name() ADDED (2026-10-27, #168). The counterpart to patch_profile_name(), which could write the display name since the initial commit while nothing could read it back. Needed because the Edge RENAMES an imported profile from its own sport and display name (Doc rev 182), so the filename a caller deployed under is gone afterwards and the display name is the only handle that survives. Never raises -- a missing sport message, an unreadable file or a non-FIT file all return None, because callers are asking "which of these is mine" across a directory that may hold anything. Prior entry (1.0.1): New constant, Doug's real on-device test (2026-08-19): PROFILE_NAME_MAX_CHARS = 15 -- Garmin's own Activity Profile name editor hard-blocks typing a 16th character (confirmed directly: typing past 15 switches straight to the checkmark/complete control instead of accepting more input). This is a real, CONFIRMED device UI limit -- distinct from, and much stricter than, NAME_FIELD_SIZE's 31-usable-byte storage capacity below, which patch_profile_name() already enforces safely (raises ValueError, never corrupts). A name between 16 and 31 bytes patches through this tool's raw byte write with no error -- Garmin's own software could never have produced one, so how the device actually renders it (visually truncated? something worse?) is untested territory this toolkit has no reason to create. Backs gui_app.py's new ClonePanel hard block (v0.19.9) -- Doug's explicit call, not a guess: this mirrors an independently-confirmed on-device fact the exact same way NO_SHOW_TOGGLE_TYPES (fit_patch.py) does, so it's enforced the same way (a real block, not soft guidance like startup.txt's character/line counts, which were never independently confirmed on real hardware). No functional change to patch_profile_name() itself -- this is a new reference constant only, the GUI does the enforcing. Prior entry (v1.0.0): initial version.
"""
fit_clone_profile.py -- patch an Activity Profile's display name
(sport_mesgs[0].name, mesg_num=12, field 3) and/or its ride type
(sub_sport, field 1), for cloning a profile under a new identity.

Separate tool from fit_patch.py because this touches a completely
different message (sport_mesgs, mesg_num=12 -- a standard, SDK-known
message, unlike data_screen). Same design principle throughout this
project: locate exact byte offsets, patch only what's changing,
recompute the trailing CRC, leave everything else untouched.

Intended workflow for cloning a profile under a new name:
    1. Back up / stage a copy of an existing profile (garmin_device.py)
    2. python3 fit_clone_profile.py staged.fit cloned.fit --name "NewName"
       -- add --sub-sport gravel_cycling to make the clone a different
       ride type at the same time (see RIDE_TYPES below)
    3. garmin_device.py deploy cloned.fit <NEW_FILENAME>.fit
       -- IMPORTANT: use a filename that does NOT match any existing
       profile on the device. Deploying under an EXISTING profile's
       filename overwrites that profile; a genuinely new filename is
       what creates a new profile via NewFiles import.
    4. Restart and check the device.

CHANGING THE RIDE TYPE. Proven end to end on an Edge 840 (Doc revs
204-212): the device accepts a written sub_sport, keeps it across a
restart, labels the ride it records with it, and Garmin Connect files
that ride under the new category in both Reports and Goals. That last
part is the one that matters -- Connect's Goals page filters on sport
plus sub_sport, so the ride type decides which goal a ride counts
against.

WHAT A CLONE IS NOT. The device's own templates differ by ride type: a
natively-created Emountain profile carries Assist Mode and Smart
Travel Range screens, a Tour profile carries Distance to Next. A clone
carries the SOURCE profile's screens and settings, so it is that
profile wearing a different type -- not what the device would have
built for that type. Usually exactly what you want when cloning; worth
knowing when you are not.

EXPECT THE DEVICE TO REORGANISE. On import the device reassigns
message_index whenever the arrangement it receives differs from the
arrangement it holds, which a clone's always does (Doc rev 210).
Screen identities, field arrays and display order all survive, and the
device repairs mesg 170's Connect IQ placements itself. Compare
profiles by f10, never by message_index.
"""
import sys
import struct

from fit_raw_walk import parse_fit
from fit_crc import fit_crc

SPORT_MESG_NUM = 12
NAME_FIELD_DEF_NUM = 3
NAME_FIELD_SIZE = 32  # fixed-width, confirmed via real file inspection

SUB_SPORT_FIELD_DEF_NUM = 1
SUB_SPORT_FIELD_SIZE = 1  # uint8, confirmed across 68 profiles

# The device's own "Ride Type" menu, as read off an Edge 840 when
# creating a profile (Doug, 2026-11-06, Doc rev 205) and CONFIRMED
# IDENTICAL on an Edge 530 (2026-11-16, section D1, Doc rev 217).
#
#   (device label, FIT SDK sub_sport name, sub_sport value)
#
# ⚠ NOT PER-MODEL, which is the opposite of what was expected. The
# scope for #171 said that if the 530's menu differed, this table
# would be per-model "like so much else here" -- the field-ID
# availability work (#165) having established that data FIELDS vary by
# model. Ride types do not, across these two: the 530 is the OLDER
# device and still offers all nine, including the later enum additions
# Gravel (46), Emountain (47), Commute (48) and Tour (49).
#
# Two models, one owner, one account. That is not proof for a
# 540/1040/1050, so the table is not asserted as universal -- but it
# is no longer a known-dubious 840 reading either, and nothing here
# needs qualifying by model.
#
# THIS MUST STAY A TABLE. The obvious rule -- "<label>_cycling" -- is
# wrong for seven of the nine: only indoor_cycling and gravel_cycling
# carry the suffix, three are bare nouns, and four are different words
# entirely. Deriving the SDK name from the label would silently write
# the wrong number. Doc rev 206; same failure shape as the field-ID
# batch error in revs 83-84.
#
# NINE ENTRIES, NOT THE SDK'S EIGHTEEN. The FIT SDK tags nine further
# sub_sports as cycling -- spin, downhill, recumbent, hand_cycling,
# track_cycling, bmx, esport, enduro, e_bike_enduro -- and the 840's
# menu offers none of them. Writing one would produce a profile whose
# type the device's own settings UI cannot express, which is the
# inverse of the problem this feature exists to solve. Garmin Connect
# does appear to know some of them (Doug saw BMX and handcycling in
# its activity-type list), so this may be worth revisiting -- but not
# before someone has confirmed on hardware what the device does with
# a type it has no menu entry for.
#
# Order is the device's menu order, so the GUI picker matches what the
# rider sees on the Edge.
# The fourth column is the middle segment the DEVICE puts in the
# filename it generates, `Cycling<segment><DisplayName>.fit` (rev 187).
# Every one of the nine is MEASURED, not inferred:
#
#   Road, Mountain, Indoor, Cyclocross   from the profile corpus
#   Gravel, Ebike                        rev 205, from Doug's own device
#   Commute, Tour, Emountain             rev 206, three profiles created
#                                        from the 840's templates on
#                                        purpose to settle exactly this
#
# FIVE OF THE NINE ARE EMPTY, and they split cleanly by enum value: the
# device has a label for sub_sports 6, 7, 8 and 11 and none for 28, 46,
# 47, 48 or 49 -- all later additions to the SDK's sub_sport enum. The
# firmware's label table was evidently never extended past the original
# cycling types (rev 206). Nothing depends on predicting the filename
# (#170 removed the last thing that did) -- this is here so the clone
# panel's SUGGESTION matches what the device will do, which is the whole
# point of #169.
RIDE_TYPES = (
    ("Road",       "road",             7, "Road"),
    ("Mountain",   "mountain",         8, "Mountain"),
    ("Indoor",     "indoor_cycling",   6, "Indoor_Cycle"),
    ("Gravel",     "gravel_cycling",  46, ""),
    ("Cyclocross", "cyclocross",      11, "Cyclocross"),
    ("Commute",    "commuting",       48, ""),
    ("Tour",       "mixed_surface",   49, ""),
    ("Ebike",      "e_bike_fitness",  28, ""),
    ("Emountain",  "e_bike_mountain", 47, ""),
)

SUB_SPORT_BY_SDK_NAME = {sdk: num for (_l, sdk, num, _seg) in RIDE_TYPES}
RIDE_TYPE_BY_SUB_SPORT = {num: label for (label, _s, num, _seg) in RIDE_TYPES}
SDK_NAME_BY_SUB_SPORT = {num: sdk for (_l, sdk, num, _seg) in RIDE_TYPES}
FILENAME_SEGMENT_BY_SUB_SPORT = {num: seg for (_l, _s, num, seg) in RIDE_TYPES}


def filename_prefix_for(sub_sport):
    """
    The `Cycling<segment>` prefix the device would generate for a
    profile of this ride type, or None if the sub_sport is not one of
    the nine.

    Returns the bare "Cycling" for the five types the device has no
    label for -- which is correct, not a failure: `CyclingGRAVEL.fit`
    is exactly what the device writes.
    """
    if sub_sport not in FILENAME_SEGMENT_BY_SUB_SPORT:
        return None
    return "Cycling" + FILENAME_SEGMENT_BY_SUB_SPORT[sub_sport]


def ride_type_label(sub_sport):
    """
    The device's menu label for a sub_sport value, or None if it is not
    one of the nine the device offers.

    Returns None rather than guessing, because an unknown value here
    means either a model with a different menu or a profile written by
    something other than the device -- and in both cases inventing a
    label would be worse than saying nothing.
    """
    return RIDE_TYPE_BY_SUB_SPORT.get(sub_sport)


def read_sub_sport(path):
    """
    Return a profile's sub_sport value (mesg 12 field 1), or None if
    the file has no sport message or cannot be read.

    Same never-raises contract as read_profile_name(), and for the same
    reason: callers scan directories that may hold anything.

    NOTE on the companion field: `sport` (field 0) is deliberately not
    exposed. It is 2 on every profile in the corpus and nothing has
    ever suggested it should change (Doc rev 203).
    """
    try:
        messages = parse_fit(path)[0]
    except Exception:
        return None
    msg = find_sport_message(messages)
    if msg is None:
        return None
    try:
        start, end = field_byte_range(msg, SUB_SPORT_FIELD_DEF_NUM)
    except KeyError:
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if end - start != SUB_SPORT_FIELD_SIZE:
        return None
    return data[start]

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


def read_profile_name(path):
    """
    Return a profile's DISPLAY NAME -- the thing the rider sees in the
    device's profile list -- or None if the file has no sport message
    or cannot be read.

    Added 2026-10-27 (#168). The counterpart to patch_profile_name(),
    which has been able to write this field since the initial commit
    while nothing could read it back.

    WHY IT MATTERS. Doc rev 182: the Edge RENAMES a profile on import,
    generating `Cycling<Sport><DisplayName>.fit` from the file's own
    contents, so the filename a caller deployed under is gone
    afterwards. The display name is what survives, which makes it the
    only reliable way to find a profile again on the device.

    NEVER RAISES. A missing sport message, an unreadable file or a
    non-FIT file all return None, because every caller is asking "which
    of these files is the one I want" over a directory that may hold
    anything -- an exception there would be a crash, not an answer.
    """
    try:
        messages = parse_fit(path)[0]
    except Exception:
        return None
    msg = find_sport_message(messages)
    if msg is None:
        return None
    try:
        start, end = field_byte_range(msg, NAME_FIELD_DEF_NUM)
    except KeyError:
        return None
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    raw = data[start:end]
    # Everything up to the first NUL. The field is fixed-width and
    # null-padded, and the padding is NOT guaranteed to be zeros --
    # Doc rev 116 found uninitialised junk after the terminator in a
    # Totals.fit name field, which is what misled the SDK there.
    return raw.split(b"\x00")[0].decode("ascii", "replace")


def patch_profile(input_path, output_path, new_name=None, sub_sport=None):
    """
    Patch a profile's display name and/or its sub_sport, in ONE pass
    with ONE CRC recompute.

    Both arguments are optional, but at least one must be given. Each
    is patched only when explicitly supplied -- in particular,
    **sub_sport is never changed as a side effect of a name change**,
    because a wrong sub_sport silently reroutes which Garmin Connect
    category a profile's rides count against (Doc revs 206, 212), and
    that is not the kind of thing to do by implication.

    WHY ONE PASS. Patching the two fields with two calls would work,
    but would write the file twice and recompute the CRC twice over a
    file that was briefly inconsistent on disk. The project's standing
    rule is to locate exact byte offsets, patch only what changes, and
    recompute the trailing CRC once at the end.

    sub_sport must be one of the values in RIDE_TYPES -- the nine the
    device's own Ride Type menu offers. Anything else is refused; see
    the RIDE_TYPES comment for why the SDK's wider cycling list is not
    accepted.

    Returns output_path. Raises ValueError on a bad name, a bad
    sub_sport, a missing sport message, or an unexpected field size.
    """
    if new_name is None and sub_sport is None:
        raise ValueError("Nothing to patch -- supply new_name, sub_sport, or both.")

    padded = None
    if new_name is not None:
        encoded = new_name.encode("utf-8")
        if len(encoded) > NAME_FIELD_SIZE - 1:
            raise ValueError(
                f"Name {new_name!r} is {len(encoded)} bytes encoded -- "
                f"must fit in {NAME_FIELD_SIZE - 1} bytes (the field is a "
                f"fixed {NAME_FIELD_SIZE}-byte null-padded string)."
            )
        padded = encoded + b"\x00" * (NAME_FIELD_SIZE - len(encoded))

    if sub_sport is not None:
        if sub_sport not in RIDE_TYPE_BY_SUB_SPORT:
            offered = ", ".join(f"{sdk} ({num})" for (_l, sdk, num, _g) in RIDE_TYPES)
            raise ValueError(
                f"sub_sport {sub_sport!r} is not one of the ride types the "
                f"device offers -- refusing to write it. Accepted: {offered}."
            )

    with open(input_path, "rb") as f:
        data = bytearray(f.read())

    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_sport_message(messages)
    if msg is None:
        raise ValueError(f"No sport_mesgs (mesg_num={SPORT_MESG_NUM}) found in {input_path}")

    # Resolve EVERY byte range before writing ANY of them, so a file
    # with an unexpected layout is refused outright rather than left
    # half-patched. Same discipline as fit_odometer.py's resolve_plan().
    plan = []
    if padded is not None:
        start, end = field_byte_range(msg, NAME_FIELD_DEF_NUM)
        if end - start != NAME_FIELD_SIZE:
            raise ValueError(
                f"Unexpected name field size ({end - start} bytes, expected "
                f"{NAME_FIELD_SIZE}) -- refusing to patch, file structure may "
                f"differ from what this tool assumes."
            )
        plan.append(("name", start, end, padded))
    if sub_sport is not None:
        start, end = field_byte_range(msg, SUB_SPORT_FIELD_DEF_NUM)
        if end - start != SUB_SPORT_FIELD_SIZE:
            raise ValueError(
                f"Unexpected sub_sport field size ({end - start} bytes, "
                f"expected {SUB_SPORT_FIELD_SIZE}) -- refusing to patch."
            )
        plan.append(("sub_sport", start, end, bytes([sub_sport])))

    messages_out = []
    for (what, start, end, payload) in plan:
        old = bytes(data[start:end])
        data[start:end] = payload
        if what == "name":
            old_name = old.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
            messages_out.append(f"Patched profile name: {old_name!r} -> {new_name!r}")
        else:
            old_ss = old[0]
            messages_out.append(
                f"Patched sub_sport: {SDK_NAME_BY_SUB_SPORT.get(old_ss, old_ss)} "
                f"-> {SDK_NAME_BY_SUB_SPORT[sub_sport]} "
                f"({ride_type_label(sub_sport)} on the device)"
            )
            if old_ss != sub_sport:
                # Doc rev 206: the device's templates differ by ride
                # type, and a clone carries the SOURCE's screens. The
                # rider gets none of the destination type's template
                # content, and nothing on the device will say so.
                messages_out.append(
                    "  NOTE: the screens in this profile come from the source "
                    "profile, NOT from the device's own template for "
                    f"{ride_type_label(sub_sport)}. A profile created on the "
                    "device would carry that type's default screens instead."
                )

    body = bytes(data[:-2])
    data[-2:] = struct.pack("<H", fit_crc(body))

    with open(output_path, "wb") as f:
        f.write(data)

    for line in messages_out:
        print(line, file=sys.stderr)
    return output_path


def patch_profile_name(input_path, output_path, new_name):
    """
    Patch sport_mesgs[0].name to new_name.

    Kept as the name-only entry point -- it predates patch_profile()
    and has callers (gui_app.py's ClonePanel among them). It delegates,
    so there is one write path rather than two to keep in step.
    """
    return patch_profile(input_path, output_path, new_name=new_name)


def _cli():
    import argparse
    epilog = "Ride types (--sub-sport takes the SDK name):\n" + "\n".join(
        f"  {sdk:<16} {label:<11} (sub_sport {num})"
        for (label, sdk, num, _seg) in RIDE_TYPES
    )
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--name", help="new profile display name")
    parser.add_argument(
        "--sub-sport", dest="sub_sport", metavar="SDK_NAME",
        help="new ride type, by FIT SDK name (e.g. gravel_cycling). "
             "Only ever changed when you pass this -- never as a side "
             "effect of --name. See the list below.",
    )
    args = parser.parse_args()

    if args.name is None and args.sub_sport is None:
        parser.error("nothing to do -- pass --name, --sub-sport, or both")

    # The SDK name is required rather than the number, deliberately: a
    # wrong integer is silent and a wrong name is caught right here.
    sub_sport = None
    if args.sub_sport is not None:
        key = args.sub_sport.strip().lower()
        if key not in SUB_SPORT_BY_SDK_NAME:
            # Accept the device's menu label too, since that is what the
            # rider actually sees -- but say which spelling is canonical.
            by_label = {label.lower(): num for (label, _s, num, _g) in RIDE_TYPES}
            if key in by_label:
                sub_sport = by_label[key]
                print(
                    f"NOTE: {args.sub_sport!r} is the device's menu label; the "
                    f"SDK name is {SDK_NAME_BY_SUB_SPORT[sub_sport]!r}.",
                    file=sys.stderr,
                )
            else:
                names = ", ".join(sdk for (_l, sdk, _n, _g) in RIDE_TYPES)
                parser.error(
                    f"unknown ride type {args.sub_sport!r} -- expected one of: {names}"
                )
        else:
            sub_sport = SUB_SPORT_BY_SDK_NAME[key]

    try:
        patch_profile(args.input_file, args.output_file,
                      new_name=args.name, sub_sport=sub_sport)
    except (ValueError, KeyError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _cli()
