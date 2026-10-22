# Scope — #106, editing a profile's totals (`Totals.fit`)

*Scoping only, 2026-10-22. Nothing built. Doc revs 118, 168, 169 are
the hardware evidence behind it.*

---

## 1. What is already settled, so it isn't re-litigated

| fact | established |
|---|---|
| the device **accepts** a hand-written `Totals.fit` | rev 118 |
| the written value becomes a **baseline it adds to**, over a month of riding | rev 168 |
| a cloned profile **already has** a blank record — patch, never create | rev 168 |
| `sport` does **not** gate display; a blank record needs only the value | rev 169 |
| only **four** fields exist to write | rev 118 |

The four, with their on-disk types:

| f | meaning | type | units on disk |
|---|---|---|---|
| 0 | timer time | uint32 | seconds |
| 1 | distance | uint32 | **metres** |
| 2 | calories | uint32 | kcal |
| 5 | sessions | uint16 | count |

`sport` (f3), `sport_index` (f9), the 32-byte name (f10), f11, f12 and
`message_index` (f254) are **never written**. Record identity is not
ours to change.

---

## 2. The write mechanism — and the one thing that is NOT settled

Doug's framing: `startup.txt` is a **direct overwrite** of a file on
the mounted device, no `NewFiles`, with a power cycle to take effect.
Could `Totals.fit` work the same way?

**Unknown, and I would not assume it.** What rev 118 actually proved is
the `NewFiles` route. Two reasons direct overwrite is a different
proposition from `startup.txt`:

- `startup.txt` is a plain text file the device only ever **reads** at
  boot. `Totals.fit` is **live state the device itself writes** — it
  accumulates ride data into those records. A direct edit while mounted
  can plausibly be overwritten from memory on eject or shutdown.
- rev 115 recorded `Device.fit` declaring the `Totals` directory with
  `flags: 'read'`. rev 118 showed that does *not* mean "cannot be
  restored" — but it was `NewFiles` that disproved it, not a direct
  write.

**Recommendation: ship on `NewFiles`, which is proven.** Then test
direct overwrite separately, as a cheap experiment, and only adopt it
if it survives a power cycle unchanged. The test is one write, one
eject, one restart, one pull — the same shape as everything else here.

If direct overwrite does work it is strictly nicer (no import step), so
it is worth the experiment — just not worth betting the feature on.

---

## 3. The UI flow

Doug's sketch, which I would build as-is:

**Step 1 — list what is actually there.** Read `Totals.fit`, show one
row per record that **has a name**. Blank-named records are real
(unclaimed slots) but there is nothing for a user to recognise, so they
are hidden rather than listed.

```
Profile      Distance     Time      Calories   Rides
ROAD         2,240 mi     189:42      59,553      64
GRAVEL           0 mi       0:00           0       0
INDOOR         7.5 mi       0:45         238       1
```

Show in the user's own units, with the metric value available — the
file is metres and seconds, and a toolkit that silently converts is one
that can silently convert wrongly. State the unit in the column header
rather than leaving it implied.

**Step 2 — pick one record.** One at a time. Multi-record editing adds
nothing a second visit does not.

**Step 3 — Reset, or Set.**

- **Reset** zeroes all four. No data needed, no arithmetic, no
  ambiguity. This is the common case for a clone and should be one
  click.
- **Set** opens the four fields pre-filled with current values, so an
  unchanged field stays unchanged by construction.

**Step 4 — confirm, naming the record and the before/after.** Then
back up, write, and tell the user a power cycle is required.

---

## 4. Where the user gets the numbers — the honest part

This is the part Doug flagged, and it is a **documentation problem, not
a code problem**. The toolkit cannot fetch it; Garmin Connect is the
only source and there is no local API here.

Route: Garmin Connect → **Reports / Statistics** → filter to cycling →
set the date range → read off total distance, total time, total
calories and activity count.

**Two mismatches to state plainly in the UI, not bury in a README:**

1. **Connect groups by activity TYPE, the Edge by PROFILE NAME.** If
   ROAD and GRAVEL both record as "Cycling", Connect cannot split them
   and the user must apportion by judgement. There is no correct
   automatic answer and the toolkit should not imply there is one.
2. **Only four of Connect's ~20 columns have anywhere to go.** No
   ascent, descent, average speed, heart rate, cadence or power. rev
   118 already says any odometer feature must say so rather than
   implying a fuller restore. Put it on the dialog.

