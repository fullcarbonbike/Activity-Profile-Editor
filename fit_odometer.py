#!/usr/bin/env python3
__version__ = "1.0.1"  # QUOTING HINTS, FROM DOUG USING IT (2026-10-31). Half his profiles are named with a space ("ROAD A1"), and an unquoted --profile ROAD A1 fails inside argparse as "unrecognized arguments: A1" -- accurate and useless. The hint cannot live in find_one() because argparse exits before any of this module's code runs, so _Parser overrides error() and appends the fix when the message is about unrecognized arguments. find_one() separately suggests a near match for the two realistic typos: a case slip, and a name truncated at its first word, which is what an unquoted space produces when it does NOT trip argparse. Docs and --help now show a spaced example; they only ever showed single-word names, which is how the gap survived. No behaviour change to any write path. Prior entry (1.0.0): RESET TAKES SEVERAL PROFILES, SET TAKES ONE AND SAYS SO (2026-10-29). Doug's stated workflow is a reset every January 1st, which covers every profile at once -- four chained invocations for an annual task is the kind of friction that makes a tool go unused. `reset --profile A --profile B ...` resolves EVERY name before writing anything, so a typo among good names touches nothing rather than zeroing half the list and then failing. `set` is deliberately NOT repeatable: one set of values cannot be right for two profiles. It still takes action=append, purely so that passing two can be REFUSED -- plain argparse silently keeps the last, and quietly writing your numbers to a profile you did not name is the worst thing this tool could do. A duplicate --profile is refused too. The preview now lists what will be left Untouched, because with several names the thing worth checking before pressing y is what is NOT in the list. #106 AS A CLI, NOT A GUI PANEL (2026-10-29, Doug's design). SCOPE_106_odometer.md scoped a GUI feature with a prerequisite bug and three open questions; a path-in/path-out CLI removes all four. (1) The backup-store collision is GONE, not fixed: that bug existed because backing Totals.fit into working_dir/backups/ made it appear in Restore-a-Deleted-Profile's picker, which finds candidates by "filename ends in .fit". This tool follows fit_patch's input_file/output_file convention, never writes in place and never touches the backup store, so the collision cannot arise. (2) It WORKS ON THE 840, which the GUI version could not have -- that write path was device-mode-only and the 840 has no device mode. A file path serves both models identically. (3) "Where does Totals.fit live?" -- the user says. (4) "Direct overwrite or NewFiles?" -- neither; it emits a file and tells you to use NewFiles, which is both the proven route (rev 118) and the only route (MEMORY_LOG.md 235). UNITS ARE EXPLICIT BY REQUIREMENT, not by default: a bare number for distance or time is REFUSED. The stored units are metres and seconds, the user thinks in miles and hours, and a silent unit error here writes a wrong lifetime odometer that the device then ACCUMULATES ON -- the one mistake in this tool that is expensive and invisible. NAME IS THE ONLY KEY: field 3 (sport) is unreliable -- on Doug's own 530, GRAVEL carries sport=255 despite being a real cycling profile with hundreds of logged miles, while the zeroed test profiles carry sport=2. Same conclusion #168 reached for profile files, reached again here independently.

