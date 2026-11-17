# Test plan — #171 step 1, writing `sub_sport` into a cloned profile

*2026-11-06. This is the gate identified in `SCOPE_171_sub_sport.md`
section 7: **mesg 12 field 1 has never been written by this project.**
Nothing is built yet — `CyclingGRAVEL.fit` was hand-patched, which is
how #106 and #170 were both de-risked.*

Device: **Edge 840** (MTP only — OpenMTP, no device mode, no
DeployPanel/Check).

---

## The file

`CyclingGRAVEL.fit`, built from Doug's `CyclingRoadROAD-e1813fe5.fit`.

| | |
|---|---|
| size | 5307 bytes — unchanged |
| md5 | `6f1007f11fa3…` (source `6c6487e96ea5…`) |
| bytes changed | 8, and only 8 |

Verified before handover:

```
name      258..289   32-byte null-padded   'ROAD' -> 'GRAVEL'      5 bytes
sub_sport 295        1 byte                7      -> 46            1 byte
CRC       5305..5306 recomputed, validates                          2 bytes
elsewhere                                                           0 bytes
```

- `sport` (f0) left at **2** deliberately — it is 2 on all 68 profiles
  in the corpus and nothing suggests it should move (scope §6)
- colour (f10) `0044f8` inherited, untouched
- all **31** `data_screen` records byte-identical, `message_index`
  included
- mesg 170 Connect IQ record identical: uuid `c7c508c8…`,
  `placements [(0, 2), (4, 0)]`

## ⚠ Before you start

1. **Back up the existing `GRAVEL` profile off the 840** — this test
   replaces it. (Doug said he would; restating because there is no
   undo.)
2. Back up `Totals.fit` too. The `GRAVEL` totals record is keyed by
   profile **name**, which is not changing, so it should be untouched
   — but step 3 is the first time anything has written `sub_sport`,
   and the cheap backup covers the case where that assumption is
   wrong.

**Why the name is `GRAVEL` and not something new.** A profile the
device has not seen gets its `message_index` renumbered on import
(rev 192); a replacement does not. Matching is by display name. The
Connect IQ placements in mesg 170 encode **screen slot indices**, so
renumbering would misalign them. Naming it `GRAVEL` makes this a
replacement and sidesteps that.

> **⚠ Correction, 2026-11-07.** An earlier version of this paragraph
> called misaligned CIQ placements "the one thing that has
> historically broken on a clone". **That was stale.** The CIQ failure
> was early-project, before mesg 170 was understood; the maintenance
> path built in #123–#128 fixed it, and cloning has worked for toolkit
> users since. Replacing rather than creating was still the right
> call — it avoids renumbering for free — but it was not rescuing a
> known-fragile path, and describing it that way made a routine pass
> look like a narrow escape. Doc rev 204.

The cost of that choice: this test does **not** exercise the
new-profile path. That is a separate test, and worth doing only after
this one passes.

## ⚠ What this test canNOT show — added 2026-11-07

Three fresh templates pulled off the 840 (`COMMUTE`, `TOUR`,
`EMOUNTAIN`) proved that **the device's templates differ by ride
type** — Doc rev 206. A native `EMOUNTAIN` gets Grit, Flow, Assist
Mode and Smart Travel Range; a native `TOUR` gets Distance to Next and
an extra enabled screen.

So this profile is `ROAD`'s screens wearing Gravel's type. **It is not
what the device would have built for Gravel**, and no amount of
on-device checking will make it so. That is the intended outcome here
— keeping `ROAD`'s screens is the point — but it means **step 4's
pass condition is "same as ROAD", never "same as a native GRAVEL"**.

Doug, 2026-11-07: *"In my case I wasn't worried about it nor did I
need a Gravel specific screen/data field."* Noted, and it is why the
finding became a **warning in the picker** rather than a blocker on
the feature.

## The steps

*ALL TEN STEPS PASS — completed 2026-11-09. Doc rev 212.*

| # | do | pass condition | status |
|---|---|---|---|
| 1 | copy `CyclingGRAVEL.fit` to `Garmin/NewFiles/` on the 840, restart | device boots normally, no error | **PASS** |
| 2 | open the profile list | `GRAVEL` present, exactly one of it | **PASS** |
| 3 | check the profile's type in its settings | reads as **Gravel**, not Road — *this is the whole question* | **PASS** |
| 4 | page through its data screens | same 17 configured screens as `ROAD`, same fields, same order | **PASS** |
| 5 | **Screen 1 position 3 and Screen 6 position 1** | the Connect IQ field renders **its app**, not a fallback to Timer | **PASS** — both |
| 6 | check the Odometer field | shows the `GRAVEL` total, not `ROAD`'s, not zero | **PASS** — 0.00, correct for this profile |
| 7 | pull the profile back off the device and diff | `sub_sport` still 46 — the device kept it rather than overwriting | **PASS**, with three device-side changes — Doc rev 209 |
| 8 | one ride on `GRAVEL` | — | **DONE** |
| 9 | Garmin Connect → Goals, the gravel-bike battery goal | the ride counts against **Gravel Cycling**, not Road Cycling | **PASS** — Reports and Goals both, after a delay |
| 10 | pull `Totals.fit`, compare to the backup | ride in the `GRAVEL` record and record 0, nothing else moved | **PASS** — +98 m identical in both |

