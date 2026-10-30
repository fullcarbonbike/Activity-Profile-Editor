# v1.7.6 — A warning deleted, a device fact moved, and a tool for the bench

*Released 2026-10-29.*

**This release removes advice rather than adding a feature.** The
export dialog had been warning, for months, that the Edge matches
profiles by filename and ignores anything else. It does not. The claim
was wrong in every version of itself, it lived in eight places, and it
is now gone from all of them.

Also here: a new tool for comparing two profiles, a printable flow
chart, and the last device observation leaves the GUI.

---

> ### ⚠ A note about the v1.7.5 tag
>
> **`v1.7.5` was tagged one commit too early.** It points at
> `Doc rev 188`, which carries `gui_app.py` 0.31.1 — so it contains
> #162, #168 and #169, but **not** #170, and not its own release
> notes, which were never committed.
>
> The tag has been left exactly where it is rather than moved, because
> it is already public and rewriting a published tag is worse than
> explaining one. **`v1.7.6` therefore carries both its own content
> and the tail of v1.7.5's**, including `RELEASE_NOTES_v1.7.5.md`.
>
> If you want the full v1.7.5 feature set, use v1.7.6.

---

## ⚠ The filename warning was wrong, and is deleted

Export a profile under a different name and the toolkit used to
interrupt you:

> *"the Edge matches profiles by filename when it imports them. Under
> any other name it will accept the file and quietly ignore it."*

**None of that is true.** The device accepts any filename, imports the
file, and renames it — generating `Cycling<Sport><DisplayName>.fit`
from the profile's own contents. Tested across five imports on both an
Edge 530 and an 840. One profile deployed under a deliberately wrong
name came back **byte-for-byte identical**, same checksum, under the
device's own generated name.

The claim died in three stages, each a softened version of the last:

| | claim | outcome |
|---|---|---|
| 1 | the device ignores a differently-named file | false — it imports and renames it |
| 2 | matching the name stops the device *rewriting* your file | false — `qqtest.fit` returned byte-identical |
| 3 | keep the name for the `Garmin/Sports/` route | false, and worse — **there is no such route** |

So the dialog is gone, not reworded. Renaming an export now simply
works, silently, as it always did in fact.

**What replaces it is the thing that is actually true**, and had never
once been shown to a user: **`Garmin/NewFiles/` is the only import
route.** Copying a profile straight into `Garmin/Sports/` does not
import it. That has been known since the project's first week and was
sitting in an archived log nobody searched.

The export success message and the offline deploy status now both say
so.

## Compare two profiles — `fit_profile_diff.py`

New tool, for the question that comes up after every deploy:

```bash
python3 fit_profile_diff.py SENT.fit RETURNED.fit
```

> *"I sent the device this file, it gave me back that one. What
> changed, and was it me or the device?"*

It reports byte-identity, which screens **moved** to a different slot,
and which screens **changed** — pairing them by screen identity rather
than by slot number. It also prints what a slot-based comparison would
have said, because the disagreement between the two is itself the
signal: identity saying "nothing changed" while slots say "six things
changed" is the signature of a renumbering import.

Exit status is 0 when the profiles are equivalent and 1 when they
differ, so it works in a loop over a backup folder. Standard library
only.

## A printed flow chart

`GUI_FLOWCHART.pdf` — three pages, US Letter: which mode you are in
and why, device mode step by step, offline mode step by step. It
branches on whether your Edge mounts as a disk rather than on its
model number, because that is the test the toolkit actually performs,
and because offline mode is also the right answer for a mass-storage
Edge with nothing plugged in.

`make_flowchart.py` regenerates it. It is in the repo so the chart can
be rebuilt when the GUI changes — a diagram that cannot be regenerated
goes stale silently.

## The last device fact leaves the GUI

Two observations — what layout variant B does to a Map at zero fields,
and to a Segment at four — were hardcoded in the GUI's diagram code.
They are device behaviour, and they now live in `fit_dump.py` beside
every other fact about those screen types, where the CLI and
`fit_patch` can see them.

No visible change. Verified as a pure refactor rather than as working
code: the old and new logic were replayed across **6,864 states** —
every named screen type, every field count and variant, both models —
with zero differences.

## Installing on Windows

`install.sh` told Windows users the toolkit did not support them,
citing a limitation that was fixed in August. The script is still
macOS-only, for its own reasons — it uses Homebrew and Xcode Command
Line Tools — but that is a fact about the installer, not the toolkit.
It now points at `install_windows.bat`.

## Upgrading

No file format change, no migration. Profiles, backups and favourites
from v1.7.4 and v1.7.5 work unchanged.

`fit_dump.py` 2.30.0 · `gui_app.py` 0.33.0 · `fit_patch.py` 1.20.0 ·
`garmin_device.py` 0.13.1 · `fit_clone_profile.py` 1.0.2 ·
`fit_profile_diff.py` 1.0.0 · `fit_census.py` 1.1.0 ·
`fit_sdk_check.py` 1.0.0 · `install.sh` 1.0.4

---

## Testing

#170 was bench-tested on an Edge 530: the export dialog in both the
renamed and un-renamed cases, the success message, the pre-fill, and
the device-mode path confirmed untouched by reading its only two call
sites rather than guessing at reachability.

**Two of the eight copies of the removed claim were found by running
the export and reading the dialog, not by searching for them.** They
were the only two a user would ever have seen; every copy found by
grep was a code comment. The search had looked for the sentence that
had been written, not for the claim it made.

## Known gaps, named rather than hidden

- **Windows is tested at the dates stated in the README**, not
  continuously.
- **Four fields exist on the 840 and not the 530**, and the picker
  offers every field to both models.
- **Id 331 is unnamed** — a real data field with no label that stays
  at `0:00` through an entire ride.
- **A cloned profile reads a zero odometer.** Expected; the clone has
  a real but empty totals record.
- **An import is not the only thing that moves a screen's slot
  number.** A native on-device Remove does too. The toolkit survives
  both because it pairs on screen identity and never asks why.
