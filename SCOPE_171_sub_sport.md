# Scope — #171, changing a cloned profile's sport type

*Scoping only, 2026-11-06, at Doug's request. Nothing built, nothing
changed. Measured against the existing corpus; the open questions are
named rather than guessed.*

---

## 1. The short answer to the motivating question

Doug's framing: clone `ROAD`, make the clone a different sport, so
the road bike and the gravel bike keep **separate odometers**.

**The odometer part is already solved, and needs no sport change at
all.** `Totals.fit` records are keyed by **profile NAME** — that is
established across revs 198–202, including the cross-device sync
which matched on name. Two profiles called `ROAD` and `GRAVEL`
already have independent totals regardless of their sport fields.
Doug's own 530 demonstrates it: both exist, with very different
mileages, today.

So the real question is not "how do I get separate odometers" but
**"what else does the sport field actually control?"** — which is
worth answering, because the answer is not nothing.

## 2. What the field actually is — measured, not assumed

Scanning every profile in the corpus, **`sport` (mesg 12 field 0) is
`2` on all of them.** It never varies. The field that distinguishes
profile types is **`sub_sport` (field 1)**:

| sub_sport | SDK name | filename prefix the device generates |
|---|---|---|
| 6 | `indoor_cycling` | `CyclingIndoor_Cycle…` |
| 7 | `road` | `CyclingRoad…` |
| 8 | `mountain` | `CyclingMountain…` |
| 11 | `cyclocross` | `CyclingCyclocross…` |
| 28 | `e_bike_fitness` | `Cycling…` — **prefix empty** |

**This refines Doc rev 187.** The rule was recorded as
`Cycling<Sport><DisplayName>.fit`. The middle segment is the
**sub_sport** label, not `sport` — `sport` is always "Cycling" and
contributes the constant prefix. Worth correcting in the notes
whether or not this item is ever built.

**`e_bike_fitness` produces an empty middle segment.** Either the
device has no filename label for that sub_sport, or it maps to blank
deliberately. One observation, not explained.

**`gravel_cycling` is sub_sport 46** in the FIT SDK. Also present:
`e_bike_mountain` 47, `commuting` 48, `mixed_surface` 49,
`hand_cycling` 12, `track_cycling` 13.

## 3. What changing it would plausibly buy

Not the odometer. More likely:

- **The activity type reported to Garmin Connect.** This connects to
  something already observed: Connect returned three different totals
  for "Road", "Road Cycling" and "Cycling" over what Doug considered
  the same riding. If his `GRAVEL` profile is sub_sport 7 (`road`) —
  unknown, see below — its rides would log as road, which would
  explain some of that spread.
