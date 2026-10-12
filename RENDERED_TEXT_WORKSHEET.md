# Rendered-text verification worksheet — Edge 840, Census4

*Generated 2026-09-30 directly from `CyclingRoadCensus4.fit`, not from the
build sheet. Slot order, field order, counts and layout variants below are
read out of the file's own bytes, so there is no transcription step between
the device and this table — the one place the 2026-08-17 batch went wrong.*

## What this is for

`FIELD_ID_NAMES` is supposed to hold **what the data field displays on the**
**device**, not what the picker menu calls it and not what the manual calls
it. Most of the 33 names added on 2026-09-30 came from the manual, so they
are provisional. The **ids are not in question**; only the strings are.

Already one confirmed divergence: 294's menu entry says **Trainer Controls**
and the rendered field says **Resistance**. That is exactly the class of
difference this pass is looking for.

## The blank fields are DATA, not mistakes

Doug noted a couple of fields rendering with no text. Worth separating three
different things, because they mean different things:

1. **No LABEL but a value present** — normal for Graph/Bars-type fields,
   which draw a widget instead of a text label. If any of the new ids does
   this, it belongs in `GRAPH_OR_BARS_FIELD_IDS` (currently 23, 343-350,
   368) and gains the existing full-width advisory. **This would be a real
   finding, not an error.**
2. **A label but no value** (blank, `--`, `0`) — the field is recognised and
   placed, but has nothing to show: no sensor, or nothing to measure while
   stationary. Expected for much of the Force family and for Resistance.
   Says nothing about the name.
3. **Nothing at all, label included** — the interesting case. Could mean the
   slot is too narrow to render that field, or the field is not supported in
   that position. Note the width column when this happens.

Please record which of the three, not just "blank".

## ⚠ The Width column is 530 geometry, NOT measured 840 fact

Read it as a hint, not an answer. `MODEL_LAYOUTS` has no entry for the
840's *plain user screens* — only for its named types — and omission is
meaningful in that table: it means unmeasured, not "same as the 530". The
widths below were computed from the 530's grids because that is the only
grid this project has, and `fit_dump.py` says as much when it reads this
file ("this model's layout rules have NOT been measured").

So if a field's rendered width disagrees with the column, **the column is
the thing that is wrong**, and that disagreement is itself worth recording —
it would be the first measurement of 840 user-screen geometry and would
start a `MODEL_LAYOUTS[4062]` user-screen entry.

Treating the 530's grid as universal is the exact mistake that hard-locked
Compass at 2 fields when the 840 offers 0, 1 or 2. Not repeating it here by
dressing up a 530 number as an 840 one.

---

## Screen A — on-device position 0, slot [0] — 10 fields, layout variant 0
NOTE: all of the Force related data field labels are proceeded with a icon to represent force
| Pos | ID | Name we recorded | Width *(530 est.)* | Rendered text on device | Same? |
|---|---|---|---|---|---|
| 0 | 48 | Speed ← anchor, already known | **half** | SPEED | Y |
| 1 | 860 | Force | **half** | FORCE | Y |
| 2 | 847 | Avg Force | **half** | Average | |
| 3 | 851 | 3s Force | **half** | 3S FRC | |
| 4 | 852 | 10s Force | **half** | 10S FRC | |
| 5 | 853 | 30s Force | **half** | 30S FRC | |
| 6 | 848 | Lap Force | **half** | LAP FRC | |
| 7 | 854 | Last Lap Force | **half** | LAST LAP | |
| 8 | 849 | Max. Force | **half** | MAX | |
| 9 | 850 | Max. Lap Force | **half** | MAX LAP | |

---

## Screen B — on-device position 16, slot [7] — 9 fields, layout variant 0

