# Activity Profile Editor for Garmin Edge — changes since v1.2.3

Covers everything since the `v1.2.3` tag (2026-09-06). Suggested tag
for this update: **v1.3.0** — a real new capability around Connect IQ
data fields. No breaking changes.

## The headline

**Connect IQ data fields can now be moved, rearranged around, and
removed.** Since v1.2.2 this toolkit refused any edit to a screen
holding a Connect IQ field, because such edits reliably broke the field
on the device — it would come back as **"Timer"**. That refusal was the
right response to the evidence, but the cause turned out to be
something the toolkit wasn't doing rather than something it couldn't.

Activity Profile files contain an undocumented FIT message (170) that
Garmin's published FIT Profile omits entirely. It holds one record per
Connect IQ app used by the profile: the app's UUID, plus a packed list
of exactly which screen slot and field position that app occupies. The
device renders a Connect IQ field **only** where a record claims that
exact position, and falls back to "Timer" otherwise.

Every version of this toolkit before v1.3.0 rewrote screen field arrays
without moving those records. The field moved; its record didn't.

The records are now kept in step. Confirmed on a real Edge 530:

- moving a Connect IQ field to a different position on a screen
- inserting or removing ordinary fields around one
- removing a Connect IQ field outright, with no "Timer" left behind
- a position shift caused by inserting a neighbouring field — the
  ordinary "add a field" case that broke originally
- choosing which app renders, on a device with two Connect IQ apps
  installed

What was a hard refusal is now ordinary editing, in both the GUI
(Add/Remove Field, Move Up/Down, Replace Field, Layout A/B) and
`fit_patch.py` (`--fields`, `--swap-fields`, `--layout`).

## What is still refused

Both remaining refusals exist because the information genuinely isn't
in the edit, not because the operation is risky. Neither has a
`--force` override.

- **Adding a Connect IQ field to a screen that doesn't have one.** The
  id stored in the field array is a generic "a Connect IQ field goes
  here" marker carrying no app identity — two different apps are
  byte-identical there, confirmed by placing both on one screen at
  once. Nothing in the edit says which app a new one should mean.
- **Editing a screen that already holds two Connect IQ fields.** Same
  reason: after a rearrange there's no way to tell which app ended up
  where, and guessing risks silently swapping them.

Use Garmin's own on-device editor for both. The Favorite Screen blocks
added in v1.2.3 also stand — carrying a Connect IQ field to a
*different* profile needs a link record created from scratch, which is
the one case not yet confirmed on hardware.

## Also in this release

- A Connect IQ field placed in a shared/half-width row now draws the
  same style of advisory the Graph/Bars fields already do. The device
  accepts a Connect IQ field in a half-width slot without complaint,
  but the apps tested need full width to be readable. Advisory only,
  never a block.
- If you open a screen whose Connect IQ field no record claims — a file
  already broken by an older version of this toolkit — the GUI now says
  so plainly, rather than leaving you to discover it after a deploy.
- `DEVICE_DEPENDENT_CIQ_IDS` is renamed `CIQ_FIELD_MARKER_IDS`. The old
  name still works as an alias. The rename follows a correction: field
  216 is neither device-dependent nor an app identity.

## Deploy-flow clarity

Two things that were confusing rather than broken, both from real use.

- **The pre-flight step now looks like what it is.** It used to read as
  a second review of changes you'd just seen on the Screens view, which
  made the following click to Deploy feel like a bare "are you sure?"
  prompt. It isn't a repeat — it runs a byte-level comparison against
  the untouched staged copy and a real checksum check of the file about
  to be written, neither of which the Screens view does. It's now
  titled **Pre-Flight Verification**, leads with those two checks as
  explicit pass/fail lines, and shows the change list under "What will
  change on the device".
- **The empty box on the deploy screen now explains itself.** It holds
  post-write verification results and only fills in after the device
  reconnects and you check it — but until then it was simply blank,
  with nothing indicating what it was waiting for. It now has a label
  and placeholder text.

Neither change touches any write path.

## Verification

Headless-verified against real device-written profiles rather than
synthetic fixtures: encode/decode round-trip across all 32 slots × 10
positions; byte-exact re-pack of every record in four captured
profiles; a no-op write leaving a file byte-identical with a valid CRC;
move, remove, insert-shift, no-Connect-IQ and refusal cases each with a
full-file consistency sweep; the CLI exercised end-to-end including
confirming `--force` bypasses neither refusal; and a five-step sequence
mirroring real GUI usage with the consistency sweep clean at every
step.

**Confirmed through the GUI on a real Edge 530**, not only headlessly:
moving a Connect IQ field within a screen; adding and removing ordinary
fields around one (a different code path from Move Up/Down, and the
exact operation that broke originally); the two-Connect-IQ-fields
refusal firing correctly; and — most important of the set — a profile
with *no* Connect IQ fields surviving a full edit cycle unchanged,
since every shape edit now routes through the new code whether or not a
Connect IQ field is involved.

## Version bumps

- `fit_dump.py` 2.5.0 → 2.6.0
- `fit_patch.py` 1.15.0 → 1.16.0
- `gui_app.py` 0.20.1 → 0.21.1
