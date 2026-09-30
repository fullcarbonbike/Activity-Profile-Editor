# Action plan — v1.6.0 and beyond

*Working document. Edit as things land; it is the worklist, not the
history. `PROJECT_NOTES.md` is the permanent record — if the two
disagree, the newest Doc rev wins and this file is stale.*

*Rewritten 2026-09-30, after v1.5.0 shipped. Supersedes the v1.5.0 plan
entirely; Phases 0–2 of that plan are done and tagged.*

---

## Read this first if you're picking the project up cold

**Shipped:** `v1.5.0`, tagged and pushed 2026-09-29. `fit_dump` 2.10.0,
`fit_patch` 1.18.0, `gui_app` 0.23.0, `garmin_device` 0.13.0,
`fit_census` 1.1.0. Docs at PROJECT_NOTES rev 127, README Changelog
rev 80.

**Hardware:** Edge **530** (USB mass storage, the regression baseline)
and Edge **840** (MTP, no mass-storage mode). The 840 is why offline
mode and Export exist.

**The one idea that shapes everything now:** layout rules are **per
model**, and they cannot be derived. Segment stores different `f8`
values on the two devices for the same screen type, the same visible
layout and the same field geometry. Measurement is the only source.

**The posture that follows from it:** refuse only when the model is
known AND the state is known-illegal. For an unmeasured model or
combination, allow it, say it's unverified, and never rewrite what
wasn't explicitly edited. `fit_dump.model_rule_known()` is where that
decision lives.

---

## Who does what

- **[CODE]** — written by Claude. Nothing for Doug until it exists.
- **[BENCH]** — Doug, on the device or in the Connect app. Cannot be
  done from a file, which is exactly why it's his.
- **[LAB]** — Claude verifies headlessly against files on disk. No
  device, no GUI.
- **[GUI TEST]** — Doug, running the app on real hardware. The only
  verification that can't be automated; there's no wx in the build
  environment and no Edge attached.

**Doug only ever does [BENCH] and [GUI TEST].** Anything that reads a
`.fit`, runs a toolkit command or compares bytes is [LAB] — even under
a heading called "Verify".

---

## Phase A — complete the per-model tables   **the v1.6.0 core**

Phase 1B of the last plan landed the measured 840 entries early, so
this is **completion, not construction.**

### A1. Finish the 840 entry   [BENCH] then [CODE]

Deliberately absent from `MODEL_LAYOUTS[4062]` today, because their
A/B/C → `f8` mapping is unknown and the 530 proves it can't be guessed:

- [ ] **[BENCH] Lap Summary (74)** — 840 offers 0, 1/A, 1/B, 2/A, 2/B,
      3, 4. Counts known, `f8` values for the B variants unknown.
- [ ] **[BENCH] Stamina (127)** — 840 offers 0, 2/A, 2/B, 4, 5, 6.
- [ ] **[CODE]** Add both once measured. **A partial entry is worse
      than none** — it makes `model_rule_known()` return True and starts
      refusing legal states. That's why Segment was held out until every
      state was measured.

**Method, proven on Segment:** set each variant in Garmin's own editor
across several profiles, pull them in one session, read `f8` from the
stored bytes. One profile holds only one of each named type, so each
variant needs its own file. **Record what each one LOOKS like, not just
its menu letter** — the letter is what's under test, so it can't also be
the evidence. That's what settled Segment when a plausible hypothesis
was wrong.

### A2. Stamina's geometry is the awkward one   [CODE]

Stamina's 2-field layout renders **stacked** where every other named
type renders side by side. `NAMED_SCREEN_LAYOUTS`' grid model assumes
rows of positions, so this may not be expressible as-is. Decide whether
the grid model needs a vertical/horizontal flag before writing the
entry, rather than forcing it.

### A3. Consider whether `grids` should stay global   [CODE]

Doc rev 125 found that **geometry travels between models while variant
numbering doesn't** — the 840's Segment grids are identical to the
530's. So the per-model dimension may only be needed on `states`, not
on `grids`. Confirm across more types before committing to that shape;
if it holds, the refactor is half the size it looks.

