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

Two Garmin editors disagree about the same device:

- The **840's own on-device editor** offers Compass at 0, 1 or 2 fields.
- The **iPhone Garmin Connect app** shows Compass fixed at 2, greyed out
  -- the same limit the 530 has.

So "what Garmin's editor allows" is not a single authority. The app
appears to carry a conservative cross-device table; the device firmware
knows its own capability.

**Rule adopted: the device's own editor is the authority. The Connect
app is a second opinion that can be wrong.**

Important nuance, confirmed on-device 2026-09-28: the disagreement is
**type-specific, not blanket.** For USER-DEFINED screens the app and the
device agree exactly --

| Field count | Alternate layouts |
|---|---|
| 1, 2 | none |
| 3 through 9 | **A / B / C** |
| 10 | none |

-- which confirms the range Doc rev 120 took from the Connect app. It is
the NAMED types (Compass so far) where the app is more restrictive than
the hardware.

**Where this bites today:** the toolkit hard-locks Compass to 2 fields
as a fixed-2 type. On an 840 it therefore REFUSES an edit the device
itself offers. That is the first case where the global 530 table blocks
legitimate use rather than merely mislabelling something. eBike Metrics
(1-8 vs the table's 1-4) and STEPS Metrics (1-8) are the same shape but
are not locked, so they do not bite the same way.

---

## Phase 0 -- model identity

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

- [ ] `fit_dump.profile_model(path)` -- returns a model id/name, or
      `None` for an unrecognised product. Never raises.
- [ ] `KNOWN_MODELS` map, with a comment that an absent product means
      "unsurveyed", which is a real state and not an error.
- [ ] `SURVEYED_MODELS` -- the set whose layout rules have actually been
      measured. Currently the 530; the 840 joins it when Phase 3 lands.

**Verify**

- [ ] Returns 530 for every profile in `ClaudeCowork`, 840 for the three
      Census files.
- [ ] Returns `None` rather than raising on `Totals.fit` and
      `Device.fit`.

---

## Phase 1 -- stop refusing what the device permits

**This is the safety fix, and it is NOT the per-model tables.** It only
changes the posture from *"I know the rules"* to *"I know the 530's
rules."* Per Doc rev 120 SS4:

> Refuse only when the model is **known** AND the state is
> **known-illegal**. For an unsurveyed model, or a combination absent
> from that model's table: allow it, say plainly that it is unverified,
> and never rewrite what was not explicitly edited.

**Tasks**

- [ ] `count_is_locked()` locks only for the model the lock was measured
      on. Removes the Compass defect.
- [ ] Layout validation (`fit_patch.py`) refuses only when the model is
      surveyed AND the state is known-illegal; otherwise advise and
      write.
- [ ] v1.4.0's read-side "state the device doesn't offer" flag gates on
      model-surveyed, so it stops crying wolf on 840 profiles.
- [ ] GUI shows the model, and carries a one-line advisory when a
      profile's model is unsurveyed.

**Verify**

- [ ] 530 profiles: every existing refusal still fires. This is the
      regression that matters -- Phase 1 must not loosen the 530 path.
- [ ] 840 Compass accepts 0, 1 and 2 without a refusal.
- [ ] An 840 profile produces no read-side out-of-range flag.
- [ ] `fit_census.py` output unchanged (it does no validation, so any
      change here means something leaked).

---

## Phase 2 -- finish v1.5.0

Ordered deliberately: safety, then the feature that depends on Phase 1,
then the smaller piece, then release mechanics.

- [ ] **#142 -- device-dependent paths inert offline.** First because
      it is the safety item: today an offline session walks all the way
      to "Write to Device" before anything stops it. It refuses cleanly
      rather than tracebacking, so this is untidy rather than dangerous
      -- but it invites a real mistake.
- [ ] **#141 -- Export replaces Deploy offline.** Safe to build only
      after Phase 1, so its validation does not encode 530 rules into
      the one feature whose entire purpose is serving the 840.
- [ ] **#145 -- `startup.txt` offline import/export.**
- [ ] **#143 -- release mechanics.** Headless verification, version
      bumps, `RELEASE_NOTES_v1.5.0.md`, README changelog entry, State of
      play refresh.

**Verify:** `TEST_PLAN_v1.5.0.md` sections B through E, which are
currently blocked on exactly these three items. Section A already
passes in full.

---

## Phase 3 -- v1.6.0, per-model layout tables

Do NOT start this inside v1.5.0.

Keyed on Phase 0's model id, populated from the on-device notes below,
with an explicit "unsurveyed model" entry that is permissive by
construction.

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

Also outstanding, and cheap once the tables exist:
`NAMED_SCREEN_LAYOUTS` entries for Power Guide, Stamina, GroupRide and
Music Control. Stamina's 2-field layout renders STACKED where other
named types render side-by-side, so its grid needs care rather than
speed.

---

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
