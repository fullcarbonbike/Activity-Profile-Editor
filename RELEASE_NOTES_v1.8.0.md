# v1.8.0 — Clone a profile onto a different bike

*Released 2026-11-09.*

**You can now change a clone's ride type.** Clone `ROAD`, call it
`GRAVEL`, set its type to Gravel, and the rides you log on it count
under Gravel in Garmin Connect — separate reports, separate goals,
separate per-bike tracking — while keeping every data screen you
already set up.

That last part is the point. Garmin Connect's Goals page filters on
sport *plus* sub_sport, so a profile's ride type decides which goal
its rides count against. Before this release, a cloned profile kept
the source's type, so a gravel bike's rides quietly counted as road.

This release also corrects user-facing text in `fit_odometer.py` that
described `Totals.fit`'s first record wrongly.

---

## In the GUI

Clone Profile has a third field, **Ride type**, offering the nine
types the Edge's own "Ride Type" menu offers, in the device's order
and with the device's wording:

> Road · Mountain · Indoor · Gravel · Cyclocross · Commute · Tour ·
> Ebike · Emountain

It defaults to **Unchanged**, naming the source profile's current
type, and in that state writes nothing at all — leaving it alone
produces exactly the file this panel produced before.

Pick a different type and a note appears:

> *The clone's screens come from the source profile, not from this
> device's own Gravel template — a Gravel profile created on the
> device would start with that type's default screens instead. Rides
> on this profile will count under Gravel in Garmin Connect's reports
> and goals.*

Both halves of that matter. The device's templates genuinely differ by
ride type — a natively-created Emountain profile starts with **Assist
Mode** and **Smart Travel Range** screens, a Tour profile with
**Distance to Next** — and a clone carries the source's screens
instead. That is usually exactly what you want when cloning. It is
worth saying out loud when it isn't, because nothing on the device
will mention it.

## On the command line

```bash
python3 fit_clone_profile.py staged.fit cloned.fit \
        --name GRAVEL --sub-sport gravel_cycling
```

`--sub-sport` takes the **FIT SDK name**, not the number: a wrong
integer is silent, a wrong name is caught. The device's menu label is
accepted too, with a note telling you the canonical spelling.

| SDK name | on the device | sub_sport |
|---|---|---|
| `road` | Road | 7 |
| `mountain` | Mountain | 8 |
| `indoor_cycling` | Indoor | 6 |
| `gravel_cycling` | Gravel | 46 |
| `cyclocross` | Cyclocross | 11 |
| `commuting` | Commute | 48 |
| `mixed_surface` | Tour | 49 |
| `e_bike_fitness` | Ebike | 28 |
| `e_bike_mountain` | Emountain | 47 |

**The same nine on both models.** The list was read off an Edge 840
and then confirmed identical on an Edge 530 — including the later
`sub_sport` additions Gravel, Emountain, Commute and Tour, on the
older of the two devices. Data *fields* vary by Edge model; ride types
appear not to. Two devices is not every device, so this is not claimed
as universal.

**Nine, not the SDK's eighteen.** The FIT SDK tags nine further
sub_sports as cycling — `spin`, `downhill`, `recumbent`,
`hand_cycling`, `track_cycling`, `bmx`, `esport`, `enduro`,
`e_bike_enduro` — and no Edge menu offers them. Writing one would
produce a profile whose type the device's own settings screen cannot
express, so they are refused.

**The ride type is never changed as a side effect.** `--name` on its
own leaves `sub_sport` untouched, byte for byte. A wrong ride type
silently reroutes which goal a year of riding counts against, and that
is not a thing to do by implication.

## This was proven on hardware before it was built

Every claim above was measured on an Edge 840 using a hand-patched
file, across ten test steps, before a line of this feature was
written:

| | |
|---|---|
| the device accepts a written `sub_sport` | yes |
| it keeps it across a restart | yes |
| the screens, their order and the Connect IQ fields survive | yes |
| the ride it records is labelled with the new type | yes |
| **Garmin Connect files that ride under the new category** | **yes — reports and goals** |

The file this release generates is **byte-identical** to the
hand-patched one that passed.

### What the device does on import

It reassigns `message_index` whenever the arrangement it receives
differs from the one it already holds — which a clone's always does.
Screen identities, field arrays and display order all survive, and the
device repairs the Connect IQ placements in mesg 170 itself.

