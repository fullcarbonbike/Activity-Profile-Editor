# Field-ID capture — build sheet

*Four user screens in one profile, one pull, 34 unknown field IDs.
Generated 2026-09-30 from `EDGE840_NEW_FIELDS_CHECKLIST.md`.*

---

## The one safeguard that matters

The 2026-08-17 batch went wrong through a **screen transposition** — 20
field names mapped to the wrong screens' IDs, caught only by dropping to
raw bytes afterwards. With 34 fields across 4 screens the same risk
applies, and two things here defend against it:

**1. Slot 0 of every screen is a KNOWN anchor field, different on each
screen.** It costs four slots and makes transposition impossible to miss
— if the anchors come back in the wrong order, we know immediately and
exactly what happened.

**2. Screens are grouped BY CATEGORY.** A category is self-identifying:
if a screen comes back holding twelve IDs where Force was expected, and
they're contiguous, that corroborates independently of the anchor.

Belt and braces, because this is the one step in the project with a
prior failure.

---

## Screen A — anchor **Speed** + Force, part 1   (10 fields)

| Slot | Field | ID found |
|---|---|---|
| 0 | **Speed** *(anchor — id 48, already known)* | 48 |
| 1 | Force | |
| 2 | Avg Force | |
| 3 | 3s Force | |
| 4 | 10s Force | |
| 5 | 30s Force | |
| 6 | Lap Force | |
| 7 | Last Lap Force | |
| 8 | Max. Force | |
| 9 | Max. Lap Force | |

## Screen B — anchor **Cadence** + Force part 2 + Vertical Descent   (9)

| Slot | Field | ID found |
|---|---|---|
| 0 | **Cadence** *(anchor — id 3)* | 3 |
| 1 | Normalized Force | |
| 2 | Lap Norm. Force | |
| 3 | Last Lap Norm. Force | |
| 4 | Vertical Descent Speed | |
| 5 | Avg. Vertical Descent Speed | |
| 6 | 30s Vertical Descent Speed | |
| 7 | Lap Vertical Descent Speed | |
| 8 | Lap Ascent | |

## Screen C — anchor **Heart Rate** + Navigation, Temperature   (7)

**This screen has been renumbered TWICE — use the table below, not any
copy you wrote down earlier.** Three of its original targets came off
during Step 0: HR Zone Bar (= id 23 "HR Zone Graph"), and 3s Power Bar
and 3s Power Graph, neither of which the 840's picker offers under those
names. It is 7 fields now, down from 10, and the Graphical category is
gone from it entirely.

| Slot | Field | ID found |
|---|---|---|
| 0 | **Heart Rate** *(anchor — id 13)* | 13 |
| 1 | Lap Descent | |
| 2 | Dist. to Point | |
| 3 | Next Waypoint | |
| 4 | Time to Point | |
| 5 | 24-Hour Minimum Temperature | |
| 6 | 24-Hour Maximum Temperature | |

Slots 2 and 4 are still on the Step 0 list. If those also fall, Screen C
is down to four fields and should be merged into Screen D rather than
built on its own.

## Screen D — anchor **Power** + Workouts, Trainer, carried-over   (8)

| Slot | Field | ID found |
|---|---|---|
| 0 | **Power** *(anchor — id 36)* — **pick from the plain Power category, NOT Power Graphical** (see warning below) | 36 |
| 1 | Load | |
| 2 | Trainer Controls | |
| 3 | Segment Time | |
| 4 | Primary Target | |
| 5 | Secondary Target | |
| 6 | Step Distance | |
| 7 | Lap %HRR | |
| 8 | Lap Watts/kg | |

*(Screen D has 9 rows including the anchor; drop Lap Watts/kg to Screen E
if the device caps a screen at 8 for some layout you pick.)*

## Screen E — anchor **Odometer** + Stamina   (5)

Added 2026-09-30. The Stamina category was not in the manual appendix and
so was not in the original four screens — Doug found it in the picker.

Kept as its own screen rather than appended to C or D, because the sheet's
second safeguard is that a screen's category is self-identifying: four
contiguous unknown ids under a Stamina anchor corroborate each other even
if the anchor itself were somehow wrong.

| Slot | Field | ID found |
|---|---|---|
| 0 | **Odometer** *(anchor — id 95)* | 95 |
| 1 | Stamina | |
| 2 | Potential | |
| 3 | Estimated Distance | |
| 4 | Estimated Time | |

**Anchor choice is deliberate:** Odometer (95), not Timer (56). 56 is
`DEFAULT_FILLER_FIELD_ID` — the toolkit stamps it into slots when a layout
change grows a screen — so a 56 appearing in a pull is ambiguous between
"the anchor Doug placed" and "filler the device or toolkit added". An
anchor has to be unambiguous or it is not an anchor.

**These four are NOT the Stamina screen.** `f10=127` is a named screen
type, already known, layouts already measured. These are ordinary data
fields that happen to share the word. Place them on a plain user screen.

---

## ⚠ Screen D's anchor — pick it from the right category

Doug found that the **Power Graphical** category lists **Power** as well as
Power Bars and Power Graph. That is probably plain id 36 cross-listed under
a second heading, which Garmin does, **but it has not been proven**, and
the whole point of an anchor is that its id is not in question.

If that entry turns out to be a distinct graphical-power field, Screen D's
anchor would come back as an unknown id — and an anchor whose value is
unknown cannot detect a transposition, which is the one thing it is there
for. The safeguard would fail silently, exactly as the per-model feature
once shipped inert.

**So pick Power from the plain Power category.** Cheap, and it keeps the
anchor an anchor.

(Worth capturing separately: if the Graphical "Power" is in fact a distinct
field, it is a 32nd unknown nobody has counted. Placing it somewhere other
than slot 0 would settle that. Not required for this pull.)

## Step 0 — check the name-mismatch pairs first

`EDGE840_NEW_FIELDS_CHECKLIST.md` now lists six manual names that
resemble something already known. One scroll through the picker tells
you whether each is a rename or a real field, and anything that turns
out to be a rename comes off the sheet before you build a single screen.

HR Zone Bar already went that way: the device offers **HR Zone Graph**,
which is id 23 and has been known all along.

## Before you start

- **Place them in the order listed.** The mapping is read positionally,
  so order is the data.
- **Use a scratch profile**, not one you ride with. It needs 4 new user
  screens and they'll be numbered after your existing ones.
- **Layout: pick a plain user-screen count that matches** (10, 9, 10, 8
  or thereabouts). Any layout works — the IDs are in `f7` regardless of
  how they're arranged.

## If a field isn't in the picker

**That is data, not a failure.** Note it as "not offered" and move on.
Two likely reasons, and the distinction matters:

- **Hardware-gated in the picker** — no power meter with force sensing,
  no eBike, no smart trainer. The field exists but can't be placed.
- **Not on this firmware at all** — the manual documents a model
  variant or a later build.

Either way, leave its row blank and note which. A field the 840 won't
offer is worth recording as such, since it bounds what the toolkit can
ever place.

The **Force** category (12 fields) is the most likely to be
hardware-gated in bulk — it reads like a newer force-sensor generation.
If none of them appear, that answers the whole category at once and
Screen A becomes nearly empty, which is fine.

## After

Pull the profile once and send it. With the anchors in place I can map
all four screens in a single pass and say definitively whether anything
transposed.
