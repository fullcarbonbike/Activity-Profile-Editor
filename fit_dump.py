#!/usr/bin/env python3
__version__ = "2.4.4"  # add 18 confirmed field IDs, 2026-08-10 batch: 7 Lap Dist., 30 Time to Next, 31 Dest. Location, 39 Lap Power, 50 Lap Speed, 57 Avg Lap Time, 61 Total Descent, 62 Dest. Ahead, 63 Time Ahead, 67 Reps to Go, 86 Last Lap Speed, 88 30s VAM, 94 ETA to Next, 95 Odometer, 295 Target Power, 442 Lap VAM, 443 Avg VAM, 445 Asc to Next Crs Pt -- developer arranged two screens to 10 fields each on a real profile specifically for this census, entered/selected each field by its on-device name, then cross-referenced every field's raw ID against its known on-screen position using the GUI (v0.16.4's readability/resize fixes were what made that cross-referencing practical -- see gui_app.py). No collisions with any existing FIELD_ID_NAMES entry (confirmed via grep before insertion). FIELD_ID_NAMES now 105 confirmed entries; KNOWN_UNRESOLVED_IDS still empty. Prior entry (2.4.3): add 1 confirmed field ID (58, Lap Timer) -- surfaced incidentally by real GUI Restore-from-Backup testing (an old 8/3/2026 backup had a field the GUI's picker didn't recognize), confirmed via direct visual comparison against the live device display. FIELD_ID_NAMES now 87 confirmed entries. Prior entry (2.4.2): add 2 confirmed field IDs closing the last open field-ID mystery (84 Last Lap Dist, 87 Last Lap Timer -- note: unrelated numeric coincidence to this entry's field 58, "Last Lap Timer" vs. "Lap Timer" are genuinely distinct fields, not a naming collision), confirmed via a forced-field test deployed successfully through NewFiles -- FIELD_ID_NAMES was 86 confirmed entries; KNOWN_UNRESOLVED_IDS still empty
"""
fit_dump.py - Dump (and diff) Garmin .FIT files for reverse-engineering
undocumented messages/fields, e.g. Edge Sports/<Profile>.fit data-screen
and data-field layout.

Uses garmin_fit_sdk (official Python SDK: `pip install garmin-fit-sdk
--break-system-packages`). Known messages/fields decode with their real
names via the public Profile; anything NOT in the public Profile.xlsx
comes through keyed by its raw numeric global_mesg_num / field number
(e.g. message key "147", field key 254) instead of being dropped -- that
raw numeric output is exactly what you diff to find undocumented
screen/field-layout messages.

USAGE
-----
Dump a single file to a stable, diff-friendly text form:
    python3 fit_dump.py dump baseline_A.fit > A.txt
    python3 fit_dump.py dump baseline_B.fit > B.txt
    diff A.txt B.txt

Or let the script do the dump + diff in one step:
    python3 fit_dump.py diff baseline_A.fit baseline_B.fit

Show only messages the public FIT profile doesn't recognize
(these are your reverse-engineering targets):
    python3 fit_dump.py unknown baseline_A.fit

Notes
-----
- Output is sorted (message key, message occurrence index, field key) so
  that two dumps of files that are semantically identical produce
  byte-identical text, and `diff` only shows what actually changed.
- Multi-value / byte-array fields are rendered as compact repr() so they
  diff cleanly on one line instead of exploding into multiple lines.
- Decoder errors (bad CRC, truncated file, etc.) are printed to stderr
  but don't abort the dump -- partial data is still useful when you're
  poking at a device that might reject a hand-edited file.

GUI reuse
---------
classify_screens() and active_field_ids() are plain, print-free
functions that return Python data structures -- safe to import
directly (`from fit_dump import decode_file, classify_screens,
field_name`) from the GUI or any other in-process consumer, with no
subprocess call and no text to parse back out. cmd_screens() is just
the CLI's own consumer of the same two functions; its printed output
is unchanged by this split.
"""