The practical consequence for anyone building on this: **compare
profiles by their f10 screen identity, never by `message_index`.**

## `fit_odometer.py` text correction

Shipped in v1.7.8, `list` told you record 0 of `Totals.fit` was "the
device's own ledger". It isn't. It accumulates rides *reported* to it,
including rides performed on a different Edge on the same Garmin
Connect account, matched by profile name. The tool's behaviour never
depended on the answer — it does not write record 0 — but the wrong
description reached a string users read, and that is now fixed.

Record 0's behaviour has since been confirmed on an Edge 840 as well
as the 530.

## New: `release_check.py`

Pre-tag checks, run as `python3 release_check.py 1.8.0`: clean tree,
`HEAD == origin/main`, release notes present and tracked, every
version claimed in the notes matching the module that declares it,
every module compiling and importing, and no rider-attributed distance
figures in tracked files — the repo is public.

It found three of the last category on its first run.

A sixth check went in a day later, after #171's own bench test found a
`NameError` that every other check here was blind to — a function used
in `gui_app.py` and never imported, which only fails on the code path
that calls it. `py_compile` passes, and so does importing the module,
because the name resolves at call time. **No undefined names in
tracked modules** now catches that class outright, borrowing the
interpreter's own symbol tables rather than re-deriving scope rules.

## Versions

| | |
|---|---|
| `fit_clone_profile.py` | 1.1.2 |
| `gui_app.py` | 0.34.2 |
| `fit_odometer.py` | 1.0.4 |
| `release_check.py` | 1.2.0 |
| `make_flowchart.py` | 2.0.1 |
| `fit_dump.py` | 2.31.0 |

## Two things the bench test found

Both in the GUI, both fixed before release.

**The filename suggestion ignored the new ride type.** Cloning
`CyclingGRAVEL.fit` and choosing Road suggested `CyclingNEWNAME.fit`,
where the device writes `CyclingRoadNEWNAME.fit` — and it failed the
other way too, keeping a `Road` segment the device would have dropped.
The suggestion now follows the ride type you picked, falling back to
the source's prefix when you leave the picker on Unchanged. It is only
ever a suggestion and the device renames on import regardless, but a
suggestion that contradicts the device on the very screen where you
just declared the type is worse than none.

This needed the device's filename segment for all nine ride types.
Every one is measured, and **five of the nine are empty** — the
firmware has a filename label for sub_sports 6, 7, 8 and 11 and none
for the later additions, so `CyclingGRAVEL.fit` really is what the
device writes.

**Two labels widened the window.** The ride-type note did it first;
then a clone name colliding with an existing profile did it again,
from the opposite branch of the same if/else — the success branch had
been wrapped and the problem branch had not. Both are wrapped now, via
a `wrapped_label()` helper that any branch can route through, and the
same pair in the Import panel is wrapped with them. A sweep found 28
more such labels elsewhere in the GUI, all predating this release;
they are left alone, but `release_check.py` now ratchets the count so
it cannot grow.

The underlying behaviour: Now
hard-wrapped and shortened. The window growing and never shrinking is
deliberate — it dates from a report of manually-enlarged windows
snapping back on every refresh — so the fix is to stop causing the
growth rather than to re-introduce shrinking. The validation summary
line is wrapped now too; it was already long before this release, and
the new ride-type clause is what pushed it past the window edge.

## `fit_dump.py screens` now names the profile and its ride type

```
Profile: GRAVEL  --  ride type Gravel (gravel_cycling, sub_sport 46)
Device model: Edge 840
```

Doug's suggestion, from using `screens` during the bench test to check
a clone's ride type and having to read the raw message by hand. The
tool prints everything else about a profile; it may as well print the
field this release lets you change.

A `sub_sport` outside the nine the device offers is reported with its
raw value and a plain note that it is not on the Ride Type menu —
no invented label.

## Also updated

`GUI_FLOWCHART.pdf` — the capability table and both Clone entries said
cloning copies a profile under a new *name*, which was all it could do
before this release. They now mention the ride type, and the chart
states what the GUI warns about: the screens come from the source
profile, not from the Edge's own template for the chosen type.

## Upgrading

Nothing to migrate. Existing clones are unaffected, and a clone made
with the Ride type picker left on **Unchanged** is byte-identical to
one made by any earlier version.