"""
Read and edit a Garmin Edge `Totals.fit` -- the per-profile odometer.

    python3 fit_odometer.py list   TOTALS.fit
    python3 fit_odometer.py reset  IN.fit OUT.fit --profile ROAD
    python3 fit_odometer.py reset  IN.fit OUT.fit --profile "ROAD A1"
    python3 fit_odometer.py set    IN.fit OUT.fit --profile "ROAD A1" \\
                                   --distance 2240mi --time 189:42 \\
                                   --calories 59553 --rides 64

Four fields are writable per record (established revs 118/168/169):

    f0  timer time   uint32, SECONDS
    f1  distance     uint32, METRES
    f2  calories     uint32, kcal
    f5  sessions     uint16, a count

`sport` (f3), `sport_index` (f9), the name (f10) and `message_index`
(f254) are NEVER written. Record identity is the device's, not ours.

The device treats what you write as a BASELINE IT ADDS TO (rev 168), so
the number to enter is the total AS OF NOW -- after which the Edge keeps
counting. Entering a year-to-date figure mid-season is correct and will
keep accruing; entering a lifetime figure when you meant YTD is a
mistake only you can catch.

YOU DECIDE WHAT THE ODOMETER SHOWS. There is no correct value to
restore, and this tool deliberately does not imply one. Three sane
choices, none more legitimate than the others:

  * LEAVE IT -- the device's own count of what it recorded on that
    profile. Accurate about this Edge; silent about every ride on any
    other device.
  * RESET IT -- `reset` zeroes the four fields, after which the Edge
    starts accumulating again. A reset each January 1st turns the
    odometer into a year-to-date figure, which is a common reason to
    want this tool at all.
  * SET IT -- from whatever report you trust, for whatever span you
    care about.

If you take a number from Garmin Connect (Reports / Statistics), be
aware its own categories do not agree with each other. On one real
account, asking for "Road", "Road Cycling" and "Cycling" returned
three different totals for what the rider considered the same riding,
the largest several times the smallest.
Connect also groups by activity TYPE while the Edge groups by PROFILE
NAME, so two profiles recording as the same type cannot be split
apart there. Pick the figure that means what you want the odometer to
mean; the toolkit will not second-guess it.

Only four of Connect's ~20 columns have anywhere to go here -- no
ascent, descent, average speed, heart rate, cadence or power.

This module is stdlib + fit_raw_walk + fit_crc, like garmin_device.
"""

import argparse
import os
import re
import struct
import sys

import fit_raw_walk
from fit_crc import fit_crc

TOTALS_MESG = 33

# field def_num -> (label, how it is stored)
F_TIMER, F_DIST, F_CAL, F_SPORT, F_SESSIONS, F_SPORT_IDX, F_NAME, F_INDEX = (
    0, 1, 2, 3, 5, 9, 10, 254)

WRITABLE = {
    F_TIMER:    "time",
    F_DIST:     "distance",
    F_CAL:      "calories",
    F_SESSIONS: "rides",
}

METRES_PER_MILE = 1609.344


# --------------------------------------------------------------- reading

def _uint(raw):
    """Little-endian unsigned int of whatever width this field is."""
    if len(raw) == 4:
        return struct.unpack('<I', raw)[0]
    if len(raw) == 2:
        return struct.unpack('<H', raw)[0]
    if len(raw) == 1:
        return raw[0]
    raise ValueError(f"unexpected field width {len(raw)}")


def read_records(path):
    """
    Every totals record in the file, in file order.

    Returns a list of dicts. `raw` holds the parsed message so the
    patcher can find byte offsets without re-walking the file.

    A missing or unreadable path exits with a message rather than a
    traceback -- found by mistyping one. A stack trace is a fine
    answer for a programming error and a poor one for a typo.
    """
    if not os.path.isfile(path):
        sys.exit(f"No such file: {path}")
    out = []
    try:
        msgs = fit_raw_walk.parse_fit(path)[0]
    except (OSError, struct.error, ValueError, IndexError) as e:
        sys.exit(f"Could not read {os.path.basename(path)} as a FIT file: {e}")
    for msg in msgs:
        if msg.get('kind') != 'data' or msg.get('mesg_num') != TOTALS_MESG:
            continue
        d = {num: raw for num, _size, _type, raw in msg['fields']}
        name = d.get(F_NAME, b'')
        name = name.split(b'\x00')[0].decode('ascii', 'replace') if name else ''
        out.append({
            'index':    _uint(d[F_INDEX]) if F_INDEX in d else None,
            'name':     name,
            'time':     _uint(d[F_TIMER]) if F_TIMER in d else None,
            'distance': _uint(d[F_DIST]) if F_DIST in d else None,
            'calories': _uint(d[F_CAL]) if F_CAL in d else None,
            'rides':    _uint(d[F_SESSIONS]) if F_SESSIONS in d else None,
            'sport':    _uint(d[F_SPORT]) if F_SPORT in d else None,
            'raw':      msg,
        })
    return out


def assert_totals_file(path, records):
    if not records:
        sys.exit(f"{os.path.basename(path)} holds no totals records -- "
                 f"this does not look like a Totals.fit.")


# -------------------------------------------------------------- formatting

def fmt_distance(metres):
    if metres is None:
        return "-"
    return f"{metres / METRES_PER_MILE:,.1f} mi"


