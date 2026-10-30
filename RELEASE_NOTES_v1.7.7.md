# v1.7.7 — The odometer, and what the first record in `Totals.fit` actually is

*Released 2026-10-30.*

**New tool: `fit_odometer.py`.** Read, reset or set a profile's
lifetime totals — distance, moving time, calories and ride count. A
reset of every profile each January is one command.

Along the way this release settles what the unnamed first record in
`Totals.fit` is for, and disproves the advice most people find when
they search for how to edit this file.

---

## `fit_odometer.py`

```bash
python3 fit_odometer.py list   Totals.fit
python3 fit_odometer.py reset  Totals.fit new.fit --profile ROAD
python3 fit_odometer.py set    Totals.fit new.fit --profile ROAD \
                               --distance 1234mi --time 100:30 \
                               --calories 45000 --rides 77
```

`reset` takes `--profile` repeatedly. `set` deliberately does not —
one set of values cannot be right for two profiles, so passing two is
refused rather than silently applied to the last one named.

**Units are explicit by requirement.** `1234mi`, `1985km`, `100:30`,
`683520s`. A bare number is rejected, because the file stores metres
and seconds, nobody thinks in those, and **the device accumulates on
whatever you write** — a silent factor-of-1609 error would be both
expensive and invisible until a season of riding had landed on top of
it. Thousands separators are accepted, since Garmin Connect prints
them.

**What it will not do.** It never writes in place. It never creates or
deletes a record. It never touches a profile's name, sport or message
index — record identity is the device's. And after every write it
re-reads the result and confirms that *only* the records you named
changed, reporting how many were left byte-identical.

**What the odometer should read is your decision.** Leave it, reset
it, or set it from any report you trust. There is no correct value to
restore and the tool does not imply one.

### A CLI rather than a GUI panel, deliberately

The original scope was a GUI feature. The command-line shape is
better in three ways that only became clear once it was written:

- **It works on the Edge 840.** The GUI write path is device-mode
  only, and the 840 is MTP — it never mounts, so it has no device
  mode. A tool that takes a file path serves both models identically.
- **It removed a prerequisite bug.** The scoped version had to back
  `Totals.fit` into the shared backup folder, where *Restore a Deleted
  Profile* would have offered it as a restorable profile, because that
  picker matches on "filename ends in `.fit`". A tool that reads one
  path and writes another never touches that store.
- **It is verifiable.** 13 guard cases and a four-profile reset,
  checked headlessly before any hardware was involved.

## What the first record in `Totals.fit` is

Every `Totals.fit` holds 11 records. The first is unnamed and carries
the largest numbers, and until now nobody here knew what it was.

**It is the device's own ledger.** Measured across five events on an
Edge 530:

| | the first record |
|---|---|
| a real ride | **moved by exactly that ride** — distance, time, calories, +1, field for field |
| a distance written into a profile | no change |
| four fields written into another profile | no change |
| four profiles reset to zero in one import | no change |
| a second real ride, 68 m | **+68 m, exact** |

Riding moves it. Nothing this toolkit writes ever does. The second
ride is the cleaner proof — a 68-metre delta appearing identically in
two records cannot be rounding.

`fit_odometer.py` shows it and refuses to edit it.

## ⚠ A widely-repeated forum rule is wrong

Search for how to edit `Totals.fit` and you will find this, given as
an accepted answer:

> *"The first row has to equal the total of all profiles in the rest
> of the rows."*

**It does not.** Five consecutive working device states from this
release's testing were checked: the first record and the sum of the
others were **never equal**, the sign of the difference flipped
between pulls, and in one state the sum exceeded the first record by
236 miles — after which the device accepted that file, imported the
next one cleanly, and carried on accumulating correctly.

The likely real cause in that thread is in the asker's own follow-up:
his FIT → CSV → FIT round-trip produced a file whose fields were *"in
other orders"* with *"some hex mess"* in cells. The file that worked
for him came from a different tool. His responder's **other**
instruction is the one that mattered: *do not change the file
structure.*

This is a direct argument for editing these files at the byte level.
`fit_odometer.py` overwrites values in place and never alters field
order, widths, record count or message definitions, so it cannot
produce the file that failed for him. An SDK round-trip rebuilds the
file and can.

## Upgrading

No file format change, no migration. Nothing else in the toolkit
changed — `fit_odometer.py` is additive.

`fit_dump.py` 2.30.0 · `gui_app.py` 0.33.0 · `fit_patch.py` 1.20.0 ·
`garmin_device.py` 0.13.1 · `fit_clone_profile.py` 1.0.2 ·
`fit_odometer.py` 1.0.0 · `fit_profile_diff.py` 1.0.0 ·
`fit_census.py` 1.1.0 · `fit_sdk_check.py` 1.0.0 · `install.sh` 1.0.4

---

## Testing

`TEST_PLAN_106_odometer.md`, sections A–D, all passing on an Edge 530:
a single-field write, all four fields, four profiles reset in one
import, and a ride afterwards to confirm the device resumes counting
from a written value rather than restoring its own.

**Only one of the four fields has an on-device display.** The
Odometer data field shows distance; time, calories and ride count have
no display found anywhere in the menus. Every step in the plan states
whether it was verified on screen or by pulling the file back, because
"the odometer reads 100" confirms a quarter of a write.

## Known gaps, named rather than hidden

- **The 840 is untested for this.** Same file format, and the tool is
  model-agnostic by construction, but no odometer write has been
  confirmed on one.
- **Why the device keeps time, calories and rides per profile is
  unknown.** They are stored, they are writable, they survive an
  import — and nothing on the device appears to show them.
- **What reads the first record is unknown.** No on-device screen
  showing a lifetime total has been found.
- **There is no Restore-from-Backup for `Totals.fit`.** It is the one
  write path in the toolkit without one. The tool never writes in
  place, so your input file is always intact — but back up the
  device's copy by hand before the first write.
