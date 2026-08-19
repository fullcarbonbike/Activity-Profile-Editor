# Activity Profile Screen Editor for Garmin Edge — changes since v1.0.1

Covers everything since the `v1.0.1` tag (2026-08-13). Suggested tag
for this update: **v1.1.0** — new platform support and several new
features justify a minor version bump, not just a patch.

## Windows support (new)

- Device detection, backup, staging, write/deploy, and eject are all
  now implemented and **confirmed working on real Windows 11 hardware**
  against a real Edge 530 — CLI tools and the full GUI workflow both
  tested end to end, including a real screen-add/deploy/restart round
  trip.
- macOS remains fully supported and unchanged. Linux is untested.
- Setup differs by platform for now: macOS has a one-command
  `./install.sh`; Windows setup is a couple of `pip install` commands
  run by hand (no installer script yet). See the README's Setup
  section for the exact steps.

## New features

- **Delete Screen** — permanently remove a screen from a profile
  (CLI `--remove`, GUI "Remove Selected Screen"), confirmed via a real
  on-device round trip. Replaces the old `--un-remove` flag, which has
  been retired — Restore-from-Backup already covers real recovery from
  a mistake, with no historical data-loss risk.
- **Restore a Deleted Profile** — a profile no longer on the device
  can now be found in backup history and restored (GUI), confirmed
  that `NewFiles` correctly recreates a deleted profile, not just
  replaces an existing one.
- **View/edit the device's custom boot message** (`startup.txt`) —
  new CLI `startup-txt` subcommand and a GUI "Startup Message" panel.
- **20 new confirmed data fields**, mostly power-meter and Shimano
  Di2 metrics: Balance family (Balance, Avg/Lap/3s/10s/30s Balance),
  Power/W-kg variants, TSS, Intensity Factor, Normalized Power,
  Torque Effectiveness, Pedal Smoothness, Power Zone, Di2 Battery,
  and Di2 Shift Mode.
- **3 newly-identified screen types**: Workout, eBike Metrics, and
  STEPS Metrics (Shimano).
- **Graph/Bars full-width warning** — the GUI now flags fields (HR
  Zone Graph, Speed/Cadence/Power Bars, etc.) that silently render as
  plain text unless placed in a full-width screen slot.
- Reduced redundant profile backups — the GUI no longer re-backs-up
  every profile on every ordinary visit, only on a genuine device
  reconnect or after a real deploy.

## Bug fixes

- Fixed two separate, unrelated causes of stray "?" characters
  appearing in `startup.txt`: macOS's smart-quote/dash
  auto-substitution while typing, and a UTF-8 byte-order-mark left in
  the file's preserved header comment.
- Found and corrected a field-ID mismatch from a census mix-up
  (two screens' field lists had gotten transposed when written up) —
  independently re-verified byte-for-byte against the original device
  data before trusting the fix.
- Fixed the Startup Message editor showing far fewer visible lines on
  Windows than macOS for the identical file (a font-metrics/DPI
  difference between platforms, not a data problem).
- Several GUI window-sizing bugs fixed during testing — a window that
  could grow off-screen or a field list that silently truncated
  instead of scrolling, both triggered by unusually long field names.
- `install.sh`: fixed a crash on a fresh Mac with no Xcode Command
  Line Tools installed, and a `bash` 3.2 compatibility bug (macOS's
  stock shell) that broke dependency installation partway through.

## Documentation

- README restructured with a clear "Who this is for" section and
  separate macOS/Windows setup instructions.
- Full internal changelog and design-decision history maintained in
  `PROJECT_NOTES.md` for anyone who wants the "why," not just the
  "what."
