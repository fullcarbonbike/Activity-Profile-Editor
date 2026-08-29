# Activity Profile Editor for Garmin Edge — changes since v1.1.1

Covers everything since the `v1.1.1` tag (2026-08-24). Suggested tag
for this update: **v1.2.0** — two new features (Import, backup
retention) plus several real-hardware-found bug fixes and a
project-wide rename justify a minor version bump, not just a patch.

## New features

- **Import an external profile** — a new file-picker entry point for a
  `.fit` profile this toolkit never backed up itself (e.g. one shared
  by another user, or restored from outside the toolkit). It lands in
  staging for the normal Screens review before any deploy, exactly like
  every other edit path.
- **Favorite Screen** — save a screen's full configuration and reuse it
  from any profile via "Load from Favorite..." on the Add New Screen
  panel, instead of rebuilding the same screen by hand each time. A
  single save slot; saving a new favorite over an existing one now
  prompts for confirmation first (see Bug fixes).
- **Backup retention/pruning** — a new "Clean Up Old Backups..." button
  (next to "Change...") previews and deletes entire `backups/<timestamp>/`
  folders older than a chosen day count (30 by default), with the same
  explicit-confirm posture as every other destructive action in this
  app. Also available from the CLI: `garmin_device.py prune-backups`.
  Manual only — nothing is pruned automatically. Confirmed on real
  hardware.

## Bug fixes

- **Deploy safety net** — a bare CLI `deploy` call used to have zero
  backup protection, unlike every GUI-driven write. `deploy --working-dir
  DIR` (and every GUI write path, which already passes this) now backs
  up whatever profile currently exists under the target filename before
  overwriting it.
- **Import: fixed a stuck fresh import** — a profile brought in via
  Import had no way to reach Deploy (no "Review & Deploy..." button
  reachable), and backing out silently lost the import with no warning.
  Both fixed; an imported-but-undeployed profile is now treated the
  same as any other pending edit.
- **Import: cleaner suggested filenames** — importing a file that was
  previously staged or cloned by this toolkit itself no longer carries
  every layer of its own internal `_staged_<timestamp>`/`_clone_<timestamp>`
  naming into the suggested "Deploy as" filename.
- **Favorite Screen: overwrite confirmation** — "Save as Favorite" now
  warns and asks for confirmation before replacing an already-saved
  favorite, instead of silently overwriting it.
- **Window-width fix** — a long file path or filename on the Screens
  review or Deploy page used to force the GUI window nearly
  screen-width, and it stayed that way for the rest of the session.
  Long values now wrap instead.

## Documentation

- **Project renamed consistently everywhere** — the canonical public
  name is now **"Activity Profile Editor for Garmin Edge"** (no
  "Screen," no "530"), matching the GitHub repo name
  (`Activity-Profile-Editor`) and this project's own Release titles.
  Updated: this document's title, `README.md`, `PROJECT_NOTES.md`,
  `MVP_SCOPE.md`, `FIT_PATCH.md`'s banner, and `gui_app.py`'s window
  title, module docstring, and About dialog text. No behavior changes —
  text only.
