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
| A2 | Still at count 3, read the line under the diagram | A height note, not a blank |
| A3 | Add a **Graph** field (e.g. Power Graph) to a half-width slot on the **530** | ⚠ warning appears, naming the field |
| A4 | Same field, same slot, on the **840** | **No** warning — the 840 draws it at half width |
| A5 | Add a **Bars** field to a half-width slot, either model | ⚠ warning says it needs a **full-width** slot |
| A6 | Add one of the composite fields (Heart Rate (Avg/Max) etc.) to a half-width slot on the **530** | ⚠ warning, remedy says **full-width** |

A3/A4 together are the actual test: the same action on two models must
give different answers. One of them alone proves nothing.

## B. Edit panel is unchanged by the refactor (0.29.0)

| # | Do | Expect |
|---|---|---|
| B1 | Open an existing plain screen, note the diagram and any warnings | Identical to what v1.7.1 showed for that screen |
| B2 | Open a **named** screen with a content area (Segment, Lap Summary) | Content block still drawn, still at the right end (bottom for Lap Summary) |
| B3 | Open a named screen in an **unmeasured** state (eBike Metrics at 1, 2, 3, 4, 6 or 8) | Honest blank with a note leading on the field count — **not** a drawn grid |

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
