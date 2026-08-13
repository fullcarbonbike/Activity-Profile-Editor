# Garmin Edge 530 Activity Profile Screen Editor

*Doc rev 25 — refreshed 2026-08-13. **Second real bug found via real
Mac hardware, same test session: `install.sh` v1.0.1 crashed with
`PIP_EXTRA[@]: unbound variable`** the moment it tried to install
`garmin-fit-sdk`, on a Mac with a freshly-installed Homebrew python3
3.14. Cause: bash 3.2 (confirmed to be what actually runs this
script on real macOS, via Doug's `bash-3.2$` prompt) throws
unbound-variable when an *empty* array is expanded under `set -u` —
a real bash bug, fixed in 4.4+, invisible in the bash 5 dev sandbox.
Fixed in v1.0.2: replaced the array with a `pip_install()` wrapper
function, no array left in the script at all — eliminates the whole
bug class rather than patching around this one instance. Re-verified
both the plain-install and `--upgrade` code paths in the dev sandbox.
Prior rev (24, 2026-08-13) summary follows.*

*Doc rev 24 — refreshed 2026-08-13. **Real bug found via real hardware
test: `install.sh` v1.0.0 crashed silently on a fresh Mac with no
Xcode Command Line Tools installed** — invoking python3 for its
version check triggered macOS's own `xcode-select` "requesting
install" note plus a non-zero exit, and `set -e` turned that into an
unexplained stop right after "Found python3," no error message from
the script. Fixed in v1.0.1: explicit Command Line Tools check as its
own step, before python3 is touched at all, with clear instructions
instead of a silent failure; defense-in-depth error handling on the
python3 version-check call itself; new `--version` flag. Verified
the fix in the dev sandbox by reproducing both the no-CLT and
CLT-present paths. Not yet re-tested on Doug's actual Mac. Prior rev
(23, 2026-08-13) summary follows.*

*Doc rev 23 — refreshed 2026-08-13. **Cosmetic fix confirming pre-v1.0.1
release state.** `gui_app.py`'s `FieldPickerDialog` docstring still
said "105 confirmed entries," stale since the 2026-08-11 batches grew
`fit_dump.py` to 117 — comment only, the picker itself always read
`FIELD_ID_NAMES` live so it was never actually wrong. Fixed, `gui_app.py`
now v0.16.12. Confirmed for Doug: `fit_dump.py` v2.4.9 (117 entries,
field 320 "Perf. Conditioning" the latest correction) and `gui_app.py`
both reflect everything gathered so far, ahead of testing `install.sh`
on real Mac hardware and a possible v1.0.1 tag. Prior rev (22,
2026-08-13) summary follows.*

*Doc rev 22 — refreshed 2026-08-13. **New `install.sh` setup script**
(macOS only, matching this toolkit's current real platform support).
Checks python3 presence/version (warns and checks for Xcode Command
Line Tools if older than 3.10, since `wxPython` only has pre-built
PyPI wheels from 3.10 up), creates/reuses a dedicated `.venv`, installs
`garmin-fit-sdk` and `wxPython` into it, then verifies both import.
Idempotent, `--upgrade`/`--help` flags. Setup section and GUI section
updated to lead with it, manual `pip install` steps kept as a
fallback. Cross-platform support deferred until Windows/Linux device
detection itself exists. Prior rev (21, 2026-08-11) summary follows.*

*Doc rev 21 — refreshed 2026-08-11. **Field 320 corrected** —
"Conditioning" is now "Perf. Conditioning." Full concept name is
"Performance Conditioning," but Doug confirmed the actual on-device
DATA FIELD display reads "Perf. Conditioning" (abbreviated), matching
this toolkit's on-device-display naming convention (`fit_dump.py` now
v2.4.9, still 117 entries, rename only). Prior rev (20, 2026-08-11)
summary follows.*

*Doc rev 20 — refreshed 2026-08-11. **Field 49 corrected** — "Avg
Speed (Alt)" is actually just "Avg Speed," confirmed by deploying it
into a full-width screen slot and visually checking on-device: plain
text, no graph/bars (`fit_dump.py` now v2.4.8). Flagged as a caution
for the Graph/Bars marker theory, not a falsification — see
`PROJECT_NOTES.md` for the full reasoning. Prior rev (19, 2026-08-11)
summary follows.*

*Doc rev 19 — refreshed 2026-08-11. **12 new field IDs** from Doug's
continued census (2, 15, 18, 32, 165, 347, 350, 433, 452, 478, 495,
497), plus 3 placeholder names corrected now that the "*"/"(Alt)"
on-device marker is understood — it denotes a Graph/Bars-style field
needing a full-width screen slot (`fit_dump.py` now v2.4.7, 117
confirmed entries). See `PROJECT_NOTES.md` for the full writeup.
Prior rev (18, 2026-08-11) summary follows.*

*Doc rev 18 — refreshed 2026-08-11. **Two field names corrected**
(real user report) — fields 58/87 were "Lap Timer"/"Last Lap Timer,"
now correctly "Lap Time"/"Last Lap Time" (`fit_dump.py` v2.4.5, no
IDs added/removed, still 105 confirmed entries). See `PROJECT_NOTES.md`
for the full writeup. Prior rev (17, 2026-08-11) summary follows.*

*Doc rev 17 — refreshed 2026-08-11. **Clone Profile CONFIRMED via real
hardware** — two working clones deployed via NewFiles under brand-new
filenames (`Clonebox`, `CloneRoad`), reported after the fact and
corrected here (this file had been carrying a stale "not yet tested
through the actual GUI" note). `gui_app.py` reached v0.16.10 (doc-only)
logging the confirmation. See `PROJECT_NOTES.md` for the fuller
writeup. Prior rev (16, 2026-08-11) summary follows.*

*Doc rev 16 — refreshed 2026-08-11. **Pre-publish housekeeping ahead
of a possible GitHub release.** Added a License/Disclaimer section
(MIT, "not affiliated with Garmin" trademark note, black-box-
reverse-engineering method note, device-write risk warning).
`gui_app.py` reached v0.16.9: window title renamed to "Activity
Profile Screen Editor for Garmin Edge" (v0.16.7), a new About
button/dialog (v0.16.8), and a fix to the default backup working
directory — now cross-platform (`~/GarminBackups`) and persisted
across restarts instead of resetting to a hardcoded Mac-specific path
every launch (v0.16.9). See `PROJECT_NOTES.md` for the full pre-publish
writeup, including an in-progress Windows-support scoping assessment.
Prior rev (15, 2026-08-05) summary follows.*

*Doc rev 15 — refreshed 2026-08-05. **MAJOR REVERSAL: Add New Screen
via NewFiles is now CONFIRMED WORKING.** The "always fails" limitation
documented since early in this project was root-caused as an f10
IDENTITY COLLISION, not a hard device restriction — `--new-slot`'s old
default silently wrote f10=0, colliding with the f10 almost every real
profile's existing "Screen 1" already holds. `fit_patch.py` 1.12.0 adds
`next_available_field10()` and uses it as the new auto-default,
replacing the old hardcoded 0. CONFIRMED via a live on-device
round-trip (2026-08-05, CyclingRoadSandbox): a new screen with a
collision-free f10 survives the NewFiles restart cycle intact,
verified independently by both `fit_dump.py` and `garmin_device.py`
reading the live mounted device afterward. `--un-remove` uses the same
corrected default but hasn't itself been re-tested live yet. See
`FIT_PATCH.md` BUGS and `PROJECT_NOTES.md` for the full writeup,
including the superseded original failure diagnosis.

Prior rev (14, 2026-08-04): **field 10 (f10) confirmed as a real,
content-independent screen TYPE identifier** — named Garmin types
(Map, Compass, Elevation, Segment, ClimbPro, etc.) get a fixed global
code; plain user screens use a per-profile counter shown on-device as
"Screen N". This finally answers "how many real user screens does
this profile have" directly from the file. Landed: `fit_dump.py` 2.4.2
(bug fix for a `classify_screens()` gate that missed some genuine
screens; `screens` output now shows real type names; 86 confirmed
field IDs — 84/87 resolved, closing the last open field-ID mystery),
`fit_patch.py` 1.11.0 (`would_hide_last_visible_screen()` rewritten to
count only real user screens via f10, fixing a confirmed undercounting
bug; `check_system_screen_guard()` also made f10-based, fixing a real
reported false positive where a confirmed user screen still triggered
the old "possibly a system screen" pause; NEW
`hide_unsupported_screen_type()` hard-blocks hiding Map or ClimbPro at
all — confirmed via direct on-device inspection that neither has a
Show Screen toggle, on any profile type), and `gui_app.py` 0.6.3
(screen list shows a Type column with real names, edit screen title
shows the real name, guard warning dialogs no longer false-positive on
confirmed user screens, and a third HARD block against hiding
Map/ClimbPro). Also corrects an earlier claim that Removed-state
screen content is preserved indefinitely — it's purged by the next
NewFiles-mediated deploy of any kind, confirmed via real testing. See
`PROJECT_NOTES.md` for full detail.*

Command-line toolkit for reading and editing Garmin Edge 530 Activity
Profile screen configurations directly, without the on-device menu —
screen order, field lists, layout, show/hide, multi-step batched
edits, and profile cloning, all from a computer. Built by
reverse-engineering an undocumented section of the FIT file format;
see [`PROJECT_NOTES.md`](PROJECT_NOTES.md) for the full technical
writeup, [`MVP_SCOPE.md`](MVP_SCOPE.md) for what's in/out of scope,
and [`MEMORY_LOG.md`](MEMORY_LOG.md) for the complete project history
and findings log.

**Status:** CLI toolkit complete and validated end-to-end on real
hardware — every core capability (field edits in both directions,
layout, show/hide, reorder, multi-step chaining, profile
clone-and-retarget, restore-from-backup) has a confirmed real-device
round trip. GUI implementation has started: `gui_app.py` is a
skeleton covering step 1 of the agreed flow (detect device + show
device info) — see `PROJECT_NOTES.md` for the full flow and what's
built vs. still to come.

## License

Released under the [MIT License](LICENSE) — free to use, modify, and
redistribute, with no warranty.

## Disclaimer

This is an independent, unofficial project. It is **not affiliated
with, endorsed by, or sponsored by Garmin Ltd. or its subsidiaries.**
"Garmin" and "Edge" are trademarks of Garmin Ltd. or its subsidiaries;
they're used here only to describe which devices this toolkit is
compatible with, not to claim any official status.

The `data_screen` message and related undocumented fields this project
relies on were reverse-engineered entirely through **black-box
observation** — making isolated changes on a real device (or via a
custom byte-patcher) and diffing the resulting files — never by
decompiling, disassembling, or otherwise reverse-engineering Garmin's
own software or SDK. The official `garmin_fit_sdk` Python package is
used only as a normal dependency, for its documented decode/encode
support of standard FIT messages.

**Use at your own risk.** This toolkit patches undocumented file
structures and writes the result back to your device through an
undocumented pathway (`NewFiles/`). It's been tested carefully against
real hardware throughout development, but Garmin could change this
behavior in a future firmware update without notice, and no guarantee
is made against corrupting a profile, losing data, or other unintended
device behavior. Back up your profiles before use (this toolkit does
this automatically before every write, but the responsibility is
ultimately yours) and don't run it on a device you can't afford to have
misbehave.

No warranty of any kind is provided, express or implied — see
[LICENSE](LICENSE) for the full legal text.

## Setup

**macOS only.** Run the install script — it checks your python3
version, creates a dedicated `.venv` (nothing touches your system or
Homebrew Python), and installs both dependencies (`garmin-fit-sdk` and
`wxPython`) into it:

```bash
./install.sh
source .venv/bin/activate
```

Safe to re-run any time; add `--upgrade` to update already-installed
packages, or `--help` for details. It's a plain bash script, no
network access beyond pip, and no admin/sudo required.

Prefer to do it by hand, or need just the CLI tools without the GUI's
`wxPython` dependency? The manual equivalent:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install garmin-fit-sdk --break-system-packages
```

## Quick start

Connect your Edge 530 via USB, then:

```bash
# Confirm the device is detected (also shows device info: manufacturer/product/serial/software version)
python3 garmin_device.py detect

# See what profiles are on it
python3 garmin_device.py list

# Back everything up before touching anything
python3 garmin_device.py backup ~/path/to/a/working/directory

# See the current screen layout for one profile
python3 garmin_device.py screens CyclingRoadRoadtest.fit
```

To make a change, stage a backed-up profile, patch it, then deploy:

```bash
python3 garmin_device.py stage CyclingRoadRoadtest.fit <backup_path> <working_dir>
python3 fit_patch.py <staged_file> <patched_file> --slot 9 --hide
python3 garmin_device.py deploy <patched_file> CyclingRoadRoadtest.fit
```

To make several changes before a single device write/restart, use
`fit_chain.py` instead of calling `fit_patch.py` directly:

```bash
python3 fit_chain.py <staged_file> <patched_file> \
    --step '--slot 9 --hide' \
    --step '--swap-order 1,11' \
    --step '--slot 4 --layout 1'
python3 garmin_device.py deploy <patched_file> CyclingRoadRoadtest.fit
```

Follow the eject prompt. After the device's automatic restart
finishes, press the power button **once** to bring it back into
mass-storage mode (it does not remount on its own), then reconnect and
verify:

```bash
python3 garmin_device.py wait-for-remount
python3 garmin_device.py screens CyclingRoadRoadtest.fit
```

To clone an existing profile under a new name (e.g. building a second
bike's profile from an existing one instead of rebuilding every screen
by hand):

```bash
python3 fit_clone_profile.py <staged_file> <cloned_file> --name "NewBikeName"
python3 garmin_device.py deploy <cloned_file> <NEW_FILENAME>.fit   # filename must NOT match an existing profile
```

## Tools

| Tool | Version | Purpose |
|---|---|---|
| `install.sh` | 1.0.2 | macOS-only setup script. **SECOND real bug found via real hardware, same test session (2026-08-13):** past the CLT/python3 checks (Homebrew python3 3.14, freshly installed), "Installing garmin-fit-sdk..." died with `PIP_EXTRA[@]: unbound variable`. Cause: bash 3.2 (macOS's stock `/bin/bash` — confirmed that's really what runs this script, via Doug's `bash-3.2$` prompt) has a long-standing bug where expanding an *empty* array under `set -u` throws unbound-variable instead of silently expanding to nothing — fixed in bash 4.4+, so it never showed up in the bash 5 dev/test sandbox, only on real hardware. Fixed in v1.0.2 by replacing the `PIP_EXTRA` array with a small `pip_install()` wrapper function that branches on `$UPGRADE` directly — no array left anywhere in the script, so this bug class is now structurally impossible, not just avoided this one instance. Also v1.0.1: on a genuinely fresh Mac with no Xcode Command Line Tools ever installed, v1.0.0 crashed silently right after "Found python3" — invoking python3 for its version check triggered macOS's own `xcode-select` "requesting install" note to stderr and a non-zero exit, which `set -e` turned into an unexplained stop with no error message from the script itself. Fixed with an explicit Command Line Tools check as its own step, before python3 is touched at all, plus defense-in-depth error handling around the version-check invocation; new `--version` flag. Checks the platform, checks Xcode CLT, checks python3 is present and at least 3.9 (warns if older than 3.10, since `wxPython` only ships pre-built PyPI wheels from 3.10 up), creates/reuses a dedicated `.venv` so nothing touches system or Homebrew Python, installs `garmin-fit-sdk` and `wxPython` into it, then imports both back to confirm the install actually works. Idempotent, `--upgrade`/`--help`/`--version` flags. Windows/Linux support deferred until device detection itself is implemented for those platforms (see `garmin_device.py`'s `_find_garmin_root_windows()` stub). |
| `garmin_device.py` | 0.11.0 | Detect (+ device info)/list/backup/stage/write/eject/remount-wait workflow for the device itself. NEW (v0.11.0): `list_backup_history()` lists a single profile's backup history (newest first), de-duplicating consecutive byte-identical backups — a real characteristic of this app, since every visit to the GUI's profile list re-backs-up all profiles, not just on real changes. Backs the GUI's Restore-from-Backup picker; also a new `backup-history` CLI subcommand. |
| `fit_dump.py` | 2.4.9 | Read and inspect a `.fit` file (`dump`, `unknown`, `diff`, `screens` subcommands). `classify_screens()`/`active_field_ids()`/`screen_type_name()` are print-free, importable data functions — the seam the GUI reads screens through. `FIELD_ID_NAMES` has 117 confirmed entries (`KNOWN_UNRESOLVED_IDS` still empty; v2.4.9: field 320 corrected "Conditioning" → "Perf. Conditioning" — full concept name is "Performance Conditioning," but the actual on-device DATA FIELD display reads "Perf. Conditioning" (abbreviated), matching this toolkit's on-device-display naming convention; v2.4.8: field 49 corrected "Avg Speed (Alt)" → "Avg Speed" — deployed into a full-width slot and visually confirmed as plain text, no graph/bars; flagged as a caution (not a falsification) for the Graph/Bars marker theory below, since there's no record this field's old "(Alt)" label was ever a real on-device marker transcription like 23/348/349 were; v2.4.7, 2026-08-11 batch: 12 new IDs plus 3 corrected placeholder names — 23 "Heart Rate (Alt)" → "HR Zone Graph", 348/349 "Speed */Cadence *" → "Speed Bars"/"Cadence Bars" — confirming the "*"/"(Alt)" marker denotes a Graph/Bars-style field needing a full-width slot; v2.4.6, doc-only: the long-open "*" marker mystery on fields 348/349 is likely resolved — marks a Graph/Bars-style rendering needing a full-width screen slot, else falls back to plain text; v2.4.5: fields 58/87 corrected from "Lap Timer"/"Last Lap Timer" to "Lap Time"/"Last Lap Time" — a mistaken analogy to the separate, correctly-named field 56 "Timer"; 2026-08-10 batch: 18 IDs confirmed via a dedicated two-screen, 10-field-each census on a real profile, cross-referencing on-device field names against their GUI-shown position); `NAMED_SCREEN_TYPES` has 10 confirmed f10 screen-type codes (Map, Compass, Segment, ClimbPro, etc.) — `screens` output now shows real screen names. |
| `fit_patch.py` | 1.12.0 | Patch a screen's fields, layout, order, or visibility. `next_available_field10()` (NEW) auto-computes a collision-free screen identity for `--new-slot`/`--un-remove`, replacing the old hardcoded f10=0 default — root cause of the now-RESOLVED "Add New Screen always fails" limitation; CONFIRMED working via live on-device round-trip. `check_system_screen_guard()` is f10-based and CERTAIN for any Active screen (old content-pattern/field-count heuristics are a fallback only for Removed-state slots) — fixed a real false positive on a confirmed user screen. `would_hide_last_visible_screen()` is a HARD, non-heuristic guard (no `--force`) blocking `--hide`/`--disable` on a profile's last remaining real USER screen, counted via f10. `hide_unsupported_screen_type()` is a SECOND hard guard blocking `--hide` on Map or ClimbPro entirely — confirmed neither has a Show Screen toggle at all, on any profile type. |
| `fit_chain.py` | 1.0.0 | Apply several `fit_patch.py` operations in sequence before one device write |
| `fit_clone_profile.py` | 1.0.0 | Clone a profile under a new display name (patches `sport_mesgs[0].name`) |
| `fit_raw_walk.py` | 1.0.0 | Internal support — generic FIT byte-offset walker, not meant to be run directly |
| `fit_crc.py` | 1.0.0 | Internal support — FIT CRC-16, not meant to be run directly |
| `gui_app.py` | 0.16.12 | wxPython GUI — covers steps 1-10 plus Restore-from-Backup and Clone Profile (v0.16.12: cosmetic doc-only fix, field picker's docstring count updated 105 -> 117 to match `fit_dump.py` v2.4.9's current entry count (the picker itself was never wrong — it reads `FIELD_ID_NAMES` live — only the comment had drifted stale, caught while confirming pre-release state ahead of a possible v1.0.1 tag); v0.16.11: doc-only, the "restore a profile no longer on the device" feature's one real open risk (whether NewFiles can recreate a genuinely deleted profile, not just replace/create-new) is now CONFIRMED via a direct `garmin_device.py deploy` test against a deliberately-deleted profile — only the GUI entry point itself remains unbuilt; v0.16.10: doc-only, no code change — Clone Profile CONFIRMED via real hardware, reported after the fact (two working clones deployed via NewFiles under brand-new filenames: `Clonebox`, `CloneRoad`), correcting a stale "not yet tested through the actual GUI" note and resolving whether NewFiles accepts a genuinely new filename, not just a replacement — see the toolkit table's v0.16.0 entry below for the corrected text; v0.16.9: pre-Windows-support housekeeping — the default backup working directory was hardcoded to a specific Mac path, now `~/GarminBackups` (resolves correctly on any OS/user); the working directory is now also persisted across restarts via a small config file (`~/.garmin_screen_editor_config.json`), so a custom location picked via "Change..." is remembered instead of resetting every launch; v0.16.8: new "About" button on the detect screen opens a short summary dialog — name/version, "not affiliated with Garmin" disclaimer, reverse-engineering method note, MIT mention pointing to `LICENSE`/`README.md` for the full text; v0.16.7: window title renamed to "Activity Profile Screen Editor for Garmin Edge" ahead of a possible public release — this is an independent, unofficial project, not a Garmin product; see `LICENSE` and `README_DISCLAIMER_DRAFT.md` (pending review) for the rest of that pass; v0.16.6: fixed a real bug where v0.16.3's own fix for the Fields-column width issue was itself wrong — capping the column stopped the window from growing but silently truncated text instead, with no scrollbar; correct fix decouples the frame's size from the column's width via a `ScreensListCtrl` subclass, letting the column go back to full auto-size and the list's real native horizontal scroll work as intended — see `PROJECT_NOTES.md` toolkit table row and "Corrections and lessons learned" for the full story; v0.16.5: cosmetic doc-only fix, field picker's docstring count updated 87 -> 105 to match `fit_dump.py` v2.4.4's new field IDs, no functional change; v0.16.4: bumped the on-device layout diagram's font from 9pt to 13pt for readability, per real feedback with a screenshot — safe change, no width/height risk since that panel is custom-painted at a fixed size, unlike the widgets behind v0.16.2/v0.16.3; v0.16.3: same-day follow-up to v0.16.2 — the identical unresolved-field-ID window-widening bug also hit the Fields column on the main Screens view, not just the Edit Screen panel; fixed with the same terse-label approach plus a width ceiling on that column; v0.16.2: fixed a real bug where editing a screen with an unresolved field ID permanently oversized/off-screened the window — see `PROJECT_NOTES.md` toolkit table row for the full root-cause writeup; v0.16.1: the "not connected" message and window title are now model-generic/version-visible — see `PROJECT_NOTES.md` "Model portability") (detect, list/backup, select+stage, view screens with a real Type column and screen-level Move Up/Down reordering, add a brand-new screen, edit one screen's fields/layout/Show-Hide/type, review accumulated changes, deploy to the device, post-write verification, restore any profile from its backup history, and clone a profile under a new name). **This closes out the GUI's full feature backlog.** NEW (v0.16.0): `ClonePanel` — "Clone..." on the profile list patches `sport_mesgs[0].name` via `fit_clone_profile.py`'s `patch_profile_name()` (CLI-validated full-fidelity on real hardware already), with live filename-collision checking against every profile currently on the device (deploying under an existing filename would silently overwrite it) and an auto-suggested filename from the display name. Hands off straight to Deploy, same as Restore — no staged-vs-editing diff applies to a clone. Headless-verified: filename validation, byte-for-byte-structurally-identical clone output, and zero screen differences between source and clone via `describe_screen_changes()`. **CONFIRMED via real hardware (2026-08-11, reported after the fact):** at least two clones deployed and working correctly through NewFiles under brand-new filenames not previously present on the device (`Clonebox` from `Sandbox`, `CloneRoad` from `Road`) — this also confirms NewFiles correctly accepts a genuinely new filename, not just a replacement of an existing one, a question that had been open until now. Prior entry (v0.15.2): cosmetic doc-only fix (a stale field-count reference in a docstring, no functional change). v0.15.1: fixed a real bug found via testing — backing out of a Restore attempt without completing it left a stale reference to the abandoned backup file in place, so a subsequent normal Stage silently showed that leftover instead of the profile just staged ("View Screens shows the backup I was about to restore, not what I just staged"). A fresh Stage now always clears any prior session's state first. v0.15.0: "Restore from Backup..." on the profile list now goes somewhere — `RestorePanel` lists the selected profile's backup history with a plain-English screen summary per entry ("8 screen(s): Screen 1, Lap Summary, Map, ..."), and picking one hands off straight to Deploy, skipping the staged-vs-editing review (nothing to review — you already picked a known backup). The backup file is used directly, never copied. "Back" from Deploy now returns to wherever it was actually reached from. v0.14.0: the moment "Check for Reconnected Device" succeeds, the GUI automatically re-pulls the live profile from the device and compares it against what was sent, reusing the same plain-English per-screen summary as "Review & Deploy..." (now shared as a module-level `describe_screen_changes()`). Compares visible/active screens only — the device's known Removed-list wipe on NewFiles import (a side effect that's always happened, unrelated to anything this GUI does) isn't reported, matching the fact that neither Garmin's own editor nor this GUI offers an un-remove workflow. **CONFIRMED live on real hardware** (2026-08-06) alongside a full deploy of a new 10-field screen. v0.13.0: "Continue to Deploy" now goes somewhere — `DeployPanel` writes the working copy to the device's `NewFiles/` (with byte-for-byte write-back verification), then a confirm-then-`diskutil eject` button (plus an "I Ejected It Myself" fallback for non-macOS/Finder), then a manual "Check for Reconnected Device" button. User-confirmed design decision: no background polling for the reconnect wait (this app has never used a background thread, and it's not worth the new failure-mode class for saving a few clicks) — each Check click is one immediate, non-blocking connectivity check. v0.12.0: "Review & Deploy..." now describes changes in plain English per screen (e.g. "Screen 4: added Cadence, removed Grade") instead of a raw `fit_dump.py diff`-style unified diff — real user feedback that the byte-level diff was too technical for the GUI's actual audience (a rider, not a developer); the CLI tools remain there for anyone who wants that detail. Covers new/removed screens, field changes, layout changes, show/hide changes, and position changes, with a fallback line so real changes are never silently under-reported; whether there's anything to deploy is still decided from the raw bytes directly. v0.11.1: fixed a real reported bug where the Fields column silently clipped (not wrapped) any screen with more than ~3-4 short field names — a 10-field screen only showed 3 fields and part of a 4th; the column now auto-sizes to its actual content on every refresh. v0.11.0: fixed a real reported bug where manually enlarging the window (e.g. to see more of the screens list) snapped back to a smaller size the moment any button triggered a refresh — `_relayout()` was calling `Fit()`, which resizes in both directions including shrinking; now only grows the window when content needs more room, never shrinks it. v0.10.0: "Review & Deploy..." is a pre-flight step showing a `fit_dump.py diff`-style comparison against the untouched staged file plus a real CRC check against the working file's actual bytes — REVISES the original "pending/preview state" plan to match how the GUI actually works (every change is already applied immediately, click by click; there's no separate queue to apply, only a review+verify step). Continue to Deploy is a placeholder until deploy/eject/remount is built. "Change Type..." is Add-New-Screen and EditScreenPanel's "Replace Field" — swaps one field's ID without the Remove+Add+reposition workaround. Add-New-Screen panel replicates `--new-slot`'s exact defaulting logic — auto-assigns f9/f10, enforces the confirmed 10-user-screen cap with a friendly message; **CONFIRMED live on real hardware** (2026-08-05), including a confirmed field-type change on ClimbPro after overriding the guard. Screen-level reordering is select + Move Up/Down on the main screens list, wired to `swap_display_order()` — same validated primitive as `--swap-order`. Show/Hide hard-blocks hiding a profile's last real user screen (f10-based) AND hiding Map/ClimbPro at all (neither has an on-device toggle). Guard dialogs no longer false-positive on confirmed user screens (real GUI testing found and fixed this). Swallows a cosmetic teardown-only `wxAssertionError` on exit. Field picker offers 117 confirmed IDs. |

## GUI

`gui_app.py` is the editor GUI, built incrementally, one step of the
agreed flow (see `PROJECT_NOTES.md`) at a time — each step wired to
its already-validated backend function, tested against real hardware
before the next step is added. **All 10 flow steps plus
Restore-from-Backup and Clone Profile are now built — nothing left in
the GUI feature backlog**: detect the device and show its
info; list profiles (via an automatic backup-all-profiles call);
select a profile and stage it for editing; view the staged profile's
current screens, read-only, with screen-level reordering (Move
Up/Down); a real Add-New-Screen panel (pick fields and layout, the
tool auto-assigns everything else — CONFIRMED live on real hardware);
drill into a single screen to reorder, add, remove, or change the type
of its fields and change its A/B layout, with a live visual diagram of
the on-device grid (built from the developer's own text-based Edge 530
layout reference — see `PROJECT_NOTES.md` / "On-device layout
geometry") — the field-type swap ("Change Type...") is CONFIRMED live
on real hardware including a guard-overridden edit to ClimbPro; a
"Review & Deploy..." pre-flight step showing a plain-English,
per-screen change summary plus a real CRC check; "Deploy to Device"
(write to `NewFiles/`, guided eject, manual reconnect check) —
CONFIRMED live on real hardware alongside a full 10-field new screen;
automatic post-write verification the instant reconnect is confirmed,
re-pulling the live profile and comparing it against what was sent;
"Restore from Backup..." — pick any of a profile's past backups
from a plain-English-summarized list and it goes through the same
Deploy/verify pipeline as a normal edit; and "Clone..." — clone the
selected profile under a new display name (`fit_clone_profile.py`,
already CLI-validated on real hardware) with live filename-collision
checking, going through the same Deploy pipeline as Restore. See
`PROJECT_NOTES.md` / "Clone Profile" for the full writeup.

Editing architecture: rather than an abstract in-memory list of
"pending changes," a scratch working copy of the staged file (which
persists across edits to multiple screens in one session) IS the
queue — every button click is a real, immediately-applied
`fit_patch.py` operation, and the screen always re-reads the actual
resulting bytes afterward instead of trusting an in-memory guess.
"Discard Edits" on the screens view resets back to the untouched
staged file.

The Show/Hide checkbox is guarded two ways, checked in order: a HARD
block (unhideable, no override) if hiding this screen would leave the
profile with zero visible Active/Display screens — confirmed via real
on-device testing that Garmin's own editor refuses this too — followed
by the existing softer heuristic guard for likely system/overlay
screens (content-pattern match OR field count ≤2, `--force`-style
confirm dialog).

Editing UX decision (recorded ahead of building it): reordering is
select + Move Up/Move Down buttons, not drag-and-drop — it maps
directly onto the already-validated `--swap-order`/`--swap-fields`
primitives with no new backend logic. Field count changes and
reassigning which fields appear on a screen go through `--fields`
(replaces the whole list, count follows from its length), fed from a
picker over the known field ID catalog rather than free-text entry,
and guarded by the same heuristic the CLI uses.

```bash
./install.sh              # installs wxPython too -- see Setup above
source .venv/bin/activate
python3 gui_app.py
```

(Manual equivalent without the script: `pip install wxPython
--break-system-packages`.)

Full CLI reference: [`FIT_PATCH.md`](FIT_PATCH.md). (A companion
`FIT_DUMP.md` reference is planned but not yet written.)

## ⚠️ Before you write anything to a real device

- Always run `garmin_device.py backup` first.
- Always verify a patched file with `fit_crc.py` and
  `fit_dump.py screens` *before* deploying it.
- Adding a brand-new screen via `fit_patch.py --new-slot` is now
  CONFIRMED WORKING (v1.12.0+, live on-device round-trip verified
  2026-08-05) — the earlier "must use the on-device Add New menu"
  guidance is superseded. Still verify with `fit_dump.py screens` and
  `fit_crc.py` before every deploy, and expect the profile's entire
  Removed-screen list to be purged by the deploy regardless of what
  it targets. See `PROJECT_NOTES.md`/`FIT_PATCH.md` BUGS for the full
  writeup.
- `fit_patch.py --un-remove` uses the same corrected auto-default as
  `--new-slot` but has NOT itself been re-tested live since the fix.
  Also: Garmin's own on-device editor has no un-remove option at all,
  so this is likely never going to be a first-class GUI feature —
  kept available for deliberate testing, final call deferred. Back up
  first, not just recommended, required.
- `fit_patch.py --fields` refuses to overwrite a slot whose current
  content matches a pattern commonly seen on system/overlay screens
  (empty, Elevation/Grade, Cycling Dynamics) unless you pass
  `--force` — a "did you mean to?" pause, not a certain
  identification. Verify what the screen actually is on-device first.
