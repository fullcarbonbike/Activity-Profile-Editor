#!/usr/bin/env python3
"""
fit_census.py -- RAW screen census across a folder of Activity Profile
`.fit` files. Read-only: this script never opens a file for writing.

WHY THIS EXISTS, AND WHY IT REPORTS NO NAMES
--------------------------------------------
Every layout constant in this toolkit (`LAYOUT_GRIDS`,
`COUNTS_WITH_B_VARIANT`, `NAMED_SCREEN_TYPES`, `NAMED_SCREEN_LAYOUTS`)
was measured on an Edge 530 and is currently applied to every device.
PROJECT_NOTES.md Doc rev 120 established that this is wrong: the 840's
editor offers A/B/C layout variants for field counts 3-9 where the 530
offers A/B for 3-7 and nothing at all for 8-9.

Surveying a new model therefore means finding out which
`(field count, layout variant)` combinations that model ACTUALLY USES,
and a profile pulled off a device is direct evidence about that device.
This script extracts that evidence.

It deliberately prints **raw numbers and no interpretation.** No screen
type names, no layout letters, no "unknown field" flags. Two reasons:

  1. `NAMED_SCREEN_TYPES` is known-incomplete for every model except the
     530 (Doc rev 120 SS3 -- all seven of the 840's f10 codes are absent),
     so a classified census would mislabel the very screens being
     surveyed. Raw f10/f8/f3 values are unaffected by that gap.
  2. A/B/C are the ON-DEVICE MENU's names, positional and not derivable
     from the stored number (Doc rev 120 SS2). Printing "B" next to an f8
     this script did not confirm would manufacture exactly the kind of
     unearned certainty Doc rev 118 was written about.

Interpretation is the reader's job. This reports what is in the bytes.

USAGE
-----
    python3 fit_census.py <folder-or-file> [...]           # CSV to stdout
    python3 fit_census.py <folder> --out census.csv
    python3 fit_census.py <folder> --summary               # the (f3,f8) question
    python3 fit_census.py <folder> --summary --out -       # both to stdout

`--summary` answers the question that prompted this script: which
`(f3, f8)` pairs occur, grouped by device serial, so one folder holding
two models' profiles still yields one table per device.

Non-profile `.fit` files (Totals.fit, Device.fit, Locations.fit) are
skipped by checking `file_id.type == 4` (sport) -- the same test
`fit_dump.is_profile_file()` makes, reimplemented here from raw bytes so
this script depends on nothing but `fit_raw_walk` and the stdlib, and so
it keeps working on a model whose files the rest of the toolkit cannot
yet classify.
"""

import argparse
import csv
import os
import struct
import sys
from collections import defaultdict

import fit_raw_walk
import fit_dump

__version__ = "1.1.0"  # Added a `model` column so a whole folder of backups is attributable in one command, and f4/f6/f11 columns -- three mesg-14 fields present on BOTH models that this project had never decoded, surfaced because anything without a column lands in `extra`. f7_active (the first f3 entries) is now reported separately from f7_nonempty: f7 is a fixed 10-slot array and only the first f3 entries are read by the device, the rest being stale ids left by an earlier shrink. Treating trailing slots as content is how the 2026-08-17 field-ID batch went wrong.

DATA_SCREEN_MESG_NUM = 14
FILE_ID_MESG_NUM = 0
FILE_TYPE_SPORT = 3      # VERIFIED against real files, not assumed: a
                         # profile's file_id.type reads 3, Totals.fit
                         # reads 10. (First draft of this script used 4,
                         # which is `activity`, and silently censused
                         # zero screens across a whole folder -- a wrong
                         # filter constant fails as "nothing to report",
                         # which looks exactly like a clean run.)

# Byte width of one element of each FIT base type. Same table
# fit_raw_walk.parse_fit() uses internally; duplicated rather than
# imported because it is a local in that function.
BASE_TYPE_SIZE = {
    0x00: 1, 0x01: 1, 0x02: 1, 0x83: 2, 0x84: 2, 0x85: 4, 0x86: 4,
    0x07: 1, 0x88: 4, 0x89: 4, 0x0A: 1, 0x8B: 2, 0x8C: 4, 0x0D: 1,
    0x8E: 4, 0x8F: 8, 0x90: 8, 0x91: 8, 0x92: 8, 0x93: 8,
}

# Signed base types, so a sentinel prints as the value actually stored
# rather than as a negative surprise.
_SIGNED = {0x01, 0x83, 0x85, 0x88, 0x89, 0x8E, 0x8F, 0x91}

# struct format letters by (element size, signed).
_FMT = {(1, False): 'B', (1, True): 'b',
        (2, False): 'H', (2, True): 'h',
        (4, False): 'I', (4, True): 'i',
        (8, False): 'Q', (8, True): 'q'}

