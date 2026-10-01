# Edge 840 — Fields Not in the Edge 530 Census

**STATUS 2026-09-30: ALL 41 RESOLVED — Compass (529), Map (725), Smart
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

## ✅ COMPLETE — 2026-09-30, one pull

`CyclingRoadCensus4.fit`, five user screens, **33 new field ids in a single
pull**, plus 2 resolved as renames of already-known ids and 6 resolved
earlier without touching the device. `FIELD_ID_NAMES` 173 → **206**.
`KNOWN_UNRESOLVED_IDS` is **empty** for the first time since it was
repopulated — 520 and 578 are Primary Target and Secondary Target.

**No transposition.** All five anchors came back correct and in order
(48 Speed, 3 Cadence, 13 Heart Rate, 36 Power, 95 Odometer). The 2026-08-17
batch needed a raw-byte dump to discover its screens had swapped; this one
was verifiable on sight.

### Corroboration that does not depend on placement order

Within-screen mapping is positional, so it rests on the fields having gone
in as listed — the anchors cannot catch a within-screen slip. Four pieces
of independent evidence matter more than the anchors here:

1. **520/578 appear on the device's OWN Workout screen** in this same
   profile, beside 522 Duration and 511 Workout Comparison. Primary and
   Secondary Target is exactly what belongs there, and Doug never edited
   that record. This is the strongest single result in the batch: those two
   ids had been the only entries in `KNOWN_UNRESOLVED_IDS`.
2. **223 Lap Ascent / 224 Lap Descent are adjacent, from DIFFERENT
   screens** (B and C) — so the pairing is not an artifact of one screen's
   ordering. Mirrors 60/61 Total Ascent/Descent.
3. **438 Lap Watts/kg lands inside the W/kg numeric block**: 98 base,
   159 30s, **438 Lap**, 439 3s, 440 10s.
4. **580-583 contiguous for the four Stamina fields; 847-854 contiguous
   for eight of the Force family.** Categories are self-identifying, which
   was the build sheet's second safeguard.

### ⚠ One anomaly, and one naming decision

**220 "Avg. Vertical Descent Speed" sits nowhere near 786/787/788**, the
other three of its family. Every permutation of Screen B's order still
places 220 inside the VDS family, so 220 IS one of those four; *which* one
rests on placement order alone. **Worth one confirmation that Screen B went
in as listed.** Recorded rather than smoothed over.

**The Force family was not hardware-gated.** All 12 appeared, falsifying
the build sheet's own guess that they needed a newer force sensor. Same
correction applies to Trainer Controls: it appeared with no smart trainer
paired, so the long-standing hypothesis that the 530's "Trainer
Resistance" needed a paired FE-C trainer to show in the picker is **not
supported** — at least not on the 840.

### Display text is provisional for several entries

This dict's convention is the on-device DISPLAY label, not the manual's
name, and most of these names came from the manual. "24-Hour Minimum
Temperature" is far too long to be what a data field actually renders. The
ids are solid; the strings need a pass with the GUI picker open beside the
device.

**294 is the one that was confirmed**, and it is the clearest example of
why: the picker MENU says "Trainer Controls", but Doug reports the rendered
field says **"Resistance"**. Stored as "Resistance".

---

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

- [x] **Vertical Descent Speed** — **ID: 786** — The rate of descent over time.
- [x] **Avg. Vertical Descent Speed** — **ID: 220 ⚠ see anomaly note below** — The average rate of descent.
- [x] **30s Vertical Descent Speed** — **ID: 787** — 30-second moving average rate of descent.
- [x] **Lap Vertical Descent Speed** — **ID: 788** — The rate of descent for the current lap.
- [x] **Lap Ascent** — **ID: 223** — The vertical distance of ascent for the current lap.
- [x] **Lap Descent** — **ID: 224** — The vertical distance of descent for the current lap.

## Force (12) — whole new category

