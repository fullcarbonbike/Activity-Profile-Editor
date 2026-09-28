# Action plan -- moving the GUI forward with two device models

*Working document, like `TEST_PLAN_v1.5.0.md`. Meant to be edited as
things land, not preserved as history. The permanent record is
`PROJECT_NOTES.md`; this file is the worklist.*

*Written 2026-09-28, after Doc rev 123.*

---

## Where things stand

**Branch:** all work is on local `v1.5.0-wip`. `main` is clean at
`v1.4.0` / Doc rev 117 and nothing is pushed. Version strings are
deliberately NOT bumped -- in this project a bumped version means
shipped, so the mismatch between version and contents is the marker
that this is untested. The merge-and-tag procedure is written into
`PROJECT_NOTES.md` / State of play.

**Committed on the branch so far:**

| Commit | What |
|---|---|
| `ba5605b` | v1.5.0 offline mode, backend done, GUI half unbuilt |
| `0c16307` | `fit_census.py` + Doc rev 121 |
| `ce5758b` | Doc rev 122 -- A/B/C decoded, 3 new field IDs |
| `b9d4db4` | `f1` is the state, not `f9` -- classification + guard fix |
| `96a0108` | #146 -- the 840's screen types enter the code |
| `8921f06` | Withdraw the "Lights" name for `f10=64` |
| `23970ad` | Census3 -- `f10=30` is Music Control, reserve pool |
| `aea524b` | Doc rev 123 |

**Unbuilt in v1.5.0:** #141 Export, #142 device paths inert offline,
#145 `startup.txt` offline, #143 verify/docs/version bumps.

---

## The finding this plan is built around

The iPhone Garmin Connect app and the 840's own on-device editor
disagree about Compass: the device offers 0, 1 or 2 data fields, the app
shows the count greyed out and uneditable.

**First read (WRONG, recorded so it is not re-derived): "the app carries
a conservative cross-device table."** Two checks killed that:

1. Doug set Compass to 0 on-device. The app then DISPLAYS 0 correctly
   but still greys out the selector. So the app's READ path is
   model-accurate; only its edit-capability entry is wrong.
2. Cross-checking every other named type, the app agrees with the device
   exactly -- eBike Metrics at 1-8, Lap Summary's count-0 state, Segment
   4/C, all offered. A conservative table would have clamped those too.

So it is **one bad entry, not a policy** -- most likely device firmware
ahead of the app's revision, or simply an app bug.

**Rules adopted:**

- The **device's own editor is the authority.**
- The **Connect app is a usable survey instrument** -- much faster to
  enumerate options in than walking on-device menus -- **but confirm
  on-device anything that appears LOCKED**, since a greyed-out control
  is exactly where its one known failure mode lives. Everything it
  OFFERS has matched the device so far.

Confirmed on-device 2026-09-28, for USER-DEFINED screens, app and device
agreeing exactly:

| Field count | Alternate layouts |
|---|---|
| 1, 2 | none |
| 3 through 9 | **A / B / C** |
| 10 | none |

That confirms the range Doc rev 120 took from the app, which had been
flagged as needing on-device backing.

---

## What is actually broken today -- three classes

Checked against what `NAMED_SCREEN_LAYOUTS` and the guards actually
hold, not from memory.

**Class 1 -- the toolkit REFUSES what the 840 permits (hard blocks):**

| Type | 530 rule | 840 offers |
|---|---|---|
| **Compass (35)** | `[(2,0)]`, count LOCKED | 0, 1 or 2 |
| **Workout (38)** | in `NO_FIELD_EDIT_TYPES` -- no field editing at all | layout can't change, but scrolling reaches the fields and offers to change them |

**Class 2 -- validation range too narrow (refuses an edit; no symptom
until you make one):**

| Type | 530 table | 840 offers |
|---|---|---|
| **eBike Metrics (58)** | 1-4 | 1-8 -- and the 840 SHIPS it at 5, already outside the table |
| **STEPS Metrics (95)** | 1-4 | 1-8 |
| **Lap Summary (74)** | 1-4, no variants | 0, 1/A, 1/B, 2/A, 2/B, 3, 4 |
| **Segment (56)** | 0, 2, 4/A, 4/B, 6 | adds **4/C**, and 6 gains A/B |

**Class 3 -- no table entry at all, so they fall through to GENERIC
user-screen geometry:**

Power Guide (125, fixed 2), Music Control (30, fixed 2), GroupRide
(162, zero fields), Stamina (127, 0/2A/2B/4/5/6), plus 64, 128, 223.
Not a refusal -- the layout picker just offers the wrong shape, which
for a fixed-2 type means offering counts the device will not honour.

**Phase 1 below fixes classes 1 and 2. Class 3 needs actual table
entries -- no amount of loosening supplies a grid that is not there.**

