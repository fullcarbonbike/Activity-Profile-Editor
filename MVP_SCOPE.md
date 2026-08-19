# MVP Scope — Garmin Edge 530 Screen Editor GUI

*Doc rev 16 — refreshed 2026-08-15. **"Reduce redundant profile
backups" BUILT, Doug's go-ahead (low priority).** `ProfileListPanel`
no longer calls `garmin_device.backup_profiles()` -- a real device
read/write of every profile -- on every ordinary visit to the profile
list; a new frame-level `needs_backup` flag (set by a fresh Detect or
a confirmed post-deploy reconnect) gates the real backup call, and the
"Refresh (re-backup + re-list)" button still always forces one
regardless of the flag. Quality-of-life fix, not a new capability --
contained entirely to `gui_app.py` (now v0.19.1), no scope change to
any feature in the table below. See `PROJECT_NOTES.md` doc rev 46 for
the full writeup. Prior rev (15, 2026-08-15) follows.*

*Doc rev 15 — refreshed 2026-08-15. **"Restore a profile that's no
longer on the device" is now BUILT, Doug's go-ahead.** See the
"Restore from backup" section below for the full writeup — built
exactly to Doug's own 2026-08-11 design decision (second list in
`ProfileListPanel`, no new button/panel), reusing the existing
`RestorePanel`/`DeployPanel` pipeline unchanged. `garmin_device.py`
now v0.12.2, `gui_app.py` now v0.19.0. See `PROJECT_NOTES.md` doc rev
45 for the technical detail. Prior rev (14, 2026-08-14) follows.*

*Doc rev 14 — refreshed 2026-08-14. **"Startup message (startup.txt)"
is now BUILT end to end, Doug's go-ahead.** Both real open questions
this feature was waiting on (exact on-device path, write mechanism)
are RESOLVED via Doug's own real Edge 530, not secondary sources alone
— see the new "Startup message (startup.txt)" section below for the
full writeup, and `PROJECT_NOTES.md` doc rev 42 for the technical
detail. `garmin_device.py` now v0.12.0, `gui_app.py` now v0.18.0.
Prior rev (13, 2026-08-14) follows.*

*Doc rev 13 — refreshed 2026-08-14. **"Remove a screen" is now
COMPLETE end to end, GUI included.** "Remove Selected Screen" built on
the GUI's Screens view (`gui_app.py` v0.17.0), Doug's go-ahead —
backend, real device test, and GUI wrapper are all done. See
PROJECT_NOTES.md Open Items ("Delete Screen") for the full build
history. Prior rev (12, 2026-08-14) follows.*