**A third thing worth saying, from rev 168:** the device *adds to* what
is written. So the number to enter is the total **as of now** — after
which the Edge keeps counting. Entering a year-to-date figure mid-season
is correct and will keep accruing; entering a lifetime figure when the
user wanted YTD is a mistake only they can catch.

---

## 5. Connected and offline

The existing split handles this with no new concept:

| | connected | offline |
|---|---|---|
| source | `Totals.fit` on the mounted device | `Totals.fit` in the chosen folder |
| write | `NewFiles` (or direct, if proven) | **Export** — save to a chosen path |
| user then | power-cycles the device | transfers it themselves (MTP) |

Mirrors `export_profile()` exactly, including that **the caller owns the
filename** — it must land as `Totals.fit` or the device ignores it.

**Offline needs one case the profile path never had:** the folder may
contain no `Totals.fit` at all. A user who pulled only `Sports/*.fit`
has no totals file, and the feature must say so plainly rather than
offering an empty list. `fit_dump.is_profile_file()` already
distinguishes the file types; the totals file reports `'totals'`.

---

## 6. ⚠ A collision in the backup store, found while scoping

`Totals.fit` **must be backed up before any write** — same discipline as
every other write path. The natural home is
`working_dir/backups/<serial>/<timestamp>/`, where `startup.txt` already
lives beside the profiles.

**But that breaks "Restore a Deleted Profile."**
`list_backed_up_profile_filenames()` finds restore candidates by taking
every backed-up filename **ending in `.fit`**, and its docstring states
the reasoning explicitly: `startup.txt` is safe to co-locate *because it
is not a `.fit` file*.

`Totals.fit` **is** a `.fit` file. Backed up there, it would appear in
the deleted-profile picker as a profile available to restore — and
restoring it would write a totals file into `Sports/` as though it were
an Activity Profile.

Three ways out, in order of preference:

1. **Filter by file TYPE, not extension.** `is_profile_file()` exists
   for precisely this and already returns False for a totals file. It
   needs a path to a readable file, which the backup store has. This
   fixes the class of bug, not the instance.
2. Exclude the literal name `Totals.fit` — a one-line special case that
   works until the next non-profile `.fit` is backed up.
3. Back up totals to a separate folder — avoids the collision and gives
   up the single browsable history.

Option 1, and it should land **before** the write path, not after.

---

## 7. What NOT to build

- **No record creation.** rev 168: a clone already has a blank record.
  Creating one means appending a FIT message and renumbering — large,
  and unnecessary.
- **No writes to `sport`, the name, or `message_index`.** rev 169
  showed `sport` is not needed. Identity is the device's.
- **No arithmetic on the user's behalf.** No "scale the other three to
  match", no deriving calories from distance. Four numbers in, four
  numbers written.
- **No claim about how the device computes battery- or
  estimate-style figures.** Not applicable here, but the same posture:
  rev 172 found the device's own battery estimate is not what a naive
  reading of the manual implies.

---

## 8. Open questions before building

1. **Does direct overwrite work, or is `NewFiles` required?** Section 2.
   One experiment settles it.
2. **Where exactly does `Totals.fit` live** relative to `garmin_root` —
   `Totals/Totals.fit` is implied by `Device.fit`'s directory
   declaration but should be confirmed by looking, as `startup.txt`'s
   location was.
3. **Which unit does the user want to type in?** Showing both is safe;
   accepting both needs a unit selector or a parsed suffix.
4. **Should Reset be offered for a record that has real data?** A clone
   reading zero is the motivating case. Zeroing ROAD by mis-click is the
   motivating accident. The confirmation should name the profile and the
   value being discarded.

---

## 9. Rough size

| piece | where | notes |
|---|---|---|
| read + list named records | `fit_dump.py` | parse exists already; this is presentation |
| patch four fields + CRC | `fit_patch.py` | the rev 118 locate-and-patch, twice proven |
| backup-before-write | `garmin_device.py` | plus the section 6 fix |
| export (offline) | `garmin_device.py` | mirrors `export_profile()` |
| panel | `gui_app.py` | list, pick, reset-or-set, confirm |
| CLI subcommand | `garmin_device.py` | parity with `startup-txt` |

No new unknowns in the file format or the device's behaviour. The
risk left is all in the UI being honest about what the four numbers
mean and where they come from.
