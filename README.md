# Activity Profile Editor for Garmin Edge

## What it does

This toolkit reads and edits Garmin Edge 530 Activity Profile screens
directly, on a computer, instead of through the on-device menu —
reordering screens, changing which data fields appear and in what
layout, showing/hiding or deleting screens outright, cloning a
profile under a new name, restoring a profile from backup, and
batching several changes into one device write/restart. Cloning
duplicates the entire profile file, not just its screens — every other
setting you've already tuned (navigation, alerts, sensor pairing, and
everything else that isn't a data screen) comes along automatically,
so creating a second, similar profile doesn't mean redoing all of that
by hand the way it does starting a new profile on-device. It reaches
data fields the on-device editor doesn't expose at all (power-meter/
Shimano Di2 metrics, Torque Effectiveness, Balance, TSS/IF, and more).

Two ways to use it, sharing the same validated backend and the same
automatic backup-before-every-write safety net: a point-and-click
**GUI** (`gui_app.py`) that walks through detect → back up → edit →
review → deploy, or a set of **command-line tools** (`fit_dump.py`,
`fit_patch.py`, and others) for the same operations plus lower-level
inspection, useful for scripting or checking exactly what a change
will do before it's written.

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

## Which Edge models this works with — and the two ways to use it

There are **two workflows**, and which one you get depends on how your
Edge connects to a computer. Both end with an edited profile on the
device; they differ in who moves the file.

| | **Connected mode** | **Offline mode** |
|---|---|---|
| Your Edge appears as | a normal disk — a volume under `/Volumes` on macOS, a drive letter on Windows | a "Portable Device" (MTP), or nothing browsable on macOS |
| Models | **Edge 530** *(tested)*, and other USB Mass Storage Edges | **Edge 840** *(tested)*; **540, 1040, 1050** reported as MTP |
| The toolkit | finds the device itself | asks you for a folder of `.fit` profiles |
| Writing the result | **Deploy** — straight to the device | **Export** — to a folder, then you copy it across |
| Restore from backup | yes | no, it is a device operation — the panel points you at your backup folder instead |

Garmin moved the newer models to MTP (Media Transfer Protocol), which
presents a firmware-controlled view rather than a real disk. Note this
may have arrived on your device through a firmware update rather than
being true when you bought it.

Offline mode is not only for MTP devices — it is also how you edit a
profile you pulled last week with nothing plugged in.

### Connected mode, step by step

1. Plug the Edge in and wait for it to mount.
2. Start the toolkit; it finds the device and lists your profiles.
3. Edit screens, fields and layouts.
4. **Deploy.** The toolkit backs up the original first, writes, then
   reads the file back and byte-compares before reporting success.
5. Eject and restart the Edge.

### Offline mode, step by step

