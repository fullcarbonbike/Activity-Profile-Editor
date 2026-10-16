# v1.7.0 — The layout diagram tells the truth about slot sizes

*Released 2026-10-15.*

The toolkit has known since v1.6.1 how tall every data field slot is. This
release makes it *use* that: the layout diagram draws rows to scale, and
the placement advice is finally right on both devices instead of wrong on
each in a different way.

## Rows are drawn to scale

The diagram used to draw every row the same height, which made several
layouts indistinguishable from one another. Pick 3 fields and cycle A, B
and C: all three share the same row structure and differ *only* in how
tall each row is, so until now all three drew identically and a line of
text was the only thing telling them apart.

Now they look like what the device shows:

| | rows |
|---|---|
| 3 fields, A | three equal thirds |
| 3 fields, B | one short row, then two tall |
| 3 fields, C | two tall rows, then one short |

Same for every layout with a tall slot — 5/B, 7/B, 4/C and the rest. If
you have been choosing a variant to give one field more room, you can now
see whether you got it.

**Plain user screens only.** Named screens (eBike Metrics, Segment,
Compass and the rest) still draw uniform rows, because their row heights
have never been measured — all twenty of them. Drawing a plausible guess
is how an earlier release ended up showing geometry nobody had checked,
and that is not worth repeating for a nicer picture.

## Placement advice that is right on your device

The old warning said a graph or bars field "needs full width to render as
a graph/bar, not plain text" whenever it shared a row. Measuring both
devices field by field showed that was **wrong in both directions**:

- on an **840** it was a false alarm — that model draws the widget at half
  width perfectly well, just smaller
- on a **530** it was silent about a real loss — a Graph field in a
  full-width row of *regular* height draws its plot but quietly drops its
  AVG and MAX

The second one was the more embarrassing, because the 530 is the device
the original rule was measured on. Every observation behind it had come
from the half-width case, so the rule was never wrong about what it had
seen — only about everything it had not.

Warnings are now per model and per family, and say what to **do** rather
than describing the slot:

> ⚠ "Power Graph" will not draw its plot in this slot — it shows a plain
> number instead.

> ⚠ "Power Graph" draws here, but needs a taller row to show its AVG/MAX
> as well.

> ⚠ "Speed (Avg/Max)" draws here, but needs a full-width slot to show its
> AVG/MAX as well.

The remedy differs by family — a Graph field needs a taller row, a Bars or
numeric field needs a wider one — so calling a slot "too short" when you
need to widen it would send you the wrong way.

When the toolkit cannot tell which model a profile came from, it now says
nothing rather than guessing. Guessing is what produced the old advice.

## Cycling layouts: the warning now says the loss is permanent

Switching a named screen to a layout with fewer fields has always warned,
and has always named the fields being dropped. What it never said is that
switching back does **not** bring them back — the slots refill with
"Timer" and you set each one again.

Anyone cycling the layouts to see what each looks like read "removes 2
fields… Proceed?" and reasonably assumed it was reversible. It is not, and
now the dialog says so, and points at "Discard Edits" as the way to undo.

The underlying behaviour is unchanged — this is the honest warning, not the
fix. Garmin's own on-device editor preserves fields across a layout change,
so the toolkit should too; that is the next piece of work.

## Fixes

- **The first screen no longer implies a USB cable is required.** "No
  Garmin device connected" told you to plug in and retry, and said nothing
  about offline mode — on the one screen every user starts on, with the
  "Work Without a Device…" button sitting right beside it. An Edge 840
  owner has no USB route at all, so the app was turning away exactly the
  people the last two releases were built for.
- **The Add New Screen panel's placement warnings work again.** They had
  stopped appearing entirely — introduced and fixed inside this release,
  found by reading the code rather than by testing, because a warning that
  stops appearing looks exactly like a screen with nothing to warn about.

## New: `fit_sdk_check.py`

A read-only script that answers one question: does the installed
`garmin-fit-sdk` still mis-render the profile-name field in a
`Totals.fit`? That matters because this toolkit deliberately uses its own
raw parser for undocumented FIT messages, and that decision deserved a way
to be re-checked rather than assumed.

Answer, across three SDK versions spanning five point releases: **yes,
identically, and it will not change.** The field is undocumented, so it has
no entry in the SDK's profile, so the decoder has no declared type for it
and guesses. There is nothing for Garmin to fix short of documenting the
field.

Useful tell that came out of it: a decoded record mixing named keys with
**bare integer keys** is showing you exactly which fields the SDK is
guessing at.

## Upgrading

No file format change, no migration. Backups and profiles from v1.6.1 work
unchanged.

`fit_dump.py` 2.26.0 · `gui_app.py` 0.27.8 · `fit_patch.py` 1.18.0 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0

---

## Known gaps, named rather than hidden

- **Cycling a named screen's layouts still replaces its fields with
  Timer.** Now warned about honestly, not fixed. The device does this
  properly, so the toolkit should.
- **Named screens have no measured row heights**, so their diagrams still
  draw uniform rows. Twenty screen types, each with a content area the row
  model does not describe — a bigger measuring job than the user screens
  were, and it would need its own model rather than an extension of this
  one.
- **Two user-screen states are still unmeasured for graphical fields** —
  the quarter-screen and half-screen full-width rows. Both are taller than
  a regular row, so the toolkit treats them as safe; if that is wrong the
  cost is a missing warning rather than a false one.
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
