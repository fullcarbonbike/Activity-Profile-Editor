# Test plan — v1.6.0 (in progress)

*Written 2026-10-01. Covers everything built since the v1.5.0 tag that
needs a display. `fit_dump.py` 2.14.1, `gui_app.py` 0.26.0.*

## Why this exists before anything else gets built

Four changes have landed that cannot be exercised headlessly, and one of
them is of the exact kind that shipped **inert** in v1.5.0 — the per-model
feature worked in every CLI test and did nothing in the GUI, because
`frame.profile_product` was set on the wrong object and `None` silently
means "enforce the 530's rules". Nothing here is believed to work until
the device says so.

**Use `CyclingRoadLayouts.fit` for sections C and D.** It carries all nine
of the newly measured 840 states, which is exactly what needs exercising.

---

## A — Field picker (`gui_app.py` v0.24.0)

Open any screen → **Add Field**.

| | Check | Expect |
|---|---|---|
| A1 | Dialog width | Wider than before (360 → 460). Nothing clipped at the right edge. |
| A2 | Scroll to **Avg Force** | `Avg Force  (id=847, shows as “Average”)` |
| A3 | **Max. Force**, **Max. Lap Force**, **Last Lap Force** | `shows as “MAX”` / `“MAX LAP”` / `“LAST LAP”` |
| A4 | **Primary Target**, **Secondary Target** | `(id=520, no label on-device)` and `(id=578, …)` |
| A5 | **Force**, **3s Force**, **Lap Force** | **No** suffix — their text already says force, so they are deliberately not flagged |
| A6 | Type `force` in Search | Still filters correctly. Matching is on the stored name only; the suffix must not interfere |
| A7 | Select **Power Graph** | The Graph/Bars note below the list still appears (pre-existing behaviour, must not have regressed) |

## B — Tier-2 advisory (v0.26.0, new)

| | Check | Expect |
|---|---|---|
| B1 | Put **Compass** (529) in a slot that **shares a row** | `⚠ “Compass” shares a row -- it will draw correctly but be very small to read at half width.` |
| B2 | Same field in a **full-width** slot | **Silent** |
| B3 | **Map** (725), shared row | Same message, named for Map |
| B4 | A screen holding Map **and** Power Graph **and** a Connect IQ field, all half-width | **Three different messages.** Keeping them distinct is the whole point — if Compass gets told it "needs full width to render as a graph/bar, not plain text", that's wrong |

## C — 840 per-model geometry (v0.25.0 + `fit_dump` v2.13.0)

**This is the inert-feature test.** Open `CyclingRoadLayouts.fit`.

| | Check | Expect |
|---|---|---|
| C1 | Open each of the five **C-variant** screens (counts 3, 4, 5, 6, 7) | Diagram draws the row structure you described on the device, not a generic one |
| C2 | Open the **8/B, 8/C, 9/B, 9/C** screens | Same — these four had **no geometry at all** before today |
| C3 | On the **9/C** screen, put a Graph/Bars field (e.g. Power Graph) at **position 0** | Advisory **fires**. It was silent on this state before v0.25.0 |
| C4 | Same field at **position 4** of 9/C | **Silent** — position 4 genuinely *is* full width there |

> **If C3 stays silent, suspect the wiring, not the data.** The grids are
> verified; the likely cause is `frame.profile_product` not reaching
> `EditScreenPanel`, which is precisely how v1.5.0 shipped inert. Worth
> checking the title bar / details pane says **Edge 840** at all.

## D — Height notes (v0.26.0, consolidated)

| | Check | Expect |
|---|---|---|
| D1 | A **530** profile, 3-field screen, layout **B** | `B: top field renders smaller on-device (not shown to scale here)` — unchanged wording, now from one place instead of two hardcoded copies |
| D2 | 840 **3/C, 4/C, 5/C, 6/C** | A **new** note naming which rows are taller |
| D3 | 840 **9/C** (or 7/C, 8/B, 8/C, 9/B) | **No note.** Correct — no height observation exists for those, and `None` means "nothing known", not "all rows equal" |