def fmt_time(seconds):
    if seconds is None:
        return "-"
    return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}"


def print_table(records, path):
    print(f"{os.path.basename(path)} -- {len(records)} records\n")
    print(f"{'#':>3}  {'profile':<16}{'distance':>14}{'time':>10}"
          f"{'calories':>10}{'rides':>7}   editable")
    for r in records:
        editable = "yes" if r['name'] else "no   (unnamed)"
        print(f"{r['index']:>3}  {(r['name'] or '--'):<16}"
              f"{fmt_distance(r['distance']):>14}{fmt_time(r['time']):>10}"
              f"{(r['calories'] if r['calories'] is not None else '-'):>10}"
              f"{(r['rides'] if r['rides'] is not None else '-'):>7}   {editable}")

    unnamed = [r for r in records if not r['name']]
    if unnamed:
        print(f"\n{len(unnamed)} unnamed record(s), not offered for editing.\n"
              f"  Record 0 is the DEVICE's own ledger. Measured on an Edge "
              f"530: it grew\n"
              f"  by exactly the distance, time, calories and ride count of a "
              f"real ride,\n"
              f"  twice, and did not move for any value written into a "
              f"profile record.\n"
              f"  It is shown rather than hidden, and left alone rather than "
              f"edited.\n"
              f"\n"
              f"  You may read that the first record must equal the sum of "
              f"the rest.\n"
              f"  It does not: five consecutive working states measured here "
              f"were never\n"
              f"  equal, once differing by 236 miles. What matters is not "
              f"changing the\n"
              f"  file's STRUCTURE, which this tool never does.")


# ------------------------------------------------------------ unit parsing
#
# A bare number is REFUSED for distance and time. See the version note:
# the stored units are not the units anyone thinks in, and the device
# accumulates on whatever is written, so a silent factor-of-1609 error
# is both expensive and invisible until a season's riding has landed on
# top of it.

_DIST_RE = re.compile(r'^\s*([0-9]+(?:\.[0-9]+)?)\s*(mi|km|m)\s*$', re.I)
_HMS_RE  = re.compile(r'^\s*([0-9]+):([0-5][0-9])(?::([0-5][0-9]))?\s*$')
_SECS_RE = re.compile(r'^\s*([0-9]+)\s*s\s*$', re.I)


def _degroup(text):
    """
    Drop thousands separators before parsing.

    Added after testing against real Garmin Connect output, which
    prints grouped numbers like "1,234.00 mi" and "45,678" -- both of
    which the first version refused. Copy-and-paste from Connect's
    Reports page is the ENTIRE intended workflow for this tool, so
    rejecting Connect's own number format made it useless for the one
    job it exists to do. The explicit-unit requirement is unaffected:
    a bare "1,234" is still refused, only the comma is tolerated.
    """
    return text.replace(',', '') if text else text


def parse_distance(text):
    """-> metres. Requires an explicit mi / km / m suffix."""
    m = _DIST_RE.match(_degroup(text))
    if not m:
        raise argparse.ArgumentTypeError(
            f"distance needs an explicit unit: {text!r}. "
            f"Use e.g. 2240mi, 3604km or 3604920m -- a bare number is "
            f"refused on purpose, because the file stores metres and "
            f"guessing wrong writes an odometer the device then adds to.")
    value, unit = float(m.group(1)), m.group(2).lower()
    metres = {'mi': value * METRES_PER_MILE,
              'km': value * 1000.0,
              'm':  value}[unit]
    return int(round(metres))


def parse_time(text):
    """-> seconds. Requires H:MM, H:MM:SS, or an explicit 's' suffix."""
    text = _degroup(text)
    m = _HMS_RE.match(text)
    if m:
        h, mins, secs = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
        return h * 3600 + mins * 60 + secs
    m = _SECS_RE.match(text)
    if m:
        return int(m.group(1))
    raise argparse.ArgumentTypeError(
        f"time needs H:MM, H:MM:SS or an explicit seconds suffix: {text!r}. "
        f"Use e.g. 189:42 or 683520s -- a bare number is refused on purpose.")


def parse_count(text):
    text = _degroup(text)
    if not re.match(r'^\s*[0-9]+\s*$', text):
        raise argparse.ArgumentTypeError(f"expected a whole number: {text!r}")
    return int(text)


