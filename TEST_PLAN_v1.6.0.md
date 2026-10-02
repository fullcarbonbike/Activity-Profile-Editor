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

## Known limitation — WIDER than this plan first said

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

**So there is currently NO route** through the GUI to any of the nine
states measured on 2026-10-01. They are reachable only by building the
screen in the device's own editor, as `CyclingRoadLayouts.fit` was.

**What still works, and is worth confirming — this is section C's point:**
the toolkit now READS and DRAWS those states correctly. The read side and
the write side are separate, and only the write side is blocked, so
sections B through E are unaffected and worth finishing.

**Why the fix is small:** `layout_variants_for_count(0, 9, 4062)` already
returns `[0, 1, 2]` — the data layer has been model-aware all along. Only
the GUI's `else` branch ignores it in favour of the 530 constant. Three
sites need it: that branch, `on_layout_choice()`'s refusal test, and
`_apply_field_list()`'s equivalent.
