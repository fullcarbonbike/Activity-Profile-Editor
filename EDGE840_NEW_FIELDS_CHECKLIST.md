# Edge 840 — Fields Not in the Edge 530 Census

**STATUS 2026-09-30: 3 of 37 resolved — Compass (529), Map (725), Smart
Travel Range (579) — leaving 34 that need a device. Two of the three
needed no device at all.**

*Cross-referenced against the 530's 169-entry known-ID list and 185 unique
field names from the Edge 840 manual appendix. These 37 are the ones with
no corresponding entry on the 530 side — either genuinely new hardware/
firmware features, or renamed/restructured versions of something the 530
already has. Fill in ID # as you confirm each one on-device.*

## eBike (1)

- [x] **Smart Travel Range** — **ID: 579** — RESOLVED 2026-09-30, no device needed.
  Matched against positions already in the on-device notes for TWO screens:
  eBike Metrics `491, 579, 494, 56, 6` and STEPS Metrics `491, 579, 180, 494`.
  Both place 579 where "Smart Travel Range" was recorded, anchored by ids
  already independently confirmed. This checklist is what made the match
  possible -- the records existed, the name did not.

## Elevation — Vertical Descent Speed family (6)

*Parallel structure to VAM (which the 530 already has), but for descent rate. Worth checking if these exist on the 530 under firmware the manual just never documented.*

- [ ] **Vertical Descent Speed** — ID: ____ — The rate of descent over time.
- [ ] **Avg. Vertical Descent Speed** — ID: ____ — The average rate of descent.
- [ ] **30s Vertical Descent Speed** — ID: ____ — 30-second moving average rate of descent.
- [ ] **Lap Vertical Descent Speed** — ID: ____ — The rate of descent for the current lap.
- [ ] **Lap Ascent** — ID: ____ — The vertical distance of ascent for the current lap.
- [ ] **Lap Descent** — ID: ____ — The vertical distance of descent for the current lap.

## Force (12) — whole new category

*Pedal-platform force in Newtons. Likely tied to a newer force-sensor generation — may not exist on the 530 at all, but worth a quick check.*

- [ ] **Force** — ID: ____ — Current force applied to the pedal platforms.
- [ ] **Avg Force** — ID: ____
- [ ] **3s Force** — ID: ____
- [ ] **10s Force** — ID: ____
- [ ] **30s Force** — ID: ____
- [ ] **Lap Force** — ID: ____
- [ ] **Last Lap Force** — ID: ____
- [ ] **Max. Force** — ID: ____ — Top force for the activity.
- [ ] **Max. Lap Force** — ID: ____ — Top force for the current lap.
- [ ] **Normalized Force** — ID: ____
- [ ] **Lap Norm. Force** — ID: ____
- [ ] **Last Lap Norm. Force** — ID: ____

## Graphical (5)

- [x] **Compass** — **ID: 529** — CONFIRMED BY EXPERIMENT 2026-09-29, and the
  caveat is answered: it IS freely placeable on the 840. Placed in a
  half-width slot it renders as a miniature compass gauge, with no text
  fallback -- unlike the Graph/Bars family.
- [x] **Map** — **ID: 725** — CONFIRMED the same way on the same screen.
  Renders as a small live map area in a half-width slot.
- [ ] **HR Zone Bar** — ID: ____ — Bar-graph variant, parallel to the Bars cluster (347-350) already found on the 530, but for HR zone specifically.
- [ ] **3s Power Bar** — ID: ____
- [ ] **3s Power Graph** — ID: ____

## Heart Rate (1)

- [ ] **Load** — ID: ____ — Training load (EPOC-based). Distinct from the 530's plain EPOC field (478) — check whether it's a different display of the same underlying data or a genuinely separate field.

## Navigation (3)

- [ ] **Dist. to Point** — ID: ____ — Generic waypoint version, distinct from Course Pt. Distance (2) / Distance to Destination (27) already known.
- [ ] **Next Waypoint** — ID: ____
- [ ] **Time to Point** — ID: ____

## Temperature (2)

- [ ] **24-Hour Minimum Temperature** — ID: ____
- [ ] **24-Hour Maximum Temperature** — ID: ____

## Smart Trainer (1)

- [ ] **Trainer Controls** — ID: ____ — Possibly just the 840's name for the 530's still-open **Trainer Resistance**, not a separate field. Check whether the 840's picker shows both names or just this one before assuming it's new.

## Workouts (4)

- [ ] **Segment Time** — ID: ____ — Time racing a segment during the activity.
- [ ] **Primary Target** — ID: ____ — Possibly a split-out of the 530's generic "Target" (521).
- [ ] **Secondary Target** — ID: ____
- [ ] **Step Distance** — ID: ____ — Distance for the current workout step.

---

## Also still open (not 840-exclusive — carried over from the 530 census)

These two are genuinely unresolved on *both* devices, not new to the 840 — worth grabbing an ID while you're testing the 840 anyway, since it'd resolve the 530's gap too:

- [ ] **Lap %HRR**
- [ ] **Lap Watts/kg**

And the 530's own last open item, for reference: **Trainer Resistance** (see Trainer Controls note above — may turn out to be the same thing).
