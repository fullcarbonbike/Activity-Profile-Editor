# v1.7.2 — One layout picker, for every screen

*Released 2026-10-21.*

Pick a layout for an ordinary screen the way you already can for
Garmin's own: **one list, every layout the device offers, count and
variant together**.

## What changed

An ordinary screen used to give you a "Layout: A / B / C" dropdown that
changed the *variant* and nothing else. To change how many fields the
screen had, you used Add Field and Remove Field — one field per click,
nine clicks to get from 1 to 10, and nothing anywhere showing which
layouts your device actually has.

Garmin's named screens — eBike Metrics, Segment, Lap Summary and the
rest — have had the whole list since v1.4.0:

| | before | now |
|---|---|---|
| named screen | whole-layout picker | unchanged |
| ordinary screen | variant only, count one at a time | **whole-layout picker** |

On an **840** that is 24 layouts, on a **530** 15. The same list the
device's own layout control steps through.

**Add Field and Remove Field stay** on an ordinary screen. They are off
for a named type, and that difference is deliberate: a named type's
count arrives with the layout and is not yours to choose, while on an
ordinary screen it is — and Add Field also picks *which* field arrives,
which jumping to a layout cannot. The picker is a second route to the
count, not a replacement for the first.

## This needed no new machinery, which is the interesting part

Everything the picker needs had been in place for releases:

- the list of layouts a model offers already covered ordinary screens —
  24 and 15, each one consistent with the variant table, checked rather
  than assumed
- the menu-style label already handled them
- the handler that applies a chosen layout was never specific to named
  screens; only its name was

So the change is two code paths collapsing into one, plus deleting the
two methods that drove the old dropdown. Deleted rather than left
dormant: two pieces of code writing the same byte is how this project's
layout tables drifted apart unnoticed once before.

## Why the testing for this was mostly about v1.7.1

v1.7.1 stopped the toolkit erasing the fields past a layout's count.
The old dropdown never needed that fix — **it could not change the
count, so it could not lose a field**. It was safe by inability rather
than by design, and this release removes the inability.

That made one section of the bench run mandatory rather than optional:
take a 10-field screen, shrink it, grow it, cycle it, edit a field in
the middle and grow it again, on both models, and confirm every
original field comes back. It does, in all seven cases, with no "Timer"
anywhere.

## Fixed: the diagram stopped calling itself a lie

The note under the layout diagram ended **"(not shown to scale here)"**.

That was true when it was written and has been false since v1.7.0,
which taught the diagram to draw each row at its real height. For three
releases the one line of text beside the picture has been telling you
to disbelieve a picture that had become correct.

The parenthetical now appears only where it is still true — when the
model is unknown, or the state's heights were never measured, both of
which still draw uniform rows.

Found by writing a test step that asserted the note would be there, and
then reading what it said.

## Upgrading

No file format change, no migration. Backups and profiles from v1.7.1
work unchanged. `gui_app.py` is the only file that changed.

`fit_dump.py` 2.26.0 · `gui_app.py` 0.29.2 · `fit_patch.py` 1.19.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0

---

## Known gaps, named rather than hidden

- **Remove Field leaves a repeat.** Removing from the middle shifts the
  others up, so the last position keeps a duplicate beyond the count.
  Nothing displays it; it reappears only if you later grow the screen.
- **Named screens have no measured row heights**, so their diagrams
  still draw uniform rows — all twenty types.
- **Two user-screen slot sizes are unmeasured for graphical fields** —
  the quarter-screen and half-screen full-width rows. Both are taller
  than a regular row, so they are treated as safe; if that is wrong the
  cost is a missing warning rather than a false one.
- **48 of the 840's named layout states have no measured grid** and
  draw an honest blank with the field count rather than a guessed
  shape: Virtual Partner, Reserved, GroupTrack List and two unnamed
  types at their C variants and at 8/B, 8/C, 9/B, 9/C, plus Radar at
  three states. The 530 has none — all 190 of its named states are
  measured.
- **Radar's three layouts cannot be drawn.** Measured, documented, not
  expressible as rows.
- **Content composition is unmodelled.** Segment's A/B/C select which
  graphics appear, not the field arrangement.
- **No per-model field availability.** The picker offers every known
  field to both models. Harmless — the device substitutes Speed and
  leaves the file alone.
- **A cloned profile reads a zero odometer.** Expected rather than
  lost: the odometer lives in `Totals.fit`, which appears to key its
  records by profile name, so a clone has no record of its own. Under
  investigation.
