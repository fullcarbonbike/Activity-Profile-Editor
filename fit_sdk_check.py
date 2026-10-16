#!/usr/bin/env python3
"""
fit_sdk_check.py -- does this garmin-fit-sdk still mis-render the
undocumented 32-byte profile-name field in a `Totals.fit` record?

Read-only. Opens nothing for writing, touches no device.

WHY THIS EXISTS
---------------
PROJECT_NOTES.md carries a standing rule: for UNDOCUMENTED FIT messages,
trust `fit_raw_walk.parse_fit()` and not the garmin-fit-sdk decoder,
because the SDK mis-rendered `Totals.fit` and produced a confident wrong
conclusion (Doc rev 116).

That rule is VERSION-SPECIFIC and was recorded for years without naming a
version. `install.sh` does not pin the SDK, so every user is on whatever
pip gave them that day. Two ways the rule can rot:

  * a later SDK FIXES the rendering, and the rule becomes an unnecessary
    restriction stated as fact
  * a later SDK changes decoding some other way, and the rule does not
    cover it

This script turns "we assume it still does that" into something you can
check in about two seconds against any SDK version.

IT IS WRITTEN TO PASS WHEN THE SDK IS CORRECT. Exit status 0 means the
decoder rendered the name faithfully and the standing rule can be
narrowed to the versions that need it; exit status 1 means the
workaround is still required. A fix should announce itself rather than
go unnoticed for another year.

WHAT IS ACTUALLY WRONG
----------------------
A totals record (global message 33) carries the profile name in def_num
10 as 32 bytes. On the device those bytes are the name, a NUL, and then
uninitialised junk rather than zero padding. The SDK splits the field on
every NUL run and hands back a LIST of fragments:

    ['ROAD', '', '', '', '', '\\x12c', 'c:', '', '', 'Fb', ...]

The real name survives as element 0, which is exactly why the wrong
conclusion looked plausible. `fit_raw_walk` returns the 32 raw bytes and
the name is everything up to the first NUL.

USAGE
-----
    python3 fit_sdk_check.py /path/to/Totals.fit

Run it with the interpreter you actually use. An activated venv and a
bare `python3` can resolve to different installs, which is its own trap:
the script prints the interpreter and the SDK's file path, not just the
version number, because a version number alone is what misled this
project once already.

To test a DIFFERENT SDK version, make a throwaway folder, copy this file
and `fit_raw_walk.py` into it (those two and nothing else), create a venv
there and install the version you want to try. `fit_raw_walk.py` is the
reference this compares against and imports only `struct` and `sys`.
"""

import os
import sys

__version__ = "1.0.0"

TOTALS_MESG_NUM = 33
NAME_FIELD_NUM = 10


def _raw_names(path):
    """
    The reference answer: profile names straight from the bytes.

    Returns a list of (message_index_or_None, name) in file order. The
    name is everything before the first NUL, which is the rule the
    device's own layout implies and the one Doc rev 116 established.
    """
    try:
        import fit_raw_walk
    except ImportError:
        # Exit 2, not 1. The exit codes mean something to anything that
        # scripts this: 0 faithful, 1 MANGLED, 2 could not run. A missing
        # reference file is the third kind, and reporting it as the second
        # would have a caller record a verdict no test actually reached.
        print("fit_raw_walk.py is not importable from here.\n\n"
              "It is the reference this script compares the SDK against,\n"
              "so it has to sit beside this file (or on PYTHONPATH). Copy\n"
              "it from the toolkit folder -- it is self-contained and\n"
              "imports only struct and sys.")
        sys.exit(2)
    records = fit_raw_walk.parse_fit(path)[0]
    out = []
    for rec in records:
        if rec.get("mesg_num") != TOTALS_MESG_NUM or rec.get("kind") != "data":
            continue
        name = None
        for num, _size, _typ, val in rec["fields"]:
            if num == NAME_FIELD_NUM:
                name = val.split(b"\x00")[0].decode("ascii", "replace")
                break
        out.append(name)
    return out


def _sdk_names(path):
    """
    What the SDK makes of the same field, untouched.

    Deliberately does NOT reach for a 'profile_name' key or tidy the
    value up: the question is what the decoder hands a caller who asks
    for field 10, so whatever it returns is what gets compared.
    """
    from garmin_fit_sdk import Decoder, Stream
    stream = Stream.from_file(path)
    messages, _errors = Decoder(stream).read()
    out = []
    for rec in messages.get("totals_mesgs") or []:
        out.append(rec.get(NAME_FIELD_NUM, rec.get("profile_name")))
    return out


def main(argv):
    if len(argv) != 2:
        print("usage: python3 fit_sdk_check.py /path/to/Totals.fit")
        print()
        print("Checks whether this garmin-fit-sdk mis-renders the 32-byte")
        print("profile-name field in a Totals.fit record, against")
        print("fit_raw_walk.parse_fit() as the reference.")
        print()
        print("Exit: 0 faithful, 1 mangled (workaround still needed),")
        print("      2 could not run.")
        print()
        print("Run it with the interpreter you actually use -- an active")
        print("venv and a bare python3 can resolve to different installs.")
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        print(f"No such file: {path}")
        return 2

    import garmin_fit_sdk

    print("Environment")
    print(f"  interpreter : {sys.executable}")
    print(f"  SDK version : {garmin_fit_sdk.__version__}")
    print(f"  SDK loaded  : {garmin_fit_sdk.__file__}")
    print(f"  file        : {path}")
    print()

    raw = _raw_names(path)
    sdk = _sdk_names(path)

    if not raw:
        print("No totals records (global message 33) in that file.")
        print("Point this at a Totals.fit, not an Activity Profile.")
        return 2
    if len(raw) != len(sdk):
        print(f"Record count disagrees: raw sees {len(raw)}, SDK sees "
              f"{len(sdk)}. That is a finding in itself -- report it.")
        return 1

    # Only NAMED records are diagnostic. An unused slot has a blank name
    # either way, so it cannot distinguish a good decoder from a bad one.
    named = [(i, r, s) for i, (r, s) in enumerate(zip(raw, sdk)) if r]
    print(f"{len(raw)} totals records, {len(named)} of them named\n")

    bad = []
    for i, r, s in named:
        ok = isinstance(s, str) and s == r
        print(f"  record {i}: raw={r!r}")
        print(f"            sdk={s!r}  ({type(s).__name__})")
        print(f"            -> {'faithful' if ok else 'MANGLED'}")
        if not ok:
            bad.append(i)

    print()
    if not named:
        print("INCONCLUSIVE: no named records, so nothing to compare.")
        print("Use a Totals.fit from a device with at least one named "
              "profile.")
        return 2
    if bad:
        print(f"RESULT: the SDK MANGLES the name field "
              f"({len(bad)} of {len(named)} named records).")
        print("The standing rule stands for this version -- keep using")
        print("fit_raw_walk.parse_fit() for undocumented messages.")
        return 1
    print("RESULT: the SDK renders the name field FAITHFULLY.")
    print("This version does not need the workaround. Worth narrowing the")
    print("standing rule in PROJECT_NOTES.md to the versions that do,")
    print("rather than leaving it stated absolutely.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