*Pedal-platform force in Newtons. Likely tied to a newer force-sensor generation — may not exist on the 530 at all, but worth a quick check.*

- [x] **Force** — **ID: 860** — Current force applied to the pedal platforms.
- [x] **Avg Force** — **ID: 847**
- [x] **3s Force** — **ID: 851**
- [x] **10s Force** — **ID: 852**
- [x] **30s Force** — **ID: 853**
- [x] **Lap Force** — **ID: 848**
- [x] **Last Lap Force** — **ID: 854**
- [x] **Max. Force** — **ID: 849** — Top force for the activity.
- [x] **Max. Lap Force** — **ID: 850** — Top force for the current lap.
- [x] **Normalized Force** — **ID: 856**
- [x] **Lap Norm. Force** — **ID: 857**
- [x] **Last Lap Norm. Force** — **ID: 858**

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

- [x] **Load** — **ID: **478, already known as "EPOC"** — RENAME; Garmin renamed EPOC to Load** — Training load (EPOC-based). Distinct from the 530's plain EPOC field (478) — check whether it's a different display of the same underlying data or a genuinely separate field.

## Navigation (3)

- [x] **Dist. to Point** — **ID: 595** — Generic waypoint version, distinct from Course Pt. Distance (2) / Distance to Destination (27) already known.
- [x] **Next Waypoint** — **ID: **32, already known as "Next Pt Location"** — RENAME, nothing new**
- [x] **Time to Point** — **ID: 596**

## Temperature (2)

- [x] **24-Hour Minimum Temperature** — **ID: 215 (display text unconfirmed)**
- [x] **24-Hour Maximum Temperature** — **ID: 214 (display text unconfirmed)**

## Smart Trainer (1)

- [x] **Trainer Controls** — **ID: 294 — stored as **"Resistance"**, the rendered label** — Possibly just the 840's name for the 530's still-open **Trainer Resistance**, not a separate field. Check whether the 840's picker shows both names or just this one before assuming it's new.

## Stamina (4) — whole new category, and NOT from the manual appendix

Found 2026-09-30 by Doug reading the picker directly, not the manual.
None of the four is in `FIELD_ID_NAMES` (173 entries) and none was on
this checklist, because this checklist was built from the 840 manual's
data-field appendix and the appendix does not list them.

**Do not confuse these with the Stamina SCREEN**, `f10=127`, which is
already known and has its layouts measured (0/2A/2B/4/5/6). That is a
named screen type; these are four ordinary data fields in the picker,
placeable on any user screen. Two separate namespaces, same word.

- [x] **Stamina** — **ID: 581** — Current stamina remaining.
- [x] **Potential** — **ID: 580** — Stamina potential.
- [x] **Estimated Distance** — **ID: 582** — **NOT a rename of 27 "Distance
  to Destination" or 65 "Distance to Go"**, despite the name similarity.
  Those are course/navigation metrics; this is how much further you can
  go at current effort. Different quantity, needs its own id.
- [x] **Estimated Time** — **ID: 583** — Same caution against 28 "Time to
  Destination" and 68 "Time to Go".

## Workouts (4)

- [x] **Segment Time** — **ID: 654** — Time racing a segment during the activity.
- [x] **Primary Target** — **ID: 520 ← was KNOWN_UNRESOLVED** — Possibly a split-out of the 530's generic "Target" (521).
- [x] **Secondary Target** — **ID: 578 ← was KNOWN_UNRESOLVED**
- [x] **Step Distance** — **ID: 302** — Distance for the current workout step.

---

## Also still open (not 840-exclusive — carried over from the 530 census)

These two are genuinely unresolved on *both* devices, not new to the 840 — worth grabbing an ID while you're testing the 840 anyway, since it'd resolve the 530's gap too:

- [x] **Lap %HRR** — **ID: 21**
- [x] **Lap Watts/kg** — **ID: 438**

And the 530's own last open item, for reference: **Trainer Resistance** (see Trainer Controls note above — may turn out to be the same thing).