1. Copy the profiles off the device with an MTP browser —
   [OpenMTP](https://openmtp.ganeshrvel.com/) or Commander One on macOS,
   Explorer on Windows. They live in `Garmin/Sports/` as `.fit` files
   named after the profile.
2. Start the toolkit and choose **"Work Without a Device…"**, then point
   it at that folder.
3. Edit exactly as you would with a device attached — the profile list,
   screens view, editor, backups, Clone and the boot-message editor all
   work the same.
4. **Export.** It writes to a folder you choose, reads the result back
   and byte-compares it, and checks the file's own CRC before writing
   anything at all.
5. Copy the exported file into `Garmin/NewFiles/` on the device and
   restart the Edge.

**The filename matters, and the dialog handles it for you.** The Edge
matches profiles by filename on import and silently ignores anything
that does not match — no error, no indication, the profile simply does
not change. The save dialog pre-fills the original filename. Change it
anyway and you get a warning naming the consequence, not a refusal:
exporting a spare copy under another name is legitimate.

`startup.txt`, the custom boot message, works in both modes.

### Does the `NewFiles/` route actually work over MTP?

**Yes — confirmed repeatedly on an Edge 840.** An edited ROAD profile
has gone through it end to end, including a Connect IQ field that
survived three chained edits, and a screen using a layout variant the
530 does not offer, which the 840 rendered correctly. A hand-built
`Totals.fit` written the same way was also accepted.

This was an open question until v1.5.0 and is recorded here because
earlier versions of this README asked readers to help answer it.


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

The toolkit itself (CLI tools and GUI) runs on both **macOS** and
**Windows** — device detection is confirmed working on real hardware
on both (see `garmin_device.py`'s changelog). Both platforms have a
one-command setup script (`install.sh`/`install_windows.bat`); the
*after-setup launch path* differs a bit, covered below for each.

### macOS

Run the install script — it checks your python3 version, creates a
dedicated `.venv` (nothing touches your system or Homebrew Python),
and installs both dependencies (`garmin-fit-sdk` and `wxPython`) into
it:

```bash
./install.sh
```

Safe to re-run any time; add `--upgrade` to update already-installed
packages, or `--help` for details. It's a plain bash script, no
network access beyond pip, and no admin/sudo required.

Once that's done, launching the GUI from here on doesn't need Terminal
at all — double-click **`launch_gui.command`** in Finder. (The very
first double-click will likely be refused by Gatekeeper as "from an
unidentified developer" — right-click, or Control-click, the file and
choose Open instead, just that first time; every launch after that
works with a normal double-click. This is standard macOS behavior for
any downloaded/unsigned script, not specific to this toolkit.) This is
the macOS equivalent of Windows' native double-click-`gui_app.py`
convenience below — macOS has no matching file association to hijack
the way Windows' installer does, so a small launcher script is the
actual fix here, not a workaround; see `PROJECT_NOTES.md` "macOS
double-click launcher" for the full story of why.

Prefer to do it by hand, or need just the CLI tools without the GUI's
`wxPython` dependency? The manual equivalent:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install garmin-fit-sdk --break-system-packages
```

### Windows

`install_windows.bat` — download or copy the whole toolkit folder
(Doug used a `Documents` subfolder), then double-click
`install_windows.bat` in File Explorer. It checks for Python 3.10+
(the `py` launcher, falling back to `python.exe`), installs
`garmin-fit-sdk` and `wxPython` directly — deliberately no virtual
environment, see below — and verifies both import cleanly. If Python
isn't found or is too old, it opens the python.org download page and
stops with instructions rather than trying to install Python itself.
**Not yet confirmed on real hardware** — written against Doug's own
confirmed-working manual sequence below, but there's no way to
dry-run Windows batch syntax in this project's dev environment (no
`cmd.exe` available), so this needs a real run before it can be
trusted the way the manual steps already are.

Prefer to install by hand, or the script hits a snag? This is the
exact sequence Doug used for the confirmed-working 2026-08-19 test, no
venv involved:

1. Install Python from [python.org](https://www.python.org/downloads/windows/)
   (the standard Windows installer, downloaded via browser).
2. Install the two dependencies directly — no virtual environment
   needed for this toolkit on Windows:
   ```powershell
   python -m pip install garmin-fit-sdk wxPython
   ```
3. Copy the *whole* toolkit folder somewhere (Doug used a `Documents`
   subfolder) — not individual `.py` files. `garmin_device.py`, for
   example, imports `fit_dump.py` at runtime, so a partial copy fails
   with `ModuleNotFoundError`.

From there, either run the CLI tools from PowerShell (`python
garmin_device.py detect`, etc.), or — found during testing, and a
nicer experience once setup is done — just double-click `gui_app.py`
in File Explorer to launch the GUI directly. That works here (and
deliberately doesn't on macOS, see the About section/`gui_app.py`
changelog for that story) because the python.org Windows installer
associates `.py` files with the same Python install `pip` just used —
there's no separate system-vs-project Python split for a file
association to point at the wrong one.

A `.venv` is optional, not required, on this path — reach for one only
if you want this toolkit's dependencies kept isolated from other
Python projects on the same machine:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install garmin-fit-sdk wxPython
```

(Double-clicking `gui_app.py` in File Explorer won't use a venv's
Python, though — that path only works with the direct, no-venv install
above; from inside a venv, launch via `python gui_app.py` in an
activated PowerShell instead.)

**⚠ Windows note, 2026-10-26.** The confirmations below are real but
they are **dated**, and what shipped between v1.5.0 and v1.7.3 was not
covered by them: a macOS-only call added on 2026-09-27 stopped the GUI
launching on Windows altogether, and both confirmations predate it.
Fixed; see the v1.7.4 notes. The CLI tools were unaffected throughout.
Windows is not currently part of the per-release test loop, which is
how seven releases went out with it broken — worth knowing before
relying on an untested release there.

Confirmed on Windows 11 (2026-08-19): `detect`, `screens` (both CLI
tools), and the full GUI workflow (add a screen, deploy, restart,
NewFiles round-trip). Also confirmed on Windows 10 32-bit (2026-08-29),
including the same `detect`/edit/deploy round trip — see the note below
for genuinely 32-bit-only hardware, which needs a different install
path from the one above. Linux is untested.

**Genuinely 32-bit-only hardware (no 64-bit CPU at all — confirmed on
an Intel Atom N270 netbook-era laptop) needs a different install path,
not just the 32-bit Windows installer above.** wxPython dropped
official 32-bit Windows wheels as of version 4.2.0, and the last
release that has one (4.1.1) only has wheels for Python 3.6–3.9 — so
this specifically needs 32-bit **Python 3.9.13** (the last 3.9.x
release with a binary installer at all — later 3.9.x releases are
source-only; get it directly from
`https://www.python.org/ftp/python/3.9.13/python-3.9.13.exe`, since
python.org's normal download flow now points to an installer that only
fetches current releases) plus a pinned wxPython:

```powershell
py -m pip install garmin-fit-sdk wxPython==4.1.1
```

`install_windows.bat` won't work for this case — it hard-checks for
Python 3.10+ — so skip it and run the command above directly. If `pip`
tries to *build* wxPython from source instead of downloading a
`cp39-cp39-win32` wheel, stop and double check the Python install is
really the 32-bit 3.9.13 build; a source build needs a full Visual
Studio C++ toolchain and isn't a realistic path here.

## Quick start

The commands below assume an active environment with both dependencies
installed. On macOS via `install.sh`, that means running `source
.venv/bin/activate` first (once per Terminal session — `launch_gui.command`
handles this for you for the GUI, but these are CLI commands, run
directly in Terminal). On Windows via the no-venv install path, no
activation step is needed at all.

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

What each file is for. **Versions are deliberately not listed here** —
they live in each file's own `__version__`, and a copy in this table has
no way to stay true: the one that used to be here drifted eight releases
before anyone noticed, because nobody reads a version column. Per-release
history is in the Changelog below.

| Tool | Purpose |
|---|---|
| `install.sh` | macOS setup script (`install_windows.bat` is the Windows counterpart) |
| `install_windows.bat` | Windows setup script |
| `launch_gui.command` | macOS double-click launcher for `gui_app.py` |
| `gui_app.py` | wxPython GUI — the whole workflow, and what most people should use |
| `garmin_device.py` | Detect, list, back up, stage, write, eject and wait-for-remount against the device |
| `fit_dump.py` | Read and inspect a `.fit` file — `dump`, `screens`, `diff`, `unknown` and `knowledge` subcommands. Also holds the field-name, layout and slot-height tables the rest of the toolkit reads |
| `fit_patch.py` | Patch a screen's fields, layout, order or visibility |
| `fit_chain.py` | Apply several `fit_patch.py` operations in sequence before one device write |
| `fit_clone_profile.py` | Clone a profile under a new display name (patches `sport_mesgs[0].name`) |
| `fit_census.py` | Read-only raw screen census across a folder of profiles. Reports counts, layout variants and screen types without names, for measuring what a model actually offers |
| `fit_sdk_check.py` | Checks whether the installed garmin-fit-sdk still mis-renders the profile-name field in a `Totals.fit`. Read-only. Exits 0 faithful, 1 mangled, 2 could not run — so a future SDK fix announces itself instead of going unnoticed |
| `fit_raw_walk.py` | Internal support — generic FIT byte-offset walker. Not meant to be run directly, but it is what to trust for undocumented messages |
| `fit_crc.py` | Internal support — FIT CRC-16. Not meant to be run directly |

`fit_dump.py knowledge` is worth knowing about on its own: it prints what
the toolkit has actually measured per model — which layout states have
grids, which have row heights, which are undrawable — and self-checks
those tables. Run it before assuming something is unknown.


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

## Working with Connect IQ data fields

If you use third-party Connect IQ data fields, there's one rule worth
knowing and one workflow that follows from it.

**The rule: this toolkit can move a Connect IQ field, but not create
one.** Reorder it within a screen, add or remove ordinary fields around
it, remove it, delete or reorder whole screens that hold one — all
fine, and the underlying link Garmin uses is kept correct
automatically. What it won't do is put a Connect IQ field somewhere it
isn't already. The reason is a limitation of the file rather than a
policy choice: a Connect IQ field is stored as a generic marker that
carries no app identity, so nothing in an edit says *which* app a new
one should be. Only Garmin's own on-device editor can make that choice.

**The workflow: set it up once on the device, then clone.**

1. Using the Edge's own screen editor, build one profile with your
   Connect IQ field(s) placed where you want them.
2. In this toolkit, **Clone** that profile under a new name. The clone
   is a byte-for-byte copy, so the Connect IQ placements come with it
   intact.
3. Now edit the clone freely — rearrange the fields on the Connect IQ
   screen, add or remove ordinary fields around it, add or delete other
   screens, change layouts. Deploy when it looks right.

That gives you as many variants as you like — a race setup, a training
setup, a bad-weather setup — all carrying the same Connect IQ fields,
without touching the device's editor again. Repeat step 2 from the same
source profile whenever you want another.

**A few practical notes.** Connect IQ fields generally need a
full-width row to be readable; the device will happily let you put one
in a half-width slot, and the GUI will point it out but won't stop you.
A screen holding *two* Connect IQ fields can't be edited here at all —
with two generic markers on one screen there's no way to tell which app
ended up where after a rearrange, so the toolkit refuses rather than
risk swapping them. And if a Connect IQ field ever shows up as
**"Timer"** on the device, that's Garmin's fallback for a field whose
link is missing; restore from a backup, or set it again on the device.

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
- **Connect IQ data fields (third-party apps like WindField) can be
  moved, rearranged around, and removed — but not added.** As of
  v1.3.0 this toolkit keeps Garmin's own Connect IQ link record (FIT
  message 170, undocumented in the published FIT Profile) in step with
  your edits, so a Connect IQ field follows a reorder instead of
  breaking. Confirmed on real hardware for moving one within a screen,
  inserting or removing ordinary fields around it, removing it
  outright, and shifting it as a side effect of editing a neighbour.

  Two things are still refused, and both are refused because the
  information genuinely isn't there rather than out of caution.
  **Adding a Connect IQ field to a screen that doesn't have one**: the
  field id stored in the file is a generic "a Connect IQ field goes
  here" marker carrying no app identity — two different apps are
  byte-identical in the field array — so nothing in the edit says which
  app a new one should resolve to. **Editing a screen that already has
  two Connect IQ fields on it**: for the same reason, there's no way to
  tell which app ended up where after a rearrange, and this toolkit
  won't guess and risk silently swapping them. In both cases, use
  Garmin's own on-device editor.

  If a Connect IQ field ever shows as **"Timer"** on the device, that's
  Garmin's fallback for a marker no link record claims — the symptom
  every pre-v1.3.0 version of this toolkit produced when it rewrote a
  screen. Cloning a whole profile has always been safe, and still is.

  **Favorite Screen** still won't carry a Connect IQ field across to
  another profile, and saving one is still refused: that needs a link
  record created from scratch, the one case not yet confirmed on
  hardware. See `PROJECT_NOTES.md` Doc rev 95-109 for the full
  investigation, including the decoded message-170 format.

## Changelog

Detailed, chronological doc-revision notes -- every fix, feature, and
correction to this project, newest first. Most readers won't need
this; it's kept for the full history.

*Doc rev 88 — refreshed 2026-10-27.* **v1.7.4: the GUI starts on
Windows again, and offline work can leave the app.** See
`RELEASE_NOTES_v1.7.4.md`.

**The Windows crash is the headline, and the testing gap behind it is
worth stating.** One line in the boot-message editor called a
macOS-only wx method behind a guard that checked whether the method
*exists* — wxPython provides it everywhere and raises off macOS, so the
guard passed and the call failed. Because every panel is constructed at
startup, that killed the app before it drew a window. Seven releases,
v1.5.0 through v1.7.3, shipped it. The cause of the delay was not
subtlety — one launch catches it — but that Windows left the test loop
in August while the offending line arrived in late September. The CLI
tools were unaffected throughout.

**Offline clone and restore had no way out.** Both navigate straight to
the deploy page, which offered only "Write to Device" and refused when
pressed, with export living on a panel neither flow returns to. That
page is now mode-aware: Export offline, with the same CRC-plus-read-back
verification, and the device-only controls hidden rather than greyed.
The export routine itself was *extracted* and shared rather than copied,
since it carries three separately hard-won behaviours that must not
drift apart.

**And the clone dialog's filename field** no longer stays stuck once you
clear it — an empty field has nothing to protect, so the auto-suggestion
resumes.

Separately established and recorded while testing: **the Edge renames
an imported profile**, constructing the filename from the profile's own
sport and display name. The `Cycling…` convention is the device's
output, not a rule users follow.

*Doc rev 87 — refreshed 2026-10-23.* **v1.7.3: three data fields that
were never in the Edge's menu, and the ten-screen limit enforced
everywhere.** See `RELEASE_NOTES_v1.7.3.md` for the user-facing summary.

Ids 358 "Elevation (Asc/Desc)", 371 "Speed Over Ground" and 395 "Battery
Hours" join the picker. None was reachable by the method used until now.

**The field list had been built by walking the on-device menu**, which
misses a field three ways: when its label duplicates another's (the
Avg/Max group, v1.6.1), when it has no label at all (358), and when the
field simply is not in the menu (371, 395). The third was not understood
before this release and is the widest — these ids belong to a catalogue
shared across Garmin's product range, and the Edge renders entries it
never offers. 371 is documented in the Venu 4 manual, 395 in the fenix 7
manual, neither in the Edge's.