---

## Phase B — the 840 picture is really a ROAD picture   [BENCH] + [LAB]

Doc rev 123 recorded `f10=128` as "not yet seen in a pulled profile". It
had been there all along — in the factory **INDOOR** profile, not Road,
which is all the census had ever been pointed at.

**So a screen type can be per-SPORT as well as per-model**, and "we
surveyed the 840" is currently overstated.

- [ ] **[LAB]** Census the INDOOR and MOUNTAIN factory profiles already
      in `Test4`: `python3 fit_census.py <folder> --summary`. Costs
      nothing; they're on disk.
- [ ] **[BENCH]** If either holds types or states Road never showed,
      walk that profile's Screens menu the way the Road one was walked.

---

## Phase C — the field-ID census   [BENCH] then [CODE]

Current state, measured 2026-09-29:

```
FIELD_ID_NAMES holds          : 172 names
Unnamed ids actually IN USE   : 3  (520, 578, 579)
530 profiles: 87 distinct ids, 84 named
840 profiles: 35 distinct ids, 32 named
```

There is **no backlog from what has been pulled**. The gap is between
what the table knows and what the 840 *offers*, and only the manual can
size that.

- [ ] **[BENCH]** List the data field names the 840's manual documents.
- [ ] **[LAB]** Subtract the 172 known names — that difference is the
      real scoping number.
- [ ] **[BENCH]** Place-and-pull the remainder in **small batches**.
- [ ] **[CODE]** Add confirmed ids; move any that resist to
      `KNOWN_UNRESOLVED_IDS`.

**The 2026-08-17 lesson applies hard here.** That batch went wrong
through a screen transposition and had to be unpicked from raw bytes.
So: small batches, a **unique first data field per screen**, and written
notes of what went where *before* pulling.

**Shortcut worth trying:** Garmin's ID space is grouped — the Power
Phase family landed contiguously, as did the eBike cluster (491, 494,
579). Placing a few from each category the manual lists will likely
reveal neighbours by proximity.

Known unresolved, with what's been narrowed:
- **520, 578** — on the 840's Workout screen, alongside 522 Duration
  and 511 Workout Comparison.
- **579** — on both STEPS Metrics and eBike Metrics, between 491 Assist
  Mode and 494 Travel Range. An eBike/drivetrain field.

---

## Phase D — named screen types still unidentified   [BENCH]

- [ ] **`f10=64`** — carries 316 "Lights Connected" and 319 "Light
      Mode". Named "Lights" once and **withdrawn**: field contents are a
      stamped template, not proof of identity, and the 840's Screens
      menu offers no Lights entry. Census3 killed the competing Music
      reading (Music is `f10=30`), leaving Lights as the only hypothesis
      standing — **which is not evidence.** Naming it needs the editor
      to actually offer the screen, i.e. paired lights.
- [ ] **`f10=128`** — factory INDOOR profile, inactive, `f3=2` holding
      Speed and Distance. See Phase B.

### D1. The activation experiment   [BENCH] — file already built

Doug's idea, 2026-09-30, and it reaches something nothing else does:
**force the unknown types ACTIVE and let the device say what they are.**

`CyclingIndoor_CycleF10TEST.fit` is built and waiting in the working
folder. It is the factory INDOOR profile — the only one holding all
three unknowns — cloned to the display name `F10TEST`, with slots 8
(`f10=64`), 14 (`f10=128`) and 19 (`f10=223`) set to `f1=1`, `f12=0`
and non-colliding `f9` values of 57/58/59, so they land as the LAST
three screens and disturb nothing above them.

Identify them on-device by content, in scroll order after Power Guide:

| Position | `f10` | Fields |
|---|---|---|
| 12th | 64 | Lights Connected, Light Mode |
| 13th | 128 | Speed, Distance |
| 14th | 223 | Timer, Speed, Distance, Grade, Time of Day |

