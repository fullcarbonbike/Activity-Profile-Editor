#!/usr/bin/env python3
__version__ = "1.15.0"  # Device-dependent Connect IQ field guard, two passes, both real-hardware-driven bug fixes -- see PROJECT_NOTES.md Doc rev 95-99 for the full investigation. Pass 1 (2026-09-02): --fields now hard-refuses (no --force) if any REQUESTED field ID is in fit_dump.py's new DEVICE_DEPENDENT_CIQ_IDS (currently {216}) -- CONFIRMED this toolkit cannot write a Connect IQ third-party field (e.g. WindField) into a slot at all, it silently renders as "Timer" on-device regardless of what the file/GUI shows. Pass 2 (2026-09-03), added after Doug's own further real-hardware testing exposed a real gap in pass 1: the request-side check alone missed a screen that ALREADY has a device-dependent CIQ field on it having ITS OWN id/position left untouched while OTHER, ordinary fields are added/removed/reordered around it -- confirmed this breaks the CIQ field's linkage exactly like a fresh introduction does. New screen_has_device_dependent_ciq_field() checks the slot's CURRENT on-disk content (independent of what's being requested) and hard-refuses whenever a write touches the screen's shape (f3 count / f7 field array / f8 layout) -- applies to --fields, --swap-fields, and a bare --layout change alike; does not apply to --swap-order (f9 only, screen DISPLAY position, confirmed separately safe in Doc rev 99) or --enable/--disable (f12 only, no evidence either way yet). Doc-only, no functional change, Doug's decision (2026-08-15): comments referencing the f10=32 Conditional runtime record as "GroupTrack"/"the GroupTrack Conditional record" updated to describe it as "Reserved" (display name change lives in fit_dump.py v2.4.12's NAMED_SCREEN_TYPES -- this file has no code path of its own that special-cases f10=32, only prose describing it) -- read_current_state()'s docstring and NO_SHOW_TOGGLE_TYPES' comment block updated to match, both now note the record's real purpose was never actually confirmed rather than asserting a GroupTrack identity. count_shown_active_screens()'s docstring updated the same way. f10=57 "GroupTrack List" is untouched by this pass -- that one remains correctly, confirmedly GroupTrack-specific. No behavior change anywhere in this file. Prior entry (1.14.1): Doc-only, no functional change (2026-08-14): --remove is now CONFIRMED via a real on-device round-trip test (Doug) -- the target screen was correctly removed from the on-device Data Screens order, matching a real Remove button press, and (as expected, matching the retired --un-remove's own history and Doug's stated reasoning for retiring it) the removed screen does NOT survive as a recoverable Removed-state slot after the deploy -- NewFiles wipes it, same as every other Removed-state slot on any NewFiles deploy. Updated remove_screen()'s docstring and --remove's argparse help text from "NOT YET VERIFIED ON REAL HARDWARE" to CONFIRMED. This closes step 2 of the two-phase build plan (backend + headless verification, then a real device test) -- the GUI wrapper (ViewScreensPanel, per Doug's placement decision) is now the one remaining, unblocked step; still not built until Doug asks for it, per this project's established discipline of not building ahead of an explicit go-ahead. Prior entry (1.14.0): New feature, first half of "Delete Screen" (2026-08-14): added --remove and its backend primitive remove_screen() -- transitions an Active screen slot to the Removed state (f1=0, f9/f10 cleared to sentinel, f3/f7 content left untouched, matching the confirmed on-device Removed-state model). Mirrors --new-slot's activation in reverse, same spirit as the now-retired --un-remove but going the other direction. Reuses hide_unsupported_screen_type() and would_hide_last_visible_screen() directly as --remove's two hard guards (no --force override for either) -- CONFIRMED (2026-08-13, Doug, directly on-device) that NO_SHOW_TOGGLE_TYPES (Map, ClimbPro) bounds Remove availability identically to Show/Hide, and the last-visible-user-screen floor rule is documented as already covering Remove too, so no new guard logic was needed, only reuse. ONE-WAY by design -- no --un-remove exists anymore (retired v1.13.0); Restore-from-Backup is the only real undo path, matching Garmin's own editor (Hide is reversible, Remove is permanent, same as Add New). Headless-verified only so far, against a real profile copy (CyclingRoadSandbox): remove_screen() correctly transitions the target slot to 'removed' (read_current_state()), leaves f3/f7 byte-identical to before, and leaves read_current_state() unchanged on every OTHER slot in the file; the CLI end-to-end path (--slot 3 --remove) wrote a file with a valid trailing CRC (fit_crc() recomputation matched the stored value exactly); both guards were exercised directly and blocked exactly as designed -- --slot 2 (Map) errored via hide_unsupported_screen_type(), and removing a profile's second-to-last then last visible user screen correctly errored via would_hide_last_visible_screen() on the second attempt. But this is NOT YET VERIFIED ON REAL HARDWARE (no on-device round-trip test yet, unlike --new-slot/--hide/--swap-order, all of which are proven live). Per the two-phase build plan recorded when "Delete Screen" was scoped (see PROJECT_NOTES.md Open Items, 2026-08-13): this backend flag is step one: a real on-device round-trip test is needed next, and ONLY THEN (not before) does a GUI wrapper (ViewScreensPanel, per Doug's placement decision) get built. Prior entry (1.13.2): doc-only, no functional change (2026-08-13): corrected a self-inflicted gap from the previous entry -- Doug clarified that "GroupTrack" in his confirmed-active-Remove list meant the on-device editor's actual label "GroupTrack List" (f10=57), which was already covered, not a separate untested type. The genuinely separate f10=32 GroupTrack Conditional runtime record never appears as a row in the on-device Data Screens editor at all (no real f9), so it has no Remove-button status to check and is already structurally out of reach of the future --remove flag regardless. Also recorded, for pattern-recognition: an early, already-removed SYSTEM_SLOT_HINTS hardcode once claimed "slot 10 = GroupTrack" by message_index -- confirmed wrong on the Indoor profile (slot 10 there is a genuine Cadence screen); slot numbers were never reliable for identifying GroupTrack or anything else, only f10 is. NO_SHOW_TOGGLE_TYPES (Map, ClimbPro) is now documented as the COMPLETE confirmed Remove-block set for common named types, no remaining gap. No code/behavior change -- comment only. Prior entry (1.13.1): doc-only, no functional change (2026-08-13): Doug confirmed directly on-device that NO_SHOW_TOGGLE_TYPES (Map, ClimbPro) also bounds Remove availability, not just the Show/Hide toggle it already guards -- every other common named type (Elevation, GroupTrack, Cycling Dynamics, Lap Summary, Virtual Partner, Compass, Segment) has an active Remove option. Added a comment documenting this at the constant's definition, directly relevant to the still-scoped, not-yet-built --remove flag (its future type-check guard can reuse this exact set). No code/behavior change -- comment only. Prior entry (1.13.0): RETIRED --un-remove entirely, Doug's decision (2026-08-13): Restore-from-Backup already covers the real recovery use case (a whole-profile undo, already CONFIRMED on real hardware), and --un-remove itself was never a clean win -- it had a CONFIRMED real device-side data-loss hazard pre-v1.12.0 (root-caused to the same f10=0 collision --new-slot had, see BUGS in FIT_PATCH.md), was never re-tested live after that fix (still "unverified-but-plausibly-fixed" as of v1.12.0), and Garmin's own on-device editor doesn't expose an un-remove workflow at all -- Hide (temporary) and Remove + Add New (permanent) are the only two lifecycle actions it offers, matching this project's own "Product note on --un-remove" which had left the final call deferred. Removed the --un-remove argparse flag, its --new-slot mutual-exclusion check, its Removed-state validation block, and simplified every `args.new_slot or args.un_remove` conditional down to just `args.new_slot` (the f1 configured-flag set, and the f9/f10 auto-fill safety net) -- confirmed via grep that zero `un_remove` references remain in this file outside this changelog line and the retirement note left in its place. No behavior change to --new-slot itself. This also removes a layer of unverified risk that would otherwise sit underneath any future --remove (Delete Screen) flag -- see PROJECT_NOTES.md Open Items. Prior entry (1.12.0): add next_available_field10() and wire it into --new-slot/--un-remove's auto-default, replacing the old hardcoded f10=0 -- ROOT-CAUSES the long-standing "Add New Screen via NewFiles always fails" limitation as an f10 IDENTITY COLLISION (0 = "Screen 1", already in use on almost every real profile), not a hard device restriction. CONFIRMED via live on-device round-trip (2026-08-05, CyclingRoadSandbox): --new-slot with a collision-free f10 survives the NewFiles restart cycle intact, verified independently by both fit_dump.py and garmin_device.py reading the live mounted device. Also fixed next_available_field9()'s f3-presence gate to match the f1-based gate used elsewhere (same Virtual-Partner-style blind spot fixed in classify_screens()/read_current_state() earlier)
"""
fit_patch.py - Surgical patcher for Garmin Edge data_screen (mesg_num=14) messages.

Design: every real edit we've observed on-device (field count changes,
field ID changes, layout variant changes, activating a brand-new screen
slot) is an ISOLATED, IN-PLACE byte patch -- the file never changes size,
nothing outside the target message's byte range moves. So this patcher
does the simplest, lowest-risk thing possible: locate the target message's
exact byte offsets via the structural walker (fit_raw_walk.py), overwrite
only the specific field bytes being changed, recompute the trailing file
CRC (fit_crc.py), and leave every other byte -- known or still-unknown --
completely untouched.

This deliberately does NOT re-encode the file. We do not fully understand
every field in this message (f9-f12 partially, and definitely not every
other message type in the file), so a full re-encode would require
correctly reproducing things we can't yet verify. Patching in place means
our ignorance of those bytes is harmless -- they're never touched.

GUI reuse
---------
patch_screen(), read_current_field_array(), read_current_count_and_layout(),
read_current_state(), swap_display_order(), remove_screen(), the pack_*()
helpers, check_system_screen_guard(), count_shown_active_screens(),
would_hide_last_visible_screen(), hide_unsupported_screen_type(),
next_available_field9(), next_available_field10(),
KNOWN_SYSTEM_CONTENT_PATTERNS, and COUNTS_WITH_B_VARIANT are all plain,
print-free functions/constants -- safe to import directly
(`from fit_patch import patch_screen, ...`) from the GUI or any other
in-process consumer. _cli() is just this module's own CLI consumer of
the same building blocks; nothing about its argparse plumbing needs to
be reused elsewhere.
"""
import sys
import struct
from fit_raw_walk import parse_fit
from fit_crc import fit_crc
from fit_dump import NAMED_SCREEN_TYPES, DEVICE_DEPENDENT_CIQ_IDS