| Pos | ID | Name we recorded | Width *(530 est.)* | Rendered text on device | Same? |
|---|---|---|---|---|---|
| 0 | 3 | Cadence ← anchor, already known | full | CADENCE | Y |
| 1 | 856 | Normalized Force | **half** | NORM FRC | |
| 2 | 857 | Lap Norm. Force | **half** | LAP N FRC | |
| 3 | 858 | Last Lap Norm. Force | **half** | LL N FRC| |
| 4 | 786 | Vertical Descent Speed | **half** | DESC SPD | |
| 5 | 220 | Avg. Vertical Descent Speed | **half** | AVG DESCENT | |
| 6 | 787 | 30s Vertical Descent Speed | **half** | 30S DES SPD | |
| 7 | 788 | Lap Vertical Descent Speed | **half** | LAP DESCENT | |
| 8 | 223 | Lap Ascent | **half** | LAP ASCENT | Y |

---

## Screen C — on-device position 17, slot [14] — 7 fields, layout variant 1

| Pos | ID | Name we recorded | Width *(530 est.)* | Rendered text on device | Same? |
|---|---|---|---|---|---|
| 0 | 13 | Heart Rate ← anchor, already known | **half** | | Y |
| 1 | 224 | Lap Descent | **half** | LAP DESCENT | Y |
| 2 | 595 | Dist. to Point | full | DIST TO PT | |
| 3 | 32 | Next Pt Location ← already known, rename case | **half** | WPT NEXT | |
| 4 | 596 | Time to Point | **half** | TIME TO PT | |
| 5 | 215 | 24-Hour Minimum Temperature | **half** | 24-HOUR MIN | |
| 6 | 214 | 24-Hour Maximum Temperature | **half** | 24-HOUR MAX | |

---

## Screen D — on-device position 18, slot [20] — 9 fields, layout variant 0

| Pos | ID | Name we recorded | Width *(530 est.)* | Rendered text on device | Same? |
|---|---|---|---|---|---|
| 0 | 36 | Power ← anchor, already known | full | | Y |
| 1 | 478 | EPOC ← already known, rename case | **half** | LOAD | |
| 2 | 294 | Resistance | **half** | RESISTANCE | Y |
| 3 | 654 | Segment Time | **half** | SEGMENT TIME | Y |
| 4 | 520 | Primary Target | **half** | No Label just 2 "--" in the DF | |
| 5 | 578 | Secondary Target | **half** | No Label just 2 "--" in the DF | |
| 6 | 302 | Step Distance | **half** | STEP DIST | |
| 7 | 21 | Lap %HRR | **half** |  LAP %HRR | Y |
| 8 | 438 | Lap Watts/kg | **half** | LAP W/KG | |

---

## Screen E — on-device position 19, slot [21] — 5 fields, layout variant 0

| Pos | ID | Name we recorded | Width *(530 est.)* | Rendered text on device | Same? |
|---|---|---|---|---|---|
| 0 | 95 | Odometer ← anchor, already known | full | | Y |
| 1 | 581 | Stamina | full | | Y |
| 2 | 580 | Potential | full | | Y |
| 3 | 582 | Estimated Distance | full | | Y |
| 4 | 583 | Estimated Time | full | | Y |

---

## Two specific questions, beyond the names

**1. Screen B's order.** 220 "Avg. Vertical Descent Speed" sits nowhere near
786/787/788, the other three of its family. Every ordering of Screen B still
puts 220 inside the VDS family, so that much is certain, but *which* of the
four it is rests on the fields having gone in as listed. If Screen B's four
VDS fields render their own names, that settles it outright.

**2. EPOC / Load — a decision, not a lookup.** `FIELD_ID_NAMES` is global
and holds one string per id, but 478 renders as "EPOC" on the 530 and the
840 calls it "Load". Same for 32 ("Next Pt Location" vs "Next Waypoint").
Three options, and this pass produces the evidence to choose:

- leave the 530 strings and note the 840 name in a comment (what is in place
  now — costs nothing, but the GUI picker shows an 840 user the wrong word)
- carry both, e.g. `"EPOC (840: Load)"` — honest, slightly ugly in the picker
- make display names per-model, like `MODEL_LAYOUTS` already is — correct,
  and a real change to every read path

Worth knowing how many ids actually diverge before picking. If it is two,
option one or two is fine. If this pass turns up fifteen, that is an argument
for the third, and the count is the thing that decides it.

