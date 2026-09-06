# Activity Profile Editor for Garmin Edge — changes since v1.2.2

Covers everything since the `v1.2.2` tag (2026-09-03). Suggested tag
for this update: **v1.2.3** — a coverage fix to v1.2.2's own Connect IQ
guard, no new features, no breaking changes.

## Bug fixes

- **The Connect IQ guard shipped in v1.2.2 had a gap: the Favorite
  Screen path went around it entirely.** v1.2.2 wired its guard into
  the six write and entry points on the Edit Screen panel, and that was
  verified by confirming those six existed. That check proves the guard
  is present where it was installed; it can't prove there isn't a
  seventh writer that never got one. A read-only audit of every code
  path that writes to the working file found exactly that: creating a
  new screen reaches the file by a different route with no Connect IQ
  check of any kind.
- **Confirmed on real hardware.** Saving a favorite from a screen that
  holds a Connect IQ data field, then loading that favorite into a new
  screen, does not carry the field over — it renders as **"Timer"** on
  the device, the same failure mode as every other way of introducing
  one. This produced a file that looked correct everywhere: in
  `fit_dump.py`'s output, in the GUI, and on disk.
- **Fixed at three points.** Saving a favorite from a Connect IQ screen
  is now refused outright, so the problem never enters the saved-favorite
  store. Anything loaded from a favorite has Connect IQ ids stripped,
  with a notice saying what was dropped — this step is not redundant
  with the first, because the favorite is a single JSON file in your
  home directory that survives toolkit upgrades, so a favorite saved by
  an earlier version is already on disk. And creating the screen is
  refused as the real enforcement point.
- A favorite that contained *nothing but* Connect IQ fields now leaves
  your current field list alone rather than loading an empty one. When
  fields are dropped, the layout A/B choice is re-validated against the
  reduced field count.

## Audited and found clean

Recorded so the same ground doesn't get re-covered later. Every other
writer was checked and needs no change: Show/Hide (writes field 12
only), screen reordering (field 9 only, already confirmed safe on
hardware), Remove (field 1 only), and Import (a byte-for-byte copy that
rewrites no screen shape at all, same as Clone). On the command-line
side, `--seed-from-slot` copies only fields 9 and 10 and never the
field array, and `--new-slot` was already covered by the existing
request-side check. The command-line tools have no known gap; this was
GUI-only.

## Also in this release

- The toolkit table in `README.md` had gone stale at v1.2.2, still
  listing `fit_dump.py` 2.4.25, `fit_patch.py` 1.14.2 and `gui_app.py`
  0.19.19. Corrected to the current versions.

## Version bumps

- `gui_app.py` 0.20.0 → 0.20.1

`fit_dump.py` (2.5.0) and `fit_patch.py` (1.15.0) are unchanged since
v1.2.2 — this fix was entirely in the GUI, which is where the gap was.