DATA_SCREEN_MESG_NUM = 14


def find_screen_message(messages, message_index):
    """Return the raw walker message dict for a given data_screen slot."""
    for m in messages:
        if m['kind'] != 'data' or m['mesg_num'] != DATA_SCREEN_MESG_NUM:
            continue
        fd = {d: (sz, bt, raw) for (d, sz, bt, raw) in m['fields']}
        if 254 not in fd:
            continue
        idx = struct.unpack('<H', fd[254][2])[0]
        if idx == message_index:
            return m
    return None


def field_byte_range(msg, field_def_num):
    """Return (start, end) absolute file offsets for one field within a message."""
    cursor = msg['start'] + 1  # skip record header byte
    for (def_num, size, base_type, raw) in msg['fields']:
        if def_num == field_def_num:
            return (cursor, cursor + size)
        cursor += size
    raise KeyError(f'field {field_def_num} not present in this message definition')


def patch_screen(input_path, output_path, message_index, changes):
    """
    changes: dict of field_def_num -> new raw bytes (already packed, correct
    size for that field -- e.g. struct.pack('<H', 320) for a uint16 field,
    or bytes([4]) for a uint8 field). Caller is responsible for packing --
    this function does not know field semantics, only byte offsets.

    Returns the patched byte buffer (also written to output_path).
    """
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_screen_message(messages, message_index)
    if msg is None:
        raise ValueError(f'message_index {message_index} not found in {input_path} '
                          f'(structural change would be needed -- this patcher only '
                          f'handles slots that already exist as preallocated messages)')

    for field_def_num, new_bytes in changes.items():
        start, end = field_byte_range(msg, field_def_num)
        expected_len = end - start
        if len(new_bytes) != expected_len:
            raise ValueError(f'field {field_def_num}: expected {expected_len} bytes, '
                              f'got {len(new_bytes)}')
        data[start:end] = new_bytes

    # Recompute and rewrite the trailing file CRC (last 2 bytes)
    body = bytes(data[:-2])
    new_crc = fit_crc(body)
    data[-2:] = struct.pack('<H', new_crc)

    with open(output_path, 'wb') as f:
        f.write(data)

    return bytes(data)


# --- Convenience packers for the fields we understand -----------------

def pack_field_count(n):
    return bytes([n])


def pack_field_id_array(ids):
    """ids: list of up to 10 field IDs. Shorter lists are padded with 0xFFFF (unset)."""
    ids = list(ids) + [0xFFFF] * (10 - len(ids))
    return struct.pack('<10H', *ids[:10])


def pack_layout_variant(v):
    return bytes([v])


def pack_uint8(v):
    return bytes([v])


def pack_configured_flag():
    """field 1 -- goes FF -> 01 when a slot transitions to configured."""
    return bytes([1])


def pack_enabled(enabled=True):
    """field 12 -- 0 = enabled/shown, 1 = disabled/hidden."""
    return bytes([0 if enabled else 1])


def pack_removed_flag():
    """field 1 -- goes 01 -> 00 when a slot transitions from Active/
    Configured to Removed (see remove_screen())."""
    return bytes([0])


def read_current_count_and_layout(input_path, message_index):
    """
    Peek at a slot's CURRENT field_count (f3) and layout (f8) without
    patching anything -- used to validate a requested change against
    whatever isn't being explicitly overwritten this call. Returns
    (count_or_None, layout_or_None); None means "unconfigured/sentinel",
    matching the 0xFF raw value.
    """
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_screen_message(messages, message_index)
    if msg is None:
        return (None, None)

    with open(input_path, 'rb') as f:
        data = f.read()

    def _read_u8(field_def_num):
        try:
            start, end = field_byte_range(msg, field_def_num)
        except KeyError:
            return None
        val = data[start]
        return None if val == 0xFF else val

    return (_read_u8(3), _read_u8(8))