So the method changed to writing unknown ids into slots and reading what
the device draws. 66 probed, 4 found. A fourth, id 331, is real and
remains unnamed: no label, and it holds `0:00` through an entire ride
while every other timer counts.

358 and 395 are confirmed by behaviour on a real ride — ascent and
descent accumulated, and the battery figure counted down. 358 is
deliberately left out of the Avg/Max family despite looking like its
missing fifth member: family membership drives the placement warnings,
and its half-width behaviour is unmeasured.

**The ten-user-screen limit now lives where every write path can see
it.** It had lived in the GUI's Add Screen panel alone, so the command
line could push a profile past it — which is how the field probe got
built, eight extra screens on one profile. Such a profile rides fine and
renders every screen, but the device's own editor shows the overflow as
blank entries that open to nothing, so those screens can only ever be
changed by this toolkit again. `--new-slot` now refuses, with
`--allow-over-cap` to do it deliberately.

*Doc rev 86 — refreshed 2026-10-21.* **v1.7.2: one layout picker for both
kinds of screen.** See `RELEASE_NOTES_v1.7.2.md` for the user-facing
summary.

An ordinary screen's field count was reachable only through Add and
Remove Field, one field at a time — nine clicks from 1 field to 10, with
a dropdown beside it that changed the variant alone. Garmin's named
screens have had the device's own whole-layout menu since v1.4.0, and the
device makes no such distinction: its layout control is one list on both
kinds. Now so is the toolkit's.

**Nothing had to be built.** `layout_states()` has returned the
plain-user states for a non-named screen type since it was written — 24
on an 840, 15 on a 530 — the label helper already handled it, and the
handler was never named-specific. The change is two branches collapsing
into one and two now-dead methods deleted, rather than kept dormant: two
writers for the same byte is how this project's layout tables drifted
apart once already.

Add and Remove Field stay available on an ordinary screen and stay off
for a named type. On a named type the count arrives with the layout; on
an ordinary one it is the user's, and Add Field also chooses *which*
field arrives, which jumping to a layout cannot.

**The old dropdown was safe from the v1.7.1 data-loss class by
inability, not by design** — it could not reach the count, so it could
not lose a field. Making the count reachable removes that protection and
leans entirely on the v1.7.1 fix, which is why the bench run made the
shrink-grow-cycle section mandatory. Seven steps, both models, no field
substituted.

**Also fixed, found while testing:** the note under the layout diagram
ended "(not shown to scale here)" on a diagram that has drawn to scale
since v1.7.0 — three releases of text telling the reader to disbelieve a
correct picture. It is removed only where the rows really are drawn to
scale; where the model is unknown the diagram still draws uniform rows
and the note still says so.

*Doc rev 85 — refreshed 2026-10-18.* **v1.7.1: changing a layout no longer
throws your data fields away.** See `RELEASE_NOTES_v1.7.1.md` for the
user-facing summary.

**The toolkit was the only thing deleting fields.** Four device pulls
settled it: the Edge's entire behaviour for a layout count change is to
write ONE byte, the count. The field array is always ten slots and the
count is simply how many are shown, so a 10 → 4 → 10 round trip on the
device returns the file byte for byte identical. Nothing is deleted,
which is why its layouts have always appeared to remember.

`fit_patch.pack_field_id_array()` had padded short lists with `0xFFFF` on
every write — one line, and the whole of "cycling layouts loses my data
fields". It now merges into the stored array, and rejects a short base or
an over-long list so a caller that still truncates fails loudly instead of
silently wiping a tail. Four write sites audited together, each judged
separately: the layout picker writes the count alone, Change Field Type
merges, the swap path already read-modify-wrote all ten, and new-screen
creation still pads because there is no tail to keep.

**Verified byte-identical to Garmin's own editor** for shrinking, growing
and changing a single field, against the real device pulls.

**An asymmetry caught by Doug's knowledge of the device**, not by testing:
the Edge has no add-or-remove-field control after a screen exists — only
the layout control and per-field changes. That makes Add Field and Remove
Field this toolkit's own inventions, and once growth started revealing the
parked field, widening 4→5 restored it while Add Field silently consumed
it. The picker now opens on whatever is already in that slot. The general
point is that an operation the device cannot express has nothing to be
consistent with, so its semantics have to be chosen rather than inherited.

**v1.7.0's warning was corrected in the same release that falsified it** —
it said the loss could not be undone, which stopped being true. Shipping a
true warning and leaving it to quietly become a lie would be worse than
never having written it.

*Doc rev 84 — refreshed 2026-10-15.* **v1.7.0: the layout diagram tells
the truth about slot sizes.** See `RELEASE_NOTES_v1.7.0.md` for the
user-facing summary.

**Rows are drawn to scale.** The diagram had drawn every row the same
height, which made some layouts indistinguishable — 3 fields A, B and C
share a row structure and differ only in row height, so all three drew
identically and a line of text was the sole distinguisher. They now draw
as the device shows them. Plain user screens only: named types have no
measured row heights (all twenty), and drawing a guess is how v0.26.3
ended up rendering geometry nobody had checked.

**Placement advice is per model and per family.** The old rule equated
"shares a row" with "loses the widget" and was wrong in both directions —
a false alarm on the 840, which draws the widget fine at half width, and
silent on the 530, where a Graph field in a full-width regular-height row
quietly loses its AVG and MAX. The second mattered more: the 530 is the
device the rule was measured on, and every observation behind it came
from the half-width case. Messages now state the remedy, which differs by
family, and the toolkit says nothing when it cannot tell which model a
profile came from — guessing is what produced the old advice.

**The layout-shrink warning says the loss is permanent.** It always named
the fields being dropped; it never said switching back would not restore
them. Behaviour unchanged — the fix is a per-count cache, and the device's
own editor manages it, so the toolkit should.

**Two fixes.** The first screen no longer implies a USB cable is required,
on the one screen every user starts on and where an 840 owner has no USB
route at all. And the Add New Screen panel's placement warnings work
again after stopping entirely — introduced and fixed within this release,
found by reading call sites, because a warning that stops appearing looks
like a screen with nothing to warn about.

**New `fit_sdk_check.py`**, and a settled question. Three garmin-fit-sdk
versions across five point releases all mis-render the `Totals.fit`
profile-name field identically, and the mechanism says they always will:
the field is undocumented, so it has no entry in the SDK's profile, so
the decoder has no declared type and guesses. Not a defect Garmin would
recognise. The standing rule to prefer this toolkit's raw parser is
therefore structural rather than version-bound, and the SDK stays
unpinned.

*Doc rev 83 — refreshed 2026-10-14.* **v1.6.1: four data fields that were
hiding behind other fields' names.** See `RELEASE_NOTES_v1.6.1.md` for the
user-facing summary.

**Ids 351–354** — `Heart Rate (Avg/Max)`, `Speed (Avg/Max)`, `Cadence
(Avg/Max)`, `Power (Avg/Max)`. A third family in the device's Graphical
menu alongside the Graph and Bars entries: a live numeric readout plus AVG
and MAX, no widget at any size on either model. Confirmed on a 530 and an
840 by placement and pull, and deployed to both.

They are the **first name collisions** this catalog has held — the device
calls each of them exactly what it calls ids 13, 48, 3 and 36 — and that
collision is why they went unfound. Every census was built by reading menu
labels and skipping the familiar ones, so a field wearing another field's
name was invisible *and* left no trace of having been skipped. A new
`check_field_name_uniqueness()` makes the rule enforceable rather than
merely true: collisions are allowed, but a colliding id must be declared,
so the next one fails a check instead of producing a picker a user cannot
choose from.

