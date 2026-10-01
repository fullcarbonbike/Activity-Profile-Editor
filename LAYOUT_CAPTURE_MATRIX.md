# Layout capture matrix — Edge 840 user screens

*One profile, ten screens, one pull. Generated 2026-10-01 from
`MODEL_LAYOUTS[4062]['user_states']` versus what `LAYOUT_GRIDS` can
actually express. See PROJECT_NOTES.md Doc rev 131.*

## What this closes

Nine of the 840's twenty-four legal user-screen states have **no grid
anywhere in the code** — every "C" variant plus 8/B, 8/C, 9/B and 9/C. For
those nine `is_position_full_width()` returns `None`, so the full-width
advisory, the Graph/Bars warning and the layout diagram all go silent. Safe
(no opinion beats a wrong opinion) but unexplained to the user.

This matrix is the nine, plus one control.

## ⚠ Each screen needs a DIFFERENT anchor field at slot 0

Not decoration — **without it two of these screens are indistinguishable.**
Screens 6 and 7 are both 8 fields, screens 8 and 9 are both 9 fields. After
the pull they differ only by `f8`, which is the very thing being measured,
so there would be no way to say which one you saved as B and which as C.
A distinct known field at slot 0 makes identity readable from the bytes.

Same safeguard as the field census, same reason, and that pull came back
with all five anchors correct.

Put the anchor in **slot 0**, and **set the field count and layout letter
FIRST, then place the anchor** — changing the count can reshuffle or
truncate slots. Glance at slot 0 before moving on.

## The matrix

| # | Count | Letter | Anchor at slot 0 | Expected `f8` | Geometry you observe |
|---|---|---|---|---|---|
| 1 | 3 | **C** | Speed *(48)* | 2 | |
| 2 | 4 | **C** | Cadence *(3)* | 2 | |
| 3 | 5 | **C** | Heart Rate *(13)* | 2 | |
| 4 | 6 | **C** | Power *(36)* | 2 | |
| 5 | 7 | **C** | Odometer *(95)* | 2 | *(already described — see below)* |
| 6 | 8 | **B** | Total Ascent *(60)* | 1 | |
| 7 | 8 | **C** | Total Descent *(61)* | 2 | |
| 8 | 9 | **B** | Avg Speed *(49)* | 1 | |
| 9 | 9 | **C** | Max Speed *(91)* | 2 | |
| 10 | 5 | **B** | Laps *(24)* | 1 | *control — see below* |

For "geometry you observe", the format you used for count 7 is exactly
right: *"2 rows of 2 HW DFs at the top, then the FW DF, then 1 row of 2
HW DFs at the bottom."*

## The two rows that are checks rather than measurements

**Screen 5 (7/C)** — you have already described this geometry, so its job
here is different: it tests the **elimination**. A=0 and B=1 are accounted
for at count 7, so C ought to be 2. If it comes back `f8=2`, the ordering
holds. **If it comes back anything else, the elimination was wrong and
every "expected `f8`" in this table is suspect** — which is precisely what
happened with Segment on the 530, where the menu's "A" stores `f8=2`.

**Screen 10 (5/B)** — a control at a *different count*. Its grid is already
known from the 530 and B is already measured as `f8=1` at count 7. If 5/B
also stores 1, the letter→`f8` mapping is confirmed across counts and the
nine new readings can be trusted. If 5/B stores something else, the mapping
is **per-count**, which would be a genuinely new finding and worth more
than the nine grids.

Cheap, and between them they mean nothing in this table rests on inference.

## Notes

- **Field contents don't matter** beyond slot 0. Let the device fill the
  rest with whatever defaults it likes — this is a geometry census, not a
  field census.
- **Ten user screens is a lot.** Census4 carried twenty reorderable slots
  total, so there should be room, but you may need to remove or hide some
  existing screens first. A scratch profile, not one you ride with.
- **If the editor won't offer a letter** for some count, that is data: it
  would mean `user_states` is wrong about that state being legal, which
  came from the iPhone Connect app rather than the device itself. Note it
  and move on.
- **Don't fill in the `f8` column yourself** — it comes from the bytes. If
  the pull disagrees with the "expected" column, the expectation is what
  was wrong.
