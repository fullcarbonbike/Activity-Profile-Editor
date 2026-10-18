# v1.7.1 — Changing a layout no longer throws your data fields away

*Released 2026-10-18.*

Shrink a screen's layout and the fields that stop fitting are **kept**.
Grow it again and they come back, exactly as they were. This is how the
Edge itself has always behaved; the toolkit was the only thing deleting
them.

## What was wrong

Switching a screen to a layout with fewer fields discarded the ones that
no longer fitted. Going back refilled those slots with "Timer" and the
originals were gone — so cycling the layouts to see what each looked like
quietly destroyed the screen you were inspecting.

v1.7.0 made the warning honest about that. This release removes the cause.

## What the device actually does

Four pulls from a real Edge 840, shrinking a 10-field screen to 4 and
growing it back:

| action | bytes the device writes |
|---|---|
| change the layout count | **one** — the field count |
| change a field | **two** — that slot, in place |
| the fields beyond the count | **none; never touched** |

A full 10 → 4 → 10 round trip returns the file **byte for byte identical**
to where it started.

So there is no clever restore to admire. The field list is always ten
slots long and the layout count is simply how many of them are shown. The
device never deletes anything, which is why its layouts have always
appeared to remember.

The toolkit had been overwriting the unused slots every time it wrote a
screen — one line, padding the list out with "empty". That was the whole
defect.

## What changed

Shrinking now writes the count and nothing else. Growing reveals whatever
those slots already held, and only falls back to "Timer" for a slot that
was genuinely never configured.

The same applies to **Change Field Type**: changing one field used to wipe
every slot past the count as a side effect. It now touches only the slot
you changed.

Verified against the device pulls: for shrinking, growing and changing a
field, **the toolkit now writes byte-identical files to Garmin's own
editor**.

## Add Field now offers what the slot already holds

The Edge has no add-or-remove-field control once a screen exists — you
choose fields when you create it, and after that only the layout control
and per-field changes. Add Field and Remove Field are this toolkit's own
additions, which is useful, but it left two routes to the same result
disagreeing:

- widening the layout from 4 to 5 brought back the field that was there
- Add Field replaced it with whatever you picked, and said nothing

Now the picker **opens on the field already waiting in that slot**. Accept
it and you get what widening the layout would have given you; pick
anything else and you have deliberately replaced it.

## The v1.7.0 warning has been corrected

Three days ago it said the loss could not be undone by switching back.
That was true then and is false now, so it has been reworded in the same
release that makes it so.

It is still a confirmation rather than nothing at all — the fields do stop
being *displayed*, and on a screen you are about to ride with that is
worth one look — but it now tells you they are kept and will return.

## Upgrading

No file format change, no migration. Backups and profiles from v1.7.0 work
unchanged.

**Screens you shrank with an earlier version cannot be recovered** — those
fields were erased at the time, not hidden. From this release forward they
are kept. If you have a backup from before the shrink, restoring it brings
them back.

`fit_dump.py` 2.26.0 · `gui_app.py` 0.28.1 · `fit_patch.py` 1.19.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0

---

## Known gaps, named rather than hidden

- **Remove Field leaves a repeat.** Removing a field from the middle
  shifts the others up, so the last position keeps a duplicate beyond the
  count. Nothing displays it, and it only reappears as a repeated field if
  you later grow the screen. Preserving the deeper fields was judged worth
  that.
- **No layout-count control for ordinary screens.** Only the named screens
  — eBike Metrics, Segment, Lap Summary and so on — offer a layout picker
  that changes how many fields are shown. On an ordinary screen the count
  changes one field at a time through Add and Remove. The device offers it
  on both.
- **Named screens have no measured row heights**, so their diagrams still
  draw uniform rows.
- **Two user-screen slot sizes are unmeasured for graphical fields** — the
  quarter-screen and half-screen full-width rows.
- **Radar's three layouts cannot be drawn.** Measured, documented, not
  expressible as rows.
- **Content composition is unmodelled.** Segment's A/B/C select which
  graphics appear, not the field arrangement.
- **No per-model field availability.** The picker offers every known field
  to both models. Harmless — the device substitutes Speed and leaves the
  file alone.
- **A cloned profile reads a zero odometer.** Expected rather than lost:
  the odometer lives in `Totals.fit`, which appears to key its records by
  profile name, so a clone has no record of its own. Under investigation.