# ----------------------------------------------------------------- writing

def field_byte_range(msg, def_num):
    """Absolute (start, end) file offsets of one field's payload."""
    cursor = msg['start'] + 1              # skip the record header byte
    for (num, size, _base_type, _raw) in msg['fields']:
        if num == def_num:
            return cursor, cursor + size
        cursor += size
    raise KeyError(f"field {def_num} not present in this record")


def pack_for(msg, def_num, value):
    """Pack `value` at whatever width THIS file stores that field in."""
    start, end = field_byte_range(msg, def_num)
    width = end - start
    fmt = {4: '<I', 2: '<H', 1: '<B'}.get(width)
    if fmt is None:
        raise ValueError(f"field {def_num} has unexpected width {width}")
    ceiling = (1 << (width * 8)) - 2       # -1 is the FIT 'invalid' sentinel
    if not (0 <= value <= ceiling):
        sys.exit(f"{WRITABLE.get(def_num, def_num)}: {value} does not fit in "
                 f"this file's {width}-byte field (max {ceiling:,}).")
    return struct.pack(fmt, value)


def assert_distinct_paths(input_path, output_path):
    """
    Refuse to write over the input.

    Called TWICE on purpose: once at the top of main() before anything
    is printed, and again inside patch(). The first is the one users
    meet -- the first version of this checked only inside patch(), so
    typing the same path twice walked you through a full before/after
    preview and a confirmation prompt for a write that was then
    refused. The input survived, but being asked to confirm something
    that cannot happen is its own kind of wrong. The second call stays
    so the guard does not depend on a caller remembering it.
    """
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        sys.exit("Refusing to write over the input file. Give a different "
                 "output path -- the original is your only copy until the "
                 "new one is verified.")


def find_one(records, name):
    """The single named record, or exit explaining why not."""
    hits = [r for r in records if r['name'] == name]
    if not hits:
        names = [r['name'] for r in records if r['name']]
        # Suggest before listing. The two realistic mistakes are a case
        # slip and an unquoted space that truncated the name at the
        # first word -- both are recognisable, so say so rather than
        # making the user eyeball a list.
        near = [n for n in names if n.lower() == name.lower()]
        if not near:
            near = [n for n in names
                    if n.lower().startswith(name.lower() + ' ')]
        hint = ""
        if near:
            hint = f"\nDid you mean {near[0]!r}?"
            if any(' ' in n for n in near):
                hint += (" Names with spaces need quoting: "
                         f"--profile \"{near[0]}\"")
        sys.exit(f"No record named {name!r}.{hint}\n"
                 f"Named records are: {', '.join(repr(n) for n in names)}\n"
                 f"Matching is exact and case-sensitive -- it is the only "
                 f"reliable key, since the sport field is not.")
    if len(hits) > 1:
        sys.exit(f"{len(hits)} records are named {name!r}. Refusing to guess "
                 f"which one you meant.")
    return hits[0]


def resolve_plan(records, names, changes):
    """
    {name: changes} for every requested name, or exit.

    EVERY name is resolved before anything is written. A `reset
    --profile ROAD --profile TYPOE` must fail having touched nothing,
    not having zeroed ROAD and then discovered the second name is
    wrong. Order of operations is the safety property here.
    """
    seen, plan = [], {}
    for name in names:
        if name in plan:
            sys.exit(f"--profile {name!r} given more than once.")
        find_one(records, name)          # exits with a useful message
        plan[name] = dict(changes)
        seen.append(name)
    return plan


def patch(input_path, output_path, plan):
    """
    Write each name's changes into that record only. -> (before, after).

    Never writes in place; never creates a record; never touches any
    field outside WRITABLE.
    """
    assert_distinct_paths(input_path, output_path)   # belt and braces
    records = read_records(input_path)
    assert_totals_file(input_path, records)

    data = bytearray(open(input_path, 'rb').read())
    for name, changes in plan.items():
        target = find_one(records, name)
        for def_num, value in sorted(changes.items()):
            start, end = field_byte_range(target['raw'], def_num)
            data[start:end] = pack_for(target['raw'], def_num, value)

    # Recompute the trailing CRC over everything but itself, exactly as
    # fit_patch does -- a correct body behind a stale CRC is a file the
    # device rejects silently.
    data[-2:] = struct.pack('<H', fit_crc(bytes(data[:-2])))

    with open(output_path, 'wb') as f:
        f.write(bytes(data))

    return records, read_records(output_path)