import sys
import argparse
from garmin_fit_sdk import Decoder, Stream

# [VERIFIED S1] mesg_num=14 == data_screen, one message instance per screen
# slot. Confirmed via byte-level diff of three known-good Road profile
# copies (single isolated field-count edits) and independently re-validated
# against a second, structurally different Gravel profile with zero
# misreads.
DATA_SCREEN_MESG_KEY = "14"

# [VERIFIED S1] Field layout within a data_screen message:
#   254 = message_index (screen slot number, 0-based)
#   3   = active field count (uint8). Key is ABSENT ENTIRELY (not present
#         in the dict at all) on unconfigured/preallocated-but-empty slots
#         -- confirmed via garmin_fit_sdk output, not a literal 255.
#   7   = 10-slot list of field IDs (uint16). Only the first field_count
#         entries are active; trailing entries are leftover/default values
#         or None (SDK's decode of the FIT uint16 invalid sentinel 0xFFFF)
#         and are NOT meaningful past field_count.
#   1, 9, 10, 11 exist but semantics are NOT yet confirmed. Field 1
#   is NOT the enable/disable flag (always 1 on populated slots) -- that
#   mechanism is field 12, see below.
# [VERIFIED S4] field 12 = enabled/disabled flag (uint8). 0 = enabled
#   (shown in the on-device Data Screens list), 1 = disabled/hidden.
#   Confirmed two ways: (a) in the original baseline, Slot 1 (Lap
#   Summary) was the ONLY screen with f12=1, and the developer's own
#   ground-truth device check independently marked that exact screen
#   OFF while every f12=0 screen was ON; (b) toggling Lap Summary's
#   on-device enable switch flipped
#   f12 from 1 -> 0, isolated to this single byte with no other change
#   to the message. This resolves the earlier mystery of why "OFF"
#   screens still carry real, valid field data (they're just marked
#   disabled, not cleared).
# [VERIFIED S3] field 8 = layout_variant (uint8). 0 = default/"A" grid
#   layout for the current field_count; 1 = alternate/"B" layout (e.g.
#   an on-device #6-A -> #6-B change for Slot 4, isolated to this
#   single byte via before/after message diff, confirmed 0 on every
#   never-edited screen in the baseline profile). Only 0/1 confirmed so
#   far -- layouts with more than two named variants (if any exist) may
#   use higher values, unconfirmed.

