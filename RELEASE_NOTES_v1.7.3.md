# v1.7.3 — Three fields that weren't in the menu, and a limit the toolkit now respects

*Released 2026-10-23.*

Two things, both found the same way: by writing something to the device
and looking at what came back.

## Three new data fields

| id | name | shows on-device as |
|---:|---|---|
| 358 | Elevation (Asc/Desc) | *nothing — no label at all* |
| 371 | Speed Over Ground | `SOG` |
| 395 | Battery Hours | `Battery`, with `hrs` |

All three now appear in the field picker, with the device's own label
noted beside them where that label doesn't identify the field on its
own.

**None of them is in the Edge's field menu.** That is why they were
missing, and it took a different method to find them.

## Why the old method could not have found them

Earlier releases built the field list by walking the on-device editor's
menu and recording what it offered. That misses a field three different
ways:

| | example | visible in the menu? |
|---|---|---|
| its label is identical to another field's | the four Avg/Max fields added in v1.6.1 | two identical rows — no |
| it has no label at all | **358** | nothing to read — no |
| it isn't in the menu | **371, 395** | not there — no |

The third is the widest and was not understood until now. These ids
come from a field catalogue shared across Garmin's product range, and
the Edge **renders** entries it never **offers**. 371 is documented in
the Venu 4 manual and 395 in the fenix 7 manual — not the Edge's.

So the method changed: write an unknown id into a slot, deploy, and read
what the device draws. 66 ids probed, 4 real fields found, and the two
without labels could not have been reached any other way.

The fourth, **id 331**, is real and still unnamed. It renders with no
label, holds `0:00` through an entire ride while every other timer
counts, and is evidently waiting for a context that a bicycle may not be
able to supply. Recorded rather than guessed at.

## Verified on the device, not inferred

- **358** accumulated ascent and descent over a real ride.
- **395** counted down over a 3:52 ride, consistent with roughly a 40-hour
  full charge. Worth knowing: the figure is **not** "hours left at the
  current rate" — this ride's actual consumption implied about seven
  hours less than the device was claiming. Garmin's description says what
  the number means; it does not say how it is reached.
- **371** tracked the ordinary Speed field closely. Which is consistent
  with Speed Over Ground and does not prove it, so the name comes from
  Garmin's own manual rather than from this observation.

358 is deliberately **not** classified into the Avg/Max family, despite
looking exactly like its missing fifth member. Family membership drives
the placement warnings, and nobody has yet put 358 in a half-width slot
to see what it loses there. Naming a field from what the device showed is
evidence; classifying it from a pattern would be a guess wearing the same
clothes.

## The ten-screen limit is now enforced everywhere

The Edge allows **ten** plain user screens. Garmin-named screens — Map,
Segment, Elevation and the rest — don't count against it.

The toolkit knew that, in one place: the GUI's Add Screen panel. The
command line didn't know at all, so a script could push a profile to
eleven or more, and this release exists partly because that is exactly
what happened while probing for the fields above.

**What an over-cap profile does:** the device rides it perfectly well and
renders every screen. But its own editor shows the overflow as blank
entries with no field count that open to nothing — so those screens can
never be changed on the device again, only through this toolkit.

`fit_patch.py` now refuses to create an eleventh user screen. The limit
lives in one place that every write path can see, instead of one panel.

**`--allow-over-cap`** produces the state deliberately, with a warning
saying what you get. It exists because the field probe genuinely needed
eight extra screens on one profile, and a capability that useful should
be deliberate rather than accidental.

Editing a screen on a profile that is *already* over the cap is not
refused — that would strand anyone who has one.

## Upgrading

No file format change, no migration. Profiles and backups from v1.7.2
work unchanged. The only behaviour that changes is that `--new-slot`
can now refuse, and only past ten user screens.

`fit_dump.py` 2.28.0 · `fit_patch.py` 1.20.0 · `gui_app.py` 0.29.3 ·
`garmin_device.py` 0.13.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0

---

## Known gaps, named rather than hidden

- **Id 331 is unnamed.** Real, no label, inert through a full ride.
- **551 unassigned field ids have never been probed**, in 25 runs. The
  probe covered 66. Sweeping more without a reason to look somewhere
  specific has poor odds.
- **358's half-width behaviour is unmeasured**, which is why it carries
  no family and so produces no placement warning.
- **A slot number is not a stable handle.** A `NewFiles` import was
  observed to renumber screens while preserving every screen's identity,
  order and content. Observed once, on an over-cap profile, so whether
  it is routine import behaviour is not yet established.
- **Named screens have no measured row heights**, so their diagrams draw
  uniform rows.
- **Radar's three layouts cannot be drawn.** Measured, documented, not
  expressible as rows.
- **No per-model field availability.** The picker offers every known
  field to both models; the device substitutes Speed for one it lacks.
- **A cloned profile reads a zero odometer.** Expected rather than lost —
  the clone has a real totals record and it is blank. Editing it is
  scoped (`SCOPE_106_odometer.md`) and not built.
