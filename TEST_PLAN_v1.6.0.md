# Test plan — v1.6.0 (in progress)

*Written 2026-10-01. Covers everything built since the v1.5.0 tag that
needs a display. `fit_dump.py` 2.14.1, `gui_app.py` 0.26.0.*

## Why this exists before anything else gets built

Four changes have landed that cannot be exercised headlessly, and one of
them is of the exact kind that shipped **inert** in v1.5.0 — the per-model
feature worked in every CLI test and did nothing in the GUI, because
`frame.profile_product` was set on the wrong object and `None` silently
means "enforce the 530's rules". Nothing here is believed to work until
the device says so.

**Use `CyclingRoadLayouts.fit` for sections C and D.** It carries all nine
of the newly measured 840 states, which is exactly what needs exercising.

---

## A — Field picker (`gui_app.py` v0.24.0)

Open any screen → **Add Field**.

| | Check | Expect |
|---|---|---|
| A1 | Dialog width | Wider than before (360 → 460). Nothing clipped at the right edge. |
| A2 | Scroll to **Avg Force** | `Avg Force  (id=847, shows as “Average”)` |
| A3 | **Max. Force**, **Max. Lap Force**, **Last Lap Force** | `shows as “MAX”` / `“MAX LAP”` / `“LAST LAP”` |
| A4 | **Primary Target**, **Secondary Target** | `(id=520, no label on-device)` and `(id=578, …)` |
| A5 | **Force**, **3s Force**, **Lap Force** | **No** suffix — their text already says force, so they are deliberately not flagged |
| A6 | Type `force` in Search | Still filters correctly. Matching is on the stored name only; the suffix must not interfere |
| A7 | Select **Power Graph** | The Graph/Bars note below the list still appears (pre-existing behaviour, must not have regressed) |

## B — Tier-2 advisory (v0.26.0, new)

| | Check | Expect |
|---|---|---|
| B1 | Put **Compass** (529) in a slot that **shares a row** | `⚠ “Compass” shares a row -- it will draw correctly but be very small to read at half width.` |
| B2 | Same field in a **full-width** slot | **Silent** |
| B3 | **Map** (725), shared row | Same message, named for Map |
| B4 | A screen holding Map **and** Power Graph **and** a Connect IQ field, all half-width | **Three different messages.** Keeping them distinct is the whole point — if Compass gets told it "needs full width to render as a graph/bar, not plain text", that's wrong |

## C — 840 per-model geometry (v0.25.0 + `fit_dump` v2.13.0)

**This is the inert-feature test.** Open `CyclingRoadLayouts.fit`.

| | Check | Expect |
|---|---|---|
| C1 | Open each of the five **C-variant** screens (counts 3, 4, 5, 6, 7) | Diagram draws the row structure you described on the device, not a generic one |
| C2 | Open the **8/B, 8/C, 9/B, 9/C** screens | Same — these four had **no geometry at all** before today |
| C3 | On the **9/C** screen, put a Graph/Bars field (e.g. Power Graph) at **position 0** | Advisory **fires**. It was silent on this state before v0.25.0 |
| C4 | Same field at **position 4** of 9/C | **Silent** — position 4 genuinely *is* full width there |

> **If C3 stays silent, suspect the wiring, not the data.** The grids are
> verified; the likely cause is `frame.profile_product` not reaching
> `EditScreenPanel`, which is precisely how v1.5.0 shipped inert. Worth
> checking the title bar / details pane says **Edge 840** at all.

## D — Height notes (v0.26.0, consolidated)

| | Check | Expect |
|---|---|---|
| D1 | A **530** profile, 3-field screen, layout **B** | `B: top field renders smaller on-device (not shown to scale here)` — unchanged wording, now from one place instead of two hardcoded copies |
| D2 | 840 **3/C, 4/C, 5/C, 6/C** | A **new** note naming which rows are taller |
| D3 | 840 **9/C** (or 7/C, 8/B, 8/C, 9/B) | **No note.** Correct — no height observation exists for those, and `None` means "nothing known", not "all rows equal" |