**Method note:** `--un-remove` was retired in v1.13.0, so there is no
CLI path to set `f1=1`. `patch_screen()` takes a raw `def_num -> bytes`
dict and writes it directly — the retired flag was a convenience, not
the capability.

**What each outcome tells us:**

- **They appear and render** — the types are identified, and the
  toolkit can reach screens Garmin's own editor won't offer.
- **They appear in the editor but render blank** — they are real types
  NOT explained. See Phase E -- the "waiting on hardware" reading was
  falsified on 2026-09-30.
- **The device erases them on import** — then the purge that took
  `f10=64` out of Census3 is about the TYPE, not the `f1` state, which
  explains the 64-survives-223 asymmetry differently and is worth
  knowing on its own.

All three are findings. There is no wasted outcome.

**Caveats.** The filename is new, so the device may create a new profile
or may ignore it — NewFiles is confirmed to RECREATE a deleted profile
but creating one that never existed is untested. If it is ignored, fall
back to replacing a profile that can be restored from backup. And pull
the profile back afterwards either way: whether the records survived is
half the result.
- [x] ~~**`f10=223`**~~ **= RADAR, identified 2026-09-30** (Doc rev 128).
      States 0, 5/A, 5/B; A and B swap which side the radar strip sits
      on. In the code with no `grids` entry -- it is a column layout and
      the grid model describes rows.
- [ ] **`f10=26` Virtual Partner** is 530-only. Kept in the global table
      and in the 840's no-field-edit set deliberately: a 530 profile can
      be deployed to an 840, so an 840 session can still meet the
      record.

---

## Phase E — open questions, none blocking

- **The device erases some reserve records on import — and it is NOT
  about hardware.** A NewFiles import wiped `f10=64` and the
  user-Removed record while `f10=223`, in the identical state,
  survived. The obvious reading was that the device rebuilds the
  reserve pool from what the hardware supports.

  **That reading is FALSIFIED (2026-09-30).** Radar (`f10=223`) was
  forced active and the 840's editor listed it **with no Varia radar
  paired at all** — so the editor reads the RECORD, not the hardware.
  And in the same profile `f10=64` and `f10=128` were forced active
  the same way and did NOT appear.

  So the pattern holds by TYPE across both experiments: 223 survives,
  64 does not, now with 128 alongside it. Whatever the device is doing,
  it is keyed on `f10` rather than on `f1` or on paired hardware.

  Peculiar, and worth stating plainly: **the 840 shipped 64 and 128 in
  its own factory profiles**, so the device wrote records it then
  strips on import. A firmware that carries types its current build
  does not expose would explain it, but nothing tests that yet.

  **RESOLVED 2026-09-30 (Doc rev 128 §4).** `F10TEST` was pulled back:
  slots 8 (`f10=64`) and 14 (`f10=128`) came back **erased, every field
  `0xFF`**, while slot 19 (Radar) returned byte for byte. Only those two
  records differ.

  So the strip is keyed on **`f10` type** — not `f1` (all three were
  active), not hardware (no radar paired, Radar kept), not `f9` (all
  three clean). Consistent with Census3, where 223 survived at `f1=0`
  and 64 was erased: two experiments, same answer, opposite `f1` states.

  What remains unexplained is why the 840 ships 64 and 128 in its own
  factory profiles and then strips them. **Naming those two now needs a
  different route entirely** — they cannot be reached by activation.
- **The inactive/removed split is provisional.** It rests on `f9`/`f10`
  surviving, inferred from two models; the 840's own Remove behaviour
  has never been tested.
- **`f4`, `f6`, `f11`** — three `mesg 14` fields present on both models
  and never decoded. `f4` reads `1..10` on factory screens and `255` on
  any screen added later, even by Garmin's own editor. `f11` is `1`
  almost everywhere and `2` on exactly the INDOOR Map screens. Whether
  `f11` tracks the sport or the screen type is untested.
- **Named-screen appearance is EDITOR PREVIEW, not live rendering.**
  Everything recorded about what Segment, ClimbPro, Workout and
  GroupTrack look like comes from the editor's static mock. Not
  load-bearing — `f8` values are stored bytes and field geometry is
  identical across variants — but it should not be read as a sighting.

