# v1.7.4 — The app starts on Windows again

*Released 2026-10-27.*

**If you use Windows, every release since v1.5.0 has been broken for
you.** The GUI exited before drawing a window. This release fixes it.

Also here: offline work finally has a way out of the app, and a small
annoyance in the clone dialog.

## The Windows crash

`gui_app.py` would not launch. It exited with:

```
NotImplementedError
OnInit returned false, exiting...
```

A single line in the boot-message editor called a macOS-only wxWidgets
method. It was guarded — by a check for whether the method *exists*,
under a comment confidently stating it exists only on macOS builds.
That is wrong: wxPython provides the method on every platform, and the
non-macOS version raises as soon as you call it. The guard passed, the
call failed.

It took down the whole app rather than one feature because every panel
is built at startup, so the boot-message editor's constructor runs
whether or not you ever open it.

**Seven releases shipped this.** Not because it was subtle — one launch
catches it — but because Windows stopped being tested in August and the
offending line arrived in late September. The CLI tools were never
affected; `detect`, `screens` and the rest worked throughout.

Confirmed fixed on the Windows 10 machine that reported it.

## Offline work can leave the app

Clone a profile with no device connected and you reached a page offering
only **"Write to Device (NewFiles)"** — which refused when pressed.
There was no export anywhere on that path, so a finished clone was
stranded.

That page is now mode-aware. Without a device it becomes **Export**,
with the same save dialog and the same double verification the rest of
the offline flow uses: the file's own checksum, and a byte-for-byte
read-back of the copy. The eject-and-reconnect controls, which mean
nothing offline, are hidden rather than greyed.

Restoring from a backup used the same page and had the same dead end.
Both are fixed by the one change.

## The clone dialog's filename field

Typing a display name auto-fills a suggested filename, and typing
directly into the filename field stops that — so your choice is not
overwritten. But *clearing* the filename field used to leave the
auto-fill switched off for the rest of the visit, with no way back
except leaving the page and returning.

An empty field has nothing to protect, so clearing it now resumes the
suggestion.

## Worth knowing: the Edge renames what you import

Not a change in this release, but newly established and useful.

Deploy a new profile under any filename and the device **renames it**,
building the name from the profile's own sport and display name —
`ROAD22.fit` became `CyclingRoadROAD_22.fit`. So the `Cycling…` naming
convention is the Edge's output, not a rule you have to follow.

Two consequences, both already known about and neither fixed here:

- after deploying a *clone* in device mode, the post-write check looks
  for the name you chose and reports it could not verify. The profile is
  on the device and correct; only the confirmation message is wrong.
- a screen's internal slot number is not stable across an import. The
  toolkit never relies on this across sessions, but anything you script
  against slot numbers might.

## Upgrading

No file format change, no migration. Profiles and backups from v1.7.3
work unchanged. `gui_app.py` is the only file with behaviour changes.

`fit_dump.py` 2.28.0 · `gui_app.py` 0.30.1 · `fit_patch.py` 1.20.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0

---

## Known gaps, named rather than hidden

- **Windows is not in the per-release test loop.** This release fixes
  the crash; it does not fix the reason it went unnoticed for a month.
  Treat Windows as tested at the dates stated in the README, not as
  continuously verified.
- **A harmless `unsupported locale setting` message** appears at launch
  on Windows. A known wxWidgets behaviour, nothing to do with this
  toolkit, present before and after the fix.
- **The export dialog's filename warning overstates its case.** It says
  a differently-named file will be ignored. Testing shows the device
  accepts it and renames it. Matching the original name is still the
  right advice — it appears to be what stops the device rewriting your
  file — but the warning's wording needs correcting.
- **Post-deploy verification after a clone** reports failure when the
  write succeeded; see above.
- **Id 331 is unnamed** — a real data field with no label that stays at
  `0:00` through an entire ride.
- **Four fields exist on the 840 and not the 530**, and the picker
  offers every field to both models.
- **A cloned profile reads a zero odometer.** Expected; the clone has a
  real but empty totals record.