def verify(before, after, plan):
    """
    Confirm the named records changed as asked AND nothing else moved.

    This is the whole safety argument of the tool, and it matters more
    with several names than with one: a real odometer typically sits in
    the same file as the profiles being reset, so "only the records I
    named" has to be demonstrated rather than assumed.
    """
    problems = []
    b_by = {r['index']: r for r in before}
    a_by = {r['index']: r for r in after}

    if set(b_by) != set(a_by):
        problems.append("the set of records changed -- records were added "
                        "or removed, which this tool must never do")

    for idx in sorted(set(b_by) & set(a_by)):
        b, a = b_by[idx], a_by[idx]
        for key in ('name', 'sport'):
            if b[key] != a[key]:
                problems.append(f"record {idx}: {key} changed "
                                f"{b[key]!r} -> {a[key]!r}; identity is not "
                                f"ours to edit")
        changes = plan.get(b['name'], {})
        for def_num, label in WRITABLE.items():
            want = changes.get(def_num)
            if want is not None:
                if a[label] != want:
                    problems.append(f"{b['name']}: {label} is {a[label]}, "
                                    f"expected {want}")
            elif b[label] != a[label]:
                problems.append(f"record {idx} ({b['name'] or 'unnamed'}): "
                                f"{label} changed {b[label]} -> {a[label]} "
                                f"but was not asked to")
    return problems


def describe(before_rec, after_rec, changes):
    print(f"\n  {before_rec['name']}")
    for def_num, label in sorted(WRITABLE.items(), key=lambda kv: kv[1]):
        if def_num not in changes:
            continue
        b, a = before_rec[label], after_rec[label]
        if label == 'distance':
            b, a = fmt_distance(b), fmt_distance(a)
        elif label == 'time':
            b, a = fmt_time(b), fmt_time(a)
        print(f"    {label:<10} {str(b):>14}  ->  {a}")


DEPLOY_NOTE = """
Not yet on the device. To apply it:

  1. Copy the new file into the Edge's Garmin/NewFiles/ folder, named
     Totals.fit.
  2. Disconnect and restart the Edge. It imports on boot.

NewFiles is the only route that works -- copying into Garmin/Totals/ or
anywhere else does not import it.

The device ADDS TO what you just wrote, so these are starting totals,
not a cap. A reset leaves it counting from zero.
"""


# --------------------------------------------------------------------- CLI

class _Parser(argparse.ArgumentParser):
    """
    argparse with one extra hint.

    Found by Doug using it: half his profiles have a space in the name
    ("ROAD A1"), and an unquoted `--profile ROAD A1` fails inside
    argparse as "unrecognized arguments: A1" -- true, and useless. The
    tool's own code never runs, so the hint cannot live in find_one().
    """

    def error(self, message):
        if 'unrecognized arguments' in message:
            message += ("\n\nIf a profile name contains a space, quote it: "
                        "--profile \"ROAD A1\"\n(or escape it: "
                        "--profile ROAD\\ A1). Run `list` to see exact names.")
        super().error(message)