## E — Regressions worth a glance

| | Check | Expect |
|---|---|---|
| E1 | Open a **530** profile and walk several screens | Everything exactly as in v1.5.0. The 530 was verified byte-identical across all 30 of its layout states, headlessly — this is the visual confirmation |
| E2 | Any screen with many fields / long names | **No window-width blowup.** This codebase's most recurrent bug, seven occurrences; the picker was deliberately widened and that is safe only because it has a fixed size and never calls `Fit()` |
| E3 | Named screens — Compass, Stamina, Lap Summary, Segment | Layout pickers and content-area diagrams unchanged |

---

## Does any of this need a pull? — NO, for B through F

Asked 2026-10-02. **Every check in B through F is either a display
assertion or a write to the toolkit's own staged copy.** Nothing reads
anything back off the device, so no pull is required and nothing needs
deploying.

More than that: **B, C, D, E and F can all be done in OFFLINE mode with no
device connected at all**, using `CyclingRoadLayouts.fit` and any 530
profile from your folder. That works because `frame.profile_product` is
derived from `file_id.product` **in the file**, which was the point of
making it a property in v1.5.0 — model identity travels with the profile,
not with the USB connection. Worth knowing precisely because section C is
the inert-feature test and it depends on that value arriving.

**But there IS a gap the plan did not cover, and it needs a round trip.**
See section G. It is optional for signing off B–F and important before
release.

## C1 FAILED and is FIXED — re-run C and F on v0.26.2

**Doug, 2026-10-02:** the layout preview read **"(No layout to show)"** for
every C variant and for 8/B, 8/C, 9/B and 9/C. His table matched the nine
`user_grids` states exactly, which is what identified the cause.

**Cause, and it was mine.** `AddScreenPanel`'s diagram still read the
global 530 `LAYOUT_GRIDS`, which holds none of those nine, so it returned
`[]` — and an empty grid is precisely what the diagram draws that message
for. v0.26.1 made that panel's *dropdown* model-aware and left the diagram
global, with a comment claiming it was safe because "a new screen starts at
variant A, which is in the global table at every count". True of the
default and irrelevant to the feature: the whole point of the new dropdown
is that B and C became selectable. **The justification was written in the
same commit that invalidated it.**

A second instance of the same mistake, in the same method, found only
because the first one was visible: the **height note** was also still
global-only. It had no symptom of its own — but at count 3 the note is the
*only* thing distinguishing A, B and C, since all three share the row
structure `[[0],[1],[2]]` and differ purely in row height.

**Expect this on re-run, and it is correct, not a bug:** at **count 3**,
A, B and C all draw the **same three stacked full-width rows**. They differ
only in height, which the grid cannot express. The note below the diagram
is what tells them apart.

## F — Layout variant dropdown (v0.26.1, replaces the A/B radios)

**New since you ran section A. Section A does NOT need re-running** — those
tests are all `FieldPickerDialog`, which this did not touch.

The two A/B radio buttons in **Edit Screen** and **Add New Screen** are now
a single **Layout:** dropdown, built from what the model actually offers.

| | Check | Expect |
|---|---|---|
| F1 | 840, 9-field screen, Edit Screen | Dropdown offers **A, B and C**. This is the bug you found |
| F2 | 840, 8-field screen | **A, B, C** |
| F3 | 840, 3-field through 7-field | **A, B, C** |
| F4 | 840, 1, 2 or 10 fields | **A only**, control disabled — those counts have one variant |
| F5 | Pick **C** on a 9-field 840 screen | Applies. Diagram redraws to the 9/C row structure, and no "Layout B isn't available" dialog appears — that refusal is deleted, not corrected |
| F6 | **530**, 3- to 7-field screen | **A and B** only. Unchanged from v1.5.0 |
| F7 | **530**, 8-, 9- or 10-field screen | **A only**, disabled. Unchanged |
| F8 | 840 **Segment** screen with 4 fields (named type, separate picker) | Reads **"4 fields (C)"**, not "4 fields (3)". Separate bug, live before today |
| F9 | 530 **Segment** with 4 fields | Still "4 fields (A)" / "4 fields (B)". Its "A" stores `f8=2`, so if the letters moved, the positional mapping broke |
| F10 | Change a layout, then re-open the screen | The dropdown shows the variant you chose, i.e. it was written and read back |
| F11 | Load a **Favorite** saved from an 840 C-variant screen onto a 530 | Falls back to a legal variant rather than writing `f8=2`, which the 530 offers at no count |