# Confirmed field-ID -> display name. Built and cross-validated across
# Road, Gravel, and Tourtst profiles -- multiple independent screens
# agreeing on the same ID -> name mapping, plus on-ride visual
# verification for several graph-type fields (see note on 344/346 below).
FIELD_ID_NAMES = {
    0:   "Calories",
    3:   "Cadence",
    4:   "Avg Cadence",
    5:   "Lap Cadence",
    6:   "Distance",
    # 2026-08-10 batch (18 confirmed): the developer arranged two
    # screens to 10 fields each on a real profile specifically for this
    # census, entered/selected each field by its on-device name, then
    # cross-referenced every field's raw ID against its known on-screen
    # position using this toolkit's own GUI -- same direct verification
    # method as every other confirmed entry in this dict, just batched.
    7:   "Lap Dist.",
    9:   "Elevation (ft)",
    36:  "Power",
    37:  "Avg Power",
    38:  "Kilojoules",
    39:  "Lap Power",
    11:  "Percent Grade",
    12:  "Heading",
    13:  "Heart Rate",
    14:  "Avg Heart Rate",
    16:  "%Max Heart Rate",
    17:  "Avg %Max Heart Rate",
    19:  "%Heart Rate Reserve",
    20:  "Avg %HRR",
    22:  "Heart Rate Zone",
    23:  "Heart Rate (Alt)",
    27:  "Distance to Destination",
    28:  "Time to Destination",
    29:  "Distance to Next",
    30:  "Time to Next",
    31:  "Dest. Location",
    48:  "Speed",
    49:  "Avg Speed (Alt)",
    50:  "Lap Speed",
    53:  "Sunrise",
    54:  "Sunset",
    55:  "Elapsed Time",
    56:  "Timer",
    57:  "Avg Lap Time",
    # 58: found on a restored 8/3/2026 CyclingRoadSandbox backup
    # (surfaced by real GUI testing of Restore-from-Backup, v0.15.x --
    # not an active field-ID hunt), unrecognized by the GUI's field
    # picker at the time -- confirmed via direct visual comparison
    # against the live device display, which reads "Lap Timer".
    58:  "Lap Timer",
    59:  "Time of Day (TOD)",
    60:  "Total Ascent",
    61:  "Total Descent",
    62:  "Dest. Ahead",
    63:  "Time Ahead",
    64:  "Calories to Go",
    65:  "Distance to Go",
    66:  "Heart Rate to Go",
    67:  "Reps to Go",
    68:  "Time to Go",
    77:  "VAM",
    78:  "Temperature",
    79:  "3s Power",
    81:  "Normalized Power",
    84:  "Last Lap Dist",
    86:  "Last Lap Speed",
    87:  "Last Lap Timer",
    88:  "30s VAM",
    91:  "Max Speed",
    93:  "ETA at Destination",
    94:  "ETA to Next",
    95:  "Odometer",
    96:  "Battery Level",
    97:  "GPS Signal Strength",
    99:  "Aerobic Training Effect",
    146: "10s Power",
    178: "Gears",
    179: "Front Gear",
    180: "Rear Gear",
    181: "Gear Battery",
    182: "Gear Ratio",
    199: "HR Zone 1 (time)",
    200: "HR Zone 2 (time)",
    201: "HR Zone 3 (time)",
    202: "HR Zone 4 (time)",
    203: "HR Zone 5 (time)",
    216: "WindField Widget",
    257: "Time Standing",
    259: "Time Seated",
    263: "Platform Center Offset",
    266: "Power Phase Right",
    270: "Avg R. Peak Pwr Phase",
    272: "Power Phase Left",
    276: "Avg L. Peak Pwr Phase",
    295: "Target Power",
    # 316/319: found on Gravel's Removed-state Slot 7, unresolved for
    # a long time (no on-device path to identify a Removed screen).
    # Confirmed via direct raw-ID injection test: patched a fresh slot
    # with exactly [316, 319] and visually confirmed on-device.
    316: "Lights Connected",
    319: "Light Mode",
    317: "Light Battery",
    318: "Beam Angle Status",
    320: "Conditioning",
    # 343/344/345/346/368: a Graph-type cluster, confirmed via TWO
    # independent screens (Tourtst Slot 0 [6-B layout] and Slot 16
    # [4-A layout]) plus on-ride photo verification. IMPORTANT: the
    # first pass at this cluster assumed raw field-array position
    # matched on-screen display position, which was WRONG for 344/346
    # -- corrected here after visually verifying on an actual ride
    # which graph was which. Lesson: don't assume array order = display
    # order, especially on B-variant (split) layouts.
    343: "Heart Rate Graph",
    344: "Speed Graph",
    345: "Cadence Graph",
    346: "Power Graph",
    # 348/349: on Tourtst Slot 6 (nav-themed screen), visually read as
    # "Speed"/"Cadence" but marked with a "*" prefix in the on-device
    # editor -- NOT present on 48/3's normal Speed/Cadence fields (e.g.
    # Roadtest's Dashboard screen). Confirmed genuinely distinct from
    # 48/3 by this UI marker, not a duplicate or census row-slip. Exact
    # meaning of the "*" unknown (course/route-derived? estimated?) --
    # named literally after the visible marker rather than guessing.
    348: "Speed *",
    349: "Cadence *",
    368: "Elevation Graph",
    409: "Gear Combo",
    442: "Lap VAM",
    443: "Avg VAM",
    444: "Ascent Remaining",
    445: "Asc to Next Crs Pt",
    486: "Grit",
    487: "Lap Grit",
    488: "Flow",
    489: "Lap Flow",
    491: "Assist Mode",
    492: "Shifting Advice",
    493: "eBike Battery",
    494: "Travel Range",
}

