# Garmin Edge 530 Activity Profile Screen Editor

*Doc rev 51 — refreshed 2026-08-19. **New "Who this is for" section**,
between Disclaimer and Setup, ahead of Doug posting this update to
GitHub -- prompted by Doug's own reflection after hitting setup
friction on both platforms this session (venv/Python Launcher on Mac,
PowerShell/module-copying on Windows) and asking whether the toolkit
was exceeding the audience it's actually built for. States plainly
this is a terminal-comfortable-rider tool right now, not a
plug-and-play app, and names what you get in return (direct field
access the on-device editor doesn't expose, Delete Screen, Clone,
Restore, batch changes, automatic backups) so a visitor self-selects
correctly instead of hitting the same friction Doug did. No scope
change to the toolkit itself -- packaging into a real installer/app
bundle for a non-technical audience was discussed and deliberately
deferred, to revisit only if this GitHub post actually draws interest
from less-technical riders. Prior rev (50, 2026-08-19) follows.*

*Doc rev 50 — refreshed 2026-08-19. **Two follow-ups from the Windows
test pass.** (1) Setup docs restructured into explicit macOS/Windows
sections — the toolkit itself runs on both now, but only macOS has a
one-command install script; Windows setup for now is manual
`pip install garmin-fit-sdk wxPython` in PowerShell (see Setup above),
plus a note that the WHOLE toolkit folder needs copying over, not
individual files, after Doug's first test hit
`ModuleNotFoundError: No module named 'fit_dump'` from copying just
`garmin_device.py`. (2) Real bug fix, Doug's report: `StartupTxtPanel`
(the GUI's `startup.txt` editor)'s message box showed only ~2 lines on
Windows vs. ~5 on the Mac for the same file — the multiline TextCtrl
had no explicit minimum height, just proportion=1/EXPAND in its sizer,
so its visible size was whatever leftover space remained after every
fixed-size sibling control, and that leftover happened to differ by
platform (font metrics/DPI). Fixed in `gui_app.py` v0.19.6 with a
`SetMinSize()` floor computed from the control's own
`GetCharHeight()` × `STARTUP_TXT_MAX_LINES` (6) — guarantees at least
6 lines visible with no scrolling on any platform's real font metrics,
not a pixel value tuned to one machine; the control still grows taller
than this floor when more room is available. Prior rev (49,
2026-08-19) follows.*

*Doc rev 49 — refreshed 2026-08-19. **Windows support CONFIRMED on
real hardware.** Doug ran the full test pass on a real Windows 11
laptop against his actual Edge 530: `garmin_device.py detect` printed
the same device info the Mac shows, `screens` worked from both
`fit_dump.py` and `garmin_device.py`, and the full GUI workflow — add
a screen to the Sandbox profile, deploy, restart, NewFiles round-trip
— completed cleanly. No code changes were needed; copying the
toolkit's `.py` files to the laptop was enough (one hiccup along the
way: an early CLI-only test copied over just `garmin_device.py`,
which failed with `ModuleNotFoundError: No module named 'fit_dump'`
since `get_device_info()` imports it — resolved by copying the whole
toolkit folder). Doug's `D:\Garmin` has `Sports`/`NewFiles` flat at
the drive root, resolving Doc rev 48's open question — Level 1 of
`_find_garmin_root_windows()`'s two-level check is what matched; the
Level 2 (one-subfolder-deep) branch is still unexercised on real
hardware but has no reason to behave differently. `garmin_device.py`
now v0.12.6 (confirmation-only entry, no code changed). `install.sh`
remains macOS-only; Windows setup for now is the manual
`pip install garmin-fit-sdk wxPython` path, which is what Doug used
here. No Linux testing has been done. Prior rev (48, 2026-08-17)
follows.*