> **F9 is the one that catches a whole class of error.** The dropdown's
> selection index is *not* the `f8` value — Segment's "A" is `f8=2` on the
> 530. If letters and layouts have come unstuck anywhere, this is where it
> shows.

---

## Known limitation — FIXED 2026-10-01, see section F

**Corrected 2026-10-01 after Doug found it in testing (A-section run).**

On an 840, **neither panel can select a C variant, nor any variant of 8 or
9 fields.** Doug viewing a 9-field screen in **Edit Screen**: the radios
show A and B, B cannot be selected, and there is no C at all.

**The workaround this plan originally gave does not work.** It said to
create the screen in Add New Screen and change its layout in Edit Screen
"which *is* model-aware". Edit Screen is model-aware for **geometry and
advisories** — that is what v0.25.0 added — but **not for the variant
selector**. For a plain user screen it still asks
`count in COUNTS_WITH_B_VARIANT`, the 530's set `{3,4,5,6,7}`, so a
9-field screen gets B disabled and C never existed as a control. Two
radios cannot express three options.

My error, in both this plan and PROJECT_NOTES Doc rev 132.

**~~So there is currently NO route~~ FIXED in v0.26.1** — both panels now
build the control from `layout_variants_for_count()`. The section below is
kept as the record of what was wrong and why. Test it via section F.

**What still works, and is worth confirming — this is section C's point:**
the toolkit now READS and DRAWS those states correctly. The read side and
the write side are separate, and only the write side is blocked, so
sections B through E are unaffected and worth finishing.

**Why the fix is small:** `layout_variants_for_count(0, 9, 4062)` already
returns `[0, 1, 2]` — the data layer has been model-aware all along. Only
the GUI's `else` branch ignores it in favour of the 530 constant. Three
sites need it: that branch, `on_layout_choice()`'s refusal test, and
`_apply_field_list()`'s equivalent.

---

## G — OPTIONAL, but the real write-side gap (needs a deploy and a pull)

**Not required to finish B–F. Required before release.**

Every one of the nine 840 layout states was measured from a profile **the
device itself authored**. v0.26.1 now lets the *toolkit* author them — and
nothing has confirmed that a toolkit-written `f8=2` survives the NewFiles
process and renders as expected on the device.

That is a different question from everything above, and it is the question
this project has been burned by before: the toolkit can write the byte, the
file can pass CRC and read-back, and the device can still do something
else with it. ClimbPro, Compass and the CIQ Timer-fallback were all found
exactly there.

| | Step | Expect |
|---|---|---|
| G1 | On an 840 profile, set a user screen to **9 fields, layout C** using the new dropdown. Deploy | Writes cleanly, pre-flight CRC and content checks pass |
| G2 | Let the device run NewFiles, then look at that screen **on the 840** | Renders as **2 HW rows, 2 HW rows, 1 FW, 2 HW rows** — the 9/C structure, matching what the toolkit drew |
| G3 | Pull the profile back and send it to me | `f8` is still **2** on that record, and the field array is intact |
| G4 | Repeat for one **8/C** screen | Same |

> **If G2 renders something other than 9/C**, the grid is not the suspect —
> it was measured from the device's own file. The suspect is the write:
> either `f8` did not land, or the device re-derived the layout from
> something else on import, which is the behaviour it already shows when it
> **strips screen records by type** and when it **clamps over-range counts
> at render without rewriting the file**.
>
> **If G3 comes back with `f8` changed**, that is a new device behaviour
> and more interesting than the feature.