# REMOVED (superseded below): previously had SYSTEM_SLOT_HINTS keyed by
# raw message_index (e.g. {8: "terminator", 10: "GroupTrack"}). CONFIRMED
# WRONG via a real profile (Indoor): slot numbers are NOT stable across
# profiles -- Slot 8 there is a genuine, populated 3-field screen, and
# Slot 10 is a genuine Cadence/Avg Cadence screen, neither remotely
# GroupTrack/terminator-like. That ruled out message_index (f 254) as an
# identity signal -- it's just a slot address, reused freely.
#
# CONFIRMED (side-thread Test 4, 2026-08-04): field 10 (f10), not slot
# number, is a genuine screen TYPE identifier -- global and content-
# independent. Two categories:
#   - Named Garmin screen types get a FIXED numeric code, the same value
#     regardless of profile/template or what content the user has since
#     customized the screen to show (proven: patched Cycling Dynamics'
#     fields via --force, redeployed -- f10 stayed 63, tag marks type,
#     not displayed content).
#   - Plain user-created screens use a per-profile, zero-indexed counter;
#     the on-device editor displays f10=N as "Screen N+1" (confirmed
#     exactly across 6 independent instances on one profile, no
#     exceptions).
# Named types are actively RE-APPLIED, not just inherited from original
# template creation: removing GroupTrack List on-device and re-adding it
# from the device's own named-screen menu brought it back tagged f10=57
# again, not the next free counter value. f9 (display order) and f10
# (identity) are fully independent -- removing a screen renumbers every
# other screen's f9 to close the gap, but f10 is untouched by that same
# operation.
#
# This is what finally makes "how many REAL user screens are left"
# answerable from the file alone -- see fit_patch.py's
# would_hide_last_visible_screen(). GroupTrack itself has TWO independent
# f10 representations: 32 is the actual Conditional runtime record (this
# module's "conditional" bucket, f9 absent); 57 is a separate, always-
# orderable Active placeholder ("GroupTrack List") -- confirmed
# structurally independent via an on-device remove-then-re-add of List
# alone, which left the f10=32 record completely unaffected.
NAMED_SCREEN_TYPES = {
    25:  "Map",
    26:  "Virtual Partner",
    32:  "GroupTrack",       # the real Conditional runtime record
    35:  "Compass",
    44:  "Elevation",
    56:  "Segment",
    57:  "GroupTrack List",  # always-orderable Active placeholder, independent of the f10=32 record above
    63:  "Cycling Dynamics",
    74:  "Lap Summary",
    104: "ClimbPro",
}


def screen_type_name(f10):
    """
    Human-readable screen TYPE name from field 10 (f10) -- NOT the
    screen's current field content (that can be freely customized, e.g.
    a "Map" screen showing Speed/Distance instead of a map overlay -- the
    type tag persists regardless), and NOT its display position (f9).

    Returns a known Garmin type name if f10 matches NAMED_SCREEN_TYPES,
    otherwise the on-device "Screen N" label a plain user-created screen
    actually shows (f10=N displays as "Screen N+1", confirmed exactly --
    see the NAMED_SCREEN_TYPES comment above). Returns None if f10 itself
    is absent -- e.g. a Removed-state screen has no real f10 to report.
    """
    if f10 is None:
        return None
    if f10 in NAMED_SCREEN_TYPES:
        return NAMED_SCREEN_TYPES[f10]
    return f"Screen {f10 + 1}"