## E — Regressions worth a glance

| | Check | Expect |
|---|---|---|
| E1 | Open a **530** profile and walk several screens | Everything exactly as in v1.5.0. The 530 was verified byte-identical across all 30 of its layout states, headlessly — this is the visual confirmation |
| E2 | Any screen with many fields / long names | **No window-width blowup.** This codebase's most recurrent bug, seven occurrences; the picker was deliberately widened and that is safe only because it has a fixed size and never calls `Fit()` |
| E3 | Named screens — Compass, Stamina, Lap Summary, Segment | Layout pickers and content-area diagrams unchanged |

---

## Does any of this need a pull? — NO, for B through F

Asked 2026-10-02. **Every check in B through F is either a display
assertion or a write to the toolkit's own staged copy.** Nothing reads
anything back off the device, so no pull is required and nothing needs
deploying.

More than that: **B, C, D, E and F can all be done in OFFLINE mode with no
device connected at all**, using `CyclingRoadLayouts.fit` and any 530
profile from your folder. That works because `frame.profile_product` is
derived from `file_id.product` **in the file**, which was the point of
making it a property in v1.5.0 — model identity travels with the profile,
not with the USB connection. Worth knowing precisely because section C is
the inert-feature test and it depends on that value arriving.

**But there IS a gap the plan did not cover, and it needs a round trip.**
See section G. It is optional for signing off B–F and important before
release.

## C1 FAILED and is FIXED — re-run C and F on v0.26.2

**Doug, 2026-10-02:** the layout preview read **"(No layout to show)"** for
every C variant and for 8/B, 8/C, 9/B and 9/C. His table matched the nine
`user_grids` states exactly, which is what identified the cause.

**Cause, and it was mine.** `AddScreenPanel`'s diagram still read the
global 530 `LAYOUT_GRIDS`, which holds none of those nine, so it returned
`[]` — and an empty grid is precisely what the diagram draws that message
for. v0.26.1 made that panel's *dropdown* model-aware and left the diagram
global, with a comment claiming it was safe because "a new screen starts at
variant A, which is in the global table at every count". True of the
default and irrelevant to the feature: the whole point of the new dropdown
is that B and C became selectable. **The justification was written in the
same commit that invalidated it.**

A second instance of the same mistake, in the same method, found only
because the first one was visible: the **height note** was also still
global-only. It had no symptom of its own — but at count 3 the note is the
*only* thing distinguishing A, B and C, since all three share the row
structure `[[0],[1],[2]]` and differ purely in row height.

**Expect this on re-run, and it is correct, not a bug:** at **count 3**,
A, B and C all draw the **same three stacked full-width rows**. They differ
only in height, which the grid cannot express. The note below the diagram
is what tells them apart.

## F — Layout variant dropdown (v0.26.1, replaces the A/B radios)

**New since you ran section A. Section A does NOT need re-running** — those
tests are all `FieldPickerDialog`, which this did not touch.

The two A/B radio buttons in **Edit Screen** and **Add New Screen** are now
a single **Layout:** dropdown, built from what the model actually offers.

