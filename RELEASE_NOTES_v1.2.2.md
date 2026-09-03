# Activity Profile Editor for Garmin Edge — changes since v1.2.1

Covers everything since the `v1.2.1` tag (2026-08-31). Suggested tag
for this update: **v1.2.2** — a real-hardware bug fix around Connect IQ
third-party data fields, no new features, no breaking changes.

## Bug fixes

- **Connect IQ data fields (e.g. WindField) could be silently broken by
  this toolkit.** Real-hardware investigation found that Connect IQ
  third-party data fields get a numeric field ID that's assigned by the
  device itself, not the app — and that ID gets reused for a
  *different* app if you install another one later. Nothing in the
  file carries enough information to recreate this link, so any attempt
  by this toolkit to place one of these fields into a screen wrote a
  file that looked correct (right ID, right name, right position in the
  GUI and in `fit_dump.py`'s own output) but rendered as **"Timer"** on
  the actual device — Garmin's generic fallback for an unresolved
  Connect IQ reference.
- Further testing narrowed this down further: it isn't just placing one
  fresh that breaks it. **Editing a screen that already has a working
  Connect IQ field on it — adding, removing, or reordering *other*,
  ordinary fields around it — breaks that field too**, even though its
  own ID and position never change. Screen *display order* (moving the
  whole screen earlier/later in the on-device carousel) is unaffected —
  only that screen's own field count, field list, or layout is fragile.
- **Fixed with a hard guard, no override.** Both `fit_patch.py`
  (`--fields`, `--swap-fields`, `--layout`) and the GUI (Add/Remove
  Field, Move Up/Down, Replace Field, Layout A/B) now refuse outright —
  before writing anything — the moment a target screen already has one
  of these fields on it, or the moment you try to place one fresh.
  `fit_dump.py` and the GUI's read-only views are unaffected — an
  already-configured Connect IQ field still displays correctly, now
  under a generic **"CIQ Data Field"** label instead of a specific app
  name that isn't actually reliable (the same field ID meant a
  different, unrelated app after a device-local reassignment during
  testing).
- This isn't a licensing check — confirmed with both a paid,
  currently-licensed Connect IQ app and a completely free one showing
  the identical failure mode. It's how Garmin links a screen slot to
  whichever Connect IQ app the device currently has installed in that
  slot, independent of any file this toolkit can write.
- **What still works:** cloning a whole profile that already has a
  working Connect IQ field preserves it untouched. Only Garmin's own
  on-device editor can place one fresh or restructure a screen that
  already has one.

Full investigation, including the real-hardware evidence behind each
claim above, is in `PROJECT_NOTES.md` Doc rev 95–99.

## Version bumps

- `fit_dump.py` 2.4.25 → 2.5.0
- `fit_patch.py` 1.14.2 → 1.15.0
- `gui_app.py` 0.19.20 → 0.20.0