G1 and G2 alone are worth the bench time. G3 is cheap once the device is
already connected, and it is the only step that proves the byte persisted
rather than merely rendered once.

### G5 — what does a 530 do with an 840-only data field?

**Added 2026-10-04. One screen, and it decides how much work the per-model
field question is worth.**

Confirmed by inspection: `FieldPickerDialog` excludes only Connect IQ
markers, so **on a 530 it offers all 33 fields that were confirmed on the
840 and are absent from the 530's own census** — Force, Stamina, Potential,
Resistance and the rest. Nothing in `fit_patch.py` validates a field id
against the model either. So a 530 user can place field 860 "Force" today
and deploy it.

**What the device then does is unknown.** Precedent points at benign — the
Connect IQ marker renders as Garmin's "Timer" fallback, and the device
clamps an over-range field count at render without rewriting the file — but
that is inference, and this project's rule is that inference about device
behaviour is a hypothesis until hardware says otherwise.

| | Step | Why |
|---|---|---|
| G5a | On a **530** profile, put **Stamina (581)** and **Force (860)** on a user screen. Deploy | Both are 840-confirmed and absent from the 530 census |
| G5b | Look at that screen **on the 530** | Blank? "Timer"? A dash? The field's real name? Something else? |
| G5c | Pull the profile back and send it | Did the device keep ids 581/860 in `f7`, replace them, or strip the screen? |

**This is the deciding experiment.** If the device shrugs, per-model field
data is a nicety — worth an annotation in the picker, not a guard. If it
blanks the screen or rewrites the record, it becomes a correctness issue
and jumps the queue.

Cheapest to fold into G, since the 530 is already connected for G1–G4.

---

## H — Named screens, 530 vs 840 (v0.26.3)

**Added 2026-10-02 after Doug asked whether the C1 class of bug reached
named screens. It did, silently. See Doc rev 136.**

Until v0.26.3, 18 of the 46 states the 840 offers on named types drew
**ordinary-user-screen geometry** — a confident wrong shape with nothing
saying so, because those states are legal and no flag applied.

| | Check | Expect |
|---|---|---|
| H1 | 840, open the **Workout** screen in Census4 (6 fields) | Diagram **blank**, with a note: *"Field arrangement at this layout has not been measured on the Edge 840 — not drawn rather than guessed"* |
| H2 | 840, **eBike Metrics** — change its count to 7 | Same blank + note |
| H3 | 840, **eBike Metrics** at **5** fields | **Draws a real grid.** 5 is measured; this is the control proving H2 is about data, not about the type |
| H4 | 840, **STEPS Metrics** at **4** fields | Draws a real grid (measured) |
| H5 | 840 **Compass** at 0, 1 and 2 fields | All three draw. The 840 offers all three where the 530 locks 2 — the original per-model defect |
| H6 | 840 **Segment** at 4 fields | Picker reads **"4 fields (C)"** for the third variant, not "(3)" — same as F8 |
| H7 | **530**, walk every named screen you have | **Every one draws a grid. No blanks, no notes.** All 25 of its named states are measured, so a blank here is a regression |
| H8 | 840 **Workout** — confirm field editing is offered at all | Allowed on the 840, refused on the 530 (`NO_FIELD_EDIT_BY_MODEL`) |

> **H7 is the regression guard.** The v0.26.3 change only suppresses the
> guessed-geometry fallback for named types. If a 530 named screen now
> draws blank, the suppression is too broad.

**H1 is the cheap one and needs no hardware** — Census4 already has a
6-field Workout screen, and Workout is field-editable on the 840.

To replace those blanks with real geometry, see `NAMED_LAYOUT_CAPTURE.md`.

---

## I — Layout letter, everywhere it appears (v0.26.4 / fit_dump 2.15.1)

**Doug found the screens-list Layout column showing `-` for every
C-variant. The letter was derived in four places by arithmetic on `f8`.
See Doc rev 138.**

