#!/usr/bin/env python3
__version__ = "1.0.0"  # THE BENCH DIFF, AS A TOOL (2026-10-28). Every useful conclusion between Doc revs 179 and 195 came from comparing two profile files -- what was sent against what the device returned -- and every one of them was run by hand in an ad-hoc script. Three of those runs reached a WRONG conclusion (revs 189, 193) and the cause each time was a hand-assembled comparison: a substituted baseline, a forgotten pairing rule. A one-line command cannot substitute the wrong file for you, but it can stop the comparison itself from being improvised. Pairs by f10 (screen identity) and ALSO by message_index (slot), and prints both -- because the disagreement between them is the finding, not noise: it is how rev 190 established the device renumbers, and how rev 192 established what triggers it. stdlib only, like fit_raw_walk and garmin_device.

USAGE = """
Compare two Garmin Edge activity-profile .fit files.

The question this answers, which came up on nearly every bench run:

    "I sent the device THIS file. It gave me back THAT one.
     What changed, and was it me or the device?"

Usage:

    python3 fit_profile_diff.py SENT.fit RETURNED.fit
    python3 fit_profile_diff.py SENT.fit RETURNED.fit --verbose

Reads both files and reports:

  * whether they are byte-identical (the strongest possible result --
    it means the device rewrote nothing at all)
  * which screens MOVED to a different slot (the device renumbering)
  * which screens CHANGED content, paired by f10 screen identity
  * what a slot-based pairing would have said instead

WHY BOTH PAIRINGS. A device import can move a screen to a different
message_index with its content untouched. Pairing by slot then
compares unrelated screens and reports differences nobody made -- on a
real renumbered pair, 11 of them on a byte-identical profile (Doc rev
190). Pairing by f10 is correct. This tool prints both so that the
DISAGREEMENT is visible: f10 saying "no change" while slots say
"everything changed" is the signature of a renumbering import, and
that signature is itself evidence worth having.

Exit status: 0 if the profiles are equivalent (no moves, no content
differences), 1 if they differ, 2 on a read error. So it is usable in
a shell loop over a backup folder.

Named USAGE rather than left as a module docstring: this project puts
__version__ on line 2, before any string literal, so a block here is
NOT __doc__ -- __doc__ is None and printing it raises AttributeError.
Caught by running the tool with no arguments. Every module in the
toolkit has this shape, so do not "restore" this to __doc__.
"""

import os
import struct
import sys

import fit_raw_walk

try:
    import fit_dump
    _field_name = fit_dump.field_name
    _screen_name = fit_dump.screen_type_name
except Exception:                                    # pragma: no cover
    # Degrade to raw ids rather than refusing to run. This tool's whole
    # point is being available in a hurry.
    def _field_name(fid, terse=False):
        return f"id {fid}"

    def _screen_name(f10):
        return None

DATA_SCREEN = 14
UNSET8 = 0xFF


def _one(d, key):
    """Single-byte field, or None if absent/not one byte."""
    v = d.get(key)
    return v[0] if v is not None and len(v) == 1 else None


def read_screens(path):
    """
    Every data_screen message in the file, keyed by message_index.

    Deliberately NOT filtered to configured screens: an unconfigured
    slot becoming configured is exactly the kind of change worth
    seeing, and it is what the A2 run turned out to be.
    """
    out = {}
    # parse_fit returns (messages, hdr_size, end_of_data, total_len);
    # index rather than unpack, so adding a return value upstream does
    # not break this.
    records = fit_raw_walk.parse_fit(path)[0]
    for rec in records:
        if rec.get("kind") != "data" or rec.get("mesg_num") != DATA_SCREEN:
            continue
        d = {num: val for num, _sz, _t, val in rec["fields"]}
        raw254 = d.get(254)
        if raw254 is None or len(raw254) != 2:
            continue
        f7 = d.get(7)
        out[struct.unpack("<H", raw254)[0]] = {
            "mi": struct.unpack("<H", raw254)[0],
            "configured": _one(d, 1),
            "count": _one(d, 3),
            "f10": _one(d, 10),
            "variant": _one(d, 8),
            "order": _one(d, 9),
            "hidden": _one(d, 12),
            "fields": struct.unpack("<10H", f7) if f7 and len(f7) == 20 else None,
        }
    return out


def identity(scr):
    """
    The stable handle for a screen across a device import.

    f10 for a configured screen that has one; the slot number
    otherwise, because an unconfigured slot has no identity of its own
    and the slot is the only thing left to call it.
    """
    if scr["configured"] == 1 and scr["f10"] not in (None, UNSET8):
        return ("f10", scr["f10"])
    return ("slot", scr["mi"])


def label(key, scr=None):
    if key == ("slot", -1):
        return "unconfigured slots"
    if key[0] == "f10":
        name = _screen_name(key[1])
        return f"{name} (f10={key[1]})" if name else f"f10={key[1]}"
    return f"slot {key[1]} (unconfigured)"


