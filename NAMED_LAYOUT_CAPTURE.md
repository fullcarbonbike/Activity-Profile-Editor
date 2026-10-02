# Named-screen layout capture — Edge 840

*Generated 2026-10-02. The named-screen analogue of `LAYOUT_CAPTURE_MATRIX.md`,
which closed the same gap for plain user screens. See PROJECT_NOTES.md Doc rev 136.*

## What is missing

**18 of the 46 layout states the 840 offers on named screen types have no
measured grid.** Until v0.26.3 seventeen of them silently drew
ordinary-user-screen geometry — the exact defect v0.22.0 existed to remove.
They now draw blank with a note. Filling this table replaces the blank with
the real arrangement.

The 530 is complete: all 25 of its named states are measured.

| Type | `f10` | Unmeasured states | Hardware needed? |
|---|---|---|---|
| Workout | 38 | 6/A | no — Workout is field-editable on the 840 and Census4 already has a 6-field one | 
| eBike Metrics | 58 | 1/A, 2/A, 3/A, 4/A, 6/A, 7/A, 8/A | **eBike** — you have none. The screen record exists though; the editor may still list layouts | 
| STEPS Metrics (Shimano) | 95 | 1/A, 2/A, 3/A, 5/A, 6/A, 7/A, 8/A | **Shimano STEPS** — you have none. Same caveat as eBike | 
| Radar | 223 | 0/A, 5/A, 5/B | no Varia needed — Radar appeared with none paired, which is how it was identified | 

## ⚠ Radar may not be representable at all — read before measuring it

Your own description of Radar: *"5 half width data fields stacked on the
left side of the screen and the full height half width 'radar' field on the
Right."*

That is a **column**, not a stack of rows. `LAYOUT_GRIDS` and `user_grids`
both model a layout as an ordered list of ROWS, each holding one or two
positions. A left-hand column of five beside a single full-height right-hand
cell cannot be written in that form at all — it is not an unmeasured value,
it is a shape the structure has no way to hold.

So Radar is the one entry here that may need the model extended rather than
a number filled in. **Measure it last**, and if the other three types go in
cleanly, that is the signal that Radar alone is the structural problem.

## Order worth doing it in

1. **Workout at 6 fields** — needs no hardware, and Census4 already has a
   6-field Workout screen. Cheapest possible confirmation that the blank-plus-note
   behaviour is working and that the measurement route is sound.
2. **eBike and STEPS** — try the on-device editor even without the hardware.
   Radar proved the editor lists a type from its RECORD, not from a paired
   sensor, so these may well be readable. If the editor refuses to offer a
   count, **that is data**: it would mean `user_states`/`states` overstate
   what the device offers, and those came from reading menus rather than
   from bytes.
3. **Radar last**, for the reason above.

## How to record each one

Same format you used for the user screens, which worked first time:

> *"2 rows of 2 HW DFs at the top, then the FW DF, then 1 row of 2 HW DFs
> at the bottom."*

Plus, where it applies, which rows are **taller** — that is a separate
dimension the grid cannot express and it is captured as a note
(`row_height_note()`), not as geometry.

**No pull is needed for the geometry itself.** It is read off the device's
own editor. A pull is only needed if you want the stored `f8` for a state
confirmed from bytes, which for named types matters more than usual —
Segment's menu "A" stores `f8=2` on the 530 and `f8=0` on the 840, the one
confirmed case of the same apparent layout storing a different byte across
models.
