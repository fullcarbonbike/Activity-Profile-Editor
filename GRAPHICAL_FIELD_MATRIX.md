# Graphical data-field rendering matrix — 840 vs 530

*Generated 2026-10-09 from the measured grids and the row-height model.*

This sheet records **what a graphical field draws at each slot size**, per
model. The cell to fill in is what it *draws*, not whether it works.

It started from Doug's 2026-10-09 pass, which found that the 840 and the 530
render these fields differently and that the Bar types change *form* rather
than merely shrinking. Several of that pass's conclusions have since been
narrowed or overturned by measurement — see **Settled, no action** in the
status section below for where things actually stand, and the dated sections
further down for how each conclusion changed.

## STATUS — what is left to test

*Current as of 2026-10-13. Everything below this section is detail and
working notes; this is the whole of the outstanding work.*

| family | Edge 840 | Edge 530 |
|---|---|---|
| **Graph** 23, 343–346, 368 | **343–346 to redo** (23 ✓, 368 ✓) | ✅ complete |
| **Bars** 347–350 | ✅ complete | ✅ complete |
| **Composite** 351–354 | ✅ complete | ✅ complete |

**One block left: the four Graph rows on the 840 (343–346).** Everything
else in the matrix is measured. Two small open questions remain beside it —
the `*` label TEXT for the 530 Graph family, and whether 352 reads `*Speed`
or `*MPH` at S1, which decides whether the unit-substitution exception is
about Speed or about Bars.

### The work, in the order that costs least

1. **Redo 343–346 on the 840.** The returned rows had six values for five
   columns, probably including a 1/4-screen row from toggling layouts. One
   5/B screen plus one 3/A plus one 1/A covers all five columns.
2. ~~**Bars family, both models.**~~ ✅ **Done 2026-10-13**, all eight rows,
   family-uniform on both models. Produced the sheet's most interesting
   result — form follows **aspect ratio**, gauge → bar → gauge — and showed
   that sub-field thresholds differ **by family** on the same device.
3. ~~**Composite 351, 353, 354 on the 530.**~~ ✅ **Done 2026-10-13**, all
   four, family-uniform on the 530 as well. Showed that the composite family
   *loses* its label as the slot grows — the opposite of the Graph family —
   with the unit carrying the identification from S2 up.
4. **The `*` label TEXT on the 530 at S1 — Graph family only now.** The
   Bars pass answered it for 347–350: three matched the predicted base-metric
   name, **348 gave `MPH`** (the unit) instead of `Speed`, and the marker
   **leads** on all four. Still unrecorded as text for the Graph family —
   343, 344, 345, 346, 368, where the same question applies and 344 is the
   one to watch, since it is Speed and may also show its unit. Marker
   position settled as leading; August's trailing `Speed *` is now the only
   contrary record and is probably a loose transcription.
5. **The two missing geometries, if you want them.** `4/A` gives
   quarter-screen rows and `2/A` half-screen — neither is among the five
   columns, because both states were left unmeasured. A 4-field layout A
   screen answers two things at once: whether its four rows really are
   equal (closing the height gap) and what a graph draws in a 1/4 row
   (a sixth column).

### Not needed

- **A ride, for the zone counts.** Doug, 2026-10-13: a live ride shows which
  zones become *active* but should not change the *number* of zone plots in
  the field, which is what the editor already shows. So the band count
  stands as geometry, and the remaining cross-device oddity — 840 `Z1–2`
  vs 530 `Z5` at the same S3 — is a real rendering difference rather than a
  data artifact. Optional to confirm on a ride; nothing is blocked on it.

### Settled, no action

- the `*` exists on the 530 and **not** on the 840 — decided by id 23
  degrading on the 840 with no marker
- labels change with slot size on **both** models
- id 23 is on the 530 after all; it was hiding behind its own degraded label
- the composite family has one threshold; the Graph family has two

---

## Why this is only five columns

Across the 840's and the 530's **measured** user states there are five
distinct slot geometries, the same five on both models. Height is in units
where the screen is 5 units tall (the half-width row rule).

> ### ⚠ CORRECTION 2026-10-12 — five is the MEASURED set, not the full set
>
> This section previously read *"this is the full set — not a sample"*. That
> was wrong, and Doug found it from the device: *"I think I mixed in a 1/4
> screen, when I toggled thru the layouts... the 5 tests don't include that
> variation."*
>
> Two states were deliberately left unmeasured — `2/A` and `4/A`, because
> the slot-heights sheet asked for them with a generated hint that printed
> an impossible number. Under the 5-unit rule each contributes a geometry
> that is **not** among the five:
>
> | state | each full-width row | sits |
> |---|---|---|
> | **4/A** | 5/4 unit = **1/4 of screen** | between S2 and S3 |
> | **2/A** | 5/2 unit = **1/2 of screen** | between S4 and S5 |
>
> So the real count is **seven**, of which this sheet measures five.
>
> **How the error happened, which matters more than the error.**
> `row_height_units()` correctly returns `None` for both states. The
> generator that produced this list iterated over the entries *present* in
> that table, so an honest omission became a confident "full set" one step
> downstream. The data never lied; the derivation dropped the distinction —
> the same shape as `layout_grid()` returning `None` for
> measured-but-undrawable and genuinely-unknown alike, which is what
> `fit_dump.py knowledge` exists to prevent. A gap marked in one place does
> not protect a claim derived from it somewhere else.
>
> **Cheap way to close it while passing through:** a 4-field layout A screen
> shows four quarter-screen rows. Noting (a) whether those four rows really
> are equal, and (b) what a graph field draws in one, closes both the 4/A
> height gap and a sixth matrix column at the same time. 2/A likewise with
> a 2-field screen.

| # | slot | width | height | share of screen |
|---|---|---|---|---|
| S1 | half-width | half | 1 unit | 1/5 |
| S2 | full-width, regular | FULL | 1 unit | 1/5 |
| S3 | full-width, 3/A | FULL | 5/3 unit | 1/3 |
| S4 | full-width, tall | FULL | 2 unit | 2/5 |
| S5 | full-width, whole screen | FULL | 5 unit | 5/5 |

