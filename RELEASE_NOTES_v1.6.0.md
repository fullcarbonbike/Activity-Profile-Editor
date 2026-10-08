# v1.6.0 — The Edge 840 stops being a guess

*Released 2026-10-07. Corrected 2026-10-08 — see the correction directly
below. The body of these notes is left as written and is not rewritten.*

> ## Correction, 2026-10-08
>
> **The `v1.6.0` tag contains two commits these notes do not describe.**
> Work on row heights landed between the notes being written and the tag
> being pushed, so the tag carries `fit_dump.py` **2.23.0**, not the
> 2.21.0 printed under *Upgrading* below. `gui_app.py`, `fit_patch.py`,
> `garmin_device.py` and `fit_census.py` are exactly as stated.
>
> **Nothing in the release behaves differently because of it.** The two
> commits add a data table and three functions to `fit_dump.py` and
> nothing outside that file calls them — no read path, no write path, no
> GUI path. v1.6.0 behaves as tested.
>
> **One Known gap below is now half wrong.** *"Row and content height are
> unmodelled"* was true when written. Row height is now modelled: 22 of
> the 24 Edge 840 user-screen states and 13 of the 15 the 530 offers are
> recorded as per-row unit vectors, from the rule that a row of two
> half-width fields is always 1/5 of screen height. So:
>
> - **row height — superseded.** Measured and recorded, though not yet
>   drawn to scale or annotated in the GUI; that is the remaining work.
> - **content height — still true.** eBike's content strip is still drawn
>   about four times too tall.
> - the sentence about counts 3–6 variant C differing from A and B *only*
>   in row height is still correct, but it is no longer unmodelled.
>
> `fit_dump.py knowledge` prints the height coverage for both models and
> self-checks the table, so the accurate statement is always available
> from the code rather than from this file.
>
> **Cause, recorded because the process is the fix:** the version line
> under *Upgrading* is a frozen claim about the tree, and commits
> continued to land on `main` after it was written. Bump versions and
> write the notes **last**, or do not commit between the notes and the
> tag.

v1.5.0 made the toolkit usable on an 840 and stopped it applying one
device's measurements to another. It did not yet **know** the 840. Where
the Edge 530's layouts had been surveyed screen by screen, the 840's were
largely assumed — and the places that assumption showed were the places it
was wrong.

This release closes that. Every layout state either has a measured grid or
is explicitly marked as one the model cannot draw. Nothing is inferred.

---

## What the 840 actually does

**206 data fields are now named**, up from 173. The 33 new ones came from a
single profile built for the purpose: five screens, each anchored with a
known field so a transposition would be visible, pulled once. Among them
the whole Force family, the Stamina group, and **520 and 578 — the two ids that
had sat in `KNOWN_UNRESOLVED_IDS` since it was repopulated.** They turned
out to be Primary and Secondary Target, and the strongest evidence was not
the census screens at all: both already appeared on the device's own
Workout screen template, beside Duration and Workout Comparison, in a
record nobody had edited.

**Every named screen layout on the 840 is measured.** Workout, eBike
Metrics, STEPS Metrics, Compass, Segment, Lap Summary, Stamina, Power
Guide, Music Control, GroupRide — 50 states with grids. The three that
remain undrawn are Radar's, and that is a different problem: its layout is
a left-hand **column**, and the model describes rows.

**Nine user-screen layouts the 840 offers and the 530 does not** — every
"C" variant, plus 8/B, 8/C, 9/B and 9/C. Before this release the toolkit
could neither draw nor select them.

`fit_dump.py knowledge` prints the whole picture, derived from the tables
rather than written alongside them:

```
=== Edge 530 (product 3121) ===
    25 named states: 25 drawn
=== Edge 840 (product 4062) ===
    53 named states: 50 drawn, 3 undrawable
```

---

## Things you can now do that you could not

**Choose a C variant.** The layout control was two radio buttons built on
the 530's two-option shape; on an 840 a 9-field screen offered A and B with
B unselectable and no C at all. It is now a dropdown built from what the
model actually offers, and the illegal states are unreachable by
construction rather than refused after the click.

