# Garmin Edge 530 Activity Profile Screen Editor

*Doc rev 33 — refreshed 2026-08-13. **Second real bug, same test
session: `install.sh` v1.0.1 died with `PIP_EXTRA[@]: unbound
variable`** the moment it tried to install `garmin-fit-sdk`, right
after cleanly passing the v1.0.1 CLT fix (Doug had run `xcode-select
--install`, Homebrew python3 3.14 detected fine). Root cause: bash
3.2 -- confirmed for real via Doug's `bash-3.2$` prompt, macOS's
actual stock `/bin/bash` -- has a genuine, long-documented bug where
`set -u` throws unbound-variable on an EMPTY array's `[@]` expansion
instead of expanding to nothing (fixed upstream in bash 4.4, 2016;
macOS still ships 3.2 for GPLv3-avoidance reasons). `PIP_EXTRA=()`
plus `"${PIP_EXTRA[@]}"` when `--upgrade` wasn't passed (the normal
case) hit this exactly. Invisible in the dev sandbox because that
sandbox runs bash 5.1.16, which doesn't have the bug -- a real,
now-identified gap between sandbox and real-hardware test coverage.
Fixed in v1.0.2: `PIP_EXTRA` array removed entirely, replaced with a
`pip_install()` function branching on `$UPGRADE` directly -- zero
arrays left in the script (`grep '\[@\]'` confirms), so the bug class
is eliminated structurally, not patched around. Tried to get a real
bash 3.2 into the sandbox to close the coverage gap properly (compile
from source) -- blocked by the sandbox's network allowlist (GNU
mirrors all returned `blocked-by-allowlist`); fell back to structural
elimination plus this being a well-known, well-documented historical
bash bug. Re-verified both the plain-install and `--upgrade` paths in
the dev sandbox. Not yet re-confirmed end-to-end on Doug's Mac past
this fix. See the toolkit table entry below for the full writeup.
Prior rev (32, 2026-08-13) summary follows.*

*Doc rev 32 — refreshed 2026-08-13. **Real bug found via real Mac
hardware test: `install.sh` v1.0.0 crashed silently on a fresh
machine with no Xcode Command Line Tools installed.** Doug's report:
`bash-3.2$ ./install.sh` got through the platform check and "Found
python3" cleanly, then died right there -- only output was macOS's own
`xcode-select: note: No developer tools were found, requesting
install` message, no error from the script itself, prompt just
returned. Root cause: invoking python3 for its version check was the
first real python3 execution, and a CLT-less `/usr/bin/python3` can't
actually run -- it exited non-zero, `set -e` turned that into a silent
stop. The script's only CLT check existed, but was buried inside the
"Python < 3.10" warning branch, reachable only AFTER a version check
that could never succeed without CLT in the first place -- backwards
ordering. Fixed in v1.0.1: Command Line Tools check moved to its own
step immediately after the platform check, before python3 is touched
at all, with a clear message (install dialog may have just opened --
let it finish, or run `xcode-select --install` yourself, then
re-run). Also added defense-in-depth error handling around the
version-check python3 invocation itself, and a `--version` flag.
Verified the fix in the dev sandbox (both the no-CLT-stops-cleanly
path and the CLT-present-proceeds-normally path); not yet re-tested
end to end on Doug's Mac. Bonus confirmation: Doug's `bash-3.2$`
prompt confirms the script really is running under real macOS stock
bash 3.2 as designed, not just assumed compatible. See the toolkit
table entry below for the full writeup. Prior rev (31, 2026-08-13)
summary follows.*

*Doc rev 31 — refreshed 2026-08-13. **Pre-release consistency check,
one cosmetic fix.** Doug asked directly whether `fit_dump.py` and
`gui_app.py` reflect all field IDs gathered so far, ahead of testing
`install.sh` on real Mac hardware and a possible v1.0.1 tag. Confirmed
yes -- `fit_dump.py` v2.4.9 (117 entries, field 320 "Perf. Conditioning"
the latest); `gui_app.py` has no separate field ID list, it imports
`FIELD_ID_NAMES` live, so it can never go stale on data. Did catch one
purely cosmetic drift while checking: `FieldPickerDialog`'s docstring
still said "105 confirmed entries" (last updated at v0.16.5, before
the 2026-08-11 batches). Fixed, `gui_app.py` now v0.16.12. Prior rev
(30, 2026-08-13) summary follows.*