| | Check | Expect |
|---|---|---|
| I1 | 840 Layouts profile, screens-list Layout column | A real letter on every screen — **C** where you set C. No `-` on a C screen |
| I2 | 840, counts 1, 2 and 10 | **A** |
| I3 | 840, **GroupTrack List** and **Virtual Partner** rows | `-`, not `?`. Those types have no layout to letter |
| I4 | **530**, a **Segment** screen at 4 fields in layout **A** | **A**. It stores `f8=2` and showed `-` before today — a pre-existing 530 bug |
| I5 | CLI `fit_dump.py screens <840 profile>` | LAY column shows **C** on C screens, blank on A (established terse convention), `-` on types with no layout |
| I6 | Same CLI with `-v` | Reads **`C (f8=2)`**, not `variant=2?` |
| I7 | Change a layout on an 840 screen, then open **Pre-Flight** | *"layout changed from B to C"* — not *"from A to -"* |

> **I4 is a 530 check and the important one.** It confirms the letter is
> positional rather than arithmetic. If I4 reads **C**, the fix has
> reintroduced the exact error it was meant to remove.

### Does section I change the earlier sections?

**No step is invalidated and nothing already passed needs redoing.**
Checked rather than assumed — v0.26.4 touched the Layout COLUMN, the CLI
output and the deploy summary, none of which A through H depend on.

| Section | Effect |
|---|---|
| **A** (picker) | **Unaffected.** Still no re-run — nothing since has touched `FieldPickerDialog` |
| **B** (tier-2 advisory) | Unaffected. `graph_bars_warnings()` unchanged |
| **C** (840 geometry) | Unaffected. **But I1–I3 are free while you are here** — the Layout column is on the same screens list you open to reach C |
| **D** (height notes) | Unaffected |
| **E** (regressions) | **E1 gains weight.** "Walk a 530 profile" now also exercises the changed Layout column, and I4 is the specific case inside it |
| **F** (variant dropdown) | Unaffected. F9 and I4 are complementary, not duplicate: **F9 is the named-type picker, I4 is the screens-list column** — two different renderers of the same positional rule |
| **G** (device round trip) | Unaffected |
| **H** (named screens) | Unaffected. **H6 and F8 are the same check** — 840 Segment at 4 fields reading "(C)". Do it once, in whichever section you reach first |

**Suggested grouping to save passes:** open the 840 Layouts profile once and
take **I1, I2, I3** off the screens list before drilling into **C**, then
**F** on the same screens. **I4 and E1** are the 530 pass. **I5 and I6** are
CLI only and need no device at all.

**One change to expect in output you send me:** the CLI `screens` LAY column
now reads `C` where it used to be blank, `-` for types with no layout, and
`?` for a genuine mismatch. That makes your pasted dumps more diagnostic,
not less — but it will look different from earlier ones in this thread.

---

## J — Offline restore + cross-model warning (v0.27.0)

**Both from Doug's own test-E attempt. See Doc rev 139.**

| | Check | Expect |
|---|---|---|
| **J0** | **Offline entry itself:** click "Work Without a Device", pick a folder with profiles | **The profile list appears.** v0.27.0 crashed here on every attempt (`SetLabel()` on a `wx.TextCtrl`), killing the only offline entry path. Do this first — nothing else offline is reachable until it passes |
| **J0b** | Offline, select a profile from the ordinary **"In folder"** list | **"Restore from Backup..." stays absent.** v0.27.0 hid the deleted list but left this button live, so selecting a normal profile reopened the same dead end |
| J1 | **Offline**, profile list panel | **No** "Deleted, but available to restore" list and **no** Restore button. One line in their place pointing at opening the backup folder as the source and using Export |
| J2 | Offline, read that line | Wraps inside the window — **no width blowup**. It is a read-only TextCtrl for exactly that reason |
| J3 | **Connected 530**, profile list | Deleted list and Restore button are **back**, unchanged from v1.5.0 |
| J4 | Connected **530**, look for an **840** backup to restore | **None is offered, and that is CORRECT** — see the note below. Not a bug and not a test failure |
| J4b | Connected 530, `ls ~/GarminBackups/backups/` | Any folder named with a **timestamp** rather than a serial is a LEGACY backup. Those are offered to either device, so a cross-model restore is reachable only through them — the one path where the J4 warning can still fire |
| J5 | Connected 530, restore a **530** backup | **No** model warning at all — just the normal confirmation |
| J6 | J4, then press **No** | Nothing written. The warning must not be a one-way door |
| ~~J7~~ | ~~Connected 840, restore an 840 backup~~ | **N/A — the configuration cannot exist.** The 840 is MTP with no mass-storage mode, which is *why* offline mode was built. There is no connected 840, so it never reaches the restore path at all |