**Step 7 passed, but the device did not return our file unchanged** —
208 bytes differ. It **relocated five screens** to different
`message_index` slots (identities, field arrays and display order all
preserved, so nothing changed for the rider), **reassigned the profile
colour** `0044f8` → `a800f8`, and **updated mesg 170 itself** to
follow the Connect IQ screen it had moved, `(4,0)` → `(5,0)`.

The last of those is the good news: the firmware repairs CIQ
placements across its own reorganisation. The first contradicts
rev 192 — a *replacement* was renumbered, which that rev's rule says
should not happen. See Doc rev 209; the open question is whether the
trigger is the `sub_sport` write or the model.

**Step 6 passed in a slightly stronger form than written.** The
`GRAVEL` odometer reads 0.00, and `fit_dump` confirms all four fields
of its `totals` record are zero. The pass condition said "not
`ROAD`'s, not zero" — but `GRAVEL` on this device has genuinely never
been ridden, so **zero IS the correct value**, and the thing actually
established is that the write did not inherit `ROAD`'s total. The
condition as written was wrong about this device; the result is right.

**Step 10's baselines are in place** — three genuine 840 pulls now
sit in `baselines/`: 2026-11-06, after the three template profiles
were created, and after a road ride. All three are device pulls, so
the rev 202 baseline rule is satisfied whichever pair gets compared.

### What is left

**Steps 8, 9 and 10 — one ride on the gravel bike with the `GRAVEL`
profile active, then the Connect Goals check.** Everything the device
can show has now been shown; step 9 is the only remaining question
that decides whether to build the feature, because Connect honouring
`sub_sport` is what Doug's battery goals depend on.

### A cheap side experiment — corrected 2026-11-07

**An earlier version of this section proposed the wrong test.** It
suggested a replacement with *only the display name changed*, to
isolate the `sub_sport` write. That is incoherent: matching is **by
display name**, so changing the name is exactly what makes a profile
NEW rather than a replacement. The test could not have isolated
anything.

**The test that works needs no patching at all:** copy the
`CyclingGRAVEL.fit` just pulled off the 840 **straight back** into
`Garmin/NewFiles/` and restart. The device is handed its own file, so
there is nothing to get wrong.

It also tests a hypothesis rev 209 did not consider. The file we sent
carried **`ROAD`'s** slot arrangement — gaps at 12 and 15, content at
20 and 21. The device may rebuild whenever the incoming arrangement
differs from the one it already holds for that profile, mapping the
screens onto its own structure. **That would explain `qqtest` coming
back byte-identical**: `ROAD_T1` was replaced by an edited copy of
*itself*, so the arrangement already matched.

| result | conclusion |
|---|---|
| **byte-identical** | the device reorganises only when the incoming arrangement differs from what it holds; the `sub_sport` write is **not** the trigger |
| **relocates again** | arrangement is not the cause either, and something keeps provoking a rebuild |

### ✅ RESULT, 2026-11-08: byte-identical

Same md5 in and out. **The arrangement is the trigger**, and
`sub_sport` was never a candidate — the 840's existing `GRAVEL`
already carried 46, so from the device's side that field never
changed. Doc rev 210 has the rule that replaces rev 192's, and it
accounts for all seven observations with one mechanism.

Nothing here blocks step 9; the remaining question is still only
whether Connect honours `sub_sport`.

## What each step actually decides

**Steps 1–2** — whether the device accepts a file with a written
`sub_sport` at all. It could reject the import outright. This is the
cheapest possible failure and the reason the file is hand-patched
rather than a built feature.

**Step 3** is the gate. If it reads Road, the field is display-only
or the device recomputes it from something else, and `--sub-sport`
is not worth building.

**Steps 4–5** — whether changing an identity field disturbed the
screens. Expected not: screens are keyed on f10, not sport. "Should
be unaffected" is doing real work in that sentence, hence the check.
Step 5 is the specific risk — if the CIQ field falls back to Timer,
mesg 170 came adrift despite the byte-identical placements, and that
is worth knowing on its own.

**Step 7** matters because the device treats some fields as its own
(`message_index` being the precedent). Accepting a write and
*keeping* it are different claims.

**Step 9 matters more than it looks.** Per the scope: *"The device
accepting the write and Connect honouring it are different claims,
and Doug's battery goals depend on the second."* Connect's Goals page
filters on top-level sport plus sub_sport, so this is the step that
tests the thing the feature is actually for. "The profile says Gravel
on the device" would not establish it.

**Step 10** confirms the odometer is still keyed on name and the
sub_sport change did not reroute it.

## If it passes

Build `--sub-sport gravel_cycling` on `fit_clone_profile.py` — SDK
names only, vetted cycling list, never a side effect of a name
change, and it announces the type change in its output. Scope §6 and
§7 step 4.

## If step 3 fails

Restore the backed-up `GRAVEL` profile and close #171. The odometer
motivation was already solved by profile name, so there is nothing
left to salvage — the feature's whole value was the Connect
categorisation.

## Rollback

Copy the backed-up original `CyclingGRAVEL.fit` to
`Garmin/NewFiles/` and restart. Same name, so it replaces rather than
duplicates. `Totals.fit` from backup if step 10 shows it moved.