*Doc rev 30 — refreshed 2026-08-13. **New `install.sh` setup script**
(real user request: "make it easier to plug and play"). macOS-only
per Doug's decision (matches the toolkit's current real platform
support -- Windows/Linux device detection still isn't implemented).
Checks python3 presence/version (hard floor 3.9, warns plus checks for
Xcode Command Line Tools below 3.10, since `wxPython` only ships
pre-built PyPI wheels from 3.10 up -- verified directly against PyPI's
JSON API), creates/reuses a dedicated `.venv` (user-confirmed choice
over the README's existing bare system-Python `pip install
--break-system-packages` pattern, which this also sidesteps entirely
since a venv's pip is never PEP-668 externally-managed), installs
`garmin-fit-sdk`/`wxPython` into it, then imports both back to confirm
the install actually works, not just that pip exited 0. Idempotent,
`--upgrade`/`--help` flags. Verified in the dev sandbox (Linux) with
the platform gate patched out: version-check arithmetic, venv
creation, pip upgrade, and `garmin-fit-sdk` install/import all
confirmed working; `wxPython`'s install predictably fails there
(no macOS wheel, no GTK headers to build from source in this sandbox)
-- expected, not a real bug, since real macOS would fetch the prebuilt
wheel instead. Not yet run on Doug's actual Mac. README.md Setup/GUI
sections now lead with it, manual `pip install` steps kept as an
explicit fallback. See the toolkit table entry below for the full
writeup. Prior rev (29, 2026-08-11) summary follows.*

*Doc rev 29 — refreshed 2026-08-11. **Field 320 corrected.** Doug
reported the "Conditioning" field's full concept name is "Performance
Conditioning," but the actual on-device DATA FIELD display reads
"Perf. Conditioning" (abbreviated). Renamed to match this toolkit's
established convention of naming fields as they display on-device
rather than by their full/conceptual name -- same convention behind
"Lap Dist." and "Dest. Location" (`fit_dump.py` now v2.4.9, still 117
entries, rename only; `FIT_PATCH.md` now doc rev 16). Prior rev (28,
2026-08-11) summary follows.*

*Doc rev 28 — refreshed 2026-08-11. **Field 49 corrected; important
methodological caution for the Graph/Bars marker theory.** Doug
followed up by deploying field 49 (old placeholder "Avg Speed (Alt)")
into a full-width screen slot and visually confirming on-device: it's
plain text, no graph or bars. Renamed to "Avg Speed"
(`fit_dump.py` now v2.4.8, `FIT_PATCH.md` now doc rev 15). Flagged as
a caution, not a falsification -- unlike 23/348/349, there's no record
this field's old "(Alt)" label was ever a literal on-device marker
transcription, so it may simply have been an old, undocumented naming
guess. Practical takeaway for the eventual GUI feature: the confirmed
Graph/Bars set should only grow from fields where a real on-device
marker was directly observed and recorded, not from any old name that
happens to contain "(Alt)". Prior rev (27, 2026-08-11) summary
follows.*

*Doc rev 27 — refreshed 2026-08-11. **12 new field IDs, plus 3
placeholder names corrected now that the "*"/"(Alt)" marker is
understood.** Doug's continued census (separate session): 2 Course Pt
Dist., 15 Lap HR, 18 Lap %Max HR, 32 Next Pt Location, 165 Last Lap
HR, 347 HR Bars, 350 Power Bars, 433 Anaerobic TE, 452 Respiration,
478 EPOC, 495 60s Grit, 497 60s Flow. Corrected: 23 "Heart Rate (Alt)"
→ "HR Zone Graph", 348 "Speed *" → "Speed Bars", 349 "Cadence *" →
"Cadence Bars" — confirming the marker denotes Graph/Bars-type
rendering. `fit_dump.py` now v2.4.7 (117 confirmed entries, no
collisions), `FIT_PATCH.md` now doc rev 14 with a regenerated
reference table. Graph/Bars full-width warning Open Item updated with
the now-10-field confirmed set. Prior rev (26, 2026-08-11) summary
follows.*

*Doc rev 26 — refreshed 2026-08-11. **"*" marker mystery likely
resolved; Graph/Bars full-width warning scoped.** Doug confirmed the
long-open "*"/"(Alt)" field-name marker (fields 348/349, 23, 49, and
the self-evidently-named Graph cluster) denotes a Graph- or Bars-style
rendering that needs a full-width screen slot, falling back to plain
text otherwise — corrected throughout (`fit_dump.py` now v2.4.6,
`FIT_PATCH.md` now doc rev 13, doc-only, not independently re-verified
by this project yet). New Open Item: a GUI warning surfacing this,
fully computable from `LAYOUT_GRIDS`'s existing row-width data with no
new geometry model needed — see "Graph/Bars full-width warning" below.
Prior rev (25, 2026-08-11) summary follows.*

*Doc rev 25 — refreshed 2026-08-11. **Redundant-backup reduction
scoped and batched as low priority.** A tester's complaint (repeated
"Backed up X profile(s)..." messages just from reselecting a different
profile, no edits involved) traced to `ProfileListPanel` re-backing-up
everything on every visit rather than once per meaningful device-state
change. Scoped correctly (the naive "once ever" version would silently
skip the backup taken right after a real deploy — the most important
one). Doug's call: worth doing, but low priority — his own real usage
numbers (~1MB backup folder even after heavy testing, ~4-5GB across
1098 files over this project's whole prior history) confirm disk
footprint was never really the issue. He also flagged a possibly
better-value alternative: a real backup retention/pruning routine,
already an existing (until now unscoped) Open Item — updated with his
numbers and his own suggestion that it may be worth doing first. Prior
rev (24, 2026-08-11) summary follows.*

*Doc rev 24 — refreshed 2026-08-11. **Two field names corrected,
real user report.** Fields 58 and 87 were transcribed as "Lap
Timer"/"Last Lap Timer" — a mistaken analogy to the separate,
correctly-named field 56 "Timer" — but a closer on-device relabeling
check found the real display text is "Lap Time"/"Last Lap Time," no
"r." Corrected in `fit_dump.py` (now v2.4.5, `FIELD_ID_NAMES` still
105 entries, none added/removed) and `FIT_PATCH.md` (now doc rev 12).
Field 56 "Timer" is unaffected. Prior rev (23, 2026-08-11) summary
follows.*

*Doc rev 23 — refreshed 2026-08-11. **Design chosen for "restore a
deleted profile"; both it and `startup.txt` deferred to a future
batched release.** `ProfileListPanel` gets a second list section below
the existing on-device one ("Deleted, but available to restore"),
implemented as a separate widget rather than an inline divider row
(deliberately avoiding a repeat of this session's wx.ListCtrl/ListBox
issues) — the existing Restore button/`RestorePanel` need no changes
at all, since neither has ever cared whether a filename is currently
live. Doug's decision: hold off building this and `startup.txt` for
now (a confirmed-working CLI workaround exists via `garmin_device.py
deploy`), watch for anything else that surfaces over the next few
days, and fold whatever accumulates into one future release. Prior rev
(22, 2026-08-11) summary follows.*

*Doc rev 22 — refreshed 2026-08-11. **"Restore a deleted profile"
fully de-risked.** Doug directly tested the exact scenario that
enhancement is about — `garmin_device.py deploy` with a backup of a
profile deliberately deleted from the device, targeting that
now-absent filename — and confirmed via on-device verification that
NewFiles correctly recreates it. This is a stronger, more direct
confirmation than rev 21's Clone Profile finding (same underlying
mechanism, but this is the literal restore-a-deleted-profile path, not
an analogous one). The backend/CLI side of this feature is now fully
proven; only the GUI entry-point gap remains. `gui_app.py` reached
v0.16.11 (doc-only). Prior rev (21, 2026-08-11) summary follows.*

*Doc rev 21 — refreshed 2026-08-11. **Clone Profile's real-hardware
status corrected.** Doug reported (after the fact) that Clone Profile
has actually been confirmed working on real hardware for some time —
two clones deployed via NewFiles under brand-new filenames, `Clonebox`
and `CloneRoad` — which had never been logged here; this document (and
README.md) had been carrying a stale "not yet tested through the
actual GUI" note against it. Corrected throughout. This also resolves
what had just been flagged (rev 20, below) as the single biggest open
risk for the newly-scoped "restore a deleted profile" enhancement,
since both features write a NewFiles filename not currently present in
`Sports/` — that mechanism is now confirmed working. `gui_app.py`
reached v0.16.10 (doc-only, logging this confirmation). Prior rev (20,
2026-08-11) summary follows.*

*Doc rev 20 — refreshed 2026-08-11. **Repo is live on GitHub; first
external user-reported gap scoped.** A user working from
`garmin_device.py` (GUI restore path not yet used) found that a
profile deleted from the device has no way to be selected for Restore
in the GUI — correctly diagnosed as a real gap (`ProfileListPanel`'s
list is sourced entirely from the live device), not user error.
Scoped, not yet built — see "Restore a profile that's no longer on the
device" under Open Items below; flags a shared unconfirmed-on-real-
hardware risk with Clone Profile (both write a NewFiles filename not
currently present in `Sports/`). Prior rev (19, 2026-08-11) summary
follows.*

*Doc rev 19 — refreshed 2026-08-11. **Pre-publish/GitHub-release
housekeeping pass.** Landed: `LICENSE` (MIT, copyright `Doug
(fullcarbonbike)`), a License/Disclaimer section merged into
`README.md`, `gui_app.py`'s v0.16.7 window-title rename ("Activity
Profile Screen Editor for Garmin Edge"), v0.16.8's About button/dialog,
and v0.16.9's working-directory fix — cross-platform default
(`~/GarminBackups`) plus persistence across restarts via a small
config file, replacing a hardcoded Mac-specific path that reset every
launch. Also landed (discussed and documented, neither built yet): a
Windows-support scoping assessment — device detection is the only real
gap, `_find_garmin_root_windows()` is a clearly-marked stub and
everything else in the toolkit is already OS-agnostic — and a scoping
writeup for a tester-requested "Favorite Screen" feature (save a
screen's field set + layout, reuse it across other profiles). See
"Publishing to GitHub" and the two newest entries under Open Items
below for full detail. Prior rev (18, 2026-08-06) summary follows.*

*Doc rev 18 — refreshed 2026-08-06. **Clone Profile is now built in
the GUI** (`gui_app.py` v0.16.0, `ClonePanel`) — see "Clone Profile"
below. This was the last item in the GUI feature backlog; all ten
agreed flow steps plus Restore-from-Backup and Clone are now built,
headless-verified, with only Clone's real-hardware GUI pass still
outstanding. Prior rev (17, 2026-08-05) summary follows.*

*Doc rev 17 — refreshed 2026-08-05. **MAJOR REVERSAL: Adding a
brand-new screen via `fit_patch.py --new-slot` is now CONFIRMED
WORKING.** The "reliably fails" conclusion in rev 16 and earlier —
documented as settled and root-caused to the NewFiles delivery
mechanism itself — has been superseded. Root cause, now confirmed: an
f10 IDENTITY COLLISION. `--new-slot`'s old default silently wrote
f10=0, and f10=0 is a real, specific identity ("Screen 1") that almost
every real profile already has — not an inert sentinel as assumed at
the time. `fit_patch.py` v1.12.0 adds `next_available_field10()` and
uses it as the new auto-default. Live-tested 2026-08-05 on
`CyclingRoadSandbox`: a new screen (fields Gears/Front Gear, f10=2,
"Screen 3") survived a full deploy → restart → remount cycle intact,
independently re-confirmed against the live mounted device by both
`fit_dump.py` and `garmin_device.py`. See "Adding a new screen" below
for the full rewrite, including an honest note on a loose end this
doesn't fully explain. Prior rev (16, 2026-08-04) summary follows.*

*Doc rev 16 — refreshed 2026-08-04. Major update from a side-thread
field-exploration session (see `MEMO_FINDINGS.md`): **f10 is now
CONFIRMED as a real, content-independent screen TYPE identifier** —
named Garmin types (Map=25, Virtual Partner=26, GroupTrack=32,
Compass=35, Elevation=44, Segment=56, GroupTrack List=57, Cycling
Dynamics=63, Lap Summary=74, ClimbPro=104) get a fixed global code;
plain user screens use a per-profile counter shown on-device as
"Screen N" (f10=N → "Screen N+1"). This solves the previously-open
"tell a user screen from a Garmin screen" problem outright. Landed
this session: `fit_dump.py` 2.4.2 (bug fix — `classify_screens()` no
longer misses screens with no `f3`, e.g. Virtual Partner; added
`NAMED_SCREEN_TYPES`/`screen_type_name()`, `screens` output now shows
real type names; 86 confirmed field IDs, with 84/87 — Last Lap
Dist/Last Lap Timer — closing the toolkit's last open field-ID
mystery), `fit_patch.py` 1.11.0 (same `f3`-gate bug fixed in
`read_current_state()`; `would_hide_last_visible_screen()` rewritten
to count only real user screens via f10, fixing a confirmed
undercounting bug; `check_system_screen_guard()` also made f10-based,
fixing a real reported false positive where a confirmed user screen
still triggered the old "possibly a system screen" pause; NEW
`hide_unsupported_screen_type()` hard-blocks `--hide` on Map or
ClimbPro entirely, confirmed via direct on-device inspection that
neither has a Show Screen toggle at all — see CORRECTIONS), a
correction to the Screen State Model's Removed-state persistence
claim, and `gui_app.py` 0.6.3 (ViewScreensPanel gets a Type column,
EditScreenPanel's title shows the real screen name, all guard-warning
dialogs reworded to match the confirmed model, and a third HARD block
against hiding Map/ClimbPro at all). Not auto-synced with ongoing
work — regenerate from `MEMORY_LOG.md` (or the live project context)
if this drifts again.*

Reverse-engineering project to read and edit Garmin Edge 530 Activity
Profile screen configurations (data screens, fields, layouts, display
order, and the device connection/write workflow itself) — with the
goal of a GUI editor to replace the on-device menu workflow for the
single most-requested capability on Garmin's own forums: reordering
screens and fields from a computer.

**Status:** The full CLI toolkit is validated end-to-end on real
hardware. Every core capability — field edits (both replacing a
screen's whole field list and increasing its field count), layout
A/B, show/hide, screen reordering, multi-step chaining before a single
write, and profile clone-and-retarget — has a confirmed real-device
round trip, not just a simulated one. The device connection layer
(`garmin_device.py`) is fully validated end-to-end: detect → list →
backup → stage → patch → deploy → eject → power-button restart →
remount → re-verify. Field ID census: 80 of an estimated ~200 possible
IDs confirmed. **GUI implementation is underway**: `gui_app.py` covers
steps 1-8 of the agreed flow (detect device + show device info; list
profiles via an automatic backup of every profile; select a profile
and stage it for editing; view its current screens read-only, with
screen-level Move Up/Down reordering as of v0.7.0; a real
Add-New-Screen panel as of v0.8.0, not a redirect -- see "Adding a new
screen" below), plus step 6 -- editing one screen's fields
(reorder/add/remove/change-type as of v0.9.0), A/B layout with a live
visual diagram of the on-device grid layout (see "On-device layout
geometry", below), and a guarded Show/Hide toggle -- all built and
syntax-verified, including a fix for a window-close crash found during
real use, and CONFIRMED on real hardware for Add-New-Screen and Change
Type both. Steps 7-8 (v0.10.0): a "Review & Deploy..." pre-flight
panel showing a diff against the staged file plus a real CRC check --
see "Agreed high-level flow" below for why this ended up as a pure
review+verify step rather than the originally-planned "apply changes"
step; the diff itself became a plain-English, per-screen change
summary in v0.12.0 after real user feedback that the byte-level diff
was too technical for the GUI's actual audience (a rider, not a
developer). Step 9 (v0.13.0): a `DeployPanel` writes the working copy
to NewFiles/, then walks the user through eject and reconnect via a
manual "Check for Reconnected Device" button rather than background
polling -- see "Agreed high-level flow" below for the reasoning.
Post-write verification (step 10, v0.14.0) automatically re-pulls the
live profile the moment reconnect is confirmed and compares it against
what was sent, sharing the same plain-English comparison as steps 7-8.
Restore-from-Backup (v0.15.0) is built too -- a `RestorePanel` lists a
profile's backup history with a per-candidate screen summary and hands
off straight to `DeployPanel`, skipping the staged-vs-editing review
entirely since it doesn't apply to a restore. Clone Profile (v0.16.0)
is also built -- a `ClonePanel` clones the selected profile under a new
display name (`fit_clone_profile.py`, CLI-validated on real hardware
already) with live filename-collision checking, and hands off straight
to `DeployPanel` the same way Restore does. **All ten flow steps, plus
Restore and Clone, are now built -- this closes out the GUI's full
feature backlog** -- see "Agreed high-level flow" below.

---

## Background

The Edge 530 stores each Activity Profile as a `.FIT` file at
`Garmin/Sports/<ProfileName>.fit`. Screen layouts are stored using an
**undocumented** message type (`data_screen`, global `mesg_num=14`)
absent from Garmin's public FIT SDK. Everything below was reverse-
engineered by making a single, isolated change (on the device itself,
or via a custom byte-patcher), pulling the resulting file, diffing it
byte-for-byte against a known "before" state, and confirming the
change matches exactly what was intended before generalizing.

Dev environment: working directory is
`/Volumes/UserDCbu/dougcurtis/garmindev` (a separate external volume,
deliberately not under `$HOME`, to avoid home-volume space
constraints), with a working `.venv` containing `garmin_fit_sdk`. Git
repo lives here specifically — an earlier `git init` accidentally
scoped to the home directory and was caught before any commit landed
(an obviously-too-broad untracked-file list was the tell), then fixed
by deleting that `.git` and reinitializing in `garmindev` directly.
Backups and staged edits live in `/Volumes/UserDCbu/dougcurtis/GarminBackups`
— one level above `garmindev`, same volume, outside the git repo
entirely (cleaner than relying on `.gitignore` alone). Use this same
path consistently for both backup and stage.

---

## Toolkit

| File | Version | Purpose |
|---|---|---|
| `install.sh` | 1.0.2 | macOS-only setup script, real user request ("make it easier to plug and play"). Bash, `set -euo pipefail`, written to also run correctly under macOS's stock bash 3.2 (no associative arrays, no `[[ ]]` regex-only features from bash 4+) even though it was authored/tested against bash 5 in the dev sandbox -- **CONFIRMED running under real bash 3.2 on Doug's actual Mac** (`bash-3.2$` prompt visible in his terminal output), so that compatibility goal is now verified, not just theoretical. **REAL BUG FOUND AND FIXED (v1.0.1, 2026-08-13):** Doug's first real-hardware test was on a genuinely fresh Mac laptop that had never had Xcode Command Line Tools installed. v1.0.0 got through the platform check and "Found python3" cleanly, then died silently: invoking `python3 -c '...'` for the version check triggered macOS's own `xcode-select` "note: No developer tools were found, requesting install" message on stderr, python3 itself exited non-zero (CLT-less `/usr/bin/python3` can't actually run), and `set -e` turned that into an immediate, unexplained script exit -- no `die()` message, nothing actionable, just the raw OS message and a dead prompt. Root cause: the script's only CLT check (`xcode-select -p`) was buried inside the "Python < 3.10" warning branch, reachable only AFTER a successful version check -- exactly backwards, since CLT has to exist before python3 can run AT ALL on a fresh install, not just before building wxPython from source. Fix: moved the Command Line Tools check to its own step, immediately after the platform check and before python3 is touched in any way -- on failure it now explains plainly that macOS may have just opened an install dialog (let it finish) or to run `xcode-select --install` directly, then re-run. Also hardened the version-check python3 invocation itself with explicit `if ! ... ; then die ...` error handling (previously bare `set -e`-reliant) as defense-in-depth against any other python3-fails-to-run scenario, not just this one. Added `SCRIPT_VERSION`/`--version` (this class of tool had no version string at all before -- every other file in this toolkit tracks one). **Verified the fix in the dev sandbox** by reproducing both branches: no-`xcode-select`-on-PATH now stops cleanly at the new step with the intended message (confirmed NOT reaching python3 at all); a stubbed `xcode-select -p` that reports success now proceeds correctly through python3 detection, version check, venv creation, and `garmin-fit-sdk` install/import exactly as before. **SECOND real bug found and fixed, same test session (v1.0.2, 2026-08-13):** Doug ran `xcode-select --install`, got past the v1.0.1 fix cleanly (CLT found, python3 found -- Homebrew's, freshly installed, reporting 3.14 -- version check passed), then hit a new failure the instant the script tried "Installing garmin-fit-sdk...": `./install.sh: line 174: PIP_EXTRA[@]: unbound variable`. Root cause: `PIP_EXTRA=()` followed later by `"${PIP_EXTRA[@]}"` when `--upgrade` wasn't passed (the common case) means expanding a genuinely EMPTY array -- and bash 3.2 has a real, long-documented bug where `set -u` treats an empty array's `[@]` expansion as an unbound variable and errors, instead of correctly expanding to zero words the way POSIX/modern bash does. Fixed in bash 4.4 (2016), but macOS still ships 3.2 as `/bin/bash` for licensing reasons (GPLv3 avoidance) and has for over a decade -- exactly the environment `install.sh` was written to target, confirmed for real this session via Doug's own `bash-3.2$` shell prompt in his pasted output. This bug was INVISIBLE in the dev/test sandbox specifically because that sandbox runs bash 5.1.16 (`bash --version` confirmed), which doesn't have it -- every earlier "verified in the dev sandbox" claim for this script was genuinely accurate for what it tested, it just couldn't have caught this one, a real gap in the sandbox-vs-real-hardware coverage that's now closed. Fix: removed `PIP_EXTRA` entirely, replaced with a `pip_install()` shell function that takes a package name and internally branches `if (( UPGRADE )); then ... --upgrade ...; else ...; fi` -- no array anywhere in the script now, so this isn't a patch around one instance, the whole bug class is structurally gone. Re-verified in the dev sandbox: both the plain-install path and `--upgrade` path exercised end to end (confirmed `garmin-fit-sdk` installs/imports correctly either way; `wxPython`'s build-from-source failure at that point remains the expected, sandbox-is-Linux-not-macOS limitation, unrelated to this fix). Attempted to get real bash 3.2 into the dev sandbox for a true repro (compile from source) specifically to close this coverage gap properly -- blocked by the sandbox's network allowlist (ftp.gnu.org and mirrors all returned `blocked-by-allowlist`); relying instead on eliminating the array construct structurally (confirmed via `grep '\[@\]'` returning zero matches in the whole file) plus the well-documented nature of this specific historical bash bug. Not yet re-confirmed end-to-end on Doug's Mac past this fix. Prior entry (v1.0.0, 2026-08-13, initial version): macOS-only setup script. Sequence: (1) `uname -s == Darwin` gate, dies with a clear message otherwise -- explicitly scoped to macOS only per Doug's decision, since `garmin_device.py`'s Windows path is still a `NotImplementedError` stub and Linux isn't even stubbed; cross-platform version deferred until Doug has Windows hardware to test against; (2) `python3` presence check; (3) version check -- hard floor 3.9 (dies below that), warns below 3.10 specifically because PyPI's `wxPython` wheels are only pre-built for cp310 and up (verified directly against the live PyPI JSON API before picking this cutoff -- 3.9 and older would silently fall through to a from-source build, 10-20 min, requiring the Command Line Tools); (4) creates/reuses a dedicated `.venv` in the toolkit's own directory via `python3 -m venv` -- deliberate choice over installing to system/Homebrew Python (Doug's explicit choice over the alternative), which also sidesteps PEP 668's "externally managed environment" block entirely, since a venv's own pip is never marked externally-managed -- no `--break-system-packages` needed anywhere in this script, unlike the manual README instructions it supplements; (5) upgrades pip inside the venv; (6) installs `garmin-fit-sdk` and `wxPython` into it (`--upgrade` CLI flag threads through to both if passed); (7) imports both back inside the venv's own Python and reports version strings, so a "successful" pip install that's actually broken doesn't get reported as done. Idempotent by construction. User-confirmed design decisions (2026-08-13): macOS-only for now (cross-platform revisited once Windows access exists); dedicated venv rather than the README's existing bare `pip install ... --break-system-packages` pattern, specifically to avoid touching system/Homebrew Python at all. README.md's Setup and GUI sections lead with `./install.sh`, keeping the original manual `pip install` commands as an explicit fallback. |
| `fit_raw_walk.py` | 1.0.0 | Generic FIT definition/data message byte-offset walker. No SDK dependency — needed because the SDK doesn't recognize `data_screen` at all. |
| `fit_crc.py` | 1.0.0 | FIT file CRC-16 (Garmin's nibble-table algorithm). Self-verifies against known-good files before being trusted for writes. |
| `fit_dump.py` | 2.4.9 | SDK-based (`garmin_fit_sdk`) read/inspect tool. Subcommands: `dump`, `unknown`, `diff`, `screens` (sorted by true display order, shows all three screen states plus real f10-derived screen-type names). `classify_screens()`/`active_field_ids()`/`screen_type_name()` are print-free functions, importable directly by the GUI. `NAMED_SCREEN_TYPES` holds the 10 confirmed f10 codes. `FIELD_ID_NAMES` has 117 confirmed entries (v2.4.9, real user report: field 320 corrected "Conditioning" -> "Perf. Conditioning" -- full concept name is "Performance Conditioning," but the actual on-device DATA FIELD display reads "Perf. Conditioning" (abbreviated), matching this toolkit's on-device-display naming convention (same as "Lap Dist.", "Dest. Location"); v2.4.8, real user report: field 49 corrected "Avg Speed (Alt)" -> "Avg Speed" -- deployed into a full-width slot and visually confirmed on-device as plain text, no graph/bars; a METHODOLOGICAL CAUTION for the Graph/Bars marker theory, not a falsification -- no record exists that this field's old "(Alt)" label was ever a real on-device marker transcription the way 23/348/349 were; v2.4.7, 2026-08-11 batch: 12 new IDs -- 2, 15, 18, 32, 165, 347, 350, 433, 452, 478, 495, 497 -- plus 3 corrected placeholder names (23 "Heart Rate (Alt)" -> "HR Zone Graph", 348 "Speed *" -> "Speed Bars", 349 "Cadence *" -> "Cadence Bars"), confirming the "*"/"(Alt)" marker denotes a Graph/Bars-style field needing a full-width screen slot, else falls back to plain text; v2.4.6, doc-only: the long-open "*" marker mystery on fields 348/349 is likely resolved -- Graph/Bars-style rendering needing a full-width screen slot, else falls back to plain text, per Doug's report; v2.4.5, real user report: fields 58/87 corrected from "Lap Timer"/"Last Lap Timer" to "Lap Time"/"Last Lap Time" -- a mistaken analogy to the separate, correctly-named field 56 "Timer," caught via a closer on-device relabeling check; 2026-08-10 batch: 18 IDs -- 7, 30, 31, 39, 50, 57, 61, 62, 63, 67, 86, 88, 94, 95, 295, 442, 443, 445 -- confirmed by arranging two screens to 10 fields each on a real profile for this census, entering each field by its on-device name, then cross-referencing raw ID against known on-screen position via the GUI) -- `KNOWN_UNRESOLVED_IDS` is still empty. |
| `fit_patch.py` | 1.12.0 | Surgical byte-level patcher/writer. `next_available_field10()` (NEW) auto-assigns a collision-free screen identity for `--new-slot`/`--un-remove`, replacing the old hardcoded f10=0 default -- root-caused and RESOLVED the long-standing "Add New Screen always fails" limitation; CONFIRMED working via live on-device round-trip (2026-08-05). `check_system_screen_guard()` (`--force` to override) is f10-based and CERTAIN for any Active screen, not a guess -- old content-pattern/low-field-count heuristics kept only as a fallback for Removed-state slots with no real f10. `would_hide_last_visible_screen()` is a HARD, non-heuristic guard (no `--force`) blocking `--hide`/`--disable` on a profile's last remaining REAL USER screen, correctly counted via f10. `hide_unsupported_screen_type()` is a SECOND hard guard (no `--force`) blocking `--hide` on Map or ClimbPro entirely -- CONFIRMED via direct on-device inspection that neither has a Show Screen toggle at all, on any profile type. |
| `fit_chain.py` | 1.0.0 | Chains multiple `fit_patch.py` operations into one file before a single device write, avoiding a restart per change. CRC-verified after every step. |
| `fit_clone_profile.py` | 1.0.0 | Clones a profile under a new display name by patching `sport_mesgs[0].name` — a standard, SDK-known message, unlike `data_screen`. |
| `garmin_device.py` | 0.11.0 | Device connection layer: detect (+ `get_device_info()` device identification), list, backup (lineage-tracked), stage, write to `NewFiles` with read-back verification, eject/remount-wait. `screens` subcommand shells out to `fit_dump.py screens` directly -- no separate classification logic to fix. NEW (v0.11.0): `list_backup_history(working_dir, profile_filename)` lists every backup of one profile under `working_dir/backups/<timestamp>/`, newest first, de-duplicating consecutive byte-identical entries (a real characteristic of this app: every visit to the GUI's profile list re-backs-up all profiles, not just on real changes, so an untouched profile accumulates many identical timestamped backups per session -- collapsing those keeps the history meaningful, one entry per REAL change). Backs the GUI's `RestorePanel`; also a new `backup-history` CLI subcommand for parity. |
| `gui_app.py` | 0.16.12 | wxPython GUI. NEW (v0.16.12, cosmetic doc-only fix, 2026-08-13): `FieldPickerDialog`'s docstring said "105 confirmed entries" -- stale after `fit_dump.py` grew to 117 across the 2026-08-11 batch (v2.4.7) and the field 49/320 rename-only corrections (v2.4.8/2.4.9); same class of drift already fixed once before at v0.16.5 (87->105). No functional change -- `FIELD_ID_NAMES` is imported live from `fit_dump.py`, so the actual field picker was never wrong, only this comment. Caught while confirming pre-release state ahead of a possible v1.0.1 tag (Doug asked directly whether `fit_dump.py`/`gui_app.py` reflect all field IDs gathered so far -- yes, both do; `FIELD_ID_NAMES` has no separate copy in `gui_app.py` to go stale). Prior entry (v0.16.11, doc-only, no code change): the "restore a profile no longer on the device" enhancement's one real open risk -- whether NewFiles can RECREATE a deleted profile, not just replace an existing one or accept a never-before-seen filename -- is now RESOLVED. Doug tested the exact scenario via `garmin_device.py deploy` with a backup of a deliberately-deleted profile, targeting that now-absent filename; CONFIRMED via on-device verification. Only the GUI entry-point itself remains unbuilt (see Open Items). Prior entry (v0.16.10, doc-only, no code change): Clone Profile CONFIRMED via real hardware, reported after the fact by Doug -- two working clones deployed via NewFiles under brand-new filenames (`Clonebox`, `CloneRoad`), correcting a stale "not yet tested through the actual GUI" note that had been sitting in both this table and the "DONE" section below, and resolving a previously-open question shared with the newly-scoped "restore a deleted profile" enhancement: NewFiles does correctly accept a genuinely new filename, not just a replacement of an existing one. Prior entry (v0.16.9, pre-Windows-support housekeeping): `DEFAULT_WORKING_DIR` was hardcoded to Doug's own actual Mac path (`/Volumes/UserDCbu/dougcurtis/GarminBackups`) -- harmless for Doug alone, but wrong for any other user and outright broken on Windows, where `/Volumes/...` doesn't exist. Now `os.path.join(os.path.expanduser("~"), "GarminBackups")`, resolving sanely on any OS/user. Also, `working_dir` was never persisted across restarts even after being changed via "Change..." -- every launch reset to the default. New `load_saved_working_dir()`/`save_working_dir()` persist the choice to a small JSON sidecar (`~/.garmin_screen_editor_config.json`); `MainFrame.__init__` seeds `working_dir` from the saved value if present (falling back to `DEFAULT_WORKING_DIR` only on a genuine first-ever launch), and `on_change_working_dir()` saves immediately on every pick. Both best-effort/never-raise -- a missing/corrupt config file or read-only home directory just falls back to in-memory-only behavior for that session, never blocks the app. User-confirmed design (2026-08-11) over two simpler alternatives (plain default with no persistence; first-use-only prompt) -- both would have needed the same persistence layer anyway, so this solves it for good. Prior entry (v0.16.8): "About" button on `DetectPanel` opens `AboutDialog` -- a short modal summary (name/version, "not affiliated with Garmin" trademark disclaimer, a one-paragraph note that `data_screen` was reverse-engineered via black-box observation rather than reverse-engineering Garmin's own software, MIT license mention pointing to `LICENSE`/`README.md` for the full text). Deliberately short, not an attempt to embed the full legal text verbatim -- keeps this dialog from ever needing to track the README disclaimer word-for-word. Read-only word-wrapped `wx.TextCtrl` body; as a modal dialog with its own fixed size (not embedded in `MainFrame`'s resizable sizer tree) it can't reproduce the v0.16.2/v0.16.3/v0.16.6 best-size bug class regardless, wrapping is just the right call for a paragraph this long either way. Headless-verified the template string's line-continuation formatting collapses correctly (real string-literal evaluation, not regex extraction). Prior entry (v0.16.7): cosmetic rename ahead of a possible public GitHub release -- window title changed from "Garmin Edge Screen Editor" to "Activity Profile Screen Editor for Garmin Edge" (this is an independent, unofficial project, not a Garmin product; "for Garmin Edge" is the standard nominative-fair-use naming pattern, user-confirmed over two other candidates). No functional change -- part of the same pre-publish pass as the new `LICENSE` (MIT) and the disclaimer draft, see Open Items below ("Publishing to GitHub"). Prior entry (v0.16.6): real reported bug fix that also corrects a WRONG previous fix -- v0.16.3's 460px ceiling on the Fields column stopped the frame from growing but silently broke something else: `wx.ListCtrl` clips a cell's text to its column's pixel width with no wrap/ellipsis, and the control's own horizontal scrollbar only engages when the SUM of all column widths exceeds the control's rendered area, which a single capped column mostly never triggers -- confirmed on a real 10-field screen with several of the new longer field names, only 6-7 visible, no way to see the rest, no error. New `ScreensListCtrl(wx.ListCtrl)` subclass overrides `DoGetBestSize()` to cap only the WIDTH the sizer system sees (height still comes from the normal calculation, preserving v0.11.0's grow-taller-for-more-rows intent) -- decoupling the FRAME's size from the COLUMN's width entirely, rather than trying to control one by capping the other. `ViewScreensPanel.screens_list` and `RestorePanel.history_list` (same exposure, proactively fixed too -- it had never even gotten the v0.16.3 ceiling) both switched to it. The Fields column reverted to floor-only auto-size (280px minimum, no ceiling) -- safe again now that content width can't reach the frame; genuine overflow now correctly triggers the `ListCtrl`'s real native horizontal scroll, since assigned-area-smaller-than-content is finally the true state of affairs. See PROJECT_NOTES.md "Corrections and lessons learned" for the full three-strikes story on this widget. Prior entry (v0.16.5): cosmetic doc-only fix -- `FieldPickerDialog`'s docstring said "87 confirmed entries," stale after `fit_dump.py` v2.4.4's 2026-08-10 batch of 18 new field IDs brought `FIELD_ID_NAMES` to 105; no functional change. Prior entry (v0.16.4): readability fix -- real reported feedback (with a side-by-side screenshot) that `LayoutDiagramPanel`'s cell-label text (9pt) was noticeably smaller than the rest of the window's controls. Bumped to 13pt (10pt for the italic note/placeholder text) and `SetMinSize()` from (280,220) to (340,280) for more breathing room at the bigger font in dense 8-10 field layouts. Confirmed via code review this carries NONE of the v0.16.2/v0.16.3 width-blowup risk -- `LayoutDiagramPanel` is custom-painted with an explicit per-cell clipping region, its reported size is only ever the fixed `SetMinSize()` value, never derived from font/content the way `wx.ListBox`/`wx.ListCtrl` are. One flagged trade-off to watch during testing: a longer known field name in a busy layout is now somewhat more likely to get silently clipped (no ellipsis) at the bigger font. Prior entry (v0.16.3): same-day follow-up to v0.16.2 -- the identical root cause also hit `ViewScreensPanel`'s "Fields" `ListCtrl` column, not just `EditScreenPanel`/`AddScreenPanel`'s `wx.ListBox`: a real profile with 9 of 10 fields unresolved on two screens still widened the window from "View Screens." The v0.11.1 fix's assumption -- that a report-mode `ListCtrl`'s column content never grows the frame, since its own native horizontal scrollbar takes over -- didn't hold for large enough overflow, confirmed via real testing. Fixed both the trigger and the mechanism together: the Fields column and the Conditional/Removed summary lines (`self.other_text`, a plain `wx.StaticText` with no scrollbar at all -- actually more exposed to this than the `ListCtrl` was) now use `field_name(fid, terse=True)`; `SetColumnWidth(6, wx.LIST_AUTOSIZE)`'s result is now capped on both ends -- the existing 280px floor plus a new 460px ceiling -- with overflow relying on the `ListCtrl`'s own horizontal scroll rather than a frame resize. `wx.ListCtrl` report mode has no built-in per-cell wrap (that's a `wx.grid.Grid` feature, not applied here), so cap-plus-shorten is the practical equivalent without a heavier widget swap. Prior entry (v0.16.2): real reported bug fix -- editing a screen with an unresolved/unknown field ID pushed the whole window off the left edge of the screen, with a large gap between the field list and the diagram, and the diagram column stretched wider than needed too; the oversized window then persisted across every subsequent panel. Root cause: `wx.ListBox` sizes itself to its longest item string, and `field_name()`'s default non-terse form returns a long descriptive sentence for unknown IDs (~40 chars) vs. a normal field name (~10-20 chars) -- that inflated best-size propagated through the shared-proportion `body_row` sizer (explaining why the diagram column grew too, not just the field list) into `MainFrame._relayout()`'s v0.11.0 grow-only behavior, which has no ceiling once triggered. Fixed at the source (`field_name(fid, terse=True)` in both `EditScreenPanel` and `AddScreenPanel`'s field list AND diagram labels -- "id58?" instead of the full sentence) and hardened `_relayout()` itself as defense-in-depth: growth is now clamped to the current display's usable work area, so this whole *category* of bug (any future content-driven best-size spike, not just this one) degrades to tight/scrolled content instead of an off-screen, restart-required lockout. Headless-verified (`field_name(9999, terse=True)` -> `"id9999?"`, 7 chars vs. 40 for the old form); compiled clean. Prior entry (v0.16.1): two minor UX fixes, no behavioral change -- the "no device connected" message now says "Connect your Garmin Edge device via USB" instead of naming the 530 specifically (detection has always been structure-based, not model-specific -- see "Model portability" note below); the window title now shows the running version (`f"Garmin Edge Screen Editor v{__version__}"`) so it's visible in-app, not just in the file. **Covers steps 1-10**, plus Restore-from-Backup and Clone Profile as sibling actions to editing: detect, list+backup, select+stage, view screens (Type column showing real f10-derived screen names, plus screen-level Move Up/Down reordering), add a brand-new screen, edit one screen's fields (reorder/add/remove/change type), A/B layout (live visual diagram), and Show/Hide, review accumulated changes, deploy to the device, post-write verification, restore any profile from its backup history, and clone a profile under a new name. **This closes out the GUI's full feature backlog -- nothing left unscoped.** NEW (v0.16.0): `ClonePanel` -- "Clone..." on `ProfileListPanel` patches `sport_mesgs[0].name` via `fit_clone_profile.py`'s `patch_profile_name()` (a completely different message than `data_screen` -- already CONFIRMED full-fidelity on real hardware at the CLI level, see MVP_SCOPE.md "Clone-and-retarget"). Live filename-collision validation against `frame.known_profiles` (kept fresh by `ProfileListPanel.on_refresh()` every visit) blocks "Create Clone" until the chosen filename is guaranteed not to match anything currently on the device -- deploying under an existing filename would silently OVERWRITE that profile instead of creating a new one. Auto-suggests a filename from the display name (alnum-only) but never overwrites one the user has typed directly. Sources from the selected profile's just-taken backup, never the live device file, same discipline as Stage/Restore. Hands off straight to `DeployPanel` (steps 9-10) exactly like Restore does -- no staged-vs-editing diff applies to a clone either. `frame.deploy_return_panel` gains a third value ("clone"), handled by the same context-aware Back button and belt-and-suspenders `editing_path` cleanup pattern `RestorePanel` already uses. Headless-verified against a real backup file: filename validation (missing extension, path separators, case-insensitive collision) all behave correctly; `patch_profile_name()` produces a byte-for-byte-structurally-identical clone (same screens/fields/order, only the name field bytes differ, source untouched); `describe_screen_changes()` confirms zero screen differences between source and clone, matching the confirmed real-hardware CLI result. Prior entry (v0.15.2): cosmetic doc-only fix -- `FieldPickerDialog`'s docstring said "86 confirmed entries," stale after `fit_dump.py` v2.4.3 added field 58 (Lap Timer); no functional change. v0.15.1: fixed a REAL bug found via testing (2026-08-06) -- `frame.editing_path` was only ever cleared by `DeployPanel.on_done()`, so backing out of a Restore attempt without completing it left `editing_path` pointed at the abandoned restore's backup file; since `get_working_path()` prefers `editing_path` over `staged_path`, a subsequent normal Stage then silently showed that stale leftover instead of what was just staged (reported symptom: "View Screens shows the backup I was about to restore, not what I just staged" -- it happened to produce a plausible-looking Preflight diff purely by coincidence, not because anything was actually correct). Fixed in two places: `ProfileListPanel.on_stage()` now unconditionally discards any prior session's `editing_path` before staging (the real fix -- a fresh Stage should always start clean; this also covers the same latent risk when switching to a different profile mid-session, which existed even before Restore was added); `RestorePanel.on_back()` also proactively discards when `frame.deploy_return_panel == "restore"` (cleans up immediately rather than waiting for the next Stage). v0.15.0: `RestorePanel` -- "Restore from Backup..." on `ProfileListPanel` lists the selected profile's backup history (`list_backup_history()`, newest first) with a per-candidate screen-type summary (e.g. "8 screen(s): Screen 1, Lap Summary, Map, ..."), then hands off straight to `DeployPanel` (steps 9-10), deliberately skipping `PreflightPanel` (steps 7-8) -- there's no staged-vs-editing diff to review when the user already picked a specific, known backup from a summarized list. `frame.editing_path` points at the chosen backup file directly (never copied -- `DeployPanel`/`describe_screen_changes()` only ever read it). `DeployPanel`'s "Back" button is now context-aware (`frame.deploy_return_panel`) so it returns to wherever Deploy was actually reached from. Headless-verified against real backup files (row summaries build correctly, including reflecting a screen-order swap between two backups). v0.14.0: `DeployPanel.on_check()` now re-pulls the LIVE profile from the device's `Sports/` folder the instant reconnect is confirmed, and compares it against `editing_path` (what was actually sent) via a new module-level `describe_screen_changes()` -- factored out of `PreflightPanel`'s former `_describe_changes()` so both panels share one implementation. Runs automatically on reconnect, not a separate manual step. User-confirmed design decision (2026-08-06): compares visible/active screens only, no Removed-list bookkeeping -- Garmin's own editor has no un-remove option and neither does this GUI, so the device's known Removed-list wipe on NewFiles import isn't reported; `describe_screen_changes()` already does this for free (only reports slots ACTIVE on at least one side, so Removed/Unconfigured-only transitions are invisible to it by construction) -- headless-verified by simulating the exact Removed→Unconfigured flip and confirming zero diff lines while a real field/position change on the same file pair still reports correctly. v0.13.0: `DeployPanel` (step 9) writes `editing_path` to the device's `NewFiles/` via `write_to_newfiles()` (byte-for-byte write-back verification), then walks the user through eject (confirm-then-`diskutil eject`, reusing `_volume_mount_point()` for the real ejectable target, plus an "I Ejected It Myself" fallback) and reconnect. User-confirmed design decision (2026-08-06): reconnect detection is a manual "Check for Reconnected Device" button rather than background-thread polling of `wait_for_remount()` -- this app has never used a background thread, and the manual-click tradeoff avoids introducing a new class of failure mode (thread lifetime vs. panel teardown) for the sake of a few saved clicks. `eject_device(auto_eject=True)`'s own `input()`-based confirmation isn't reused since it would hang a GUI handler -- the eject confirmation is a `wx.MessageBox` instead. "Done" clears `editing_path` (`discard_edits()`) and returns to the profile list. **CONFIRMED live on real hardware** (2026-08-06): full deploy of a new 10-field screen, plus the change summary and Fields-column fixes below, all verified end to end. v0.12.0: `PreflightPanel`'s change summary is now a plain-English, per-screen description (`_describe_changes()`) instead of a raw `fit_dump.py diff`-style unified diff -- real user feedback: the byte-level diff was too technical for the GUI's actual audience (a rider, not a developer); anyone who wants that level of detail still has the CLI tools directly. Compares the staged file against the working copy by slot (message_index) and reports plain lines like "Screen 4: added Cadence, removed Grade" or "Screen 2: moved from position 3 to position 2" -- new/removed screens, field set changes, field-order-only changes, layout A/B changes, show/hide changes, and position changes are all covered; a generic fallback line covers any future edit type not yet described in plain English, so real byte-level changes are never silently under-reported. Whether there's anything to deploy at all is still decided from the raw bytes directly, independent of the summary's coverage. v0.11.1: fixed `ViewScreensPanel`'s "Fields" column being a fixed 280px width, which silently CLIPPED (not wrapped) any screen's field list wider than ~3-4 short names -- real reported bug: a 10-field screen only showed 3 fields plus part of the 4th. `on_refresh()` now auto-sizes that column to its actual widest content on every refresh (never below the original 280px floor); overflow beyond the window's own width falls to the ListCtrl's native horizontal scrollbar instead of clipping. v0.11.0: fixed `MainFrame._relayout()` to only GROW the window when content needs more room, never shrink it -- real reported bug: manually enlarging the window (e.g. to see more of the screens list) snapped back to a smaller size on the next button click, since nearly every handler ends with `self.frame._relayout()`, which called `self.Fit()` unconditionally (Fit() resizes to the sizer's ideal size in both directions). The original v0.1.1 anti-overlap intent (grow when content needs more room) is preserved via `GetBestSize()`; only the unwanted shrink is gone. No call sites needed to change. v0.9.0: "Change Type..." on both `EditScreenPanel` and `AddScreenPanel` -- swaps one field's ID in place via the existing `FieldPickerDialog`, without the Remove+Add+reposition workaround ("Replace Field" from the original design notes, now built) -- **CONFIRMED live on real hardware** (2026-08-05), including a guard-overridden field change on ClimbPro that survived a full deploy/restart/reconnect cycle. v0.8.0: `AddScreenPanel` (step 5) replicates `--new-slot`'s exact defaulting logic via direct function calls -- picks the lowest unconfigured slot (never shown to the user), sets f1/f12 like every real device-created screen, auto-assigns collision-free f9/f10 via `next_available_field9()`/`next_available_field10()`, and enforces the confirmed 10-user-screen cap with a friendly message rather than a raw failure -- **CONFIRMED live on real hardware** (2026-08-05). v0.7.0: `ViewScreensPanel` Move Up/Down buttons swap two screens' on-device display order via `swap_display_order()` (the `--swap-order` backend) -- select-plus-buttons, same UX pattern as field reordering, enabled/disabled based on the selected row's position (top/bottom can't move further that direction). `_confirm_guard()`/`_confirm_hide_guard()` no longer show a false-positive "possibly a system screen" dialog for confirmed user screens. `on_show_toggle()` HARD-blocks (no override) hiding Map or ClimbPro at all, ahead of the last-visible-user-screen check. Deploy and restore-from-backup's picker not yet built. |

Design principle throughout: **patch bytes in place, never re-encode
the whole file.** Every edit observed on real devices — ours and the
device's own — has been a minimal, isolated byte change. The patcher
follows the same pattern: locate exact byte offsets, overwrite only
what's changing, recompute the trailing CRC, leave everything else,
including fields we don't fully understand, completely untouched.

---

## The `data_screen` message (mesg_num=14)

One message instance per screen "slot" (all ~30 preallocated from
profile creation, whether populated or not). Key fields:

| Field | Meaning |
|---|---|
| `254` | `message_index` — raw slot number. NOT stable across a NewFiles write (physically relocated during cap-eviction compaction) — never treat this as a screen's identity; use `f9` for identity/order instead. |
| `1` | Active/Removed flag (see Screen State Model) |
| `3` | Field count. Key absent entirely (not `0`) when the slot has never been configured. |
| `7` | 10-slot array of field IDs (uint16) |
| `8` | Layout variant: `0`=A/default, `1`=B/alternate. Only field counts **3, 4, 5, 6, 7** have a real B option — enforced as a hard error by the patcher if violated. |
| `9` | Screen creation-order stamp **and** literal on-device display order, ascending. Dense `0..N-1`, must be globally unique among Active screens (a duplicate is silently discarded on reboot). |
| `10` | **CONFIRMED screen TYPE identifier** (see "Screen identity — SOLVED", below) — NOT just a Conditional-state marker as earlier thought. Named Garmin types get a fixed global code (Map=25, Elevation=44, ClimbPro=104, etc.); plain user screens use a per-profile counter shown on-device as "Screen N" (`f10=N` → "Screen `N+1`"). Persists through content edits; actively re-applied when a named type is re-added from the device's own menu. `fit_dump.py`'s `NAMED_SCREEN_TYPES`/`screen_type_name()`. |
| `12` | Enabled/disabled ("Show Screen" toggle). `0`=shown, `1`=hidden. Independent of the Removed state. |
| `11` | **DISPROVEN as a user-vs-template signal** (tested on-device, side-thread, 2026-08-04) — four screens created via genuine on-device Add New all came back `f11=1`, identical to factory template screens, not absent as the earlier 2-data-point theory predicted. `f11=1` appears to be set by ANY device-side creation, template or Add New alike; doesn't distinguish authorship at all. (The user-vs-Garmin screen problem this was meant to solve is now solved anyway, via `f10` — see above.) One unexplained anomaly remains: Indoor profile slot 2 has `f11=2`, the only such value seen across 114 sample files — unresolved, unrelated to either theory. Unused by the toolkit. |

## Display order — solved

**Field `9`, ascending, is the literal on-device viewing order.**
Confirmed by matching a user-verified on-device editor sequence
exactly, and by a real device round-trip (`--swap-order`, swapping two
screens' `f9` and nothing else) producing the exact predicted
on-screen position swap.

## Screen State Model — three states, not two

| State | `f1` | `f9` | `f10` | Notes |
|---|---|---|---|---|
| **Active/Display** | `1` | real, unique | real | Normal, in the ordered sequence |
| **Conditional** (e.g. GroupTrack) | `1` | absent | **real** (seen: `32`) | Active feature, structurally exempt from ordering |
| **Removed** | `0` | absent | absent | Content (`f3`/`f7`) preserved -- ONLY until the next NewFiles-mediated write (see correction below) |

"Removed" is a soft delete — field count and the field ID array
survive completely intact at the moment of removal. Discovered via the
on-device "Remove" button; independently confirmed by finding this
exact signature on five "orphaned" screens in a real profile, and
again — byte-for-byte identical — on a **brand-new profile built
fresh from Garmin's own template with zero edits**. Every profile
ships pre-populated with these in the Removed state; it has nothing to
do with a user's own edit history.

**CORRECTION (2026-08-04, side-thread finding):** an earlier version
of this document implied Removed content is stably, indefinitely
preserved. That's wrong. **A NewFiles-mediated deploy purges whatever
is currently in the Removed state, every time — not a one-time
cleanup, but standing behavior of the NewFiles import/rebuild
pathway** (the same pathway already documented below as the root cause
of the Add-New-Screen failure). Confirmed via two independent Sandbox
deploys, each wiping a *different* Removed-state screen the deploy
itself never touched — once on long-standing factory-template content,
once on a screen the developer had Removed on-device only seconds
earlier. Both came back fully **Unconfigured** (not Removed, not
present at all) after the deploy and restart, even though neither
deploy edited that screen. Crucially, this is specific to the
**NewFiles pathway**, not to "any device write": Removed screens
edited or created purely through the on-device editor (no toolkit
deploy involved) are left alone and continue to show up normally in
`fit_dump.py screens`'s Removed section. Only a *toolkit*-mediated
deploy — a field edit, a layout change, a Show/Hide toggle, a reorder,
completely unrelated to the Removed screen itself — triggers the
purge. **Practical implication:** since most profiles ship with at
least one Removed-state screen from their factory template, any GUI
deploy of any kind will likely purge it, silently. Not a reason to
avoid the toolkit's core editing capabilities — none of them relied on
Removed content surviving — but worth knowing before treating a
Removed screen as a safe, permanent fallback.

A structurally normal Active screen is not a guarantee it will show
while riding, either: on the Indoor profile, Map and Elevation are
both ordinary Active screens (real `f9`) that never appear live —
confirmed there's a separate, undocumented runtime filtering layer
(near-certain cause on Indoor: GPS-dependent screens auto-suppressed
on a trainer profile) that nothing in `data_screen` predicts. This is
a real limitation of what the file format can tell you, not a bug in
the toolkit.

---

## Adding a new screen — CONFIRMED WORKING (2026-08-05), root cause revised

**Status as of `fit_patch.py` v1.12.0: activating a brand-new screen
via `--new-slot` and pushing it through NewFiles is CONFIRMED to
survive a live device round-trip**, including on a profile already
touched by NewFiles many times before. Test: `CyclingRoadSandbox`,
2026-08-05 — `--new-slot --slot 6 --fields 178,179 --field10 2`
(fields Gears/Front Gear; f10=2, collision-free, shows on-device as
"Screen 3"). After deploy → automatic restart → power-cycle → remount,
the new screen was present and correct, verified two independent ways
against the live mounted `/Volumes/GARMIN/Garmin/Sports/` file: once
via `fit_dump.py screens` run directly against that path, once via
`garmin_device.py screens` (which also reads the live device, no
staging). Both agreed exactly. The only side effect was the profile's
Removed-state screen being purged — already-known standing behavior of
*any* NewFiles deploy, unrelated to this change (see Screen State Model
above).

**Root cause, revised.** The previous conclusion — reached before f10's
meaning was understood, and documented for a long time as settled and
root-caused to the NewFiles delivery mechanism itself — turned out to
be explainable by something much narrower: `--new-slot`'s old default
silently wrote f10=0 whenever `--field10` wasn't given explicitly. f10
is a real, specific per-profile identity (0 = "Screen 1"), not an
inert sentinel as assumed when that default was written, and almost
every real profile already has a Screen 1. Writing a second screen
with the same f10 collides with that identity, and the device's
NewFiles reconciliation appears to merge/discard on that collision —
which matches every observed failure signature (new content vanishing,
sometimes grafted onto or destroying whichever existing slot shared the
colliding identity). `fit_patch.py` v1.12.0's `next_available_field10()`
auto-assigns a collision-free value instead, fixing this at the source.

**Loose end, noted for honesty rather than swept under the rug:** an
earlier test (predating this section's original writeup) reported that
a *synthetic* push built to byte-match a genuinely successful native
on-device "Add New" — same `f9`, same `f10`, same `f12`, same byte
positions, confirmed via a full whole-file diff — still failed when
delivered via NewFiles. If that test's f10 really was captured from a
successful native add, it would by definition already have been
collision-free, which the new theory doesn't obviously explain. Since
that older result can't be re-examined byte-for-byte here (it predates
this project's current file set), and the new result is fresh,
reproducible, and independently double-confirmed against the live
device by two separate tools, the new result is what current guidance
is based on — but this discrepancy is worth keeping in mind if a future
`--new-slot` attempt fails despite a collision-free f10. Possible
explanations not yet ruled out: some other field besides f9/f10/f12
mattering, a difference in which slot/`message_index` the synthetic
push targeted versus where the device itself placed the real one, or
NewFiles behavior that isn't fully deterministic across firmware
versions or profile history.

**Practical guidance:** `--new-slot` no longer requires manually
computing `--field10` — the auto-default handles it — but verify with
`fit_dump.py screens` and `fit_crc.py` before every deploy regardless,
same discipline as any other change, and expect the Removed-screen list
to be purged as a side effect. `--un-remove` shares the same fixed
default but has NOT itself been re-tested live since the fix — treat
it as unverified-but-plausibly-fixed until it has been.

**Product note on `--un-remove`, added after further side-thread
testing (2026-08-05):** Garmin's own on-device editor has no
un-remove option at all — Hide (temporary) and Remove + Add New
(permanent) are the only workflows it exposes. Two related, now-
confirmed facts: a factory-shipped profile's Removed list already
contains a few entries the user never touched (seen on a brand-new
template with zero edits), and that list survives ordinary on-device
editing (adding screens, changing fields, etc.) but is wiped the
moment the profile goes through NewFiles, regardless of what the
NewFiles-mediated change actually touched. Together these suggest
Garmin itself may not treat "Removed" as a meaningfully distinct,
user-facing state the way this toolkit has had to reverse-engineer it
as. Current lean: keep `--un-remove` in the codebase for deliberate
future testing, but likely don't expose it as a first-class GUI
feature — final call deferred, not yet made.

**Design decision, updated -- DONE (2026-08-05, gui_app.py v0.8.0):**
built a real Add-New-Screen panel (`AddScreenPanel`) rather than
redirecting the user to the on-device "Add New" menu, which was the
prior design's workaround for what's now a fixed limitation. Picks the
lowest unconfigured slot automatically (never shown to the user), lets
the user set fields/layout via the same widgets EditScreenPanel uses,
and auto-assigns f9/f10 via the fixed `next_available_field9()`/
`next_available_field10()`. Enforces the confirmed 10-user-screen cap
with a friendly message. Verified headlessly (replicated the panel's
exact call sequence outside wx, since wxPython can't be installed in
the dev sandbox) against a clean profile copy -- output byte-shape
matched the live-tested CLI success exactly (f1/f9/f10/f12 set the
same way, only the target slot touched, CRC valid). **CONFIRMED live
through the actual GUI widgets on real hardware (2026-08-05,
CyclingRoadSandbox)**: created a new screen via the GUI, deployed
through the normal eject/restart/remount flow, and verified on-device
-- the Active ride profile shows the new screen at the right position
with the correct fields. Add-New-Screen is now fully validated at
every level: fit_patch.py backend, headless GUI-logic replication, and
the real GUI end to end.

---

## Write path

- **Direct overwrite is unreliable** — works once, then permanently
  stops taking effect for a given profile once it's been touched by
  NewFiles even a single time.
- **NewFiles is the reliable path** — copy the patched file into the
  device's `NewFiles/` folder using the profile's exact existing
  filename, eject, restart.
- **Device quirk (important for the GUI):** after ejecting, the
  device auto-restarts to run the NewFiles import, but does **not**
  remount as USB storage on its own afterward — it settles into
  charging mode. It needs exactly **one power-button press**, after
  the restart finishes, to come back as a mounted drive. Any GUI must
  surface this instruction explicitly or a user will be stuck
  watching a spinner that never resolves.
- **Timestamps:** the `Sports` folder's timestamp updates on *any*
  restart (not diagnostic). The `Backup` folder's timestamp updates
  *only* on a genuine content change — a reliable signal, confirmed
  via a clean no-op control test and multiple real edits.
- **Screen-count cap: CONFIRMED via real testing.** 10 fields per
  screen, and 10 USER-definable screens per profile. Additional
  Garmin-predefined/overlay screens are allowed beyond that 10 and do
  NOT count against it -- consistent with the Conditional screen
  state and the pre-Removed factory-shipped screens already documented
  in the Screen State Model above. This resolves the earlier "not
  fully pinned down" uncertainty (a flat 13-total-slots cap was ruled
  out -- a 17-screen profile was fine -- and an isolated eviction had
  been observed at only 6-7 user screens on another profile; the
  10-user figure is the real, confirmed cap, with the earlier
  early-eviction case likely reflecting NewFiles' own rebuild trigger
  interacting with something else, still not isolated in detail but no
  longer the open question it was). When eviction does happen: the
  lowest-`f9` screen is evicted and every remaining `f9` is renumbered
  to close the gap (same renumbering also happens on a plain native
  Remove, not just via NewFiles).

---

## Field ID dictionary

105 of an estimated ~200 possible field IDs confirmed (this count was
stale here for several updates -- last synced 2026-08-10; `fit_dump.py`
itself is always the source of truth via `len(FIELD_ID_NAMES)`),
cross-referenced against on-device visual verification across six
profiles (Road, Gravel, Tourtst, Mountain2, Indoor, plus the 2026-08-10
census pass on a Sandbox clone). Full table lives in
[`FIT_PATCH.md`](FIT_PATCH.md).

Lessons from the census process worth remembering for future work:
- Don't assume a field's position in the raw storage array matches
  its on-screen display position — caused one real mis-identification,
  corrected via on-ride photo verification against a second,
  independent screen using the same field.
- An on-device UI marker (a `*` shown only in the field picker, never
  while actually riding) revealed two field IDs (348/349, "Speed
  \*"/"Cadence \*") that would otherwise have looked like duplicates
  of already-known ones (48/3).
- **DONE (2026-08-10)** — 18 new field IDs confirmed in one batch: 7
  Lap Dist., 30 Time to Next, 31 Dest. Location, 39 Lap Power, 50 Lap
  Speed, 57 Avg Lap Time, 61 Total Descent, 62 Dest. Ahead, 63 Time
  Ahead, 67 Reps to Go, 86 Last Lap Speed, 88 30s VAM, 94 ETA to Next,
  95 Odometer, 295 Target Power, 442 Lap VAM, 443 Avg VAM, 445 Asc to
  Next Crs Pt. Method: arranged two screens to 10 fields each on a real
  profile specifically for this census, entered/selected each field by
  its on-device name (so the name itself came straight from Garmin's
  own UI, not a guess), then cross-referenced each field's raw ID
  against its known on-screen position using this toolkit's own GUI —
  the same direct-verification standard as every other entry, just
  batched at scale rather than one disposable test screen per ID. This
  batch is also what surfaced the two window-sizing bugs fixed in
  `gui_app.py` v0.16.2/v0.16.3 (a screen with 9 of 10 fields unresolved
  was an unusually good stress test for exactly that failure mode) —
  see the toolkit table entry for those versions. `FIELD_ID_NAMES` now
  105 confirmed entries; `KNOWN_UNRESOLVED_IDS` still empty.
- **DONE** — the last deliberately-unresolved IDs, 84/87 (seen on
  GroupTrack's Conditional record), were closed 2026-08-04 via a
  forced-field test screen deployed successfully through NewFiles,
  rather than waiting on a live multi-rider session: `84` = Last Lap
  Dist, `87` = Last Lap Timer. Turned out to have nothing to do with
  GroupTrack at all — they'd only been assumed GroupTrack-related by
  association with the screen they happened to be seen on. Lesson:
  don't assume a field's meaning from which screen it's seen on,
  especially a Conditional-state one — the safer, faster path (a
  disposable forced-field test, the same low-risk method used for the
  VAM/Lap Cadence/Max Speed/Lap Flow census) should have been tried
  before assuming a live session was the only option.

---

## On-device layout geometry

Supplied directly by the developer as a text-based Edge 530 reference
(one entry per field count, A/B where applicable) and encoded as
`LAYOUT_GRIDS` in `gui_app.py`, driving the GUI's live layout diagram.
Cross-checked against `fit_patch.py`'s `COUNTS_WITH_B_VARIANT` (3, 4,
5, 6, 7 have a real A/B choice) — matches exactly, no discrepancies.

| Count | A (or only) layout | B layout |
|---|---|---|
| 1 | 1 full-width row | — |
| 2 | 2 full-width rows | — |
| 3 | 3 full-width rows (equal) | 3 full-width rows (top field renders smaller — not a row/column difference, just a size one) |
| 4 | 4 full-width rows | row1: 2 side-by-side, rows 2-3: full-width |
| 5 | 5 full-width rows | rows 1-2: full-width, row3: 2 side-by-side, row4: full-width |
| 6 | rows 1-4: full-width, row5: 2 side-by-side | row1: 2 side-by-side, rows 2-3: full-width, row4: 2 side-by-side |
| 7 | rows 1-3: full-width, rows 4-5: 2 side-by-side each | row1: 2 side-by-side, row2: full-width, rows 3-4: 2 side-by-side each |
| 8 | rows 1-2: full-width, rows 3-5: 2 side-by-side each | — (no B variant) |
| 9 | row1: full-width, rows 2-5: 2 side-by-side each | — (no B variant) |
| 10 | rows 1-5: 2 side-by-side each | — (no B variant) |

This also confirms two hard caps via real device testing, not just
inference: **10 fields per screen**, and **10 user-definable screens
per profile** (additional Garmin-predefined/overlay screens are
allowed beyond that 10 and don't count against it) — see Write Path,
below, which previously had this only partially pinned down.

---

## Activity Profile settings (outside `data_screen`)

- `sport_mesgs` (`mesg_num=13`), field 53 = Segments toggle
  (1=on/0=off). Large, sparse message (~40 fields); the rest is
  unmapped and out of scope for now.
- `training_settings_mesgs[0]`, field 63 = ClimbPro toggle
  (1=on/0=off) — a **different** message than Segments. (An early
  test showed zero diff and briefly suggested a device-wide setting;
  it turned out to be an accidental duplicate file upload, caught via
  a CRC check. Treat any "zero difference" toggle result as suspect
  until file identity is verified.)
- `mesg_num=280`: likely a Power Curve cache (3 rolling time windows,
  15 shared duration-bucket boundaries, monotonically decreasing peak
  wattage per window). Populated only when real ride data exists and
  Graph-type fields are active. Tangential to the core goal, not
  pursued further.

## `startup.txt` — custom boot message (documented, not yet built)

Outside `data_screen` entirely, and outside any Activity Profile too —
a plain-text file, not a `.fit` file, living at the device-root level
(alongside the `Garmin` folder itself, not under `Sports/`/`NewFiles/`
where every other file this toolkit touches lives). Displays a
custom message at device boot. Discussed 2026-08-06 as a candidate
GUI feature (see Open Items / GUI scoping below for the "Show
startup.txt" button design) but deliberately held until now — nothing
below has been confirmed against real hardware by this project yet,
unlike everything else in this document.

**Syntax:** a `<display=N>` directive controls how many seconds the
message shows at boot (a duration, not a screen-position or content
directive).

**Limits, per Garmin Support + community testing (GPLama) — supplied
by the developer 2026-08-07, not yet independently confirmed on real
hardware by this project:**

- **256 characters total**, across the entire custom text area.
- **7-bit ASCII only** — standard letters/numbers/basic punctuation.
  Special characters, emojis, or extended-ASCII text-art won't render
  correctly.
- **No hard line-count cap in the file itself** — but the physical
  screen truncates anything beyond its own layout allocation, and that
  allocation is **model-specific**:

| Edge model | Max visible lines |
|---|---|
| Edge 520 / 820 | 5 |
| Edge 530 / 830 / 1030 | 6 |
| Edge 800 | 7 |

This is the same shape of problem as the "Model portability" Open Item
above — a real constraint that varies by physical device, not
something `data_screen`/field-count logic predicts — and would fit the
same eventual `DEVICE_PROFILES`-keyed-by-`garmin_product` approach if
that ever gets built, rather than needing its own separate mechanism.
For now, since the 530 is the only confirmed/owned device, a future
"Edit startup.txt" GUI feature could hard-code the 530's own limits
(256 chars, 6 visible lines, 7-bit ASCII) as a live character-count/
line-count warning while typing, without needing the full
`DEVICE_PROFILES` machinery just for this one file.

**Open questions before building the edit/create half (see Open Items
below for the full GUI feature sketch):** the exact on-device path
(device-root relative to `find_garmin_root()`, not yet confirmed
directly), and whether a write needs the same eject/power-button/
remount cycle every other write in this project does, or takes effect
some simpler way. Both are quick real-device checks, not open-ended
unknowns.

## Screen identity — SOLVED via field 10 (f10)

**CONFIRMED (side-thread Test 4, 2026-08-04) — this section previously
called the problem unsolvable at the file-format level; it isn't.**
Field 10 (f10) is a real, content-independent screen TYPE identifier,
fully independent of `f9` (display order):

- **Named Garmin screen types** get a FIXED global code, the same
  value regardless of profile/template or what content the user has
  since customized the screen to show. Proven, not inferred: patching
  Cycling Dynamics' fields via `--force` and redeploying left `f10`
  unchanged at 63 -- the tag marks *type*, not *displayed content*.
  Also actively RE-APPLIED, not just inherited from original template
  creation: removing GroupTrack List on-device and re-adding it from
  the device's own named-screen menu brought it back tagged `f10=57`
  again, not the next free counter value.
- **Plain user-created screens** use a per-profile, zero-indexed
  counter; the on-device editor displays `f10=N` as "Screen `N+1`"
  (confirmed exactly across 6 independent instances on one profile, no
  exceptions).

Ten named types confirmed so far (see `fit_dump.py`'s
`NAMED_SCREEN_TYPES` / `screen_type_name()`):

| f10 | Screen type | f10 | Screen type |
|---|---|---|---|
| 25 | Map | 57 | GroupTrack List |
| 26 | Virtual Partner | 63 | Cycling Dynamics |
| 32 | GroupTrack (Conditional record) | 74 | Lap Summary |
| 35 | Compass | 104 | ClimbPro |
| 44 | Elevation | 56 | Segment |

This directly fixes `would_hide_last_visible_screen()` (see
`fit_patch.py` v1.9.0, CORRECTIONS below) -- "how many real user
screens does this profile have left" is now a straightforward f10
filter, not a guess, and it only counts plain `Screen N` entries, not
every visible screen of any kind.

**Also fixes `check_system_screen_guard()` (v1.10.0), confirmed via
real GUI testing:** the pre-f10 heuristic guard (content-pattern match
OR field count ≤2) fired on ANY low-field-count screen, including
genuine user screens -- exactly the false positive it was designed to
avoid, just moved rather than eliminated. The guard now checks f10
first: a confirmed plain user screen gets NO warning at all, and a
confirmed named Garmin type gets a CERTAIN message naming it directly
rather than a guess. The old heuristics are now a fallback used only
for Removed-state slots, which have no real f10 to read.

### GroupTrack — two independent structural representations

`f10=32` is the real Conditional-state runtime record (`f1=1`, `f9`
absent, `f10` real) -- exempt from `f9` ordering entirely. Its two
fields, 87 and 84, are now resolved (Last Lap Timer, Last Lap Dist --
confirmed 2026-08-04 via a forced-field test rather than waiting on a
live multi-rider session) and turn out to have nothing to do with
GroupTrack at all; they'd only been assumed GroupTrack-specific by
association with the screen they were seen on. `f10=57`, "GroupTrack
List," is a SEPARATE,
always-orderable Active screen (real `f9`) that's simply excluded from
the active-ride scroll list by firmware, the same pattern as ClimbPro
and Segment below. Confirmed structurally independent: removing
GroupTrack List on-device and re-adding it left the `f10=32` record
completely unaffected.

### ClimbPro, Segment — conditionally visible, structurally ordinary

Both (`f10=104` and `f10=56`) are structurally normal Active screens
(real `f9`, real `f12`), indistinguishable from any other screen by
shape alone -- their "only visible under some condition" behavior
(entering a qualifying climb; entering a course segment, per Garmin's
own Edge 530 manual) is pure firmware logic layered on top, nothing in
`data_screen` predicts it. ClimbPro additionally: content-identical to
a plain Elevation overlay by default (Grade + Elevation) since content
is freely customizable regardless of type tag; and has at least two
more on-device-only behaviors never reflected in `data_screen` -- an
"Upcoming Climbs" list screen inserted when a qualifying course is
loaded, and a scrollable-away-from (not full-takeover) hijack of the
display while actually climbing.

**ClimbPro has two entirely separate on/off controls, confirmed
directly on-device, not to be conflated:** an overall profile-wide
enable/disable that lives one level up in the Profile menu
(`training_settings_mesgs[0]` field 63) -- and, within the per-screen
Data Screens editor itself, **no Show Screen toggle at all** for
ClimbPro's own screen entry, same as Map (below). `fit_patch.py`
v1.11.0's `hide_unsupported_screen_type()` hard-blocks `--hide` on
ClimbPro for exactly this reason -- forcing `f12=1` on it would
produce a state with no on-device action to compare it against.

### Map, Compass, Virtual Partner

Map (`f10=25`) has **no Show Screen toggle at all, on ANY profile
type** -- confirmed directly on-device, not a per-profile-type
exception. `hide_unsupported_screen_type()` (`fit_patch.py` v1.11.0)
hard-blocks `--hide` on Map for exactly this reason, universally.

**What the Indoor profile actually does is a different mechanism
entirely, not a Show Screen toggle:** it exposes a control that
changes Map's state between "Always" and "While Navigating" -- a
genuinely different axis (when Map is relevant, not whether it's
shown/hidden in the reorderable sense this project's `f12` models).
**Working hypothesis, not yet confirmed:** this may be exactly what
sets `f11=2` on Indoor's slot 2 -- the only occurrence of that value
across all 114 sample files (see Open items) -- i.e. Garmin may be
using `f11` as the field for this specific state, on this specific
screen type, rather than reusing `f12`. Not yet tested directly (would
need toggling Indoor's Map between Always/While-Navigating on-device
and diffing the result). Compass (`f10=35`) is
structurally ordinary, nothing special. Virtual Partner (`f10=26`) is
structurally DIFFERENT from every other screen in this project: no
`f3`, `f4`, `f7`, `f8`, or `f11` at all -- just `f1`, `f9`, `f10`,
`f12`, `254`. It has no editable field list (hence no field picker
on-device), but DOES have real Reorder and Show/Hide controls (`f9`
and `f12` are both present and real). Its displayed content (Dist
Ahead/Time Ahead) and its speed setting are both firmware-rendered
from a separate, not-yet-located profile-level setting, the same
pattern already established for the Segments toggle
(`sport_mesgs`) and ClimbPro's toggle (`training_settings_mesgs`) --
neither lives in `data_screen`.

**Bug this uncovered:** `classify_screens()` (`fit_dump.py`) and
`read_current_state()` (`fit_patch.py`) both used to gate
configured/Active status on field 3 (`f3`) presence. Virtual Partner's
missing `f3` caused it to silently vanish into "unconfigured" in both.
Fixed in `fit_dump.py` 2.4.1 / `fit_patch.py` 1.9.0 -- both now gate on
`f1`/`f9`/`f10` instead, confirmed via live RoadClone data (Virtual
Partner now appears correctly in the reorderable list) and a synthetic
regression test covering all four states.

---

## Device connection layer (`garmin_device.py`)

Automates the full manual workflow this project used throughout
testing, and is now confirmed **end-to-end on real hardware**: detect
(+ `get_device_info()` — manufacturer/product/serial/software version,
for a multi-device user to confirm the right one is connected) → back
up all profiles to a working directory (never `/tmp`) → let the user
pick one → view current screens → stage a patched copy (tagged with
exactly which backup it was derived from, preventing a repeat of an
earlier v5/v6 chaining mistake where the source backup for a patch got
lost track of) → verify the device is still connected → write to
`NewFiles` with an immediate read-back verification → prompt for eject
(never silent/automatic without confirmation) → poll for reconnect,
with the power-button instruction surfaced explicitly → re-dump to
confirm the change landed, both byte-level and visually.

Also hardening-tested: a disconnect mid-deploy fails cleanly with no
corruption, and `--auto-eject` correctly asks for confirmation before
running.

Detection is structure-based (looks for `Sports/` + `NewFiles/`
directories, checking up to two levels of nesting) rather than
name-based, so it doesn't depend on what the volume happens to be
called. macOS is implemented and confirmed working on real hardware
for the full pipeline; Windows support is a single clearly-marked stub
function (`_find_garmin_root_windows`), everything else in the file is
OS-agnostic.

---

## Corrections and lessons learned

Kept deliberately, for pattern-recognition on future work:

- **Hardcoded slot-number labels were wrong twice.** An earlier
  `SYSTEM_SLOT_HINTS` table in `fit_dump.py` (e.g. "slot 8 =
  terminator", "slot 10 = GroupTrack") was confirmed wrong on the
  Indoor profile — slot 8 there is a genuine populated screen, slot 10
  a genuine Cadence screen. Slot numbers are **not** stable across
  profiles; this had been documented as a risk once before but not
  acted on until it broke on real data. It was removed entirely and
  replaced with the structural (f1/f9/f10-based) Conditional
  classification, which found the real GroupTrack signature correctly
  with zero dependency on slot number.
- **`diskutil eject` needs the volume mount point, not the deeper
  functional root.** `garmin_device.py` originally tried to eject
  `garmin_root` (e.g. `/Volumes/GARMIN/Garmin`); the real Edge 530
  mounts one level deeper than the ejectable volume
  (`/Volumes/GARMIN`). Fixed with a `_volume_mount_point()` helper
  used only for eject.
- **The power-button remount step wasn't obvious from the first
  successful test** — Doug pressed the button without mentioning it,
  so the requirement only surfaced when a later inconsistency prompted
  asking directly. Now stated explicitly in `eject_device()` and
  `wait_for_remount()` output, and in this doc.
- **A one-way "grow, never shrink" fix (v0.11.0) had no ceiling until
  v0.16.2.** The v0.11.0 fix (never shrink a manually-enlarged window)
  and the v0.11.1 fix (auto-size the Fields column to its content) were
  each correct in isolation, but combining "the window only ever grows"
  with "a widget's reported size is driven by its content" meant any
  content that could transiently demand too much room would inflate
  the window PERMANENTLY, with no automatic way back -- which is
  exactly what happened in v0.16.2 (an unresolved field ID's verbose
  label blew out `wx.ListBox`'s best-size). The narrow fix (shorter
  labels) addressed this one trigger; the general fix (clamp growth to
  the display's work area in `_relayout()` itself) addresses the whole
  category, so the next unanticipated wide-content case degrades
  gracefully instead of requiring another bug report and an app
  restart. Lesson: a one-directional size policy needs an explicit
  ceiling from the start, not just a floor.
- **A confidently-stated assumption in a code comment (v0.11.1) turned
  out to be wrong, and the FIX for it (v0.16.3) made a second wrong
  assumption of its own -- three unverified claims about the same
  widget's behavior in three days, each one caught only by real
  testing, not by review.** The v0.11.1 comment claimed a `wx.ListCtrl`
  in report mode never grows the FRAME from column content -- "if
  that's wider than the window can show, the ListCtrl's own native
  horizontal scrollbar takes over rather than clipping." True for
  ordinary field lists, false for a real profile with 9 of 10 fields
  unresolved on two screens (v0.16.3's bug report). v0.16.3's own fix
  then claimed capping the column's width would make "content past the
  ceiling rely on the ListCtrl's own native horizontal scroll" --
  ALSO false: a capped column just clips its cell text with no wrap and
  no ellipsis, since the control's real horizontal scrollbar only
  engages when the SUM of every column's width exceeds the control's
  own rendered area, a completely different, coarser trigger than "one
  cell's text doesn't fit." Confirmed the hard way (2026-08-10): real
  testing on newly-added longer field names showed only 6-7 of 10
  fields, silently truncated, no scrollbar, no error. The actual fix
  (v0.16.6) had to stop trying to control the FRAME by capping the
  COLUMN at all -- the two need to be decoupled at a different layer
  entirely (a `DoGetBestSize()` override), not reasoned about via
  assumptions about how the column and the scrollbar interact. Lesson,
  sharpened from the first time this happened: "the framework handles
  this automatically" claims about a specific widget's behavior deserve
  the same skepticism this project already applies to file-format
  claims, AND a fix built on top of an unverified assumption can just
  as easily introduce a second one -- the fix itself needs the same
  scrutiny as the bug it's fixing, not a pass because it's "the fix."
- **An early `git init` was accidentally scoped to the home
  directory** instead of the project folder — caught via an obviously
  too-broad untracked-file list (personal `Documents/`, `.ssh/`, etc.)
  before any commit landed. Fixed by deleting that `.git` and
  reinitializing directly in `garmindev`.

---

## Open items

- The very first test profile's original opening screen (WindField
  Widget, evicted during early cap-testing on "Roadtest") is
  recoverable from a full external device backup, if wanted.
- **DONE** — the screen-count cap itself is now confirmed (10 fields/
  screen, 10 user screens/profile, see Write Path above). The
  narrower residual question -- why one early test ("Roadtest")
  evicted at only 6-7 user screens rather than the full 10 -- is still
  unexplained, but no longer blocks anything; not worth pursuing
  further given the eviction risk of testing it directly.
- **DONE** — the last two unidentified field IDs, 84/87 (seen on
  GroupTrack's Conditional record), resolved 2026-08-04: `84` = Last
  Lap Dist, `87` = Last Lap Timer, confirmed via a forced-field test
  deployed successfully through NewFiles — the disposable-test method
  worked without needing a live multi-rider session after all. Turned
  out unrelated to GroupTrack itself, just two ordinary lap-stat
  fields that happened to appear on that particular screen.
  `FIELD_ID_NAMES` now has 86 confirmed entries;
  `KNOWN_UNRESOLVED_IDS` is empty.
- **DONE** — field `58` = Lap Timer, resolved 2026-08-06: surfaced
  incidentally by real GUI testing (Restore-from-Backup on a restored
  8/3/2026 `CyclingRoadSandbox` backup showed a field the GUI's picker
  didn't recognize), confirmed via direct visual comparison against
  the live device display (`fit_dump.py` 2.4.3). Not the result of an
  active field-ID hunt -- those stay in the other thread per the
  earlier decision to keep this thread focused on GUI work.
  `FIELD_ID_NAMES` now has 87 confirmed entries.
- **DONE** — user-built vs. Garmin-authored screen identification,
  previously this section's biggest open question, is now solved via
  `f10` (see "Screen identity — SOLVED", above).
- **DONE (2026-08-05)** — Add-New-Screen via `--new-slot`/NewFiles,
  previously documented as a settled, root-caused hard limitation, is
  now CONFIRMED WORKING. Root-caused to an f10 identity collision
  (old default wrote f10=0, colliding with the profile's existing
  "Screen 1"), fixed via `next_available_field10()` in `fit_patch.py`
  v1.12.0, verified via a live on-device round-trip. One honest loose
  end remains -- an earlier, exact-byte-match synthetic push also
  failed and isn't fully explained by this theory -- see "Adding a new
  screen" above. `--un-remove` shares the fix but hasn't itself been
  re-tested live yet.
- **Indoor profile's Map "Always"/"While Navigating" state, and the
  slot-2 `f11=2` anomaly — likely the same open question, not yet
  confirmed.** Map has NO Show Screen toggle on any profile type
  (confirmed, now hard-guarded in the toolkit -- see "Map, Compass,
  Virtual Partner" above), so what the Indoor profile actually exposes
  for Map is a different control entirely: a toggle between "Always"
  and "While Navigating," not a show/hide in the `f12` sense. Working
  hypothesis: this may be what sets `f11=2` on Indoor's slot 2 -- the
  only occurrence of that value across all 114 sample files, previously
  logged as a bare anomaly with no theory attached. Next step to
  confirm: toggle Indoor's Map between Always/While-Navigating
  on-device and diff the result -- now trivial to locate by name via
  `f10=25` in `screens` output, whereas previously it required guessing
  among several 0-field candidates.
- `sport_mesgs`' other ~39 fields (name/color/ride type/alerts/auto
  features/etc.) remain unmapped — same toggle-and-diff method would
  work, low priority, outside the core Data Screens MVP.
- Where Virtual Partner's speed setting (and the Segments on/off
  toggle) actually live is still unknown — confirmed NOT to be in
  `data_screen` itself (Virtual Partner has no `f3`/`f4`/`f7`/`f8`/`f11`
  at all to hold it), same unresolved-location pattern as ClimbPro's
  toggle before it was traced to `training_settings_mesgs`. Not chased
  down yet; low priority.
- The Map "(Always)" vs. "(when navigating)" qualifier text seen in
  the on-device editor is a distinct, UI-only axis not yet traced to
  any byte field — low priority.
- **Publishing to GitHub — license/disclaimer landed (2026-08-11).**
  Doug asked about licensing/hosting ahead of a possible public
  release. Landed: `LICENSE` (MIT, standard "AS IS" no-warranty text,
  copyright holder `Doug (fullcarbonbike)` — Doug's own choice, name
  and GitHub handle together), a License/Disclaimer section merged
  into `README.md` (right after the intro, before Setup — "not
  affiliated with Garmin" trademark disclaimer, black-box
  reverse-engineering method note, device-write use-at-your-own-risk
  warning; reviewed and approved by Doug; `README_DISCLAIMER_DRAFT.md` is now
  superseded and can be deleted), and the `gui_app.py` v0.16.7
  window-title rename ("Activity Profile Screen Editor for Garmin
  Edge" -- the standard nominative-fair-use "for X" pattern,
  user-confirmed over two other candidates). Researched (not just
  assumed) before drafting: Garmin's SDK Terms of Use prohibit reverse-
  engineering the SDK *software* itself, but this project never did
  that -- it used `garmin_fit_sdk` as a normal dependency and separately
  reverse-engineered the undocumented `data_screen` message via
  black-box observation of real files, a meaningfully different
  activity; Garmin's separate FIT Protocol licensing is more permissive
  about building compatible tools; and several comparable community
  FIT-file tools have existed publicly on GitHub for years with no
  known enforcement action found. None of this is legal certainty --
  flagged to Doug as such. Also landed (v0.16.8): an "About" button on
  `DetectPanel` opening a short in-app summary dialog (name/version,
  trademark disclaimer, reverse-engineering method note, MIT mention)
  — Doug's own idea, matching a pattern he'd seen in other tools. Still
  open: decide whether the same rename should extend to the module
  docstring and other doc titles (only the GUI window title has been
  changed so far, scoped to what was actually asked).
- **`startup.txt` custom boot message — discussed, not yet built
  (2026-08-06/07).** Sketched design: a "Show startup.txt" button on
  `DetectPanel` (alongside Detect Garmin/List Profiles) that checks for
  the file's existence, shows its content if present or a "how to use
  this" explainer if not, with edit/create as a nice-to-have follow-on.
  See "`startup.txt` — custom boot message" above for the full
  character-limit/line-limit findings (256 chars, 7-bit ASCII, 5/6/7
  visible lines depending on model) supplied by the developer from
  Garmin Support + community testing, not yet independently confirmed
  by this project. Two quick real-device checks needed before or
  during the build: the exact on-device path, and whether a write
  needs the eject/remount cycle to take effect. Estimated small — no
  FIT parsing, CRC, or NewFiles pathway involved at all, unlike
  everything else in this toolkit. BATCHING PLAN (2026-08-11, Doug's
  decision): this is the first item slated for the next release batch,
  alongside "Restore a profile that's no longer on the device" below
  (fully scoped and de-risked, also deferred) — waiting a few days to
  see if anything else external turns up before building either.
- **Graph/Bars full-width warning (raised by Doug, 2026-08-11,
  discussed not yet built).** Doug confirmed (see the corrected "*"
  mystery note under field 348/349 above) that fields marked with a
  "*" or "(Alt)" suffix are Graph- or Bars-style fields that need a
  FULL-WIDTH screen slot to actually render as a graph/bar; placed in
  a shared/split row instead, they silently fall back to plain text
  with no on-device indication anything's wrong. UPDATE (2026-08-11,
  same day): confirmed set now stands at 10 fields following Doug's
  continued census -- 343 Heart Rate Graph, 344 Speed Graph, 345
  Cadence Graph, 346 Power Graph, 347 HR Bars, 348 Speed Bars, 349
  Cadence Bars, 350 Power Bars, 368 Elevation Graph, and 23 HR Zone
  Graph (renamed from the placeholder "Heart Rate (Alt)" now that its
  real on-device name and Graph-type nature are both confirmed).
  UPDATE (2026-08-11, same day): field 49 was checked next and turned
  out NOT to be Graph/Bars -- Doug deployed it into a full-width
  screen slot via the GUI and visually confirmed on-device it's a
  plain text "Avg Speed" value. Renamed from the old placeholder "Avg
  Speed (Alt)" accordingly. IMPORTANT METHODOLOGICAL CAUTION, not a
  falsification of the marker theory: unlike 23/348/349, there's no
  record that 49's old "(Alt)" label was ever a literal transcription
  of a real on-device UI marker -- it may simply have been an old,
  undocumented naming guess (predating this project's later discipline
  of noting confirmation method per field) that happened to reuse the
  same word. Practical implication for the eventual GUI feature: the
  confirmed Graph/Bars set (the 10 fields above) should only ever grow
  from fields where an actual on-device marker was directly observed
  and recorded at confirmation time -- an OLD placeholder name merely
  containing "(Alt)" is not itself sufficient evidence on its own.
  Question: should the GUI flag this so a user doesn't unknowingly end
  up with a "graph" field that's actually just showing a number?
  Good news on feasibility: this is fully computable from data the GUI
  already has, no new geometry model needed. `LAYOUT_GRIDS` (in
  `gui_app.py`) already represents each row as a list of field
  positions -- a row with exactly one position (e.g. `[0]`) is
  full-width; a row with more than one (e.g. `[2, 3]`) means those
  fields split the row, each less than full width. So "is position P
  full-width for this field count + A/B layout" is a small, pure,
  already-derivable lookup -- no new geometry data to maintain. What's
  actually needed: (1) a small NEW curated set (e.g.
  `GRAPH_OR_BARS_FIELD_IDS`, kept separate from `FIELD_ID_NAMES` in
  `fit_dump.py` rather than folding a category flag into it, to avoid
  touching every existing consumer of that dict) -- listing only the
  fields individually confirmed as Graph/Bars type, same discipline as
  every other confirmed entry in this toolkit's field data; (2) a
  helper function checking row membership/width for a given
  count+layout+position; (3) UI surfacing in two natural, complementary
  places -- a static note in `FieldPickerDialog` when a Graph/Bars
  field is being picked at all (independent of placement), and a
  CONTEXT-AWARE warning in `EditScreenPanel`/`AddScreenPanel` once a
  field is actually placed, reflecting whether ITS CURRENT position is
  full-width or not (recomputed whenever fields are reordered, since a
  position's row membership can change as neighbors are added/
  removed). `LayoutDiagramPanel` could optionally reinforce this
  visually later, but isn't essential to the core value. Real
  limitation to flag: the Graph/Bars membership set can only ever be as
  complete as what's been individually confirmed -- there could be
  other Graph/Bars-type fields not yet caught by the "*"/"(Alt)"
  marker pattern that simply haven't been identified yet, so this
  would have false negatives (unflagged fields that actually need full
  width) but should have no false positives (nothing flagged incorrectly).
- **"Favorite screen" -- save a screen, reuse it across profiles
  (requested by a tester, 2026-08-11, discussed not yet built).** A
  tester wants to save his favorite "dashboard" screen (a specific
  field set + layout) and add it to other profiles without rebuilding
  it field-by-field each time. Scope assessment: what actually needs
  saving is small -- just the ordered field ID list, field count, and
  A/B layout variant (f7/f3/f8's content). f9 (display order) and f10
  (screen identity) are already auto-assigned per-profile by
  `next_available_field9()`/`next_available_field10()` and must stay
  that way regardless, so a favorite is NOT a raw copy of a
  `data_screen` message, just its field-content triple. Estimated
  moderate, and smaller than either Restore-from-Backup or Clone
  Profile were, since it reuses more existing infrastructure than new:
  (1) persistence -- a small JSON favorites file (e.g.
  `~/.garmin_screen_editor_favorites.json`, list of {name, field_ids,
  layout}), same pattern as v0.16.9's new working_dir config sidecar;
  (2) capture -- a "Save as Favorite" action on an already-staged
  screen (EditScreenPanel/ViewScreensPanel already hold the field
  list + layout in memory, just needs a name prompt and a JSON
  append); (3) apply -- a "Load from Favorite..." entry point on
  `AddScreenPanel` that pre-fills its field list/layout picker from a
  saved favorite instead of building it manually, then falls through
  to the SAME already-confirmed-working add-screen path (auto f9/f10,
  10-field/10-screen caps, deploy) -- no new patch-layer logic needed
  at all; (4) favorites management -- a simple named list with
  delete/rename, same UI pattern as `RestorePanel`'s backup-history
  picker (v0.15.0), and could reuse `LayoutDiagramPanel` as-is to
  preview a favorite before applying it, since that panel already
  takes arbitrary field labels + layout + count. The one real open
  question that can't be resolved by design alone: whether a field
  that's valid/meaningful on the profile a favorite was captured from
  is still valid on a DIFFERENT profile it's applied to -- not yet
  tested cross-sport-type (e.g. a Cycling-specific field applied to a
  Running profile). Needs a real-device check before trusting this
  works generally, not just within same-sport-type profiles.
- **Restore a profile that's no longer on the device (first external
  GitHub user report, 2026-08-11, discussed not yet built).** A user
  (currently on `garmin_device.py` directly, not the GUI yet) deleted a
  profile from the device and found no way in the GUI to restore it --
  correctly identified as a real gap, not user error. Root cause:
  `ProfileListPanel`'s profile list -- the ONLY entry point into
  `RestorePanel` (via its "Restore from Backup..." button, which
  requires a selection from that list) -- is sourced entirely from
  `garmin_device.backup_profiles()`'s read of the LIVE device's
  `Sports/` folder. A deleted profile vanishes from that list
  immediately, so it can never be selected again, even though its
  backup history is still sitting untouched under
  `working_dir/backups/<timestamp>/` -- `list_backup_history()` only
  needs a profile filename + working_dir, no device dependency at all.
  So this is purely a missing GUI entry point, not a missing backend
  capability -- good news for scope. `RestorePanel` itself needs ZERO
  changes; it already only depends on `frame.profile_filename` +
  `frame.working_dir`, never on whether that profile currently exists
  on the device. What's actually needed: (1) a new
  `garmin_device.py` helper (e.g. `list_all_backed_up_profiles
  (working_dir)`) that scans every `backups/<timestamp>/` folder and
  returns the UNION of every filename ever backed up, not just what's
  live now -- small, mirrors `list_backup_history()`'s existing
  directory-walk logic closely; (2) a new GUI entry point surfacing
  profile names that are in that backup-history set but NOT in the
  current live list (i.e. "deleted" from the device's point of view),
  then setting `frame.profile_filename` to the chosen one and routing
  straight to the existing `RestorePanel`/`DeployPanel` flow unchanged.
  DESIGN CHOSEN (2026-08-11, Doug): `ProfileListPanel` gets a second,
  visually separated section below the existing "On Device" list --
  something like "Deleted, but available to restore" -- populated from
  the new backup-history-union helper minus whatever's currently live.
  Implemented as a SECOND, separate list widget with its own header
  label rather than one list with an inline divider row, deliberately
  avoiding the kind of custom-selectable-divider hackery that would
  reopen the exact class of wx.ListCtrl/ListBox trouble this project
  has already hit three times this session. The existing "Restore from
  Backup..." button and `RestorePanel` need NO changes at all -- a
  selection from either section just sets `frame.profile_filename` and
  routes to the same already-built date-history picker, which has
  never cared whether that filename currently exists on the device.
  Stage/Clone/View Screens stay gated to the top (live) section only,
  since those genuinely require the profile to currently exist.
  Net effect: no new button, no new panel -- just one new list, one
  new backend helper, and the copy fix below. Also needs a small copy
  fix either way: `RestorePanel.on_restore()`'s confirmation dialog currently says
  "REPLACING what's currently on it," which is only true for the
  existing live-profile case -- restoring a deleted profile would be
  closer to *recreating* it, not replacing anything. UPDATE
  (2026-08-11, same day): the one real open technical risk flagged
  here — whether NewFiles correctly handles a filename that isn't
  currently present in `Sports/` at all, as opposed to replacing an
  existing file — is now RESOLVED. Doug reported Clone Profile (which
  shares this exact mechanism) has in fact already been confirmed live
  on real hardware: at least two working clones, `Clonebox` and
  `CloneRoad`, both deployed under brand-new filenames via NewFiles.
  See the corrected Clone Profile entry above (which had incorrectly
  been carrying a stale "not yet tested" note) for the full
  confirmation. SECOND, MORE DIRECT CONFIRMATION (2026-08-11, same
  day): Doug tested the exact scenario this feature is about, via
  `garmin_device.py deploy <backup_of_a_deleted_profile.fit>
  <target_profile_filename>` — a backup of a profile he'd deleted from
  the device, targeting that now-absent filename. Confirmed via
  on-device verification: NewFiles correctly RECREATED the deleted
  profile, not just accepted a never-before-seen name (Clone's case).
  This is the stronger of the two confirmations, since it's the actual
  restore-a-deleted-profile path, not just an analogous one — the
  backend/CLI mechanics this feature would wrap are now fully proven
  end to end. This removes what was the single biggest open risk for
  this feature — the remaining work is genuinely just the GUI
  entry-point gap described above. Also worth a documentation caveat rather than a
  code fix: `list_backup_history()` (and any new helper built on it)
  identifies a profile purely by filename, so if a filename is ever
  reused for an unrelated profile after the original was deleted, its
  backup history would silently mix both profiles' snapshots together
  -- an existing characteristic of the backup system, not new to this
  feature, but more likely to surface once "browse backups of
  something not currently live" becomes a normal, supported action
  instead of an edge case. IMPLEMENTATION DEFERRED (2026-08-11, Doug's
  decision): fully scoped and de-risked, design chosen, but not
  urgent -- `garmin_device.py deploy` is a confirmed-working manual
  workaround in the meantime. Holding off building this alone; plan is
  to watch for anything else that turns up over the next few days and
  fold multiple changes into one future release, alongside the
  `startup.txt` feature below.
- **Reduce redundant profile backups -- LOW PRIORITY (requested by a
  tester, scoped 2026-08-11).** `ProfileListPanel` currently re-backs-
  up all profiles on every visit to the profile list, not just when
  something actually changed -- a tester reported the confusing
  side-effect directly (going back and re-selecting a different
  profile printed another "Backed up X profile(s)..." message, with no
  edits in between). Scoped fix: track a frame-level `needs_backup`
  flag, reset to `True` on either of the two real "device state may
  have changed" events -- a fresh `DetectPanel.on_detect()`, or
  `DeployPanel.on_check()` confirming reconnect after a deploy (the
  naive "just back up once ever this session" version would miss that
  second case, silently skipping the backup that captures state right
  after a real edit -- the one that matters most). "Refresh (re-backup
  + re-list)" would still always force a real backup regardless of the
  flag, honoring its own label. Contained entirely to `gui_app.py`, no
  changes needed to `garmin_device.py` or any CLI tool. Doug's call
  (2026-08-11): worth doing, but LOW priority -- his own
  `~/GarminBackups` folder is only ~1MB (plus ~160KB staging) even
  after heavy recent testing, and even the much larger prior dev
  folder (~4-5GB across 1098 `.fit` files accumulated over this whole
  project) isn't a real problem at these file sizes. The redundant
  copies are annoying (terminal noise, wasted I/O) but not a resource
  concern. Batched with the other low-priority/deferred items.
- **Backup retention/pruning.** Backups accumulate indefinitely right
  now — nothing deletes old ones. Deliberately left out of MVP.
  UPDATE (2026-08-11): Doug's real usage numbers (see above) confirm
  this genuinely isn't urgent at Garmin-profile file sizes -- even
  ~1098 backed-up `.fit` files over the life of this project only came
  to ~4-5GB. His own suggestion, worth weighing against the
  once-per-session change above: a cleanup/pruning routine (e.g.
  auto-delete backups older than N days, or cap total count/size) may
  be the more useful thing to build here than reducing HOW OFTEN
  backups happen -- it addresses the same "backups accumulate" root
  concern but as a real, permanent feature (worth having regardless of
  file-count growth over a long project lifetime) rather than a minor
  redundant-work optimization. Not yet scoped in detail; worth doing
  before the once-per-session change if only one gets built, since it
  solves a longer-term problem the other doesn't touch at all.
- **Model portability (discussed 2026-08-06, not yet built).** The
  `data_screen` layout mechanism is count-driven, not geometry-stored —
  a screen's grid shape comes from field 3 (count) + field 8 (A/B flag)
  alone, looked up against a firmware-side table (`LAYOUT_GRIDS` in
  `gui_app.py`, sourced from the developer's own Edge 530 reference),
  never computed or stored per screen. This means the *architecture*
  plausibly generalizes to other Edge models, but the *numbers*
  (`MAX_FIELDS_PER_SCREEN`, the 10-user-screen cap, which counts get a
  B variant, and `LAYOUT_GRIDS` itself) are tied to each model's actual
  screen size/firmware and do NOT — each would need its own on-device
  confirmation, same process used for the 530, before being trusted.
  `garmin_device.get_device_info()` already surfaces `garmin_product`
  (e.g. `'edge_530'`) from the device's own FIT identification message
  on every connect, so model detection itself is not a gap. Sketched
  approach for when a second model's numbers exist: a `DEVICE_PROFILES`
  dict keyed by `garmin_product`, each entry holding that model's caps/
  `LAYOUT_GRIDS`, with `edge_530` as the seed entry and an unrecognized
  model falling back to the 530's numbers with a visible non-blocking
  warning (530-as-floor is the safe fallback direction — understating a
  bigger screen's real limits is just annoying, overstating a smaller
  one's is the dangerous direction, a screen that builds fine in the
  GUI but fails/truncates on-device). Deliberately NOT built yet — no
  second model's real numbers exist to plug in, and guessing at the
  dict's shape ahead of real data would just be speculative scaffolding,
  same reasoning applied throughout this project. Doug noted he can't
  personally test other models but may be able to seed
  `DEVICE_PROFILES` with values sourced from Garmin's published specs/
  product pages online, pending confirmation from a beta tester with
  different hardware, rather than needing a live device in hand purely
  to get started.

---

## GUI scoping and implementation

**Scoping is complete; implementation is underway, one step at a
time.** `gui_app.py` currently covers steps 1-3:

- **Step 1** (`DetectPanel`) — detect device, show device info via
  `get_device_info()`. Detection is manual/on-demand (a "Detect
  Garmin" button, also fired once automatically whenever this panel
  becomes active), matching `garmin_device.py`'s own polling model —
  there's no USB hot-plug listener.
- **Steps 2+3** (`ProfileListPanel`) — list profiles and back all of
  them up in the same call (`garmin_device.backup_profiles()` already
  enumerates every profile in `Sports/` to back each one up, so the
  list shown to the user is just that result's keys — no separate,
  redundant `list_profiles()` call needed). A working-directory field
  (defaulting to the path used throughout manual CLI testing, but
  user-changeable) controls where backups and staged files land.
  Selecting a profile and clicking "Stage Selected for Edit" calls
  `stage_for_edit()` (lineage-tracked, as always). A "Restore from
  Backup..." button exists as a stub for a later slice.
- **Step 4** (`ViewScreensPanel`) — shows the staged profile's current
  screens, read-only, built directly on `fit_dump.py`'s
  `classify_screens()`/`active_field_ids()`/`field_name()` (imported
  in-process, no subprocess call). The reorderable/Active screens are
  a `wx.ListCtrl` in report mode (Pos/Slot/Count/Layout/Flag/Fields)
  — deliberately a list control even though this slice is read-only,
  since step 6's Move Up/Move Down buttons will act on whichever row
  is selected here. Conditional and Removed screens are shown
  underneath as plain text, since editing them is out of MVP scope.
  Selecting a row and clicking "Edit Selected Screen →" drills into
  step 6. A "Discard Edits" button resets the working copy back to
  the untouched staged file.
- **Step 6, partial** (`EditScreenPanel`) — edit one screen's fields
  and layout. Field list (`wx.ListBox`) with Move Up/Move Down
  (swap-fields-equivalent, no system-screen guard since a pure
  reorder doesn't change content); "+ Add Field..."/"− Remove Field"
  (both replace the whole field array via `patch_screen`, guarded by
  `check_system_screen_guard()`, with a confirmation dialog on a
  match rather than a hard block); a two-option A/B layout radio,
  auto-restricted to "B" only when the current count is in
  `COUNTS_WITH_B_VARIANT`; and a live read-only `LayoutDiagramPanel`
  showing the actual on-device grid (full-width rows vs. side-by-side
  pairs) from `LAYOUT_GRIDS`, driven by the developer's own text-based
  Edge 530 layout reference (see "On-device layout geometry", above).
  A "Show Screen" checkbox toggles field 12, matching the on-device
  wording exactly (Garmin's own UI uses "Show," not "Hide," per the
  developer). Turning it OFF (hiding) is gated two ways, checked in
  order: first a HARD, non-overridable block
  (`would_hide_last_visible_screen()`, `fit_patch.py` v1.9.0) if this
  would leave zero visible plain user screens on the profile -- now
  correctly f10-based, see "Screen identity — SOLVED" above --
  followed by `check_system_screen_guard()`'s softer heuristic
  confirm dialog for likely system/overlay content. Map is confirmed
  to have no on-device Show Screen toggle at all on standard outdoor
  profiles; forcing `f12=1` on it via a raw file write is genuinely
  untested, not just a possible misidentification -- same caution
  applies to any named Garmin screen type, since none of them have
  been deliberately hidden this way and confirmed safe. Turning it
  back ON (showing) is NOT gated, since that's a normal,
  well-understood on-device action with no equivalent risk. Every
  change is applied
  immediately to `MainFrame.editing_path` (a scratch working copy of
  the staged file) via direct `fit_patch.py` function calls -- never a
  subprocess, never simulated -- and the panel always re-reads the
  actual resulting bytes afterward. **DONE (v0.7.0):** screen-level
  reordering -- `ViewScreensPanel` has its own Move Up/Down pair,
  acting on `swap_display_order()` (`--swap-order`'s backend), same
  select-plus-buttons pattern as field reordering.

Architecture: `MainFrame` owns app state (`garmin_root`,
`working_dir`, `staged_path`, `profile_filename`, `editing_path`,
`editing_slot`) and swaps between panel instances in one window
rather than opening a new top-level window per step. `editing_path`
IS the pending-edit queue -- see the `gui_app.py` module docstring's
"Editing architecture" note -- rather than an abstract in-memory list
that could drift from real file semantics; it persists across edits
to multiple screens within one session. Build order going forward
follows the same pattern established from step 1: wire one step of
the flow below to its already-validated backend function, test
against real hardware, then move to the next step.

### Editing UX decision (for step 6, decided ahead of building it)

Reordering screens and fields will be **select + Move Up/Move Down
buttons, not drag-and-drop**. Every reorder capability already
validated on real hardware is a *swap* — `--swap-order` swaps two
screens' display positions, `--swap-fields` swaps two field
positions within a screen — and "move up" is exactly "swap with the
row above," so buttons map onto the tested primitives with zero new
backend logic. Drag-and-drop in wxPython has no built-in reorderable
list control, behaves inconsistently across platforms, and is much
harder to make keyboard-accessible; not worth the cost here.

Field count changes and reassigning which fields appear on a screen
don't map onto a swap at all — `--fields` replaces a screen's entire
field list and derives the count from its length (why both
same-count-replace and count-increase were separately validated).
So "Add Field" / "Remove Field" / "Replace Field" in the GUI all
funnel into one operation: take the screen's current list, apply the
one change, queue a `--fields` call with the resulting full list —
fed from a picker over the known `FIELD_ID_NAMES` catalog, not
free-text entry, so a user can't accidentally queue an unresolved or
mistyped ID.

**Status:** Add Field and Remove Field are built (`EditScreenPanel`
since v0.2.0, `AddScreenPanel` since v0.8.0). **DONE (v0.9.0):**
"Replace Field" -- a "Change Type..." button on both panels that swaps
one field's ID in place, without the Remove+Add+reposition workaround.
In `EditScreenPanel` it funnels into the exact same
`_apply_field_list()`/`check_system_screen_guard()` path Add/Remove
Field already use; in `AddScreenPanel` it's a pure in-memory edit
since nothing's written until Create Screen. Headless-verified against
a real user screen (Screen 2, VAM -> Max Speed) -- guard correctly
passed through with no false warning, only the target field changed,
CRC valid. **CONFIRMED live through the actual GUI on real hardware**:
changing a field on an existing user-defined data screen worked as
expected; attempting the same on ClimbPro correctly triggered the
named-Garmin-type confirmation dialog (f10=104) instead of silently
proceeding -- the guard is doing its job on a real, non-user screen,
not just in headless testing. **Follow-up, CONFIRMED (2026-08-05):**
the developer went ahead and overrode the guard on ClimbPro, deployed,
and verified on the reconnected/restarted Sandbox profile -- the field
change took and survived the round-trip. This closes the loose end
just above: overriding check_system_screen_guard() to edit a named
Garmin type's field content via a raw file write is now confirmed
SAFE for ClimbPro specifically, not just theoretically possible. Not
yet extended to any other named type (Map, Compass, GroupTrack List,
etc.) -- each would need its own confirmation before being treated as
equally safe, since "this is genuinely untested" language elsewhere in
the docs (FIT_PATCH.md's `--force` section, the GUI's confirmation
dialog wording) was written before this result and should be read as
"untested for types other than ClimbPro" going forward.

**Toolkit choice:** leaning **wxPython** over CustomTkinter —
`wx.grid.Grid` / `wx.propgrid` map naturally onto "list of screens,
each with editable properties," avoiding the need for two separate
toolkits.

**Agreed high-level flow**, as the scoping baseline going forward:

1. Detect the device, and show device info (`get_device_info()`) so a
   multi-device user can confirm the right one is connected.
2. List profiles on the device.
3. Back up all profiles (cheap — do it on every connect, regardless
   of which profile ends up being touched) and let the user select
   one, then stage it (lineage-tracked).
4. Alongside editing, offer **"Restore from a previous backup"** as a
   sibling action to editing, not a buried settings option — see
   *Restore from backup*, below.
5. Show the selected profile's current screens, read-only.
6. Present available actions, including a real "Add New Screen" panel
   (pick an unconfigured slot, set fields/layout, f9/f10 auto-assigned)
   — CONFIRMED working as of `fit_patch.py` v1.12.0, BUILT as of
   `gui_app.py` v0.8.0, no longer an on-device-menu redirect; see
   *Adding a new screen*, above.
7. ~~Apply changes in a loop — a pending/preview state, not immediate
   writes~~ **SUPERSEDED by the architecture actually built (see
   "Editing architecture" above):** every change (field edits, layout,
   reorder, Add-New-Screen, Change Type) is already applied
   immediately to `MainFrame.editing_path` the moment it's made, one
   real `fit_patch.py` call per click, with the guarded-operation
   confirmation dialog (`check_system_screen_guard()`) already
   happening at that same moment. There's no separate abstract
   pending-changes queue to build or apply — `editing_path` already IS
   that queue, in real bytes, so this step turned out to have nothing
   left to do by the time steps 1-6 were finished.
8. Do a final pre-flight verification (diff + CRC) of the accumulated
   result before touching the device -- **DONE (`gui_app.py` v0.10.0,
   `PreflightPanel`, "Review & Deploy...")**: shows a `fit_dump.py
   diff`-style comparison of `editing_path` against the untouched
   staged file, plus a real `fit_crc()` check against the working
   file's current bytes -- the automated version of what the CLI docs
   already tell a user to do by hand before every deploy. Given step 7
   turned out to be a no-op, this is effectively where steps 7 and 8
   merged into one panel.
9. Deploy → verify the write → explicit eject prompt → power-button
   instruction → wait-for-remount -- **DONE (`gui_app.py` v0.13.0,
   `DeployPanel`)**: writes `editing_path` to `NewFiles/` via
   `write_to_newfiles()` (byte-for-byte write-back verification, same
   as the CLI), then a confirm-then-`diskutil eject` button (reusing
   `_volume_mount_point()` for the real ejectable target -- NOT
   `garmin_root` itself, confirmed via testing that only the volume
   root works) plus an "I Ejected It Myself" fallback for non-macOS/
   Finder-eject preference, then a manual "Check for Reconnected
   Device" button. Deliberately NOT the CLI's `wait_for_remount()`
   directly (blocks with `time.sleep()` for up to 180s) and
   deliberately NOT background-thread polling either -- user-confirmed
   design decision (2026-08-06): this app has never used a background
   thread, and introducing one here would trade a few extra clicks for
   a new class of failure mode (thread lifetime vs. panel teardown --
   the same species of bug already hit once with `EVT_SIZE` during
   teardown, see `LayoutDiagramPanel.on_size()`). Each "Check" click is
   one immediate, non-blocking `find_garmin_root()` call instead.
10. Automatic post-write verification — re-pull the profile and
    confirm the change actually landed, rather than leaving that as a
    manual afterthought -- **DONE (`gui_app.py` v0.14.0,
    `DeployPanel.on_check()`)**: the moment reconnect is confirmed,
    re-pulls the LIVE profile straight from the device's `Sports/`
    folder and runs it through the same `describe_screen_changes()`
    used in steps 7-8 (now factored out to module level so both panels
    share one implementation), comparing it against `editing_path`
    (what was actually sent). Runs automatically, not a separate
    manual step, since the device is already confirmed connected at
    that point. User-confirmed design decision (2026-08-06): compare
    visible/active screens only — no Removed-list bookkeeping in the
    result, matching the "Product note on `--un-remove`" reasoning
    below (Garmin's own editor has no un-remove option, neither does
    this GUI, so the device's known Removed-list wipe on NewFiles
    import isn't something to surface). This falls out of
    `describe_screen_changes()` for free — it only ever reports a slot
    that's ACTIVE (field 1 == 1) on at least one side, so a
    Removed-only or Unconfigured-only transition never produces a
    line, no special-casing needed (headless-verified: simulated the
    exact Removed→Unconfigured flip and confirmed zero diff lines,
    while a real field/position change on the same file pair still
    reports correctly).

### Restore from backup

Added to the flow after realizing edit-and-regret needs an easy way
back. Mechanically this needs **no new toolkit capability** — a
restore is identical to a normal deploy, just sourced from an old
backup file instead of a freshly patched one; `garmin_device.py`'s
existing `write_to_newfiles()` → eject → power-button → remount →
verify pipeline handles it as-is.

**DONE (`gui_app.py` v0.15.0, `RestorePanel`)**: "Restore from
Backup..." on `ProfileListPanel` (enabled the moment a profile is
selected — a sibling action to Stage, not buried in a menu) opens a
list of that profile's backup history, newest first, each row showing
a plain-English screen-type summary (e.g. "8 screen(s): Screen 1, Lap
Summary, Map, Elevation, ...") via `classify_screens()`/
`screen_type_name()` — no guessing "which one was before I broke it"
from a bare date string. Picking one and confirming hands off straight
to `DeployPanel` (steps 9-10), reusing it completely unchanged —
`frame.editing_path` just points at the chosen backup file directly
(never copied; `DeployPanel`/`describe_screen_changes()` only ever
read it). `PreflightPanel` (steps 7-8) is deliberately skipped for a
restore — there's no staged-vs-editing diff to show when the user
already picked a specific, known backup from a summarized list.
`DeployPanel`'s "Back" button is now context-aware
(`frame.deploy_return_panel`) so it returns to the right place either
way.

- Since every connect backs up *all* profiles (step 3), by the time
  someone wants to undo something there's usually already a stack of
  timestamped backups to choose from. **NEW:** `garmin_device.py`
  v0.11.0's `list_backup_history()` de-duplicates consecutive
  byte-identical backups (every visit to the profile list re-backs-up,
  not just real changes, so an untouched profile would otherwise
  accumulate many identical entries per session) — one entry per REAL
  change, nothing lost.
- The GUI needs to list a given profile's backups specifically (filter
  the timestamped backup folders down to that one filename), and
  should show more than a raw timestamp per entry — **DONE**, see
  above.
- **Before restoring, back up the current (about-to-be-overwritten)
  on-device state first**, exactly like any other write. This makes a
  restore itself always undoable — no dead end where someone restores
  to the wrong backup with no way back. **Satisfied by construction,
  no extra logic needed**: `ProfileListPanel.on_show()`/`on_refresh()`
  already re-backs-up unconditionally every time that panel is
  displayed, which happens right before a user ever reaches "Restore
  from Backup..." — so the pre-restore on-device state is always
  already the newest entry in the very history list being restored
  from.
- Backup retention is an open question, not an MVP blocker — see Open
  Items.

### Clone Profile

The last remaining item in the GUI feature backlog — `fit_clone_profile.py`
(CLI-validated on real hardware, see MVP_SCOPE.md "Clone-and-retarget")
was written early in this project but not yet wired to a GUI button.

**DONE (`gui_app.py` v0.16.0, `ClonePanel`)**: "Clone..." on
`ProfileListPanel` (enabled alongside Stage/Restore the moment a
profile is selected) opens a simple form — a new display name, with a
filename auto-suggested from it (editable, but never silently
overwritten once the user types into it directly). Clicking "Create
Clone" patches `sport_mesgs[0].name` (mesg_num=12, field 3, a fixed
32-byte null-padded string) via `patch_profile_name()` against the
source profile's just-taken backup — never the live device file, same
discipline as Stage/Restore — and hands off straight to `DeployPanel`
(steps 9-10), reusing it completely unchanged, exactly the way Restore
does. There's no staged-vs-editing diff to review for a clone either,
so `PreflightPanel` is skipped.

- **The one real risk with cloning: deploying under a filename that
  already matches an existing on-device profile silently overwrites
  it** instead of creating a new one — `fit_clone_profile.py`'s own
  docstring warns of this. Guarded by live validation against
  `frame.known_profiles` (a new frame-level dict, kept in sync by
  `ProfileListPanel.on_refresh()` on every visit) — "Create Clone"
  stays disabled until the chosen filename is confirmed to not collide
  with anything currently on the device, case-insensitively.
- Same state-leak risk as Restore (see the v0.15.1 bug entry above)
  applies here too, since Clone reaches `DeployPanel` the same way —
  proactively fixed from the start rather than waiting to reproduce it:
  `ClonePanel.on_back()` discards `frame.editing_path` when abandoned,
  same pattern as `RestorePanel.on_back()`.
- Headless-verified against a real backup file (`patch_profile_name()`
  can't be exercised through actual wx widgets in this sandbox):
  filename validation correctly rejects a missing/blank name, a
  filename with no `.fit` extension, a filename containing a path
  separator, and a case-insensitive collision with an existing
  profile; the produced clone is structurally identical to the source
  (`classify_screens()` reports the same screens/fields/order) with
  only the name field bytes different, and `describe_screen_changes()`
  reports zero differences — matching the already-confirmed real-
  hardware CLI result for `fit_clone_profile.py` itself. **CONFIRMED
  via real hardware (2026-08-11, reported after the fact by Doug,
  hadn't been logged here yet):** at least two clones deployed and
  working correctly through NewFiles under brand-new filenames not
  previously present on the device — `Clonebox` (from `Sandbox`) and
  `CloneRoad` (from `Road`). This also settles a previously-open
  question relevant beyond Clone itself: NewFiles correctly accepts a
  genuinely NEW filename, not just a replacement of an existing one —
  see "Restore a profile that's no longer on the device" under Open
  Items, which shares this exact mechanism and was flagged as carrying
  the identical unconfirmed risk as of the last revision of this
  document.

See [`MVP_SCOPE.md`](MVP_SCOPE.md) for the feature-level scope this
flow is built around, and [`MEMORY_LOG.md`](MEMORY_LOG.md) for the
complete, unabridged project history and findings.