# Field counts that have a real, on-device-confirmed A/B layout choice.
# Everything else has only one real layout -- see the developer's own
# on-device reference table (screen layouts #1-#10).
def next_available_field9(input_path):
    """
    f9 appears to be a global, monotonically-increasing 'screen creation
    order' stamp -- every configured slot in every real profile we've
    examined uses a distinct value, 0..N with no gaps or duplicates.
    Returns the smallest value not already in use (max existing + 1).

    Gates on f1==1 (Active), not f3 presence -- some genuine Active
    screens (Virtual Partner, f10=26) have no f3 at all and would be
    silently skipped by an f3-presence check, same class of bug fixed
    in classify_screens()/read_current_state() earlier this session.
    """
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    with open(input_path, 'rb') as f:
        data = f.read()

    highest = -1
    for m in messages:
        if m['kind'] != 'data' or m['mesg_num'] != DATA_SCREEN_MESG_NUM:
            continue
        try:
            start1, end1 = field_byte_range(m, 1)
        except KeyError:
            continue
        if data[start1] != 1:
            continue  # not Active (Removed or never-configured) -> skip
        try:
            start, end = field_byte_range(m, 9)
        except KeyError:
            continue
        val = data[start]
        if val != 0xFF and val > highest:
            highest = val
    return highest + 1


def next_available_field10(input_path):
    """
    f10 is a per-profile, zero-indexed counter for plain, user-created
    screens (shown on-device as "Screen N" = f10+1); named Garmin screen
    types (Map, ClimbPro, GroupTrack List, etc.) use a fixed global code
    and are excluded from this count entirely.

    CONFIRMED via live on-device round-trip (2026-08-05,
    CyclingRoadSandbox): writing a --new-slot screen with an f10 value
    already held by an existing user screen collides with that screen's
    identity -- the device's NewFiles reconciliation merges/discards the
    new content on the next restart. A collision-free f10 (one past the
    highest value already in use) survives the restart cycle intact.
    This is what made the OLD hardcoded f10=0 default unsafe: 0 is a
    real identity ("Screen 1"), not an inert sentinel, and almost every
    real profile already has a Screen 1.

    Returns the smallest non-negative value not already in use by a
    real user screen (max existing user-screen f10 + 1, or 0 if the
    profile has no user screens yet).
    """
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    with open(input_path, 'rb') as f:
        data = f.read()

    highest = -1
    for m in messages:
        if m['kind'] != 'data' or m['mesg_num'] != DATA_SCREEN_MESG_NUM:
            continue
        try:
            start1, end1 = field_byte_range(m, 1)
        except KeyError:
            continue
        if data[start1] != 1:
            continue  # not Active -> skip
        try:
            start, end = field_byte_range(m, 10)
        except KeyError:
            continue
        val = data[start]
        if val == 0xFF or val in NAMED_SCREEN_TYPES:
            continue  # unset, or a named Garmin type -- not a user-screen slot
        if val > highest:
            highest = val
    return highest + 1


def read_current_field_array(input_path, message_index):
    """
    Read the current 10-slot field ID array for an already-configured
    screen, as a list of 10 ints (0xFFFF for unset slots preserved as-is).
    Returns None if the slot has no field 7 (shouldn't happen structurally,
    every slot has this field, but defensive anyway).
    """
    raw = read_raw_field(input_path, message_index, 7)
    if raw is None:
        return None
    return list(struct.unpack('<10H', raw))


def read_raw_field(input_path, message_index, field_def_num):
    """Read the raw bytes of one field from an existing message, as-is."""
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_screen_message(messages, message_index)
    if msg is None:
        raise ValueError(f'slot {message_index} not found in {input_path}')
    start, end = field_byte_range(msg, field_def_num)
    with open(input_path, 'rb') as f:
        f.seek(start)
        return f.read(end - start)


def swap_display_order(input_path, output_path, slot_a, slot_b):
    """
    Swap the on-device DISPLAY ORDER of two already-configured screens by
    swapping their field 9 (creation-order stamp) values. Confirmed:
    ascending f9 == on-device display order (Gravel profile editor
    sequence matched exactly). This does NOT touch field count, field
    content, or total configured-screen count -- both slots keep their
    own fields, they just trade places in the viewing sequence.

    Both slots must already have a real (non-sentinel) f9 -- this only
    reorders existing screens, it doesn't activate new ones.
    """
    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg_a = find_screen_message(messages, slot_a)
    msg_b = find_screen_message(messages, slot_b)
    if msg_a is None:
        raise ValueError(f'slot {slot_a} not found in {input_path}')
    if msg_b is None:
        raise ValueError(f'slot {slot_b} not found in {input_path}')

    start_a, end_a = field_byte_range(msg_a, 9)
    start_b, end_b = field_byte_range(msg_b, 9)
    f9_a = bytes(data[start_a:end_a])
    f9_b = bytes(data[start_b:end_b])

    if f9_a == b'\xff' or f9_b == b'\xff':
        raise ValueError(
            f"--swap-order: slot {slot_a} or {slot_b} has no real f9 (sentinel/unconfigured) -- "
            f"can only reorder already-configured screens, not activate new ones."
        )

    data[start_a:end_a] = f9_b
    data[start_b:end_b] = f9_a

    body = bytes(data[:-2])
    new_crc = fit_crc(body)
    data[-2:] = struct.pack('<H', new_crc)

    with open(output_path, 'wb') as f:
        f.write(data)

    return bytes(data), f9_a, f9_b


def read_current_state(input_path, message_index):
    """
    Read the raw f1/f9/f10 bytes for a slot to determine its screen
    state (see SCREEN STATE MODEL in project notes): Active (f1=1, f9
    real), Conditional (f1=1, f9 absent, f10 real -- always seen as
    f10=32, display name "Reserved," see fit_dump.py's
    NAMED_SCREEN_TYPES), Removed (f1=0, f9/f10 both absent, content
    preserved), or
    Unconfigured (no f1==1 signal at all -- never created). Returns one
    of those four strings, or None if the slot doesn't exist in the
    file at all.

    v1.9.0 BUG FIX: previously gated on f3 (field count) presence,
    matching a bug found and fixed in fit_dump.py's classify_screens()
    -- some genuine Active screens (Virtual Partner, f10=26) have no f3
    key at all, and were misreported as 'unconfigured' by this
    function. Now gated on f1/f9/f10 instead, same fix as fit_dump.py.
    """
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    msg = find_screen_message(messages, message_index)
    if msg is None:
        return None

    with open(input_path, 'rb') as f:
        data = f.read()

    def _read_u8(field_def_num):
        try:
            start, end = field_byte_range(msg, field_def_num)
        except KeyError:
            return None
        val = data[start]
        return None if val == 0xFF else val

    f1 = _read_u8(1)
    f9 = _read_u8(9)
    f10 = _read_u8(10)

    if f9 is not None:
        return 'active'
    if f1 == 0:
        return 'removed'
    if f1 == 1 and f10 is not None:
        return 'conditional'
    return 'unconfigured'