Naming follows this table's own convention — a content qualifier, as in
`HR Zone 1 (time)` and `Intensity Factor (IF)`, not the menu category. The
real device string is shown alongside, so a row reads `Speed (Avg/Max)
(id=352, shows as "Speed")`.

**Two fixes.** A favourite saved from an 840 C-variant screen came back as
an A, silently; the clamp responsible predated C variants and was defeating
a model-aware check that had been added for exactly this case. And the Add
Field dialog was about to truncate its longest rows, which are now the new
ones — it is a list with no horizontal scrolling, so a cut row gives no
indication it was cut.

**The front page was wrong.** It still described the 540, 840, 1040 and
1050 as "currently unusable" and offline mode and Export as unbuilt, both
untrue since v1.5.0, and asked readers to answer a question a real 840 had
settled many times. Replaced with a Connected-vs-Offline workflow
comparison.

**Slot heights are now complete** — all 24 Edge 840 user states and all 15
on the 530 — though nothing draws to scale yet. The useful consequence: a
taller full-width row exists only at 1, 3, 4, 5, 6 and 7 fields, so no
rearrangement of an 8-field screen will ever give a field more height.

*Doc rev 82 — refreshed 2026-10-08.* **Row heights are measured, and the
v1.6.0 notes are corrected rather than rewritten.**

Data-field **row heights** are now recorded for both models. The rule came
from measuring the device: a row of two half-width fields is always 1/5 of
the screen, so the screen is five units tall, a half-width row costs one
unit, and the full-width rows share what is left. 22 of the Edge 840's 24
user-screen states are recorded, and 13 of the 15 the 530 offers — derived
rather than re-measured, because the 530's A and B layouts resolve to the
same grids as the 840's.

The practical consequence, for anyone placing a data field that wants
vertical room: **a taller full-width row exists only at 1, 3, 4, 5, 6 and
7 fields.** Every 8-, 9- and 10-field layout is five regular rows in every
variant, so no rearranging of an 8-field screen will ever give a field more
height. Drop to 7 or fewer and pick the B or C variant, which is what the
variant letter is for — it chooses where the tall row sits.

`fit_dump.py knowledge` prints the coverage for both models and
self-checks the table. Nothing is drawn to scale or annotated in the GUI
yet; that is the next piece of work.

**Correction to v1.6.0.** The `v1.6.0` tag includes the first two of these
commits, which its release notes do not describe: the tag carries
`fit_dump.py` 2.23.0, not the 2.21.0 printed in those notes, and the Known
gap reading *"row and content height are unmodelled"* is now half
superseded — content height still is, row height is not. No behaviour
differs; nothing outside `fit_dump.py` calls the new table.
`RELEASE_NOTES_v1.6.0.md` carries the correction at its top and its body
is left as written.

*Doc rev 81 — refreshed 2026-10-07.* **v1.6.0: the Edge 840 stops being
a guess.** See `RELEASE_NOTES_v1.6.0.md` for the user-facing summary.

**Every 840 layout state is now measured or explicitly marked undrawable.**
v1.5.0 stopped the toolkit applying one device's measurements to another;
it did not yet KNOW the 840. This closes that. 50 named states have grids,
nine user-screen layouts the 530 does not offer were measured and wired,
and `fit_dump.py knowledge` prints the whole picture derived from the
tables rather than written beside them — a hand-maintained status table
would have been a fifth copy of facts that live in the dicts, which is this
project's most repeated failure mode.

**206 data fields, up from 173**, from one profile built for the purpose:
five screens each anchored with a known field so a transposition would be
visible, pulled once. 520 and 578 — the only two entries left in
`KNOWN_UNRESOLVED_IDS` — are Primary and Secondary Target, and the
strongest evidence was not the census at all: both already sat on the
device's own Workout screen template beside Duration and Workout
Comparison, in a record nobody had edited.

**The layout control is a dropdown built from what the model offers.** Two
radio buttons could not express three variants, so on an 840 a 9-field
screen showed A and B with B unselectable and no C. The post-hoc legality
refusals are deleted rather than corrected: the control is built from the
legal set, so an illegal variant is unreachable by construction. The
selection INDEXES the offered list and is not the f8 value — Segment's menu
"A" stores f8=2 on the 530, so treating the index as an f8 would silently
write the wrong byte.

**Where the toolkit does not know a layout it now draws nothing and says
so**, instead of falling back to ordinary user-screen geometry. That
fallback was not harmless: for eBike Metrics it would have drawn four of
eight layouts correctly and four wrongly, with nothing on screen
distinguishing the halves. Unpredictably wrong is worse than consistently
wrong. Today the blank appears only for Radar, whose layout is a left-hand
column the row model cannot express.

**Cross-model transfers are measured rather than guessed.** An 840 profile
pushed to a 530 and pulled back: a screen type the target lacks is dropped
entirely, an unknown field id renders as Speed (not the "Timer" fallback a
Connect IQ field gets, so the two diagnose differently), an unsupported
layout renders as a legal one, and nothing is rewritten — all 33 foreign
ids survived in the file. So a migrate is lossy on screen and reversible on
disk. The device also RE-INDEXES the screens it keeps, which makes the
deploy change summary unreliable after such a transfer; the warning says
so.

**A pre-existing 530 defect, surfaced by an 840 symptom.** A 530 Segment at
4 fields in layout A displayed as "-" in the screens list, the CLI and the
deploy summary, because all three derived the letter by arithmetic on f8
and that layout stores 2. Fixed once, in one shared place.

Also: the offline restore dead end closed (restoring is a device operation,
so the controls are gone offline with a line pointing at the backup folder
instead), a crash on the only offline entry path, the named picker reading
"(3)" where it meant "(C)", and confirmation from the bytes that a
toolkit-written f8=2 survives NewFiles and renders correctly.

*Doc rev 80 — refreshed 2026-09-29.* **v1.5.0: offline mode, Export,
and per-model layout rules.** See `RELEASE_NOTES_v1.5.0.md` for the
user-facing summary.

**Work without a device.** "Work Without a Device..." takes a folder of
`.fit` profiles in place of a mounted Edge, and everything downstream
behaves the same. This is what makes the toolkit usable at all on models
that connect over MTP and can never be mounted (540, 840, 1040, 1050) —
but it is also simply how you edit a profile you pulled last week with
nothing plugged in. **Export** replaces Deploy: it writes to a folder
you choose, checks the file's own CRC before writing anything, then
reads the copy back and byte-compares before reporting success. The save
dialog pre-fills the profile's ORIGINAL filename, because the device
matches by filename on import and silently ignores anything else —
no error, no indication, the profile simply does not change.
`startup.txt` gets the same treatment.

**Layout rules are per-model.** Every table in this toolkit was measured
on an Edge 530 and applied to every device. With two models that started
REFUSING states the hardware permits — Compass is locked at 2 fields on
a 530 and the 840 offers 0, 1 or 2. The model is now read from
`file_id.product` in the profile itself, so it works offline and on
backups, and each model's rules apply only to that model. **Where a
model has not been measured, the toolkit advises instead of refusing**:
it will say a count looks unusual and write it anyway, rather than
blocking an edit on hardware it has never seen. The 840's measured rules
are included.

Why it cannot be derived: Segment stores different values on the two
models for the same screen type, the same visible layout and the same
field geometry. No rule generates that, so unmeasured combinations are
allowed rather than guessed at.

**Fixes.** The guard protecting your last visible data screen counted
switched-off screens as active — on an 840 profile with exactly one user
screen it counted seven, and now counts one. Switched-off screens (the
hardware-conditional ones an 840 holds in reserve) were listed as
ordinary editable screens and are now shown separately. New screens on
an 840 were named absurdly ("Screen 164"). The window stretched to
screen width on a long details block, which is now a scrolling pane that
never widens the window. The screens list shows ten rows rather than
six. Backing out of a profile you only looked at no longer warns about
unsaved edits. Four new data field names.

Prior rev (79, 2026-09-12) follows.*

*Doc rev 79 — refreshed 2026-09-12.* **Documentation only, no code
change: which Edge models this actually works with.** Newer Edge models —
reported for the 540, 840, 1040 and 1050 — connect over MTP rather than
as a USB mass-storage disk, so they never appear under `/Volumes` on a
Mac or get a drive letter on Windows. This toolkit finds your Garmin by
looking for that mount, which makes it a hard stop at the first screen
rather than a degraded experience. That was previously undocumented, so
anyone with a current-generation Edge would reasonably have concluded the
software was broken.

The new "Which Edge models this works with" section says so plainly. It
also corrects a first draft of that section, written the same day, which
described a manual workaround — copy the profile off, use Import Profile,
copy the result back — **that cannot actually be followed today.** The
GUI disables its Next button when no device is mounted, and Import
Profile lives behind that gate, so an MTP user can't reach it. Publishing
instructions that dead-end would have been worse than saying nothing, so
the section now states plainly that these models are unusable at present
and describes the offline-mode + Export route as planned rather than
available. Scoped in `PROJECT_NOTES.md` under Open items.