### Audited, so it need not be re-checked

Every button on `ProfileListPanel` was traced to the panel it opens, and
against every `assert_mode(False, ...)` site in the file:

| Button | Goes to | Offline |
|---|---|---|
| Startup Message... | `startup_txt` | **works** — import/export added v0.23.0; the eject control is hidden |
| Clone... | `clone` | **works** — clones into the folder being viewed |
| View Screens → | `screens` → Preflight → Deploy | **works** — Deploy becomes Export |
| Restore from Backup... | `restore` → Deploy | **device-only.** The one unguarded route, fixed in v0.27.2 |

So `restore_btn` was the only hole, and the audit is the thing that should
have been done when the first fix was written rather than after the second
report.

### ⚠ J4 was a badly specified test — Doug, 2026-10-04

He found no 840 backups offered while a 530 was connected and correctly
diagnosed why: **the restore list is scoped by device serial.**
`list_backed_up_profile_filenames()` restricts the scan to the connected
device's own serial, and its comment already states the intent — *"offering
the OTHER Edge's profiles invites restoring a profile onto hardware it was
never meant for."*

**That is the right behaviour and nothing should change.** His framing:

> a strict restore is same-device. If the user wants to *try* a profile
> from a different model, that is a **migrate**, and **Import** is the
> route they should take.

Which is correct, and it means **the cross-model warning built into
`RestorePanel` on 2026-10-03 is on nearly the wrong path.** Restore can
almost never see a foreign model, by design.

**Almost, not quite** — and the exception is real rather than a
rationalisation. Legacy flat backups, from before per-device separation,
are **deliberately included** for either device because they cannot be
attributed to one; dropping them would orphan restore points. So a
cross-model restore remains reachable precisely through the backups whose
provenance is unknown — which is the case where a warning earns its keep.

So the restore-side check stays, correctly scoped as narrow, and **the
warning's real home is the Import path**, which v0.27.0 recorded as "not
wired -- noted rather than half-done". Doug's framing promotes that from a
loose end to the main requirement.

**Nothing has been changed on his instruction to hold.**

### J7 is void, and it narrows the guard further — Doug, 2026-10-04

There is **no connected mode for the 840**: MTP, no mass-storage. That is
the reason offline mode exists at all, and it is stated on line 52 of
`PROJECT_NOTES.md` — fifty lines into the file's own State of play. The
test was written against a mental model instead of the recorded facts, the
same way J4 was.

**The consequence is sharper than J4's.** Restore is connected-mode-only,
now correctly hidden offline. The 840 is offline-only. Therefore **the 840
can never reach the restore path.** So the cross-model warning there can
only fire on a **530** — the only connected device — meeting a **legacy
flat backup that happens to hold an 840 file**. Since serial-keying
predates the 840 work, that set is probably empty in practice.

So on the restore path the guard is, for this setup, effectively dead. Doc
rev 140 called it "narrow, not inert". **Rev 141 corrects that: on this
path it is nearer inert than narrow**, and Import is not merely the better
home for it but the only reachable one.

> **J5 matters as much as J4.** A warning that fires on same-model
> restores would get ignored within a week, which is the failure mode that
> makes guards useless.

**J4 needs both devices' backups in one working folder**, so it may be the
one J-check worth deferring until you have the 530 connected with 840
backups present. The rest need no 840 at all.