Size order is S1 < S2 < S3 < S4 < S5. Doug's impression is that bigger is
better throughout; if that holds, each field has a single **threshold** and
the cells below it all read the same.

## The three screens that cover all five

### 1 field(s), layout A

    row 0  [ 0 ]   FULL 5 unit   -> **S5**

### 3 field(s), layout A

    row 0  [ 0 ]   FULL 5/3 unit   -> **S3**
    row 1  [ 1 ]   FULL 5/3 unit   -> **S3**
    row 2  [ 2 ]   FULL 5/3 unit   -> **S3**

### 5 field(s), layout B

    row 0  [ 0 ]   FULL 1 unit   -> **S2**
    row 1  [ 1 ]   FULL 2 unit   -> **S4**
    row 2  [ 2 | 3 ]   half 1 unit   -> **S1**
    row 3  [ 4 ]   FULL 1 unit   -> **S2**

That is the whole grid: S5 from the 1-field screen, S3 from 3/A, and S1,
S2 and S4 together from one 5/B screen. The 530 offers all three of these
states, so the same three screens work on both devices.

## The matrix

Write what it DRAWS. A suggested vocabulary, so cells are comparable —
but if none fits, write what you actually see rather than forcing it:

`circle` circular/gauge form · `bar` straight-line bar · `plot` line or
area graph over time · `zones` banded zone display · `number` numeric only,
widget gone · `blank` nothing drawn · `n/a` not offered in the picker

Add `*` after the value if the editor marked the label that way.

### Graph family — Edge 840 — PARTIAL 2026-10-12

| id | field | S1 half | S2 full reg | S3 full 3/A | S4 full tall | S5 full screen |
|---|---|---|---|---|---|---|
| 23 | HR Zone Graph | label `HEART RATE` + number, **no plot**, no `*` | label `HEART RATE` + number, **no plot**, no `*` | label → `HR Zone Graph`, plot Z1–2 only, **no number** | label → `HR Zone Graph`, plot Z1–5, no number | label → `HR Zone Graph`, plot Z1–5, no number |
| 343 | Heart Rate Graph | *held — see below* | | | | |
| 344 | Speed Graph | *held — see below* | | | | |
| 345 | Cadence Graph | *held — see below* | | | | |
| 346 | Power Graph | *held — see below* | | | | |
| 368 | Elevation Graph | tiny plot + single number | small plot + single number | plot + number + **ASC/DESC** | larger plot + number + **ASC/DESC** | largest plot + number + **ASC/DESC** |

**343–346 are held as unmeasured, not transcribed.** The returned rows
carried six values for five columns. Doug, on being asked which was the
stray: *"I think I mixed in a 1/4 screen, when I toggled thru the layouts,
but let me make sure, the 5 tests don't include that variation."* A 1/4
screen is `4/A`, which is genuinely outside these five columns — see the
correction at the top of this file. Left blank rather than guessed; the
pattern suggested an answer, and a suggested answer is what the
slot-heights sheet taught not to record.

#### The `*` question is ANSWERED, not moot

Doc rev 159 and an earlier section of this file closed it as *undecidable
and harmless*, on the grounds that separating "the 840 has no marker" from
"the 840 has a marker that stays silent when nothing is lost" would need an
840 field that genuinely loses content — and that none was known.

**Id 23 is that field.** On the 840 at S1 and S2 it shows a label and a
number and **no plot** — real degradation, the same loss the 530 marks with
`*` — and there is no `*`. Doug's own 530 row writes the marker explicitly
at the same sizes, so the contrast is within one observer's notation.

So: **the 840 has no `*` marker.** Reading (a), settled by evidence rather
than closed as unanswerable. Worth noting the earlier reasoning was sound —
the test available *then* could not distinguish the two — and that "moot"
was still the wrong label, because a decisive case existed and had simply
not been measured yet. *Undecidable with current data* and *undecidable* are
different claims.

#### "The 840 scales, never degrades" is FALSIFIED

Rev 157's headline, from the graph/bars and composite families, was that the
530 degrades and the 840 scales. Id 23 degrades on the 840 — no plot at
either S1 or S2. The real picture is narrower and more interesting:

| | 530 | 840 |
|---|---|---|
| 343–346, 368 at S1 | loses the plot, marked `*` | keeps a tiny plot *(pending recheck)* |
| 23 at S1 and S2 | loses the plot, marked `*` | **loses the plot, unmarked** |
| everything S3 and up | identical | identical |

So the models differ in **where the threshold sits and whether it is
signposted**, not in whether degradation happens at all. And **23 has a
higher threshold than the rest of its family on both models** — making it
the family's true outlier, not 368.

#### Label-by-size is a BOTH-models behaviour

The 840 relabels exactly as the 530 does — `HEART RATE` when degraded,
`HR Zone Graph` when plotting. Only the `*` is 530-only. Doc rev 159
described this as a 530 behaviour; it is not, and that is the part of rev
159 to supersede.

#### ⚠ The zone counts: partly structural, partly not, and confounded

Doug, 2026-10-12: *"I only see what the editor shows, but on a Live Active
profile, the displayed zone of zones would most likely be the one(s) that
I'm exerting in at the time, this may need an actual ride interactive to
document."*

Right to raise, and it splits in two:

**Within one device, the band count IS structural.** On the 840, in one
editor session with one set of data, S3 showed `Z1–2` and S4/S5 showed
`Z1–5`. Same data, different heights, different band counts — so **height
determines how many bands are drawn**. That is a layout property and belongs
in this sheet.

**Across devices, WHICH bands differ, and that is unexplained.** At S3 the
840 shows `Z1–2` and the 530 shows `Z5`. A pure "as many bands as fit" rule
would predict the same *end* of the range on both. Low zones on one and the
top zone on the other is not that. Candidates, none tested:

- the editor preview is a static mock that differs per model
- one device shows the lowest bands and the other the current/last zone
- the two previews reflect different stored histories