---

## Who does what

Every task below is tagged. This was missing in the first draft and
caused exactly the confusion it should have prevented -- Doug read
Phase 0 as something to run and found no script to run it with.

- **[CODE]** -- Claude writes it. Nothing for Doug to do until it exists.
- **[BENCH]** -- Doug, on the device or in the Connect app. Cannot be
  done from a file, which is exactly why it is his.
- **[LAB]** -- Claude verifies it headlessly against files already on
  disk. No device, no GUI, nothing for Doug to run.
- **[GUI TEST]** -- Doug, running the app against real hardware. The
  build environment has no wx and no Edge attached, so this is the one
  kind of verification that CANNOT be automated here.

### So what does Doug actually do, start to finish?

Only two things. Everything else is mine.

1. **[BENCH]** -- look at the device or the app and report what it
   offers. Currently: the three lock checks below, and Segment 4/A/B/C.
2. **[GUI TEST]** -- run the app on hardware and work through
   `TEST_PLAN_v1.5.0.md`. That file is the live record; tick results
   there rather than relaying passes through chat.

If a step involves reading a `.fit` file, running a toolkit command
against one, or comparing bytes, it is **[LAB]** and it is mine -- even
when it is listed under "Verify". Doug never needs to synthesise test
files.

---

## Phase 0 -- model identity   **DONE 2026-09-28**

Small, headless, foundational. Everything below depends on it and
nothing else does.

`file_id.product` already distinguishes the models and is present in
every profile, so this needs no connected device and works on backups
and offline folders:

| Model | `file_id.product` |
|---|---|
| Edge 530 | 3121 |
| Edge 840 | 4062 |

**Tasks**

- [x] **[CODE]** `fit_dump.profile_model()` -- returns `(product_id,
      name)`, `(id, None)` for an unrecognised device, `(None, None)` if
      the file doesn't say. Never raises. Takes a path OR an
      already-decoded messages dict.
- [x] **[CODE]** `KNOWN_MODELS` = {3121: Edge 530, 4062: Edge 840}, and
      `SURVEYED_MODELS` = {3121} -- deliberately SEPARATE sets.
      Recognising a product id is not the same as knowing what that
      device's editor offers, and conflating the two is how a 530
      measurement came to be applied to an 840 in the first place.
- [x] **[CODE]** `model_label()` and `model_is_surveyed()`.
- [x] **[CODE]** `fit_dump.py screens` prints a **Device model:** line
      first, plus a NOTE when the model is unsurveyed. Doug's report:
      `screens` never said which device, and `dump` said it only amid
      everything else.
- [x] **[CODE]** `fit_census.py` gains a **model** column, so a whole
      folder of backups is attributable in one command.

**How to use it -- for Doug, whenever it is useful. Not a required step.**

One profile, with the model on the first line:

    python3 fit_dump.py screens <file.fit>

A whole folder, or several, in one pass:

    python3 fit_census.py <folder> [<folder> ...] --out models.csv

then read the `model` column. Files the toolkit doesn't recognise show
an empty `model` with the raw id still in `product` -- that id is what
to report so a new device can be added.

**[LAB] Verified 2026-09-28**

- [x] Sweep of `ClaudeCowork` + the Census uploads: 1178 records Edge
      530 (3121), 217 Edge 840 (4062), nothing unrecognised.
- [x] `screens` on an 840 profile prints the unsurveyed NOTE; on a 530
      profile it prints the model and no note.

---

## Phase 1 PREREQUISITE -- three bench checks   **DONE 2026-09-28**

Three types were count-LOCKED in the table on 530 evidence alone and had
never been checked on the 840. **All three confirmed LOCKED at 2 on the
840 as well** (Doug, 2026-09-28, checked on-device AND in the app):

- [x] **[BENCH] Elevation (44)** -- fixed 2 half-width fields at the
      bottom of the screen. App: layout selection greyed out, shows 2.
- [x] **[BENCH] Cycling Dynamics (63)** -- same.
- [x] **[BENCH] ClimbPro (104)** -- same.

**Result: NO new class-1 defects. Compass remains the only one.**

Two consequences, both good:

1. **Part B gets smaller.** These three agree with the 530, so the 840
   table needs NO entries for them -- it only carries the types that
   actually differ. An 840 entry that merely restates the 530's rule
   would be duplication waiting to drift.
2. **The "one bad app entry" reading is now supported by three negative
   controls.** The app was checked on all three and agrees with the
   device every time. So the app is not conservative about fixed-2 types
   in general -- it is wrong about Compass specifically.

That makes the coherent story: **840 firmware added variable field
counts to Compass, and the app's table predates that change.** The other
three fixed-2 types did not change, which is exactly why the app is
still right about them. Doug's firmware-ahead-of-app-revision hypothesis,
now with controls rather than a single observation.