def count_shown_active_screens(input_path):
    """
    Count how many CURRENTLY VISIBLE (field 12 = 0), plain user-created
    "Screen N" screens this profile has -- i.e. Active/Display screens
    (real, non-sentinel f9) whose field 10 (f10) is NOT one of the
    NAMED_SCREEN_TYPES fixed Garmin codes (Map, Elevation, Cycling
    Dynamics, etc. -- see fit_dump.py).

    v1.9.0 CORRECTION: earlier versions counted EVERY visible Active
    screen, named Garmin types included. That undercounted the real
    on-device constraint -- confirmed directly on a real profile
    (Atest) where the on-device editor grayed out Remove/Show Screen
    for the profile's ONE user screen (Slot 0) despite 7 OTHER visible
    screens (Lap Summary, Elevation, Map, GroupTrack List, ClimbPro,
    Cycling Dynamics, Segment -- all named Garmin types) still being
    shown. The device evidently only counts plain user screens toward
    "at least one must remain visible," not screens of any kind. This
    is what f10 (confirmed as a genuine, content-independent screen
    TYPE identifier -- see fit_dump.py's NAMED_SCREEN_TYPES) finally
    makes possible to check correctly from the file alone.

    Directly countable fact, not a guess -- unlike
    check_system_screen_guard()'s content heuristics. Conditional (the
    f10=32 "Reserved" record) and Removed screens are excluded -- they
    have no real f9, so they were never part of the on-device "Data
    Screens" reorderable list this constraint applies to.
    """
    messages, hdr_size, end_of_data, total_len = parse_fit(input_path)
    with open(input_path, 'rb') as f:
        data = f.read()

    count = 0
    for m in messages:
        if m['kind'] != 'data' or m['mesg_num'] != DATA_SCREEN_MESG_NUM:
            continue

        try:
            f9_start, _ = field_byte_range(m, 9)
        except KeyError:
            continue  # no f9 field at all -- not Active/Display
        if data[f9_start] == 0xFF:
            continue  # sentinel -> Conditional or Removed, not counted

        try:
            f12_start, _ = field_byte_range(m, 12)
            shown = data[f12_start] != 1
        except KeyError:
            shown = True  # field 12 absent entirely -- every real profile examined
                          # so far has this set on every Active screen, but default
                          # to "shown" (the safer assumption) if it's ever missing
        if not shown:
            continue

        try:
            f10_start, _ = field_byte_range(m, 10)
            f10_val = data[f10_start]
            if f10_val == 0xFF:
                f10_val = None
        except KeyError:
            f10_val = None

        if f10_val is not None and f10_val in NAMED_SCREEN_TYPES:
            continue  # a named Garmin screen type -- doesn't count toward the floor

        count += 1
    return count


def would_hide_last_visible_screen(input_path, message_index):
    """
    Returns True if hiding `message_index` (i.e. setting its field 12
    to hidden) would bring the count of visible, plain user-created
    "Screen N" screens on this profile to zero. Only meaningful to call
    BEFORE applying a hide.

    Returns False (guard doesn't apply) if:
      - the slot isn't currently an Active, visible screen at all
        (nothing this specific action would change), OR
      - the slot is already hidden, OR
      - v1.9.0: the slot itself is a NAMED Garmin screen type (Map,
        Elevation, Cycling Dynamics, etc. -- see f10/NAMED_SCREEN_TYPES
        in fit_dump.py). Hiding a named Garmin screen type is governed
        by a completely different, per-type rule -- most have their own
        working Show Screen toggle, Map has none at all, ClimbPro's
        lives outside data_screen entirely (training_settings_mesgs).
        None of that is the "can't hide the last screen" behavior this
        guard reproduces -- that behavior is specifically about plain
        user screens, confirmed on a real profile where 7 OTHER visible
        named-type screens did NOT prevent the device from graying out
        Hide/Remove on the profile's one real user screen.

    This is a HARD constraint, not a heuristic -- see
    count_shown_active_screens(). There is deliberately no --force
    override for it in the CLI, unlike check_system_screen_guard()'s
    checks: we're not guessing here, we know for certain what state
    the write would produce, and that state is confirmed to be one the
    on-device editor itself refuses to create.
    """
    if read_current_state(input_path, message_index) != 'active':
        return False

    try:
        f10_raw = read_raw_field(input_path, message_index, 10)
        f10_val = f10_raw[0] if f10_raw and f10_raw[0] != 0xFF else None
    except (KeyError, ValueError):
        f10_val = None
    if f10_val is not None and f10_val in NAMED_SCREEN_TYPES:
        return False  # a named Garmin screen type -- this guard doesn't apply to it

    try:
        f12_raw = read_raw_field(input_path, message_index, 12)
        already_hidden = bool(f12_raw) and f12_raw[0] == 1
    except (KeyError, ValueError):
        already_hidden = False
    if already_hidden:
        return False
    return count_shown_active_screens(input_path) <= 1


# CONFIRMED via direct on-device inspection (2026-08-04): Map (f10=25)
# and ClimbPro (f10=104) have NO "Show Screen" toggle anywhere in the
# per-screen Data Screens editor -- not "commonly don't," not a
# heuristic, a directly observed fact for both. This is distinct from
# ClimbPro's separate on/off setting one level up in the Profile menu
# (training_settings_mesgs field 63, already documented) -- that's a
# different control entirely; the per-screen entry itself simply has no
# Show/Hide option, the same as Map. The one apparent exception, the
# Indoor profile's Map screen, does NOT use this mechanism either: it
# exposes a different control that changes Map's state between
# "Always" and "While Navigating," not a Show Screen toggle -- almost
# certainly a different field, not f12 (see PROJECT_NOTES.md Open
# items; still investigating which field, possibly related to the
# f11=2 anomaly seen only on that one slot). So this hard guard applies
# universally, regardless of profile type: forcing f12=1 on a Map or
# ClimbPro screen via a raw file write has no on-device equivalent
# action to compare it against, on ANY profile.
#
# CONFIRMED (2026-08-13, Doug, directly on-device) that this exact set
# also bounds Remove availability, not just Show/Hide: of the common
# Garmin Edge named screen types, Map and ClimbPro are the ONLY two
# with the on-device Remove option disabled -- Elevation, "GroupTrack
# List" (f10=57, the on-device editor's actual label -- not to be
# confused with f10=32, the separate always-present Conditional-only
# runtime record, display name "Reserved" (renamed 2026-08-15 from
# "GroupTrack" -- its real purpose was never actually confirmed), which
# never appears as a row in the editor at all and so has no
# Remove-button status to check), Cycling Dynamics, Lap Summary,
# Virtual Partner, Compass, and Segment all show an active Remove
# option. That's the complete set of common named types -- no gap
# remains. Directly relevant to the scoped-but-not-yet-built --remove
# flag (see PROJECT_NOTES.md Open Items, "Delete Screen") -- its own
# type-check guard can reuse this same set (Map, ClimbPro) as-is.
NO_SHOW_TOGGLE_TYPES = {25, 104}  # Map, ClimbPro


def screen_has_device_dependent_ciq_field(input_path, message_index):
    """
    Returns the sorted list of DEVICE_DEPENDENT_CIQ_IDS (fit_dump.py --
    e.g. {216}) currently present in this slot's field array right now,
    on disk, BEFORE any edit -- or [] if none.

    CORRECTION (2026-09-03, Doug, real on-device test): the original
    --fields guard below (added 2026-09-02) only checked the NEWLY
    REQUESTED ids against DEVICE_DEPENDENT_CIQ_IDS -- which misses a
    real failure mode. Doug added two ordinary fields to a screen that
    already had a working Connect IQ field (Edge 3270), rearranging it
    from a 1-field to a 3-field layout with the CIQ field kept in the
    middle position -- its own ID value was never "requested" or
    changed, only fields AROUND it were. Deployed: the CIQ field broke
    exactly the same way a fresh introduction does (renders as Timer).
    So the real rule isn't "does this write's REQUESTED ids include a
    CIQ id" -- it's "does this slot CURRENTLY hold one, period," in
    which case this toolkit has no confirmed-safe way to touch that
    slot's count (f3), field array (f7), or layout (f8) at all, even
    when the CIQ field's own ID/position isn't the thing changing.
    Whatever actually resolves the device-side linkage appears to get
    invalidated by ANY toolkit rewrite of the screen's shape, not just
    ones that touch the CIQ field's own bytes.

    Used as a SECOND, independent check alongside the request-side one
    -- this one catches "slot already has one, leave the whole screen
    alone," the other catches "don't let me freshly introduce one that
    isn't there yet." Both are real, both confirmed, neither implies
    the other.
    """
    current_array = read_current_field_array(input_path, message_index)
    if current_array is None:
        return []
    return sorted(set(current_array) & DEVICE_DEPENDENT_CIQ_IDS)