# IDs seen in the wild but not yet identified with confidence.
# (84/87 RESOLVED 2026-08-04 -- see FIELD_ID_NAMES: Last Lap Dist/Last
# Lap Timer, confirmed via a forced-field test deployed successfully
# through NewFiles. Previously assumed GroupTrack-related purely by
# association with the f10=32 Conditional record they happened to be
# seen on -- they aren't GroupTrack-specific at all, just two ordinary
# lap-stat fields that record used them for other purposes.)
KNOWN_UNRESOLVED_IDS = set()


def _fmt_value(value):
    """Render a decoded field value as a single stable diff-friendly line."""
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if isinstance(value, float):
        # Avoid float repr jitter across platforms; 6 sig figs is plenty
        # for anything a bike computer setting would encode.
        return f"{value:.6g}"
    return repr(value)


def _sort_key(k):
    # Message/field keys are either strings (known, named) or ints
    # (unknown, raw numeric id). Normalize to a tuple that sorts unknown
    # numeric ids after named ones, and sorts numerically within each group,
    # instead of raising a TypeError when Python tries to compare str to int.
    if isinstance(k, str):
        return (0, k, 0)
    return (1, "", k)


def decode_file(path):
    stream = Stream.from_file(path)
    decoder = Decoder(stream)
    messages, errors = decoder.read(
        apply_scale_and_offset=True,
        convert_datetimes_to_dates=False,   # keep raw epoch ints - more diffable
        convert_types_to_strings=True,      # enum names where the profile knows them
        expand_sub_fields=True,
        expand_components=True,
    )
    for err in errors:
        print(f"[decoder error] {path}: {err}", file=sys.stderr)
    return messages


def render_lines(messages):
    """Turn the messages dict into a flat, sorted list of diff-friendly lines."""
    lines = []
    for mesg_key in sorted(messages.keys(), key=_sort_key):
        occurrences = messages[mesg_key]
        for idx, mesg in enumerate(occurrences):
            for field_key in sorted(mesg.keys(), key=_sort_key):
                value = mesg[field_key]
                lines.append(
                    f"{mesg_key}[{idx}].{field_key} = {_fmt_value(value)}"
                )
    return lines


def is_unknown_mesg_key(k):
    # Known/named messages come back as strings from the SDK profile
    # (e.g. "record", "device_settings"). Unknown ones come back as the
    # raw numeric global_mesg_num, either as int or numeric-looking str.
    if isinstance(k, int):
        return True
    if isinstance(k, str) and k.isdigit():
        return True
    return False


def cmd_dump(args):
    messages = decode_file(args.file)
    for line in render_lines(messages):
        print(line)


def cmd_unknown(args):
    messages = decode_file(args.file)
    unknown = {k: v for k, v in messages.items() if is_unknown_mesg_key(k)}
    if not unknown:
        print("No undocumented (unknown global_mesg_num) messages found.",
              file=sys.stderr)
        return
    for line in render_lines(unknown):
        print(line)
    # Also flag unknown *fields* inside otherwise-known messages -- these
    # are numeric-keyed entries mixed in with named ones.
    print("\n--- unknown fields inside known messages ---", file=sys.stderr)
    for mesg_key, occurrences in messages.items():
        if is_unknown_mesg_key(mesg_key):
            continue
        for idx, mesg in enumerate(occurrences):
            for field_key in mesg.keys():
                if isinstance(field_key, int):
                    print(f"{mesg_key}[{idx}].{field_key} = "
                          f"{_fmt_value(mesg[field_key])}", file=sys.stderr)


def field_name(field_id, terse=False):
    """Return a display name for a field ID, or a clear unknown marker."""
    if field_id is None:
        return "--" if terse else "(empty slot)"
    if field_id in FIELD_ID_NAMES:
        return FIELD_ID_NAMES[field_id]
    if terse:
        return f"id{field_id}?"
    if field_id in KNOWN_UNRESOLVED_IDS:
        return f"UNKNOWN (id={field_id}, previously seen, unresolved)"
    return f"UNKNOWN (id={field_id}, NEW - not seen before)"