# data_screen fields given their own column. Anything NOT in here is
# reported in the `extra` column -- which is how the 840's field 14 would
# have announced itself, and how the next model's novelty will.
#
# f4, f6 and f11 were added here after the first real run: they are
# present on BOTH the 530 and the 840 and are absent from this project's
# mesg-14 documentation entirely. They are NOT decoded -- reported raw so
# a pattern can be spotted, not interpreted.
KNOWN_SCREEN_FIELDS = {1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 254}

CSV_COLUMNS = [
    "file", "model", "serial", "manufacturer", "product",
    "msg_index", "f1_state", "f3_count", "f8_variant", "f9_order",
    "f10_type", "f12_hidden",
    "f7_field_ids", "f7_active", "f7_nonempty",
    "f4", "f6", "f11", "f5", "f14", "extra",
]


def _decode(raw, base_type, endian):
    """
    Decode one raw field value into a scalar or list of ints. Returns
    the raw hex string for anything that doesn't divide evenly into its
    base type's element size (malformed, or a base type not in the
    table) -- a census should surface such a field, not drop it.
    """
    elem = BASE_TYPE_SIZE.get(base_type)
    if not elem or not raw or len(raw) % elem:
        return raw.hex() if raw else None
    fmt = _FMT.get((elem, base_type in _SIGNED))
    if fmt is None:                       # strings and byte arrays
        return raw.hex()
    n = len(raw) // elem
    vals = list(struct.unpack(endian + fmt * n, raw))
    return vals[0] if n == 1 else vals


def _read_messages(path):
    """
    parse_fit() records endianness on DEFINITION messages only, so walk
    in order and carry the last definition per local type forward onto
    the data messages that use it. Yields (mesg_num, {def_num: (value,
    base_type)}) for data messages only.
    """
    messages, _hdr, _eod, _total = fit_raw_walk.parse_fit(path)
    endian_by_local = {}
    for m in messages:
        if m['kind'] == 'def':
            endian_by_local[m['local_type']] = m.get('endian', '<')
            continue
        if m['kind'] != 'data':
            continue
        endian = endian_by_local.get(m['local_type'], '<')
        decoded = {}
        for (def_num, _size, base_type, raw) in m['fields']:
            decoded[def_num] = (_decode(raw, base_type, endian), base_type)
        yield m['mesg_num'], decoded


def _fmt_cell(value):
    """List -> space-separated, so the CSV stays one cell per field."""
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def census_file(path):
    """
    Returns (file_info, rows) for one profile, or (None, []) if the file
    is not a sport profile or cannot be parsed. Never raises on a bad
    file -- a census run over a folder should report what it could read
    rather than dying on the first oddity.
    """
    try:
        msgs = list(_read_messages(path))
    except Exception as exc:                      # noqa: BLE001
        print(f"  ! {os.path.basename(path)}: unreadable ({exc})",
              file=sys.stderr)
        return None, []

    file_id = next((d for num, d in msgs if num == FILE_ID_MESG_NUM), None)
    if not file_id:
        return None, []

    def val(d, num):
        got = d.get(num)
        return got[0] if got else None

    if val(file_id, 0) != FILE_TYPE_SPORT:
        return None, []                           # Totals/Device/Locations

    product = val(file_id, 2)
    info = {
        "file": os.path.basename(path),
        # Model NAME resolved from the product id. Added 2026-09-28 so a
        # whole folder of backups can be attributed in one command --
        # `dump` mode reported the product id but only amid everything
        # else, and `screens` did not report it at all.
        "model": fit_dump.KNOWN_MODELS.get(product) or "",
        "serial": val(file_id, 3),
        "manufacturer": val(file_id, 1),
        "product": product,
    }

    rows = []
    for num, d in msgs:
        if num != DATA_SCREEN_MESG_NUM:
            continue
        ids = d.get(7, (None,))[0]
        id_list = ids if isinstance(ids, list) else ([ids] if ids is not None else [])
        row = dict(info)
        row.update({
            "msg_index":   _fmt_cell(val(d, 254)),
            "f1_state":    _fmt_cell(val(d, 1)),
            "f3_count":    _fmt_cell(val(d, 3)),
            "f8_variant":  _fmt_cell(val(d, 8)),
            "f9_order":    _fmt_cell(val(d, 9)),
            "f10_type":    _fmt_cell(val(d, 10)),
            "f12_hidden":  _fmt_cell(val(d, 12)),
            "f7_field_ids": _fmt_cell(ids),
            # f7 is a FIXED 10-slot array and f3 says how many slots the
            # device actually reads. Slots past f3 routinely hold STALE
            # ids left behind when a screen was shrunk -- observed
            # directly: an 840 Map screen with f3=0 still carries 10
            # plausible-looking ids, and f10=57 and f10=162 carry the
            # SAME 8, which is template residue rather than content.
            #
            # So f7_active is the evidence; f7_nonempty is not. Reading
            # trailing slots as real content would inject junk ids into a
            # field-ID census, which is exactly how the 2026-08-17 batch
            # went wrong.
            "f7_active":   _fmt_cell(id_list[:val(d, 3)]
                                     if isinstance(val(d, 3), int)
                                     and val(d, 3) <= len(id_list)
                                     else None),
            "f7_nonempty": sum(1 for v in id_list if v not in (None, 0xFFFF)),
            "f4":          _fmt_cell(val(d, 4)),
            "f6":          _fmt_cell(val(d, 6)),
            "f11":         _fmt_cell(val(d, 11)),
            "f5":          _fmt_cell(val(d, 5)),
            "f14":         _fmt_cell(val(d, 14)),
            "extra":       ";".join(
                f"f{n}={_fmt_cell(v)}"
                for n, (v, _bt) in sorted(d.items())
                if n not in KNOWN_SCREEN_FIELDS
            ),
        })
        rows.append(row)
    return info, rows