Flagged there too: whether `NewFiles/` is visible and writable over MTP
at all is **unverified**, since this project has no MTP device to test
against — with a request for anyone who has one to report what they can
see, because that answer decides whether the work is worth doing.
Prior rev (78, 2026-09-10) follows.*

*Doc rev 78 — refreshed 2026-09-10.* **v1.4.0 — Garmin's special screens
are now edited the way the device actually presents them.** Map, Segment,
Compass, Elevation, ClimbPro, Cycling Dynamics, Lap Summary, eBike
Metrics and STEPS Metrics each have their own rules, and the editor had
been treating all of them like ordinary screens.

Instead of Add/Remove Field and an A/B choice, these screens now offer a
single **Layout** list containing exactly what the device offers — for a
Segment that's 0, 2, 4/A, 4/B or 6 fields, with no odd number available,
because the Edge doesn't allow one. Screens fixed at two fields (Compass,
Elevation, ClimbPro, Cycling Dynamics) no longer let you add a third: the
device would quietly show only two while the file claimed three. Map and
Segment can now be set to **no data fields at all**, which is a layout
the device has always supported and the toolkit simply couldn't express.

The layout diagram draws the map, compass rose or lap table as its own
block, so what you see matches the shape of the real screen — including
Lap Summary, whose fields sit *above* its content rather than below. The
"needs full width" advisories for Graph/Bars and Connect IQ fields are
corrected too: they read a two-field special screen as two stacked
full-width rows, when the device puts those fields side by side at half
width, and so stayed silent exactly where the warning mattered most.

Also fixed: setting a Segment to its 4-field "A" layout wrote the wrong
value. If you have a Segment screen set that way from an earlier version,
re-pick the layout once and it'll be stored correctly.

If a screen already holds more fields than its type supports, the editor
now says so and tells you what the device will really show — and leaves
the file exactly as it is. Nothing is rewritten unless you choose a
layout yourself. Prior rev (77, 2026-09-10) follows.*

*Doc rev 77 — refreshed 2026-09-10.* **v1.3.1 — GroupTrack List,
Virtual Partner and Workout can no longer have data fields edited.**
Selecting one and pressing "Add Field..." used to open the normal field
picker. The device generates these screens itself — the riders you're
connected to, your Virtual Partner, the current step of a structured
workout — and Garmin's own on-device editor offers no field options for
any of them, so there was nothing there to edit. The field buttons and
layout choice are now greyed out, with a hard refusal behind them in
both the GUI and `fit_patch.py`. Showing, hiding and reordering these
screens still work normally; only field editing is blocked.

Workout had previously only been warned about, because unlike the other
two it stores a real, readable field array. That turned out to be the
useful part: the three screens store 0, 255 and 2 fields respectively
and none of them is editable, so what a screen has stored says nothing
about whether you can edit it. Each type has to be checked against the
on-device editor individually, which is the bar for anything added to
this list later.

Also under investigation, not yet changed: the layout diagram draws
Garmin's special screens (Map, Lap Summary, Elevation and friends)
using the ordinary two-stacked-fields arrangement, which isn't how they
actually render. That affects the full-width advisories as well as the
picture. A survey of all twelve of these screens is now complete and
the fix is scoped for the next release. See `PROJECT_NOTES.md` Doc rev
111. Prior rev (76, 2026-09-06) follows.*

*Doc rev 76 — refreshed 2026-09-06.* **v1.3.0 — Connect IQ placements
are maintained instead of refused. The limitation this project has
documented since v1.2.2 turned out to be a missing write, not a wall.**

FIT message 170, which is absent from Garmin's published FIT Profile
entirely, was decoded and confirmed on real hardware. It holds one
record per Connect IQ app used by a profile: the app's UUID, plus a
packed list of exactly which screen slot and field position that app
occupies. Every symptom this project chased since Doc rev 95 follows
from a single rule — the device renders a Connect IQ field only where
a record claims that exact position, and falls back to "Timer"
otherwise. Earlier versions rewrote screen field arrays without moving
the records, so the field moved and its record didn't.

The toolkit now keeps those records in step. Confirmed on a real Edge
530: moving a Connect IQ field within a screen, adding fields around
it, removing fields around it, removing the Connect IQ field itself,
choosing which app renders where two are installed, and a position
shift caused by inserting a neighbouring field. What was a hard
refusal in v1.2.2/v1.2.3 is now ordinary editing.

Two refusals remain, narrowed to what genuinely can't be determined
rather than what's merely risky. Introducing a Connect IQ field where
a screen has none is refused because the id in the file is a generic
marker carrying no app identity — two different apps store identically,
confirmed by putting both on one screen at once — so nothing in the
edit says which app it means. Editing a screen holding two Connect IQ
fields is refused for the same reason: after a rearrange there's no way
to tell which app went where. Neither has a `--force` override. The
Favorite Screen blocks from v1.2.3 all stand, since carrying a Connect
IQ field to another profile needs a record created from scratch — the
one case still unconfirmed on hardware.

Also added: a Connect IQ field placed in a shared/half-width row now
draws the same style of advisory the Graph/Bars fields do. The device
accepts it without complaint, but the apps tested need full width to be
readable. Advisory only, never a block.

Two deploy-flow clarity fixes ship alongside, neither touching a write
path. The pre-flight step is retitled **Pre-Flight Verification** and
now leads with its two real checks — a byte-level comparison against
the untouched staged copy, and a checksum check of the file about to be
written — with the change list following under "What will change on the
device". It previously read as a second review of what the Screens view
had already shown, which made the following click feel like a bare "are
you sure?" prompt. And the post-write verification box on the deploy
screen, which sat blank until the device reconnected with nothing
saying what it was for, now has a label and placeholder text.

Full investigation, decoded format, and the on-device confirmations are
in `PROJECT_NOTES.md` Doc rev 103-110. Prior rev (75, 2026-09-06)
follows.*

*Doc rev 75 — refreshed 2026-09-06.* **Connect IQ guard coverage fix
(v1.2.3) — the Favorite Screen path bypassed the v1.2.2 guard
entirely.** A read-only audit of every code path that writes to the
working file found that v1.2.2's guard, wired into `EditScreenPanel`'s
six write and entry points, never covered the Favorite Screen
pipeline: `AddScreenPanel.on_create()` reaches `patch_screen()` by a
different route with no Connect IQ check of any kind. Doug then
CONFIRMED the consequence on real hardware — saving a favorite from a
screen holding a Connect IQ data field and loading it into a new
screen does not carry the field over; it renders as "Timer" on the
device, exactly like every other way of introducing one.

Fixed at three points, defense in depth: capture is now refused
outright (`on_save_favorite`), so nothing bad enters the saved-favorite
store; anything loaded has Connect IQ ids stripped with a notice
(`on_load_favorite`) — this step is mandatory rather than redundant,
because the favorite lives in a single JSON file in the user's home
directory that survives upgrades, so favorites saved by earlier
versions are already on disk; and the write itself is refused
(`on_create`) as the real enforcement point. Every other writer was
audited and found clean: Show/Hide (field 12 only), screen reordering
(field 9 only), Remove (field 1 only), and Import (a byte copy that
rewrites no screen shape). On the CLI side `--seed-from-slot` copies
only fields 9 and 10 and never the field array, and `--new-slot` was
already covered by the existing request-side check.

Also corrected in this release: the toolkit table above had gone stale
at v1.2.2, still listing `fit_dump.py` 2.4.25, `fit_patch.py` 1.14.2
and `gui_app.py` 0.19.19. Now current. Full investigation in
`PROJECT_NOTES.md` Doc rev 101-102. Prior rev (74, 2026-09-03)
follows.*

*Doc rev 74 — refreshed 2026-09-03.* **Connect IQ data field guard,
real-hardware bug fix -- CONFIRMED bug, CONFIRMED fix.** Doug reported
a WindField (third-party Connect IQ) data field set via the GUI showing
correctly in the file and GUI but rendering as "Timer" on the actual
device; extensive real-hardware testing (his own, across two Connect IQ
apps -- one paid, one free) traced this to a device-local, install-
order-reassigned numeric field ID that nothing in the file carries
enough information to reproduce -- not a licensing check, since the
free app failed identically. Further testing (also Doug's own, the day
after the first fix shipped) found the first guard was too narrow: it
only blocked FRESHLY placing one of these fields, but editing OTHER,
ordinary fields on a screen that already had a working one broke it
just the same, and that write path (the GUI's Add/Remove Field, Move
Up/Down, Replace Field, Layout A/B) never went through the first
guard's code at all. Fixed properly this time with a second check
against the slot's CURRENT content, wired into every real write path in
both `fit_patch.py` and the GUI. Tagged `v1.2.2`. See
`PROJECT_NOTES.md` Doc rev 95-99 and `RELEASE_NOTES_v1.2.2.md` for the
full investigation and fix writeup. Prior rev (73, 2026-08-31)
follows.*

