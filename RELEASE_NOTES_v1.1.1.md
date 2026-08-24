# Activity Profile Screen Editor for Garmin Edge — changes since v1.1.0

Covers everything since the `v1.1.0` tag (2026-08-19). Suggested tag
for this update: **v1.1.1** — a Windows setup script plus data/bug-fix
additions, no breaking changes.

## Windows setup script (new)

- **`install_windows.bat`** — one-command setup for Windows, mirroring
  `install.sh` on macOS. Checks for Python 3.10+ (the `py` launcher,
  falling back to `python.exe`), installs `garmin-fit-sdk` and
  `wxPython` directly (deliberately no virtual environment, so the
  double-click-`gui_app.py`-in-File-Explorer workflow keeps working),
  and verifies both packages import cleanly. If Python is missing or
  too old, it detects and guides to the python.org installer rather
  than installing anything silently.
- **Confirmed on real Windows 11 hardware** — a full uninstall/
  reinstall cycle, dependency install, import verification, and
  double-click launch of `gui_app.py` all tested end to end.

## New data fields

- **32 new confirmed field IDs** (`FIELD_ID_NAMES` grew from 137 to
  169), closing out a full cross-check against the Garmin Edge 530
  Owner's Manual's own data-field appendix — no further appendix-listed
  fields remain unconfirmed.
- Notable additions: Target, Duration, Step Time, Workout Comparison,
  Workout Step (structured-workout fields), Last Lap Power, Lap Time
  Standing/Seated, the full Left/Right Power Phase and Peak Power
  Phase family, Avg/Lap PCO, 10s and 3s Watts/kg, Watts/kg, Power Zone
  1–9 (time-in-zone), Laps, and Max Lap Power.
- One remaining gap, not part of this batch: "Trainer Resistance" —
  hypothesized to need a paired ANT+ FE-C smart trainer to appear in
  the on-device picker at all, same sensor-gated pattern already
  confirmed for eBike Metrics fields.

## New features

- **Clone Profile name limit** — the "New display name" field now
  hard-blocks past 15 characters, matching a real limit confirmed on
  Garmin's own on-device Activity Profile name editor (previously only
  the much looser 31-byte storage cap was enforced).

## Bug fixes

- **Stage/View Screens button merge** — selecting a different profile
  after staging one no longer leaves View Screens pointing at the
  stale, previously-staged profile; the two separate clicks are now
  one.
- Removed a stale "genuinely untested" warning shown when hiding a
  named screen type (Lap Summary, Cycling Dynamics, Elevation) — every
  such type has since been confirmed working on-device, so hiding one
  now behaves exactly like hiding a plain user screen.

## Documentation

- **README restructured** — now opens with a short "What it does"
  section (covering both the GUI and CLI) leading straight into "Who
  this is for," so a new reader gets the pitch and the experience-level
  expectation before Setup. The full doc-revision changelog (46+
  entries) moved from the front of the document to a "Changelog"
  section at the end.
