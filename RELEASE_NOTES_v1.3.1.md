# Activity Profile Editor for Garmin Edge — changes since v1.3.0

Covers everything since the `v1.3.0` tag (2026-09-07). Suggested tag for
this update: **v1.3.1** — a small guard fix, no new features, no
breaking changes.

## Fix

- **GroupTrack List, Virtual Partner and Workout can no longer have data
  fields edited.** Selecting one and pressing "Add Field..." opened the
  normal field picker, which was wrong: the device generates these
  screens' contents itself — the riders you're connected to, your
  Virtual Partner, the current step of a structured workout — and
  Garmin's own on-device editor offers no field options for any of them.
  There was never anything there to edit.
- The five field buttons and the layout A/B choice are now **greyed out**
  for such screens, rather than accepting a click and refusing
  afterwards. A hard refusal remains behind them as a backstop, in both
  the GUI and `fit_patch.py`.
- **Showing, hiding and reordering the screen still work normally.**
  Only field editing is blocked.

Workout was previously only *warned* about, because its stored field
bytes are real and readable — it carries a full field array identical to
a Cycling Dynamics screen's. That turned out to be the useful part of the
finding: GroupTrack List stores 0 fields, Virtual Partner stores 255 (an
unset marker), and Workout stores a genuine array of 2, yet none of the
three can be edited on the device. Whatever a screen has stored tells you
nothing about whether it's editable, so each type has to be confirmed
against the on-device editor individually. That's the bar for anything
added to this list later.

On the command line this applies to `--fields`, `--swap-fields` and
`--layout`, with no `--force` override — `--force` cannot conjure a
field array that doesn't exist. `--enable`/`--disable` and
`--swap-order` are unaffected.

## Known issue, being investigated

The layout diagram draws Garmin's special screens — Map, Lap Summary,
Elevation, ClimbPro, Cycling Dynamics — using the ordinary
two-stacked-fields arrangement. That isn't how they actually render on
the device, and because the same layout model also feeds the "needs full
width" advisories for Graph/Bars and Connect IQ fields, those advisories
can be wrong on these screens too.

Investigation established that Lap Summary puts its content area at the
*bottom* with 1–4 flexible fields above it and no A/B choice, and that
the metric shown in its lap table is not stored in the Activity Profile
at all — so what the toolkit currently reports for these screens is
accurate as far as the file goes. A full survey of all twelve special
screens is now complete, and the fix is scoped for the next release
rather than this patch, because these screens turn out to fall into four
distinct groups with per-type layout rules. Details in `PROJECT_NOTES.md`
Doc rev 111.

One specific consequence is worth knowing about if you edit a Segment
screen: its 4-field layout offers an A and a B variant, and the toolkit
currently writes the wrong value for A. Leave a Segment screen's layout
alone until the next release, or set it on the device.

## Version bumps

- `fit_dump.py` 2.6.0 → 2.7.0
- `fit_patch.py` 1.16.0 → 1.16.1
- `gui_app.py` 0.21.1 → 0.21.2
