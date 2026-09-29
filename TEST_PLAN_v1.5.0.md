# Test plan — v1.5.0 (offline mode + per-device backups)

*Working checklist. Update the result column as you go; this file is
meant to be edited during testing, not preserved as history.*

**Why this release needs more testing than v1.3.1 or v1.4.0 did:** those
changed a guard and a panel. This adds a **MODE**, so every panel
downstream of Detect now has two states. The dangerous failure is silent
rather than loud — a device-only path that isn't properly inert won't
raise a clean error, it will reach for `garmin_root = None` deep inside
code that has never seen `None`, possibly after doing half of something.

So the valuable tests here are the **negative** ones: confirm that each
mode never reaches for the other.

---

## Build status — read before testing

| Piece | State |
|---|---|
| Folder listing / profile detection / folder-sourced backup | **built, headless-verified** |
| `export_profile()` with read-back verification | **built, headless-verified** |
| Serial-keyed backup folders, both layouts coexisting | **built, headless-verified** |
| Mode state, `assert_mode()`, title-bar indicator | **built** |
| "Work Without a Device..." entry + offline profile list | **built** |
| **Export replacing Deploy in offline mode** | **NOT BUILT** |
| **Device paths made inert offline** | **NOT BUILT** |
| **`startup.txt` offline import/export** | **NOT BUILT** |

⚠ **Until the three unbuilt items land, an offline session works right up
to the point you would leave it and then hits a `None`.** Not dangerous
— there is no path to write to — but don't spend time distinguishing
"not built" from "broken". Sections B and C below are partial until then.

---

## A. Device mode unchanged — the regression risk

**Do this first, on the 530.** This release touches the backup store,
which every existing workflow depends on.

| # | Step | Expect | Result |
|---|---|---|---|
| A1 | Connect 530, click Detect | Title reads `[Device connected]`; device info as before | ✅ pass |
| A2 | Go to profile list | Profiles listed; backup runs | ✅ pass |
| A3 | Check the "Deleted, but available to restore" list | Offers profiles backed up previously but no longer on the device — and **no 840 profiles** | ✅ pass |
| A4 | Edit a screen → Pre-Flight → Deploy → restart | Normal flow, verified on device | ✅ pass |
| A5 | Startup Message: open it, change nothing, click Back | **No "unsaved changes" warning** | ⬜ retest (bug found + fixed twice) |
| A6 | Clean Up Old Backups | Store summary line visible; list of snapshots shown with device serials; no overlap with the buttons | ⬜ retest (bug found + fixed) |
| A7 | Restore from Backup | **Pre-existing backups from before today still offered** | ⬜ |
| A8 | Clone Profile | Works as before | ⬜ |

**A7 matters most of anything here.** There are ~1098 files in that
store and they are the only restore points that exist. New backups go to
`backups/<serial>/<timestamp>/`; old ones stay at
`backups/<timestamp>/`. Both must remain reachable.

---

## B. Offline mode basics

Point it at `GarminBackups/Test4` (the pre-setup 840 profiles).

| # | Step | Expect | Result |
|---|---|---|---|
| B1 | Detect panel → **Work Without a Device...** → pick the folder | Title reads `[Offline — Test4]` | ⬜ |
| B2 | Profile list | Heading reads `In folder "Test4" (offline — no device):`; the 840 profiles listed | ⬜ |
| B3 | Check what is NOT listed | `Device.fit` and `Totals.fit` absent — they are `.fit` but not profiles | ⬜ |
| B4 | Check the backup location | New snapshot under `backups/3632253714/` — serial read from the files, no device attached | ⬜ |
| B5 | Add a file to the folder, click **Refresh (re-backup + re-list)** | The new profile appears | ⬜ (bug found + fixed) |
| B6 | Select a profile → View Screens → Edit a screen | Layout picker, diagram, advisories all behave | ⬜ |
| B7 | Export | *Not built yet* | — |

---

## C. Mode isolation — the point of the release

**C2 is the important one.** Everything else is a variation on it.

| # | Step | Expect | Result |
|---|---|---|---|
| C1 | Offline mode with **no device attached**, walk the whole flow | Nothing reaches for a device | ⬜ |
| C2 | **Detect the 530 first, then switch to offline mode** | No device backup runs; title flips to Offline; the 530 is untouched | ⬜ |
| C3 | While offline, try to reach Deploy | Clear refusal, not a traceback | ⬜ (needs the unbuilt work) |
| C4 | Switch back to device mode | Title updates; offline folder cleared; device flow normal | ⬜ |
| C5 | Bounce between modes several times | No state leaks across transitions | ⬜ |

State leaking across a transition is the likely failure. `garmin_root`
is forced to `None` on entering offline mode specifically so that
anything slipping through fails loudly rather than quietly writing to
hardware you didn't mean to involve.

---

## D. Mixed-device folder

| # | Step | Expect | Result |
|---|---|---|---|
| D1 | Put one 530 profile into a folder of 840 profiles, open it offline | Advisory naming both serials; **not** a block — keeping two devices' profiles together is legitimate | ⬜ |