**What a ride would settle:** whether the drawn bands track live exertion at
all. If they do, the cell means "as many bands as the height allows, filled
from live data" and the specific zone names in this sheet are session
artifacts. If they do not — if the editor and the activity screen show the
same bands — then the zone set is fixed per height and the cross-device
difference is a real rendering difference worth its own entry.

Recorded as observed; the **band count** is treated as geometry, the
**zone identities** are not.

#### The editor-vs-live question, for the sheet as a whole

Everything in these tables was read from the **editor**, not from a running
activity. That is fine for what the matrix is for, provided the distinction
is kept:

- **structural cells** — plot present or absent, label text, whether AVG/MAX
  or ASC/DESC appear at all — are what `graph_bars_warnings()` needs, and
  the editor renders the real widget at the real size
- **content cells** — which zones, what values — are placeholder outside a
  ride and mean nothing here

Only id 23's zone identities fall in the second group. No other cell in this
sheet records a value, so no other cell is affected. Worth stating plainly
rather than leaving implicit, because "measured on the device" and "measured
while riding" are different claims and this sheet only supports the first.

### Graph family — Edge 530 — MEASURED 2026-10-11

| id | field | S1 half | S2 full reg | S3 full 3/A | S4 full tall | S5 full screen |
|---|---|---|---|---|---|---|
| 23 | HR Zone Graph | `*` marked | `* Heart Rate` + number, no plot | label → `HR Zone Graph`, plot Z5 only, **no number** | label → `HR Zone Graph`, plot Z1–5, no number | label → `HR Zone Graph`, plot Z1–5, no number |
| 343 | Heart Rate Graph | `*` label + number, no plot | small plot (left) + single number | plot + number + AVG/MAX | larger plot + number + AVG/MAX | largest plot + number + AVG/MAX |
| 344 | Speed Graph | `*` label + number, no plot | small plot (left) + single number | plot + number + AVG/MAX | larger plot + number + AVG/MAX | largest plot + number + AVG/MAX |
| 345 | Cadence Graph | `*` label + number, no plot | small plot (left) + single number | plot + number + AVG/MAX | larger plot + number + AVG/MAX | largest plot + number + AVG/MAX |
| 346 | Power Graph | `*` label + number, no plot | small plot (left) + single number | plot + number + AVG/MAX | larger plot + number + AVG/MAX | largest plot + number + AVG/MAX |
| 368 | Elevation Graph | `*` label + number, no plot | small plot (left) + single number | plot + number + **ASC/DESC** | larger plot + number + **ASC/DESC** | largest plot + number + **ASC/DESC** |

*(Doug's returned table listed 344 twice with identical values; recorded once.
Not a discrepancy — the two rows agreed.)*

#### ⚠ CONFLICT: id 23 and the 530

Doug, 2026-10-11: HR Zone Graph is **not offered on the 530**. That sits
awkwardly against two existing records:

- `fit_dump.py` line 136: *"CORRECTED 2026-08-11 — was 'Heart Rate (Alt)';
  Doug verified the real on-device name directly"*. The comment does not say
  which device, but 2026-08-11 predates this project's 840 work — the 840
  census was Phase C in late September — so that verification was almost
  certainly on a **530**.
- `EDGE840_NEW_FIELDS_CHECKLIST.md` line 262: confirmed 2026-09-30 that the
  **840** offers HR Zone Graph and no "HR Zone Bar".

So 23 is confirmed present on the 840, and was named from what looks like a
530 observation, yet now reads as absent from the 530.

**The likely benign explanation, and the cheap check:** this pass walked the
**Graphical** category. 23 may well be on the 530 but filed under **Heart
Rate** instead. That would reconcile all three records at once and make the
cell "not in Graphical on the 530" rather than "not on the 530".

**No restore needed — the bytes are already on disk.** A scan of all 80
`.fit` files available found **22 screens containing id 23**:

| written by | count | earliest | latest |
|---|---|---|---|
| Edge 530 (product 3121) | 21 | **2026-07-31** | 2026-09-29 |
| Edge 840 (product 4062) | 1 | 2026-10-06 | — |

Every one is the **same screen**: `message_index=6`, `f10=2` (a plain user
screen, not a named type), **6 fields, layout A**, with id 23 at **position
3**. Its neighbours are 59 Time of Day, 317 Light Battery, 56 Timer, then 23,
then 48 Speed and 49 Avg Speed.

Two things follow immediately:

1. **It is in Doug's live ROAD profile on BOTH devices** — the 2026-10-06
   file is 840-written. So nothing needs restoring to look at it.
2. **Position 3 of 6/A is a full-width 1-unit row — that is S2.** The
   `23 / S2` cell can be read straight off a screen that already exists, on
   either device, with nothing to build.

Files in the working folder carrying it, if a specific one is wanted:
`CyclingRoadFLDTEST.fit` (2026-09-24), `CyclingRoadCNTTEST2.fit`,
`CyclingRoadCNTTEST.fit`, `CyclingRoadCIQTEST.fit`,
`CyclingRoadValueSwapTest.fit` — all 530-written.

#### ✅ RESOLVED 2026-10-11 — and the answer was none of the three readings

