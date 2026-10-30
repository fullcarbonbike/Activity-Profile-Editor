# Test plan — #106, `fit_odometer.py` 1.0.0

> # ✅ ALL SECTIONS PASS — 2026-10-30, Edge 530
>
> A–D complete. Every write landed exactly; nothing unnamed moved.
> **D3 answered itself in section A** — Doug rode between the baseline
> and the first pull, and record 0 moved by exactly that ride. Results
> are in each section; the full writeup is Doc rev 198.

*Built 2026-10-30. Edge 530. The CLI half is already verified
headlessly — 13 guards, a four-profile reset proven to leave seven
records byte-identical. **None of that tells us what the device does
with the file**, which is the whole of this plan.*

---

## ⚠ Read this before section A

**You can only see ONE of the four fields on the device.** The
odometer data field displays distance. Time, calories and rides have
no display you have found, so their landing can only be confirmed by
pulling the file back.

That is not a flaw in the plan, but it does mean a step that says
"the odometer reads X" has verified **a quarter** of the write. Each
step below states which of the two instruments it uses:

| instrument | what it can show |
|---|---|
| **screen** | distance only, live, on a `ROAD_<xx>` profile's odometer field |
| **file** | all four fields, plus record 0, plus whether anything else moved |

A step with no file pull proves less than it looks like.

**Use a throwaway profile.** `ROAD_T1`, `ROAD A1`, `ROAD A2` and
`Sandbox` are all zeroed and expendable. **Do not point anything at
`ROAD`** until section D passes — it holds real riding that exists
nowhere else.

**Back up `Totals.fit` by hand first.** This tool never writes in
place, so your input is safe, but the *device's* copy is about to be
replaced and there is no Restore-from-Backup path for totals.

---

## What is actually unknown

Rev 118 proved a `Totals.fit` written through `NewFiles` is accepted.
That was **one record, one field**. Everything below is untested:

| question | why it matters |
|---|---|
| does a **multi-record** edit import cleanly? | the January reset writes four at once |
| does the import disturb **record 0**? | it is unnamed, unexplained, and this tool refuses to touch it |
| does the device **resume accumulating** from a written value? | rev 168 says it adds to what is written; never checked after a reset |
| does a reset **survive a ride**? | the real failure would be the device restoring its own number afterwards |

---

## A. One field, one profile — ✅ PASS

Re-establishes rev 118 with this tool rather than assuming it carries.

| # | do | instrument | expect |
|---|---|---|---|
| A1 | `set` a distance on `ROAD_T1`, e.g. `--distance 100mi` | — | tool reports verified, 10 records untouched |
| A2 | copy to `NewFiles` as `Totals.fit`, restart | — | — |
| A3 | ride-screen odometer on `ROAD_T1` | **screen** | reads ~100 mi |
| A4 | pull `Totals.fit` back, send it to me | **file** | `ROAD_T1` distance = 100 mi, nothing else moved |

**A4 is not optional.** A3 alone cannot distinguish "the write
landed" from "the write landed and something else broke."

## B. All four fields, one profile — ✅ PASS

| # | do | instrument | expect |
|---|---|---|---|
| B1 | `set` all four on `ROAD A1` — distance, time, calories, rides | — | — |
| B2 | deploy, restart | — | — |
| B3 | odometer field | **screen** | reads the distance you set |
| B4 | pull and send | **file** | **all four** match; `ROAD_T1` from section A still intact |

B4 is the only way the other three fields are ever confirmed.

## C. Four profiles at once — ✅ PASS

The case the multi-profile feature exists for, and the one rev 118
says nothing about.

| # | do | instrument | expect |
|---|---|---|---|
| C1 | `reset --profile ROAD_T1 --profile "ROAD A1" --profile "ROAD A2" --profile Sandbox` | — | preview lists four, `Untouched:` names the rest **including ROAD** |
| C2 | deploy, restart | — | — |
| C3 | odometer on any of the four | **screen** | reads 0 |
| C4 | pull and send | **file** | all four zeroed; **ROAD, INDOOR, GRAVEL, MOUNTAIN unchanged**; record 0 unchanged |

**C4 is the most important file in this plan.** If a multi-record
import is going to fail, this is where — and "the odometer reads 0"
would look identical whether the other three records survived or not.

## D. Does it stick, and does it resume? — ✅ PASS

Everything above tests the import. This tests the *device*.

| # | do | instrument | expect |
|---|---|---|---|
| D1 | after C, ride a short distance on one reset profile | **screen** | odometer counts up from 0 |
| D2 | pull `Totals.fit` | **file** | that profile ≈ the ride; the other three still 0 |
| D3 | compare record 0 before C and after D1 | **file** | did it move by the ride distance, by more, or not at all? |

**D3 is a genuine experiment, not a check.** Three outcomes, all
informative:

- **record 0 grew by the ride** → it is a live device-level
  accumulator, and the "independent total" reading is supported
- **record 0 unchanged** → it is something else entirely
- **record 0 jumped by a reset profile's old value** → the device
  reconciles, and resetting a profile has side effects on it

Any answer is worth having. None of them changes the tool.

## E. Nothing else in the file moved

| # | do | instrument | expect |
|---|---|---|---|
| E1 | on every pull above, check the profile **names** and **sport** values | **file** | identical to before — this tool never writes them |
| E2 | check the device still shows all its profiles normally | **screen** | nothing missing or renamed |

I check E1 automatically on each file you send; it is listed so it is
not forgotten if someone runs this plan without me.

---

## Pass criteria — ALL MET (2026-10-30)

| | criterion | result |
|---|---|---|
| **A4** | a single-field write lands, nothing else moves | **pass** — 160,934 m exact |
| **B4** | all four fields land | **pass** — all four exact, to the unit |
| **C4** | four records at once, untouched ones proven untouched | **pass** — ROAD/INDOOR/GRAVEL/MOUNTAIN and record 0 all unchanged |
| **D1** | the device resumes from the written value | **pass** — a reset profile counted up from 0 |

**D3 had no pass criterion, and produced the headline finding.**
Outcome one of the three listed: record 0 grew by exactly the ride,
twice, in stored units — matching the ridden profile field for field
each time. The second ride was 68 m and 94 s, which makes it the
cleaner proof: a delta that small cannot be rounding. It never
moved for any toolkit write.

### What the plan did not anticipate

**An unrelated forum thread turned out to be testable here.** Its
accepted answer says the first record must equal the sum of the
others. Five consecutive working device states from this plan say
otherwise — they are never equal, and after section B the sum
*exceeded* record 0 by 236 miles with no ill effect. See Doc rev 198;
the likely real cause in that thread was a structurally rebuilt file,
which is exactly what a byte-level patcher cannot produce.

## If something goes wrong

Send the pulled file rather than describing it. Every useful
conclusion in this project came from diffing one, and three wrong
conclusions came from reasoning about one that had not been sent.

Restoring: copy your hand-made backup of `Totals.fit` into `NewFiles`
and restart. There is no automatic undo for this file — it is the one
write path in the toolkit with no Restore-from-Backup behind it, which
is itself worth remembering before pointing it at `ROAD`.

## Not covered, and deliberately

- **The 840.** Same tool, same file format, but no second device
  needed to establish the behaviour. If the 530 answers these
  questions the 840 almost certainly matches, and "almost certainly"
  is honest here in a way it was not for the screen-layout work, where
  the two models genuinely differed.
- **Record 0 as an editable target.** The tool refuses it. D3 observes
  it; nothing writes it.
- **Whether Connect re-syncs any of this back.** Out of scope, and the
  answer would not change what the tool does.