**See what the device will really display.** The field picker names the
on-device label where it differs from the catalog — `Avg Force (id=847,
shows as "Average")`, because an icon carries the word "Force" and a list
box cannot show it. Two fields render no label at all until a workout step
defines them, and the picker says so.

**Get warned about a field that will be unreadable.** Compass and Map draw
correctly in a half-width slot and are too small to use there. That is a
different failure from a Graph or Bars field, which stops being a graph
entirely, so it gets its own wording instead of borrowing that one.

**Be told when a backup belongs to another model.** Restoring across models
now warns, names the layouts the target does not offer, and says plainly
that data fields are *not* checked — because no per-model record of field
availability exists, and a warning that looks complete and isn't is worse
than one that admits its edge.

---

## Honest blanks

The release's recurring theme, and the thing most likely to look like a
regression: **where the toolkit does not know a layout, it now draws
nothing and says so**, instead of falling back to ordinary user-screen
geometry.

That fallback was not harmless. For eBike Metrics it would have drawn four
of the eight layouts correctly and four wrongly — and nothing on screen
distinguished the halves. Unpredictably wrong is worse than consistently
wrong, because consistently wrong is learnable.

So a diagram may read *"4 field(s) — arrangement not measured on the Edge
840, so not drawn rather than guessed."* That is the toolkit declining to
invent a picture. Today it appears only for Radar.

---

## Cross-model transfers, measured

An 840 profile was pushed to a 530 and pulled back, and the result is now
recorded rather than guessed at:

- a **screen type** the target lacks is **dropped entirely**
- a **field id** it does not know **renders as Speed** — not the "Timer"
  fallback a Connect IQ field gets, so the two diagnose differently
- an **unsupported layout** renders as a legal one
- **nothing is rewritten.** All 33 foreign field ids survived in the file

So a migrate is lossy on screen and reversible on disk. One caveat found
the same way: the device **re-indexes** the screens it keeps, so after a
cross-model transfer the deploy change summary cannot line screens up
correctly. The warning says so.

---

## Fixes

- **A 530 Segment at 4 fields in layout A displayed as "-"**, in the
  screens list, the CLI and the deploy summary. Its menu "A" stores `f8=2`,
  and all three places derived the letter by arithmetic. A pre-existing 530
  defect, surfaced by an 840 symptom and fixed in one shared place.
- **Offline restore led to a dead end** — the whole way to "Write to Device
  (NewFiles)" before refusing, with no Export on that path. Restoring is a
  device operation; offline, the deleted list and its button are gone, with
  a line pointing at opening the backup folder as the source instead.
- **The offline entry path crashed** on a `wx.TextCtrl` given a
  `wx.StaticText` method.
- **The named-screen picker showed "4 fields (3)"** where it meant "(C)".
- A toolkit-written `f8=2` **survives NewFiles and renders correctly** —
  confirmed from the bytes, not just the screen.

---

## Upgrading

No file format change, no migration. Backups and profiles from v1.5.0 work
unchanged, and nothing in this release writes differently to a 530 — all 25
of its named states were verified identical before and after.

`fit_dump.py` 2.21.0 · `gui_app.py` 0.27.3 · `fit_patch.py` 1.18.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0

---

## Known gaps, named rather than hidden

- **Radar's three layouts cannot be drawn.** Measured, documented, and not
  expressible as rows. Needs the geometry model extended.
- **Row and content height are unmodelled.** Counts 3–6 variant C differ
  from A and B *only* in row height, and eBike's content strip is drawn
  about four times too tall.
- **Content composition is unmodelled.** Segment's A/B/C select which
  graphics appear in its panel, not the field arrangement.
- **No per-model field availability.** The picker offers an 840 user all
  206 fields and a 530 user the same 206. Harmless — the device substitutes
  Speed and leaves the file alone — but it means the cross-model warning
  cannot check fields.
- **Cycling a named screen's layouts replaces its fields with Timer.** Back
  out without applying to recover them.
