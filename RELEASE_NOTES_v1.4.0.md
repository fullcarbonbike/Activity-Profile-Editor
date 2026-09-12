# Activity Profile Editor for Garmin Edge — changes since v1.3.1

Covers everything since the `v1.3.1` tag (2026-09-10). Suggested tag for
this update: **v1.4.0** — Garmin's special screens are now modelled per
type. No breaking changes to ordinary screens.

## What this fixes

The editor had one idea of what a screen looks like, and applied it to
every screen. That was right for the ones you build yourself and wrong
for Garmin's own — Map, Segment, Compass, Elevation, ClimbPro, Cycling
Dynamics, Lap Summary, eBike Metrics and STEPS Metrics each have their
own rules, and a survey of all twelve on a real Edge 530 found they fall
into four distinct groups rather than one.

### Layouts you pick, instead of fields you count

These screens now offer a single **Layout** list holding exactly what the
device offers. A Segment gives you 0, 2, 4/A, 4/B or 6 fields — and no
odd number, because the Edge doesn't allow one. That's why the old
"+ Add Field" button had to go for these screens: adding exactly one
field could only ever produce a layout the device doesn't have.

Screens fixed at two fields — Compass, Elevation, ClimbPro, Cycling
Dynamics — no longer let you add a third. The device would have shown
two regardless, while the file went on claiming three. Their field
*contents* are still fully editable; only the count is fixed.

Choosing a **smaller** layout drops the fields that no longer fit, and
asks first, naming them. Those fields are then gone — growing the layout
again gives you "Timer" placeholders, not the fields you had before, so
re-pick them with Change Type. If you'd rather undo the whole thing,
Discard Edits or Restore from Backup will take the profile back.

### Map and Segment can have no data fields

A full-screen map with no fields over it is a layout the Edge has always
supported. The toolkit simply had no way to express it, because the
minimum was hardcoded at one. Both `0/A` and `0/B` Map layouts now work
(they differ in how much room the elevation graph gets).

### The Segment 4/A bug

Setting a Segment to its 4-field "A" layout wrote the wrong value. If you
have a Segment screen set that way from an earlier version, re-pick the
layout once and it will be stored correctly.

This one is worth explaining, because it is why the whole release is
built the way it is. Every other layout in this toolkit stores 0 for "A"
and 1 for "B". Segment's 4-field "A" stores **2**. Nothing about the
letter tells you that — it's positional in Garmin's menu. It only turned
up by saving the screen one way, pulling the file, saving it the other
way and pulling again: the two differed by a single byte. So the new
table stores every measured value rather than deriving any of them.

### Diagrams that match the real screen

The layout preview now draws the map, compass rose or lap table as its
own block, so the picture has the shape of the actual screen — including
Lap Summary, whose data fields sit *above* its lap table rather than
below it.

The "needs full width" advisories for Graph/Bars and Connect IQ fields
were wrong on these screens for the same underlying reason: a two-field
special screen was read as two stacked full-width rows, when the device
puts those two fields side by side at half width. The advisories stayed
silent exactly where a graph or a Connect IQ field is most cramped.

### Screens that already hold too many fields

If a screen stores more fields than its type supports, the editor now
says so and tells you what the device will really show — and **leaves
the file exactly as it is.** Nothing is rewritten unless you pick a
layout yourself. Garmin's own on-device editor can leave a screen in this
state too, so this is a new piece of information rather than a repair.

## Command line

- `--fields none` sets a screen to zero data fields (Map and Segment
  only). A bare empty string is refused on purpose — that's what an unset
  shell variable expands to, and it shouldn't silently wipe a screen.
- `--layout` accepts `2`, which a 4-field Segment requires. Invalid
  combinations are refused with the legal values for that screen type
  listed, spelling out which is "A" and which is "B".
- Ordinary user screens validate exactly as before.

## Under the hood

Layout geometry now lives in one place, `fit_dump.py`. It used to be
split — the grids in `gui_app.py`, the A/B rules in `fit_patch.py` — with
nothing forcing the two to agree. They had drifted apart without anything
noticing, which is how a 4-field Segment came to be written with a user
screen's layout value.

## Version bumps

- `fit_dump.py` 2.7.0 → 2.8.0
- `fit_patch.py` 1.16.1 → 1.17.0
- `gui_app.py` 0.21.2 → 0.22.0