def hide_unsupported_screen_type(input_path, message_index):
    """
    Returns the screen type name (e.g. "Map") if `message_index` is a
    NAMED Garmin type CONFIRMED to have no on-device Show Screen toggle
    at all (see NO_SHOW_TOGGLE_TYPES above), or None otherwise
    (including for every plain user screen and every OTHER named type,
    which do have working toggles).

    This is a HARD constraint, not a heuristic, same spirit as
    would_hide_last_visible_screen() -- there is deliberately no
    --force override for it: we're not guessing here, we directly
    observed these two screens have no Show Screen control on-device,
    so there is nothing to second-guess by forcing the byte anyway.
    """
    try:
        f10_raw = read_raw_field(input_path, message_index, 10)
        f10_val = f10_raw[0] if f10_raw and f10_raw[0] != 0xFF else None
    except (KeyError, ValueError):
        f10_val = None
    if f10_val is None or f10_val not in NO_SHOW_TOGGLE_TYPES:
        return None
    return NAMED_SCREEN_TYPES[f10_val]


def remove_screen(input_path, output_path, message_index):
    """
    Transition an Active, configured screen slot to the Removed state:
    f1 -> 0, f9/f10 cleared to the 0xFF sentinel. Mirrors --new-slot's
    activation in reverse. Field count/array (f3/f7) are deliberately
    left UNTOUCHED -- confirmed on-device behavior (see SCREEN STATE
    MODEL, PROJECT_NOTES.md) is that a Removed screen's CONTENT is
    preserved, only its f1/f9/f10 identity/order signals go away.

    This is a ONE-WAY operation by design, matching Garmin's own
    editor (Hide is the only reversible per-screen action; Remove is
    permanent, same as Add New). --un-remove, this project's own
    former attempt at a per-screen undo, was retired entirely
    (v1.13.0) -- Restore-from-Backup (a whole-profile undo, confirmed
    on real hardware) is the only real recovery path after a Remove.
    There is no --force override for anything this function's callers
    guard against, for the same reason --hide's guards have none: both
    hard guards below are directly observed facts, not heuristics.

    Caller is responsible for running the SAME two guards --hide
    already enforces, BEFORE calling this -- this function is a pure
    byte-patch primitive and does not re-check either one itself, same
    division of responsibility patch_screen() itself follows:
      - hide_unsupported_screen_type(input_path, message_index): CONFIRMED
        (2026-08-13, Doug, directly on-device) that NO_SHOW_TOGGLE_TYPES
        (Map, ClimbPro) bounds Remove availability too, not just Show/
        Hide -- these two named types have no Remove option either.
      - would_hide_last_visible_screen(input_path, message_index):
        documented as already covering Remove's identical on-device
        floor-of-one rule (a profile must always have at least one
        visible plain user screen) -- no separate function needed,
        since Remove and Hide both result in the screen no longer
        being shown.

    CONFIRMED via a real on-device round-trip test (2026-08-14, Doug):
    the target screen was correctly removed from the on-device Data
    Screens order, matching a real Remove button press. Also confirmed
    the expected corollary from the retired --un-remove's own history:
    the removed screen does NOT survive as a recoverable Removed-state
    slot after the deploy that removes it -- NewFiles wipes it, same as
    every other Removed-state slot on any NewFiles deploy (see BUGS).
    This directly matches Doug's own reasoning for retiring --un-remove
    in the first place ("if the user mistakenly deletes a screen, they
    can always recover the previous state using restore from backup")
    -- there was never going to be a toolkit-side undo path for this,
    by design, and this test confirms there isn't one on the device
    side either. See PROJECT_NOTES.md Open Items ("Delete Screen") for
    the full two-phase build history this function completed: backend
    primitive, headless verification, then this real device test --
    the GUI wrapper (ViewScreensPanel, per Doug's placement decision)
    is the one remaining, now-unblocked step.
    """
    changes = {
        1: pack_removed_flag(),
        9: bytes([0xFF]),
        10: bytes([0xFF]),
    }
    patch_screen(input_path, output_path, message_index, changes)
    return changes


# Content patterns that have recurred, on MULTIPLE different profiles,
# as likely system/overlay screens (Elevation, Map, Cycling Dynamics,
# ClimbPro, Compass/Lap Summary) rather than screens the user built from
# scratch. ORIGINALLY a heuristic because there was NO reliable
# structural marker for "system screen" anywhere in data_screen
# (confirmed the hard way: a previous hardcoded slot-number version of
# this idea was proven WRONG on a real profile and removed entirely, see
# FIT_PATCH.md / PROJECT_NOTES.md CORRECTIONS).
#
# v1.10.0 CORRECTION: field 10 (f10) is now CONFIRMED as a real,
# content-independent screen TYPE identifier (see NAMED_SCREEN_TYPES,
# imported from fit_dump.py) -- check_system_screen_guard() now checks
# f10 FIRST and answers with CERTAINTY whenever it's available. These
# two content/count-based heuristics are now only a FALLBACK, used
# solely when f10 itself is unavailable (a Removed-state slot has no
# real f10 to read). They are no longer the primary identity check for
# any Active screen, which is every screen this guard is normally
# called on. Kept for that fallback case and left otherwise unchanged.
# Frozensets of (sorted tuple of field IDs).
KNOWN_SYSTEM_CONTENT_PATTERNS = {
    (): "0 fields -- commonly Map or a similar system overlay",
    (9, 11): "Percent Grade + Elevation -- commonly the Elevation overlay "
              "and/or ClimbPro (both use this same content)",
    (266, 272): "Power Phase Left + Right -- commonly Cycling Dynamics",
}

# v1.7.0: generalizes the same heuristic beyond specific content-ID
# matches -- ANY screen with this few fields is commonly a
# Garmin-predefined/system screen (Map, Compass, a small overlay, etc.),
# and there is no reliable way to tell a genuine small user-built screen
# apart from one of these purely from the file. Chosen after real GUI
# usage surfaced this as a distinct risk from the specific content
# patterns above -- e.g. a 2-field screen whose exact field IDs don't
# happen to match any pattern already in the dict above would otherwise
# sail through unguarded. v1.10.0: superseded as the PRIMARY check by
# f10 (see above) -- fallback only now.
LOW_FIELD_COUNT_THRESHOLD = 2

COUNTS_WITH_B_VARIANT = {3, 4, 5, 6, 7}


