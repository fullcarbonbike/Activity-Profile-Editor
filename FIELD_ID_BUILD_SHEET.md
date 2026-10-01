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

## Screen C — anchor **Heart Rate** + Graphical, Navigation, Temperature   (10)

| Slot | Field | ID found |
|---|---|---|
| 0 | **Heart Rate** *(anchor — id 13)* | 13 |
| 1 | Lap Descent | |
| 2 | ~~HR Zone Bar~~ **already known: id 23, "HR Zone Graph"** — skip, use a spare target here | |
| 3 | 3s Power Bar | |
| 4 | 3s Power Graph | |
| 5 | Dist. to Point | |
| 6 | Next Waypoint | |
| 7 | Time to Point | |
| 8 | 24-Hour Minimum Temperature | |
| 9 | 24-Hour Maximum Temperature | |

## Screen D — anchor **Power** + Workouts, Trainer, carried-over   (8)

| Slot | Field | ID found |
|---|---|---|
| 0 | **Power** *(anchor — id 36)* | 36 |
| 1 | Load | |
| 2 | Trainer Controls | |
| 3 | Segment Time | |
| 4 | Primary Target | |
| 5 | Secondary Target | |
| 6 | Step Distance | |
| 7 | Lap %HRR | |
| 8 | Lap Watts/kg | |

*(Screen D has 9 rows including the anchor; drop Lap Watts/kg to a fifth
screen if the device caps a screen at 8 for some layout you pick.)*

---

## Before you start — check the name-mismatch pairs first

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