*Doc rev 73 — refreshed 2026-08-31.* **Setup section clarity fix,
Doug's question -- doc-only, no code changed.** Doug asked whether
`source .venv/bin/activate` is now handled by `install.sh` itself,
given `launch_gui.command`'s addition. It isn't, and can't be -- a
script running in its own subshell can't activate a venv in the
Terminal window that launched it, a shell limitation, not a gap;
`install.sh`'s own "Next steps" output already prints that line as
something the USER runs, not something it does silently, unchanged by
the launcher's addition. What HAD gone stale: showing `source
.venv/bin/activate` as step 2 of the primary Setup block implied it's
required for everyone, when the GUI path via `launch_gui.command`
doesn't need it at all anymore -- only direct CLI use does. Removed it
from the Setup block; added a short note to Quick start instead,
where the CLI commands actually need it. Prior rev (72, 2026-08-31)
follows.*

*Doc rev 72 — refreshed 2026-08-31.* **`launch_gui.command` CONFIRMED
on real hardware.** Doug ran `./install.sh` fresh, then double-clicked
`launch_gui.command` in Finder -- worked, closing out the one thing
Doc rev 71 flagged as unverifiable from the dev sandbox. Tagged
`v1.2.1`. See `PROJECT_NOTES.md` Doc rev 92. Prior rev (71, 2026-08-30)
follows.*

*Doc rev 71 — refreshed 2026-08-30.* **New macOS double-click launcher
(`launch_gui.command`), Doug's go-ahead -- closes the gap first noted
back at Doc rev 76's macOS Python Launcher/`.venv` mismatch story
(2026-08-22).** New file, `launch_gui.command` v1.0.0: resolves its own
folder, confirms `.venv` exists (points at `./install.sh` with a
paused, readable message if not), then launches `gui_app.py` directly
via `.venv/bin/python3` -- pauses on any error so Terminal's window
doesn't vanish before the message is readable, exits cleanly with no
pause on a normal close. `install.sh` is now v1.0.3 -- `chmod +x`'s the
launcher as a defensive last step (covers a download method that didn't
preserve the executable bit) and mentions it in its "Next steps"
output. Setup section rewritten to document it, including the one-time
Gatekeeper right-click-Open note every downloaded/unsigned macOS script
needs. Also corrected a stale line in the same section claiming Windows
"doesn't have [a setup script] yet" -- `install_windows.bat` has existed
and been confirmed on real hardware since Doc rev 54/62, this was
leftover wording from before it was built. See the Tools table above
for both files' full entries, and `PROJECT_NOTES.md` Doc rev 91 for the
fuller writeup. Headlessly verified (all three of the launcher's
branches -- missing venv, clean exit, non-zero exit -- via a simulated
`.venv/bin/python3` stand-in); real Finder/Gatekeeper behavior needs
Doug's own run. Prior rev (70, 2026-08-30) follows.*

*Doc rev 70 — refreshed 2026-08-30.* **"What it does" now explains WHY
Clone Profile matters, not just what it does -- doc-only, no code
changed.** Doug recalled a complaint from an Edge 530 review's comment
section around launch: creating a new profile on-device doesn't carry
over any of your other settings (navigation, alerts, sensor pairing,
etc.) from an existing one, so every new profile means redoing all of
that by hand. Clone Profile already solves this by construction, not
by design intent discovered after the fact --
`fit_clone_profile.py`'s `patch_profile_name()` duplicates the ENTIRE
input file and only overwrites the 32-byte name field, so every other
byte/setting rides along untouched, always has. The opening "What it
does" section now says so directly, since a new reader skimming that
section wouldn't otherwise know cloning preserves anything beyond the
screens. See `PROJECT_NOTES.md` Doc rev 90 for the fuller writeup.
Prior rev (69, 2026-08-29) follows.*

*Doc rev 69 — refreshed 2026-08-29.* **Confirmed on genuinely
32-bit-only hardware (Windows 10, Intel Atom N270 -- no 64-bit CPU
extensions at all), a donated bike-club laptop.** Full round trip --
`detect`, a real data-field edit on the GRAVEL profile, and deploy --
all confirmed working. This needed a different install path from
ordinary 32-bit Windows: wxPython dropped official 32-bit wheels as of
4.2.0, and the last version with one (4.1.1) only supports Python
3.6-3.9, so this specifically needs 32-bit **Python 3.9.13** (the last
3.9.x release with a binary installer -- python.org's normal download
flow no longer surfaces it, direct link in the Setup section above)
plus `pip install wxPython==4.1.1` (pinned, not latest).
`install_windows.bat` doesn't fit this case since it hard-checks for
Python 3.10+ -- install manually instead. One cosmetic-only bug found
along the way: on the very first Edit Screen visit each session, the
Layout A/B radio controls render blank until the panel is revisited
(Back and back in) -- looks like a native-control paint-timing quirk
specific to this old wxPython/old-graphics combination, not a logic
bug (the same code runs correctly every subsequent visit), and not
chased further since there's no way to test a fix without this exact
hardware. See `PROJECT_NOTES.md` Doc rev 88 for the full writeup.
Prior rev (68, 2026-08-25) follows.*

*Doc rev 68 — refreshed 2026-08-25.* **Project rename finished --
"Publishing housekeeping cleanup" closed.** The GUI window title has
read "Activity Profile Screen Editor for Garmin Edge" since v0.16.7,
but the rename never went further -- README.md's/PROJECT_NOTES.md's
own top-level headings still led with "Garmin Edge 530," exactly the
pattern the original rename was meant to avoid (implying this might be
a Garmin product), and `gui_app.py`'s module docstring, About dialog
text, `MVP_SCOPE.md`'s heading, and `FIT_PATCH.md`'s banner all carried
one of three different inconsistent names. Doug clarified the
canonical name: **"Activity Profile Editor for Garmin Edge"** -- no
"Screen," no "530" -- matching his GitHub repo name
("Activity-Profile-Editor") and his own Release titles ("Activity
Profile Editor for Garmin Edge Devices"). Rationale, his own words:
the editor works with any Edge device, not just the 530 specifically
(even though the confirmed field-ID/screen-type data so far is 530-only),
and "Activity Profile" is the right noun to lead with over "Screen"
since backups, restores, and deploys all operate at the whole-profile
level, not the individual-screen level. Updated: this file's own H1,
`PROJECT_NOTES.md`'s H1, `MVP_SCOPE.md`'s H1, `FIT_PATCH.md`'s man-page
banner, and `gui_app.py`'s window title/module docstring/About dialog
text (now v0.19.20) -- see that file's own changelog entry for the
full list. Also closes the other half of "Publishing housekeeping
cleanup": `README_DISCLAIMER_DRAFT.md`, superseded back on 2026-08-11
when its content was merged into this file's License/Disclaimer
section, was found to already be deleted -- nothing left to do there.
Deliberately LEFT UNCHANGED: `MEMORY_LOG.md` (an explicitly archived,
dated historical record) and `RELEASE_NOTES_v1.1.0.md`/
`RELEASE_NOTES_v1.1.1.md` (already published as GitHub Releases under
Doug's own chosen title) -- both are point-in-time snapshots, not live
docs, same reasoning this project already applies to never rewriting
old changelog/Doc-rev entries.

*Doc rev 67 — refreshed 2026-08-25.* **New feature, Doug's go-ahead:
backup retention/pruning.** `garmin_device.py` is now v0.12.8,
`gui_app.py` is now v0.19.19. Backups have accumulated with nothing to
clean them up since v0.11.0 -- an Open Item deliberately deferred out
of MVP, since Doug's own real usage numbers (~1098 backed-up `.fit`
files, ~4-5GB, over this project's entire prior history) confirmed disk
space was never the actual problem. Design chosen from three options
put to Doug: time-based folder deletion (delete entire
`backups/<timestamp>/` folders older than a chosen day count) -- won
out over keep-latest-N-per-profile (rejected: each timestamped folder
snapshots every profile together, not one folder per profile, so
per-profile retention would mean deleting individual files out of a
shared folder rather than whole folders) and keep-only-the-latest
(rejected: cuts against Restore-from-Backup's whole reason for
existing, and wasn't justified by the disk numbers). Manual-only, not
automatic -- no silent pruning on launch, matching every other
destructive action in this app. New CLI `prune-backups` subcommand and
GUI "Clean Up Old Backups..." dialog (live preview of exactly what
would be deleted before an explicit confirm) -- see both files'
toolkit-table entries above for the full writeup. Headlessly verified,
and CONFIRMED via Doug's own real hardware test (2026-08-25) -- worked
as designed.

*Doc rev 66 — refreshed 2026-08-24.* **Two more real bugs found via
Doug's hardware testing of Import, same session as Doc rev 65's
deploy-path fix.** `gui_app.py` is now v0.19.18. (1) Window width: the
app window expanded to near-screen-width by the time Doug reached
Deploy. Root cause -- `ViewScreensPanel`'s title and `DeployPanel`'s
status text both embed dynamic paths/filenames in a plain, unwrapped
`wx.StaticText`, and the window's `_relayout()` only ever grows, never
shrinks, so a long value on the Screens page carries forward even
though the text visibly on screen at Deploy looked short enough to
Doug. Fixed with this codebase's established `textwrap.fill()`
hard-wrap pattern. (2) The actual long value, confirmed on real
hardware: `ImportPanel` suggested `os.path.basename(source)` verbatim
as the default filename -- Doug picked an old file already sitting in
his own `working_dir/staging/` folder (one of this toolkit's own
artifacts, not a genuinely external profile) as the Import source, and
its basename carried every layer of this toolkit's own internal
`_staged_<timestamp>`/`_clone_<timestamp>` naming, chained across
repeat passes, into the suggestion: a 92-character filename
(`CyclingRoadTClone_clone_20260823_124234_staged_20260824_182004_staged_20260824_182104.fit`).
Deployed to `NewFiles/`, Doug confirmed it sat there unconsumed even
after a full power cycle -- the device silently declined to import it.
Fixed by stripping this toolkit's own internal suffixes from the
suggested default (the field stays free-text editable either way). The
device's real filename-length tolerance is still unconfirmed -- logged
as an open question in `PROJECT_NOTES.md`, not guessed at with an
invented hard limit.

*Doc rev 65 — refreshed 2026-08-24.* **Real bug fix, Doug's report from
actually using Import External Profile right after it shipped: no way
to reach Deploy for a freshly imported profile.** `gui_app.py` is now
v0.19.17. The Screens review page for an import showed Back/Re-read
File/+ Add New Screen but no "Review & Deploy...", and going Back lost
the staged import silently. Root cause: importing left `editing_path`
at `None`, correct for the normal Stage-for-Edit flow (the staged file
already matches the device — nothing to deploy until an edit happens)
but wrong for Import, where the staged file is content the device has
never had at all. Fix creates the scratch working copy immediately on
import and adds a `frame.import_pending` flag so `PreflightPanel`
treats a byte-identical, zero-edit import as valid to deploy instead of
"nothing to deploy," and so the Back-button warning fires (with
import-accurate wording) instead of staying silent. Discarding edits
after an import no longer re-strands the session either — it re-copies
from the staged file instead of nulling `editing_path` outright.
Headlessly verified via a standalone simulation of the import/discard/
deploy-gating logic; real GUI behavior needs Doug's own run.

*Doc rev 64 — refreshed 2026-08-24.* **Real bug fix, Doug's report from
using Favorite Screen right after it shipped: "Save as Favorite" had
no warning before overwriting an existing favorite.** `gui_app.py` is
now v0.19.16 — saving a new favorite when one's already saved now
shows a confirm naming what's currently there (field count, source
profile) before it's replaced; canceling costs nothing. Still a single
favorite slot by design, not a list — Doug's own note for later, not
acted on now: if this feature turns out to be popular, a
`GarminBackups`-style `favorites/` folder (alongside the existing
`staging/`/`backups/`) could hold multiple named favorites, useful for
sports/disciplines that share similar screen needs across several
profiles. Logged as a future idea in PROJECT_NOTES.md, not scoped.

*Doc rev 63 — refreshed 2026-08-24.* **Three backlog items built in one
batch, Doug's go-ahead: a real safety fix, Favorite Screen, and Import
an external profile.** (1) `garmin_device.py` v0.12.7 — `deploy`
(CLI and GUI) now auto-backs-up whatever profile currently exists
under the target filename before overwriting it, closing a real gap
where a bare CLI `deploy` call had no safety net at all (every
GUI-driven write already got this indirectly). (2) `gui_app.py`
v0.19.14 — Favorite Screen, a single save/load slot for a screen's
field set + layout, reusable across profiles; "Save as Favorite" on
the Screens view, "Load from Favorite..." on Add New Screen.
(3) `gui_app.py` v0.19.15 — Import an external profile: a new "Import
Profile..." button opens a file picker for a `.fit` never backed up by
this toolkit, validates the target filename, and stages it for the
normal Screens review before any deploy. All three headlessly
verified (safety-fix backup/no-op/skip cases, favorite save/load
round-trip and overwrite semantics, filename-collision rules) —
real on-device GUI testing is still pending Doug's own run, same as
every GUI feature in this project. See PROJECT_NOTES.md for the full
scoping history behind each of these (all three were previously
design-locked Open Items, not new ideas built on the fly).

*Doc rev 62 — refreshed 2026-08-22.* **`install_windows.bat` CONFIRMED
on real Windows 11 hardware — the toolkit's own testing checklist
before v1.1.1.** Doug uninstalled `garmin-fit-sdk`/`wxPython` via pip,
confirmed both failed to import, then ran the script fresh: detection,
version check, install, and post-install import verification all
worked cleanly (Python 3.14). Double-click launch of `gui_app.py`
reconfirmed too, including a normal one-time Windows file-association
dialog on the very first double-click (unrelated to this script,
harmless, doesn't recur). Also confirmed: the 169-entry `FIELD_ID_NAMES`
field picker shows correct on-device labels for the three 2026-08-20
batches, spot-checked directly in the GUI. `install_windows.bat` is
now v1.0.1, `fit_dump.py` is now v2.4.25 — both confirmation-only
entries, no code changed either place. This closes out the real-world
testing Doug wanted done before tagging v1.1.1.

*Doc rev 61 — refreshed 2026-08-21.* **README restructured, Doug's
request:** the document now opens with a new "What it does" section
(covering both the GUI and CLI in one place) leading straight into
"Who this is for" (moved up from further down, unchanged text) —
readers get the pitch and the experience-level expectation before
anything else. "License" and "Disclaimer" follow, then "Setup",
"Quick start", "Tools", "GUI", and the pre-write warning, in that same
order as before. The entire 46-entry "Doc rev" changelog block (this
one included) moved from the top of the document to a new
"## Changelog" section at the very end — same content, unchanged,
just relocated so a first-time reader hits the toolkit's own
explanation before 60+ revisions of edit history. No content removed.

*Doc rev 60 — refreshed 2026-08-20. **13 new confirmed field IDs —
Doug's cross-check against the Garmin manual's own data-field
appendix.** 98 Watts/kg, 439 3s W/kg, 207-213 Power Z1-Z7, 418 Power
Z8, 419 Power Z9, 24 Laps, 41 Max Lap Power — `fit_dump.py`'s
`FIELD_ID_NAMES` now has 169 confirmed entries (was 156). Fills the
last two gaps in the W/kg family (base + 3s variant) and adds the
Power-Zone analog of the existing 5 HR-Zone-time fields (9 zones
here, not 5). 24/41 resolve an earlier same-day ambiguous "Laps Max"
note — turned out to be two separate fields Doug had conflated in his
own notes, not one oddly-named field. No collisions with any existing
entry. This closes out Doug's manual-appendix cross-check — no
further appendix-listed fields remain unconfirmed. One real gap still
open, not part of this batch: "Trainer Resistance," hypothesized
(unverified) to need a paired ANT+ FE-C smart trainer to even appear
on-device, the same sensor-gated pattern already seen for eBike
Metrics fields. See `FIT_PATCH.md` Doc rev 31 for the regenerated
field ID table. No code changed beyond the new dict entries and a
stale docstring count in `gui_app.py`. Prior rev (59, 2026-08-20)
follows.*

*Doc rev 59 — refreshed 2026-08-20. **10 new confirmed field IDs.**
Doug's continued field census: 265 Lap PCO, 267 Avg Right PP, 268 Lap
Right PP, 269 Right PPP, 271 Lap Right PPP, 273 Avg Left PP, 274 Lap
Left PP, 275 Left PPP, 277 Lap Left PPP, 440 10s W/kg —
`fit_dump.py`'s `FIELD_ID_NAMES` now has 156 confirmed entries (was
146). Fills out the L/R Power Phase/Peak Power Phase family alongside
the existing 263/264/266/270/272/276 entries — Doug supplied both the
on-device display label (stored, per this dict's established
convention) and each field's full concept name for the record (e.g.
"Avg Right PP" = "Avg Right Pwr Phase"). No collisions with any
existing entry. Same batch, doc-only: Doug's investigation of the
last unmapped on-device label he'd been tracking, "Battery Status"
(Lights category), confirms it's an alias/duplicate menu entry that
navigates straight to field 317 "Light Battery" — not a separate
field, no table entry added or needed. See `FIT_PATCH.md` Doc rev 30
for the regenerated field ID table. No code changed beyond the new
dict entries and a stale docstring count in `gui_app.py`. Prior rev
(58, 2026-08-20) follows.*

*Doc rev 58 — refreshed 2026-08-20. **Correction, same day: "Target"
is field 521, not 512 — Doug's own catch.** A transcription typo in
the Doc rev 56 batch writeup, not a raw-ID/name mismatch — 512 never
existed on-device under either name. Fixed before this ever shipped
in a tagged release. Doug also confirmed, unprompted, that all 9
fields from that batch are verified against the real on-device
screen — same confirmation standard as every other batch in
`fit_dump.py`'s `FIELD_ID_NAMES`, not just a naming guess for the 5
that read as Workout-related. `fit_dump.py` now v2.4.22 (was 146
entries, still 146 — a corrected key, not a new/removed one).
`FIT_PATCH.md`'s FIELD ID REFERENCE table and NOTE updated to match
(Doc rev 29). Prior rev (57, 2026-08-20) follows.*

*Doc rev 57 — refreshed 2026-08-20. **New `install_windows.bat` setup
script, Doug's go-ahead.** Prompted by real feedback — a rider who
wanted to try the toolkit found the install burden more than he
wanted to take on — plus Doug's own confirmation that double-clicking
`gui_app.py` in File Explorer already works once Python/dependencies
are in place. Scoped directly against Doug's own confirmed real
Windows 11 install (Doc rev 54 below): checks for Python 3.10+ (`py`
launcher, falling back to `python.exe`), installs `garmin-fit-sdk`/
`wxPython` directly with no virtual environment (a venv would break
that double-click behavior), verifies both import, `--upgrade`/
`--help`/`--version` flags. If Python's missing or too old, it detects
and guides (opens the python.org download page, stops) rather than
silently downloading/installing Python itself — Doug's explicit
call, matching `install.sh`'s own treatment of missing Xcode CLT on
macOS. One real platform-specific deviation from `install.sh`: the
3.10 floor is a HARD requirement here, not a soft warn-and-continue,
since building `wxPython` from source below that needs Visual Studio
Build Tools on Windows (a much bigger ask than macOS's one-command
Xcode CLT). **Not yet confirmed on real hardware** — there's no
`cmd.exe` in this project's dev sandbox to dry-run Windows batch
syntax against at all, so this is less tested going in than any other
single-platform code in this toolkit; Doug plans to uninstall and
re-test via this script on the Windows laptop before the next
release. Windows Setup section above now leads with the script,
keeping the manual sequence as a documented fallback. See the new
`install_windows.bat` toolkit table row below for the full writeup.
Prior rev (56, 2026-08-20) follows.*

*Doc rev 56 — refreshed 2026-08-20. **9 new confirmed field IDs.**
Doug's continued field census: 512 Target, 523 Step Time, 522
Duration, 511 Workout Comparison, 45 Workout Step, 100 Last Lap
Power, 258 Lap Time Standing, 260 Lap Time Seated, 264 Avg PCO —
`fit_dump.py`'s `FIELD_ID_NAMES` now has 146 confirmed entries (was
137). No collisions with any existing entry. Worth flagging: 5 of
these 9 (45, 511, 512, 522, 523) read by name as Workout/structured-
step fields (Workout Step, Workout Comparison, Target, Duration, Step
Time) — directly adjacent to this project's still-open f10=38
"Workout" screen-type question (see `PROJECT_NOTES.md` Open Items):
whether that screen's field slots are actually meaningful/rendered
on-device, since the on-device editor exposes no field options for it
at all. A naming lead worth watching, not new evidence either way — a
field's name alone doesn't confirm where or how it renders. The other
4 extend already-populated families (Power; Cycling Dynamics). See
`FIT_PATCH.md` Doc rev 28 for the regenerated field ID table. No code
changed beyond the new dict entries and a stale docstring count in
`gui_app.py`. Prior rev (55, 2026-08-19) follows.*

*Doc rev 55 — refreshed 2026-08-19. **New hard block: Clone Profile's
display name is now capped at 15 characters.** Doug found a note that
Garmin limits Activity Profile display names to 15 characters, and
confirmed it directly on his own device: typing a 16th character in
Garmin's own name editor does nothing — it just switches straight to
the checkmark/complete control instead of accepting more input. Since
that's a confirmed device fact, not a guess, `gui_app.py`'s Clone
Profile panel now hard-blocks Create Clone past 15 characters (new
`fit_clone_profile.py` v1.0.1 constant `PROFILE_NAME_MAX_CHARS`), the
same way Map/ClimbPro's hide-toggle guard is a hard block rather than
a warning. Also confirmed (no change needed): the "New filename" field
already enforced the required `.fit` suffix and a case-insensitive
collision check against every profile on the device. Prior rev (54,
2026-08-19) follows.*

*Doc rev 54 — refreshed 2026-08-19. **Correction: the Windows Setup
section had the wrong install steps.** Doug corrected this directly
after re-reading it: the venv-based sequence written there was never
actually what he ran on the Windows 11 laptop — that was an
unconfirmed inference on this project's part (mirroring the macOS
pattern), not something Doug had verified. What he actually did: install
Python from python.org via browser, `python -m pip install
garmin-fit-sdk wxPython` directly (no venv at all), copy the whole
toolkit folder to a `Documents` subfolder, then run from PowerShell —
plus a genuinely nice discovery, double-clicking `gui_app.py` in File
Explorer launches the GUI directly with no wrapper script needed,
because the python.org installer associates `.py` files with the same
Python `pip` installed into, unlike macOS's Python Launcher pointing
at a different `python3` than the one with `wx` (see `gui_app.py`'s
own ModuleNotFoundError episode this same week for that contrast). The
Windows section now leads with this confirmed no-venv path, keeps a
venv as an explicitly optional alternative (with a note that
double-click launch won't use it), and no longer misattributes a
theoretical sequence to Doug's real test. No code changed — README.md
only. Prior rev (53, 2026-08-19) follows.*

*Doc rev 53 — refreshed 2026-08-19. **Real bug fix: stale "hide is
untested" warning removed for named Garmin screens.** Doug's report:
unchecking "Show Screen" for Lap Summary, Cycling Dynamics, Elevation,
and others he'd tested popped a dialog claiming hiding it via a raw
file write was "genuinely UNTESTED" — even though he'd already
confirmed it worked, repeatedly. Root cause: that soft confirm ran for
ANY named-type match, downstream of two HARD blocks (Map/ClimbPro,
last-visible-user-screen) that already run first — and since
`NO_SHOW_TOGGLE_TYPES` (Map, ClimbPro) was derived as an *exhaustive*
list via direct on-device inspection, anything reaching the soft
confirm is, by elimination, a type with a working toggle. The
"untested" claim was stale the moment real testing caught up with
that logic. Removed entirely (not just reworded) after Doug confirmed
he's now tested hiding every named type that has an on-device Show
Screen checkbox — `gui_app.py` now v0.19.8. Hiding a named screen now
behaves exactly like hiding a plain user screen, no popup. The
separate guard on *editing a named screen's fields* is untouched — a
genuinely different, still-cautious case. See `PROJECT_NOTES.md` for
the full writeup. Prior rev (52, 2026-08-19) follows.*

*Doc rev 52 — refreshed 2026-08-19. **Real bug fix: "View Screens"
could silently open the wrong profile.** Doug's report from actually
editing one of his main profiles: stage Profile A, then click a
different profile (B) in the list — "View Screens" stayed enabled and
advancing to Edit Screens showed A, not the one now highlighted.
Root cause: staging and navigation were two separate buttons/clicks,
and selecting a different profile never reset the first one's state.
Fixed by merging them — "View Screens →" now stages the profile
that's actually selected immediately before navigating, on every
click, so there's no second piece of state left to go stale. Doug
chose this over two smaller alternatives (disabling the button on
reselect, or warning before opening a stale selection) once it was
clear staging itself is just a local file copy with no device
involved — free to redo every time. `gui_app.py` now v0.19.7. See
`PROJECT_NOTES.md` for the full writeup. Prior rev (51, 2026-08-19)
follows.*

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