def check_system_screen_guard(input_path, message_index):
    """
    Identify whether a data_screen slot is a Garmin-authored screen
    type, for the purpose of a "did you mean to overwrite/hide this?"
    pause before a content or visibility change. Returns None if the
    slot is confirmed (or, in the fallback case, merely suspected) to
    be a plain user screen -- safe to proceed with no pause -- or a
    human-readable warning string if it's a named type or suspected of
    being one.

    v1.10.0: field 10 (f10) is CONFIRMED as a real, content-independent
    screen TYPE identifier (side-thread Test 4, 2026-08-04 -- see
    NAMED_SCREEN_TYPES, PROJECT_NOTES.md "Screen identity — SOLVED").
    This function now checks f10 FIRST:
      - f10 present and matches a NAMED_SCREEN_TYPES code: returns a
        CERTAIN message naming the type directly -- not a guess.
      - f10 present and does NOT match (i.e. a plain "Screen N" user
        screen): returns None immediately, no further checks. This is
        the fix for a real reported false positive -- a CONFIRMED user
        screen with only 1-2 fields was still triggering the old
        ≤2-field heuristic below, which predates f10 and had no way to
        know the difference. Now that we do know, there's nothing left
        to guess about for any screen with a real f10.
      - f10 absent (e.g. a Removed-state slot, which has no real f10 by
        definition): falls back to the original two heuristics -- a
        known recurring content pattern (KNOWN_SYSTEM_CONTENT_PATTERNS)
        or a low field count (<= LOW_FIELD_COUNT_THRESHOLD). Genuinely
        still a guess in this one case, since identity can't be read
        from f10 here.

    Print-free and argparse-free by design -- both the CLI (_cli(),
    which turns a non-None result into a parser.error() unless --force)
    and the GUI (which turns it into a confirmation dialog) call this
    SAME function, so the two never drift into checking different
    things.
    """
    cur_count, _ = read_current_count_and_layout(input_path, message_index)
    if cur_count is None:
        # Unconfigured slot -- nothing to guard, there's no existing
        # content that could be a system screen.
        return None

    try:
        f10_raw = read_raw_field(input_path, message_index, 10)
        f10_val = f10_raw[0] if f10_raw and f10_raw[0] != 0xFF else None
    except (KeyError, ValueError):
        f10_val = None

    if f10_val is not None:
        if f10_val in NAMED_SCREEN_TYPES:
            return (
                f"is a Garmin '{NAMED_SCREEN_TYPES[f10_val]}' screen "
                f"(confirmed via field 10 -- not a guess)."
            )
        return None  # confirmed plain user screen -- nothing to warn about

    # Fallback: f10 unavailable (e.g. Removed state) -- original heuristics.
    cur_array = read_current_field_array(input_path, message_index)
    cur_active = tuple(sorted(v for v in cur_array[:cur_count] if v is not None))

    content_match = KNOWN_SYSTEM_CONTENT_PATTERNS.get(cur_active)
    if content_match is not None:
        return (
            f"current content ({cur_active}) matches a pattern commonly seen "
            f"on system/overlay screens on OTHER profiles: {content_match}."
        )

    if cur_count <= LOW_FIELD_COUNT_THRESHOLD:
        return (
            f"currently has only {cur_count} field(s). Screens "
            f"with {LOW_FIELD_COUNT_THRESHOLD} or fewer fields are commonly "
            f"Garmin-predefined/system screens (Map, Compass, a small "
            f"overlay, etc.) -- there is no reliable way to tell a genuine "
            f"small user-built screen apart from one of these from the "
            f"file alone (this slot has no readable field 10, so identity "
            f"can't be confirmed the reliable way either)."
        )

    return None