*Doc rev 12 — refreshed 2026-08-14. **"Remove a screen" is now
CONFIRMED via a real on-device round-trip test** (Doug) — the target
screen was correctly removed from the on-device order, and the removed
screen was wiped by NewFiles rather than surviving as recoverable,
matching `--un-remove`'s own retirement reasoning. `fit_patch.py` now
v1.14.1. Both backend build steps (headless verification, then this
device test) are done — the GUI wrapper is now unblocked but stays
unbuilt until asked for. See PROJECT_NOTES.md Open Items ("Delete
Screen") and `FIT_PATCH.md` doc rev 19. Prior rev (11, 2026-08-14)
follows.*

*Doc rev 11 — refreshed 2026-08-14. **"Remove a screen" backend is now
BUILT** — `--remove`/`remove_screen()` (`fit_patch.py` v1.14.0),
headless-verified against a real profile (correct state transition,
guards block exactly as designed, valid CRC), but NOT YET verified on
real hardware, so the GUI wrapper stays deliberately unbuilt per the
two-phase discipline. See PROJECT_NOTES.md Open Items ("Delete Screen")
and `FIT_PATCH.md` doc rev 18 for the full writeup. Prior rev (10,
2026-08-13) summary follows.*

*Doc rev 10 — refreshed 2026-08-13. **`--un-remove` RETIRED entirely**
(Doug's decision, `fit_patch.py` now v1.13.0) — Restore-from-Backup
already covers real recovery from an accidental delete at the
whole-profile level, `--un-remove` had a confirmed historical
device-side data-loss hazard never re-verified after its fix, and
Garmin's own editor has no un-remove workflow either. Also noted:
"Remove a screen" was scoped this same day as "Delete Screen" (see
PROJECT_NOTES.md Open Items) — it will be a deliberately one-way
operation by design, no un-remove counterpart. See PROJECT_NOTES.md
"Product note on `--un-remove`" for the full history. Prior rev (9,
2026-08-06) summary follows.*

*Doc rev 9 — refreshed 2026-08-06. **Clone Profile is now built in the
GUI** (`ClonePanel`, `gui_app.py` v0.16.0) — patches
`sport_mesgs[0].name` via the already CLI-validated
`fit_clone_profile.py`, with live filename-collision checking, and
hands off to the same Deploy pipeline Restore uses. Headless-verified
(filename validation, structurally-identical clone output, zero
screen differences); not yet confirmed through the actual GUI on real
hardware. **This was the last item in the GUI feature backlog — the
full 10-step flow plus Restore-from-Backup and Clone Profile are now
all built.** See `PROJECT_NOTES.md` / "Clone Profile" for the full
writeup.*

*Prior rev (8, 2026-08-06): the full 10-step GUI flow plus
Restore-from-Backup was DONE: Deploy/eject/remount (`DeployPanel`,
v0.13.0), post-write verification (v0.14.0), and the Restore-from-
Backup picker (`RestorePanel`, v0.15.0) all built and headless-tested
that pass, with Deploy + the change summary + Fields-column fix
already CONFIRMED live on real hardware (2026-08-06).*

*Prior rev (7, 2026-08-05): **MAJOR REVERSAL: adding a brand-new
screen via `fit_patch.py --new-slot` is now CONFIRMED WORKING**,
root-caused as an f10 identity collision (not a NewFiles delivery-
mechanism limitation as previously documented) and fixed in
`fit_patch.py` v1.12.0 — CONFIRMED via live on-device round-trip,
2026-08-05. This moves "Add a brand-new screen" from excluded to a
real MVP feature; see the updated feature table and writeup below, and
`FIT_PATCH.md`/`PROJECT_NOTES.md` for the technical detail.*

*Prior rev (6, 2026-08-04): Restore-from-backup validated on real
hardware; confirmed hard caps (10 fields/screen, 10 user
screens/profile) added. Corrected the conditional/system-screen
exclusion's rationale — screen TYPE identity is now solved via field
10 (see `PROJECT_NOTES.md`), so that's no longer why they're excluded;
the real reason is that most don't have anything meaningful to edit.*

Companion to `PROJECT_NOTES.md` (technical findings). This document
scopes what a first GUI version should actually do, and — just as
importantly — what it deliberately shouldn't, yet.

## Why this is worth building

Real, current, repeated complaints from Edge 530 owners on Garmin's
own forums confirm this gap is genuine and unaddressed:

> "It is quite infuriating trying to change screen order and field
> order etc from the device... this is an absurd hole in Garmin's
> product offering. They've heard about it for years and don't choose
> to put effort into it."
> — Edge 530 forum, *any way to manage screen & data fields with the
> app or computer?*

> "It would be great to be able to edit the data screens and fields in
> Garmin Connect and then sync the settings to the Edge... I believe
> that's how the Wahoo computers work."
> — Edge 1030 forum, *Feature Request - data screen editing*

A related existing tool ("Edit Edge Data" for macOS) edits FIT-stored
odometer/settings values on Edge devices but **explicitly does not
touch Data Screens at all** — confirming nobody's built this specific
piece yet.

**The single most-named specific complaint in the forum threads
searched was screen and field *reordering*** — which is fully
validated end-to-end on real hardware. Good alignment between what's
proven and what's actually wanted.

---

## MVP feature set

Every item below maps to an already-validated `fit_patch.py` /
`fit_chain.py` / `fit_clone_profile.py` capability — nothing in this
list requires new reverse-engineering to implement, only UI.

| Feature | Backing capability | Status |
|---|---|---|
| View all screens, true on-device order, with field lists | `fit_dump.py screens` | Done (CLI) |
| Edit a screen's field list / field count | `--fields` | **Fully validated on-device, both directions** — same-count content replace AND a genuine field-count increase (Slot 7, 4→6 fields, original 4 preserved + 2 appended, correct layout) |
| Reorder fields within a screen | `--swap-fields` | Validated on-device |
| Toggle layout A/B (where valid) | `--layout` (guarded) | Validated on-device, byte-for-byte confirmed |
| Show / Hide a screen | `--enable`/`--disable` (aliases `--show`/`--hide`, matching on-device wording exactly) | Validated on-device, byte-for-byte confirmed |
| Reorder screens | `--swap-order` | Validated on-device — **the most-requested forum feature** |
| Batch several edits before one device write | `fit_chain.py` | Validated: byte-identical to manual step-by-step chaining, clean failure on a bad step, confirmed on real hardware end-to-end |
| Clone a profile under a new name | `fit_clone_profile.py` + `garmin_device.py deploy` under a new filename | **DONE, GUI + CLI both** — CLI-level validated on real hardware (full-fidelity clone, all screens/content/order/layout preserved, source profile untouched), and `gui_app.py` v0.16.0's `ClonePanel` builds the picker: new display name + auto-suggested filename with live collision checking against every profile on the device, handing off straight to the same Deploy flow Restore uses. Headless-verified (filename validation, structurally-identical clone output via `describe_screen_changes()`); GUI's own real-hardware pass not yet done. |
| Restore a profile from a previous backup | `garmin_device.py`'s existing deploy pipeline, sourced from an old backup file instead of a patched one | **DONE, GUI + CLI both** — validated on real hardware (an old backup deployed cleanly through the standard write/eject/remount pipeline and restored the profile's previous state), and `gui_app.py` v0.15.0's `RestorePanel` builds the picker: per-profile backup history (`garmin_device.py` v0.11.0's `list_backup_history()`, de-duplicated) with a plain-English screen summary per candidate, handing off straight to the same Deploy/verify flow as a normal edit |
| Add a brand-new screen | `--new-slot` (f10 auto-assigned via `next_available_field10()`) | **CONFIRMED WORKING end to end** — CLI level (v1.12.0, live on-device round-trip 2026-08-05), and GUI panel (`gui_app.py` v0.8.0, `AddScreenPanel`) CONFIRMED live through the actual widgets on real hardware the same day — see below. |
| Remove a screen | `--remove` (`fit_patch.py` v1.14.1) + "Remove Selected Screen" (`gui_app.py` v0.17.0, `ViewScreensPanel`) | COMPLETE 2026-08-14 — backend, real on-device round-trip test (target screen correctly removed, wiped by NewFiles rather than surviving as recoverable), and GUI wrapper are all done. GUI reuses `--remove`'s exact two guards (Map/ClimbPro block, last-visible-user-screen floor) with no override, plus an explicit permanent-deletion confirmation. Deliberately ONE-WAY write (no un-remove counterpart at all, by design — `--un-remove` was retired the same day, see below) |