---

## Phase 1 -- stop refusing what the device permits   **DONE 2026-09-28 (A and B)**

**This is the safety fix, and it is NOT the per-model tables.** It only
changes the posture from *"I know the rules"* to *"I know the 530's
rules."* Per Doc rev 120 SS4:

> Refuse only when the model is **known** AND the state is
> **known-illegal**. For an unsurveyed model, or a combination absent
> from that model's table: allow it, say plainly that it is unverified,
> and never rewrite what was not explicitly edited.

**Tasks -- part A, scope the existing rules to the model**

- [x] **[CODE]** `count_is_locked(f10, product)` locks only for a
      SURVEYED model. New `layout_rules_enforced(product)` carries the
      policy in one place.
- [x] **[CODE]** Layout validation (`fit_patch.py`) routes its four
      refusals through `_layout_problem()`: `parser.error` on a surveyed
      model, the SAME text to stderr as a NOTE otherwise.
- [x] **[CODE]** ~~`NO_FIELD_EDIT_TYPES` per-model~~ **DONE IN PART B,
      2026-09-28.** Blanket-loosening it for unsurveyed models would also
      unblock GroupTrack List (f10=57) and GroupRide (162) on the 840 --
      both device-generated with f3=0 -- re-opening the v0.21.2 bug where
      the field picker opened on a screen whose contents the device
      writes. That set is about "the device generates this screen", which
      is structural rather than a count rule, so it needs a per-model
      ENTRY (Workout differs on the 840) and not a policy switch.
- [x] **[CODE]** v1.4.0's read-side flag gates on model-surveyed.
- [x] **[CODE]** GUI shows "Profile written by: <model>" and, when
      unsurveyed, says plainly that it won't block what it doesn't
      recognise and that any warning shown came from a 530.

**Tasks -- part B, a FIRST 840 table (plan change, 2026-09-28)**

Part A alone leaves the 840 permissive-with-advisories, which means the
toolkit stops catching real mistakes on the device doing all the
research. Since the measurements already exist, populate them:

- [x] **[CODE]** An 840 entry carrying ONLY what has been personally measured --
      Compass 0/1/2, eBike Metrics 1-8, STEPS Metrics 1-8, Lap Summary's
      full set, Segment's known states, user screens A/B/C at 3-9.
      **Nothing inferred, nothing copied across from the 530 to fill a
      gap.** An absent entry must fall back to permissive, not to the
      530's rule.
- [x] **[CODE]** Class 3 entries for the types with no geometry at all: Power Guide
      (fixed 2), Music Control (fixed 2), GroupRide (0). **Stamina is
      deliberately EXCLUDED here** -- its 2-field layout renders STACKED
      where other named types render side-by-side, so its grid needs
      care rather than speed. It stays permissive until Phase 3.

This is Phase 3's shape arriving early for the types already known. It
is in scope because the data exists and the alternative is knowingly
shipping no validation for the 840; it is NOT licence to start
inferring per-model rules that have not been measured.

**Verify -- ALL [LAB], nothing here for Doug**

Every one of these runs against files already on disk. The "fake
product id" case is a copy of a real profile with two bytes patched by
a throwaway script -- a lab fixture, not something to create by hand.

- [x] **[LAB]** 530 profiles: every existing refusal still fires.
- [x] **[LAB]** 840 Compass accepts 1 field; 530 Compass still refused.
- [x] **[LAB]** 840 Workout allows field edits; 530 Workout still
      refuses them.
- [x] **[LAB]** 840 eBike Metrics accepts 7; refuses 9. 530 unchanged.
- [x] **[LAB]** An 840 profile produces no read-side out-of-range flag.
- [x] **[LAB]** Fake product id 9999 (a real 840 profile with two bytes
      patched and the CRC recomputed): refuses nothing, advises instead.
- [x] **[LAB]** `fit_census.py` output unchanged.

**Then, and only then, [GUI TEST] -- READY FOR DOUG NOW:** confirm on
real hardware that an 840 Compass screen can be edited to 0, 1 or 2
fields through the GUI and deployed, and that the layout picker offers
exactly those three. The lab checks prove the rules changed; only the
device proves the result renders.

---

## Phase 2 -- finish v1.5.0   **STATUS: blocked on Phase 1**

Ordered deliberately: safety, then the feature that depends on Phase 1,
then the smaller piece, then release mechanics.

- [ ] **[CODE] #142 -- device-dependent paths inert offline.** First because
      it is the safety item: today an offline session walks all the way
      to "Write to Device" before anything stops it. It refuses cleanly
      rather than tracebacking, so this is untidy rather than dangerous
      -- but it invites a real mistake.
