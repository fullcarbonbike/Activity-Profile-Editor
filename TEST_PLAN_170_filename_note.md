# Test plan — #170, the filename note (`gui_app.py` 0.32.0)

*Built 2026-10-28, revised the same day. The dialog is deleted; the
rest is docstring and README corrections that cannot be tested by
running anything.*

## What changed

| | |
|---|---|
| the export dialog's filename prompt | **DELETED** |
| `export_working_copy()` docstring | the false claim deleted, evidence cited |
| `ViewScreensPanel.on_export()` docstring | same |
| `garmin_device.export_profile()` docstring | same |
| `garmin_device.write_to_newfiles()` docstring | same |
| README, two places | same |

**One behaviour changed:** renaming the file in the save dialog no
longer prompts. Everything else — the pre-fill, the CRC check, the
read-back compare — is untouched.

> ⚠ **REVISED 2026-10-28 after the bench test.** Sections A and B
> below tested `0.32.0`, which replaced the warning with an
> information note. **They passed** — but Doug identified the note's
> text as wrong: it called the `Garmin/Sports` route *untested*, when
> in fact it was tested in this project's first days and never worked
> (Doc rev 193). So the note implied a working route that does not
> exist. **`0.32.1` deletes the dialog entirely.** Retest below.

> **A′ and B′ run 2026-10-28 — and A′1 found two more copies of the
> claim.** The export succeeded with no prompt either way (the point
> of the item), but the success dialog's own last line read *"Keep the
> filename exactly as it is."* `0.32.2` fixes that and `DeployPanel`'s
> offline status, and both now state the NewFiles-only rule. See Doc
> rev 195. **Re-run A′2 and B′2 against 0.32.2**; A′1, A′3 and B′1 are
> unaffected by the string change and stand.

## A′. The dialog is gone (`0.32.1`)

Offline, **Export**, and rename the file in the save dialog.

| # | expect | result |
|---|---|---|
| A′1 | **no dialog at all** — the file saves under the name you typed | **pass** 2026-10-28 |
| A′2 | the success dialog: "Exported to", "Verified twice", and a "To put it on the Edge" line that does **not** tell you to keep the filename, and **does** say NewFiles is the only route | **pass** on 0.32.2, both renamed and not |
| A′3 | the file is valid: re-open it in the toolkit, or deploy it | **pass** — CRC `0xe452` identical across both exports |

## B′. Nothing else moved

| # | expect | result |
|---|---|---|
| B′1 | export **without** renaming — unchanged, no dialog, straight through | **pass** 2026-10-28 |
| B′2 | the save dialog still pre-fills the original profile filename | **pass** — pre-filled `CyclingRoadROAD_23.fit`, not a staging name |
| B′3 | device-mode Deploy untouched — it never called this | **pass, statically** — see below |

**B′2 matters.** The pre-fill and the warning were separate things;
deleting one must not take the other. A staging name
(`_staged_<timestamp>…editing.fit`) appearing in the save box is the
failure to watch for — and the un-renamed export above shows a real
profile name, so it survived.

**B′3 was checked in code rather than on the bench**, because it is a
reachability claim and reachability is better read than guessed.
`export_working_copy()` has exactly two callers:
`ViewScreensPanel.on_export()`, which is offline-only, and
`DeployPanel.on_write()`, which calls it inside `if
self.frame.offline_mode:` and returns before touching the device
branch. Nothing on the device-mode write path reaches this function.

*(Noting the method: this project has twice found a path that was
"unreachable by design" and wasn't — `on_check()`'s offline guard
exists for exactly that reason. The difference here is that the
dispatch is a single explicit branch with one decision point, which
is readable with certainty.)*

---

### Superseded: A and B as run against 0.32.0 — both passed

#### A. The dialog itself (0.32.0)

Offline, **Export**, and rename the file in the save dialog.

| # | expect |
|---|---|
| A1 | a dialog appears — it was not deleted |
| A2 | the icon is **information**, not a warning triangle |
| A3 | title reads **Filename**, not "Filename won't match on the device" |
| A4 | the text says the name does **not** matter for the NewFiles route |
| A5 | the text names the Garmin/Sports case as the untested one |
| A6 | **Yes** saves under the suggested name; **No** keeps yours; **Cancel** aborts the export entirely |

**A6 is the only behavioural step.** It is unchanged code, but it is
the part a text edit can break by accident, and all three branches are
one dialog apart.

#### B. Nothing else moved (0.32.0)

| # | expect |
|---|---|
| B1 | export **without** renaming — no dialog at all, straight to the CRC and read-back |
| B2 | the "verified twice" success message is unchanged |
| B3 | device-mode Deploy is untouched — it never called this |

## Pass criteria (`0.32.1`)

- **A′1** — renaming produces no prompt. The whole item.
- **A′3** — the renamed file still works.
- **B′2** — the pre-fill survived the deletion.

## Settled, and no longer an open question

Whether the Edge reads a differently-named file placed directly in
`Garmin/Sports`. `MEMORY_LOG.md` line 235, archived **2026-08-01**,
has it: direct overwrite of `Sports/<Profile>.fit` works **once**,
then stops permanently once that profile has touched `NewFiles` —
confirmed twice on hardware. Every profile this toolkit deploys has
touched `NewFiles`, so the route is dead for all of them.

That is the whole reason this toolkit writes to `NewFiles`, and it is
why there is nothing left for a filename prompt to say.

*Doc revs 193-194: I first recorded this as undocumented and had Doug
reconstruct it from memory, then found it in `MEMORY_LOG.md` — which
is not in the obvious search path and should have been.*