**Adding a new screen via file writes is now CONFIRMED WORKING — this
reverses what had been a settled, root-caused conclusion.** The
original "always fails" diagnosis was made before field 10 (f10) was
understood. Every prior failing test had `--new-slot` fall back to its
old default of f10=0 — and f10=0 turns out to be a real, specific
identity ("Screen 1"), not an inert sentinel. Almost every real profile
already has a Screen 1, so the synthetic addition was colliding with
an existing screen's identity, and the device's NewFiles reconciliation
merged/discarded on that collision — a content problem, not a delivery-
mechanism one as previously believed. `fit_patch.py` v1.12.0 auto-
assigns a collision-free f10 by default (`next_available_field10()`);
tested live on `CyclingRoadSandbox`, a new screen (fields Gears/Front
Gear) survived the full NewFiles restart cycle intact, independently
re-confirmed against the live mounted device by both `fit_dump.py` and
`garmin_device.py`. **MVP design, updated:** the GUI should offer a
real Add-New-Screen panel (pick an unconfigured slot, set fields/
layout, let the tool auto-assign f9/f10) rather than redirecting the
user to the on-device menu. Caveat carried forward: any NewFiles
deploy purges the profile's entire Removed-screen list regardless of
what it targets (unrelated, already-known behavior — see Screen State
Model). `--un-remove` itself was RETIRED entirely (2026-08-13, `fit_patch.py`
v1.13.0) before its own live round-trip re-verification ever happened
— see PROJECT_NOTES.md "Product note on `--un-remove`" for why
(Restore-from-Backup already covers real recovery, a confirmed
historical data-loss hazard was never re-verified, Garmin's own editor
has no un-remove workflow either).

