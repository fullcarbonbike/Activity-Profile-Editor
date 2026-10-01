# Edge 840 — Fields Not in the Edge 530 Census

**STATUS 2026-09-30: 6 of 41 resolved — Compass (529), Map (725), Smart
Travel Range (579), HR Zone Bar (= 23), 3s Power Bar (= 350) and 3s Power
Graph (= 346) — but the list GREW by 4 (the Stamina category), so **35**
are open, not 31. Not one of the six resolutions needed a screen built:
three were desk work, three were a scroll through the picker.**

## ⚠ The manual appendix is not a complete source

This checklist was built from the 840 manual's data-field appendix. On
2026-09-30 Doug found a whole **Stamina** category in the picker — four
fields — that the appendix does not list. So the appendix undercounts.

That cuts both ways, and both ways have now been demonstrated in a single
day: the appendix lists fields under names the picker does not use (three
struck as renames), and the picker holds fields the appendix omits (four
added). **The picker is the authority; the appendix was only a starting
point.**

Worth doing before the capture screens are built: walk the picker's
category headings top to bottom and compare the list of CATEGORIES
against this file's section headings. Finding a missing category costs one
scroll; finding it after the capture pull costs a whole second round
trip.

## ⚠ Check these in the picker BEFORE placing anything

The manual and the on-device picker do not use identical names. HR Zone
Bar was one; these may be more. Each is a pair where the manual's name
resembles something already known — **if the picker shows only ONE of
the two, it is a rename and the entry can be struck without placing
it.** If it shows both, they are genuinely separate and need capturing.

| Manual name | Possible existing match | Picker shows both? |
|---|---|---|
| ~~3s Power Bar~~ | **= 350** | rename — struck |
| ~~3s Power Graph~~ | **= 346** | rename — struck |
| Dist. to Point | Distance to Next (29) | |
| Time to Point | Time to Next (30) | |
| Trainer Controls | Trainer Resistance *(530's own open item)* | |
| Primary Target | Target (521) | |

Six entries, one scroll through the picker, no screens built. **Three are
already struck this way** — the method is paying for itself, so finish the
other three before building anything.

**Watch the category headings, not just the names.** The 840 groups the
picker by category and a field can appear under more than one heading:
"Power" is listed under **Power Graphical** alongside Power Bars and Power
Graph. That is almost certainly plain id 36 cross-listed, but it is not
proven, and it matters — see the anchor warning in
`FIELD_ID_BUILD_SHEET.md`.

**Not on this list, and worth saying so:** the 12-field **Force** family.
Force and Power are different quantities and the name similarity is
coincidental — treat those as genuinely new.

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
- [x] **HR Zone Bar** — **ID: 23, already known as "HR Zone Graph"** — RESOLVED
  2026-09-30 by Doug checking the picker: the device offers **HR Zone Graph**
  and no "HR Zone Bar". A manual-vs-device naming difference, not a new
  field. 23 is already in `FIELD_ID_NAMES` and in `GRAPH_OR_BARS_FIELD_IDS`.
- [x] **3s Power Bar** — **ID: 350, already known as "Power Bars"** — RESOLVED
  2026-09-30, Doug, two picker checks. First: no entry by the manual's
  name. Second, the deciding one: the Power Graphical category offers
  **Power, Power Bars, Power Graph** — the plain name IS present. So the
  manual's "3s " prefix is a naming difference, not a separate field;
  350 has been known from the 530 census all along. Likely the 530's
  field always WAS a 3-second average and the 840's manual simply names
  it more precisely.

- [x] **3s Power Graph** — **ID: 346, already known as "Power Graph"** — RESOLVED
  2026-09-30, Doug, two picker checks. First: no entry by the manual's
  name. Second, the deciding one: the Power Graphical category offers
  **Power, Power Bars, Power Graph** — the plain name IS present. So the
  manual's "3s " prefix is a naming difference, not a separate field;
  346 has been known from the 530 census all along. Likely the 530's
  field always WAS a 3-second average and the 840's manual simply names
  it more precisely.

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

## Stamina (4) — whole new category, and NOT from the manual appendix

Found 2026-09-30 by Doug reading the picker directly, not the manual.
None of the four is in `FIELD_ID_NAMES` (173 entries) and none was on
this checklist, because this checklist was built from the 840 manual's
data-field appendix and the appendix does not list them.

**Do not confuse these with the Stamina SCREEN**, `f10=127`, which is
already known and has its layouts measured (0/2A/2B/4/5/6). That is a
named screen type; these are four ordinary data fields in the picker,
placeable on any user screen. Two separate namespaces, same word.

- [ ] **Stamina** — ID: ____ — Current stamina remaining.
- [ ] **Potential** — ID: ____ — Stamina potential.
- [ ] **Estimated Distance** — ID: ____ — **NOT a rename of 27 "Distance
  to Destination" or 65 "Distance to Go"**, despite the name similarity.
  Those are course/navigation metrics; this is how much further you can
  go at current effort. Different quantity, needs its own id.
- [ ] **Estimated Time** — ID: ____ — Same caution against 28 "Time to
  Destination" and 68 "Time to Go".

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
