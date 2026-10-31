# v1.7.8 — Odometer confirmed on both models and on Windows, plus quoting that explains itself

*Released 2026-10-31.*

A small release. `fit_odometer.py` shipped yesterday with two gaps
named in its own release notes — the Edge 840 and Windows were both
untested. Both are now closed, and using the tool in anger turned up
one real usability problem worth fixing.

## Confirmed on the Edge 840

v1.7.7 said plainly that no odometer write had been confirmed on an
840. One has now: a profile's odometer was set with this tool, the
file copied over MTP, the device restarted, and **the new value read
back off the Odometer data field on the device itself.**

That last step is why this is recorded as a confirmed *import* rather
than a confirmed *transfer*. A copy completing and a device importing
look identical from the computer; only the device's own display
separates them.

**Scope, stated rather than implied:** distance only (the 840 has no
display for time, calories or rides either), one profile, and no file
pulled back afterwards. The 530 remains the model with the full A–D
characterisation.

### It was predicted before it was tested

Before the hardware run, the tool was pointed at an 840 `Totals.fit`
the device had accepted back in October, and asked to reproduce it
from the original. The result was **792 of 795 bytes identical** —
differing only in one `sport` byte the tool refuses to write by
design, and the two CRC bytes, which must differ because the content
does.

There was no structural difference left for an import to reject,
which is why the hardware run was unremarkable rather than lucky.

## Confirmed on Windows 10

`list` and `set` both verified on the Windows 10 laptop. No quoting,
encoding or path surprises.

Worth noting because this is the platform with a precedent: #166
shipped a Windows-fatal GUI crash for seven releases because Windows
had quietly left the test loop. This time the three known hazards
were checked in advance — binary file modes, zero non-ASCII in any
printed string, no optional imports — *and* the tool was actually run
on the machine, which is the part that was missing in August.

## Profile names with spaces now explain themselves

Half of a real Edge's profiles can have a space in the name. Pass one
unquoted and argparse fails with:

```
error: unrecognized arguments: A1
```

True, and useless. That message comes from argparse before any of
this tool's code runs, so the fix had to go in the parser itself:

```
error: unrecognized arguments: A1

If a profile name contains a space, quote it: --profile "ROAD A1"
(or escape it: --profile ROAD\ A1). Run `list` to see exact names.
```

Separately, a name that *is* parsed but doesn't match now suggests
the near miss rather than making you read a list:

```
No record named 'road a1'.
Did you mean 'ROAD A1'? Names with spaces need quoting: --profile "ROAD A1"
```

That covers the two realistic mistakes: a case slip, and a name
truncated at its first word.

**The docs are the reason this survived testing.** Every example in
the README, the `--help` text and the module docstring used a
single-word name. All three now show a spaced one.

## A missing file no longer produces a stack trace

Mistyping an input path raised `FileNotFoundError` with a full
traceback. It now says what is wrong:

```
No such file: /tmp/nope.fit
```

A traceback is a reasonable answer to a programming error and a poor
one to a typo. A file that exists but isn't a FIT file is likewise
reported rather than raised.

## Upgrading

No file format change. `fit_odometer.py` is the only file that
changed, and no write path was touched — the guards, the verification
and the output are identical to 1.0.0.

`fit_odometer.py` 1.0.1 · `fit_dump.py` 2.30.0 · `gui_app.py` 0.33.0 ·
`fit_patch.py` 1.20.0 · `garmin_device.py` 0.13.1 ·
`fit_clone_profile.py` 1.0.2 · `fit_profile_diff.py` 1.0.0 ·
`fit_census.py` 1.1.0 · `fit_sdk_check.py` 1.0.0 · `install.sh` 1.0.4

---

## Testing

Ten guard cases re-run after the change, all passing, no stray output
files. Plus section F of `TEST_PLAN_106_odometer.md`, added after the
fact to record the 840 and Windows runs the plan had deliberately
excluded.

## Known gaps, named rather than hidden

- **A multi-record write on the 840** has not been done. The 530
  proved it; nothing suggests the models differ.
- **Record 0 on the 840** is uncharacterised. The file corpus hints
  it behaves as it does on the 530 — that unit's record 0 holds
  roughly what it has genuinely ridden — but no ride-and-measure
  cycle has been run there.
- **Time, calories and rides have no display on either model.** They
  are stored, writable and survive an import; nothing shows them.
- **There is still no Restore-from-Backup for `Totals.fit`.** The
  tool never writes in place, so your input is always intact, but
  back up the device's copy by hand before a first write.