**Save workflow, by necessity, is two steps — this needs to be a
first-class part of the UI design, not an afterthought:**

1. App writes the (possibly multi-step-chained) patched file into the
   mounted device's `NewFiles` folder (fully automatable — plain file
   copy to a mounted USB volume, one write per session regardless of
   how many edits were queued).
2. App tells the user to safely eject and restart the device — the
   NewFiles import only happens on the device's own boot sequence,
   and needs one power-button press after the restart finishes before
   it remounts (see `PROJECT_NOTES.md` — write path). Nothing on the
   computer side can trigger or skip either step.

The UI should have an explicit "waiting for you to restart the
device" state, and automatically verify the change actually landed
after reconnecting (re-read the profile, diff against what was sent)
rather than leaving that as a manual afterthought.

---

## Explicitly excluded from MVP

| Feature | Why |
|---|---|
| **"Un-remove" a screen** | Leaning toward never offering this as a first-class feature, decision deferred rather than final. Garmin's own on-device editor has no un-remove option at all — the only workflow it exposes is Hide (temporary) or Remove + Add New (permanent) — and the fact that a factory-shipped profile's Removed list already contains a few entries the user never touched suggests Garmin itself may not have distinguished "Removed" from "Unconfigured" as deliberately as this project has had to. `fit_patch.py --un-remove` exists in the code (fixed in v1.12.0 alongside `--new-slot`, not yet re-tested live) purely to keep the door open for future experimentation, not because there's a real product need for it. Earlier version caused real, unwanted data loss on an *unrelated* screen during a live test — a data point for staying cautious even once re-verified. |
| **Editing conditional/system screens directly** (Map, GroupTrack, ClimbPro's own content, etc.) | Their TYPE identity is now solved (field 10, confirmed 2026-08-04 — see `PROJECT_NOTES.md`), but what it would even mean to meaningfully edit most of them still isn't understood: Map has no on-device toggle at all, ClimbPro/GroupTrack's real controls live outside `data_screen` entirely, and several (Virtual Partner, GroupTrack's Conditional record) have no editable field list to begin with. Kept out of MVP on those grounds, not on the identity problem that originally motivated this exclusion. |
| **Anything touching the still-unresolved screen-count cap trigger** | Real eviction risk observed once already (silent loss of an unrelated screen); root cause not yet isolated. |
| **Toggling Segments/ClimbPro/other profile-wide settings** | `mesg_num=13` is only ~1/40 mapped (just the Segments toggle so far; ClimbPro's toggle turned out to live in a different message, `training_settings_mesgs`). Not enough understood to expose safely yet. |
| **Multi-device / Garmin Connect sync** | What the forum posters actually *want* long-term, but far out of scope — this project works against a single mounted device's files directly. |
| **Automatic backup retention/pruning** | Backups will accumulate indefinitely with no cleanup. Not a real problem yet at these file sizes, but a future age-based cutoff (e.g. auto-delete backups older than 30 days) is worth adding once real usage patterns are clear. Manual cleanup works fine for MVP. |

---

## Restore from backup — in scope for MVP, DONE (GUI + CLI, real hardware validated)

Added after recognizing that "edit and regret it" needs an easy way
back, and that it's nearly free to support: a restore is functionally
identical to a normal deploy, just sourced from an old backup file
instead of a freshly patched one. No new toolkit capability was
required for the deploy mechanics — `garmin_device.py`'s existing
write/verify/eject/remount pipeline handled it exactly as-is,
confirmed by deploying an old backup and getting the previous profile
state back on the device.

- **DONE**: presented as a sibling action to editing right at profile
  selection (not buried in a menu) — "Restore from Backup..." on
  `ProfileListPanel`, enabled the moment a profile is selected, same
  as "Stage Selected for Edit."
- **DONE**: the GUI lists a given profile's backups specifically via
  `garmin_device.py`'s new `list_backup_history()` (filtered from the
  timestamped backup folders down to that one filename, de-duplicated
  so an untouched profile's identical repeat backups collapse to one
  entry), with a plain-English screen-type summary per candidate (via
  `classify_screens()`/`screen_type_name()`, the same functions
  `ViewScreensPanel` uses) so the user isn't guessing "which one was
  before I broke it" from a bare timestamp.
