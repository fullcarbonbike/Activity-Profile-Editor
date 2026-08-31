# Activity Profile Editor for Garmin Edge — changes since v1.2.0

Covers everything since the `v1.2.0` tag (2026-08-29). Suggested tag
for this update: **v1.2.1** — one new convenience file plus its setup-
script/doc support, no functional changes to the toolkit itself.

## New

- **`launch_gui.command`** — a double-clickable launcher so macOS users
  can start the GUI directly from Finder after running `install.sh`
  once, no Terminal needed from then on. This is the macOS equivalent
  of Windows' native double-click-`gui_app.py` convenience — macOS has
  no matching file association to hijack, so a small launcher script is
  the actual fix here, not a workaround. It resolves its own folder,
  confirms `.venv` exists (points at `./install.sh` with a readable,
  paused message if not), then launches `gui_app.py` via that exact
  venv's Python. On error it pauses so the Terminal window doesn't
  close before the message can be read; on a normal clean exit it just
  closes. **Confirmed on real hardware** — installed fresh via
  `./install.sh`, then launched via a real Finder double-click.
- `install.sh` (now v1.0.3) makes the launcher executable as a
  defensive last step on every run, in case a download method (a zip
  rather than a `git clone`) didn't preserve the bit, and its "Next
  steps" output now mentions the launcher as the no-Terminal
  alternative.

## Documentation

- README's Setup section now documents the launcher, including the
  one-time Gatekeeper "unidentified developer" prompt every downloaded/
  unsigned macOS script triggers on its first launch (right-click >
  Open once; every launch after that works normally).
- Corrected a stale line claiming Windows didn't have a setup script
  yet — leftover text from before `install_windows.bat` existed.
