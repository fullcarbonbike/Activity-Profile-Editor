# v1.6.1 — Four fields that were hiding behind other fields' names

*Released 2026-10-14.*

A small release with one user-facing addition, two fixes, and a front page
that had quietly become wrong.

## Four new data fields

The Edge's **Graphical** menu category contains three different kinds of
field, and until now this toolkit knew two of them. The third is a live
numeric readout with **AVG and MAX** alongside it — no plot, no bars, just
three numbers:

| id | this toolkit calls it | the device calls it |
|---|---|---|
| 351 | `Heart Rate (Avg/Max)` | `Heart Rate` |
| 352 | `Speed (Avg/Max)` | `Speed` |
| 353 | `Cadence (Avg/Max)` | `Cadence` |
| 354 | `Power (Avg/Max)` | `Power` |

Confirmed on both an Edge 530 and an Edge 840, placed and pulled back
rather than read off a menu, and deployed to both devices.

**Why they took this long to find, which is more interesting than the
fields themselves.** The device gives each of them the *same name* as an
existing field — 351 is called "Heart Rate" exactly as id 13 is. Every
field census this project has run was built by reading the on-device menu
and listing the unfamiliar entries, so a field wearing another field's name
was invisible to the method, and being skipped left no trace: nothing in the
unresolved list, nothing on the checklist, no count that looked wrong. The
rule from here on is that a familiar-looking menu entry gets placed and
pulled like any other, because only an id can tell you it is the same field.

**The naming.** Each entry carries a content qualifier rather than the menu
category, matching how this table already works — `HR Zone 1 (time)`,
`Intensity Factor (IF)`, `Elevation (ft)`. The picker shows the real device
string too, so the row reads:

```
Speed (Avg/Max)   (id=352, shows as "Speed")
```

`(Graphical)` was the first proposal and was dropped: all three families
live under that menu heading, so it would have separated these from plain
Speed while colliding with `Speed Graph` two rows down the list.

## Fixes

- **A saved favourite no longer loses its layout on an 840.** Saving a
  favourite from a C-variant screen and loading it back gave you an A
  variant — silently, with a plausible-looking result. The clamp
  responsible was written when only A and B existed and was never revisited
  when the 840's C variants arrived. The load path already had a
  model-aware check for exactly this case; it could never fire, because the
  clamp ran first and handed it a legal value.
- **The Add Field dialog was about to truncate.** It is a plain list with
  no horizontal scrolling, so an overlong row is cut with no ellipsis and
  nothing to say it happened — and the new field rows are the longest in
  the catalog. Widened to suit.

## The README was telling 840 owners to go away

Worth calling out rather than burying. The front page still said the
toolkit was **"currently unusable"** on the 540, 840, 1040 and 1050, that
there was **"no working route for an MTP device today"**, and that offline
mode and Export were planned features that did not exist. All of that was
true when written and has been false since **v1.5.0**, which shipped both —
and v1.6.0 was devoted to the 840.

It also asked readers to report whether `Garmin/NewFiles/` is writable over
MTP, describing that as the question that would decide whether any of this
was worth building. It has been answered many times over on a real 840.

That section is now a comparison of the two workflows — Connected and
Offline — with step-by-step instructions for each and a plain statement of
what differs between them.

## Behind the scenes

**Data field slot heights are now fully modelled**, on both devices: all 24
Edge 840 user-screen layout states and all 15 the 530 offers. The rule
behind them is simple — a row of two half-width fields is always 1/5 of the
screen, so the screen is five units tall and the full-width rows share what
is left.

Nothing in the interface draws to scale yet. The practical consequence
meanwhile, for anyone placing a field that wants vertical room: a taller
full-width row exists **only at 1, 3, 4, 5, 6 and 7 fields**. Every 8-, 9-
and 10-field layout is five regular rows in every variant, so no amount of
rearranging an 8-field screen will give a field more height.

`fit_dump.py knowledge` also now self-checks both the height tables and the
field-name table, and prints what it covers per model.

## Upgrading

No file format change, no migration. Backups and profiles from v1.6.0 work
unchanged.

`fit_dump.py` 2.25.0 · `gui_app.py` 0.27.4 · `fit_patch.py` 1.18.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0

---

## Known gaps, named rather than hidden

- **The Graph/Bars placement advice is wrong in both directions, and this
  release does not fix it.** Measuring both devices field by field showed
  that at half width the 530 drops the widget while the 840 keeps it — so
  the toolkit currently tells an 840 user a field "needs full width to
  render as a graph/bar" when on their device it renders fine, and says
  nothing to a 530 user whose field quietly loses its AVG and MAX in a
  full-width *regular-height* row. Both are understood and measured; the
  fix is deliberately held back rather than rushed into a minor release.
- **Row height is modelled but not drawn.** The layout diagram still shows
  every row the same height. Content height — eBike's strip, drawn about
  four times too tall — remains unmodelled.
- **Cycling a screen's layouts still replaces its fields with Timer.** Back
  out without applying to recover them.
- **Radar's three layouts cannot be drawn.** Measured, documented, and not
  expressible as rows.
- **Content composition is unmodelled.** Segment's A/B/C select which
  graphics appear in its panel, not the field arrangement.
- **No per-model field availability.** The picker offers every known field
  to both models. Harmless — the device substitutes Speed and leaves the
  file alone — but the cross-model warning cannot check fields.
- **A cloned profile reads a zero odometer.** Expected rather than lost:
  the odometer lives in `Totals.fit`, which appears to key its records by
  profile name, so a clone has no record of its own. Under investigation.