- **The generated filename**, per the table above. Cosmetic, since
  the device renames on import anyway (#170).
- **Possibly on-device defaults or available features.** Untested.

## 4. ANSWERED 2026-11-06 — the device supports gravel natively

Doug's `CyclingGRAVEL.fit`, from the 530:

```
sport_mesgs[0].name      = 'GRAVEL'
sport_mesgs[0].sport     = 'cycling'
sport_mesgs[0].sub_sport = 'gravel_cycling'
```

**So the step-1 question is closed: the device creates and uses
sub_sport 46 by itself.** Writing it is not inventing a value the
firmware has never seen.

*(An earlier draft of this scope said the profile "has never been
pulled". What was true is that it is not among the files in this
session's corpus — Doug has it. Stating a fact about the corpus as a
fact about the world is the same error as revs 189 and 201, in a
smaller costume.)*

### ⚠ And the filename rule has holes

The file is `CyclingGRAVEL.fit` — **not** `CyclingGravel_CyclingGRAVEL.fit`.
With sub_sport 46 the device emits an **empty middle segment**, just
as `e_bike_fitness` (28) does.

So rev 187's `Cycling<SubSport><DisplayName>.fit` holds only for the
sub_sports the device has a filename label for:

| sub_sport | middle segment |
|---|---|
| 6, 7, 8, 11 | `Indoor_Cycle`, `Road`, `Mountain`, `Cyclocross` |
| **28, 46** | **empty** |

Not a problem for the toolkit — nothing depends on predicting the
name, and #170 removed the last thing that did. Worth recording
because the rule reads as universal and is not.

### What this does to the item's motivation

Not the odometer — that was already solved by profile name. The real
value is **cloning a full screen set into a correctly-typed
profile**:

- creating a Gravel profile **on-device** gets the right sub_sport
  but starts from the stock screen set
- **cloning `ROAD`** carries all its screens but also carries
  sub_sport 7, making it a road profile wearing a gravel name
- Favorites move screens one at a time — fine for one, tedious for a
  full set

So `--sub-sport` would collapse "clone the screens I spent time on"
and "make it the right type" into one step. **That is a real gap**,
and my first pass undersold it by assuming the odometer was the
point.

## 4b. ⚠ Doug's gear tracking raises the stakes

Doug tracks SRAM derailleur battery usage **per bike** via Garmin
Connect, and relies on the profile he picks routing the ride to the
right category. **That setup works today.** Anything this item
changes has to not break it.

**Checked: nothing in mesg 12 references a bike or gear.** Every
field was examined across 68 profiles. The gear association lives on
**Connect's side**, not in the profile file — so the toolkit cannot
break it directly.

**And Doug has now described the chain directly.** Garmin Connect's
Goals page filters on top-level sport *plus* sub_sport — he selects
"Cycling" and then "Road Cycling" or "Gravel Cycling", and the
matching rides count against that bike's battery goal.

**So sub_sport is load-bearing, not cosmetic.** A profile carrying
the wrong sub_sport silently files its rides against the wrong goal.
That cuts both ways for this item: it is the reason the feature would
be useful, and the reason a careless write would be harmful.

**Resolved by section 4**: `GRAVEL` already carries 46, and Doug's
Goals tracking works. That is evidence 46 behaves correctly end to
end — device, Connect, and the goal filter — which is the best
possible starting point for writing it deliberately.

### A field identified along the way: mesg 12 field 10 is the profile COLOUR

Three bytes, one value per profile, inherited by clones:

| hex | R,G,B | |
|---|---|---|
| `0076be` | 0,118,190 | blue — every 530 `ROAD` clone (18 of them) |
| `0044f8` | 0,68,248 | blue — the 840 `ROAD` family |
| `f16125` | 241,97,37 | orange — `MOUNTAIN` |
| `00c8a0` | 0,200,160 | teal — a cyclocross profile |
| `00dcff` | 0,220,255 | cyan — an e-bike profile |
| `00b700` | 0,183,0 | green — `INDOOR` |

Inference from shape and clone-inheritance, not from a device label —
nobody has changed a colour on-device and re-pulled. Good enough to
record, not good enough to write.

**Not proposed as an editable.** It is a once-per-profile cosmetic
choice the device's own UI already offers.

## 5. The other open questions

| | |
|---|---|
| does the device **accept** a sub_sport it has no UI for? | unknown — it may reject, may display oddly, may be fine |
| does changing sub_sport on an existing profile **disturb anything else**? | unknown. Screens are keyed on `f10`, not sport, so layouts should be unaffected — but "should" |
| does it **affect the odometer record**? | expected no (name is the key), unverified |
| is sub_sport **writable at all** via `NewFiles` import? | **ANSWERED 2026-11-06 — YES.** Hand-patched `CyclingGRAVEL.fit` imported cleanly on the 840; screens, `message_index` and both Connect IQ fields intact, totals record untouched. Doc rev 204 |

That last one is the real technical risk. Changing a profile's *name*
in mesg 12 field 3 is proven (`fit_clone_profile`, many times).
Changing field 1 in the same message is a different field with
different semantics, and the device may well treat identity fields
as its own — the same posture it takes with `message_index`.

## 6. If it were built, the shape

Smallest useful version, consistent with how the rest of the toolkit
works:

```
fit_clone_profile.py  <in> <out> --name "GRAVEL" --sub-sport gravel_cycling
```

- accept the **SDK name**, not the number — `gravel_cycling`, not 46;
  a wrong integer here is silent and a wrong name is caught
- refuse any sub_sport outside a vetted cycling list; writing
  `apnea_diving` into a bike profile helps nobody

**The vetted list is settled (2026-11-06): it is the device's own
"Ride Type" menu — nine entries.** Doc rev 205 has the table. Not the
SDK's cycling-tagged eighteen; the other nine have no on-device UI to
express them. And the lookup must be a **table**, not a derivation —
only `indoor_cycling` and `gravel_cycling` follow the
`<label>_cycling` pattern; `road`, `mountain`, `cyclocross`,
`commuting`, `mixed_surface`, `e_bike_fitness` and `e_bike_mountain`
do not.

In the GUI the picker should show the device's labels — **Road,
Mountain, Indoor, Gravel, Cyclocross, Commute, Tour, Ebike,
Emountain** — since that is what the user sees on the device. The SDK
name stays internal.
- leave `sport` (field 0) alone entirely — it is 2 on every observed
  profile and nothing suggests it should change
- never write it as a *side effect* of a name change; it is opt-in

An `--sub-sport` on the existing clone tool is better than a new
tool: it is the same message, the same patch mechanism, and the
clone flow is exactly when you would want it.

**GUI: no.** This is a once-per-profile decision made at creation
time, and the CLI path already exists. Same reasoning that made #106
a CLI.

### ⚠ REVERSED 2026-11-06 — the GUI is the right home after all

Doug's framing: *"an option in the clone screen that would allow a
sub_sport change of the clone, if the user wanted to do what I'm
doing, clone an entire profile content over to use on a different
bike with a distinct cycling category."*

**He is right and the paragraph above was wrong.** The #106 analogy
does not transfer:

| | #106 odometer | #171 sub_sport |
|---|---|---|
| when you do it | occasionally, on its own | **during a clone** |
| is there a GUI flow already? | no | **yes — Clone Profile** |
| what it needs | numbers from Connect | a pick from a short list |

The reasoning that made #106 a CLI was that it had no natural home in
the GUI — it did not belong to any existing flow. `sub_sport` is the
opposite: the *only* time you would set it is the moment the Clone
Profile panel already has you. Sending the user to a terminal
mid-clone to do the second half of one operation is the worse design.

**So: a sub_sport picker in the Clone Profile panel**, defaulting to
the source's value so the current behaviour is unchanged unless asked
for. The CLI flag is still worth having underneath it — that is how
every other feature in the toolkit is built — but the GUI is the
primary surface, not a refusal.

## 7. Recommendation — revised 2026-11-06

Step 1 is answered, so the sequence shortens:

| step | cost | what it decides |
|---|---|---|
| ~~pull `GRAVEL`, check sub_sport~~ | — | **done: it is 46** |
| ~~1. hand-patch `ROAD` to sub_sport 46, import, restart~~ | — | **done: ACCEPTED, Doc rev 204** |
| ~~2. screens and Connect IQ fields survived?~~ | — | **done: all 31 screens, both CIQ fields render their app** |
| 2b. the profile's **type** as the device displays it | — | whether it is a real gravel profile or a confused road one |
| 3. one ride on it, then check the Connect goal it lands in | one ride | whether Connect honours it — the thing Doug actually cares about |
| 4. only then: build it | small | — |

**The gate is passed.** Step 1 was the one genuine unknown — mesg 12
field 1 had never been written by this project — and a hand-patched
file answered it without building anything, which is how #106 and
#170 were both de-risked.

**Step 3 is now the decision point.** 2b is a glance at a menu; 3 is
the claim the feature exists to serve.

**Step 3 matters more than it looks.** The device accepting the
write and Connect honouring it are different claims, and Doug's
battery goals depend on the second. "The profile says Gravel on the
device" would not establish it.

### If it is built

A **sub_sport picker in the GUI's Clone Profile panel**, defaulting to
the source profile's value, with `--sub-sport gravel_cycling` on
`fit_clone_profile.py` underneath it — SDK names only, restricted to a
vetted cycling list, never a side effect of a name change. See
section 6 and its 2026-11-06 reversal.

**And a guard worth adding**, now that the Goals chain is known: if
the clone's sub_sport differs from the source's, say so plainly in
the output. Someone cloning `ROAD` to make a gravel profile should
see that the type changed, because that is the part that silently
reroutes a year of battery tracking if it is wrong.

### ⚠ A second guard — added 2026-11-07, from Doc rev 206

The three fresh 840 templates (`COMMUTE`, `TOUR`, `EMOUNTAIN`) are
**not the same screen set as each other.** Each ride type has its own
tailored template: `EMOUNTAIN` leads with Grit and Flow and fills the
f10=25 screen with **Assist Mode** and **Smart Travel Range**, `TOUR`
carries Distance to Next and enables an extra screen, `COMMUTE`
carries Time of Day. Non-screen settings differ too (mesg 13, 70, 309
and four more mesg 12 fields).

**So a clone with a rewritten `sub_sport` is not equivalent to a
native profile of that type.** It is the source's screens and the
source's settings, wearing the destination's type.

That is precisely what Doug wants — keeping `ROAD`'s screens is the
entire point. But it is not what everyone will expect, and the gap is
invisible: a user who clones `ROAD` into an Ebike profile gets no
Assist Mode screen and no indication that a native one would have had
it.

**So the picker should say, when the chosen type differs from the
source's:** the screens come from the source profile, not from the
device's template for that type. One sentence, shown only when the
type actually changes.

This also kills a feature idea worth naming so it is not revisited
casually: **the toolkit cannot offer "make this a proper Gravel
profile"** in the sense of matching what the device would have built.
It has no copy of the device's templates, and they are per-model.
Cloning is the only thing on offer, and it should be described as
cloning.
