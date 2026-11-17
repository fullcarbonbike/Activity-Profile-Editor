# Bench test plan — v1.8.0 (#171, Ride Type on a clone)

*2026-11-09, re-scoped 2026-11-11 after Doug's section-A results.
Everything below is already verified headlessly (Doc revs 213, 214) — the generated file is byte-identical to the hand-patched one
that passed all ten hardware steps. What is NOT yet tested is the GUI
itself, because wx cannot run in the environment the code was written
in. So this plan is mostly about the picker's behaviour on screen.*

Device: **Edge 840** (MTP). Section D needs the **530** if it is still
on hand.

---

## Before you start

Back up the profile you clone from, as usual. Nothing here writes to
an existing profile — every step creates a NEW one — but a new profile
consumes one of the device's ten slots, so **delete the test clones
when you are done.**

---

## Section A re-run scope — after the 2026-11-11 fixes

Doug ran A1–A8 and found two bugs; gui_app 0.34.1 and
fit_clone_profile 1.1.1 fix them. **Most of A still stands.** What
changed, and what that means:

| step | stands? | why |
|---|---|---|
| A1 | ✅ stands | no control added or moved |
| A2 | ✅ stands | entry-0 text untouched |
| A3 | ✅ stands | the nine entries and their order are untouched |
| A4 | ⚠ **never reported** | no verdict was recorded for it — see below |
| A5 | 🔁 **re-run** | the note's TEXT changed: shortened, and hard-wrapped |
| A6 | 🔁 re-glance | logic unchanged, but the summary line is wrapped now |
| A7 | ✅ stands | — |
| A8 | 🔁 **re-run** | this is the fix; it is the whole point |

**A4 has no result in the returned table** — every other row carries
one. Probably just skipped while moving to the more interesting A5.
Worth a verdict since the summary line is now wrapped, which is
exactly what A4 reads.

**A8 is the one that matters.** The note and the summary are both
hard-wrapped at 42 columns now, so the panel's natural width should no
longer exceed the window's. If the window still grows, the wrap is
not the whole story and I want to know before the tag.

### ⚠ NEW steps — the filename behaviour is untested

Doug's own observation ("if I start with CyclingGRAVEL.fit and change
the Ride Type, I don't see the prefix being added") became the second
fix, and **no step in this plan covers it.** These four do:

| # | do | expect |
|---|---|---|
| A9 | source `CyclingRoadROAD.fit`, type a name, pick **Gravel** | the suggested filename **loses** `Road` → `CyclingNEWNAME.fit` |
| A10 | source `CyclingGRAVEL.fit`, type a name, pick **Road** | it **gains** `Road` → `CyclingRoadNEWNAME.fit` — Doug's case |
| A11 | type a filename BY HAND, then change the ride type | the typed filename is **NOT** overwritten |
| A12 | clear the filename field, then change the ride type | auto-fill resumes, with the new type's prefix |