| | Check | Expect |
|---|---|---|
| F1 | 840, 9-field screen, Edit Screen | Dropdown offers **A, B and C**. This is the bug you found |
| F2 | 840, 8-field screen | **A, B, C** |
| F3 | 840, 3-field through 7-field | **A, B, C** |
| F4 | 840, 1, 2 or 10 fields | **A only**, control disabled — those counts have one variant |
| F5 | Pick **C** on a 9-field 840 screen | Applies. Diagram redraws to the 9/C row structure, and no "Layout B isn't available" dialog appears — that refusal is deleted, not corrected |
| F6 | **530**, 3- to 7-field screen | **A and B** only. Unchanged from v1.5.0 |
| F7 | **530**, 8-, 9- or 10-field screen | **A only**, disabled. Unchanged |
| F8 | 840 **Segment** screen with 4 fields (named type, separate picker) | Reads **"4 fields (C)"**, not "4 fields (3)". Separate bug, live before today |
| F9 | 530 **Segment** with 4 fields | Still "4 fields (A)" / "4 fields (B)". Its "A" stores `f8=2`, so if the letters moved, the positional mapping broke |
| F10 | Change a layout, then re-open the screen | The dropdown shows the variant you chose, i.e. it was written and read back |
| F11 | Load a **Favorite** saved from an 840 C-variant screen onto a 530 | Falls back to a legal variant rather than writing `f8=2`, which the 530 offers at no count |

> **F9 is the one that catches a whole class of error.** The dropdown's
> selection index is *not* the `f8` value — Segment's "A" is `f8=2` on the
> 530. If letters and layouts have come unstuck anywhere, this is where it
> shows.

---

## Known limitation — FIXED 2026-10-01, see section F

**Corrected 2026-10-01 after Doug found it in testing (A-section run).**

On an 840, **neither panel can select a C variant, nor any variant of 8 or
9 fields.** Doug viewing a 9-field screen in **Edit Screen**: the radios
show A and B, B cannot be selected, and there is no C at all.

**The workaround this plan originally gave does not work.** It said to
create the screen in Add New Screen and change its layout in Edit Screen
"which *is* model-aware". Edit Screen is model-aware for **geometry and
advisories** — that is what v0.25.0 added — but **not for the variant
selector**. For a plain user screen it still asks
`count in COUNTS_WITH_B_VARIANT`, the 530's set `{3,4,5,6,7}`, so a
9-field screen gets B disabled and C never existed as a control. Two
radios cannot express three options.

My error, in both this plan and PROJECT_NOTES Doc rev 132.

**~~So there is currently NO route~~ FIXED in v0.26.1** — both panels now
build the control from `layout_variants_for_count()`. The section below is
kept as the record of what was wrong and why. Test it via section F.

**What still works, and is worth confirming — this is section C's point:**
the toolkit now READS and DRAWS those states correctly. The read side and
the write side are separate, and only the write side is blocked, so
sections B through E are unaffected and worth finishing.

**Why the fix is small:** `layout_variants_for_count(0, 9, 4062)` already
returns `[0, 1, 2]` — the data layer has been model-aware all along. Only
the GUI's `else` branch ignores it in favour of the 530 constant. Three
sites need it: that branch, `on_layout_choice()`'s refusal test, and
`_apply_field_list()`'s equivalent.

---

## G — OPTIONAL, but the real write-side gap (needs a deploy and a pull)

**Not required to finish B–F. Required before release.**

Every one of the nine 840 layout states was measured from a profile **the
device itself authored**. v0.26.1 now lets the *toolkit* author them — and
nothing has confirmed that a toolkit-written `f8=2` survives the NewFiles
process and renders as expected on the device.

That is a different question from everything above, and it is the question
this project has been burned by before: the toolkit can write the byte, the
file can pass CRC and read-back, and the device can still do something
else with it. ClimbPro, Compass and the CIQ Timer-fallback were all found
exactly there.

| | Step | Expect |
|---|---|---|
| G1 | On an 840 profile, set a user screen to **9 fields, layout C** using the new dropdown. Deploy | Writes cleanly, pre-flight CRC and content checks pass |
| G2 | Let the device run NewFiles, then look at that screen **on the 840** | Renders as **2 HW rows, 2 HW rows, 1 FW, 2 HW rows** — the 9/C structure, matching what the toolkit drew |
| G3 | Pull the profile back and send it to me | `f8` is still **2** on that record, and the field array is intact |
| G4 | Repeat for one **8/C** screen | Same |