def main(argv=None):
    p = _Parser(
        description="Read and edit a Garmin Edge Totals.fit odometer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Units are explicit by requirement: --distance 2240mi, "
               "--time 189:42. A bare number is refused.\n"
               "Quote any profile name containing a space: "
               "--profile \"ROAD A1\"")
    sub = p.add_subparsers(dest='cmd', required=True)

    q = sub.add_parser('list', help="show every record, change nothing")
    q.add_argument('input_file')

    r = sub.add_parser('reset', help="zero one or more profiles' totals")
    r.add_argument('input_file')
    r.add_argument('output_file')
    # Repeatable: a new-year reset is the common case and typically
    # covers every profile at once. `set` is deliberately NOT
    # repeatable -- one set of values cannot be right for two
    # different profiles, so repeating it could only mean a mistake.
    r.add_argument('--profile', required=True, action='append',
                   metavar='NAME',
                   help='exact profile name, quoted if it has a space; '
                        'repeat for several')
    r.add_argument('--yes', action='store_true', help="skip the confirmation")

    s = sub.add_parser('set', help="set one profile's totals")
    s.add_argument('input_file')
    s.add_argument('output_file')
    # action='append' here NOT to allow several, but so that giving
    # several can be REFUSED. Plain argparse would silently keep the
    # last one, and quietly writing your values to a profile you did
    # not name is the worst failure this tool could have.
    s.add_argument('--profile', required=True, action='append',
                   metavar='NAME',
                   help='exact profile name, quoted if it has a space')
    s.add_argument('--distance', type=parse_distance,
                   help="with unit: 2240mi, 3604km, 3604920m")
    s.add_argument('--time', type=parse_time,
                   help="H:MM, H:MM:SS, or 683520s")
    s.add_argument('--calories', type=parse_count, help="kcal, whole number")
    s.add_argument('--rides', type=parse_count, help="ride count")
    s.add_argument('--yes', action='store_true', help="skip the confirmation")

    args = p.parse_args(argv)

    if args.cmd == 'list':
        recs = read_records(args.input_file)
        assert_totals_file(args.input_file, recs)
        print_table(recs, args.input_file)
        return 0

    # Before ANY output: refusing after a preview and a confirmation
    # prompt is worse than refusing immediately.
    assert_distinct_paths(args.input_file, args.output_file)

    if args.cmd == 'reset':
        changes = {F_TIMER: 0, F_DIST: 0, F_CAL: 0, F_SESSIONS: 0}
    else:
        changes = {}
        for flag, def_num in (('distance', F_DIST), ('time', F_TIMER),
                              ('calories', F_CAL), ('rides', F_SESSIONS)):
            value = getattr(args, flag)
            if value is not None:
                changes[def_num] = value
        if not changes:
            sys.exit("Nothing to set. Give at least one of --distance, "
                     "--time, --calories, --rides -- or use `reset` to zero "
                     "all four.")

    # Show the before/after and confirm BEFORE writing anything.
    current = read_records(args.input_file)
    assert_totals_file(args.input_file, current)

    names = args.profile if isinstance(args.profile, list) else [args.profile]
    if args.cmd == 'set' and len(names) > 1:
        sys.exit(f"`set` takes one --profile, got {len(names)}: "
                 f"{', '.join(repr(n) for n in names)}.\n"
                 f"One set of values cannot be right for two profiles. "
                 f"Run it once per profile, or use `reset` which does "
                 f"accept several.")
    plan = resolve_plan(current, names, changes)   # every name, or exit

    for name in names:
        target = find_one(current, name)
        print(f"{name}:")
        for def_num, label in sorted(WRITABLE.items(), key=lambda kv: kv[1]):
            if def_num not in changes:
                print(f"    {label:<10} {'unchanged':>14}")
                continue
            b, a = target[label], changes[def_num]
            if label == 'distance':
                b, a = fmt_distance(b), fmt_distance(a)
            elif label == 'time':
                b, a = fmt_time(b), fmt_time(a)
            print(f"    {label:<10} {str(b):>14}  ->  {a}")

    untouched = [r['name'] or f"#{r['index']}"
                 for r in current if r['name'] not in plan]
    print(f"\nUntouched: {', '.join(untouched)}")

    if not args.yes:
        if input("\nWrite this? [y/N] ").strip().lower() not in ('y', 'yes'):
            print("Nothing written.")
            return 1

    before, after = patch(args.input_file, args.output_file, plan)
    problems = verify(before, after, plan)
    if problems:
        print("\nVERIFICATION FAILED -- the output file is suspect:",
              file=sys.stderr)
        for line in problems:
            print(f"  * {line}", file=sys.stderr)
        print(f"\n{args.output_file} was written but should not be used.",
              file=sys.stderr)
        return 2

    print(f"\nWritten to {args.output_file}")
    for name in names:
        describe(find_one(before, name), find_one(after, name), changes)
    others = len(after) - len(names)
    print(f"\n  Verified: {others} other record(s) byte-identical, "
          f"no names or sports touched, CRC recomputed.")
    print(DEPLOY_NOTE)
    return 0


if __name__ == '__main__':
    sys.exit(main())