def active_field_ids(mesg, field_count):
    """
    Return just the ACTIVE field IDs for one data_screen message, given
    its field_count -- i.e. the meaningful prefix of field 7's 10-slot
    array, with the trailing leftover/sentinel entries dropped. Shared
    by the CLI printer (cmd_screens) and any other consumer (the GUI)
    that wants a screen's real field list without reimplementing this
    slicing logic itself. Pure function, no printing, no side effects.
    """
    raw_ids = mesg.get(7, [])
    return raw_ids[:field_count] if field_count else []


def classify_screens(messages):
    """
    Pure, print-free classification of a decoded FIT file's data_screen
    (mesg 14) occurrences into the three real on-device screen states
    (see SCREEN STATE MODEL in PROJECT_NOTES.md) plus never-configured
    slots. Safe to import and call directly -- e.g. from gui_app.py --
    with no subprocess call and no CLI output to parse back out.

    Returns a dict:
        {
            "orderable":        [(f9, idx, mesg), ...] sorted ascending
                                 by f9 -- this ordering IS the true
                                 on-device display order (confirmed via
                                 --swap-order round-trip testing).
            "conditional":      [(idx, mesg), ...] -- the GroupTrack
                                 Conditional record (f10=32) specifically;
                                 active but exempt from f9 ordering.
            "removed":          [(idx, mesg), ...] -- soft-deleted; content
                                 (f3/f7) preserved ONLY until the next
                                 NewFiles-mediated (toolkit) deploy --
                                 NOT purged by on-device-only editing.
                                 See PROJECT_NOTES.md Screen State Model.
            "unconfigured":     [(idx, mesg), ...] -- no f1==1 signal at
                                 all (f9/f10 absent, f1 not 1), slot never
                                 created. NOTE (v2.3.0 bug fix): this is
                                 NOT gated on field 3 (f3) presence --
                                 some genuine Active screens (e.g. Virtual
                                 Partner, f10=26) have no f3 key at all.
            "unknown_ids_seen": set of field IDs present on this file
                                 that aren't in FIELD_ID_NAMES yet.
        }

    cmd_screens() below is just this function's CLI consumer -- it
    calls classify_screens() and then prints the result. The printed
    CLI output is unchanged by this split.
    """
    occurrences = messages.get(DATA_SCREEN_MESG_KEY, [])

    unknown_ids_seen = set()
    orderable = []    # (f9, slot_idx, mesg) -- real f9, appears in main viewing sequence
    conditional = []  # slot_idx, mesg -- f1=1, f9=None, f10=real (GroupTrack-style, still "on")
    removed = []      # slot_idx, mesg -- f1=0, f9=None, f10=None (content preserved, pulled from sequence)
    unconfigured = [] # slot_idx, mesg -- no f1==1 signal at all (f9/f10 absent, f1 not 1) -- never created

    for m in occurrences:
        idx = m.get(254)
        # BUG FIX (v2.3.0, side-thread finding): field_count (f3) is NOT a
        # reliable configured/unconfigured gate -- some genuine, Active,
        # on-device screens (e.g. Virtual Partner, f10=26) have NO f3 key
        # at all, because they have no editable field list to begin with
        # (their displayed content is firmware-rendered, not read from f7).
        # Confirmed on live RoadClone data and in historical Indoor/
        # Mountain backups carrying the same f10=26 shape with no f3.
        # "Configured" now gates on f1/f9/f10 presence instead; field_count
        # defaults to 0 (not absent) when f3 is missing, which
        # active_field_ids() already treats correctly (falsy -> []).
        field_count = m.get(3)

        f1 = m.get(1)
        f9 = m.get(9)
        f10 = m.get(10)

        if f9 is not None:
            # Real, current display-order stamp -- Active/Display, on the
            # main scrollable sequence, regardless of whether f3 is present.
            orderable.append((f9, idx, m))
        elif f1 == 0:
            # CONFIRMED via live Remove-button test (see fit_patch.1 BUGS):
            # f1 0 + f9/f10 both absent = Removed. Field content (f3/f7)
            # is preserved untouched at the moment of removal -- but see
            # PROJECT_NOTES.md Screen State Model: this is only a soft
            # delete until the NEXT device write of any kind, not a
            # persistently stable state.
            removed.append((idx, m))
        elif f1 == 1 and f10 is not None:
            # f1 == 1, f9 absent, f10 present -- GroupTrack-style: an
            # active feature structurally exempt from the ordering system,
            # not a deleted screen. Confirmed f10=32 for the real GroupTrack
            # Conditional record specifically (distinct from the separate,
            # always-orderable GroupTrack List placeholder at f10=57).
            conditional.append((idx, m))
        else:
            # No f1==1 signal of any kind (f9 absent, f10 absent, f1 not 1)
            # -- genuinely never-created slot, available for --new-slot.
            unconfigured.append((idx, m))
            continue

        active_ids = active_field_ids(m, field_count)
        for fid in active_ids:
            if fid is not None and fid not in FIELD_ID_NAMES:
                unknown_ids_seen.add(fid)

    # Sort by f9 ascending -- CONFIRMED to match real on-device display
    # order (validated against the developer's Gravel profile editor
    # sequence, and against an actual --swap-order device round-trip
    # test). This is what a person sees scrolling through the Active
    # Profile, NOT the raw slot/message_index order.
    orderable.sort(key=lambda t: t[0])

    return {
        "orderable": orderable,
        "conditional": conditional,
        "removed": removed,
        "unconfigured": unconfigured,
        "unknown_ids_seen": unknown_ids_seen,
    }