def _cli():
    import argparse
    parser = argparse.ArgumentParser(
        description="Patch a Garmin Edge data_screen slot and write a new .fit file.\n\n"
                     "Examples:\n"
                     "  # Set slot 11 to a single Speed field, default layout, enabled:\n"
                     "  python3 fit_patch.py in.fit out.fit --slot 11 --fields 48\n\n"
                     "  # Set slot 4 to 6 fields with layout B:\n"
                     "  python3 fit_patch.py in.fit out.fit --slot 4 "
                     "--fields 178,179,180,181,182,409 --layout 1\n\n"
                     "  # Disable slot 1 without touching its fields:\n"
                     "  python3 fit_patch.py in.fit out.fit --slot 1 --disable\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    parser.add_argument("--force", action="store_true",
                         help="proceed even if the target slot's CURRENT content matches a "
                              "known system-screen heuristic (see check_system_screen_guard() "
                              "-- content pattern OR field count <= "
                              f"{LOW_FIELD_COUNT_THRESHOLD}; neither is a certain "
                              "identification). Without --force, --fields refuses to "
                              "overwrite a matching slot and asks you to confirm on-device "
                              "first.")
    parser.add_argument("--slot", type=int, metavar="N",
                         help="message_index of the screen slot to patch (0-30). Required for "
                              "all operations except --swap-order.")
    parser.add_argument("--fields", metavar="ID,ID,...",
                         help="comma-separated field IDs, in display order (also sets field count). "
                              "Omit to leave the slot's fields/count untouched.")
    parser.add_argument("--swap-fields", metavar="POS,POS",
                         help="swap two field POSITIONS (0-based) within the slot's EXISTING "
                              "field array, leaving field count and every other slot untouched. "
                              "Reads the current array from the input file, swaps exactly those "
                              "two entries, writes back only field 7. Mutually exclusive with "
                              "--fields (which replaces the whole array). Useful for a minimal, "
                              "single-variable content-change test.")
    parser.add_argument("--layout", type=int, choices=[0, 1], metavar="0|1",
                         help="layout variant: 0=A/default, 1=B/alternate")
    enable_group = parser.add_mutually_exclusive_group()
    enable_group.add_argument("--enable", action="store_true",
                               help="mark this screen enabled (matches the on-device "
                                    "\"Show Screen\" toggle set ON). Same as --show.")
    enable_group.add_argument("--disable", action="store_true",
                               help="mark this screen disabled (matches the on-device "
                                    "\"Show Screen\" toggle set OFF -- i.e. \"Hide\"). "
                                    "Same as --hide.")
    enable_group.add_argument("--show", action="store_true",
                               help="alias for --enable, matching on-device wording")
    enable_group.add_argument("--hide", action="store_true",
                               help="alias for --disable, matching on-device wording")
    parser.add_argument("--new-slot", action="store_true",
                         help="this slot was previously unconfigured (sentinel) -- also sets "
                              "field 1 (configured flag) so the slot activates correctly")
    parser.add_argument("--seed-from-slot", type=int, metavar="N",
                         help="copy fields 9 and 10 from an already-configured slot N in the "
                              "SAME input file, verbatim (including duplicating slot N's f9 "
                              "value -- useful for deliberate testing, but see --new-slot's "
                              "auto-default for the normal/safe case).")
    parser.add_argument("--field9", type=int, metavar="N",
                         help="explicit override for field 9 (creation-order stamp). "
                              "Takes priority over --seed-from-slot and the --new-slot "
                              "auto-default. Mostly for deliberate testing.")
    parser.add_argument("--field10", type=int, metavar="N",
                         help="explicit override for field 10 (screen identity -- 0-indexed "
                              "'Screen N' counter for plain user screens; see NAMED_SCREEN_"
                              "TYPES for the fixed codes named Garmin types use instead). "
                              "Takes priority over --seed-from-slot and the --new-slot "
                              "auto-default (next_available_field10()). Only needed to "
                              "override the auto-computed value for deliberate testing.")
    parser.add_argument("--remove", action="store_true",
                         help="PERMANENTLY remove this screen (matches the on-device "
                              "\"Remove\" option, NOT \"Hide\"): sets field 1 to 0 and "
                              "clears fields 9/10 to the sentinel, but leaves the "
                              "screen's field count/content (fields 3/7) untouched -- "
                              "confirmed Removed-state behavior is that content is "
                              "preserved, only identity/order signals go away. "
                              "ONE-WAY: there is no --un-remove (retired, see "
                              "FIT_PATCH.md) -- Restore-from-Backup is the only real "
                              "undo path. Ignores --fields/--layout/--enable/--disable/ "
                              "etc. when used -- this is a separate operation from "
                              "those, same as --swap-order. CONFIRMED via a real "
                              "on-device round-trip test (2026-08-14) -- see "
                              "remove_screen()'s docstring.")
    parser.add_argument("--swap-order", metavar="SLOT,SLOT",
                         help="swap the DISPLAY ORDER of two already-configured screens by "
                              "swapping their field 9 (creation-order stamp) values. f9 "
                              "ascending order == on-device display order (confirmed via "
                              "Gravel's editor sequence). Does NOT touch field count, field "
                              "content, or total screen count -- low eviction risk since the "
                              "screen count never changes. Both slots must already have a "
                              "real (non-sentinel) f9. This is a separate operation from "
                              "--slot/--fields etc. -- ignores --slot when used.")
    # --un-remove RETIRED (v1.13.0, 2026-08-13) -- see BUGS below and
    # PROJECT_NOTES.md "Product note on --un-remove" for the full
    # history. It's no longer a flag this parser accepts.

    args = parser.parse_args()

    if args.swap_order is not None:
        try:
            slot_a, slot_b = (int(x) for x in args.swap_order.split(","))
        except ValueError:
            parser.error("--swap-order expects exactly two comma-separated slot numbers, e.g. --swap-order 4,5")
        _, f9_a, f9_b = swap_display_order(args.input_file, args.output_file, slot_a, slot_b)
        print(f"wrote {args.output_file}: swapped display order -- "
              f"slot {slot_a} f9 {f9_a[0]}->{f9_b[0]}, slot {slot_b} f9 {f9_b[0]}->{f9_a[0]}",
              file=sys.stderr)
        return

    if args.slot is None:
        parser.error("--slot is required (except when using --swap-order)")

    if args.remove:
        # Same two hard guards --hide already enforces, no --force
        # override for either -- see remove_screen()'s docstring for
        # why both are directly-observed facts, not heuristic guesses,
        # and why Remove reuses --hide's exact guard functions rather
        # than needing its own.
        unsupported_type = hide_unsupported_screen_type(args.input_file, args.slot)
        if unsupported_type is not None:
            parser.error(
                f"--remove: slot {args.slot} is a '{unsupported_type}' screen. "
                f"CONFIRMED via direct on-device inspection that this screen "
                f"type has no Remove option at all in the Data Screens editor "
                f"-- there is no --force override, because forcing this write "
                f"here would produce a state with no on-device equivalent to "
                f"compare it against on any profile."
            )
        if would_hide_last_visible_screen(args.input_file, args.slot):
            parser.error(
                f"--remove: slot {args.slot} is currently the ONLY visible "
                f"USER screen on this profile (Garmin-named screens don't "
                f"count toward this). Confirmed via real on-device testing "
                f"that the editor refuses to hide OR remove a profile's last "
                f"remaining user screen -- there is no --force override for "
                f"this, because it isn't a guess: show at least one other "
                f"user screen first, then remove this one."
            )
        remove_screen(args.input_file, args.output_file, args.slot)
        print(f"wrote {args.output_file}: slot {args.slot} REMOVED (f1=0, f9/f10 "
              f"cleared, content preserved) -- this is ONE-WAY, see --remove's "
              f"help text", file=sys.stderr)
        return

    if args.fields is not None and args.swap_fields is not None:
        parser.error("--fields and --swap-fields are mutually exclusive -- "
                     "--fields replaces the whole array, --swap-fields edits it in place")

    changes = {}
    requested_count = None
    if args.swap_fields is not None:
        try:
            pos_a, pos_b = (int(x) for x in args.swap_fields.split(","))
        except ValueError:
            parser.error("--swap-fields expects exactly two comma-separated positions, e.g. --swap-fields 0,1")
        if not (0 <= pos_a <= 9 and 0 <= pos_b <= 9):
            parser.error("--swap-fields positions must be 0-9 (the field array has 10 slots)")
        current_array = read_current_field_array(args.input_file, args.slot)
        if current_array is None:
            parser.error(f"--swap-fields: slot {args.slot} has no readable field array "
                          f"(is it configured? try without --swap-fields first to check)")
        current_array[pos_a], current_array[pos_b] = current_array[pos_b], current_array[pos_a]
        changes[7] = struct.pack('<10H', *current_array)
        print(f"swapped field array positions {pos_a} and {pos_b} in slot {args.slot}: "
              f"now {current_array}", file=sys.stderr)
    elif args.fields is not None:
        ids = [int(x) for x in args.fields.split(",")]
        if len(ids) > 10:
            parser.error("at most 10 fields per screen")

        # Device-dependent CIQ field guard: HARD refuse, no --force
        # override -- same posture as NO_SHOW_TOGGLE_TYPES above, not a
        # heuristic. CONFIRMED via extensive real-hardware testing (see
        # PROJECT_NOTES.md Doc rev 95-97, DEVICE_DEPENDENT_CIQ_IDS in
        # fit_dump.py) that these numeric field IDs are DEVICE-local and
        # install-order-reassigned -- writing one via this tool produces
        # a file that looks correct in the GUI/dump but renders as
        # "Timer" on-device, every single time this was tested. There is
        # nothing --force could safely do here: this isn't a guess about
        # risk, it's a byte pattern this toolkit cannot make work at all.
        blocked = sorted(set(ids) & DEVICE_DEPENDENT_CIQ_IDS)
        if blocked:
            parser.error(
                f"--fields: {blocked} {'is a' if len(blocked) == 1 else 'are'} "
                f"device-dependent Connect IQ field ID{'s' if len(blocked) != 1 else ''} "
                f"(see DEVICE_DEPENDENT_CIQ_IDS in fit_dump.py). CONFIRMED on real "
                f"hardware that this toolkit cannot introduce or relocate one of "
                f"these into a fresh slot -- it renders as \"Timer\" on-device "
                f"regardless of what the file/GUI shows. No --force override: "
                f"only Garmin's own on-device editor can place these, and only "
                f"whole-profile Clone Profile preserves an existing placement."
            )

        # System-screen guard: check the slot's CURRENT content (before
        # this edit) via check_system_screen_guard() -- see that
        # function's docstring. v1.10.0: answers with CERTAINTY via f10
        # whenever available (a real screen TYPE identifier, not a
        # guess); only falls back to a genuine heuristic for the rare
        # slot with no readable f10 (e.g. Removed state).
        if not args.force:
            warning = check_system_screen_guard(args.input_file, args.slot)
            if warning is not None:
                parser.error(
                    f"--fields: slot {args.slot} {warning} If you're confident "
                    f"this is safe to change, re-run with --force."
                )

        requested_count = len(ids)
        changes[3] = pack_field_count(requested_count)
        changes[7] = pack_field_id_array(ids)
    if args.enable or args.show:
        changes[12] = pack_enabled(True)
    if args.disable or args.hide:
        # HARD blocks, no --force override for either -- both are
        # verified facts, not heuristic guesses. (This was previously
        # completely unguarded -- --hide/--disable had no check of any
        # kind before v1.8.0.)
        unsupported_type = hide_unsupported_screen_type(args.input_file, args.slot)
        if unsupported_type is not None:
            parser.error(
                f"--hide: slot {args.slot} is a '{unsupported_type}' screen. "
                f"CONFIRMED via direct on-device inspection that this screen "
                f"type has no Show Screen toggle at all in the Data Screens "
                f"editor -- there is no --force override, because forcing "
                f"f12=1 here would produce a state with no on-device "
                f"equivalent to compare it against on any profile."
            )
        if would_hide_last_visible_screen(args.input_file, args.slot):
            parser.error(
                f"--hide: slot {args.slot} is currently the ONLY visible USER "
                f"screen on this profile (Garmin-named screens don't count "
                f"toward this). Confirmed via real on-device testing that the "
                f"editor refuses to hide or remove a profile's last remaining "
                f"user screen -- there is no --force override for this, "
                f"because it isn't a guess: show at least one other user "
                f"screen first, then hide this one."
            )
        changes[12] = pack_enabled(False)
    if args.new_slot:
        changes[1] = pack_configured_flag()
    if args.new_slot and 12 not in changes:
        # CONFIRMED via device round-trip test: every real device-created
        # screen has f12 set (0=enabled), but a genuinely fresh slot
        # starts with f12 entirely ABSENT (sentinel). Two independent
        # synthetic --new-slot additions that left f12 untouched both
        # failed on NewFiles (merged into an adjacent screen, silently
        # discarded) while a native device-created addition -- which
        # always sets f12=0 -- succeeded. Not fully proven causal yet
        # (see BUGS below), but matching real device behavior here
        # is correct regardless, so this is now the default rather than
        # leaving f12 untouched.
        changes[12] = pack_enabled(True)
        print("note: --new-slot without --enable/--disable -- defaulting field 12 "
              "to 0/enabled (every real device-created screen has this set; a "
              "candidate fix for the add-screen merge issue, see BUGS below)",
              file=sys.stderr)

    if args.seed_from_slot is not None:
        f9_raw = read_raw_field(args.input_file, args.seed_from_slot, 9)
        f10_raw = read_raw_field(args.input_file, args.seed_from_slot, 10)
        if f9_raw == b'\xff' or f10_raw == b'\xff':
            parser.error(
                f"--seed-from-slot {args.seed_from_slot}: source slot's field 9 or 10 is "
                f"itself at the sentinel value -- can't seed from an unconfigured/incomplete "
                f"slot. Pick a slot known to be fully configured (e.g. one the device created "
                f"itself)."
            )
        changes[9] = f9_raw
        changes[10] = f10_raw
        print(f"seeded fields 9,10 from slot {args.seed_from_slot}: "
              f"9={f9_raw.hex()} 10={f10_raw.hex()}", file=sys.stderr)

    # Explicit overrides always win, regardless of --seed-from-slot.
    if args.field9 is not None:
        changes[9] = pack_uint8(args.field9)
    if args.field10 is not None:
        changes[10] = pack_uint8(args.field10)

    # --new-slot safety net: fields 9/10 have been shown (device
    # round-trip test) to cause the ENTIRE slot to be silently
    # discarded/merged on reboot if left colliding with an existing
    # slot's value -- f9 needs to be globally unique, and f10 needs to
    # be free among the profile's user-screen identities (CONFIRMED via
    # live on-device round-trip, 2026-08-05: an f10 collision with an
    # existing user screen gets merged/discarded by NewFiles
    # reconciliation; a free f10 survives intact). Auto-fill only what
    # wasn't already set above by --field9/--field10/--seed-from-slot,
    # so this never overrides an explicit choice.
    if args.new_slot:
        if 9 not in changes:
            auto_f9 = next_available_field9(args.input_file)
            changes[9] = pack_uint8(auto_f9)
            print(f"note: auto-assigning field 9 = {auto_f9} (next unused value; "
                  f"f9 appears to need to be globally unique)", file=sys.stderr)
        if 10 not in changes:
            auto_f10 = next_available_field10(args.input_file)
            changes[10] = pack_uint8(auto_f10)
            print(f"note: auto-assigning field 10 = {auto_f10} (next unused user-screen "
                  f"identity; CONFIRMED via live device test -- shows on-device as "
                  f"'Screen {auto_f10 + 1}')", file=sys.stderr)

    # --- layout: figure out what value will actually end up on disk,
    # even if this call doesn't touch field 8, so we can validate it. ---
    current_count, current_layout = read_current_count_and_layout(args.input_file, args.slot)
    effective_count = requested_count if requested_count is not None else current_count

    if args.layout is not None:
        effective_layout = args.layout
    elif args.new_slot:
        # Don't leave a brand-new slot's layout at the untested sentinel --
        # every screen the device has ever created itself has this set.
        effective_layout = 0
        print("note: --new-slot without --layout -- defaulting field 8 (layout) to 0/A",
              file=sys.stderr)
    else:
        effective_layout = current_layout  # may be None if never configured

    if effective_layout == 1 and effective_count not in COUNTS_WITH_B_VARIANT:
        parser.error(
            f"--layout 1 (B/alternate) requested but the effective field count "
            f"({effective_count!r}) has no confirmed B variant on-device. "
            f"Only {sorted(COUNTS_WITH_B_VARIANT)}-field screens have a real A/B choice. "
            f"Use --layout 0 (or omit --layout) instead."
        )
    if effective_layout == 1 and effective_count is None:
        parser.error(
            "--layout 1 requested but the field count can't be determined "
            "(slot is currently unconfigured and --fields wasn't given). "
            "Specify --fields so the effective count is known before requesting a B variant."
        )

    # Only write field 8 if this call is actually supposed to set it --
    # either explicitly via --layout, or implicitly via the --new-slot
    # default above. Never silently overwrite an existing slot's layout
    # just because we computed an effective_layout for validation.
    if args.layout is not None:
        changes[8] = pack_layout_variant(args.layout)
    elif args.new_slot:
        changes[8] = pack_layout_variant(0)

    if not changes:
        parser.error("nothing to do -- specify at least one of --fields/--layout/--enable/--disable")

    # Device-dependent CIQ guard, PASS 2: checks the slot's CURRENT
    # on-disk content, independent of the request-side check above
    # (which only catches a CIQ id being freshly REQUESTED). HARD
    # refuse, no --force -- see screen_has_device_dependent_ciq_field()
    # for the real-hardware evidence (2026-09-03) behind why this
    # second check exists at all: rearranging OTHER fields around an
    # already-placed CIQ field broke it just as completely as trying
    # to introduce one fresh, even though its own id/bytes never
    # changed. Only fires when this call actually touches the screen's
    # shape (f3 count / f7 array / f8 layout) -- --enable/--disable
    # alone (f12 only) don't go through this, since there's no
    # confirmed evidence yet that Show/Hide alone affects the linkage.
    if {3, 7, 8} & set(changes.keys()):
        present = screen_has_device_dependent_ciq_field(args.input_file, args.slot)
        if present:
            parser.error(
                f"slot {args.slot} currently contains device-dependent Connect "
                f"IQ field ID(s) {present} (see DEVICE_DEPENDENT_CIQ_IDS in "
                f"fit_dump.py). CONFIRMED on real hardware (2026-09-03) that "
                f"rewriting this screen's count/field-array/layout AT ALL -- "
                f"even just adding/removing/rearranging OTHER, ordinary "
                f"fields around it -- breaks the CIQ field's on-device linkage "
                f"exactly like trying to introduce one fresh does, and it "
                f"renders as \"Timer\" afterward regardless of what the file/"
                f"GUI shows. No --force override: leave this screen alone via "
                f"this tool entirely: only Garmin's own on-device editor can "
                f"restructure a screen that has one of these without breaking "
                f"it."
            )

    patch_screen(args.input_file, args.output_file, args.slot, changes)
    print(f"wrote {args.output_file}: slot {args.slot} patched with {sorted(changes.keys())}")


if __name__ == "__main__":
    _cli()