- [ ] **[CODE] #141 -- Export replaces Deploy offline.** Safe to build only
      after Phase 1, so its validation does not encode 530 rules into
      the one feature whose entire purpose is serving the 840.
- [ ] **[CODE] #145 -- `startup.txt` offline import/export.**
- [ ] **[CODE] #143 -- release mechanics.** Headless verification, version
      bumps, `RELEASE_NOTES_v1.5.0.md`, README changelog entry, State of
      play refresh.

**Verify -- this phase is where Doug's testing lives.**

The four tasks above are [CODE]. What follows them is **[GUI TEST]**,
and it is the one kind of verification that cannot happen in the build
environment: no wx, no Edge attached.

- [ ] **[LAB]** Claude re-runs the headless checks first, so the GUI
      pass is not spent finding things a script would have caught.
- [ ] **[GUI TEST]** Doug works `TEST_PLAN_v1.5.0.md` sections B
      through E, which are currently BLOCKED on exactly the three
      unbuilt items above. Section A already passes in full.
- [ ] **[GUI TEST]** Record results in `TEST_PLAN_v1.5.0.md` itself --
      that file is the live record. Bring failures to chat; passes cost
      the same to relay and produce nothing actionable.

---

## Phase 3 -- v1.6.0, per-model layout tables   **STATUS: blocked on Segment 4/A/B/C [BENCH]**

Do NOT start this inside v1.5.0.

Phase 1 part B already lands the measured 840 entries, so this phase is
now COMPLETION rather than construction: the remaining types, Stamina's
stacked geometry, and whatever a third model turns out to need.

**Blocked on one measurement:** Segment's 4/A, 4/B and 4/C `f8` values
on the 840. The 530 INVERTS the mapping for Segment -- 4/A stores
`f8=2`, 4/B stores `f8=1`, backwards from every ordinary screen -- so
whether the 840 keeps the inversion decides whether letter-to-`f8` can
be stored per-type or has to be per-type-per-model. Nothing else
currently distinguishes those two designs.

**What is already measured, for the 840 column:**

| Type | 530 | 840 |
|---|---|---|
| User screens | A/B at 3-7 | **A/B/C at 3-9**, none at 1, 2, 10 |
| Compass (35) | LOCKED at 2 | 0, 1 or 2; default 2 (Speed, Distance) |
| eBike Metrics (58) | 1-4 | 1-8, no A/B/C |
| STEPS Metrics (95) | -- | 1-8, no A/B/C |
| Lap Summary (74) | 1-4, no variants | 0, 1/A, 1/B, 2/A, 2/B, 3, 4 |
| Segment (56) | 0, 2, 4/A, 4/B, 6 | 0, 2, 4/A, 4/B, **4/C**, 6/A, 6/B |
| Stamina (127) | -- | 0, 2/A, 2/B, 4, 5, 6 |
| Power Guide (125) | -- | fixed 2 |
| Music Control (30) | -- | fixed 2 |
| GroupRide (162) | -- | 0 fields |
| Map (25) | 0/A, 0/B, 1, 2 | identical |

## Open questions, none blocking

- **`f10=64`** -- "Lights" was named from field contents and withdrawn
  (Doc rev 123 SS3). Music turned out to be `f10=30`, killing the
  competing reading, so Lights is the only hypothesis left standing --
  which is not evidence. Naming it needs the 840's editor to actually
  offer the screen, which probably means paired lights.
- **`f10` 128 and 223** -- unnamed. 223 ships inactive on the 840 with
  five real fields; 128 has not been seen in a pulled profile at all.
- **Field ids 520, 578, 579** -- in `KNOWN_UNRESOLVED_IDS`. 520 and 578
  are Workout fields, 579 is eBike/drivetrain.
- **`f4`, `f6`, `f11`** -- three decoded-but-unexplained `mesg 14`
  fields, present on both models. `f11=2` appears only on INDOOR Map
  screens; whether it tracks the sport or the screen type is untested.
- **The inactive/removed split** rests on `f9`/`f10` surviving, which is
  an inference from two models. The 840's own Remove behaviour is
  untested.

---

## Standing disciplines, because they have each earned their place

- **The device is the author.** A profile file is evidence about a
  device only if the device wrote it. Set states in Garmin's editor,
  then pull and read.
- **Write down what you set, as you set it** -- count, menu letter,
  screen position. `f8` values are uninterpretable without it.
- **Give each screen a unique first data field**, so a dump can be
  matched to the notes even if display order shifts.
- **Build screens up rather than shrinking them**; shrinking leaves
  stale ids in `f7`'s trailing slots. Only the first `f3` entries are
  real.
- **Doc revs are superseded, never rewritten** once committed.
- **No personal ride statistics** in `PROJECT_NOTES.md` or `README.md`
  -- the repo is public.
- **No provenance in user-facing strings.**