> **If G2 renders something other than 9/C**, the grid is not the suspect —
> it was measured from the device's own file. The suspect is the write:
> either `f8` did not land, or the device re-derived the layout from
> something else on import, which is the behaviour it already shows when it
> **strips screen records by type** and when it **clamps over-range counts
> at render without rewriting the file**.
>
> **If G3 comes back with `f8` changed**, that is a new device behaviour
> and more interesting than the feature.

G1 and G2 alone are worth the bench time. G3 is cheap once the device is
already connected, and it is the only step that proves the byte persisted
rather than merely rendered once.

---

## H — Named screens, 530 vs 840 (v0.26.3)

**Added 2026-10-02 after Doug asked whether the C1 class of bug reached
named screens. It did, silently. See Doc rev 136.**

Until v0.26.3, 18 of the 46 states the 840 offers on named types drew
**ordinary-user-screen geometry** — a confident wrong shape with nothing
saying so, because those states are legal and no flag applied.

| | Check | Expect |
|---|---|---|
| H1 | 840, open the **Workout** screen in Census4 (6 fields) | Diagram **blank**, with a note: *"Field arrangement at this layout has not been measured on the Edge 840 — not drawn rather than guessed"* |
| H2 | 840, **eBike Metrics** — change its count to 7 | Same blank + note |
| H3 | 840, **eBike Metrics** at **5** fields | **Draws a real grid.** 5 is measured; this is the control proving H2 is about data, not about the type |
| H4 | 840, **STEPS Metrics** at **4** fields | Draws a real grid (measured) |
| H5 | 840 **Compass** at 0, 1 and 2 fields | All three draw. The 840 offers all three where the 530 locks 2 — the original per-model defect |
| H6 | 840 **Segment** at 4 fields | Picker reads **"4 fields (C)"** for the third variant, not "(3)" — same as F8 |
| H7 | **530**, walk every named screen you have | **Every one draws a grid. No blanks, no notes.** All 25 of its named states are measured, so a blank here is a regression |
| H8 | 840 **Workout** — confirm field editing is offered at all | Allowed on the 840, refused on the 530 (`NO_FIELD_EDIT_BY_MODEL`) |

> **H7 is the regression guard.** The v0.26.3 change only suppresses the
> guessed-geometry fallback for named types. If a 530 named screen now
> draws blank, the suppression is too broad.

**H1 is the cheap one and needs no hardware** — Census4 already has a
6-field Workout screen, and Workout is field-editable on the 840.

To replace those blanks with real geometry, see `NAMED_LAYOUT_CAPTURE.md`.

---

## I — Layout letter, everywhere it appears (v0.26.4 / fit_dump 2.15.1)

**Doug found the screens-list Layout column showing `-` for every
C-variant. The letter was derived in four places by arithmetic on `f8`.
See Doc rev 138.**

| | Check | Expect |
|---|---|---|
| I1 | 840 Layouts profile, screens-list Layout column | A real letter on every screen — **C** where you set C. No `-` on a C screen |
| I2 | 840, counts 1, 2 and 10 | **A** |
| I3 | 840, **GroupTrack List** and **Virtual Partner** rows | `-`, not `?`. Those types have no layout to letter |
| I4 | **530**, a **Segment** screen at 4 fields in layout **A** | **A**. It stores `f8=2` and showed `-` before today — a pre-existing 530 bug |
| I5 | CLI `fit_dump.py screens <840 profile>` | LAY column shows **C** on C screens, blank on A (established terse convention), `-` on types with no layout |
| I6 | Same CLI with `-v` | Reads **`C (f8=2)`**, not `variant=2?` |
| I7 | Change a layout on an 840 screen, then open **Pre-Flight** | *"layout changed from B to C"* — not *"from A to -"* |

> **I4 is a 530 check and the important one.** It confirms the letter is
> positional rather than arithmetic. If I4 reads **C**, the fix has
> reintroduced the exact error it was meant to remove.