def describe_fields(a, b):
    """Positional field differences between two 10-slot arrays."""
    if a["fields"] is None or b["fields"] is None:
        return ["field array unreadable on one side"]
    return [
        f"field {i + 1}: {u} {_field_name(u)} -> {v} {_field_name(v)}"
        for i, (u, v) in enumerate(zip(a["fields"], b["fields"]))
        if u != v
    ]


ATTRS = (("count", "field count"), ("variant", "layout variant"),
         ("order", "display order"), ("hidden", "hidden flag"),
         ("configured", "configured flag"))


def is_blank(scr):
    """
    An unconfigured slot: a placeholder carrying no information.

    These have no identity of their own, so when a configured screen
    moves INTO a slot a blank was occupying, the blank is displaced to
    wherever the configured one came from. Pairing blanks by slot then
    reports two spurious "present on only one side" differences for
    every real move -- which is the very false-difference class this
    tool exists to avoid, reproduced inside the tool. Found by running
    it against the rev 190 pair, where the answer was already known.

    So blanks are counted, not paired. Only a CHANGE IN HOW MANY of
    them there are is a real difference.
    """
    return scr["configured"] != 1


def compare(sent, returned, pair_by_identity=True):
    """Returns (moves, differences). Pure; both pairings share it."""
    key = identity if pair_by_identity else (lambda s: ("slot", s["mi"]))

    if pair_by_identity:
        amap = {key(s): s for s in sent.values() if not is_blank(s)}
        bmap = {key(s): s for s in returned.values() if not is_blank(s)}
        blanks_a = sum(1 for s in sent.values() if is_blank(s))
        blanks_b = sum(1 for s in returned.values() if is_blank(s))
    else:
        amap = {key(s): s for s in sent.values()}
        bmap = {key(s): s for s in returned.values()}
        blanks_a = blanks_b = 0

    moves, diffs = [], []
    if blanks_a != blanks_b:
        diffs.append((("slot", -1),
                      f"unconfigured slot count: {blanks_a} -> {blanks_b}"))

    for k in sorted(set(amap) | set(bmap), key=lambda t: (t[0], t[1])):
        a, b = amap.get(k), bmap.get(k)
        if a is None or b is None:
            side = "sent" if b is None else "returned"
            diffs.append((k, f"present only in the {side} file"))
            continue
        if a["mi"] != b["mi"]:
            moves.append((k, a["mi"], b["mi"]))
        for attr, pretty in ATTRS:
            if a[attr] != b[attr]:
                diffs.append((k, f"{pretty}: {a[attr]} -> {b[attr]}"))
        for line in describe_fields(a, b):
            diffs.append((k, line))
    return moves, diffs


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    verbose = "--verbose" in argv or "-v" in argv
    if len(args) != 2:
        print(USAGE.strip())
        return 2

    sent_path, returned_path = args
    try:
        raw_a = open(sent_path, "rb").read()
        raw_b = open(returned_path, "rb").read()
        sent = read_screens(sent_path)
        returned = read_screens(returned_path)
    except (OSError, struct.error, ValueError) as e:
        print(f"Could not read a profile: {e}", file=sys.stderr)
        return 2

    print(f"sent     {os.path.basename(sent_path):<40} "
          f"{len(raw_a):>6} bytes, {len(sent)} screens")
    print(f"returned {os.path.basename(returned_path):<40} "
          f"{len(raw_b):>6} bytes, {len(returned)} screens")

    if raw_a == raw_b:
        print("\nBYTE-IDENTICAL. The device rewrote nothing.")
        return 0

    moves, diffs = compare(sent, returned, pair_by_identity=True)
    slot_moves, slot_diffs = compare(sent, returned, pair_by_identity=False)

    print(f"\n--- paired by screen identity (f10) -- the correct reading ---")
    if moves:
        print(f"{len(moves)} screen(s) MOVED to a different slot "
              f"(the device renumbered):")
        for k, old, new in moves:
            print(f"  {label(k)}: slot {old} -> {new}")
    else:
        print("no screens moved")

    if diffs:
        print(f"\n{len(diffs)} content difference(s):")
        last = None
        for k, line in diffs:
            if k != last:
                print(f"  {label(k)}:")
                last = k
            print(f"    {line}")
    else:
        print("no content differences")

    print(f"\n--- paired by slot number -- what the old comparison said ---")
    print(f"{len(slot_diffs)} difference(s)")
    if verbose:
        last = None
        for k, line in slot_diffs:
            if k != last:
                print(f"  slot {k[1]}:")
                last = k
            print(f"    {line}")

    if len(slot_diffs) != len(diffs):
        print(f"\n  NOTE: the two pairings disagree ({len(diffs)} vs "
              f"{len(slot_diffs)}). That is the signature of a "
              f"renumbering import, not a bug in either -- see Doc rev 190.")

    # The files differ in bytes but may still be equivalent as profiles:
    # the device can rewrite a header or reorder records without changing
    # a single screen. Say so rather than implying a change happened.
    if not moves and not diffs:
        print("\nThe files differ in bytes but NO SCREEN DIFFERS. "
              "Something outside the data_screen messages changed.")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