**A11 is the one that could regress something.** `_filename_dirty`
follows the field's content rather than the fact it was touched
(#167), and the new re-suggestion on type change reads that flag. If
A11 overwrites a typed filename, #167 is broken and that is worse
than the bug this fixed.

**A12 is its companion** — clearing the field is what resumes
auto-fill under #167, so the two together prove the flag still works
in both directions.

For reference, the prefix the device uses for each type, all nine
measured:

| picked | suggested filename |
|---|---|
| Road | `CyclingRoad<NAME>.fit` |
| Mountain | `CyclingMountain<NAME>.fit` |
| Indoor | `CyclingIndoor_Cycle<NAME>.fit` |
| Cyclocross | `CyclingCyclocross<NAME>.fit` |
| Gravel, Commute, Tour, Ebike, Emountain | `Cycling<NAME>.fit` |

---

## A — the picker, no device needed  ✅ ALL PASS 2026-11-13 (A1–A12, after 0.34.2)

Run the GUI, pick any profile, open Clone Profile.

| # | do | expect |
|---|---|---|
| A1 | look at the Ride type control | a dropdown, between Filename and the validation line |
| A2 | read its current selection | `Unchanged (<source's type>)` — e.g. `Unchanged (Road)` for a road profile |
| A3 | open it | ten entries: Unchanged, then **Road, Mountain, Indoor, Gravel, Cyclocross, Commute, Tour, Ebike, Emountain** in that order |
| A4 | leave it on Unchanged, type a name and filename | the summary line says "keeping the source's ride type" |
| A5 | select **Gravel** | an italic note appears below the summary, naming Gravel twice — screens come from the source, rides count under Gravel in Connect. **Wrapped to four short lines, not one long one** (0.34.1) |
| A6 | select the source's OWN type (Road, cloning a road profile) | the note **disappears**; summary says "left at Road" |
| A7 | back to Unchanged | note stays gone; summary returns to "keeping the source's ride type" |
| A8 | watch the window while switching between A5 and A7 | **the window does not grow at all** — not when the note appears, not when it goes away |

**A8 failed on the first run and this is the fix.** Doug's result:
the note widened the window, and once widened it stayed widened.

Both halves were real but only one was a bug. The widening was —
fixed by hard-wrapping the note and the summary at 42 columns, the
same treatment as #69 and #105. **The not-shrinking is deliberate**:
`_relayout()` grows and never shrinks by design since v0.11.0, after
a report of manually-enlarged windows snapping back on every refresh.
So the pass condition is "never grows", not "grows then shrinks".

If it still grows, the wrap is not the whole story — stop and say so
rather than tagging.

## B — a clone that keeps its type (the regression case)  ✅ ALL PASS 2026-11-13

| # | do | expect |
|---|---|---|
| B1 | clone a profile, Ride type left on **Unchanged** | clone is created, no error |
| B2 | `python3 fit_clone_profile.py` is not involved — check the staged file | `fit_dump.py` shows the same `sub_sport` as the source |
| B3 | deploy, restart, open it on the device | the profile's type reads the same as the source's |

This is the "nothing changed for anyone who doesn't want it" case. It
is verified byte-for-byte headlessly already; B3 is on-device
confirmation.

**PASSED 2026-11-13 on the 530**, with the sub_sport confirmed intact
and no label-width problems — so `wrapped_label()` holds on the
panel's other states too, not just the two Doug had already hit.

## C — a clone that changes type  ✅ ALL PASS — C1–C6 2026-11-13, C7 2026-11-17

| # | do | expect |
|---|---|---|
| C1 | clone `ROAD`, name it something new, Ride type **Gravel** | note shown, clone created |
| C2 | deploy under a NEW filename, restart | device boots, new profile present |
| C3 | the new profile's type on-device | reads **Gravel** |
| C4 | page its data screens | the source's screens, in the source's order |
| C5 | any Connect IQ fields in the source | still render their app, not Timer |
| C6 | pull the profile back and diff | `sub_sport` is 46; expect **message_index relocation** and that is correct, not a fault (Doc rev 210) — compare by f10 |
| C7 | one ride on it, then Garmin Connect | the activity's type is Gravel Cycling, and Reports/Goals count it under Gravel |

### ✅ C7 PASSED 2026-11-17

A `GRVLROAD` clone of the 840's `ROAD` profile, made **through the GUI
picker** rather than hand-patched — so this tested the shipped feature,
not a proxy for it. A 2.98 mile ride on it registered on Garmin
Connect **as a Gravel ride**.

`Totals.fit` confirms it, and more strongly than a single ride could:

| | miles | timer | kcal | rides |
|---|---|---|---|---|
| `ROAD` | +56.20 | +17,727 | +1,855 | +3 |
| `GRVLROAD` | +2.98 | +949 | +100 | +1 |
| **record 0** | **+59.18** | **+18,676** | **+1,955** | **+4** |

Exact sums in all four fields. First time record 0 has been measured
across **several rides on two profiles** in one interval — it
aggregates rather than mirroring one profile, which no single-ride
observation could show. `GRVLROAD` also claimed blank slot 8, as the
pre-allocated pool of rev 207 predicts.

**That completes every section of this plan.**

---

**C7 needs a ride of more than a tenth of a mile.** The 2026-11-09
test very nearly read as a failure because a 98-metre ride renders as
0.0 in a distance goal (Doc rev 212). If you want to check it quickly
instead, look at the **activity's own type** in Connect's activity
list rather than at a goal total — the activity list reads the field
directly, the Goals page reads a rounded sum of it.

**C2 is a NEW profile**, so unlike the earlier GRAVEL test the device
will renumber. That is the point of doing it this way round: the
hand-patched test exercised the replacement path, this exercises the
new-profile path, and C5 is where a mis-maintained Connect IQ
placement would show up.

## D — the 530, if it is still around  ✅ ALL PASS 2026-11-16

| # | do | expect |
|---|---|---|
| D1 | open the GUI against the 530 and read the Ride Type list on its own new-profile menu | **does the 530 offer the same nine?** |
| D2 | clone with a type change, deploy, restart | same as C3 |

**D1 was a real open question and it is now ANSWERED: the 530 offers
the same nine.** Including the later enum additions — Gravel,
Emountain, Commute, Tour — on the older of the two devices. So
`RIDE_TYPES` is not per-model across these two, and the picker is not
offering 530 users a list that is not theirs. Doc rev 217,
`fit_clone_profile` 1.1.2.

**D2 passed as the C1–C6 equivalent on the 530** — clone with a type
change, deploy, restart, verify on-device — minus the ride.

### ⚠ The 530 cannot complete the Connect half, by design

Doug removed the 530 from Garmin Connect deliberately, to stop it
overwriting training status, FTP and HR data from the 840. That makes
the Connect categorisation check **untestable on the 530**, not merely
untested, and it will stay that way. C7 on the 840 is the only route
to that answer, which raises what was already the most important
remaining step to the only one that can answer its question.

## E — the CLI  ✅ ALL PASS 2026-11-16

| # | do | expect |
|---|---|---|
| E1 | `--sub-sport gravel_cycling` | works; prints the old → new type and the template note |
| E2 | `--sub-sport Gravel` | works; also prints "the SDK name is 'gravel_cycling'" |
| E3 | `--sub-sport hand_cycling` | **refused**, lists the nine accepted names |
| E4 | `--sub-sport 46` | **refused** — the SDK name is required |
| E5 | `--name X` alone | works, `sub_sport` untouched |
| E6 | neither flag | refused, "nothing to do" |
| E7 | a profile name with a space, quoted | works (the #168 lesson) |

E1–E6 all pass headlessly; they are here so a Windows run covers them
too, since that is where quoting and path handling have differed
before.

**PASSED 2026-11-16**, E7 included — the quoted spaced profile name,
which is the #168 lesson and the one case headless testing cannot
really speak to, since argparse quoting behaves differently depending
on the shell doing the splitting.

## F — `release_check.py`  ✅ F2a PASS 2026-11-16; F1/F3 effectively confirmed; F2b after the commit

| # | do | expect | needs a commit? |
|---|---|---|---|
| F1 | `python3 release_check.py 1.8.0` on the dirty tree | FAILs on the working tree and lists the files | no |
| F2a | the same run, look for the `import SKIPPED` NOTE | **absent** — `gui_app.py` imports for real on your machine | **no** |
| F2b | after committing, run it again | the working-tree check passes too | yes |
| F3 | read the privacy-check result | passes; the three figures were redacted at rev 213 | no |

**F2 was written as one step and it is really two.** `release_check`
attempts to import every tracked module on every run, regardless of
the tree's state, so the valuable half — does `gui_app` actually
import where wx exists — needs **no commit at all**. Only the
clean-tree check does. Splitting them means you can get the answer
that matters now and the bookkeeping one later.

**F2a is the half that matters**, because this is the check that was
blind to the #171 `NameError` and it cannot run here: no wx in the
environment the code was written in, so every run so far has emitted

```
NOTE  import SKIPPED (dependency not on this machine) -- gui_app.py:
      ModuleNotFoundError: No module named 'wx'
```

On your Mac that line should be **gone**. If it is still there, wx
is not visible to the interpreter running the check, and the check
is no more use on your machine than on mine — worth knowing either
way.

**PASSED 2026-11-16.** `import gui_app` succeeds in Doug's venv and
reports **0.34.2** — so the import check genuinely runs where it
counts, and the version confirms he is bench-testing the build that
carries both section-A fixes rather than a stale copy. The second
half of that is an accident of the one-liner printing the version,
and it is worth more than the check it was added to: every result in
this plan is only as good as the build it came from.

Importing `gui_app` is safe and opens nothing: everything at module
scope is imports, definitions and constants, with the only executable
statement guarded by `if __name__ == '__main__'`. Verified by AST, not
by assumption. So you can also just run it directly:

```bash
python3 -c "import gui_app; print('imports OK', gui_app.__version__)"
```

**On sequencing: do not commit for F2b yet.** C7 is still open, and a
ride that turns up a problem means another code change. The release
notes and version bumps are already written, so a fix landing after
them is exactly how v1.7.5 got tagged one commit early. Commit once,
after C7.

## G — `fit_dump.py screens` header  ✅ ALL PASS 2026-11-16  (NEW, added 2026-11-15)

Added mid-test on Doug's own suggestion, so it has no prior result.
Read-only, and isolated from every path A–F exercises.

| # | do | expect |
|---|---|---|
| G1 | `fit_dump.py screens` on any profile | first line reads `Profile: <NAME>  --  ride type <Type> (<sdk_name>, sub_sport <n>)`, above the `Device model:` line |
| G2 | the same on the clone from section C | the ride type you set, not the source's |
| G3 | the same on a `Totals.fit` | **no** `Profile:` line at all, and no error — that file has no sport message — **PASS 2026-11-16** |
| G4 | `fit_dump.py dump` and `diff` | unchanged; this line was added to `screens` only |

**G3 passed on Doug's 840 backup**, and the output shows the two
header lines are independently sourced, which is the right behaviour
rather than a coincidence:

```
Device model: Edge 840          <- from file_id, which Totals.fit HAS
  NOTE: ...
                                 <- no Profile: line; no sport message
```

A `Totals.fit` carries a `file_id` but no `sport_mesgs`, so the model
line appears and the profile line correctly says nothing at all. That
is `ride_type_line()` returning None rather than printing a
placeholder — the same None-means-say-nothing contract as
`row_height_note()` and `content_composition_note()`.

G1–G3 all pass headlessly here, including the two awkward inputs (a
`Totals.fit`, and a profile whose `sub_sport` is outside the device's
nine, which reports the raw value rather than inventing a label). G4
is the one worth a glance on your side: it is a claim about what did
**not** change.

**ALL FOUR PASSED 2026-11-16**, G4 included — so `dump` and `diff`
really are untouched, which was the only part of section G I could
not honestly certify myself.
