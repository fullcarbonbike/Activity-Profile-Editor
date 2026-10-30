# v1.7.5 — The toolkit stops trusting handles the device rewrites

*Released 2026-10-28.*

**The Edge changes things during import.** It renames the file you
sent, and it sometimes renumbers a profile's internal screen slots.
This toolkit remembered both and kept using its own copies, which
produced a verification that reported failure on a write that had
succeeded — and, underneath that, a comparison that would have
reported changes nobody made.

Also here: a warning this project has been giving for months, deleted,
because it was never true.

## Post-deploy verification works after a clone

Clone a profile, deploy it, restart, reconnect, press **Check**, and
the toolkit reported that it *could not verify* the write. The profile
was on the device and correct. Only the confirmation was wrong.

The Edge renames an imported profile, generating the filename from the
profile's own sport and display name — `zztest.fit` arrives as
`CyclingRoadROAD_A2.fit`. The check looked for the name you deployed
under, found nothing, and gave up.

It now finds the live profile by reading the device's `Sports` folder
and matching on the **display name inside the file**, which is what
the device preserves. Predicting the generated name was rejected as
the alternative: it would bake in a convention observed rather than
documented, and break silently if Garmin changed it.

Confirmed on the Edge 530, by deploying under a deliberately wrong
filename.

## Screens are now matched by identity, not by slot number

A profile's screens each carry a slot number (`message_index`).
Everything this toolkit does preserves them exactly. **A device import
does not** — on a new profile the Edge can move a screen to a
different slot, content untouched.

The change-comparison paired screens by that slot number. On a
renumbered profile it would pair unrelated screens and describe
differences that never happened.

It now pairs on the screen's stable type identity. On a real
renumbered profile the old pairing reports **11 differences on a
byte-identical file**; the new one reports none.

**These two had been hiding each other.** The only deploys that got
renumbered were the ones where verification couldn't find the file at
all — so fixing the rename alone would have exposed a comparison
confidently describing changes that did not exist. That is worse than
"couldn't verify", which is why both shipped together.

## The clone dialog suggests the name the device will use

Type a display name and the suggested filename now matches what the
Edge generates: the sport prefix from the profile you cloned, spaces
converted to underscores. `ROAD A1` cloned from a Road profile
suggests `CyclingRoadROAD_A1.fit`.

The field stays editable. The name genuinely does not matter — see
below — but a suggestion that matches what you'll see on the device
afterwards is less confusing than one that doesn't.

## ⚠ Correction: the filename never mattered

Every previous version warned that the Edge matches profiles by
filename and silently ignores anything that doesn't match. **That is
false, and this release removes it from all eight places it appeared.**

What actually happens: the device accepts any filename, imports the
file, and renames it. Tested across five imports on both models. One
profile deployed under a deliberately wrong name came back
**byte-for-byte identical**, same checksum, under the device's own
generated name.

So the export dialog no longer interrupts you for renaming a file, and
the success message no longer tells you to keep the name.

**What does matter, and is now said instead:** `Garmin/NewFiles/` is
the only route that works. Copying a profile straight into
`Garmin/Sports/` does not import it. This has been known since the
project's first week and had never once been shown to a user.

## Upgrading

No file format change, no migration. Profiles, backups and favourites
from v1.7.4 work unchanged.

`fit_dump.py` 2.29.0 · `gui_app.py` 0.32.2 · `fit_patch.py` 1.20.0 ·
`garmin_device.py` 0.13.1 · `fit_clone_profile.py` 1.0.2 ·
`fit_census.py` 1.1.0 · `fit_sdk_check.py` 1.0.0

---

## Testing

Sections A–E of `TEST_PLAN_162_168_169.md` plus
`TEST_PLAN_170_filename_note.md`, all on an Edge 530 in device mode.
The Edge 840 cannot enter device mode at all — it is MTP-only and
never mounts — so none of this is testable there, and that limitation
is unchanged.

Two of the eight copies of the removed filename claim were found not
by searching but by Doug running the export and reading the dialog.
They were the only two a user would ever have seen.

## Known gaps, named rather than hidden

- **Windows is tested at the dates stated in the README, not
  continuously.** v1.7.4 fixed a launch crash that shipped for seven
  releases; the gap that let it through is not fixed.
- **Four fields exist on the 840 and not the 530**, and the picker
  offers every field to both models.
- **Id 331 is unnamed** — a real data field with no label that stays
  at `0:00` through an entire ride.
- **A cloned profile reads a zero odometer.** Expected; the clone has
  a real but empty totals record.
- **Why the device renumbers is now known** — the profile being new,
  not the filename — but nothing depends on that, by design. The fix
  holds either way.