def cmd_screens(args):
    """
    CLI entry point for `fit_screens.py screens`. Unchanged output from
    prior versions -- this is now just classify_screens() plus the same
    printing logic that used to be inlined here directly.
    """
    messages = decode_file(args.file)
    data = classify_screens(messages)
    verbose = args.verbose

    orderable = data["orderable"]
    conditional = data["conditional"]
    removed = data["removed"]
    unconfigured = data["unconfigured"]
    unknown_ids_seen = data["unknown_ids_seen"]

    def _row(idx, m, field_count, position=None):
        # v2.3.0: field_count can genuinely be None now (Virtual
        # Partner-style screens have no f3 key at all) -- default to 0
        # for display/formatting purposes only.
        field_count = field_count or 0
        active_ids = active_field_ids(m, field_count)
        names = ", ".join(field_name(fid, terse=not verbose) for fid in active_ids)

        layout_variant = m.get(8)
        if verbose:
            if layout_variant == 1:
                layout_col = "B/alternate"
            elif layout_variant == 0:
                layout_col = "A/default"
            elif layout_variant is not None:
                layout_col = f"variant={layout_variant}?"
            else:
                layout_col = "-"
        else:
            layout_col = "B" if layout_variant == 1 else " "

        enabled = m.get(12)
        flag = "OFF" if enabled == 1 else "   "

        # v2.3.0: real screen-type name from f10 -- see NAMED_SCREEN_TYPES.
        type_name = screen_type_name(m.get(10)) or "?"

        pos_col = f"{position:3d}" if position is not None else "  -"
        if verbose:
            line = (f"  {pos_col}  slot {idx:2d}  {field_count:2d}f  {layout_col:11s}  "
                    f"{flag}  {type_name:16s} [{names}]")
        else:
            line = (f"  {pos_col}  [{idx:2d}]  {field_count:2d}f {layout_col} {flag}  "
                    f"{type_name:16s} {names}")
        return line

    print("=== Screen order as viewed on-device (reorderable via --swap-order) ===")
    if verbose:
        print("  POS  SLOT      CNT  LAYOUT       FLAG  TYPE              FIELDS")
    else:
        print("  POS  SLOT  CNT LAY FLAG  TYPE              FIELDS")
    for position, (f9, idx, m) in enumerate(orderable, start=1):
        field_count = m.get(3)
        print(_row(idx, m, field_count, position))

    if conditional:
        print()
        print("=== Conditional screens (active feature, exempt from normal ordering -- "
              "GroupTrack-style; --swap-order refuses these, no f9 to swap) ===")
        for idx, m in conditional:
            field_count = m.get(3)
            print(_row(idx, m, field_count))
        if verbose:
            print("  NOTE: this section catches the GroupTrack-style structural exemption "
                  "(f1=1, f9 absent, f10 present). Other conditionally-TRIGGERED screens "
                  "(e.g. ClimbPro) may still have a real f9 and appear in the main ordered "
                  "list above instead -- they participate normally in scroll order even "
                  "though their content is only 'live' under specific circumstances. Not "
                  "all conditional features work the same way structurally.")

    if removed:
        print()
        print("=== Removed screens (content preserved, pulled from the display sequence) ===")
        for idx, m in removed:
            field_count = m.get(3)
            print(_row(idx, m, field_count))
        if verbose:
            print("  NOTE: confirmed via live Remove-button test; NOT restorable via any "
                  "on-device menu. fit_patch.py --un-remove exists but has shown a real "
                  "device-side hazard (unrelated content loss) in testing -- see FIT_PATCH.md "
                  "BUGS before using it.")

    if args.show_unconfigured and unconfigured:
        print()
        print("=== Unconfigured (never created, available for --new-slot) ===")
        for idx, m in unconfigured:
            print(f"  [slot {idx:2d}]")

    total_configured = len(orderable) + len(conditional) + len(removed)
    print()
    print(f"  ({total_configured} configured screen slot(s) total: "
          f"{len(orderable)} reorderable, {len(conditional)} conditional, "
          f"{len(removed)} removed)", file=sys.stderr)
    if unknown_ids_seen:
        if verbose:
            print(f"  ** unknown field IDs on this file: {sorted(unknown_ids_seen)}",
                  file=sys.stderr)
        else:
            print(f"  ** unknown field IDs on this file: {sorted(unknown_ids_seen)} "
                  f"(run with -v for detail)", file=sys.stderr)