- **Satisfied by construction, no extra logic needed**: before
  restoring, the current (about-to-be-overwritten) on-device state is
  already backed up — `ProfileListPanel` re-backs-up unconditionally
  every time it's shown, which always happens right before a user
  reaches the restore picker, so that state is already the newest
  entry in the very history list being restored from. A restore is
  therefore always itself undoable, with no extra code required to
  guarantee it.
- `RestorePanel` hands off straight to `DeployPanel` (skipping
  `PreflightPanel`'s staged-vs-editing diff, which doesn't apply here)
  — reusing the exact same write/eject/reconnect/post-write-verify
  pipeline as a normal edit, unchanged.
- **DONE (v0.19.0, Doug's go-ahead, 2026-08-15): restoring a profile
  that's no longer on the device at all**, not just replacing a live
  one. First raised by an external GitHub user report (2026-08-11) —
  a deleted profile vanished from `ProfileListPanel`'s list, so it
  could never be selected for restore even though its backup history
  was untouched under `working_dir/backups/`. Built exactly to Doug's
  own 2026-08-11 design decision: `ProfileListPanel` gets a SECOND,
  separate list ("Deleted, but available to restore"), sourced from a
  new `garmin_device.list_backed_up_profile_filenames()` (v0.12.2)
  minus what's currently live — no new button, no new panel, the
  existing "Restore from Backup..." button and `RestorePanel` work
  unchanged from either list. `RestorePanel`'s confirmation now says
  "RECREATING" rather than "REPLACING" when the target isn't currently
  on the device. The one real technical risk — whether `NewFiles` can
  recreate a filename that isn't currently present in `Sports/`, not
  just replace an existing one — was confirmed via a direct on-device
  test back on 2026-08-11, so this GUI build carried no new backend
  risk. **CONFIRMED via Doug's own real GUI test (2026-08-15):** a
  deliberately-deleted profile correctly appeared in the "Deleted, but
  available to restore" list, and restoring it worked cleanly end to
  end — the last remaining gap (real widget behavior, untestable in
  the dev sandbox) is now closed.

---

## Clone-and-retarget — built and validated (moved out of "post-MVP candidate")

This was scoped as a good post-MVP candidate and has since been built
and **confirmed working end-to-end on real hardware**:

- Profile display name lives in `sport_mesgs[0].name` (standard,
  SDK-recognized message — not `data_screen` at all). `sport`/
  `sub_sport` (activity type) correctly carry over untouched.
- Workflow: stage a backup copy → `fit_clone_profile.py --name
  "NewName"` → `garmin_device.py deploy` under a **new** filename
  (one that doesn't match any existing profile).
- Result confirmed on real hardware: the original source profile is
  completely untouched, the on-device editor treats the clone as a
  genuine, independent, editable profile, and the donor backup and
  the live on-device result are screen-for-screen identical (all
  reorderable and conditional slots, same content, order, layout,
  flags) — a full-fidelity clone, nothing lost or altered.
- This directly solves the original pain point that motivated the
  idea in the first place: cloning an existing bike's profile and
  adjusting just the differences, instead of manually rebuilding every
  screen from scratch for a new one.
- Why it succeeded even before `--new-slot` was fixed: consistent with
  the now-confirmed root cause (an f10 identity collision, not a
  delivery-mechanism issue) — a clone under a brand-new profile
  filename has no prior on-device state to collide against at all, so
  even the old f10=0 default couldn't collide with anything.
  `--new-slot`'s failures were specifically about writing into an
  *existing* profile that already had its own "Screen 1" (f10=0);
  see `FIT_PATCH.md` BUGS for the full corrected diagnosis.

**DONE (`gui_app.py` v0.16.0, `ClonePanel`)** — the "expose in the
GUI" decision above is resolved: built as a sibling action to Stage/
Restore on `ProfileListPanel` ("Clone..."), not held for a fast-follow.
New display name + auto-suggested filename, live collision-checked
against every profile currently on the device (the one real risk
here — deploying under an existing filename silently overwrites it
instead of creating a new one), then straight to `DeployPanel`, same
pipeline as Restore. Headless-verified against a real backup file:
filename validation, and `patch_profile_name()` producing a
structurally-identical clone confirmed via `describe_screen_changes()`
reporting zero screen differences — consistent with the real-hardware
CLI result above. See `PROJECT_NOTES.md` / "Clone Profile" for the
full writeup; GUI's own real-hardware pass is the next thing to
verify.

---

## Startup message (startup.txt) — built and headlessly validated

Sketched as a candidate GUI feature back on 2026-08-06, deliberately
held until the two real open questions below could be confirmed
against real hardware, then **built end to end on 2026-08-14, Doug's
go-ahead**:

- `startup.txt` is a plain-text file, completely outside
  `data_screen`/FIT mechanics — it lives at the device root
  (`garmin_root` itself, same level as `Sports`/`NewFiles`/`Settings`),
  NOT inside `Sports/`. Displays a custom message at device boot,
  controlled by a `<display=N>` directive (minimum seconds shown)
  followed by free-form message text, wrapped in Garmin's own `<!--
  -->` instructional comments.
- **Both real open questions RESOLVED via Doug's own real Edge 530**
  (direct `ls -l`/`cat` of the mounted device, 2026-08-14) — not just
  the developer-supplied secondary-source findings (256-char limit,
  7-bit ASCII, ~5-7 visible lines depending on model, from
  gplama.com/DC Rainmaker) that were the only reference available
  before:
  - **Path**: confirmed exactly `garmin_root/startup.txt` — no
    `find_garmin_root()` change needed, it already resolves to the
    right directory.
  - **Write mechanism**: confirmed a DIRECT overwrite while the device
    is mounted, NOT a NewFiles import — the file's own on-device
    comment states plainly "Allow one full power cycle after editing
    for your message to be updated," meaning a full power cycle (off,
    then on) is what's needed, not just eject/remount.
- **DONE (`garmin_device.py` v0.12.0)**: `read_startup_txt()`/
  `parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`,
  plus a `startup-txt` CLI subcommand. `write_startup_txt()` backs up
  any existing file first (same `working_dir/backups/` structure
  `backup_profiles()` already uses) before overwriting.
  `parse_startup_txt()`/`build_startup_txt()` split/rejoin the file at
  its last comment block, so Garmin's own instructional text is
  preserved byte-for-byte and only the `<display=N>` value + message
  text are ever regenerated — headlessly round-trip-tested
  byte-identical against Doug's real file content.
- **DONE (`gui_app.py` v0.18.0, `StartupTxtPanel`)**: a new "Startup
  Message..." button on `DetectPanel` (not on the profile flow, since
  this file has nothing to do with any profile) opens a view/edit form
  — `<display=N>` seconds and message text are editable, everything
  else preserved verbatim. Live char/line-count guidance shown but
  deliberately NOT a hard block on Save — Doug's own explicit call
  (2026-08-14): actual on-device wrapping is character-width-dependent
  and can't be reliably predicted from typed character count, so the
  real safety net is the automatic pre-write backup, not a refusal to
  save; if a user doesn't like how it wrapped, they can just edit and
  retry. Save flow ends with the same eject-button pattern
  `DeployPanel` uses, but with no post-write verification step (a boot
  message can't be read back by this app).
- Estimated small pre-build, confirmed small in practice — no FIT
  parsing, CRC, or NewFiles pathway involved at all, unlike everything
  else in this toolkit.
- Headlessly verified: parse/build round-trip byte-identical;
  `write_startup_txt()`'s backup-then-overwrite behavior against a
  fake filesystem `garmin_root` (plain file I/O, no real device
  needed here); the `startup-txt` CLI subcommand end-to-end via a
  monkeypatched `find_garmin_root()`. Real GUI behavior on Doug's
  actual hardware is still pending his own run, same as every other
  GUI feature in this project.

---

## Design constraints worth deciding on early

- **`message_index` should never be shown to the user directly** — it
  isn't stable across writes and has no meaning to someone using the
  device normally. The UI should work entirely in terms of on-screen
  position and content; internal slot numbers stay internal.
- **`--swap-order` takes raw `message_index`, not display position** —
  the GUI sidesteps this entirely: `gui_app.py` v0.7.0's screen-level
  reordering is select-plus-Move-Up/Down-buttons (not drag-and-drop,
  per the Editing UX decision below), so the user only ever picks a
  row by its on-screen position — the panel translates that to the
  underlying slot numbers internally. Not worth fixing in the CLI
  itself.
- **GUI toolkit:** leaning wxPython over CustomTkinter —
  `wx.grid.Grid` / `wx.propgrid` map naturally onto "list of screens,
  each with editable properties," avoiding the need for two separate
  toolkits.
- **Every write should re-verify against the device afterward** where
  practical, given how many surprises this project has turned up in
  write-path behavior — don't assume success just because the copy
  operation didn't error.
- See `PROJECT_NOTES.md`'s "GUI scoping" section for the full agreed
  10-step high-level flow (detect → list → select/backup/stage → view
  → edit, applied immediately click-by-click rather than queued via
  `fit_chain.py` as originally planned → pre-flight diff/CRC review →
  deploy/eject/remount → post-write verify).
- **Confirmed hard caps (real device testing):** 10 fields per screen,
  10 user-definable screens per profile (Garmin-predefined/overlay
  screens don't count against the 10). The field editor already
  enforces the per-screen cap (Add Field disables at 10); screen-level
  reordering is built (`gui_app.py` v0.7.0, Move Up/Down) and needs no
  cap logic of its own since it only reorders existing screens, never
  adds one. **DONE (v0.8.0):** the Add-New-Screen panel enforces the
  screen-count cap directly -- counts real user screens (f10 not a
  named Garmin type) in any show state, not just currently-visible
  ones, and disables Create Screen with a friendly explanation once at
  10.