---

## Phase F — carried over, unbuilt

- [ ] **#106 odometer** (`Totals.fit`). Substantially de-risked: a
      hand-modified file was written via `NewFiles/` over MTP and
      accepted, the format is confirmed by writing, and the device does
      not rewrite totals on import. Still unbuilt. Note what the format
      *cannot* hold: no ascent, descent, speed, heart rate, cadence or
      power — four of Garmin Connect's twenty columns have anywhere to
      go, and any feature should say so rather than implying a fuller
      restore.
- [ ] **Cross-device profile check** — the other half of the serial
      work. Serial-keyed backups shipped in v1.5.0; warning when a
      profile meets a device it didn't come from did not. Decide
      nudge-vs-warning wording from a real cross-model test; note a
      cross-model deploy has already succeeded (FLDTEST, a 530 profile,
      onto the 840), so it is not automatically wrong.
- [ ] **`save_working_dir()` read-modify-write** — latent bug, no longer
      a prerequisite for anything after the backup layout changed. Worth
      fixing on its own merits.

---

## Standing disciplines — each one earned its place

**Evidence**

- **The device is the author.** A profile file is evidence about a
  device only if the device wrote it. Set states in Garmin's editor,
  then pull and read.
- **Write down what you set, as you set it** — count, menu letter,
  screen position. `f8` values are uninterpretable without it.
- **When a label is what you're testing, anchor on something the label
  can't contaminate.** Matching Segment variants by appearance rather
  than menu letter is what proved a confident hypothesis wrong.
- **Only the first `f3` entries of `f7` are real**; the rest are stale
  ids from an earlier shrink. Reading trailing slots as content is how
  the 2026-08-17 batch went wrong.
- For undocumented FIT messages trust `fit_raw_walk.parse_fit()`, not
  the garmin-fit-sdk decoder.

**Verification**

- **Structural checks beat exercising paths.** A static audit over
  every handler found three gaps that reading the code had not; a sizer
  check caught four buttons that would have been invisible. Exercising
  the paths you thought of finds only what you already thought of.
- **When a change can't be exercised in the build environment, "it
  works" is a HYPOTHESIS until hardware says otherwise — say so.** The
  per-model feature shipped inert for a day because twelve passing CLI
  tests were treated as covering the GUI.
- **Checking a feature EXISTS is not checking it's REACHABLE** from the
  state the user is actually in. This has now happened twice.

**Code**

- **A mode-dependent change to a reused widget needs a matching restore
  in the other mode, written at the same time.** Panels are reused
  across modes; anything set in one persists into the other.
- **Wrap at the point of display, not at each append** — or better, use
  a widget that can't widen its parent. The window-width bug has seven
  occurrences.
- **Omission is meaningful** in `MODEL_LAYOUTS`: a type absent from a
  model's entry is unenforced, not governed by the 530's rule. That is
  what lets the table hold only measured facts.

**Documentation**

- Doc revs are **superseded, never rewritten** once committed. Check
  `git log` before amending a recent rev.
- **No personal ride statistics** in `PROJECT_NOTES.md` or `README.md` —
  the repo is public.
- **No provenance in user-facing strings.** A dialog says what will
  happen and why it matters; the test, date and hardware go in the
  code comment beside it.

---

## Release procedure

1. Finish and test on hardware.
2. Bump the `__version__` strings; write `RELEASE_NOTES_vX.Y.Z.md`; add
   the README `## Changelog` entry; refresh PROJECT_NOTES State of play.
3. Work on a branch; `main` stays at the last release until tested.
4. `git checkout main && git merge <branch>` (fast-forward if `main`
   hasn't moved).
5. **Tag on `main`, never on the branch**, and use `-a` or `-F` —
   `git push --follow-tags` skips lightweight tags silently, which is
   how v1.3.0 ended up with no tag message.
6. `git push origin main --follow-tags`, then `git branch -d <branch>`.