*Doc rev 48 — refreshed 2026-08-17. **Windows device detection is now
implemented, pending real-hardware confirmation.** Doug has lined up
Windows 11 access for testing. `_find_garmin_root_windows()` —
`garmin_device.py`'s single deliberately-stubbed function, per its own
module docstring — now scans drive letters C: through Z: for the same
`Sports`/`NewFiles` structure check the macOS half uses, checking both
the drive root and one level of subfolder (mirroring the nesting the
macOS half already handles, since real Edge 530 hardware puts
`Sports`/`NewFiles` one folder down under the mounted volume on Doug's
Mac — whether Windows does the same is the first open question this
testing pass should answer). Uses plain `os.path`/`os.listdir` drive
iteration rather than a Windows API, so no new dependency beyond what
`install.sh` already installs. `garmin_device.py` now v0.12.5.
Headlessly verified via `ntpath`-monkeypatched fake drive trees (real
Windows drive letters can't be exercised in the dev sandbox) — nested,
flat, no-device, and flaky-drive cases all pass; `find_garmin_root()`
dispatch confirmed. `install.sh` remains macOS-only (it's a bash
script; Windows needs its own setup path, not yet built). Prior rev
(47, 2026-08-17) follows.*

*Doc rev 47 — refreshed 2026-08-17. **FULLY CONFIRMED via direct
raw-byte inspection.** Doug's `CyclingRoadRoadtemp.fit` — the original
census profile, Screen 3/Screen 4 still intact at 10 fields each —
came through on a second upload attempt. Raw field-ID arrays dumped
directly: Screen 3 (slot 6) = [150, 149, 177, 176, 43, 437, 40, 408,
411, 441], Screen 4 (slot 7) = [80, 42, 148, 147, 82, 83, 151, 161,
160, 159]. Every one of the 20 corrected pairs from Doc rev 46
matches these raw arrays position-for-position exactly, including 177
"Torque Effect" under its own ID — closing the last open question
from that fix. `fit_dump.py` now v2.4.20. Same direct byte-level
verification standard as every other confirmed batch in this project
now, not resting on device-observed inference alone. Prior rev (46,
2026-08-17) follows.*

*Doc rev 46 — refreshed 2026-08-17. **RESOLVED: the 2026-08-17 field-ID
batch had raw IDs and names correctly identified but WRONGLY
PAIRED.** Doug's census screens 3 and 4 got transposed when the
original list was written up, so all 10 IDs from one screen's block
were paired with the 10 names from the other screen's block — a clean
systematic offset (same 20 raw IDs, only the name assignment
changed). Caught via real device testing: editing a screen to
"Intensity Factor (IF)"/"Pedal Smoothness"/"Torque Effect" actually
displayed "Avg W/kg"/"Lap NP"/"Last Lap NP" on the device. Doug
re-derived the correct pairing directly from the census screens; it
resolves all three mismatches exactly. Corrected pairing: 80 30s
Power, 42 %FTP, 148 Last Lap NP, 147 Lap NP, 82 TSS, 83 Intensity
Factor (IF), 151 Lap Balance, 161 30s Balance, 160 10s Balance, 159 3s
Balance, 150 Avg Balance, 149 Balance, 177 Torque Effect, 176 Pedal
Smoothness, 43 Power Zone, 437 Avg W/kg, 40 Max Power, 408 Di2
Battery, 411 Di2 Shift Mode, 441 30s W/kg. `fit_dump.py` now v2.4.19.
Not independently re-confirmed via a raw byte dump (upload sync issue
this session) — treated as sufficiently confirmed on the 3-for-3
match against observed device behavior. See `PROJECT_NOTES.md` for
the full writeup. Prior rev (45, 2026-08-17) follows.*

*Doc rev 45 — refreshed 2026-08-17. Real bug fix: field 148 was stored
as "Torque Effect." — a guessed abbreviated form, by analogy to field
320's "Perf. Conditioning" convention. Doug directly confirmed the
real on-device text in a half-width (1/2 side-by-side) field: "Torque
Effect", no trailing period. Corrected — no count change, still 137
confirmed entries. `fit_dump.py` now v2.4.17. Prior rev (44,
2026-08-17) follows.*

*Doc rev 44 — refreshed 2026-08-17. **20 new confirmed field IDs** —
Doug's continued field census, this project's first batch touching
power-meter/Di2-electronic-shifting metrics: Balance family (42
Balance, 80 Avg Balance, 40 Lap Balance, 441 3s Balance, 411 10s
Balance, 408 30s Balance), Power/W-kg (150 30s Power, 151 Max Power,
83 Avg W/kg, 159 30s W/kg), training load (149 %FTP, 43 TSS, 437
Intensity Factor (IF)), NP (176 Lap NP, 177 Last Lap NP), pedaling
metrics (148 Torque Effect, 147 Pedal Smoothness, 82 Power Zone), and
Shimano Di2 (161 Di2 Battery, 160 Di2 Shift Mode). Notably confirms
the Power family's 3s/10s/30s/Lap/Avg naming pattern repeats
identically for L/R Power Balance, with "Balance" as the base metric
mirroring "Power" — a self-consistent family, not one-off guesses. No
collisions with any existing entry. `fit_dump.py` now v2.4.16,
`FIELD_ID_NAMES` now 137 confirmed entries (was 117); the GUI's
`FieldPickerDialog` docstring updated to match (`gui_app.py` now
v0.19.5, doc-only). See `PROJECT_NOTES.md` for the full writeup.
Prior rev (43, 2026-08-16) follows.*

*Doc rev 43 — refreshed 2026-08-16. **Real bug: startup.txt's "?"
corruption had a second, separate cause.** After the earlier
smart-quote fix, Doug still found 3 literal "?" at the very front of
the file's preserved header comment line — not anywhere he'd typed,
invisible in the GUI's own editor, only found by opening the raw file
in BBEdit. Cause: `read_startup_txt()` decodes with
`errors="replace"`, so a leading UTF-8 BOM (3 bytes, each invalid for
ASCII) becomes 3 replacement characters that ride through the
preserved header and get re-encoded to 3 literal "?" on every save —
self-perpetuating regardless of the smart-quote fix, since that only
guards freshly-typed text. `read_startup_txt()` now strips a leading
UTF-8 BOM before decoding. Matches Doug's own sequence exactly: he
manually cleaned the "?" via BBEdit, and a fresh `gui_app` edit after
that didn't bring them back. `garmin_device.py` now v0.12.4. See
`PROJECT_NOTES.md` doc rev 55 for the full writeup. Prior rev (42,
2026-08-16) follows.*

*Doc rev 42 — refreshed 2026-08-16. The f10=38 "Workout" screen's
purpose is now backed by Garmin's own Edge 530 Owner's Manual: its
Training > Workouts feature is a separate subsystem from Activity
Profile screens, and running a structured Workout "displays each step
of the workout, the target (if any), and current workout data" —
almost certainly what this screen type renders, dynamically, only
while a Workout is actively running (synced via Garmin Connect or
built on-device under `GARMIN/Workouts/Guided` or `/Scheduled`), the
same "only meaningful under a specific runtime condition" pattern this
project already established for ClimbPro/Segment/GroupTrack List. New
`FIELD_EDIT_UNCERTAIN_TYPES` set (`fit_dump.py`, now v2.4.15, currently
just `{38}`) backs a new non-blocking warning in the GUI's Edit Screen
panel (`field_edit_uncertain_warning_text()`, `gui_app.py` now
v0.19.4) — explains that editing this screen's fields is mechanically
safe (same proven write path as every other screen) but may have no
visible on-device effect, since the on-device editor doesn't expose
field editing for this type at all. Not independently confirmed via an
actual running Workout — inference from official Garmin documentation
plus this profile's own byte-level evidence. See `PROJECT_NOTES.md`
doc rev 54 and the "f10=38 'Workout'" Open Item for the full writeup.
Prior rev (41, 2026-08-16) follows.*

*Doc rev 41 — refreshed 2026-08-16. **CORRECTION: 3 new confirmed f10
screen types are 38 Workout, 58 eBike Metrics, 95 STEPS Metrics
(Shimano)** — not 39/59/96 as first added (those were read off this
tool's own "Screen N" display label, which is `f10 + 1`, not the raw
byte; corrected once Doug's `CyclingEbike.fit` was actually inspected
directly). `fit_dump.py` now v2.4.14. The f10=38 "Workout" field
question is now RESOLVED: its field bytes are confirmed byte-for-byte
identical to Cycling Dynamics' on the same profile — real data,
correctly read, not a bug — even though the on-device editor offers
no fields/options for this type at all. See `PROJECT_NOTES.md` doc
rev 53 / Open Items for the full writeup. Prior rev (40, 2026-08-16,
superseded) follows.*

*Doc rev 40 — refreshed 2026-08-16. **3 new confirmed f10 screen
types** (39 Workout, 59 eBike Metrics, 96 STEPS Metrics (Shimano)) —
SUPERSEDED, see Doc rev 41 above for the corrected f10 values.
`CyclingEbike.fit`, Doug's first e-bike/third-party-drivetrain
profile. `fit_dump.py` now v2.4.13. f10=39 "Workout" is flagged but
not resolved — this toolkit shows it with Cycling Dynamics' field set
even though the on-device editor offers no fields/options for it at
all. See `PROJECT_NOTES.md` doc rev 52 / Open Items for the full
writeup. Prior rev (39, 2026-08-16) follows.*

*Doc rev 39 — refreshed 2026-08-16. **Real bug fix, Doug's report from
actually using the GUI:** a routine startup.txt edit came back with
"?" characters where none were typed — macOS silently auto-substitutes
typed text (e.g. "..." becomes a single ellipsis character), and the
old ASCII-only write encoding replaced each result with "?". Fixed by
reversing the common substitutions back to plain ASCII before writing.
`garmin_device.py` now v0.12.3. See `PROJECT_NOTES.md` doc rev 51.
Prior rev (38, 2026-08-15) follows.*

*Doc rev 38 — refreshed 2026-08-15. **"Restore a Deleted Profile"
CONFIRMED via Doug's own real GUI test** — a deliberately-deleted
profile correctly appeared in the "Deleted, but available to restore"
list, and restoring it worked cleanly end to end. `gui_app.py` now
v0.19.3 (doc-only). Prior rev (37, 2026-08-15) follows.*

*Doc rev 37 — refreshed 2026-08-15. **Real bug fix, Doug's report from
actually testing v0.19.1:** the "reduce redundant backups" fix didn't
actually reduce them -- `DetectPanel.on_show()` auto-detects every
time it becomes active, and Back from the profile list always routes
there, so every ordinary Back click was itself resetting the
`needs_backup` flag. Fixed to only reset it on a GENUINE reconnect
(the detected root actually changes), not a redundant re-verification
of the same already-connected device. `gui_app.py` now v0.19.2. See
`PROJECT_NOTES.md` doc rev 47. Prior rev (36, 2026-08-15) follows.*

*Doc rev 36 — refreshed 2026-08-15. **"Reduce redundant profile
backups," Doug's go-ahead (low priority).** `ProfileListPanel` no
longer re-backs-up every profile on every ordinary visit to the
profile list -- a new `needs_backup` flag (set on a fresh Detect or a
confirmed post-deploy reconnect) gates the real device backup call;
the "Refresh (re-backup + re-list)" button still always forces one.
`gui_app.py` now v0.19.1. See `PROJECT_NOTES.md` doc rev 46. Prior rev
(35, 2026-08-15) follows.*

*Doc rev 35 — refreshed 2026-08-15. **"Restore a profile that's no
longer on the device," Doug's go-ahead.** `ProfileListPanel` gets a
second list, "Deleted, but available to restore," below the existing
"On Device" list -- no new button, no new panel, per Doug's own
2026-08-11 design decision. Populated from a new `garmin_device.py`
helper, `list_backed_up_profile_filenames()` (now v0.12.2), which
scans every profile ever backed up and subtracts what's currently
live. The existing "Restore from Backup..." button now works from
either list. `gui_app.py` now v0.19.0. See `PROJECT_NOTES.md` doc rev
45 for the full writeup. Prior rev (34, 2026-08-15) follows.*

*Doc rev 34 — refreshed 2026-08-15. **f10=32 renamed "GroupTrack" ->
"Reserved", Doug's decision.** This Conditional-only runtime record is
present on every profile examined so far regardless of whether
GroupTrack has ever been used, so its real purpose was never actually
confirmed. `fit_dump.py` now v2.4.12, `fit_patch.py` now v1.14.2,
`gui_app.py` now v0.18.1 — all doc-only, no functional/behavioral
change (`screen_type_name(32)` just returns a different string). f10=57
"GroupTrack List" (the real on-device menu entry) is unaffected. See
`PROJECT_NOTES.md` doc rev 44. Prior rev (33, 2026-08-14) follows.*

*Doc rev 33 — refreshed 2026-08-14. **Real bug fix, Doug's report from
actually using the new Startup Message editor:** the message text
showed a blank line between every real line, even though the same
file opened cleanly (no blank lines) in BBEdit and vi. Best-evidenced
cause: the file is likely CRLF-terminated (both those editors
silently auto-normalize that on open, so it looks identical to LF
there), and `wx.TextCtrl` has documented bad behavior when fed a
string containing embedded `\r\n`. Fixed by normalizing all line
endings to plain `\n` the moment the file is read
(`garmin_device.py`'s `read_startup_txt()`, now v0.12.1) — headlessly
verified against a simulated CRLF file (zero blank lines, zero stray
`\r` afterward) with the existing all-LF round-trip test unaffected.
See `PROJECT_NOTES.md` doc rev 43. Prior rev (32, 2026-08-14) follows.*

*Doc rev 32 — refreshed 2026-08-14. **New feature: view/edit the
device's startup.txt custom boot message.** New "Startup Message..."
button on the GUI's Detect screen opens `StartupTxtPanel` — edits the
`<display=N>` seconds value and the free-form message text, preserving
Garmin's own comment scaffolding byte-for-byte; live char/line-count
guidance only, no hard block, per Doug's own call that on-device
wrapping is character-width-dependent and can't be reliably predicted.
Confirmed via Doug's own real Edge 530 (2026-08-14): the file lives at
`garmin_root` itself (same level as `Sports`/`NewFiles`), and writes
are a DIRECT overwrite — no NewFiles import — needing a full power
cycle to take effect, per the file's own on-device comment.
`garmin_device.py` now v0.12.0 (`read_startup_txt()`/
`parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`, plus
a new `startup-txt` CLI subcommand), `gui_app.py` now v0.18.0. See
`PROJECT_NOTES.md` doc rev 42 for the full writeup. Prior rev (31,
2026-08-14) follows.*

*Doc rev 31 — refreshed 2026-08-14. **"Delete Screen" is now complete
end to end.** New "Remove Selected Screen" button on the GUI's Screens
view, next to Move Up/Down, reusing `--remove`'s exact CLI guards with
no override and a plain confirmation that the delete is permanent
(Restore-from-Backup only undo). `gui_app.py` now v0.17.0. Same
change: split that view's button row into two, since a single row had
grown to 9 buttons and ran the full window width. See `PROJECT_NOTES.md`
doc rev 41 for the full writeup. Prior rev (30, 2026-08-14) follows.*

*Doc rev 30 — refreshed 2026-08-14. **Real hardware feedback on all
three items from doc rev 29.** `--remove` is CONFIRMED via a real
on-device round-trip test (`fit_patch.py` v1.14.1) — the GUI wrapper is
now unblocked, still unbuilt until asked for. Two real bugs found and
fixed from actually using the GUI: the Graph/Bars warning text blew out
the Edit Screen window (fixed via `textwrap`-based hard wrapping, not
`wx.StaticText.Wrap()`), and the Back-button warning's wording wrongly
implied a resumable state (reworded to Doug's preference). `gui_app.py`
now v0.16.17. Full details in `PROJECT_NOTES.md` doc rev 40 and
`FIT_PATCH.md` doc rev 19. Prior rev (29, 2026-08-14) follows.*

*Doc rev 29 — refreshed 2026-08-14. **Three pending items built, Doug's
prioritization pass.** ViewScreensPanel's Back-button data-loss bug is
FIXED (`gui_app.py` v0.16.14); the Graph/Bars full-width warning is
BUILT, surfaced in the field picker and both screen-editing panels
(`fit_dump.py` v2.4.11, `gui_app.py` v0.16.15); and "Delete Screen"'s
backend half — a new `--remove` flag reusing `--hide`'s exact guards —
is BUILT and headless-verified, though NOT YET on real hardware, so its
GUI wrapper stays deliberately unbuilt (`fit_patch.py` v1.14.0). Full
details in `PROJECT_NOTES.md` doc rev 39 and `FIT_PATCH.md` doc rev 18.
Prior rev (28, 2026-08-13) summary follows.*

*Doc rev 28 — refreshed 2026-08-13. **Clarified, not a new finding:**
Doug's "GroupTrack" in the prior rev's confirmed-active-Remove list
meant the on-device editor's actual label "GroupTrack List" (`f10=57`)
— already covered, not a separate untested type. The genuinely
different `f10=32` GroupTrack Conditional record never appears as a
row in the on-device editor at all, so it has no Remove status to
check and is structurally out of reach of the future `--remove` flag
regardless. `NO_SHOW_TOGGLE_TYPES` (Map, ClimbPro) is now the complete
confirmed Remove-block set for common named types — no remaining gap.
`fit_patch.py` now v1.13.2 (doc-only). Prior rev (27, 2026-08-13)
summary follows.*

*Doc rev 27 — refreshed 2026-08-13. **Remove availability for named
screen types confirmed on-device (Doug).** Map and ClimbPro are the
only common named types with Remove disabled — Elevation, GroupTrack,
Cycling Dynamics, Lap Summary, Virtual Partner, Compass, and Segment
all show it active, same boundary `NO_SHOW_TOGGLE_TYPES` already
hard-codes for Show/Hide. `fit_patch.py` now v1.13.1 (doc-only),
directly informs the still-scoped `--remove`/"Delete Screen" feature —
see `PROJECT_NOTES.md` Open Items for the full writeup. GroupTrack
List not yet separately confirmed. Prior rev (26, 2026-08-13) summary
follows.*

*Doc rev 26 — refreshed 2026-08-13. **`fit_patch.py`'s `--un-remove`
flag RETIRED entirely (Doug's decision, now v1.13.0).** Restore-from-
Backup already covers real recovery from an accidental delete at the
whole-profile level (confirmed on real hardware), `--un-remove` had a
confirmed historical device-side data-loss hazard never re-verified
after its fix, and Garmin's own editor doesn't offer an un-remove
workflow either — see `PROJECT_NOTES.md` "Product note on
`--un-remove`" for the full history. `fit_dump.py` (v2.4.10) and
`gui_app.py` (v0.16.13) comments updated to match, doc-only. Prior rev
(25, 2026-08-13) summary follows.*

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

## Who this is for

This toolkit is built for riders who are comfortable with a terminal
and a `pip install`, not (yet) a plug-and-play app for the general
public. There's no installer or double-clickable application bundle —
setup means cloning this repo, running a setup script (macOS) or a
couple of `pip install` commands by hand (Windows), and running the
GUI or CLI tools from a terminal with that environment active. If
that's a step you've done before for some other tool, you'll be fine
here; if "open a terminal" isn't something you do, this project isn't
there yet.

What you get in exchange for that setup: direct editing access to
Activity Profile screens and data fields the on-device editor doesn't
expose at all (power-meter/Shimano Di2 metrics, Torque Effectiveness,
Balance, TSS/IF, and more), the ability to delete a screen outright
rather than just hide it, clone a profile under a new name, restore a
profile that's no longer on the device, batch several changes into one
device restart, and automatic backups before every write.

## Setup

The toolkit itself (CLI tools and GUI) runs on both **macOS** and
**Windows** — device detection is confirmed working on real hardware
on both (see `garmin_device.py`'s changelog). The *install path*
differs, though: macOS has a one-command setup script, Windows doesn't
have one yet (see task list) and needs `pip install` run by hand.

### macOS

Run the install script — it checks your python3 version, creates a
dedicated `.venv` (nothing touches your system or Homebrew Python),
and installs both dependencies (`garmin-fit-sdk` and `wxPython`) into
it:

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

### Windows

There's no `install.sh` equivalent yet for Windows — `install.sh`
itself hard-stops immediately with an error message if run there (it
checks `uname -s == Darwin` as its very first step). Until a
`.ps1`/`.bat` setup script exists, install by hand in PowerShell —
this is the exact sequence Doug used for the confirmed-working
2026-08-19 test:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install garmin-fit-sdk wxPython
```

Copy the whole toolkit folder over, not individual `.py` files —
`garmin_device.py`, for example, imports `fit_dump.py` at runtime, so
a partial copy fails with `ModuleNotFoundError`.

Confirmed on Windows 11 (2026-08-19): `detect`, `screens` (both CLI
tools), and the full GUI workflow (add a screen, deploy, restart,
NewFiles round-trip). Not yet tested on Windows 10 or any Linux
distribution.

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

To view or replace the device's custom boot message (`startup.txt`,
lives at the device root, NOT in `Sports/` — a direct overwrite, no
`NewFiles`/eject-import involved; the existing file is backed up
first):

```bash
python3 garmin_device.py startup-txt ~/path/to/a/working/directory                     # view
python3 garmin_device.py startup-txt ~/path/to/a/working/directory --write new_msg.txt  # overwrite
```

Eject, then allow one **full power cycle** (off, then on) — not just
eject/remount — for the new message to take effect (confirmed via the
file's own on-device comment).

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
| `garmin_device.py` | 0.12.6 | Detect (+ device info)/list/backup/stage/write/eject/remount-wait workflow for the device itself. **Windows support CONFIRMED on real hardware (v0.12.6, 2026-08-19)** — Doug ran `detect`, `screens` (both CLI tools), and the full GUI workflow (add screen, deploy, restart, NewFiles round-trip) against a real Edge 530 on a real Windows 11 laptop; all worked with zero code changes. `D:\Garmin` has `Sports`/`NewFiles` flat at the drive root, resolving Doc rev 48's open question. Confirmation-only entry, no code changed. See Doc rev 49 above. Prior entry (v0.12.5, Doug's go-ahead): `_find_garmin_root_windows()` filled in — the single deliberately-stubbed function per this file's own module docstring. Scans drive letters C:-Z: for the same `Sports`/`NewFiles` structure check the macOS half uses, at both the drive root and one level of subfolder (mirroring macOS's own two-level nesting check). Plain `os.path`/`os.listdir` iteration, no new dependency. Headlessly verified via `ntpath`-monkeypatched fake drive trees. See Doc rev 48 above. Prior entry (v0.12.4, same-day follow-up to v0.12.3, Doug's report from testing): a second, separate cause of the startup.txt "?" corruption — a leading UTF-8 BOM decoded (via `errors="replace"`) into 3 replacement characters that rode through the preserved header and got re-encoded to 3 literal "?" on every save, self-perpetuating regardless of the v0.12.3 smart-quote fix. `read_startup_txt()` now strips a leading UTF-8 BOM before decoding. See Doc rev 43 above. Prior entry (v0.12.3, Doug's report from testing): `write_startup_txt()` now reverses common macOS smart-substitution characters (curly quotes, en/em dash, ellipsis) back to plain ASCII before writing — typed "..." was silently becoming a single "?" on save, since `wx.TextCtrl` on macOS auto-substitutes as you type and the old ASCII-only encode replaced each result with "?". Any character outside the known-substitution table still degrades honestly to "?", unchanged. Prior entry (v0.12.2): `list_backed_up_profile_filenames(working_dir)` returns every `.fit` filename ever backed up (regardless of current on-device presence), scanning all `backups/<timestamp>/` folders — filtered to `.fit` so a `startup.txt` backup (which lives in the same folder structure) isn't mistaken for a deleted profile. New `deleted-profiles` CLI subcommand. Backs `gui_app.py` v0.19.0's new second profile list. Prior entry (v0.12.1): `read_startup_txt()` now normalizes all line endings to plain `\n` right after decoding — real reported bug, the GUI's message editor was showing a blank line between every real line, likely from CRLF line endings in the file that BBEdit/vi both silently normalize on open (so it looked fine there) but `wx.TextCtrl` does not handle cleanly when fed embedded `\r\n`. Headlessly verified against a simulated CRLF file. Prior entry (v0.12.0): startup.txt (custom boot message) support — `read_startup_txt()`/`parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`, plus a new `startup-txt` CLI subcommand (view, or `--write FILE` to overwrite). CONFIRMED via Doug's own real Edge 530 (2026-08-14): the file lives at `garmin_root` itself (same level as `Sports`/`NewFiles`), and a write is a DIRECT overwrite while mounted — NOT a NewFiles import — per the file's own on-device comment ("Allow one full power cycle after editing for your message to be updated"). `write_startup_txt()` backs up any existing file first, reusing the same `working_dir/backups/<timestamp>/` structure `backup_profiles()` uses. `parse_startup_txt()`/`build_startup_txt()` split/rejoin the file at its last comment block, so Garmin's own instructional text is preserved byte-for-byte and only the `<display=N>` value + message text are ever regenerated — headlessly round-trip-tested byte-identical against Doug's real file. Character/line-count reference constants (`STARTUP_TXT_MAX_CHARS`/`STARTUP_TXT_MAX_LINES`) are guidance only, not enforced — actual on-device wrapping is character-width-dependent (Doug's own note). Backs `gui_app.py`'s new `StartupTxtPanel`. Prior entry (v0.11.0): `list_backup_history()` lists a single profile's backup history (newest first), de-duplicating consecutive byte-identical backups — a real characteristic of this app, since every visit to the GUI's profile list re-backs-up all profiles, not just on real changes. Backs the GUI's Restore-from-Backup picker; also a new `backup-history` CLI subcommand. |
| `fit_dump.py` | 2.4.20 | Read and inspect a `.fit` file (`dump`, `unknown`, `diff`, `screens` subcommands). v2.4.20: FULLY CONFIRMED via direct raw-byte inspection — `CyclingRoadRoadtemp.fit` (the original census profile, Screen 3/4 intact at 10 fields each) came through and was dumped directly; raw arrays match all 20 corrected pairs from v2.4.19 position-for-position exactly, including 177 "Torque Effect" under its own ID. No values changed — this closes out the last open question from the fix below. v2.4.19: RESOLVED — the entire 2026-08-17 field-ID batch had raw IDs and names correctly identified but wrongly paired (Doug's census screens 3 and 4 got transposed when the original list was written up, so all 10 IDs from one screen's block were paired with the 10 names from the other's — same 20 raw IDs, only the pairing changed). Caught via real device testing (editing a screen to "Intensity Factor (IF)"/"Pedal Smoothness"/"Torque Effect" actually displayed "Avg W/kg"/"Lap NP"/"Last Lap NP"); Doug re-derived the correct pairing from the census screens and it resolves all three mismatches exactly. v2.4.18 (superseded by the fix above): flagged the whole batch SUSPECT with no value changes, pending re-verification. v2.4.17: real bug fix, Doug's report from checking the device — field 148 was stored as "Torque Effect." (a guessed abbreviated form, by analogy to field 320's "Perf. Conditioning" convention); Doug directly confirmed the real on-device text in a half-width field is "Torque Effect", no trailing period. Corrected; no count change, still 137 entries. v2.4.16: 20 new confirmed field IDs, 2026-08-17 batch — this project's first batch touching power-meter/Di2 metrics: Balance family (42/80/40/441/411/408 — Balance, Avg, Lap, 3s, 10s, 30s), Power/W-kg (150 30s Power, 151 Max Power, 83 Avg W/kg, 159 30s W/kg), training load (149 %FTP, 43 TSS, 437 Intensity Factor (IF)), NP (176 Lap NP, 177 Last Lap NP), pedaling metrics (148 Torque Effect, 147 Pedal Smoothness, 82 Power Zone), Shimano Di2 (161 Di2 Battery, 160 Di2 Shift Mode) — confirms the existing 3s/10s/30s/Lap/Avg Power naming pattern repeats identically for Balance. No collisions. `FIELD_ID_NAMES` now 137 confirmed entries (was 117). v2.4.15: new `FIELD_EDIT_UNCERTAIN_TYPES` set (currently `{38}`, "Workout") — flags screen types whose stored field bytes are real and correctly readable but whose actual on-device meaning/rendering is uncertain, backing a new non-blocking warning in the GUI's Edit Screen panel. Built in response to Doug's question about the Workout screen's edit guard; backed by Garmin's own Edge 530 manual confirming Workouts are a separate, dynamically-rendered subsystem (see Doc rev 42 above and `PROJECT_NOTES.md` doc rev 54). v2.4.14 (correction, same day): v2.4.13's new keys were wrong (39/59/96, read off this tool's own `f10+1` display fallback) — corrected to the real f10 values, 38 "Workout", 58 "eBike Metrics", 95 "STEPS Metrics (Shimano)". Also resolved the f10=38 "Workout" field question: confirmed via a direct raw-byte comparison of `CyclingEbike.fit` that its fields are byte-for-byte identical to Cycling Dynamics' on the same profile — real data, correctly read, not a bug. See `PROJECT_NOTES.md` Open Items. v2.4.12 (rename only, Doug's decision): `NAMED_SCREEN_TYPES[32]` renamed "GroupTrack" → "Reserved" — this Conditional-only record is present on every profile regardless of GroupTrack usage, so its real purpose was never actually confirmed (f10=57 "GroupTrack List" is unaffected, remains correctly GroupTrack-specific). No functional change. v2.4.11: new `GRAPH_OR_BARS_FIELD_IDS` set (10 fields confirmed needing a full-width screen slot to render as a graph/bar), kept separate from `FIELD_ID_NAMES`, backing the GUI's new Graph/Bars full-width warning — no `FIELD_ID_NAMES` entries changed. v2.4.10 (doc-only): the `screens` subcommand's verbose "Removed screens" note referenced `fit_patch.py`'s now-retired `--un-remove` flag — updated to point at Restore-from-Backup instead. `classify_screens()`/`active_field_ids()`/`screen_type_name()` are print-free, importable data functions — the seam the GUI reads screens through. `FIELD_ID_NAMES` has 117 confirmed entries (`KNOWN_UNRESOLVED_IDS` still empty; v2.4.9: field 320 corrected "Conditioning" → "Perf. Conditioning" — full concept name is "Performance Conditioning," but the actual on-device DATA FIELD display reads "Perf. Conditioning" (abbreviated), matching this toolkit's on-device-display naming convention; v2.4.8: field 49 corrected "Avg Speed (Alt)" → "Avg Speed" — deployed into a full-width slot and visually confirmed as plain text, no graph/bars; flagged as a caution (not a falsification) for the Graph/Bars marker theory below, since there's no record this field's old "(Alt)" label was ever a real on-device marker transcription like 23/348/349 were; v2.4.7, 2026-08-11 batch: 12 new IDs plus 3 corrected placeholder names — 23 "Heart Rate (Alt)" → "HR Zone Graph", 348/349 "Speed */Cadence *" → "Speed Bars"/"Cadence Bars" — confirming the "*"/"(Alt)" marker denotes a Graph/Bars-style field needing a full-width slot; v2.4.6, doc-only: the long-open "*" marker mystery on fields 348/349 is likely resolved — marks a Graph/Bars-style rendering needing a full-width screen slot, else falls back to plain text; v2.4.5: fields 58/87 corrected from "Lap Timer"/"Last Lap Timer" to "Lap Time"/"Last Lap Time" — a mistaken analogy to the separate, correctly-named field 56 "Timer"; 2026-08-10 batch: 18 IDs confirmed via a dedicated two-screen, 10-field-each census on a real profile, cross-referencing on-device field names against their GUI-shown position); `NAMED_SCREEN_TYPES` has 10 confirmed f10 screen-type codes (Map, Compass, Segment, ClimbPro, etc.) — `screens` output now shows real screen names. |
| `fit_patch.py` | 1.14.2 | Patch a screen's fields, layout, order, or visibility. v1.14.2 (doc-only, Doug's decision): comments referencing f10=32 as "GroupTrack" updated to "Reserved" — its real purpose was never actually confirmed, this record is present regardless of GroupTrack usage; f10=57 "GroupTrack List" unaffected. No functional change. **`--remove` CONFIRMED via a real on-device round-trip test (v1.14.1, 2026-08-14)** — target screen correctly removed from the on-device order, and the removed screen was wiped by NewFiles rather than surviving as recoverable, matching `--un-remove`'s own retirement reasoning. GUI wrapper (`ViewScreensPanel`) is now unblocked, still unbuilt until asked for. `--remove`/`remove_screen()` (v1.14.0) — the backend half of "Delete Screen": permanently transitions a slot to Removed (f1=0, f9/f10 cleared, content preserved), reusing `--hide`'s exact two hard guards (Map/ClimbPro block, last-visible-user-screen floor) with no new guard logic. **Remove availability for named types confirmed and clarified (2026-08-13, on-device):** Map and ClimbPro are the only common named screen types with Remove disabled — Elevation, "GroupTrack List" (the on-device label — not to be confused with the separate GroupTrack Conditional record, which isn't a selectable row at all), Cycling Dynamics, Lap Summary, Virtual Partner, Compass, and Segment all show it active. That's the complete confirmed set, same boundary `NO_SHOW_TOGGLE_TYPES` already hard-codes for the Show Screen toggle. Doc-only, directly informs the still-scoped `--remove`/"Delete Screen" feature — see `PROJECT_NOTES.md` Open Items. **`--un-remove` RETIRED (2026-08-13, real user decision)** — Restore-from-Backup already covers real recovery from an accidental delete (whole-profile undo, confirmed on real hardware), `--un-remove` had a confirmed historical device-side data-loss hazard never re-verified after the fix below, and Garmin's own editor doesn't offer an un-remove workflow either — see `PROJECT_NOTES.md` "Product note on `--un-remove`" for the full history. `next_available_field10()` auto-computes a collision-free screen identity for `--new-slot`, replacing the old hardcoded f10=0 default — root cause of the now-RESOLVED "Add New Screen always fails" limitation; CONFIRMED working via live on-device round-trip. `check_system_screen_guard()` is f10-based and CERTAIN for any Active screen (old content-pattern/field-count heuristics are a fallback only for Removed-state slots) — fixed a real false positive on a confirmed user screen. `would_hide_last_visible_screen()` is a HARD, non-heuristic guard (no `--force`) blocking `--hide`/`--disable` on a profile's last remaining real USER screen, counted via f10. `hide_unsupported_screen_type()` is a SECOND hard guard blocking `--hide` on Map or ClimbPro entirely — confirmed neither has a Show Screen toggle at all, on any profile type. |
| `fit_chain.py` | 1.0.0 | Apply several `fit_patch.py` operations in sequence before one device write |
| `fit_clone_profile.py` | 1.0.0 | Clone a profile under a new display name (patches `sport_mesgs[0].name`) |
| `fit_raw_walk.py` | 1.0.0 | Internal support — generic FIT byte-offset walker, not meant to be run directly |
| `fit_crc.py` | 1.0.0 | Internal support — FIT CRC-16, not meant to be run directly |
| `gui_app.py` | 0.19.6 | wxPython GUI — covers steps 1-10 plus Restore-from-Backup, Clone Profile, and Startup Message. Real bug fix, Doug's report from Windows 11 testing (v0.19.6, 2026-08-19): `StartupTxtPanel`'s message box showed only ~2 lines on Windows vs. ~5 on the Mac for the same file — the multiline `TextCtrl` had no explicit minimum height (just proportion=1/EXPAND in its sizer), so its visible size was whatever leftover space remained after every fixed-size sibling control, and that leftover genuinely differs by platform font metrics/DPI. Fixed with a `SetMinSize()` floor computed from `GetCharHeight()` × `STARTUP_TXT_MAX_LINES` (6) — guarantees at least 6 lines visible with no scrolling on any platform's real font metrics rather than a pixel value tuned to one machine; still grows taller than this floor when more room's available. Prior entry, cosmetic doc-only fix (v0.19.5): field picker's docstring count updated 117 -> 137 to match `fit_dump.py` v2.4.16's 2026-08-17 batch (20 new field IDs), no functional change. Prior entry (v0.19.4): new `field_edit_uncertain_warning_text()` warning on the Edit Screen panel, fires only for a "Workout" (f10=38) screen — explains the on-device editor offers no field editing for this type at all, so an edit here may have no visible effect even though it's mechanically safe (same write path as every other screen); backed by `fit_dump.py`'s new `FIELD_EDIT_UNCERTAIN_TYPES` set and Garmin's own Edge 530 manual confirming Workouts are a separate, dynamically-rendered subsystem. Prior entry, doc-only, no code change (v0.19.3): "Restore a Deleted Profile" CONFIRMED via Doug's own real GUI test — a deliberately-deleted profile correctly appeared in the "Deleted, but available to restore" list, and restoring it worked cleanly end to end. Prior entry, real bug fix (v0.19.2, Doug's report from testing): v0.19.1's redundant-backup fix didn't work in practice — every "‹ Back" click from the profile list routes through the Detect screen, which auto-re-detects every time it's shown, and that was itself resetting the new `needs_backup` flag on every visit. Now only resets it on a genuine reconnect (the detected device path actually changes), not a same-device re-verification. Prior entry (v0.19.1, Doug's go-ahead, low priority): "Reduce redundant profile backups" — the profile list no longer re-backs-up every profile on every ordinary visit; a new `needs_backup` flag (set on a fresh Detect or a confirmed post-deploy reconnect) gates the real backup call, and the Refresh button still always forces one regardless. Prior entry (v0.19.0, Doug's go-ahead): "Restore a Deleted Profile" — the profile list gets a second list, "Deleted, but available to restore," populated from `garmin_device.list_backed_up_profile_filenames()` minus what's currently live; the existing "Restore from Backup..." button now works from either list (no new button, no new panel — per Doug's own 2026-08-11 design decision). The Restore confirmation now says "RECREATING" instead of "REPLACING" for a profile that isn't currently on the device. Prior entry (v0.18.1, doc-only, Doug's decision: the f10=32 "GroupTrack"→"Reserved" rename lives in `fit_dump.py`; this file's two user-facing display strings referencing the old name updated to match, no functional change; v0.18.0: new `StartupTxtPanel`, reached via a "Startup Message..." button on the Detect screen — view/edit the device's `startup.txt` boot message, built on `garmin_device.py` v0.12.0. Editable fields are the `<display=N>` seconds value and the free-form message text; Garmin's own comment scaffolding is preserved byte-for-byte. Live char/line-count guidance shown, deliberately NOT a hard block on Save — Doug's own call, since actual on-device wrapping depends on character width in a way this toolkit can't predict; the safety net is the automatic pre-write backup instead. Save flow: confirm -> direct device write (no NewFiles) -> eject/full-power-cycle instructions, reusing `DeployPanel`'s eject-button pattern; deliberately no post-write verification step, since a boot message can't be read back by this app. Back button warns on unsaved edits, same style as `ViewScreensPanel`'s v0.16.17 fix. Prior entry, v0.17.0: "Remove Selected Screen" on the Screens view — the GUI wrapper for `--remove`, completing "Delete Screen" now that the backend and a real device test are both confirmed; reuses `--remove`'s exact two CLI guards with no override, plus an explicit permanent-deletion confirmation; same change split that view's single 9-button row into two, per real feedback that it ran the full window width; v0.16.17: reworded the Back-button warning per Doug's feedback — the old wording wrongly implied a resumable state, now his own direct wording, no logic change; v0.16.16: real bug fix found using v0.16.15's new warning — it blew out the Edit Screen window's width, the fourth time this codebase has hit that bug class; fixed via `textwrap`-based hard wrapping rather than `wx.StaticText.Wrap()` (untestable in the dev sandbox, documented bad behavior with pre-existing newlines); v0.16.15: Graph/Bars full-width warning — new helpers derived from `LAYOUT_GRIDS` surfaced in the field picker (static note) and Edit/Add Screen panels (context-aware, recomputed on every refresh); v0.16.14: real bug fix — the Screens view's Back button now warns before discarding an in-progress, undeployed edit instead of silently losing it, matching the existing confirm-dialog style used elsewhere; v0.16.13: doc-only, two comments updated now that `fit_patch.py`'s `--un-remove` is retired entirely rather than just unexposed in the GUI — no functional change; v0.16.12: cosmetic doc-only fix, field picker's docstring count updated 105 -> 117 to match `fit_dump.py` v2.4.9's current entry count (the picker itself was never wrong — it reads `FIELD_ID_NAMES` live — only the comment had drifted stale, caught while confirming pre-release state ahead of a possible v1.0.1 tag); v0.16.11: doc-only, the "restore a profile no longer on the device" feature's one real open risk (whether NewFiles can recreate a genuinely deleted profile, not just replace/create-new) is now CONFIRMED via a direct `garmin_device.py deploy` test against a deliberately-deleted profile — only the GUI entry point itself remains unbuilt; v0.16.10: doc-only, no code change — Clone Profile CONFIRMED via real hardware, reported after the fact (two working clones deployed via NewFiles under brand-new filenames: `Clonebox`, `CloneRoad`), correcting a stale "not yet tested through the actual GUI" note and resolving whether NewFiles accepts a genuinely new filename, not just a replacement — see the toolkit table's v0.16.0 entry below for the corrected text; v0.16.9: pre-Windows-support housekeeping — the default backup working directory was hardcoded to a specific Mac path, now `~/GarminBackups` (resolves correctly on any OS/user); the working directory is now also persisted across restarts via a small config file (`~/.garmin_screen_editor_config.json`), so a custom location picked via "Change..." is remembered instead of resetting every launch; v0.16.8: new "About" button on the detect screen opens a short summary dialog — name/version, "not affiliated with Garmin" disclaimer, reverse-engineering method note, MIT mention pointing to `LICENSE`/`README.md` for the full text; v0.16.7: window title renamed to "Activity Profile Screen Editor for Garmin Edge" ahead of a possible public release — this is an independent, unofficial project, not a Garmin product; see `LICENSE` and `README_DISCLAIMER_DRAFT.md` (pending review) for the rest of that pass; v0.16.6: fixed a real bug where v0.16.3's own fix for the Fields-column width issue was itself wrong — capping the column stopped the window from growing but silently truncated text instead, with no scrollbar; correct fix decouples the frame's size from the column's width via a `ScreensListCtrl` subclass, letting the column go back to full auto-size and the list's real native horizontal scroll work as intended — see `PROJECT_NOTES.md` toolkit table row and "Corrections and lessons learned" for the full story; v0.16.5: cosmetic doc-only fix, field picker's docstring count updated 87 -> 105 to match `fit_dump.py` v2.4.4's new field IDs, no functional change; v0.16.4: bumped the on-device layout diagram's font from 9pt to 13pt for readability, per real feedback with a screenshot — safe change, no width/height risk since that panel is custom-painted at a fixed size, unlike the widgets behind v0.16.2/v0.16.3; v0.16.3: same-day follow-up to v0.16.2 — the identical unresolved-field-ID window-widening bug also hit the Fields column on the main Screens view, not just the Edit Screen panel; fixed with the same terse-label approach plus a width ceiling on that column; v0.16.2: fixed a real bug where editing a screen with an unresolved field ID permanently oversized/off-screened the window — see `PROJECT_NOTES.md` toolkit table row for the full root-cause writeup; v0.16.1: the "not connected" message and window title are now model-generic/version-visible — see `PROJECT_NOTES.md` "Model portability") (detect, list/backup, select+stage, view screens with a real Type column and screen-level Move Up/Down reordering, add a brand-new screen, edit one screen's fields/layout/Show-Hide/type, review accumulated changes, deploy to the device, post-write verification, restore any profile from its backup history, and clone a profile under a new name). **This closes out the GUI's full feature backlog.** NEW (v0.16.0): `ClonePanel` — "Clone..." on the profile list patches `sport_mesgs[0].name` via `fit_clone_profile.py`'s `patch_profile_name()` (CLI-validated full-fidelity on real hardware already), with live filename-collision checking against every profile currently on the device (deploying under an existing filename would silently overwrite it) and an auto-suggested filename from the display name. Hands off straight to Deploy, same as Restore — no staged-vs-editing diff applies to a clone. Headless-verified: filename validation, byte-for-byte-structurally-identical clone output, and zero screen differences between source and clone via `describe_screen_changes()`. **CONFIRMED via real hardware (2026-08-11, reported after the fact):** at least two clones deployed and working correctly through NewFiles under brand-new filenames not previously present on the device (`Clonebox` from `Sandbox`, `CloneRoad` from `Road`) — this also confirms NewFiles correctly accepts a genuinely new filename, not just a replacement of an existing one, a question that had been open until now. Prior entry (v0.15.2): cosmetic doc-only fix (a stale field-count reference in a docstring, no functional change). v0.15.1: fixed a real bug found via testing — backing out of a Restore attempt without completing it left a stale reference to the abandoned backup file in place, so a subsequent normal Stage silently showed that leftover instead of the profile just staged ("View Screens shows the backup I was about to restore, not what I just staged"). A fresh Stage now always clears any prior session's state first. v0.15.0: "Restore from Backup..." on the profile list now goes somewhere — `RestorePanel` lists the selected profile's backup history with a plain-English screen summary per entry ("8 screen(s): Screen 1, Lap Summary, Map, ..."), and picking one hands off straight to Deploy, skipping the staged-vs-editing review (nothing to review — you already picked a known backup). The backup file is used directly, never copied. "Back" from Deploy now returns to wherever it was actually reached from. v0.14.0: the moment "Check for Reconnected Device" succeeds, the GUI automatically re-pulls the live profile from the device and compares it against what was sent, reusing the same plain-English per-screen summary as "Review & Deploy..." (now shared as a module-level `describe_screen_changes()`). Compares visible/active screens only — the device's known Removed-list wipe on NewFiles import (a side effect that's always happened, unrelated to anything this GUI does) isn't reported, matching the fact that neither Garmin's own editor nor this GUI offers an un-remove workflow. **CONFIRMED live on real hardware** (2026-08-06) alongside a full deploy of a new 10-field screen. v0.13.0: "Continue to Deploy" now goes somewhere — `DeployPanel` writes the working copy to the device's `NewFiles/` (with byte-for-byte write-back verification), then a confirm-then-`diskutil eject` button (plus an "I Ejected It Myself" fallback for non-macOS/Finder), then a manual "Check for Reconnected Device" button. User-confirmed design decision: no background polling for the reconnect wait (this app has never used a background thread, and it's not worth the new failure-mode class for saving a few clicks) — each Check click is one immediate, non-blocking connectivity check. v0.12.0: "Review & Deploy..." now describes changes in plain English per screen (e.g. "Screen 4: added Cadence, removed Grade") instead of a raw `fit_dump.py diff`-style unified diff — real user feedback that the byte-level diff was too technical for the GUI's actual audience (a rider, not a developer); the CLI tools remain there for anyone who wants that detail. Covers new/removed screens, field changes, layout changes, show/hide changes, and position changes, with a fallback line so real changes are never silently under-reported; whether there's anything to deploy is still decided from the raw bytes directly. v0.11.1: fixed a real reported bug where the Fields column silently clipped (not wrapped) any screen with more than ~3-4 short field names — a 10-field screen only showed 3 fields and part of a 4th; the column now auto-sizes to its actual content on every refresh. v0.11.0: fixed a real reported bug where manually enlarging the window (e.g. to see more of the screens list) snapped back to a smaller size the moment any button triggered a refresh — `_relayout()` was calling `Fit()`, which resizes in both directions including shrinking; now only grows the window when content needs more room, never shrinks it. v0.10.0: "Review & Deploy..." is a pre-flight step showing a `fit_dump.py diff`-style comparison against the untouched staged file plus a real CRC check against the working file's actual bytes — REVISES the original "pending/preview state" plan to match how the GUI actually works (every change is already applied immediately, click by click; there's no separate queue to apply, only a review+verify step). Continue to Deploy is a placeholder until deploy/eject/remount is built. "Change Type..." is Add-New-Screen and EditScreenPanel's "Replace Field" — swaps one field's ID without the Remove+Add+reposition workaround. Add-New-Screen panel replicates `--new-slot`'s exact defaulting logic — auto-assigns f9/f10, enforces the confirmed 10-user-screen cap with a friendly message; **CONFIRMED live on real hardware** (2026-08-05), including a confirmed field-type change on ClimbPro after overriding the guard. Screen-level reordering is select + Move Up/Down on the main screens list, wired to `swap_display_order()` — same validated primitive as `--swap-order`. Show/Hide hard-blocks hiding a profile's last real user screen (f10-based) AND hiding Map/ClimbPro at all (neither has an on-device toggle). Guard dialogs no longer false-positive on confirmed user screens (real GUI testing found and fixed this). Swallows a cosmetic teardown-only `wxAssertionError` on exit. Field picker offers 137 confirmed IDs. |

## GUI

`gui_app.py` is the editor GUI, built incrementally, one step of the
agreed flow (see `PROJECT_NOTES.md`) at a time — each step wired to
its already-validated backend function, tested against real hardware
before the next step is added. **All 10 flow steps plus
Restore-from-Backup, Clone Profile, and Startup Message are now
built**: detect the device and show its
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
`PROJECT_NOTES.md` / "Clone Profile" for the full writeup. And
"Startup Message..." — reached directly from the Detect screen (not
from the profile flow, since `startup.txt` is a device-root file, not
a profile) — view/edit the device's custom boot message, with
Garmin's own comment scaffolding preserved byte-for-byte and a direct
(non-NewFiles) write path of its own. See `PROJECT_NOTES.md` /
"startup.txt" for the full writeup.

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
