# Test plan — `gui_app.py` 0.29.0 + 0.29.1

Two changes, one bench session. Covers the `build_diagram_inputs()`
refactor (0.29.0, committed) and the layout picker extended to plain
user screens (0.29.1, #159).

**Nothing here writes to a device.** Every step is in the GUI against a
staged working copy; deploy only if you want to, and only at the end.

---

## What is being tested, and what the risk actually is

**0.29.0 is a pure refactor.** It was diffed against a faithful replica
of the old inline block over 1386 combinations — both models, every f10
including all twenty named types, counts 0–10, variants 0–2 — with zero
differences. So the risk is not in the computation; it is that the
*Add* panel now calls the same helper the *Edit* panel does, and that
panel has been left behind three times before (v0.26.1, v0.26.2,
v0.27.8, the last of which silently turned its warnings off entirely).
**Sections A and B exist to look at the Add panel.** A warning that
stops appearing looks exactly like a screen with nothing to warn about,
which is why this has to be checked by eye rather than inferred.

**0.29.1 is a real behaviour change** on plain user screens, and it
makes the field count reachable in a way it was not before. The old
A/B/C dropdown could not destroy a field because it never touched the
count. The new picker does touch it, and relies on the #150 fix to keep
the hidden tail. **Section D is the one that matters most** — if the
tail handling were wrong, this change would be the thing that exposes
it.

Run **D** even if you run nothing else.

---

## Setup

- A profile on the **840** and one on the **530**. Use clones, not your
  real ones.
- On each, one **plain user screen** with a known, distinguishable set
  of fields — not Timer in every slot, or you cannot tell preserved
  from refilled. Ten fields is ideal for D.
- One **named screen** reachable too (eBike Metrics, Segment, Lap
  Summary — whatever the profile has).

---

## A. Add New Screen panel still draws and still warns (0.29.0)

The panel that has been silently broken three times.

| # | Do | Expect |
|---|---|---|
| A1 | Add New Screen, set count 3, cycle A → B → C | Three **visibly different** diagrams: A three equal thirds, B short-then-two-tall, C two-tall-then-short |
| A2 | **CORRECTED 2026-10-20.** At count 3 read the line under the diagram **at each variant, and note which model** | **840:** blank at A, a note at B *and* at C. **530:** blank at A, a note at **B only** — 3/C is unmeasured there, and a blank is the right answer. A blank at 3/A on either model is CORRECT: equal thirds, nothing to say. |
| A2b | Read any note that does appear | It must **not** end "(not shown to scale here)" — fixed in 0.29.2; the diagram has drawn to scale since v1.7.0 |
| A3 | Add a **Graph** field (e.g. Power Graph) to a half-width slot on the **530** | ⚠ warning appears, naming the field |
| A4 | **CORRECTED 2026-10-20.** Same field, same slot, on the **840** | A warning, but a **different** one: the 530 says the plot will **not draw**; the 840 says it draws but **needs a taller row** for AVG/MAX. My original "no warning" was wrong — see the note under this table. |
| A5 | Add a **Bars** field to a half-width slot, either model | ⚠ warning says it needs a **full-width** slot |
| A6 | Add one of the composite fields (Heart Rate (Avg/Max) etc.) to a half-width slot on the **530** | ⚠ warning, remedy says **full-width** |

A3/A4 together are the actual test: the same action on two models must
give **different answers**. One of them alone proves nothing.

**My A4 expectation was wrong, not the code.** I wrote "no warning" from
v1.7.0's release note, which says the old warning was a false alarm on
an 840. That was about the old warning's *claim* — that the widget would
not render — not about there being nothing to say. A Graph field in a
half-width slot is in a 1-unit row on both models, and a 1-unit row
costs a Graph its AVG/MAX everywhere. So:

| | 530, half width | 840, half width |
|---|---|---|
| Graph | loses the **plot** | draws the plot, loses **AVG/MAX** |
| Bars | loses the **bars** | draws, loses AVG/MAX |
| composite (Avg/Max) | loses **AVG/MAX** | loses nothing |

Doug's observed 840 behaviour — "the graph is rendered, but not the
AVG/MAX data" — is exactly row 1, right-hand column. **A4 PASSES.**

## B. Edit panel is unchanged by the refactor (0.29.0)

| # | Do | Expect |
|---|---|---|
| B1 | Open an existing plain screen, note the diagram and any warnings | Identical to what v1.7.1 showed for that screen |
| B2 | Open a **named** screen with a content area (Segment, Lap Summary) | Content block still drawn, still at the right end (bottom for Lap Summary) |
| B3 | **CORRECTED 2026-10-20.** Open **Virtual Partner at a C variant** (or 8/B, 8/C, 9/B, 9/C) on the **840** | Honest blank with a note leading on the field count — **not** a drawn grid |
| B3-530 | There is no 530 equivalent | All 190 of the 530's named states are measured. Skip this step on a 530. |

**eBike Metrics was the wrong example and is my error.** It had
unmeasured states when the v0.26.3 note was written; it has none now, on
either model. Doug seeing a correct 6-field layout for it is the right
answer, so **B3 as originally written passes vacuously** — it tested
nothing.

The 48 genuinely unmeasured 840 named states today are Virtual Partner,
Reserved, GroupTrack List and the two unnamed types (64, 128) at 3/C–7/C,
8/B, 8/C, 9/B and 9/C, plus Radar at 0/A, 5/A and 5/B. The 530 has none
at all.

B3 is the one that would regress loudly if the helper fell back to the
generic table.

---

## C. The new picker appears and is correct (0.29.1)

| # | Do | Expect |
|---|---|---|
| C1 | Open a plain user screen on the **840** | A **Layout:** dropdown listing **24** entries: 1 field, 2 fields, 3 fields (A/B/C) … 9 fields (A/B/C), 10 fields |
| C2 | Same on the **530** | **15** entries — no C anywhere, and no B at 1, 2, 8, 9 or 10 |
| C3 | On both, check the current selection | Pre-selected on the screen's **actual** current state, not row 0 |
| C4 | Check **Add Field** and **Remove Field** | Both **enabled** |
| C5 | Open a **named** screen | Picker still there, still that type's own list, Add/Remove Field **disabled** |
| C6 | Open **Compass / Elevation / Cycling Dynamics / ClimbPro** | Picker **disabled** entirely (count is locked for these) |

C4 vs C5 is the deliberate asymmetry. If Add Field is greyed on a plain
screen, that is the bug.

## D. The count changes without losing fields (0.29.1 × #150) — **REQUIRED**

Use a plain screen with **10 distinct, named** fields. Write the list
down first.

| # | Do | Expect |
|---|---|---|
| D1 | Pick **4 fields (A)** from the picker | Confirmation naming the 6 that stop being displayed, and saying they are **kept** and will come back |
| D2 | Accept | Diagram shows 4; the first 4 are your originals in order |
| D3 | Pick **10 fields** | All ten back, **same fields, same order**, no Timer anywhere |
| D4 | Repeat D1–D3 twice more | Same result every time — cycling must not degrade |
| D5 | Go 10 → 7 → 3 → 10 without leaving the panel | All ten originals return |
| D6 | Shrink to 4, then **Change Field Type** on slot 1, then grow to 10 | Slot 1 holds the new field; slots 5–10 hold the **originals**, untouched |
| D7 | Shrink to 4, **Back**, re-enter the screen, grow to 10 | Originals return (proves it is in the file, not in panel state) |

**If any of D2–D7 shows "Timer" where you had a real field, stop and
report it.** That is the #150 regression this change is most able to
cause.

D6 is the one that caught a real defect last time: Change Type used to
wipe every slot past the count as a side effect.

## E. Variant changes alone still behave (0.29.1 regression guard)

The old dropdown's job, now done by the picker.

| # | Do | Expect |
|---|---|---|
| E1 | On a 5-field plain screen, pick **5 fields (B)** | Count unchanged, **no** confirmation dialog, diagram changes shape (one row taller) |
| E2 | Pick **5 fields (A)** again | Back to equal rows, fields untouched |
| E3 | On the **840**, pick a **C** variant at 7 or 9 | Selectable and applies — this was unreachable before v0.26.1 and is the state most likely to be mishandled |
| E4 | Back out, re-enter, check the picker | Shows the variant you chose, not A |

E4 is the read-back. A variant that applies but does not persist looks
identical to one that works, until deploy.

## F. The refusals still refuse (0.29.1)

`on_layout_choice()` carried these and was deleted; the shared handler
has to still have them.

| # | Do | Expect |
|---|---|---|
| F1 | Open **GroupTrack List** (no editable field array) | Picker and field buttons disabled; no dialog needed because nothing is clickable |
| F2 | Open a screen holding **two or more Connect IQ fields** and try a layout change | Hard refusal, OK-only, nothing written |
| F3 | On any plain screen, start a layout change and answer **No** to the shrink confirmation | Picker snaps **back** to the original state, file unchanged |

F3 specifically: the old code had a dedicated reselect helper for this
and it was deleted. If the picker stays on the rejected entry, the user
is looking at a lie.

---

## G. Nothing downstream broke

| # | Do | Expect |
|---|---|---|
| G1 | After a layout change, **Back** | Unsaved-edits warning appears |
| G2 | **Discard Edits**, re-enter | Original layout and fields |
| G3 | Make one layout change, go to **Pre-Flight** | Change list names the layout change with the right letters (not "A to -") |
| G4 | Save a **Favorite** from a plain screen at an 840 **C** variant, load it into another screen | Variant survives — this was #157 |

---

## Pass criteria

- **D2–D7 show no Timer substitution.** Non-negotiable.
- A3 warns and A4 does not.
- C1 = 24 entries, C2 = 15.
- C4 enabled, C5 disabled.
- F3 reverts the picker.

Anything else failing is worth reporting but does not block.

## If you want to stop early

Run **D**, then **C1–C5**, then **A3/A4**. That is about ten minutes and
covers the destructive case, the new control, and the panel with the
history of silent breakage.