Doug found it in the ROAD profile: *"in the full width 1/5 height data field
it is labeled `* Heart Rate` but if I give it a larger data field the Label
changes to `HR Zone Graph` with a plot. It was just confusing in the 530
editor (I've been getting used to the 840)."*

**Id 23 is on the 530. It was never missing. Its LABEL CHANGES WITH SLOT
SIZE.**

| slot | 530 label | content |
|---|---|---|
| S1 / S2 (degraded) | `* Heart Rate` | plain HR number |
| S3 and up | `HR Zone Graph` | plot |

So one id has **two different device strings depending on geometry**, and at
the degraded size the string is the *base metric's* name with a `*` in front
— one asterisk away from id 13, whose label is literally `Heart Rate`.

That is why it could not be found: at that slot size the editor was calling
it Heart Rate. **The same blind spot as field 352**, arrived at from the
opposite direction — there a field hid behind another field's name
permanently, here it hides behind one only at certain sizes.

#### This un-does an old "correction" that was not one

`fit_dump.py` line 136 records 23 as *CORRECTED 2026-08-11 — was "Heart Rate
(Alt)"*, and the README's v2.4.7 note pairs it with 348/349, transcribed then
as `Speed *` and `Cadence *`, renamed to Speed Bars and Cadence Bars —
*"confirming the `*`/`(Alt)` marker denotes a Graph/Bars-style field needing
a full-width slot"*.

August got the **mechanism** right. What it got wrong was treating the two
strings as a mistake and a fix. They are **both real device labels for the
same id at different slot sizes**, and replacing one with the other threw
away a fact rather than correcting an error. The degraded strings were
evidence, and they were discarded as typos.

#### The rule this suggests, now worth testing deliberately

> **On the 530, a graphical field in a slot too small for its widget
> relabels to its base metric with a `*` prefix.**

One rule covering id 23 (`* Heart Rate`), 348/349 (`Speed *`, `Cadence *`)
and — if it holds — 343–346, 368 and the composite family 351–354.

**It predicts specific strings.** While filling the S1 column, record the
*label text*, not just "`*` label/number only":

- 343 → `* Heart Rate`? 344 → `* Speed`? 345 → `* Cadence`? 346 → `* Power`?
- 368 → `* Elevation`?
- 352 at half width → `* Speed`? and 351 → `* Heart Rate`?

If those come back as predicted, the rule is established and the `*` is
explained. If the prefix sits on the *other* side for some fields — August
transcribed 348 as `Speed *`, trailing, while 23 is `* Heart Rate`, leading
— then position varies and that is worth knowing too, since it affects
nothing functionally but tells us whether these are one mechanism or two.

#### Consequence: `FIELD_ID_NAMES` assumes one string per id

It holds one display name per field, and `AMBIGUOUS_DEVICE_LABELS` holds one
alternate. Neither can express *"this id displays A at small sizes and B at
large ones"*. Not necessarily a thing to fix — the full-size name is the
right one for a picker — but it needs documenting, because the degraded
string is what a confused user is actually looking at, and that is precisely
the confusion that cost two days here.

#### What the bytes could and could not settle

Kept for the record, because the reasoning stands even though the answer
arrived another way.

Worth separating carefully, because it is easy to over-read a file:

- **proven** — the 530 stores id 23, and has since at least 2026-07-31
- **proven** — the 840 stores it too (2026-10-06)
- **strongly implied** — the 530 *renders* it, since the 2026-08-11 entry
  records Doug reading its on-device name directly
- **NOT proven** — that the 530's editor ever *offered* it in a category

The gap matters: this toolkit can write any field id into `f7` regardless of
whether the device's own picker lists it, and some of those 22 files are
toolkit staging artifacts (`edit_staged.fit`, `field_change.fit`). So a third
possibility joins the two above:

> **(c) placeable but not offered.** The 530 renders id 23 perfectly well,
> but its editor does not list it anywhere — making Doug's observation
> exactly right and not in conflict with anything.

That would be the mirror image of the "hardware-gated in the picker" case
`FIELD_ID_BUILD_SHEET.md` already describes, and it would be a genuinely new
category of fact for this project: a field the toolkit can place that the
device cannot.

**The question only Doug can answer:** was id 23 originally put on that
screen *by hand on the 530*, or *by the toolkit*? If by hand, the 530 offered
it once and the puzzle is which category. If by the toolkit, (c) is live and
the 530 may never have offered it at all.

Recorded as a conflict rather than a finding precisely because resolving it
by picking whichever record is more recent is how the 2026-08-17 batch went
wrong.

#### ⚠ THE BINARY MODEL IS WRONG. There are TWO thresholds, not one.

This is the most consequential thing in the sheet so far, and it contradicts
what was written in Doc rev 157 two days ago.

| slot | plot? | sub-fields? |
|---|---|---|
| **S1** half, 1 unit | **no** — label + number only, `*` | no |
| **S2** full, 1 unit | yes, small, left | **no** |
| **S3** full, 5/3 units | yes | **yes** |
| **S4** full, 2 units | yes, larger | yes |
| **S5** full, 5 units | yes, largest | yes |

Two separate things are lost at two separate sizes:

1. **S1 → S2: the plot appears.** Width is what buys the graph. This is the
   case `GRAPH_OR_BARS_FIELD_IDS` and the existing "needs full width"
   advisory already cover, and they are correct about it.
2. **S2 → S3: AVG/MAX appear.** *Height* is what buys the sub-fields. At
   full width but regular height, the field still loses content — and
   **nothing in the toolkit warns about this today.**

So v1.6.0 does not merely over-warn on the 840 (#153). It also
**under-warns on the 530**, on the very model its advisory was measured
from. A user who puts a Power Graph in a full-width regular row is told
nothing, and silently gets no AVG or MAX.

#### This answers #152(c)

The open question was whether a Graph/Bars field genuinely *needs* a taller
full-width row or merely looks better in one. For the 530 Graph family the
answer is **it needs one, and the difference is content rather than
cosmetics**: below 5/3 units the sub-fields are gone.

That is the strongest possible case for the taller-slot annotation, and it
comes from Garmin's own fields, so the per-app/per-version objection that
complicates WindField does not apply. The threshold sits between 1 and 5/3
units, which in practice means **any full-width row in a layout other than a
plain 1-unit one**.

Still to check: whether the same two thresholds hold for the **Bars** family,
and whether the 840 — which scales rather than degrades — nonetheless also
withholds sub-fields in a 1-unit row. The 840 composite family did *not*
(all three values survived even at half width), so the 840 may have one
threshold, none, or two.

#### 368 breaks family uniformity, mildly

Form is uniform across the family — same plot, same two thresholds — but 368
shows **ASC/DESC** where the others show AVG/MAX. Sensible for elevation, and
it means the hypothesis holds for *shape* but not for *which sub-fields*. 368
was flagged in advance as a likely oddity; it is, in the smallest way it
could have been.

Worth noting what this costs: a warning that names the lost sub-fields cannot
hardcode "AVG and MAX". It needs the pair per field, or wording that avoids
naming them.

### Bars family — Edge 840 — MEASURED 2026-10-13

| id | field | S1 half | S2 full reg | S3 full 3/A | S4 full tall | S5 full screen |
|---|---|---|---|---|---|---|
| 347 | HR Bars | tiny **gauge** + bpm | **linear bars** + bpm/avg/max | **gauge** + bpm/avg/max | gauge + bpm/avg/max | gauge + bpm/avg/max |
| 348 | Speed Bars | tiny **gauge** + mph | **linear bars** + mph/avg/max | **gauge** + mph/avg/max | gauge + mph/avg/max | gauge + mph/avg/max |
| 349 | Cadence Bars | tiny **gauge** + rpm | **linear bars** + rpm/avg/max | **gauge** + rpm/avg/max | gauge + rpm/avg/max | gauge + rpm/avg/max |
| 350 | Power Bars | tiny **gauge** + W | **linear bars** + W/avg/max | **gauge** + W/avg/max | gauge + W/avg/max | gauge + W/avg/max |

Family-uniform across all four ids, no outlier.

### Bars family — Edge 530 — MEASURED 2026-10-13

| id | field | S1 half | S2 full reg | S3 full 3/A | S4 full tall | S5 full screen |
|---|---|---|---|---|---|---|
| 347 | HR Bars | `*`**Heart Rate** — number only | **bar** + HR + AVG/MAX | **gauge** + HR + AVG/MAX | gauge + HR + AVG/MAX | largest gauge + HR + AVG/MAX |
| 348 | Speed Bars | `*`**MPH** — number only | **bar** + MPH + AVG/MAX | **gauge** + MPH + AVG/MAX | gauge + MPH + AVG/MAX | largest gauge + MPH + AVG/MAX |
| 349 | Cadence Bars | `*`**Cadence** — number only | **bar** + RPM + AVG/MAX | **gauge** + RPM + AVG/MAX | gauge + RPM + AVG/MAX | largest gauge + RPM + AVG/MAX |
| 350 | Power Bars | `*`**Power** — number only | **bar** + W + AVG/MAX | **gauge** + W + AVG/MAX | gauge + W + AVG/MAX | largest gauge + W + AVG/MAX |

Family-uniform across all four ids, no outlier.

#### ⚠ FORM FOLLOWS ASPECT RATIO, NOT SIZE — and it is not monotonic

The most interesting result in this sheet. On **both** models the widget
shape goes **gauge → bar → gauge** as the slot grows:

| slot | shape | 840 | 530 |
|---|---|---|---|
| S1 half, 1 unit (smallish, squarish) | **gauge** | tiny gauge | *(degraded, no widget)* |
| S2 full, 1 unit (**wide and short**) | **linear bar** | linear bars | bar |
| S3–S5 full, taller | **gauge** | gauge | gauge |

A wide, short slot gets a horizontal bar; a squarer or taller one gets a
circular gauge. That is the slot's **shape** choosing the widget, not its
area — and it means "bigger is better" is false for this family in the
middle of the range. Nothing in the Graph or composite families does this.

It also retires the framing this sheet opened with. The 2026-10-09 note
described the Bars types as circular in larger slots and linear in smaller
full-width ones; that was right as far as it went, but the full sequence is
**not** a single transition — the gauge returns at the small end.

#### The `*` relabel rule: 3 of 4 predicted, and one real break

Doc rev 159 proposed that a 530 field too small for its widget relabels to
its **base metric** with a `*`. The Bars S1 column tests it on four fresh
fields:

| id | predicted | observed | |
|---|---|---|---|
| 347 | `* Heart Rate` | `*Heart Rate` | ✅ |
| 348 | `* Speed` | **`*MPH`** | ❌ **the UNIT, not the metric** |
| 349 | `* Cadence` | `*Cadence` | ✅ |
| 350 | `* Power` | `*Power` | ✅ |

Three held. **348 gives the unit rather than the name**, and it is not a
transcription slip — 349 in the same pass reads `Cadence`, not `RPM`, so the
distinction is being made deliberately. The rule is therefore *mostly* right
and needs qualifying: the degraded label is the base metric's name **except
for Speed, which shows its unit**. Why Speed alone does this is unknown, and
guessing would just be a nicer-sounding version of not knowing.

**Marker position is LEADING on all four**, matching id 23's `* Heart Rate`.

#### ⚠ And that contradicts the August record for the same field

`FIELD_ID_NAMES` names 348 from a 2026-08-11 transcription of **`Speed *`** —
marker *trailing*, label *`Speed`*. Today, same field, same model: **`*MPH`**
— marker *leading*, label *`MPH`*. Both differ.

Three possibilities, untested:

- August's transcription was loose on both counts, which is plausible given
  it was recording field *names* and treated the marker as noise
- a 530 firmware update changed the degraded label
- the label differs by slot size *within* the degraded range, and the two
  observations were at different sizes

Today's reading is the more careful one and is what this sheet records. The
August string is not corrected in `FIELD_ID_NAMES`, because that table holds
the **full-size** name (`Speed Bars`), which is unaffected either way — but
the discrepancy is logged because "both are real labels at different sizes"
is exactly what turned out to be true for id 23, and the same explanation
may apply here.

#### Sub-field thresholds differ BY FAMILY on the same model

Doc rev 158 established two thresholds for the 530 Graph family: width buys
the plot, height buys the sub-fields. **Bars does not follow that.**

| 530 family | widget appears | AVG/MAX appear |
|---|---|---|
| Graph | S2 | **S3** |
| Bars | S2 | **S2** |

So on one device, two families of graphical field have different sub-field
thresholds. Any warning has to be per-family, not a single rule about
graphical fields — and `GRAPH_OR_BARS_FIELD_IDS`, which lumps them into one
set, cannot express that. This is a second reason #153 needs restructuring,
independent of the per-model one.

On the 840 both families lose their sub-fields only at S1, so the 840 has
one threshold per family and the 530 has one for Bars and two for Graph.

## Hypothesis worth trying to break

**Form depends on the family and the slot size, not on which metric it is** —
a Power Graph and a Speed Graph should draw the same shape in the same slot,
since the widget is the same and only the data source differs.

If that holds, the cheap route is: fill **346 Power Graph** and **350 Power
Bars** across all five columns, then fill only the **S1** and **S2** cells
for the rest. Six fewer screens to build.

It is written here as a hypothesis and not assumed, because the way to use it
is to **try to falsify it**: the S1/S2 spot-checks are that test. If any
sibling disagrees with its family representative, the shortcut is void and the
full grid is needed.

Two candidates for behaving unlike their families, which is why they are
listed in the Graph block rather than folded into one representative:

- **23 HR Zone Graph** — a banded zone display, not a time plot
- **368 Elevation Graph** — plots distance rather than time

## What the toolkit actually needs from this

Less than the full grid. `graph_bars_warnings()` has to answer one question:
*given this field in this slot on this model, is anything lost, and what do we
say?* That needs, per field per model, only the **smallest slot at which it
still draws its widget** — the threshold. Everything above it is confirmation
and everything below it is the warning case.

So a half-finished sheet is still useful, as long as what is filled in is
filled in for both models. A column complete on the 840 and blank on the 530
tells us nothing we can act on, because the whole point is that they differ.

## New fields found along the way

Kept in its own section on purpose. The matrix above records **rendering
behaviour of known fields**; this records **the existence of unknown ones**.
They are different kinds of claim and folding them together would blur both —
but splitting them across two files while standing at the device is friction,
so they share a file and not a table.

Anything here gets promoted into `FIELD_ID_NAMES` afterwards, as its own
change, with the id confirmed by placement rather than by the menu.

### Found 2026-10-09

| id | menu category | label on device | what distinguishes it | confirmed by |
|---|---|---|---|---|
| 351 | Graphical | `Heart Rate` | live numeric readout + **AVG** and **MAX** sub-fields | Doug, 2026-10-09 |
| 352 | Graphical | `Speed` | live numeric readout + **AVG** and **MAX** sub-fields | Doug, 2026-10-09 |
| 353 | Graphical | `Cadence` | live numeric readout + **AVG** and **MAX** sub-fields | Doug, 2026-10-09 |
| 354 | Graphical | `Power` | live numeric readout + **AVG** and **MAX** sub-fields | Doug, 2026-10-09 |

**Correction, same day:** an earlier note in this file said 352's sub-fields
were **Min** and **Max**. They are **AVG and MAX**. Doug's own correction;
the wrong pair was recorded here first and is fixed rather than left to be
read later as measured.

**Present on the 530 as well** (Doug, 2026-10-09), so `(Graphical)` is not an
840-ism and the name needs no per-model split.

**The numbering prediction held exactly** — 351 HR, 352 Speed, 353 Cadence,
354 Power, the same metric order as 343–346 (Graph) and 347–350 (Bars). Three
families of four, in register:

| | HR | Speed | Cadence | Power |
|---|---|---|---|---|
| Graph | 343 | 344 | 345 | 346 |
| Bars | 347 | 348 | 349 | 350 |
| live + AVG/MAX | **351** | **352** | **353** | **354** |

Being right does not retroactively make the arithmetic evidence: the ids came
from the device, which is the only reason they can be written down. Had the
family been ordered differently, the pattern would have produced four
confident wrong entries — and 355–367 are still unknown, so the next guess
starts from zero again.

### These four are NOT graph or bar widgets

Important for #153 and for the tables above. The device files them under the
**Graphical** menu category, but their content is **three numbers** — a live
readout plus AVG and MAX. Nothing is plotted.

So they do **not** belong in `GRAPH_OR_BARS_FIELD_IDS`: the message that
field needs "full width to render as a graph/bar, not plain text" would be
meaningless for a field that is plain text by design.

What they plausibly have instead is a **third size behaviour**, and it is
the sharpest open question in this whole sheet:

> **In a half-width slot, does a composite field still show AVG and MAX, or
> does it drop the sub-fields and show only the live number?**

If it drops them, then at half width id 352 is visually **indistinguishable
from id 48 "Speed"** — the user has given up the whole reason for choosing
it and has no way to tell. That is a genuine warning case, and a different
one from both existing tiers:

| tier | behaviour |
|---|---|
| `GRAPH_OR_BARS_FIELD_IDS` | widget deprecates to text |
| `SMALL_SLOT_UNUSABLE_FIELD_IDS` | draws fully, too small to use |
| **this, if confirmed** | **draws legibly, silently loses its extra data** |

No constant for it yet, and none should be invented before the measurement —
that is what the table below is for.

### ANSWERED 2026-10-09 — and it is a single threshold

Doug: *"When these are in a Half width data field, they revert to just the
primary data type single numerical field and the label gets the `*`, in the
editor view. In all other data field sizes, they show the main and 2
sub-fields, it's just the size of the fonts within the data field that
changes getting larger as the space allows."*

So the question above is settled, and the answer is the simplest possible
shape:

| slot | behaviour |
|---|---|
| **S1** half-width | **reverts to the primary number alone**; editor marks the label `*` |
| S2 full regular | main + AVG + MAX |
| S3 full 3/A | main + AVG + MAX, larger fonts |
| S4 full tall | main + AVG + MAX, larger fonts |
| S5 full screen | main + AVG + MAX, largest fonts |

**One threshold, between S1 and S2.** Above it nothing changes but font
size — no reflow, no dropped sub-field, no change of form. That is exactly
the "smallest slot at which it still works" the toolkit needs, and it means
the composite table below collapses to one row per model rather than five
columns of distinct behaviour.

It also confirms the consequence that made this worth asking: **at half
width, 352 shows one number with no sub-fields — visually identical to id 48
"Speed".** A user who chose the composite field for its AVG and MAX gets
neither, and the only thing that says so is the editor's `*`.

> ### RESULT 2026-10-09: the models diverge, and the `*` question is now
> ### probably MOOT rather than answered
>
> Doug checked the 840: *"for those 4 new data field IDs, on the 840, they
> scale all the way down even in a half width data field, it's just that the
> font is very small, but they don't revert to the primary data type single
> numeral only nor do they display a `*` with the label."*
>
> **What this settles — and it is the firmest result in this file:**
>
> | | half-width behaviour | editor `*` |
> |---|---|---|
> | **Edge 530** | reverts to the primary number alone | yes |
> | **Edge 840** | keeps all three values, very small font | no |
>
> That is the **second independent family** showing the same divergence in
> the same direction. Taken with the graph/bars finding:
>
> | family | Edge 530 | Edge 840 |
> |---|---|---|
> | Graph / Bars | degrades to plain text | scales down, still draws |
> | composite (351–354) | degrades to primary value | scales down, all three |
>
> So this is not a quirk of one widget. The two devices appear to follow
> **different rendering philosophies**: the 530 *degrades* content that will
> not fit, the 840 *scales* it. Two families agreeing is a far stronger
> basis for #153's per-model split than one was.
>
> **What this does NOT settle: whether the 840's editor has a `*` at all.**
> The test was designed to separate the two readings below and cannot,
> because both predict precisely what was seen:
>
> - **(a)** the 840 has no marker → no `*`
> - **(b)** the 840 has the marker but stays silent when nothing is lost →
>   no `*`, *because nothing was lost*
>
> Identical predictions. The 840 field did not degrade, so there was nothing
> for a marker to mark. An observation that comes out the same under both
> hypotheses is evidence for neither — the same fault as a comparison that
> agrees with itself (Doc rev 155).
>
> **Separating them needs an 840 field that genuinely loses something in
> some slot, and no such field is known.** The graph/bar family scales; the
> composite family scales; `SMALL_SLOT_UNUSABLE_FIELD_IDS` (Compass, Map)
> draws fully and is merely tiny. If the 840 never degrades anything, then
> (a) and (b) are not just empirically indistinguishable, they are
> **behaviourally equivalent** — a marker that can never fire and an absent
> marker are the same thing to any user and to this toolkit.
>
> Which makes this a question worth **closing as moot** rather than chasing,
> unless an 840 field that drops content turns up on its own. Recording it
> that way deliberately: "undecidable and harmless" is a real answer, and
> better than leaving an open item that implies work outstanding.
>
> ### Superseded — the framing before the 840 check
>
> Doug, 2026-10-09, asked which device: *"I was looking at the 530 for that
> part, let me double check for those particular data field types on the 840
> before I say it only occurs on the 530."*
>
> So the observation above — the `*` on a half-width composite field — is a
> **530** observation. Whether the 840's editor does the same for *these*
> fields is **not yet known**, and declining to assert it either way is the
> right call: the 2026-10-09 pass found no `*` on any 840 **graph or bar**
> field, which says nothing about the **composite** family. Different
> fields, different question.
>
> Two readings remain, and they are not close:
>
> **(a) the 840 shows no `*` here either.** Then `*` is a 530-only editor
> feature, the 840 has no editor warning at all, and this is consistent with
> everything so far while adding nothing new.
>
> **(b) the 840 does show `*` on these.** Then the 840's editor *does* use
> the marker, and the whole story unifies into one rule:
>
> > **`*` means "this field loses something in this slot" — on both
> > devices.**
>
> Under (b), the absence of `*` on 840 graph fields is not a missing
> feature, it is the marker correctly staying silent **because those fields
> do not degrade on the 840**. The device's own editor would then be
> reporting exactly the fact `graph_bars_warnings()` is trying to compute,
> on both models, and the 530-vs-840 difference in #153 would be a
> difference in *field behaviour* rather than in *editor behaviour*.
>
> (b) is much the more attractive model — one rule covering both devices,
> with the device's own editor reporting the very fact
> `graph_bars_warnings()` tries to compute. **That attractiveness is the
> reason to be careful with it.** A hypothesis one wants to be true is the
> kind that gets read into a thin observation, and the cheapest version of
> that mistake here is concluding "840 shows no `*`" from having looked at
> 840 graph fields rather than 840 composite fields.
>
> **The check:** place a composite field (352 will do) in a half-width slot
> on the **840** and read the editor label. Either answer is a finding.
>
> Record `*` presence per device in its own column below — it is an
> observation in its own right, not a detail of the rendering.

### Composite family — what survives at each slot size

Cell vocabulary: `3up` all three values shown · `live+1` live plus one
sub-field (say which) · `live` live number only, sub-fields gone ·
`number` same as `live` but also no label · `n/a` not offered.

#### Edge 840 — MEASURED 2026-10-09, all four

| id | field | S1 half | `*` at S1? | S2-S5 full width | family matches? |
|---|---|---|---|---|---|
| 351 | Heart Rate (Graphical) | `3up` tiny font | no | `3up` | yes |
| 352 | Speed (Graphical) | `3up` tiny font | no | `3up` | yes |
| 353 | Cadence (Graphical) | `3up` tiny font | no | `3up` | yes |
| 354 | Power (Graphical) | `3up` tiny font | no | `3up` | yes |

Doug checked all four, not one and an assumption — so family uniformity is
measured here rather than inferred. Nothing degrades at any size on this
model; only the font changes.

#### Edge 530 — MEASURED 2026-10-13, all four

| id | field | S1 half | `*` at S1? | S2-S5 full width | family matches? |
|---|---|---|---|---|---|
| 351 | Heart Rate (Graphical) | `*`+label, single number | yes | no label; value + **BPM**, AVG and MAX sections | yes |
| 352 | Speed (Graphical) | `*`+label, single number | yes | no label; value + **MPH**, AVG and MAX sections | yes |
| 353 | Cadence (Graphical) | `*`+label, single number | yes | no label; value + **RPM**, AVG and MAX sections | yes |
| 354 | Power (Graphical) | `*`+label, single number | yes | no label; value + **W**, AVG and MAX sections | yes |

Doug, 2026-10-13: *"All of the above have the `*<field type>` label in the
half width data field and a single number field for the primary type. All of
the other data field sizes have no label, [and a] larger section for the
primary type (Power has W for Watts, Speed has MPH, Cadence has RPM and Heart
Rate has BPM) and then the 2 secondary sections of the data field have the
AVG and MAX numerical area."*

*(One word in the original — "cable" — is almost certainly a typo; the
sentence reads as intended without it. Flagged rather than silently
smoothed.)*

#### The composite family LOSES its label as it grows

Worth pulling out, because it runs opposite to the Graph family. At S1 these
fields show `*` + a text label + one number. From S2 up they show **no label
at all** — just the value with its unit, plus the AVG and MAX sections.

So as the slot grows: Graph fields *gain* a label (id 23 goes
`HEART RATE` → `HR Zone Graph`), composite fields *lose* theirs. The unit
carries the identification instead, which is why the unit is worth recording
per field rather than treated as decoration.

#### ⚠ This sharpens the `MPH` exception into a cheap, decisive question

The Bars pass found 348 Speed Bars labelled **`*MPH`** at S1 — the unit,
where its three siblings showed the metric name. The open question was
whether that exception belongs to **Speed** or to the **Bars family**.

These four give the test, and it costs one look:

> **At S1, does 352 read `*Speed` or `*MPH`?**
>
> - **`*Speed`** → the exception is **Bars-specific**. Speed behaves
>   normally elsewhere, and only the Bars family substitutes the unit.
> - **`*MPH`** → the exception is **Speed-specific**, and the relabel rule
>   becomes "base metric name, except Speed, which always shows its unit".

Doug's note writes the S1 label generically as `*<field type>`, so it does
not settle which. Everything else in this block is measured; this one cell
is not, and it is the difference between two quite different rules.

The same question applies to **344 Speed Graph** on the 530, whose S1 text
is also still unrecorded. If 352 and 344 disagree, the exception is narrower
than either reading.

The 530 row for 352 is from the observation that opened this section. The
other three are blank on purpose: the 840 pass showed the family behaving
uniformly *on the 840*, which is not evidence about the 530. Uniformity has
to be checked per model, since the models are exactly what differ here.

The rendering question is already answered for whichever device Doug was
looking at, so what is left here is narrow:

1. **the `*` column, on the 840 specifically** — the unresolved item above,
   and the highest-value cell in this file
2. **family uniformity** — do all four behave like 352, or does one differ
3. `n/a` for any the device does not offer

`S2-S5` is one column rather than four because the only difference across
those sizes is font size. If any field turns out to break that — a
sub-field dropping at S2 but not S4, say — split the column rather than
forcing the observation into it.

**352 will be the FIRST name collision in `FIELD_ID_NAMES`** — 206 entries,
206 distinct display strings, zero collisions today. That is why no
convention exists for this cause yet, and it is also the moment to add a
uniqueness check: no two entries may share a display string unless at least
one is in `AMBIGUOUS_DEVICE_LABELS`. Worth bundling with the 352 commit
rather than added speculatively now.

**352 is a name collision, not a new name.** The device calls it `Speed` and
id 48 is also `Speed`. Proposed handling, using machinery that already
exists rather than a new convention:

- `FIELD_ID_NAMES[352] = "Speed (Graphical)"` — the device's own menu
  category as the disambiguator, since that is how a user will look for it
- `AMBIGUOUS_DEVICE_LABELS[352] = "Speed"` — so the picker row reads
  `Speed (Graphical)  (id=352, shows as "Speed")`

That constant's comment gives two reasons a field belongs there (an icon
carries part of the name; there is no label at all). This is a **third
cause with the same effect**: the text is ambiguous because it collides with
another field's text, and a list box cannot disambiguate two rows both
reading "Speed". Worth adding to that comment when 352 lands.

Deliberately NOT named for its widget form — no `Gauge`, no `Dial`. The form
is what the matrix above is measuring, and a name that encodes an unverified
guess is how `Speed *` briefly became a field name in August.

### ⚠ The blind spot that hid 352, which is bigger than 352

Doug, 2026-10-09: *"not sure how I missed it, I probably assumed, that since
it had the same name in the editor, that it was just the regular Speed data
field."*

That is a **method fault in every census pass so far**, not an oversight.
The build sheets were assembled by reading menu labels and listing the
unfamiliar ones. A field whose menu label duplicates a known field's label
is invisible to that method — it gets skipped as "already known", and the
skip **leaves no trace**: it is not in `KNOWN_UNRESOLVED_IDS` (which is
empty), not on `EDGE840_NEW_FIELDS_CHECKLIST.md`, not counted anywhere.

So "41/41 resolved" and "zero unresolved ids" are true *relative to a list
built from labels*, and label de-duplication is the step where fields fell
out silently. The familiar failure here in a new place: an absent record
read as an absent thing.

**The rule, for this pass and every future one: never skip a menu entry
because its label is already known.** Only a placed-and-pulled id can tell
you it is the same field. Placing a duplicate you already have costs one
slot; assuming costs a gap nothing can detect.

Unknown ids still sit in three contiguous blocks near this family — 330–342
(13), 351–367 (17) and 369–399 (31). Those are not all graphical fields, but
they are where a same-named sibling would hide.

### If you find more

Add a row to the table above. Useful to capture, in order of value:

1. **the id** — from a pull after placing it, not from the menu
2. **the menu category** it lives under
3. **the exact label** rendered on the screen, not the menu text (294 says
   `Trainer Controls` in the menu and renders `Resistance`)
4. **what makes it distinct** from the similarly-named field, which for this
   whole category seems to be an extra data area
5. whether it collides with an existing name — if so it wants the same
   `AMBIGUOUS_DEVICE_LABELS` treatment as 352

A field you cannot get an id for is still worth a row with the id left blank.
"Exists, unidentified" is more useful than nothing, and it bounds what the
Graphical category contains.

## Blank means unchecked

As everywhere else in this project: an empty cell is **not** "same as the one
above it". If a permutation is not worth the time, leave it blank and it stays
honestly unknown rather than becoming a guess that later reads as measured.