def cmd_diff(args):
    import difflib
    a_lines = render_lines(decode_file(args.file_a))
    b_lines = render_lines(decode_file(args.file_b))
    diff = difflib.unified_diff(
        a_lines, b_lines,
        fromfile=args.file_a, tofile=args.file_b,
        lineterm="",
    )
    had_output = False
    for line in diff:
        had_output = True
        print(line)
    if not had_output:
        print("No differences.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_dump = sub.add_parser("dump", help="Dump one FIT file as sorted, diff-friendly text")
    p_dump.add_argument("file")
    p_dump.set_defaults(func=cmd_dump)

    p_unknown = sub.add_parser("unknown", help="Show only messages/fields not in the public FIT profile")
    p_unknown.add_argument("file")
    p_unknown.set_defaults(func=cmd_unknown)

    p_screens = sub.add_parser("screens", help="Human-readable data_screen (mesg 14) report: "
                                                 "screen index, field count, field names")
    p_screens.add_argument("file")
    p_screens.add_argument("--all", dest="show_unconfigured", action="store_true",
                            help="Also list unconfigured/preallocated-but-empty screen slots")
    p_screens.add_argument("-v", "--verbose", action="store_true",
                            help="Full detail: long unknown-field text, full system-slot "
                                 "explanations, full layout labels. Default is a compact, "
                                 "column-aligned view.")
    p_screens.set_defaults(func=cmd_screens)

    p_diff = sub.add_parser("diff", help="Decode two FIT files and diff them directly")
    p_diff.add_argument("file_a")
    p_diff.add_argument("file_b")
    p_diff.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