---

## E. Backup store integrity

| # | Step | Expect | Result |
|---|---|---|---|
| E1 | After backups from both devices, inspect `backups/` | Separate `<serial>/` folders; legacy flat folders untouched | ⬜ |
| E2 | Restore from Backup, on each device in turn | Only that device's profiles offered, plus legacy ones | ⬜ |
| E3 | Clean Up preview | Spans both layouts; a non-timestamp junk folder is ignored | ⬜ |

---

## Bugs found so far, all from real use rather than reading the code

| Found in | Bug | Status |
|---|---|---|
| A5 | Startup Message reported unsaved changes with no edits made | **fixed twice** — `SpinCtrl(min=1)` couldn't hold Garmin's own `<display = 0>` and silently clamped to 1; then the same flaw in the text control, where `parse_startup_txt` leaves a trailing newline a `wx.TextCtrl` may not return. Both baselines now read back **from the controls** after loading |
| A6 | Clean Up showed only a count, never a list | fixed — lists snapshots with device serial and size |
| A6 | Backups from today never appear at any sensible day count | fixed — always-visible store summary line, independent of the filter |
| A6 | Preview text drew underneath the dialog buttons | fixed — dialog height no longer fixed; re-fits after each change, grows only |
| B5 | Refresh didn't pick up files added to the folder | fixed — the folder is re-scanned on every backup, not cached at pick time |
| — | "Deleted, restore me" list spanned all devices | fixed — scoped by serial, legacy backups still included |

Six bugs from part of one section. That is the argument for finishing
the three unbuilt pieces before the next full pass rather than testing
in slices.

---

## Separate from the GUI — the 840 profile work

Independent of this release; needs no GUI.

- [ ] Clone the three pre-setup 840 profiles under new names
      (`ROAD840`, `INDOOR840`, `MOUNTAIN840`) with
      `fit_clone_profile.py --name`, giving each a **new filename** too
      — the device matches by filename and will otherwise overwrite
- [ ] Copy them into `Garmin/NewFiles/`, restart, confirm they appear
      alongside the migrated profiles
- [ ] **Pull one back and diff it.** If the only difference is
      `file_id.number`, then `patch_screen()`'s byte-range patching
      preserved the 840-only **mesg-14 field 14** through a full round
      trip — currently reasoning, not evidence, and every future 840
      write depends on it
- [ ] Pull the profile carrying the **Map and Compass data fields** so
      their IDs can be read out (neither is in `FIELD_ID_NAMES`)
- [ ] Try one of those two in a **half-width** slot — a 3-field stacked
      layout is all full-width, so whether they degrade like the
      Graph/Bars fields is still unknown

---

## F. Export and mode isolation (#141/#142) -- 2026-09-29

**Do F6 first if you only do one thing.** The Deploy button was rebound
to a dispatcher serving BOTH modes, so device-mode Deploy is a real
regression risk, on the path used most.

The rest exists because Export's button-to-handler wiring is the one
part that cannot be checked headlessly -- the same gap that let the
per-model feature ship inert on 2026-09-28.

| # | Step | Expect | Result |
|---|---|---|---|
| F1 | Offline mode, open a profile, edit any screen | Bottom-right button reads **"Export Profile..."** and is ENABLED | |
| F2 | Before editing anything | Same button is DISABLED (nothing to export yet) | |
| F3 | Click Export | Save dialog pre-filled with the CLEAN filename -- `CyclingRoadCensus3.fit`, **not** `..._staged_...fit.editing.fit` | |
| F4 | Save it | Success dialog says the copy was read back and matches byte for byte; file exists at that path with that name | |
| F5 | Export again, rename it in the dialog | Warning that the Edge matches by filename and will silently ignore a mismatch; offers to use the right name; **warns, doesn't refuse** | |
| F6 | **REGRESSION: device mode, 530 connected, edit a screen** | Button reads **"Review && Deploy..."** and still reaches Pre-Flight exactly as before | ✅ PASS |
| F7 | Offline mode, Detect panel | **"Startup Message..."** is greyed out | |
| F8 | Device mode, Detect panel | "Startup Message..." is enabled again | |

**If F6 fails, stop and report** -- that one breaks existing behaviour
rather than a new feature.

**Not worth testing yet:** `startup.txt` offline (#145) is unbuilt, so
F7's greyed button is correct rather than a defect.

**Section F result: ALL PASS (2026-09-29).** F4 was re-scoped mid-test --
Doug asked whether the CRC was checked and it wasn't, only a byte-for-
byte read-back. Export now does both; see the commit and Doc rev 126.

**Beyond the plan, same session:** real work deployed to BOTH devices --
ROAD profile, 8 fields -> 7/B, with a Connect IQ field (Windfield) moved
two positions first. Survived on the 530 (device mode) and on the 840
(offline mode + Export + OpenMTP). See Doc rev 126.