def iter_fit_paths(targets):
    for t in targets:
        if os.path.isdir(t):
            for name in sorted(os.listdir(t)):
                if name.lower().endswith(".fit"):
                    yield os.path.join(t, name)
        elif os.path.isfile(t):
            yield t
        else:
            print(f"  ! not found: {t}", file=sys.stderr)


def print_summary(rows, stream):
    """
    The (f3, f8) table, grouped by serial. Active screens only (f1==1):
    an inactive slot's stored count and variant are leftovers, not
    evidence of what the device offers.
    """
    by_serial = defaultdict(lambda: defaultdict(set))
    types_by_serial = defaultdict(lambda: defaultdict(set))
    for r in rows:
        if r["f1_state"] != "1":
            continue
        s = r["serial"] or "unknown"
        count, variant = r["f3_count"], r["f8_variant"]
        if count == "" and variant == "":
            continue
        by_serial[s][count].add(variant)
        types_by_serial[s][r["f10_type"]].add((count, variant))

    for serial in sorted(by_serial, key=str):
        print(f"\n=== serial {serial} -- ACTIVE screens only ===", file=stream)
        print("  f3 (count) -> f8 variants seen", file=stream)
        for count in sorted(by_serial[serial], key=lambda c: (len(c), c)):
            variants = sorted(by_serial[serial][count], key=str)
            print(f"    {count:>4} -> {', '.join(variants)}", file=stream)

        print("  f10 (type) -> (count, variant) pairs seen", file=stream)
        for f10 in sorted(types_by_serial[serial], key=lambda c: (len(c), c)):
            pairs = sorted(types_by_serial[serial][f10], key=str)
            shown = ", ".join(f"({c},{v})" for c, v in pairs)
            print(f"    {f10:>4} -> {shown}", file=stream)

        distinct = {v for vs in by_serial[serial].values() for v in vs}
        print(f"  distinct f8 values on this device: "
              f"{', '.join(sorted(distinct, key=str))}", file=stream)


def main():
    ap = argparse.ArgumentParser(
        description="Raw screen census over Activity Profile .fit files. "
                    "Read-only; prints stored values with no "
                    "interpretation.")
    ap.add_argument("targets", nargs="+",
                    help="folders and/or .fit files to census")
    ap.add_argument("--out", default=None,
                    help="write CSV here ('-' for stdout; default stdout "
                         "unless --summary is given alone)")
    ap.add_argument("--summary", action="store_true",
                    help="also print the (f3,f8) and f10 tables, grouped "
                         "by device serial, to stderr")
    args = ap.parse_args()

    all_rows, files_seen, skipped = [], 0, 0
    for path in iter_fit_paths(args.targets):
        info, rows = census_file(path)
        if info is None:
            skipped += 1
            continue
        files_seen += 1
        all_rows.extend(rows)

    print(f"  {files_seen} profile(s), {len(all_rows)} screen record(s); "
          f"{skipped} non-profile/unreadable file(s) skipped",
          file=sys.stderr)

    want_csv = args.out is not None or not args.summary
    if want_csv:
        if args.out in (None, "-"):
            w = csv.DictWriter(sys.stdout, fieldnames=CSV_COLUMNS)
            w.writeheader()
            w.writerows(all_rows)
        else:
            with open(args.out, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
                w.writeheader()
                w.writerows(all_rows)
            print(f"  CSV -> {args.out}", file=sys.stderr)

    if args.summary:
        print_summary(all_rows, sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
