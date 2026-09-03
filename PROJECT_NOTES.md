# Activity Profile Editor for Garmin Edge

*Doc rev 99 — refreshed 2026-09-02.* **CONFIRMED: screen DISPLAY ORDER
is safe for a screen holding a device-dependent Connect IQ field --
only that screen's OWN count/array/layout is fragile.** Doug tested
this directly, on real hardware, as the last check before pushing the
CIQ guard fix as a release: moved a screen containing a working
WindField placement to a different position in the on-device screen
carousel (i.e. `swap_display_order()`/`--swap-order`, which swaps only
field 9 -- the creation-order stamp -- between two already-configured
screens) and it kept rendering correctly afterward. This is consistent
with, and narrows, the Doc rev 98 finding: the fragile state lives in
the screen's OWN field-array shape (f3 count / f7 field array / f8
layout), not in field 9 (display position) or the screen's
message_index/slot identity itself -- reordering which position a
screen appears in the on-device list never touches any of those three
fields, so it was never expected to be at risk, and now it's directly
confirmed rather than just inferred by omission. Practical note: this
also confirms the CIQ guard shipped in Doc rev 98 is scoped correctly
as-is -- `screen_has_device_dependent_ciq_field()` is only checked when
a write touches {3, 7, 8}, and `--swap-order` never goes through that
code path at all (it's a completely separate f9-only function), so it
was never blocked and didn't need to be. Prior rev (98, 2026-09-03)
follows.*

*Doc rev 98 — refreshed 2026-09-03.* **CORRECTION to Doc rev 97 + real
guard gap found and fixed, both via Doug's own real-hardware testing.**
Doc rev 97 stated this toolkit "can (via `patch_screen()`'s in-place
edits) MOVE [a Connect IQ field] to a different slot" -- that claim does
NOT hold up and should be read as superseded by this entry. Doug added
two ordinary fields (Cadence, %FTP) to a Clonebox screen that already
had a working Edge 3270 CIQ field (going from a 1-field to a 3-field
layout, CIQ field kept in the middle position, ID/value never itself
requested or changed) via the GUI's Add Field. On deploy, Edge 3270
rendered as Timer -- broken exactly like every failed fresh-introduction
attempt earlier in this investigation. In hindsight this is consistent
with, not contradicted by, evidence that predates Doc rev 97 itself:
the ROAD Screen 3 "value-only swap" test (Doc rev 95-96) had already
failed under the same toolkit-write mechanism. Doc rev 97's "can move
it" line was an overstatement not actually backed by a passing test --
flagged here rather than silently edited, per this file's own no-
rewrite discipline.

**Refined finding:** the real rule isn't "does this write's REQUESTED
field ids include a device-dependent CIQ id" (2026-09-02's guard, see
`DEVICE_DEPENDENT_CIQ_IDS` in `fit_dump.py`) -- it's "does this SLOT
CURRENTLY hold one, period." Any toolkit rewrite of that screen's
count (f3), field array (f7), or layout (f8) breaks the on-device
linkage, even when the CIQ field's own id/byte value/position isn't
what's changing, only OTHER fields around it are. Whatever actually
resolves this linkage on-device appears to get invalidated by any
toolkit-originated restructuring of the screen at all, not specifically
by touching the CIQ field's own bytes.

**Real gap found and fixed:** the 2026-09-02 guard only covered two
things -- `fit_patch.py --fields` refusing when a CIQ id was explicitly
REQUESTED, and `FieldPickerDialog` excluding CIQ ids from fresh
selection. Neither one protected the path Doug actually hit: the GUI's
`_apply_field_list()`/`_swap_fields()`/`on_layout_choice()` call
`patch_screen()` DIRECTLY and never route through `fit_patch.py`'s CLI
at all, so that guard simply never ran for Add/Remove Field, Move Up/
Down, Replace Field, or Layout A/B in the GUI -- only the CLI's
`--fields` had any protection, and only for the narrow "you typed 216
yourself" case. Fixed (2026-09-03) with a new, shared, single-source-
of-truth check -- `screen_has_device_dependent_ciq_field()` in
`fit_patch.py` -- that reads the slot's CURRENT on-disk field array
before any edit and hard-refuses (no override) if a device-dependent
CIQ id is already present, whenever the write would touch f3/f7/f8.
Wired into both `fit_patch.py`'s CLI (`--fields`, `--swap-fields`,
`--layout`, alongside the original request-side check, which still
catches the complementary "trying to freshly introduce one" case) and
directly into all six GUI call sites (`_apply_field_list`,
`_swap_fields`, `on_add_field`, `on_remove_field`, `on_change_type`,
`on_layout_choice`) -- the GUI checks are the ones that actually matter
here, since that's the path with no CLI guard behind it at all.

Practical upshot: once a screen has a device-dependent CIQ field on it
(currently just `{216}`), this toolkit now refuses to touch that
screen's field count, field list, or layout in any way, full stop --
not just refuses to introduce a fresh one. The GitHub Show and tell
post already published about this (2026-09-02) claimed toolkit
relocation works within a profile -- that line needs a follow-up
correction; not yet posted as of this entry. Prior rev (97,
2026-09-02) follows.*

*Doc rev 97 — refreshed 2026-09-02.* **WindField/Connect IQ investigation
(Doc rev 95-96) -- final refinement and toolkit code change shipped.**
Following Doc rev 96, Scott Beam (WindField's author) replied directly
and confirmed two things independently: the numeric field ID (216) is
"not anything I set in the code at all" (i.e., Garmin/firmware-assigned,
not app-author-controlled), and Garmin's on-device "Timer" fallback
(observed throughout this investigation whenever a toolkit-written CIQ
placement failed) is, in his words, "the default field that just shows
up whenever you uninstall any connectiq field" -- matching this
project's own independently-derived behavioral theory exactly. Doug
then ran the most direct test yet: installed a second, completely FREE
Connect IQ app ("Edge 3270," via the on-device editor, no license/
subscription involved) onto the same real device already running the
paid, currently-licensed WindField. Result: Edge 3270 shows up as a
new CONNECTIQ menu entry with its own distinct mesg_num=170 UUID
(`a2b59c28649c480294771978b38bdf9`, vs. WindField's own constant
`c7c508c824a44bcca2886f928a81b9c0`) -- but the SAME numeric field ID,
216, that previously meant WindField. This is the clearest evidence
yet that 216 is a device-local, install-order-dependent SLOT number,
not a stable per-app identity, and -- because a totally free app shows
the identical mechanism as a paid/licensed one -- it also rules out
the "licensing/anti-piracy" framing floated earlier: this is general
Connect IQ app-to-slot linking architecture, not licensing-specific.

A direct cross-file UUID survey (every WindField-active file this
project has on hand, every screen/position/layout it's ever occupied)
independently confirmed the mesg_num=170 UUID is CONSTANT per app,
with zero positional variation ever observed -- ruling out any
per-placement encoding this toolkit could exploit. Doug also raised a
legitimate methodological challenge, drawing a direct parallel to this
project's own earlier f10/screen-type mystery (once suspected to be a
firmware limitation before the real answer turned up in overlooked raw
bytes): was something in the file still being dismissed too early,
given that a toolkit-built CLONE (a file "Garmin has never seen") CAN
carry over a working CIQ field? Investigated seriously rather than
waved off -- but the proposed next rigorous test (an exact-byte
UUID/mesg170 transplant) turned out to be redundant with a test already
run and already failed (the ROAD Screen 3 value-only swap, which used
100% native, unapproximated mesg170 data). No new file-level lever was
found. Conclusion stands, now on firmer footing: this toolkit can
reliably PRESERVE an existing CIQ field placement through a whole-
profile Clone, and can (via `patch_screen()`'s in-place edits) MOVE one
to a different slot the same profile already has it in via the
on-device editor's own prior write -- but cannot ORIGINATE one in a
slot that has never held it, because whatever actually gates this
happens against device-side state (Garmin's own local record of
installed CIQ apps, checked at render time), not anything reconstructable
purely from file bytes. This remains an inference from consistent
behavioral testing across ~10+ independent attempts, not a decompiled
or firmware-documented mechanism.

**Toolkit code change shipped as a direct result (2026-09-02, Doug's
explicit request):** field IDs in this category get special, generic
handling instead of a specific (and now confirmed occasionally WRONG)
app name. `fit_dump.py` adds a new, deliberately growable
`DEVICE_DEPENDENT_CIQ_IDS` set (currently `{216}`) and renames that
entry's display name from "WindField Widget" to "CIQ Data Field" --
this is a read-only-display change only, `FIELD_ID_NAMES` itself and
everywhere that reads it directly (this file's own `screens` dump
output, the GUI's ViewScreensPanel/EditScreenPanel) are unaffected, so
an already-configured CIQ field keeps displaying correctly with its
new generic name. Two write paths now hard-refuse (no `--force`
override, same posture as `NO_SHOW_TOGGLE_TYPES`) rather than silently
producing a file that looks right but doesn't work on-device:
`fit_patch.py`'s `--fields` CLI errors out immediately if asked to
write one of these IDs into a screen, and `gui_app.py`'s
`FieldPickerDialog` (the single choke point behind all 4 Add/Change
Field call sites) unconditionally excludes them from its selectable
list, unioned on top of whatever per-call `exclude_ids` was already
passed. README caveat update (from "licensing/entitlement" framing to
the more accurate general-architecture framing) drafted but not yet
committed to `README.md` as of this entry. Prior rev (96, 2026-09-02)
follows.*

*Doc rev 96 — refreshed 2026-09-02.* **WindField Widget investigation
(Doc rev 95) -- CONCLUDED, cross-checked against a second, independent
investigation with a larger file set. Root cause identified with high
confidence: WindField is a paid Connect IQ data field, and this
toolkit's `--fields`/`patch_screen()` write path cannot create whatever
device-side reference a Connect IQ field needs -- only Garmin's own
on-device editor can.** Doug ran the same problem, independently, through
a separate long-running session dedicated to this project's field-ID
census (which has access to many more of his real, long-lived profiles
than this thread ever saw -- including two not previously known to have
WindField configured: GRAVEL and a profile called "Tourtst"). That
session did real, careful work and found WindField is confirmed to be a
purchased/subscribed third-party Connect IQ app (~$15/year, via
WebSearch), not a native Garmin field -- consistent with, and the
likely ultimate explanation for, everything found in this thread. It
also found a real, previously-unnoticed structural fact: a global
message type 170 (16-byte value + a small second field) appears
alongside every WindField-active screen it checked, and initially
concluded -- based on a clean correlation across the 28 files it had
access to (present in all 4 WindField-active files it knew of, absent
from all 24 others) -- that mesg 170 was a Connect-IQ-app "link record"
`--fields` fails to create.

**That specific theory does not survive contact with this thread's own
evidence, and the two threads' findings needed to be reconciled rather
than taken at face value from either side alone.** This thread's very
first successful fix -- `CyclingRoadClonebox_padding_test.fit`, deployed
as `CyclingRoadClonebox.fit` and confirmed by Doug on real hardware to
show WindField correctly on Screens 2 and 3 -- has NO message 170 at
all (re-verified directly, 138 messages, `mesg_num=170` absent). That
file was never uploaded to the other session, so its 28-file survey
never had the counter-example on hand. Re-integrated: message 170 most
likely correlates with "this specific file has been saved via the
on-device editor at some point in its life" in general (true of GRAVEL/
ROAD/Tourtst, all real profiles Doug has configured over time on-device;
false of freshly toolkit-built test files) -- a shared cause behind both
message 170 and a working WindField, not message 170 causing it. This
matches what this thread had already found independently (ROAD.fit and
the on-device-edited WindTest2A both carry message 170; the padding-only
fix works without it).

**The pattern that has held without a single exception, across every
test either thread has run (this thread's WindTest2A/4B/9A, the
Clonebox Screen 4 test, the message-170 injection test, Favorite Screen,
the ROAD Screen 3 value-only swap; the other thread's parallel tests on
the same files): every toolkit-written introduction or relocation of
field 216 into a screen slot has failed (falls back to Timer); every
Garmin-software-written one -- on-device edit, or a whole-file Clone
Profile copy that merely preserves an already-working placement -- has
worked.** This is consistent with (though not independently proven to
the level of, e.g., decompiling firmware) a legitimate Connect IQ
entitlement/anti-tampering check: the device likely only trusts a
WindField placement its own software created, and silently substitutes
Timer -- its apparent universal "always resolvable, zero-configuration"
default field -- for anything it doesn't trust, rather than failing
loudly. No clean bit/offset relationship exists between field 216 and
field 56 (checked independently by both threads, same negative result)
-- ruling out a numeric-confusion explanation.

**Practical conclusion, Doug's call pending final review: this is very
likely NOT fixable by this toolkit.** If a Connect IQ field genuinely
requires a device-side, purchase/install-linked reference this toolkit
has no way to construct or discover (and two independent, fairly
thorough investigations have not found a constructible file-level
substitute), the correct scope for this project is a documented
limitation, not a continued fix attempt: purchased/third-party Connect
IQ data fields can be read and displayed correctly by this toolkit, and
an EXISTING placement can be relocated or have its surrounding screen
edited safely (padding-only fixes, whole-profile clones), but a NEW
placement of a Connect IQ field cannot be created via `--fields`/the
GUI's field picker -- only via the device's own on-device editor.
README caveat drafted but not yet added (pending Doug's final go-ahead).
Prior rev (95, 2026-09-01) follows.*

*Doc rev 95 — refreshed 2026-09-01.* **WindField Widget (field 216) bug
investigation -- major real-hardware finding, session paused mid-
investigation, picking up tomorrow.** Doug found this by hand: editing
`Clonebox`'s Screen 2 (single field) and Screen 3 (7-field B, position 3)
to WindField Widget via the GUI showed correctly in the GUI's own
read-back, but the physical device rendered Timer (field 56) in both
positions instead. Full investigation, in order:

1. **Padding sentinel bug -- real, CONFIRMED, and fixed for the cases it
   applies to.** Byte-diffed the broken toolkit-written file against a
   copy Doug fixed by hand on-device: the ONLY difference was that
   unused trailing slots in the screen's 10-slot field-ID array (FIT
   mesg_num=14, field 7) were `0xFFFF` in the broken file vs a real
   field ID (48/Speed) in the working one. Built an isolated test file
   changing ONLY the padding (nothing else) and Doug confirmed it fixed
   both Screens 2 and 3. Root cause: `fit_patch.py`'s
   `pack_field_id_array()` pads unused slots with `0xFFFF`, and this
   device's firmware appears to choke on that specifically for WindField
   (ordinary fields and Graph/Bars-type fields tolerate `0xFFFF` padding
   fine -- confirmed via Screen 1's Power/HR Graphs and Screen 3's own
   Speed Bars/HR Bars, all sitting in the same padded arrays without
   issue). **This fix only ever worked for FULL-WIDTH placements.**

2. **Non-full-width WindField placement -- toolkit writes fail
   regardless of padding.** Built 3 fresh test profiles (WindTest2A,
   WindTest4B, WindTest9A) placing WindField at various field counts,
   all with CORRECT padding from the start, two of them deliberately
   non-full-width (paired/half-width slots). All 3 failed identically
   (Timer shown instead) -- including WindTest2A, which is full-width
   and STILL failed, correcting an earlier assumption that full-width
   toolkit writes reliably work. Re-tested WindField non-full-width on
   Screen 4 of the REAL, already-active Clonebox profile (not a fresh
   clone) with a Graph/Bars field (Speed Bars) in the adjacent paired
   slot as a control -- Speed Bars rendered correctly, WindField still
   showed Timer. Rules out "new profile" and "message_index 7 specifically"
   as explanations; confirms the failure is WindField-specific, not
   shared by Graph/Bars-type fields.

3. **Message 170 -- a real structural difference, but NOT sufficient on
   its own.** Diffing Doug's on-device-edited "fixed" file against the
   toolkit-written broken one (both for the original Screens 2/3 fix AND
   later for WindTest2A's on-device edit) found a message type never
   seen before (mesg_num=170: a 16-byte ID + a small incrementing
   counter) appended by the on-device editor whenever ANY change is
   saved through it, plus a separate incrementing counter in `file_id`
   itself (field 5, 3->4). These look like generic "this file was
   touched by the on-device editor" revision bookkeeping, not anything
   WindField-specific. Built a test appending a verbatim copy of this
   block (plus the file_id counter bump) onto a known-failing
   non-full-width WindField placement -- still failed. **Caught and
   fixed a real bug in that test's construction along the way**: adding
   bytes changes the file's total length, which means the file
   header's OWN internal CRC (bytes 12-13, separate from the trailing
   file CRC, protects `data_size` among other header fields) also needs
   recomputing -- missed this the first pass, which likely explained an
   even worse result (NO screen rendered correctly, not just WindField)
   on that specific attempt. Verified after the fix: header CRC,
   trailing CRC, and file length all correct. Re-tested -- still failed
   even with everything structurally clean. Also verified, importantly:
   this header-CRC gap does NOT affect any other file in this
   investigation or the toolkit's normal edit path in general --
   `patch_screen()` only ever does same-length in-place byte
   replacement, never touches `data_size`, so this was specific to the
   one test that appended new bytes.

4. **Working theory (not yet fully proven): WindField needs a one-time,
   on-device "first use" registration that only Garmin's own editor can
   perform, invisible to file content.** Every toolkit-written
   PLACEMENT of WindField into a slot that never had it before has
   failed, regardless of padding, full-width-ness, message 170, or
   which profile/message_index. Every case where WindField ended up
   correctly rendering was either an on-device edit, or a byte-for-byte
   copy (via Clone Profile, which duplicates the whole file) of a
   profile that ALREADY had a working WindField placement somewhere in
   its history -- confirmed again this session: Doug cloned ROAD (has a
   working WindField on Screen 1) to a brand-new profile name
   ("NewRoadClone") via the GUI's normal Clone Profile feature, and it
   rendered correctly there too, consistent with the theory (whole-file
   byte copy carries forward whatever makes it work, independent of
   profile name/identity). Tested whether the Favorite Screen feature
   could transplant a working WindField placement into an unrelated
   profile -- checked the code first: Favorite Screen does NOT do a
   raw byte copy of the screen record, it only remembers `field_ids` +
   `layout_variant` as plain values and rebuilds via the same generic
   `pack_field_id_array()`/`patch_screen()` path as every other failed
   test. Predicted it would fail for that reason before Doug tried it --
   confirmed, same Timer fallback. Checked whether 216 (WindField) and
   56 (Timer) have some numeric/bit-level relationship that might
   explain why the fallback is consistently Timer specifically (not
   blank, not some other field) -- no clean single-bit or mask pattern
   between `0xD8` and `0x38`; more likely Timer is just this firmware's
   generic default fallback field, unrelated to WindField's specific ID.

**NOT YET TESTED, flagged for tomorrow:** whether the on-device editor
can add WindField to a screen/profile that has GENUINELY NEVER had it
anywhere in its history (every on-device-editor success so far has been
MOVING an already-present instance, e.g. within Clonebox's Screen 3, or
cloning a profile that already had one -- never a true from-scratch add
via the device's own menu to a profile/screen with zero WindField
history). This is the cleanest possible test of the "first-use
registration" theory and doesn't require anything from this toolkit --
just Doug trying the on-device field picker on a profile like MOUNTAIN
or GRAVEL that's never had WindField configured.

**Practical implication if this holds up:** WindField Widget (and
possibly other Connect IQ/"widget"-class fields not yet identified) may
belong to a real, distinct category this toolkit cannot freely write --
unlike every other of the ~150 confirmed field IDs, which have all
worked via ordinary byte-patching throughout this project's history
without incident. If unresolved, Doug's fallback plan is a README note
documenting this as a known special-case limitation rather than
continuing to chase a fix. Prior rev (94, 2026-09-01) follows.*

*Doc rev 94 — refreshed 2026-09-01.* **Odometer/`Totals.fit` Open Item
-- back-burnered, Doug's call, no personal data logged here by design.**
Closing out today's extended investigation (Doc rev 93 above, plus
research into sourcing an accurate target figure from Strava/Garmin
Connect lifetime stats and a real 2020 `Totals.fit` backup Doug supplied
for comparison -- none of those specific figures are recorded in this
document, deliberately: they're Doug's personal ride history, and this
file lives in a public repo. The mechanism-level findings from that
comparison ARE worth keeping: renaming a profile doesn't touch its
`Totals.fit` entry -- confirmed again by a real slot that carried a
different name years apart while its totals kept accumulating
continuously underneath; and the leftover zeroed slots 5-10 were
genuinely blank in the 2020 file, which cross-confirms Doc rev 86/87's
attribution of today's slot 5-6 name remnants to this project's own
2026 test-profile work, not older pre-existing history.

Doug's conclusion: **back-burnered unless someone specifically asks for
this feature** -- a firmer deprioritization than "low priority, under
consideration" (Doc rev 86's original framing), though not closed
outright. His reasoning: a SET (not RESET-to-zero) operation is only
actually useful/reliable if `timer_time`, `calories`, and `sessions` are
ALSO populated sensibly alongside the new `distance` -- otherwise it
reproduces the exact internally-inconsistent, looks-broken-on-device
problem this whole thread has been circling (Doc rev 93's design
answer: scale time/calories proportionally, leave sessions alone -- but
that still requires the user to have or estimate that supporting data,
not just one number). Doug's framing: this is genuinely more involved
than the classic "re-enter your odometer miles after a battery change"
expectation people bring from plain bicycle computers, which only ever
tracked (and needed) the one number. A `totals_mesgs` row is a small
reconciled record, not a single counter -- so even a "just set my
mileage" request carries more real design weight than it looks like at
first glance. Mechanically de-risked since Doc rev 86 (real Edge 530
forum evidence the `NewFiles/` write path works, Doc rev 93), but the
data-sourcing burden on the user turned out to be the more practical
blocker. Task tracker: stays `[pending]`, not promoted -- no go-ahead
given. Prior rev (93, 2026-08-31) follows.*

*Doc rev 93 — refreshed 2026-08-31.* **Odometer/`Totals.fit` Open Item
(Doc rev 86/87) revisited, doc-only -- Doug's proportional-scaling design
question answered, PLUS real-world forum evidence found that meaningfully
de-risks the item's open concern (2).** Doug asked how a future Set/Reset
Odometer feature should handle `timer_time`/`calories`/`sessions` when
SETTING (not resetting to zero) a profile's distance, since leaving them
untouched would produce an internally-inconsistent record. Design
answer: scale `timer_time` and `calories` proportionally to the
distance-change ratio (continuous, effort-linked quantities -- keeps
average speed/pace and calories-per-mile looking plausible, the
least-fabricated way to avoid an obviously-broken-looking record); leave
`sessions` untouched by default (a discrete count of rides that actually
happened, not something that should be scaled to a fractional/rounded
synthetic number) unless the user separately, explicitly edits it; any
future UI/docs should be explicit that scaled values are "best-effort,
keeps the record internally consistent," not a claim of literal
historical accuracy.

Also asked whether more research in Garmin's forums was worth doing, or
whether that could be looked into directly -- searched, and found
several long-running community threads on exactly this topic across
many Edge generations (1040, 1030, 840, 520/520 Plus, 820, Explore 2,
the old Edge 25), plus two established third-party tools (Fit File
Repair Tool, BigCatOS's "Edit Edge Data") -- confirming this is a
well-known, recurring want, not a niche one. One thread is directly
on-point: **"Ride Profile Details Resetting After Editing Totals.fit,"
Edge 530 forum (Doug's own model)**,
<https://forums.garmin.com/sports-fitness/cycling/f/edge-530/411994/ride-profile-details-resetting-after-editing-totals-fit>.
Read in full. Summary: a user with the near-identical goal (transferring
an odometer total from an old bike computer) edited `Totals.fit` (FIT
SDK's `.fit`->CSV->`.fit` roundtrip) and dropped it in `NewFiles/`. Some
values updated as expected, but their target profile's own row (`Road`)
kept reverting to 0 on reboot. Root cause, found by another forum member
inspecting the file: **the `message_index` 0 aggregate row must equal
the sum of all profile rows** -- the OP's edited file had the aggregate
row set to the target total but every individual profile row (including
`Road`) still at 0, so the mismatched aggregate showed up as an "all
time / no profile" total while the specific profile row that didn't
reconcile got dropped back to 0. This is real, on-model evidence
directly bearing on this Open Item's concern (2) below (`message_index`
0's behavior after an external edit was "unknown/untested" as of Doc rev
86) -- it's no longer fully unknown: the device (or its next-boot
reconciliation) appears to care that aggregate == sum(profiles), and an
inconsistent file produces exactly the "profile value silently reverts
to 0" symptom, not a clean accept-or-reject. The fix that actually
worked, confirmed by the OP ("I tried your file and it worked!"): another
member edited BOTH the aggregate row AND the `Road` row to matching
values, deliberately did NOT change the file's structure, and filled in
a plausible `timer_time` by assuming an average pace (24 km/h) for the
added distance rather than leaving it inconsistent with the new
distance -- i.e., real independent validation of the same
keep-it-internally-consistent instinct behind the proportional-scaling
answer above, applied by hand rather than by formula. Also notable: the
OP's own FIT-SDK CSV roundtrip introduced structural corruption ("hex
mess" in some cells) that likely explains some of their earlier failed
attempts -- a concrete data point in favor of this toolkit's existing
plan (Doc rev 86: direct byte-patch-in-place plus CRC recompute, same
pattern as `fit_clone_profile.py`) over any convert-to-CSV-and-back
approach.

Net effect on this Open Item: still NOT building (no go-ahead given,
stays low-priority/under consideration), but the picture is more
encouraging than before -- the `NewFiles/`-based write path for
`Totals.fit` demonstrably works on a real Edge 530 when done carefully,
it isn't a dead end or an unreliable no-op. Any future implementation
now has a concrete, evidence-backed requirement to add to its design:
when SETTING a profile's distance (not resetting to zero), the
aggregate row's `distance` must be adjusted by the same delta in
lockstep, not just the target profile's own row -- addendum added to
the Open Item below. Prior rev (92, 2026-08-31) follows.*

*Doc rev 92 — refreshed 2026-08-31.* **`launch_gui.command` CONFIRMED
on real hardware -- the one thing Doc rev 91 flagged as untestable from
the dev sandbox.** Doug ran `./install.sh` fresh, then double-clicked
`launch_gui.command` in Finder -- worked. Closes out the last open
question on this feature; no longer just headlessly verified. Committed
and tagged as `v1.2.1` (`bb88e0e`) -- a patch bump, one new feature file
plus its `install.sh`/README support, no other changes bundled in. Prior
rev (91, 2026-08-30) follows.*

*Doc rev 91 — refreshed 2026-08-30.* **macOS double-click launcher for
`gui_app.py` -- BUILT, Doug's go-ahead.** Closes the gap first noted at
Doc rev 76 (2026-08-22, deliberately left untracked pending Doug's
confirmation he wanted it): Windows' `python.org` installer associates
`.py` files with the SAME `python` `pip install` puts packages into, so
double-clicking `gui_app.py` in File Explorer just works there (no venv
in that install path, by design -- `install_windows.bat`'s own v1.0.0
entry). macOS has no equivalent -- `install.sh` deliberately uses an
isolated `.venv` (so nothing touches system/Homebrew Python), and even
if macOS's old Python Launcher app handled a bare `.py` double-click at
all, it would invoke whatever `python3` it resolves by default, not
that `.venv` -- the exact mismatch Doug hit and worked around by hand
during the Windows-confirmation testing session two weeks prior. Since
a shared venv-vs-no-venv trade-off applies identically to both
platforms (isolation vs. double-click-ability), and Windows already
made its choice (no venv, for double-click), the macOS equivalent isn't
"remove the venv" (would undo the whole reason `install.sh` uses one)
-- it's a small separate launcher, which is what got built:

New `launch_gui.command` v1.0.0 -- a `.command` file (Finder's actual
native double-clickable-script mechanism on macOS, distinct from `.py`
file-association tricks): resolves its own folder via `$(dirname "$0")`
(same pattern `install.sh`'s `SCRIPT_DIR` uses), checks `.venv/bin/
python3` exists and is executable (if not: clear message pointing at
`./install.sh`, paused via `read` so the Terminal window doesn't close
before it's readable, exit 1), then launches `gui_app.py` directly via
that exact venv's `python3` -- not `source .venv/bin/activate` in a
subshell, functionally identical but one less moving part. On a normal
clean exit (GUI closed by the user) it exits immediately, no pause; on
ANY non-zero exit (missing venv, `gui_app.py` itself crashing/failing
to import `wx`) it prints the exit status and pauses for a keypress
first, so a real error is actually readable before whatever Terminal
does with a finished script. `install.sh` is now v1.0.3 -- adds a new
defensive step 10, `chmod +x launch_gui.command` unconditionally on
every run (covers a download method, e.g. a zip rather than `git
clone`, that might not preserve the executable bit), and its own
"Next steps" output now mentions the launcher as the no-Terminal
alternative to the two commands already listed.

Headlessly verified, all three real branches, via a simulated
`.venv/bin/python3` stand-in (a tiny script that just exits 0 or 1,
standing in for real `wx`/`gui_app.py` since wxPython can't be
installed in this dev sandbox): missing `.venv` -- correct error
message, exit 1; venv present, simulated clean exit -- no pause, exit
0; venv present, simulated crash -- error message printed, paused,
correct exit 1 propagated. `install.sh`'s own syntax reverified clean
(`bash -n`) after the edit, and the file's `SCRIPT_VERSION` bump
confirmed as the only such assignment left in the file (the edit
replaced an in-place comment block that used to sit directly above the
old `SCRIPT_VERSION="1.0.2"` line, so that had to be removed by hand
rather than just prepending new text above it, same care as always
taken with this file's changelog-in-comments style). Real Finder
double-click and Gatekeeper first-launch behavior (documented in both
the script's own header comment and README.md's Setup section, but
genuinely can't be exercised from this sandbox) still need Doug's own
run. README.md's Setup section and Tools table updated to match (see
Doc rev 71 there); also corrected a stale line there claiming Windows
"doesn't have [a setup script] yet," left over from before
`install_windows.bat` existed. Prior rev (90, 2026-08-30) follows.*

*Doc rev 90 — refreshed 2026-08-30.* **Real motivating use case
surfaced for Clone Profile, drafting the r/Garmin post below --
doc-only, no code changed.** Doug recalled a complaint from an Edge 530
review's comment section around launch: creating a new profile
on-device doesn't inherit any of the OTHER settings you'd already tuned
on an existing one -- navigation, alerts, sensor pairing, and whatever
else lives in the file outside the data screens -- so every new profile
means redoing all of that by hand. Clone Profile already solves this,
and not as a side effect discovered after the fact -- it's a direct
consequence of how `fit_clone_profile.py`'s `patch_profile_name()` has
always worked (Doc rev/table entry, `fit_clone_profile.py` v1.0.0):
read the ENTIRE input file into a `bytearray`, overwrite ONLY the
32-byte name field's byte range, recompute the trailing CRC, write
everything else untouched -- so every setting outside the name field,
including all the non-screen configuration this toolkit has never even
needed to understand, rides along automatically. This reframes Clone
Profile's value: it isn't just "rename a profile," it's "start a new
profile without losing everything you already configured on an
existing one" -- a real, previously-articulated pain point, not a
guessed-at selling point. Folded into two places: the drafted r/Garmin
post (see the workspace file `reddit_post_draft.md`) and `README.md`'s
opening "What it does" section (Doc rev 70 there), so a new reader sees
WHY cloning matters, not just that it exists. No functional change --
this is purely making an existing, unchanged behavior's value explicit
in the user-facing docs. Prior rev (89, 2026-08-30) follows.*

*Doc rev 89 — refreshed 2026-08-30.* **Second cosmetic-only startup
quirk found on the same 32-bit-only club laptop (Doc rev 88) -- a
console message, not a code bug, no fix needed.** Double-clicking
`gui_app.py` opens a console window (normal on Windows) showing `Error:
Unable to set default locale: 'unsupported locale setting'` before the
GUI itself appears; the GUI still starts and works fine afterward
(same session where Doug confirmed detect/edit/deploy all working --
see Doc rev 88). This message comes from wxWidgets' own C++
initialization (`wx.App()` construction, before any of this project's
code runs) trying to set a default locale and finding the one Windows
reports unsupported by the underlying C runtime -- confirmed via
research a known, widely-reported wxPython/wxWidgets behavior on
Windows (other unrelated wx-based apps hit the identical message and
wording), not something introduced by this toolkit or specific to this
machine's age. `gui_app.py` has no locale-related code at all (checked
directly, nothing to fix on this project's side). Harmless and
cosmetic -- logged so it's not mistaken for a new bug if seen again on
this or another Windows machine. Prior rev (88, 2026-08-29) follows.*

*Doc rev 88 — refreshed 2026-08-29.* **New hardware floor confirmed:
genuinely 32-bit-only hardware, via a donated bike-club laptop --
Windows 10 32-bit on an Intel Atom N270 (2008, no 64-bit extensions at
all). By far the oldest/most constrained machine this toolkit has ever
been tried on.** This is a different situation from ordinary
"Windows 10 vs. 11" -- the CPU itself can't execute 64-bit code (the
64-bit Python installer wouldn't even launch), so 64-bit Windows was
never an option regardless of licensing. Worked out the real dependency
chain live with Doug: wxPython dropped official 32-bit Windows wheels
as of 4.2.0, and the last version that HAS one (4.1.1) only has wheels
for Python 3.6-3.9 -- so this isn't just "install any 32-bit Python,"
it specifically needs 32-bit **Python 3.9.13** (the last 3.9.x release
with a binary installer at all; later 3.9.x security releases are
source-only) paired with `pip install wxPython==4.1.1` (not latest).
`install_windows.bat` doesn't fit this case -- it hard-checks for
Python 3.10+ -- so setup on hardware like this has to bypass the script
and install manually. CONFIRMED end to end on the real laptop: Python
3.9.13 (32-bit) installed and recognized (`py --version`);
`wxPython==4.1.1` installed clean prebuilt wheels (cp39-cp39-win32,
pulling in numpy/Pillow/six as prebuilt dependencies too -- no source
compile, which would have been a bad sign on this hardware);
`import wx`/`import garmin_fit_sdk` both clean; `gui_app.py` launched
and Doug was able to navigate into Edit Screen and use it. **UPDATE, same day: full round-trip CONFIRMED.** Doug connected a real
Edge 530 to this laptop -- `detect` worked, and a real data-field change
to the GRAVEL profile deployed successfully. This is now a complete,
real, end-to-end confirmation on genuinely 32-bit-only hardware, not
just an install/launch check -- detect, edit, and deploy all working
via `NewFiles/` exactly like every other confirmed platform.

**One real cosmetic bug found, environment-specific, not reproducible
in this project's dev sandbox (no wxPython available there at all).**
On the very first Edit Screen visit of a session (any profile, any
screen) -- and ONLY the first one; every subsequent Edit Screen visit
the same session is fine -- the "Layout:" label and both A/B
`wx.RadioButton` controls (`EditScreenPanel.__init__`, the
`layout_row` sizer) render wrong: the label area and both radio areas
look like blank text-entry-style boxes instead of a label + radio
buttons. Doug's own precise description: hovering/clicking in that area
reveals ONLY the "A" radio button and its label -- "B" and the "Layout:"
text stay unrendered. Going Back (to the profile list or Screens view,
either one) and back into Edit Screen -- for that profile or a
different one -- fixes it permanently for the rest of the session.
Since `refresh_from_file()` runs the exact same `SetValue()`/`Enable()`
calls on every visit (nothing in the code path is genuinely one-time),
this has all the signs of a native-control PAINT/invalidation timing
issue, not a logic bug -- most likely specific to wxPython 4.1.1's
Windows peer for a `wx.RB_GROUP` radio group, possibly compounded by
this laptop's very old/base integrated graphics (Atom N270-era, likely
no desktop composition) not repainting the newly-created native
controls until something forces a full `Layout()`/repaint -- which
matches exactly why revisiting the panel (a normal `_relayout()` call)
clears it. This is a HYPOTHESIS, not a confirmed root cause -- there's
no way to test a fix against this without the exact hardware/library
combination, which doesn't exist anywhere else in this project's test
matrix (macOS + Windows 11 64-bit only, until now). Purely cosmetic --
no evidence of an incorrect underlying layout value, just a rendering
gap -- self-resolves after one occurrence per session, with a trivial
workaround Doug already found by ordinary navigation. NOT chasing a
code fix for this -- logged as a known, environment-specific quirk
rather than guessed at blind. Prior rev (87, 2026-08-28) follows.*

*Doc rev 87 — refreshed 2026-08-28.* **Same-day refinement to Doc rev
86's odometer/`Totals.fit` finding: a real byte-level active/deleted
flag, found by Doug, confirmed by direct byte inspection -- plus his own
sketch of how a future set/reset feature would fit into the existing
GUI edit flow.** Doug noticed the def_num=10 32-byte packed field looks
structurally different between currently-active profiles (ROAD, INDOOR,
MOUNTAIN, GRAVEL) and the leftover entries for profiles he's since
deleted (test/sandbox/clone profiles from this project's own field-ID
exploration work). Checked byte-for-byte, not just via the SDK's
string-list decoding: active entries have the profile name starting
immediately at byte offset 0 of the field (e.g. `52 4F 41 44 00...` =
`"ROAD\x00"`). Deleted-profile remnants all have a single `\x00` at byte
offset 0, with the name text picking up at offset 1 -- missing exactly
its first character (`"oadtemp"` not `"Roadtemp"`, `"lonebox"` not
`"Clonebox"`, `"erialTest"` not `"SerialTest"` -- still shows the
capital `T` mid-string, `"oadClone"` not `"RoadClone"`, `"andbox"` not
`"Sandbox"`). Every other byte in the 32-byte block, before and after,
is identical to what an intact name record would look like -- the
device appears to zero out exactly the one leading byte in place when a
profile is deleted, clobbering only the first letter, without touching
or shifting anything else. This gives a real, confirmed `raw[0] ==
0x00` -> deleted (or the special aggregate slot at `message_index` 0,
which also reads `\x00` there -- can't fully distinguish those two
cases from this byte alone, but `message_index` 0 is presumably always
the aggregate) vs. `raw[0] != 0x00` -> active, full name intact. This
meaningfully de-risks the first of the two concerns raised in the Open
Item below (no reliable name-based lookup) -- there's now a real way to
tell active vs. deleted slots apart and recover the (almost complete)
name for display, rather than relying on pure `message_index` position
alone. The second risk (how the `message_index` 0 aggregate behaves
after an external edit) is unchanged/still open. Doug also sketched, for
if/when this is revisited, roughly how he'd want it to fit into the
existing GUI flow rather than being a separate standalone tool: when a
profile is selected, optionally read `Totals/Totals.fit` and offer the
odometer value as a displayable/selectable item; once shown, a Reset
button or a "set to value" option would be available; the change would
be HELD in the in-progress edit session the same way screen edits
already are (not written immediately), and as long as the user doesn't
back out of the session entirely, the modified `Totals.fit` would be
written to `NewFiles/` alongside whatever profile `.fit` (if any) is
also pending, for the device to pick up on next restart -- reusing this
toolkit's existing staged-edit/Apply/Deploy pattern rather than
inventing a new one. Not scoped in further implementation detail (still
"under consideration," not built) -- this is confirmation of the
byte-level mechanism plus Doug's own shape for the eventual UI, logged
for whenever it's revisited. Prior rev (86, 2026-08-28) follows.*

*Doc rev 86 — refreshed 2026-08-28.* **Odometer/mileage investigation
resolved -- located and confirmed against real on-device data, plus a
new toolkit feature idea scoped and then explicitly shelved.** Doug
asked whether a per-profile mileage/odometer total (~5,804 mi, his own
rough recollection) was stored anywhere in an Activity Profile `.fit`
file. Checked exhaustively -- every message type in
`CyclingRoadROAD.fit`/`CyclingRoadSerialTest.fit` field-by-field, plus a
raw byte-level brute-force scan of the whole file against ~10 plausible
unit-scale hypotheses -- and found nothing: the Activity Profile file is
a settings/definition file (screens, zones, name, serial), not an
accumulated-stats file. Correctly reported this as a negative result
rather than guessing. Doug then found via his own research that the
real store is a separate file, `Garmin/Totals/Totals.fit`, and uploaded
his own copy. Decoded and structurally mapped it directly: FIT mesg_num
33 (`totals_mesgs`), one message per profile slot, fields `timer_time`
(def_num 0, uint32, seconds), `distance` (def_num 1, uint32, **plain
meters -- no scale factor**, unlike most FIT distance fields which use
÷100), `calories` (def_num 2, uint32), a 32-byte packed name/type field
(def_num 10, only partially decoded by `garmin_fit_sdk` -- shows as
garbled string fragments), `message_index` (def_num 254, positional
slot index), `sessions` (def_num 5, uint16), and a `sport` enum (def_num
3, 255 = unset). CONFIRMED against real-world ground truth, not just
internally consistent: the entry matching Doug's `ROAD` profile
(`message_index` 3) has `distance = 9377167`, which as plain meters
converts to 5,826.70 mi -- an exact match (to the device's own 0.1 mi
display rounding) to what Doug's odometer showed after a ride that same
day. This also explains the earlier "not found" result: the ~5,804
figure was Doug's own rough memory, not the precise figure, which is
why the earlier byte-scan (looking for ~5,804 specifically) never
should have found anything in the Activity Profile file anyway --
correct file, correct field, confirmed. NOTE: the profiles Doug
currently has active on his Edge 530 are MOUNTAIN, INDOOR, ROAD, and
GRAVEL only -- `Totals.fit`'s other `message_index` slots (5 through 10
in the uploaded file) are leftover remnants of test/sandbox/clone
profiles created during this project's own field-ID reverse-engineering
work, since deleted from the device but still carrying zeroed entries
in `Totals.fit`. Doug then asked to scope a toolkit addition to
SET or RESET a profile's odometer total (e.g. to match a known-accurate
Strava/Garmin-Connect YTD or all-time figure), based on his own web
research describing both an on-device "Delete Totals" reset and a
manual `.fit`-editing approach via `NewFiles/`. Scoped it: the patch
mechanics are straightforward and would reuse this toolkit's existing
patterns exactly (`fit_raw_walk` to locate the field, overwrite bytes,
recompute CRC via `fit_crc`, deploy via the existing `NewFiles/`
mechanism the same way profile deploys already work) -- but flagged two
real risks before any code was written: (1) `message_index` is purely
positional with no reliable name-based lookup (the name field is only
partially decoded), so selecting the WRONG slot is a real hazard without
a solid preview/confirm UI; (2) `message_index` 0 looks like a
cross-profile aggregate whose distance doesn't cleanly sum from the
named entries, and how/whether the device recomputes it after an
external edit is unknown/untested. Doug's call: this is riskier than he
wants to take on right now, especially combined with the deleted-profile
clutter making `Totals.fit` harder to reason about confidently. NOT
BUILDING -- logged as a new, low-priority "under consideration" Open
Item below rather than pursued further. Prior rev (85, 2026-08-26)
follows.*

*Doc rev 85 — refreshed 2026-08-26.* **Real hardware test, same-day
follow-up to Doc rev 84: a profile with a deliberately fake device
serial number was actually deployed and tested, not just discussed.**
No code changed (test-only, plus a one-off patched `.fit` generated as
the test article). Result: the device imported the profile cleanly --
name and every screen/field/zone preserved byte-for-byte -- but
silently rewrote the profile's own `file_id_mesgs[0].serial_number`
back to the device's real serial number, confirming Doug's own
real-hardware observation. Independently re-verified against Doug's
uploaded post-restart file via `fit_dump.py diff`, not just taken on
his word. Unplanned second finding from the same diff:
`file_id_mesgs[0].number` also changed (0 -> 6) -- unconfirmed what it
represents, logged as a new small open question. Doug's own
conclusions, adopted: this is positive real-world evidence the
warranty-replacement/device-upgrade backup-restore scenario works, and
it REFRAMES the previously-scoped cross-device warning idea -- a
mismatch is now demonstrated harmless-and-self-correcting rather than
an unknown risk, so an informational "are you sure this is the right
device?" nudge fits better than a caution-styled warning. Doug also
raised a genuinely new, broader use case for the same underlying
per-device-serial plumbing: a bicycle club scenario where a
technically able "admin" member manages multiple less-technical
members' devices, pushing shared "club standard" profiles out to
several units while keeping each member's own personal profiles
correctly separated and backed up by device serial. See the Open Item
above for the full writeup -- still not scoped in implementation detail
or built, this is confirmed real-world evidence plus an expanded
rationale, not a finished design. Prior rev (84, 2026-08-26) follows.*

*Doc rev 84 — refreshed 2026-08-26.* **Scope review + a real new
finding on "Auto-switch backup folder by device serial," CONFIRMED on
real hardware.** No code changed. Reviewed the August 2026-08-15 design
against everything shipped since (backup pruning, Import, the deploy
safety fix) -- no conflicts, plus one real implementation wrinkle
caught: `save_working_dir()`'s blind-overwrite `json.dump()` needs to
become read-modify-write once a serial map is added, or a plain
"Change..." click would wipe it. Separately, Doug asked whether
Activity Profile files carry a copy of the device serial number at
all, specifically to guard against a profile from one Edge accidentally
landing on a different one. CONFIRMED yes, independently verified in
this session (not just trusting Doug's own `fit_dump.py` output --
re-ran it directly against his uploaded `CyclingRoadROAD.fit`):
`file_id_mesgs[0].serial_number` is present in profile files, same
structure `get_device_info()` already reads from `Device.fit`. THE
deciding question -- whether that profile-embedded serial actually
matches the SAME PHYSICAL UNIT's own `Device.fit` serial, rather than
some other identifier -- CONFIRMED via Doug's own `garmin_device.py
detect` output against the same device: both `3356943454`, exact
match. This makes a genuinely separate, valuable addition buildable
alongside the folder-auto-switch feature: warn (not hard-block, effect
of a mismatch is unconfirmed/unknown) before writing a profile whose
embedded serial doesn't match the connected device. See the Open Item
above for the full writeup -- not yet scoped in implementation detail
or built, this closes out the prerequisite fact-finding only. Prior
rev (83, 2026-08-25) follows.*

*Doc rev 83 — refreshed 2026-08-25.* **Project rename finished --
"Publishing housekeeping cleanup" closed, the last item on this
week's list.** The GUI window title has read "Activity Profile Screen
Editor for Garmin Edge" since v0.16.7, but the rename never went
further -- this file's own and README.md's top-level headings still
led with "Garmin Edge 530," exactly the pattern the original rename
was meant to avoid, and `gui_app.py`'s module docstring, About dialog
text, `MVP_SCOPE.md`'s heading, and `FIT_PATCH.md`'s man-page banner
each carried one of three different inconsistent names (found by
directly checking every file's actual current text, not assumed).
Doug clarified the canonical name: **"Activity Profile Editor for
Garmin Edge"** -- no "Screen," no "530" -- matching his GitHub repo
name ("Activity-Profile-Editor") and his own Release titles ("Activity
Profile Editor for Garmin Edge Devices"). His own rationale: the
editor works with any Edge device, not just the 530 specifically (even
though the confirmed field-ID/screen-type data so far is 530-only),
and "Activity Profile" is the right noun to lead with over "Screen"
since backups, restores, and deploys all operate at the whole-profile
level, not the individual-screen level -- not leading with "Garmin" at
all was also a deliberate, previously-established call, to avoid
implying this might be a Garmin product. Updated: this file's H1,
`README.md`'s H1, `MVP_SCOPE.md`'s H1, `FIT_PATCH.md`'s banner, and
`gui_app.py`'s window title/module docstring/About dialog text (now
v0.19.20 -- see that file's toolkit-table entry above for the full
list of what changed). Also closes the other half of "Publishing
housekeeping cleanup": `README_DISCLAIMER_DRAFT.md`, superseded back
on 2026-08-11 when merged into README.md's License/Disclaimer section,
was found to already be deleted from the repo -- nothing left to do
there. Deliberately LEFT UNCHANGED: `MEMORY_LOG.md` (an explicitly
archived, dated historical record) and
`RELEASE_NOTES_v1.1.0.md`/`RELEASE_NOTES_v1.1.1.md` (already published
as GitHub Releases under Doug's own chosen title) -- both are
point-in-time snapshots, not live docs, same reasoning this project
already applies to never rewriting old changelog/Doc-rev entries.
Prior rev (82, 2026-08-25) follows.*

*Doc rev 82 — refreshed 2026-08-25.* **New feature, Doug's go-ahead:
backup retention/pruning -- the last open item from this week's
scoping pass.** `garmin_device.py` is now v0.12.8, `gui_app.py` is now
v0.19.19. Closes the "Backup retention/pruning" Open Item, deferred out
of MVP since v0.11.0 ("Backups accumulate indefinitely right now --
nothing deletes old ones"). Design chosen from three options Doug was
asked to pick between: (1) time-based folder deletion [CHOSEN] --
delete entire `backups/<timestamp>/` folders older than a chosen day
count; (2) keep latest N backups per profile -- rejected as needlessly
complex, since each timestamped folder snapshots EVERY profile
together (`backup_profiles()`), not one folder per profile, so this
would mean deleting individual files out of a shared folder rather
than whole folders; (3) keep only the single latest backup -- rejected
as cutting against Restore-from-Backup's whole reason for existing,
and not justified by Doug's own real usage numbers (~1098 backed-up
`.fit` files, ~4-5GB, over this project's entire prior history --
confirms disk space was never the actual constraint). Trigger: manual
only, Doug's explicit choice -- a "Clean Up Old Backups..." button
(`ProfileListPanel`, next to "Change...") with a live preview and
explicit confirm, same posture as every other destructive action in
this app; no automatic/silent pruning on launch. Default window: 30
days. New `garmin_device.prune_old_backups()` (the actual folder-
selection/deletion logic, using each folder's own timestamp NAME, not
filesystem mtime) plus a new `prune-backups` CLI subcommand, and
`gui_app.py`'s new `BackupCleanupDialog`. See both files' toolkit-table
entries above for the full writeup. Headlessly verified against a fake
multi-age backup tree (several day-ages plus a non-timestamp junk
folder that's correctly left untouched) and the CLI exercised
end-to-end; real GUI behavior needs Doug's own run. This was the last
item from Doug's "scope the remaining open items on the list" request
this week -- see Doc rev 77 for where that batch started. Prior rev
(81, 2026-08-24) follows.*

*Doc rev 81 — refreshed 2026-08-24.* **Two more real bugs found via
Doug's hardware testing of Import, same session as Doc rev 80's
deploy-path fix.** `gui_app.py` is now v0.19.18. (1) Window width --
Doug's report: "After I reach the deploy screen the width of the gui
window expands to almost the width of my computer screen, even though
the line of te[x]t that starts with '>>> Once the automatic...' isn't a
length that would require the extra window width." Correct instinct --
that text wasn't the cause. `ViewScreensPanel`'s title_text embeds the
FULL absolute `editing_path`, and `DeployPanel`'s status_text embeds
`profile_filename` directly -- both plain `wx.StaticText` with no
wrapping, and `_relayout()` only ever grows the window, never shrinks,
so a long value on the Screens review page (visited before Deploy)
forces the window wide and it STAYS wide once Deploy is reached, even
though Deploy's own visible text is short. Same established bug class
this codebase has hit before (see `GRAPH_WARNING_WRAP_WIDTH`'s own
comment, and PROJECT_NOTES.md "Corrections and lessons learned").
Fixed via the same `textwrap.fill()` hard-wrap pattern already used
elsewhere; new `_wrap_status_paragraphs()` helper wraps each paragraph
individually before rejoining with blank lines (wrapping the whole
joined multi-paragraph string in one call would collapse the
intentional blank-line breaks). (2) CONFIRMED, same real hardware test,
the actual cause of the long value: Doug picked an old file already
sitting in his own `working_dir/staging/` folder as the Import source
-- one of this toolkit's OWN artifacts (a previously staged AND cloned
file), not a genuinely external profile. `ImportPanel.on_show()`
suggested `os.path.basename(source)` verbatim, which carried every
layer of this toolkit's own internal `_staged_<timestamp>`/
`_clone_<timestamp>` naming, chained across repeat passes, straight
into the "Deploy as filename" default: `CyclingRoadTClone_clone_
20260823_124234_staged_20260824_182004_staged_20260824_182104.fit` (92
characters). Doug's own words: "I doubt that a regular user would have
a profile filename like that, but if I'd have picked a carefully
selected Profile name, this wouldn't have shown up." Deployed to
`NewFiles/`, he confirmed it was STILL sitting there unconsumed even
after a full power cycle and device restart -- "the Garmin didn't know
what to do with it." New `strip_internal_staging_suffixes()` fixes the
SUGGESTED default only (field stays free-text editable) -- see the new
Open Item below for Doug's own theory about how the on-device filename
constraint likely works, logged as a still-open question rather than
guessed at. Both fixes headlessly verified: the suffix-stripper against
Doug's own real 92-character filename (strips to the correct
`CyclingRoadTClone.fit`) plus single-layer/untouched/false-positive
cases, and the wrap-width math (<=42 chars/line, paragraph breaks
preserved). Real GUI behavior needs Doug's own run. Prior rev (80,
2026-08-24) follows.*

*Doc rev 80 — refreshed 2026-08-24.* **Real bug fix, Doug's report from
actually using Import External Profile right after it shipped: no way
to reach Deploy for a freshly imported profile.** `gui_app.py` is now
v0.19.17. The Screens review page showed Back/Re-read File/+ Add New
Screen but no "Review & Deploy..." for an import, and going Back lost
the staged import silently with no warning -- Doug's exact report: "in
the review screen, I don't see a button to deploy it... if I go back, I
don't see the imported Profile to move forward with deploying from
there either." Root cause: `ImportPanel.on_import()` left
`editing_path` at `None` ("fresh staging -- no accumulated edits yet"),
correct for the normal Stage-for-Edit flow (the staged file already
matches the device, so nothing needs deploying until an edit happens)
but wrong for Import, where the staged file is content the device has
never had at all -- it needs to be deployable immediately, before any
screen edit. Fix creates the scratch working copy right away (same
pattern any first screen edit already uses) and adds a new
`frame.import_pending` flag: `ViewScreensPanel`'s "Review & Deploy..."
button (gated on `editing_path is not None`) now enables right after
import as a direct consequence; `PreflightPanel`'s deploy gating --
previously pure byte-diff, disabling Deploy and showing "No differences
from the staged file -- nothing to deploy" for ANY byte-identical
staged/editing pair -- now also allows deploy when `import_pending` is
set, with accurate messaging ("Freshly imported profile -- ready to
deploy as-is"). The Back-button "unsaved edits" warning (same
`editing_path is not None` gate) now fires for an abandoned import too,
with import-specific wording ("You imported a profile that hasn't been
deployed...") instead of talking about "edits" that were never made.
Also closed a second gap found while fixing the first: discarding edits
after an import (`ViewScreensPanel.on_discard()`) used to call the
blanket `frame.discard_edits()`, which would null `editing_path` right
back to the exact stranded state this fix closes -- it now re-copies
from the staged file instead when `import_pending`, so Deploy stays
reachable, only the screen edits made this session are undone.
`import_pending` is cleared alongside `editing_path` by
`frame.discard_edits()` itself (already the central reset point for
deploy-done, re-staging a different profile, Restore, and Clone), so it
can't leak into an unrelated session. Headlessly verified via a
standalone simulation of the import/discard/deploy-gating logic
(`on_import`'s scratch-copy creation, `PreflightPanel`'s deployable
computation for both the import and normal-stage cases, `on_discard`'s
import-vs-normal branching, and `discard_edits()`'s cleanup) -- real GUI
behavior needs Doug's own run, wxPython can't be installed in the dev
sandbox. Prior rev (79, 2026-08-24) follows.*

*Doc rev 79 — refreshed 2026-08-24.* **Real bug fix, Doug's report from
actually using Favorite Screen right after it shipped: "Save as
Favorite" overwrote an existing favorite with zero warning.**
`gui_app.py` v0.19.16 -- `ViewScreensPanel.on_save_favorite()` now
checks `load_saved_favorite()` first; if one's already saved, a YES/NO
confirm names the field count and source profile before it's replaced,
and canceling costs nothing (the newly-selected screen's own data
isn't even read in that case). Still a single favorite slot, still
overwritten on confirm -- Doug's explicit scope was the warning, not
multi-favorite support. Separately, Doug floated a possible FUTURE
idea (explicitly not scoped or built now, logged only): a
`GarminBackups`-style `favorites/` folder alongside the existing
`staging/`/`backups/` structure, to hold multiple named favorites if
this feature turns out to be popular -- see the updated Open Item
above for his own framing (quick-replicate a screen across profiles
for sports/disciplines with similar needs, without the on-device menu
round-trip each time). Prior rev (78, 2026-08-24) follows.*

*Doc rev 78 — refreshed 2026-08-24.* **"Delete an entire Activity
Profile" investigation CLOSED, logged as out of scope, Doug's own
call.** Two clean black-box tests on real hardware: deleting the
`Sandbox` profile's `.fit` from `Sports/` alone didn't stick (profile
came back after power-cycle); deleting it from BOTH `Sports/` and
`Sports/Backups/` didn't stick either (still came back) -- ruling out
the `Sports/Backups/`-restore hypothesis the first test had pointed
at. Whatever really governs a profile's existence on-device isn't
exposed over USB mass storage the way this toolkit's entire
screen-editing model depends on, so whole-profile deletion is logged
as explicitly out of scope for this tool's goals at this time (see the
new Open Item above for the full two-test writeup, and `MVP_SCOPE.md`
Doc rev 17 for the scope-table entry) -- a genuine dead end for this
project's black-box-file-manipulation approach, not a "not yet built"
backlog item. Per-screen deletion (`fit_patch.py --remove`) is
unaffected and remains fully supported; this only closes out the
separate, harder whole-profile question. Prior rev (77, 2026-08-24)
follows.*

*Doc rev 77 — refreshed 2026-08-24.* **Three backlog items built in
one batch, Doug's go-ahead: a real safety fix, Favorite Screen, and
Import an external profile -- this week's scoped work, picked from the
Open Items list per Doug's own request to "scope the remaining open
items on the list and get those ready, and tested potentially by the
end of the week."** (1) `garmin_device.py` v0.12.7: `write_to_newfiles()`
gained an optional `working_dir` safety net -- backs up whatever
profile currently exists under the target filename before overwriting
it, closing a real gap where a bare CLI `deploy` call (unlike every
GUI-driven write) had no automatic backup at all. Deliberately a
silent auto-backup, not a block or prompt, since overwriting the
target is deploy's normal intended outcome. (2) `gui_app.py` v0.19.14:
Favorite Screen, closing the Open Item design-locked back on
2026-08-15 -- a single save/load slot (not a list), "Save as Favorite"
on the Screens view, "Load from Favorite..." on Add New Screen, WARN-
ONLY on a cross-profile mismatch. (3) `gui_app.py` v0.19.15: Import an
external profile, closing the other Open Item from 2026-08-19 -- a new
file-picker entry point for a `.fit` never backed up by this toolkit,
landing it in staging via `stage_for_edit()` for the normal Screens
review before any deploy; also closed the safety-fix gap (1) above,
which was discovered while scoping this feature. All three headlessly
verified (backup/no-op/skip cases for the safety fix; save/load
round-trip and single-slot overwrite semantics for Favorite Screen;
filename-collision rules, matching Clone's pre-refactor behavior
exactly, for Import) and compiled clean with no duplicate methods
introduced anywhere (AST-confirmed). Real on-device GUI testing for
all three is still pending Doug's own run, same as every GUI feature
in this project's history -- these were built to the same "headless-
verify everything possible now, confirm the rest for real later"
discipline as every other feature here, not treated as done just
because the code compiles. Prior rev (76, 2026-08-22) follows.*

*Doc rev 76 — refreshed 2026-08-22.* **`install_windows.bat` CONFIRMED
on real Windows 11 hardware — closes out Doug's own testing checklist
before tagging v1.1.1.** Test performed: uninstalled `garmin-fit-sdk`
and `wxPython` via `py -3 -m pip uninstall -y` (Python itself left in
place), confirmed both failed to import, then ran the script fresh --
Python detection, version check, pip install of both packages, and the
post-install import verification all worked cleanly against a real
Python 3.14 install. One benign pip warning seen (wx's bundled demo/
dev console scripts installed outside PATH) confirmed harmless and
unrelated to how this toolkit actually launches. Double-click launch of
`gui_app.py` in File Explorer reconfirmed post-reinstall, including a
one-time Windows "how do you want to open this file" dialog on the very
first double-click -- normal first-use `.py` file-association behavior,
not something this script causes; Doug confirmed he didn't recall
seeing it on his original install either, so it's treated as ordinary
Windows behavior rather than a regression. `install_windows.bat` is now
v1.0.1 (confirmation-only, no code changed). Same session, Doug also
spot-checked `gui_app.py`'s field picker against several of the 169
confirmed `FIELD_ID_NAMES` entries added across the three 2026-08-20
batches and confirmed the on-screen labels match the device --
`fit_dump.py` is now v2.4.25 (also confirmation-only). This was the
last item on Doug's own pre-v1.1.1 test list (the other three -- Stage/
View Screens merge, Clone Profile 15-char block, hide-warning removal
-- were already checked and reported OK). Separately, Doug raised a
possible future item: a macOS equivalent to Windows' double-click-
`gui_app.py` convenience -- a small `.command`-style launcher script
that would `cd` into the toolkit folder, activate `install.sh`'s
`.venv`, and launch `gui_app.py`, working around the Python Launcher/
venv mismatch documented at Doc rev 68. NOT scoped or built yet, and
deliberately not added to Open Items below until Doug confirms he
wants it tracked -- noted here only so the idea isn't lost.
**BUILT (2026-08-30, Doug's go-ahead) -- see Doc rev 91 at the top of
this document for the full writeup.** Prior rev (75, 2026-08-21)
follows.*

*Doc rev 75 — refreshed 2026-08-21.* **README.md restructured, Doug's
request.** Two changes: (1) a new "What it does" section now opens the
document right after the title, covering both the GUI and CLI in a
couple of sentences each, and leads straight into "Who this is for"
(moved up, text unchanged) — so a first-time reader gets the pitch and
the experience-level expectation before License/Disclaimer/Setup. (2)
The entire 46-entry "Doc rev" changelog block, which used to open the
document, moved to a new "## Changelog" section at the very end —
same content, unchanged and in the same order, just relocated so a
first-time reader isn't met with 60+ revision notes before finding out
what the toolkit does. Doug's own framing: "start with the explanation
of what the toolkit (CLI & GUI) does and the setup/install process...
that should lead into a who it's for, that way a person will know if
they have the experience needed for the install if they want to try
it." No content removed, PROJECT_NOTES.md itself unchanged structurally
(only README.md was restructured — Doug's request was specific to
README).

*Doc rev 74 — refreshed 2026-08-20. **13 new confirmed field IDs —
Doug's cross-check against the Garmin manual's own data-field
appendix.** Doug worked through his running "last few" list against
the Edge 530 Owner's Manual's appendix, then located each remaining
gap on-device: 98 Watts/kg, 439 3s W/kg, 207-213 Power Z1-Z7, 418
Power Z8, 419 Power Z9, 24 Laps, 41 Max Lap Power -- `fit_dump.py`
v2.4.24, `FIELD_ID_NAMES` now 169 confirmed entries (was 156). Two
things worth noting from the back-and-forth that got here: (1) "Lap
Power" (39) and the "Time in Zone" concept (199-203, the existing HR
Zone 1-5 (time) fields) turned out to already be confirmed -- cross-
referencing his working list against the live dict before he went
hunting saved a wasted search; (2) an earlier same-day "Laps Max"
note turned out to be two separate fields (24 Laps, 41 Max Lap Power)
Doug had conflated in his own notes, not one oddly-named field,
resolved once he found both independently. No collisions with any
existing entry. This closes out the manual-appendix cross-check --
no further appendix-listed fields remain unconfirmed. One real gap
still open: "Trainer Resistance," hypothesized (unverified) to need
a paired ANT+ FE-C smart trainer to even appear on-device, the same
sensor-gated pattern already documented for eBike Metrics fields --
Doug doesn't currently have a smart trainer to test against. Same
batch: corrected a factual error in `fit_dump.py`'s own v2.4.23
comment/changelog (data-only, not a functional bug) -- had wrongly
said the pre-existing W/kg family included field 159; 159 is actually
"3s Balance," an unrelated field. `FIT_PATCH.md`'s FIELD ID REFERENCE
table regenerated to match (Doc rev 31); `gui_app.py`'s
`FieldPickerDialog` docstring count updated (v0.19.12, doc-only).
Compiled clean; AST-confirmed no duplicate keys in `FIELD_ID_NAMES`
and all 13 new IDs present. Task #96 complete. Prior rev (73,
2026-08-20) follows.*

*Doc rev 73 — refreshed 2026-08-20. **10 new confirmed field IDs,**
Doug's continued field census: 265 Lap PCO, 267 Avg Right PP, 268 Lap
Right PP, 269 Right PPP, 271 Lap Right PPP, 273 Avg Left PP, 274 Lap
Left PP, 275 Left PPP, 277 Lap Left PPP, 440 10s W/kg --
`fit_dump.py` v2.4.23, `FIELD_ID_NAMES` now 156 confirmed entries
(was 146). Fills out the L/R Power Phase/Peak Power Phase family
alongside the existing 263/264/266/270/272/276 entries -- no
collisions with any existing entry. Doug supplied both the on-device
display label (what's stored, per this dict's established convention)
and each field's full concept name for the record this time, recorded
inline. Same batch, doc-only: Doug's investigation of the last
unmapped on-device label he'd been tracking, "Battery Status" (Lights
category), confirms it's an alias/duplicate menu entry that navigates
straight to field 317 "Light Battery" -- not a separate field, no
table entry needed; noted inline at 317's own dict entry.
`FIT_PATCH.md`'s FIELD ID REFERENCE table regenerated to match (Doc
rev 30); `gui_app.py`'s `FieldPickerDialog` docstring count updated
(v0.19.11, doc-only). Compiled clean; AST-confirmed no duplicate keys
in `FIELD_ID_NAMES` and all 10 new IDs present. Task #95 complete.
Prior rev (72, 2026-08-20) follows.*

*Doc rev 72 — refreshed 2026-08-20. **Correction, same day: "Target"
is field 521, not 512 — Doug's own catch.** A transcription typo when
Doc rev 70's batch was written up, not a raw-ID/name mismatch like the
2026-08-17 batch's real screen-3/4 transposition -- 512 never existed
on-device under either name. Fixed before this ever shipped in a
tagged release. Doug also confirmed, unprompted, that all 9 fields
from that batch are verified against the real on-device screen --
same confirmation standard as every other batch, upgrading the
earlier "flagged, not resolved" framing for the 5 Workout-adjacent
names to fully confirmed (their IDENTITY, that is -- whether/how they
relate to the separate, still-open f10=38 SCREEN-TYPE question is
untouched by this). `fit_dump.py` now v2.4.22 (146 entries, unchanged
-- corrected key, not new/removed). `FIT_PATCH.md`'s FIELD ID
REFERENCE table and NOTE updated to match (Doc rev 29). The f10=38
Open Item addendum below also corrected. Task #94 complete. Prior rev
(71, 2026-08-20) follows.*

*Doc rev 71 — refreshed 2026-08-20. **New `install_windows.bat`
setup script, Doug's go-ahead.** Prompted directly by real external
feedback -- a rider who wanted to try the toolkit found the install
burden more than he wanted to take on -- discussed alongside Doug's
own reflection on whether this project's install-ease has kept pace
with its editing-ease (see Doc rev 64's "who is this for" discussion).
Scoped as a real conversation, not jumped into: I laid out the
mac-vs-Windows structural differences (no Xcode-CLT equivalent, and
critically, no venv -- Doug's real Windows install skipped one
entirely, and using one would break the double-click-`gui_app.py`
behavior that install produced), then asked Doug directly, via
`AskUserQuestion`, what the script should do when Python is missing
entirely: detect-and-guide (matching `install.sh`'s own Xcode-CLT
treatment) versus auto-download-and-silently-install. Doug chose
detect-and-guide. Built `install_windows.bat` v1.0.0 exactly to that
design: `py`/`python.exe` detection, a HARD 3.10 floor (stricter than
`install.sh`'s soft warn-and-continue at the same threshold, since
building `wxPython` from source needs Visual Studio Build Tools on
Windows versus one command on macOS), no venv, pip install both
dependencies directly, verify both import, `--upgrade`/`--help`/
`--version` flags. **Not yet confirmed on real hardware** -- there is
no `cmd.exe` in this project's dev sandbox, so this is the first
piece of code in this toolkit shipped with literally zero dry-run
coverage of its own syntax, not even a headless one; Doug's own plan
is to uninstall the toolkit from the Windows laptop and re-test a
fresh install via this script specifically, before the next release.
README.md's Windows Setup section now leads with the script, manual
steps kept as an already-confirmed fallback. See the new
`install_windows.bat` toolkit table row below for the full writeup.
Task #93 complete. Prior rev (70, 2026-08-20) follows.*

*Doc rev 70 — refreshed 2026-08-20. **9 new confirmed field IDs,**
Doug's continued field census: 512 Target, 523 Step Time, 522
Duration, 511 Workout Comparison, 45 Workout Step, 100 Last Lap
Power, 258 Lap Time Standing, 260 Lap Time Seated, 264 Avg PCO --
`fit_dump.py` v2.4.21, `FIELD_ID_NAMES` now 146 confirmed entries
(was 137). No collisions with any existing entry. Worth flagging,
not resolving: 5 of these 9 (45, 511, 512, 522, 523) read by name as
Workout/structured-step fields -- directly adjacent to this project's
still-open f10=38 "Workout" screen-type question (`FIELD_EDIT_UNCERTAIN_TYPES`,
see the "f10=38 'Workout' field-reading anomaly" history above and the
Open Items list below): whether that screen's field slots are
actually meaningful/rendered on-device, since the on-device editor
exposes no field options for it at all. A naming lead worth watching
if Doug can confirm any of these against an active Workout session,
not treated as new evidence on its own -- a field's name doesn't
confirm where or how it actually renders, and none of the 9 have been
individually tied to f10=38. The other 4 extend already-populated
families: Power (100, matching the existing 3s/10s/30s/Lap/Avg
pattern) and Cycling Dynamics (258/260/264, standing/seated lap time +
PCO). `FIT_PATCH.md`'s FIELD ID REFERENCE table regenerated to match
(Doc rev 28); `gui_app.py`'s `FieldPickerDialog` docstring count
updated (v0.19.10, doc-only). Compiled clean; AST-confirmed no
duplicate keys in `FIELD_ID_NAMES` and all 9 new IDs present. Task #92
complete. Prior rev (69, 2026-08-19) follows.*

*Doc rev 69 — refreshed 2026-08-19. **New hard block: Clone Profile's
display name is now capped at 15 characters, replacing the "Import
external profile" item's neighbor -- unrelated feature, same session.**
Doug's report while using the GUI from a different angle: Clone
Profile's "New display name" field had no length check at all, only
the "New filename" field was validated (`.fit` suffix required,
case-insensitive collision check against every device profile -- both
already correct, confirmed while scoping this, no change needed
there). Doug found a note that Garmin limits Activity Profile display
names to 15 characters. Asked whether this should be soft guidance
(like `startup.txt`'s unconfirmed character/line counts) or a hard
block (like `NO_SHOW_TOGGLE_TYPES`'s confirmed Map/ClimbPro fact),
Doug settled it directly with a real-device test: typing a 16th
character into Garmin's own Activity Profile name editor does
nothing at all -- it just switches straight to the checkmark/complete
control instead of accepting more input. A confirmed device fact, not
a guess, so this got the hard-block treatment. New
`fit_clone_profile.py` v1.0.1 constant `PROFILE_NAME_MAX_CHARS = 15`,
imported by `gui_app.py`'s `ClonePanel` (v0.19.9) via a new
`_name_problem()` helper (same shape as the existing
`_filename_problem()`), wired into both `_update_validation()` (now
shows a live "(N/15 characters)" count) and `on_create()`'s own guard.
Deliberately separate from, and much stricter than,
`fit_clone_profile.py`'s existing `NAME_FIELD_SIZE` byte-capacity
check (31 usable bytes) -- that one's a real storage limit
`patch_profile_name()` already enforced safely (raises `ValueError`,
never corrupts); a name between 16 and 31 bytes would patch through
fine at that level, but Garmin's own software could never have
produced one, so how the device would actually render it is genuinely
untested territory this toolkit has no reason to create. Compiled
clean; AST-confirmed `ClonePanel` has no duplicate methods. Real GUI
behavior needs Doug's own run -- wxPython can't be installed in the
dev sandbox. Task #91 complete. Prior rev (68, 2026-08-19) follows.*

*Doc rev 68 — refreshed 2026-08-19. **Correction + new discovery:
README.md's Windows Setup steps were wrong, and double-click launch
works on Windows with no wrapper needed.** Doug corrected the Windows
Setup section directly after re-reading it -- the venv-based sequence
written there (`python -m venv .venv`, `Activate.ps1`) was never
actually what he ran; that was this project's own unconfirmed
inference (mirroring the macOS pattern) rather than something Doug had
verified, even though it was worded as "the exact sequence Doug used."
PROJECT_NOTES.md itself never made that specific claim (its own
Windows mentions only ever said "manual pip install ... path," no venv
specifics), so this correction is README-only, but worth recording
here too since it's a real accuracy lapse, not just a wording tweak.

What Doug actually did (2026-08-19 test): installed Python from
python.org via browser (the standard Windows installer), ran `python
-m pip install garmin-fit-sdk wxPython` directly with NO virtual
environment at all, copied the whole toolkit folder to a `Documents`
subfolder, then ran the CLI tools from PowerShell. Genuinely new and
useful discovery reported alongside the correction: double-clicking
`gui_app.py` directly in File Explorer launches the GUI with no
wrapper script needed -- Windows just works here, in clear contrast to
the macOS Python Launcher episode earlier this same week (where
double-clicking invoked a DIFFERENT `python3` than the one `wx` was
installed into, since that install went through a `.venv`). The
mechanism: the python.org Windows installer associates `.py` files
with the SAME Python `pip` installs into by default, so there's no
system-vs-venv split for a file association to point at the wrong
one -- this only holds for the no-venv install path Doug actually
used; a venv'd install would need `python gui_app.py` from an
activated PowerShell instead, same as any other venv.

README.md's Windows Setup section rewritten to lead with this
confirmed no-venv sequence (numbered steps: install Python, `pip
install` directly, copy the whole folder, then either PowerShell or
double-click), with a venv kept as an explicitly optional alternative
for anyone who wants dependency isolation, clearly flagged as
incompatible with the double-click path. See README.md Doc rev 54 for
the full rewritten text. No code changed -- documentation accuracy fix
plus a genuinely useful new fact for anyone following the Windows
setup path from here on. Prior rev (67, 2026-08-19) follows.*

*Doc rev 67 — refreshed 2026-08-19. **New Open Item: import an
external profile, not yet built.** Doug asked whether a user can
install/restore a `.fit` profile that never passed through this
toolkit (pulled from Garmin Connect, from another rider, an old manual
copy) via the GUI, and whether it lands in `backups/` with its own
timestamp folder. Investigated and confirmed: no on both counts today
-- the GUI has no `wx.FileDialog` anywhere, every panel sources files
from what the toolkit already knows about; the CLI's `deploy` command
CAN write an arbitrary local file, but doesn't touch `backups/` at all
and doesn't back up the profile it's about to overwrite either (a real
gap, not specific to external files). Current guidance: use CLI
`deploy` directly, with a manual `backup` run first as a safety net.
Logged as a new Open Item (see "Import an external profile") with two
candidate fixes, deliberately left undecided -- Doug's own call to
possibly build this alongside "Favorite screen" (same Open Item
section, still unbuilt), since both touch the
add-a-screen/profile-from-somewhere-else shape. No code changed this
entry -- pure backlog/scoping. Prior rev (66, 2026-08-19) follows.*

*Doc rev 66 — refreshed 2026-08-19. **Real bug fix: stale "hide is
untested" warning removed for named Garmin screens.** Doug's report:
he'd successfully unchecked "Show Screen" for several named types --
Lap Summary, Cycling Dynamics, Elevation among the ones he named
directly -- and each time it worked correctly, but the confirm dialog
STILL claimed hiding a named type via a raw file write was "genuinely
UNTESTED." Doug clarified he's tested hiding every named type that
actually has a Show Screen checkbox in the on-device editor, not just
the three he mentioned, and separately noted Map/ClimbPro's existing
hard-block dialog is correct and should stay as-is.

Root cause, confirmed by reading `EditScreenPanel`: `on_show_toggle()`
runs two HARD, non-overridable blocks first --
`hide_unsupported_screen_type()` (Map/ClimbPro, `NO_SHOW_TOGGLE_TYPES`,
CONFIRMED via direct on-device inspection to have no Show Screen
toggle at all, on any profile) and `would_hide_last_visible_screen()`
-- then, ONLY if both pass, a third and much SOFTER confirm,
`_confirm_hide_guard()`, fired for ANY remaining named-type match from
`fit_patch.py`'s `check_system_screen_guard()`, with alarming
"genuinely UNTESTED" wording. The key realization, working through
this with Doug rather than just softening the wording: `NO_SHOW_TOGGLE_TYPES`
was never a partial sample of untested types -- it's the RESULT of an
exhaustive on-device check ("no toggle at all, on any profile"). So
anything that clears the Map/ClimbPro hard block and still matches a
named type is, by elimination (not by new testing), a type that DOES
have a working toggle. The soft dialog's "untested" framing was
already logically stale the moment `NO_SHOW_TOGGLE_TYPES` was
confirmed exhaustive -- Doug's real-device testing across the full
remaining set just caught up with what the architecture already
implied.

Discussed and scoped before touching code (Doug offered two
directions: soften the wording, or remove the dialog entirely) --
recommended and Doug chose full removal, since "less risky" undersold
it: there was no remaining case left for the dialog to be hedging
against once framed this way. `_confirm_hide_guard()` (the whole
method, including its docstring) DELETED from `EditScreenPanel`; its
one call site in `on_show_toggle()`'s hide path removed and replaced
with a comment explaining why. Hiding a named Garmin screen type now
proceeds exactly like hiding a plain user screen -- direct patch, no
popup. The two HARD blocks (Map/ClimbPro, last-visible-user-screen)
are completely untouched -- still fire exactly as before, still
non-overridable. The SEPARATE guard on CONTENT changes to a named
screen's fields (`_confirm_guard()`, used by Add/Remove Field, a
different question -- what a named screen's fields mean per type is
genuinely less uniformly tested than the Show/Hide bit) is also
untouched -- not what was reported, and still a legitimate caution.

`gui_app.py` now v0.19.8. Compiled clean; AST-confirmed no duplicate
methods and zero remaining references to `_confirm_hide_guard`
anywhere in the file. Real GUI behavior needs Doug's own next run --
wxPython can't be installed in the dev sandbox. Prior rev (65,
2026-08-19) follows.*

*Doc rev 65 — refreshed 2026-08-19. **Real bug fix: "View Screens"
could silently open the wrong profile.** Doug's report from actually
editing one of his main profiles: select Profile A, click "Stage
Selected for Edit," then decide to pick a different profile (B) from
the list instead -- "View Screens" stayed enabled, and advancing to
Edit Screens showed A, the ORIGINAL pick, not B. Doug asked to
discuss/scope before any change, correctly suspecting the GUI's
button logic depended on what the underlying CLI/backend calls
actually do.

Root cause, confirmed by reading `ProfileListPanel`: staging
(`on_stage()`) and navigation (`on_next()`, bound to "View Screens")
were two separate clicks, backed by two separate pieces of state --
`self.staged_path`/`frame.staged_path`/`frame.profile_filename`, set
only by staging, and `next_btn`'s enabled state, also set only by
staging. `on_profile_selected()` (fires on every list-selection
change) only ever touched Restore/Clone's enabled state -- it never
reset `next_btn` or the staged-profile pointers when the selection
moved to a different profile. So after staging A then clicking B,
`next_btn` stayed enabled and still pointed at A; the visible
"Selected: B" text was the only thing that updated, making the stale
button look current when it wasn't.

Scoping discussion (see Doug's own two proposed directions: reset/warn
the existing button, or merge Stage+View into one): the deciding fact
was that `stage_for_edit()` (`garmin_device.py`) is a plain local file
copy of the already-backed-up profile plus a `.lineage.json` sidecar
-- no device I/O, no CLI subprocess call (the GUI calls it as a direct
Python function, same as everywhere else in this app) -- so it's cheap
enough to redo on every click with no real cost. That, plus the
observation that Restore and Clone (same panel, same button row)
ALREADY skip a separate staging step entirely -- one click straight
from "profile selected" to their own next panel -- made merging the
clearly better fix over patching the sync bug in place: it removes
the whole two-buttons/two-states class of bug structurally, not just
this one instance, and makes View Screens consistent with its two
neighbors on the same panel. Presented three options (merge; keep two
buttons but disable on reselect; keep two buttons but warn on a stale
click) -- Doug chose the merge.

Implemented (`gui_app.py` v0.19.7): `stage_btn` ("Stage Selected for
Edit") removed entirely. `on_stage()`'s body folded into `on_next()`
("View Screens →"), which now looks up the CURRENTLY selected
profile, stages it, discards any stale `editing_path` (same discipline
the old `on_stage()` carried, from the 2026-08-06 fix), sets the
frame-level staged-profile pointers, and navigates -- all in one
click, every click. `next_btn`'s enabled state now follows the list
selection directly (`on_profile_selected()`/
`on_deleted_profile_selected()`), exactly like `restore_btn`/
`clone_btn` already did, rather than being set by a separate staging
step. Two prose comments elsewhere in the file that referenced
`ProfileListPanel.on_stage()` by name were updated to point at
`on_next()` instead; the class docstring's "Stage/Clone/View Screens"
phrasing updated to "Clone/View Screens" (staging is no longer a
separately-named user action). Compiled clean; AST-confirmed
`ProfileListPanel` has no duplicate methods and zero remaining
`stage_btn`/`on_stage` references. Real GUI behavior needs Doug's own
run -- wxPython can't be installed in the dev sandbox. Prior rev (64,
2026-08-19) follows.*

*Doc rev 64 — refreshed 2026-08-19. **New "Who this is for" section in
README.md**, ahead of Doug posting this update to GitHub. Prompted by
Doug's own reflection, worth recording as a real product-scope
decision rather than just a doc tweak: after hitting setup friction on
both platforms this same session (venv/Python Launcher confusion on
Mac, PowerShell/module-copying on Windows), Doug asked directly
whether this toolkit was exceeding the computer knowledge/expectation
of a tool meant to be "easier" than the built-in profile editor, and
separately reflected on whether Python/wxPython was the right
technology choice in hindsight. Discussed and resolved: the "easier"
claim is true for editing (direct field access the on-device editor
doesn't expose, Delete Screen, Clone, Restore, batch changes,
automatic backups) but not yet true for setup (Terminal, a venv, pip)
-- those are two separable things, and only the first was ever really
the goal. Python/wxPython was NOT a wrong choice -- the hard part of
this project was always the reverse-engineered byte-level FIT
patching, where Python's fast-iteration/headless-testability was a
genuine asset (most of this session's fixes were verified without
wxPython even installed), and the fact that Windows support turned out
to be "fill in one already-marked function, confirmed working the same
week" is itself evidence the architecture (thin OS-agnostic core, one
platform seam) was sound; a more platform-native language choice would
likely have solved plug-and-play on exactly one OS while making the
other one hard, which given Windows support just went live would have
been the worse trade. Packaging into a real double-click
installer/app bundle (e.g. PyInstaller) remains the actual answer if
the audience should ever be non-technical riders -- deliberately NOT
built now, since the toolkit's audience today, by Doug's own
determination, is himself and equivalently technical riders; revisit
only if this GitHub post (which also includes the new Windows support)
draws real interest from a less-technical audience. New README section
states this plainly and names what setup actually involves, so a
GitHub visitor self-selects correctly instead of hitting the same
friction Doug did. No scope/architecture change to the toolkit itself.
Prior rev (63, 2026-08-19) follows.*

*Doc rev 63 — refreshed 2026-08-19. **Two follow-ups from the Windows
test pass.** (1) README.md's Setup section restructured into explicit
macOS/Windows subsections, per Doug's request to make the install
difference clear -- the toolkit itself runs on both now (confirmed
above), but only macOS has `install.sh`; Windows setup for now is
manual `pip install garmin-fit-sdk wxPython` in PowerShell, plus an
explicit note (learned the hard way earlier this session) that the
WHOLE toolkit folder needs copying over, not individual files, since
`garmin_device.py` imports `fit_dump.py` at runtime. `install.sh`
itself untouched -- still macOS-only by design, a Windows setup
script is a separate, not-yet-scoped task. (2) Real bug fix, Doug's
report: the GUI's `startup.txt` message editor (`StartupTxtPanel`)
showed only ~2 lines on the Windows laptop vs. ~5 on the Mac for the
IDENTICAL file -- same code, no platform-specific branch anywhere in
this panel. Root cause: `self.message_text` (a multiline `TextCtrl`)
had proportion=1/EXPAND in its vertical sizer but no explicit minimum
height, so its actual visible size was whatever leftover space
remained after every fixed-size sibling control (title, spin row,
warning label, buttons) -- and that leftover genuinely differs by
platform, since font metrics and DPI scaling aren't identical between
macOS and Windows even with the same code and window size. The "5
lines on Mac" figure was never a designed guarantee, just an
incidental result of Mac's own leftover space. Fixed in `gui_app.py`
v0.19.6 with `self.message_text.SetMinSize((-1,
self.message_text.GetCharHeight() *
garmin_device.STARTUP_TXT_MAX_LINES + 10))` -- a floor sized in actual
character-height units (not a hardcoded pixel guess), so the guarantee
(at least `STARTUP_TXT_MAX_LINES`, 6, lines visible with no scrolling
for a message at the documented guidance limit) holds on any
platform's real font metrics. Proportion=1/EXPAND is untouched, so the
control still grows taller than this floor whenever more room exists
-- Doug's Mac should now show 6 lines instead of the previous
incidental 5, slightly MORE visible room than before, not less.
Compiled clean; real visual confirmation on both platforms needs
Doug's own next run. Prior rev (62, 2026-08-19) follows.*

*Doc rev 62 — refreshed 2026-08-19. **Windows support CONFIRMED on
real hardware.** Doug ran the full test pass on a real Windows 11
laptop against his actual Edge 530: `garmin_device.py detect` printed
the same device info the Mac shows, `screens` worked from both
`fit_dump.py` and `garmin_device.py`, and the full GUI workflow — add
a screen to the Sandbox profile, deploy, restart, NewFiles round-trip
— completed cleanly, with zero code changes needed (one hiccup along
the way: an early CLI-only test copied over just `garmin_device.py`,
which raised `ModuleNotFoundError: No module named 'fit_dump'` since
`get_device_info()` imports it — resolved by copying the whole toolkit
folder instead). Doug's `D:\Garmin` has `Sports`/`NewFiles` flat at
the drive root, resolving the open question from Doc rev 61 — Level 1
of `_find_garmin_root_windows()`'s two-level check is what matched;
Level 2 (one-subfolder-deep, kept for parity with the macOS half) is
still unexercised on real hardware but has no reason to behave
differently. `garmin_device.py` now v0.12.6 (confirmation-only entry,
no code changed). `install.sh` remains macOS-only; Windows setup for
now is the manual `pip install garmin-fit-sdk wxPython` path, which is
what Doug used here. No Linux testing has been done. See "Device
connection layer" above for the updated summary. Prior rev (61,
2026-08-17) follows.*

*Doc rev 61 — refreshed 2026-08-17. **Windows device detection built,
Doug's go-ahead — pending real-hardware confirmation.** Doug has
Windows 11 access lined up for testing and asked for a short test
plan (CLI `detect` first, read-only CLI pass, GUI read-only pass, then
one real deploy/eject/reconnect, in that order — same "prove the read
path before the write path" discipline this project has used
throughout). Before any of that could run, `_find_garmin_root_windows()`
needed filling in — it's `garmin_device.py`'s single deliberately-
stubbed function, per the module's own docstring ("find_garmin_root()
is the ONLY function that needs a platform-specific implementation").
Now scans drive letters C: through Z: (A:/B: skipped) for the same
`Sports`/`NewFiles` structure check the macOS half uses, checking BOTH
the drive root and one level of subfolder — mirrors the macOS check's
own two-level structure exactly, since real Edge 530 hardware nests
`Sports`/`NewFiles` one folder down under the mounted volume on Doug's
Mac (confirmed there via direct `ls`); whether Windows exposes the
same nesting or puts them flat at the drive letter is the single
biggest open unknown, and the first thing this testing pass should
settle. Deliberately uses plain `os.path.exists()`/`os.listdir()`
drive-letter iteration rather than a Windows API (e.g.
`win32api.GetLogicalDriveStrings()`) — avoids adding `pywin32` as a
new dependency beyond what `install.sh` already installs, at the
minor, harmless cost of checking 24 drive letters unconditionally.
OSError from an inaccessible drive (e.g. an empty card reader) is
caught and skipped per-letter, same defensive posture as the macOS
half's `PermissionError` handling. `garmin_device.py` now v0.12.5.
Headlessly verified via `ntpath`-monkeypatched fake drive trees, since
real Windows drive letters can't be exercised in this dev sandbox:
nested-structure case, flat-structure case, no-device-present case,
and a flaky/inaccessible-drive case all behave correctly; confirmed
A:/B: are skipped and C: through Z: are checked in order; confirmed
`find_garmin_root()` correctly dispatches here when
`platform.system() == "Windows"`. `install.sh` remains macOS-only
(it's bash; a Windows setup path isn't built yet, not blocking the
`detect` test since dependencies can be installed manually with
`pip install garmin-fit-sdk wxPython`). See the "Windows support"
Open Item below for the updated status and the test plan itself.
Prior rev (60, 2026-08-17) follows.*

*Doc rev 60 — refreshed 2026-08-17. **FULLY CONFIRMED via direct
raw-byte inspection — the last open question on the 2026-08-17
field-ID batch is now closed.** Doug's `CyclingRoadRoadtemp.fit` (the
original census profile, with Screen 3/Screen 4 still intact at 10
fields each) came through on a second upload attempt and was dumped
directly via `fit_dump.py dump`. Raw field-ID arrays: slot 6 (Screen
3) = `[150, 149, 177, 176, 43, 437, 40, 408, 411, 441]`, slot 7
(Screen 4) = `[80, 42, 148, 147, 82, 83, 151, 161, 160, 159]`. Every
one of the 20 corrected `(ID, name)` pairs from Doc rev 59 matches
these raw arrays position-for-position exactly, including field 177
"Torque Effect" under its own ID — closing the one residual flag Doc
rev 59 was still carrying (that on-device string had only been
confirmed against ID 148, before the transposition was found).
`fit_dump.py` now v2.4.20. This is now the same direct byte-level
verification standard as every other confirmed batch in this project,
not resting on the earlier 3-for-3 device-observed inference alone.
See the Open Item below (now fully closed) and this project's
long-standing evidentiary discipline note — a real example of
preferring direct byte-level confirmation over inference, even after
the inference was already very strong. Prior rev (59, 2026-08-17)
follows.*

*Doc rev 59 — refreshed 2026-08-17. **RESOLVED: the 2026-08-17
field-ID batch had raw IDs and names correctly identified but WRONGLY
PAIRED, not a code bug.** Doug diagnosed it himself: his census
screens 3 and 4 (Roadtemp profile) got transposed when the original
20-entry list was written up, so all 10 IDs from one screen's block
were paired with the 10 names from the other screen's block — a
clean systematic offset (same 20 raw IDs, only which name each points
to changed), not scattered individual errors. Doug re-derived the
correct pairing directly from Roadtemp's screen 3/4 field order; it
resolves ALL THREE real-device mismatches from Doc rev 58 exactly
(437 → Avg W/kg, 147 → Lap NP, 148 → Last Lap NP, all matching the
device precisely). All 20 entries corrected, SUSPECT warnings
removed, `fit_dump.py` now v2.4.19. Not independently re-confirmed
via a raw byte-level dump (Doug's uploaded `CyclingRoadROAD.fit`/
`CyclingRoadRoadtemp.fit` weren't readable this session — an upload
sync issue, same class as the earlier `CyclingEbike.fit` episode) —
treated as sufficiently confirmed on the strength of the 3-for-3
exact match against independently-observed real device behavior. One
residual flag: field 177 (now "Torque Effect," the string confirmed
via the earlier half-width-field test) wasn't independently re-tested
under its own ID after the swap was found — carried over on the
strength of the transposition theory. See the Open Item below
(resolved) and "Corrections and lessons learned" for the methodology
takeaway. Prior rev (58, 2026-08-17) follows.*

*Doc rev 58 — refreshed 2026-08-17. **URGENT: data integrity issue
found in the 2026-08-17 field-ID batch, real device testing.** Doug
edited Screen 4 on `CyclingRoadROAD.fit` to fields named "Intensity
Factor (IF)" (437), "Pedal Smoothness" (147), "Torque Effect" (148),
"Perf. Conditioning" (320) via this toolkit's GUI, but the profile
actually displays "Avg W/kg, Lap NP, Last Lap NP, Perf. Cond." on the
real device — 3 of 4 wrong. Code review of `FieldPickerDialog`
(`gui_app.py`) found no picker/write bug — it writes exactly the raw
ID tied to the selected name — so this points to a census/
transcription error in the original 2026-08-17 batch, not a code
defect. `fit_dump.py` (now v2.4.18) flags the ENTIRE batch (20
entries) UNCONFIRMED/SUSPECT pending re-verification, with no values
changed yet (no raw-byte evidence in hand — need `CyclingRoadROAD.fit`
or a `fit_dump.py dump` of it from Doug). See the new Open Item below
for the full writeup and next steps. Prior rev (57, 2026-08-17)
follows.*

*Doc rev 57 — refreshed 2026-08-17. Real bug fix: field 148 was stored
as "Torque Effect." — a guessed abbreviated form, by analogy to field
320's "Perf. Conditioning" convention, added in Doc rev 56 without a
direct on-device check. Doug directly confirmed the real on-device
text in a half-width (1/2 side-by-side) field: "Torque Effect", no
trailing period. Corrected in `fit_dump.py` (now v2.4.17) and in
`FIT_PATCH.md`'s FIELD ID REFERENCE table/note. No count change, still
137 confirmed entries. Prior rev (56, 2026-08-17) follows.*

*Doc rev 56 — refreshed 2026-08-17. **20 new confirmed field IDs** —
Doug's continued field census, this project's first batch touching
power-meter/Di2-electronic-shifting metrics: the L/R power Balance
family (42 Balance, 80 Avg Balance, 40 Lap Balance, 441 3s Balance,
411 10s Balance, 408 30s Balance), Power/W-kg (150 30s Power, 151 Max
Power, 83 Avg W/kg, 159 30s W/kg), training-load metrics (149 %FTP,
43 TSS, 437 Intensity Factor (IF)), Normalized Power (176 Lap NP, 177
Last Lap NP), pedaling metrics (148 Torque Effect. — reported full
concept name "Torque Effectiveness (Torque Effect.)," stored
abbreviated per this dict's on-device-display convention, e.g. 320
"Perf. Conditioning"; 147 Pedal Smoothness; 82 Power Zone), and
Shimano Di2 (161 Di2 Battery, 160 Di2 Shift Mode). Notably confirms
the Power family's 3s/10s/30s/Lap/Avg naming pattern (79/146, already
confirmed) repeats identically for L/R Power Balance, with 42
"Balance" as the base metric mirroring 36 "Power" — a self-consistent
family, not a set of one-off guesses. No collisions with any existing
entry (confirmed via AST parse before insertion). `fit_dump.py` now
v2.4.16, `FIELD_ID_NAMES` now 137 confirmed entries (was 117);
`gui_app.py`'s `FieldPickerDialog` docstring updated to match (v0.19.5,
doc-only). `FIT_PATCH.md`'s FIELD ID REFERENCE table fully
regenerated to include all 137 entries in the same aligned two-column
format. Prior rev (55, 2026-08-16) follows.*

*Doc rev 55 — refreshed 2026-08-16. **Real bug: startup.txt's "?" bug
had a SECOND, separate cause -- a UTF-8 BOM, not smart quotes.** Doug
re-checked after the Doc rev 51 fix and still found 3 literal "?"
characters, but this time at the very FRONT of the file's first
(preserved, never-retyped) header comment line -- not anywhere he'd
typed, and invisible in the GUI's own editor (which only shows the
editable message text), only found by opening the raw file in BBEdit.
Root cause, confirmed by direct code inspection: `read_startup_txt()`
decodes raw bytes as ASCII with `errors="replace"`, so a leading
UTF-8 BOM (3 bytes, EF BB BF, each individually invalid for ASCII)
decodes to 3 U+FFFD replacement characters; those ride through
`parse_startup_txt()`'s "preserve header byte-for-byte" split (which
was only ever byte-for-byte from the DECODED string onward, not a
guarantee against corruption already introduced at decode time), then
`write_startup_txt()`'s ASCII-only encode turns each into a literal
"?" on save -- exactly 3, exactly at the start of the file, matching
Doug's report precisely. Because the header is carried forward
unchanged on every write, one BOM anywhere upstream (its exact source
still unconfirmed -- possibly an editor defaulting to "UTF-8 with
BOM" touching the file outside this toolkit at some point) would keep
self-perpetuating those 3 "?" forever, regardless of the smart-char
fix, which only guards freshly-TYPED text. Fixed: `read_startup_txt()`
now strips a leading UTF-8 BOM before decoding, so it's a silent
no-op. Matches Doug's own real-world sequence exactly: he manually
removed the "?" via BBEdit and re-saved (producing a clean, no-BOM
file), confirmed gone after a restart, then did a fresh `gui_app`
edit and the "?" did NOT reappear -- consistent with this theory,
since a clean re-save breaks the self-perpetuation cycle even before
this code fix existed. `garmin_device.py` now v0.12.4. Headlessly
verified: a fake `garmin_root` with a BOM-prefixed `startup.txt` now
reads back with zero "?"/U+FFFD in the header; a file with no BOM is
untouched (byte-identical). Prior rev (54, 2026-08-16) follows.*

*Doc rev 54 — refreshed 2026-08-16. **f10=38 "Workout" field-edit
warning BUILT, Doug's go-ahead — and the leading hypothesis for what
this screen even IS now has an official source, not just inference.**
Doug raised a sharp point: "Workout" doesn't show in the on-device
scroll list during a normal ride, same conditional-trigger family as
ClimbPro/Segment, so there's no way to see what it's supposed to look
like before editing it here — and he separately noticed a `Workouts`
folder (with empty `Guided`/`Scheduled` subfolders) sitting at
`garmin_root` alongside `Sports`, asking whether "Workout" might need
loaded workout data to mean anything. Checked against Garmin's own
Edge 530 Owner's Manual (Training > Workouts): starting a Workout
"displays each step of the workout, the target (if any), and current
workout data" — a dynamically-rendered display, entirely separate from
Activity Profile screens, driven by files synced/created into
`GARMIN/Workouts/Guided` or `/Scheduled`. This matches every piece of
evidence gathered so far: Doug's empty Workouts subfolders (he's never
used the feature, hence never seen this screen render), the on-device
editor offering no field options for it, and the byte-for-byte
duplicate field content found in Doc rev 53. Built a new, narrow
WARNING (not a hard block) in `EditScreenPanel` — `fit_dump.py`'s new
`FIELD_EDIT_UNCERTAIN_TYPES = {38}` backs a new
`field_edit_uncertain_warning_text()` (`gui_app.py`), surfaced only
when editing an f10=38 screen, explaining the edit is mechanically
safe but likely has no visible on-device effect. `fit_dump.py` now
v2.4.15, `gui_app.py` now v0.19.4. See the "f10=38 'Workout'" Open
Item below for the full writeup. Prior rev (53, 2026-08-16) follows.*

*Doc rev 53 — refreshed 2026-08-16. **CORRECTION to Doc rev 52's f10
values, RESOLVED via the real file, `CyclingEbike.fit`.** Once Doug's
upload finally came through and got dumped directly, two things
turned up: (1) Doc rev 52's new `NAMED_SCREEN_TYPES` entries used the
WRONG keys -- 39/59/96 were read off this tool's own "Screen N"
display label (which is `f10 + 1`), not the raw byte; the REAL f10
values are 38 "Workout", 58 "eBike Metrics", 95 "STEPS Metrics
(Shimano)". Corrected in `fit_dump.py`, now v2.4.14. See "Corrections
and lessons learned" below for the full writeup of how this slipped
through. (2) The f10=38 "Workout" field question from Doc rev 52 is
now RESOLVED, not just flagged: a direct raw-byte comparison confirms
slot 6's f10=38 record is byte-for-byte IDENTICAL, all 10 field
positions, to slot 1's Cycling Dynamics (f10=63) record on the SAME
profile -- real, accurately-read data, not a `classify_screens()`
bug. Also found two MORE exact-duplicate pairs while looking: the
profile's two Removed screens with real field content are each
byte-identical to the currently-active eBike Metrics/STEPS Metrics
records -- three confirmed duplicate pairs on one profile, consistent
with Garmin auto-creating these types from a fixed default field
template each time (same pattern Map/Elevation/ClimbPro already show).
See the "f10=38 'Workout' field-reading anomaly" Open Item below
(renamed from "f10=39," corrected) for the full writeup and the one
still-open product question. Prior rev (52, 2026-08-16, SUPERSEDED by
this entry, kept for the record) follows.*

*Doc rev 52 — refreshed 2026-08-16. **3 new confirmed f10 screen
types, CyclingEbike.fit (Doug's first e-bike/third-party-drivetrain
profile) -- SUPERSEDED, see Doc rev 53 above for the corrected f10
values.** `NAMED_SCREEN_TYPES` gains 39 "Workout", 59 "eBike
Metrics", 96 "STEPS Metrics (Shimano)" -- `fit_dump.py` now v2.4.13.
FLAGGED, not yet resolved: f10=39 "Workout" behaves unlike every
other named type in the table -- the on-device screen editor shows no
fields/options for it at all (only Remove/Reorder Screen), but this
toolkit's own screens/edit-screen views show it with the SAME field
set as a Cycling Dynamics screen on the same profile. This session's
attempt to inspect Doug's uploaded `CyclingEbike.fit` directly to
diagnose it did not succeed (the file didn't sync into this
environment's tools -- an upload/environment issue on this end, not
yet resolved), so no code change was made for this specific behavior;
`screen_type_name(39)` now correctly labels it "Workout," but
`classify_screens()`/field reading are UNCHANGED pending a real
byte-level look at the file. See the "f10=39 'Workout' field-reading
anomaly" Open Item below for the full writeup and leading hypothesis.
Prior rev (51, 2026-08-16) follows.*

*Doc rev 51 — refreshed 2026-08-16. **Real bug fix, Doug's report from
actually using the GUI:** a routine startup.txt edit came back with
three "?" characters added on one line and "..." replaced by a SINGLE
"?" on another line, even though Doug never typed a "?" anywhere.
Root cause: `write_startup_txt()` has always encoded with
`content.encode("ascii", errors="replace")`, and `wx.TextCtrl` on
macOS is backed by Cocoa's NSTextView, which silently auto-substitutes
typed text by default -- three periods become one U+2026 ellipsis
character as you type, straight quotes become curly ones, a double
hyphen becomes an em dash, etc. Each of those single Unicode
characters then hit the ASCII-only encode and became exactly one "?"
-- matching the reported pattern precisely (the ellipsis became ONE
"?", not three, which rules out a byte-level/UTF-8 explanation and
points straight at one non-ASCII CHARACTER per substitution). Not
independently byte-confirmed via a hex dump of Doug's exact
before/after files, but the mechanism reproduces the reported symptom
pattern exactly and is directly traceable to this file's own encode
call. Fixed with a new `_SMART_CHAR_REPLACEMENTS` table +
`_normalize_smart_chars()` (`garmin_device.py`, now v0.12.3), applied
to `content` inside `write_startup_txt()` immediately before the
ASCII encode -- reverses the common Cocoa smart-substitution
characters (curly single/double quotes, en dash, em dash, ellipsis)
back to their plain-ASCII originals. Any character NOT in the table
is still replaced with "?" on write, unchanged, honest fallback for a
genuinely unsupported character -- the GUI's existing non-ASCII
warning (`StartupTxtPanel._update_warning()`) still flags anything
that slips through. Single shared fix point: both the GUI
(`StartupTxtPanel.on_save()`) and the `startup-txt --write` CLI
subcommand funnel through this same `write_startup_txt()`, so both
get the fix with zero `gui_app.py` changes needed. Headlessly
verified: an ellipsis, curly quotes, and an en/em dash all round-trip
to their exact ASCII originals with zero "?" in the encoded output; a
genuinely unmapped non-ASCII character (an accented letter) still
degrades honestly to "?", confirming the fallback is unchanged for
anything outside the table. Prior rev (50, 2026-08-15) follows.*

*Doc rev 50 — refreshed 2026-08-15. **"Restore a Deleted Profile"
CONFIRMED via Doug's own real GUI test.** A deliberately-deleted
profile correctly appeared in the "Deleted, but available to restore"
list below the on-device ones, and restoring it worked cleanly end to
end. This was the one remaining gap this feature was carrying --
headless/CLI-level mechanics were already confirmed on 2026-08-11, and
the GUI build itself (v0.19.0) compiled clean, but real widget
behavior always needed Doug's own run since wxPython can't be
installed in the dev sandbox. Now fully confirmed, real hardware and
real GUI both. `gui_app.py` now v0.19.3 (doc-only). Prior rev (49,
2026-08-15) follows.*

*Doc rev 49 — refreshed 2026-08-15. **"Keep backups of separate
physical devices apart" DESIGN CHOSEN, not yet built (low priority,
requested by a tester).** The base ability to redirect the working
directory already exists (the "Change..." button, v0.16.9) -- the gap
is that it's one global setting with no memory of WHICH folder belongs
to which physical device. DESIGN CHOSEN (Doug): auto-switch
`working_dir` by device serial number, using the `serial_number`
`garmin_device.get_device_info()` already reads on every Detect --
extend the existing JSON config sidecar with a serial-keyed mapping,
falling back to today's manual-Change/last-used behavior for a new or
unreadable serial. The "Change..." button's own handler additionally
learns the mapping automatically (saves under whichever serial is
currently connected), so no separate "assign to device" UI step is
needed. Contained entirely to `gui_app.py`. See the Open Item below
for the full writeup. Prior rev (48, 2026-08-15) follows.*

*Doc rev 48 — refreshed 2026-08-15. **"Favorite screen" DESIGN CHOSEN,
not yet built (Doug's scoping decisions).** Scoped down to a SINGLE
favorite slot, not a named list -- no management UI needed, just one
slot overwritten on every Save. Both entry points reuse existing
panels, no new panel or top-level button: "Save as Favorite" on
`ViewScreensPanel` (next to Edit/Remove), "Load from Favorite..." on
`AddScreenPanel`. Persistence via a small JSON sidecar, same pattern
as the working-directory config file. Cross-sport-type field validity
(untested) is WARN ONLY, not blocked. See the "Favorite screen" Open
Item below for the full writeup. Prior rev (47, 2026-08-15) follows.*

*Doc rev 47 — refreshed 2026-08-15. **Real bug fix, Doug's report from
actually testing v0.19.1's "reduce redundant backups" fix:** it didn't
actually reduce them. Doug's test session: Stage a profile, Back,
Stage a different profile, Back, re-select the FIRST profile again --
his own terminal log showed a full "Backed up 9 profile(s)..." right
before that third selection, with no device disconnect in between.
Root cause: `ProfileListPanel.on_back()` has always routed to
"detect" (the only place that button goes), and `DetectPanel.on_show()`
has always called `on_detect(None)` unconditionally every time that
panel becomes active -- so every single "‹ Back" click from the
profile list was itself silently re-running `on_detect()`, which
v0.19.1 treated as a real "device state may have changed" event and
set `needs_backup = True` every time, regardless of whether anything
had actually changed. Fixed in `DetectPanel.on_detect()`: captures
`previous_root` before overwriting `frame.garmin_root`, and only sets
`needs_backup = True` when the root actually differs (a genuine
reconnect -- None to a path, or a different device/mount point), not
a redundant re-verification of the SAME already-connected device.
`gui_app.py` now v0.19.2. Prior rev (46, 2026-08-15) follows.*

*Doc rev 46 — refreshed 2026-08-15. **"Reduce redundant profile
backups" BUILT, Doug's go-ahead (low priority, scoped 2026-08-11).**
`ProfileListPanel` used to call `garmin_device.backup_profiles()` --
a real device read/write of every profile in `Sports/` -- unconditionally
on every visit to the panel, even a plain "go View Screens, then Back"
round-trip with zero edits; a tester reported the confusing side
effect directly. Fix: a new frame-level `needs_backup` flag (starts
`True`), reset to `True` by the two real "device state may have
changed" events -- `DetectPanel.on_detect()` on a fresh confirmed
connection, and `DeployPanel.on_check()` on a confirmed post-deploy
reconnect. `ProfileListPanel.on_refresh()`/`on_show()` collapsed into
a shared `_refresh_list(force_backup)`: an ordinary visit passes
`force_backup=False`, so a real backup only happens when
`needs_backup` is `True` (or there's no cached list yet at all); the
"Refresh (re-backup + re-list)" button passes `force_backup=True`
unconditionally, honoring its own label regardless of the flag. The
status line now distinguishes a real backup from a cached re-list, so
the skip is visible, not silent. `gui_app.py` now v0.19.1. Contained
entirely to `gui_app.py`, exactly as scoped -- no `garmin_device.py`
or CLI changes needed. Prior rev (45, 2026-08-15) follows.*

*Doc rev 45 — refreshed 2026-08-15. **"Restore a profile that's no
longer on the device" BUILT, Doug's go-ahead.** Built exactly to the
DESIGN CHOSEN back on 2026-08-11 (see the Open Item below, now marked
BUILT): `ProfileListPanel` gets a second, separate `wx.ListBox`
("Deleted, but available to restore," own header label) below the
existing "On Device" list (which itself picked up a matching header
label for visual parity) -- NOT a new button, NOT a new panel, NOT an
inline divider row -- populated from a new `garmin_device.py` helper,
`list_backed_up_profile_filenames(working_dir)` (v0.12.2), which scans
every `backups/<timestamp>/` folder and returns the union of every
`.fit` filename ever backed up, minus whatever's currently live. The
existing "Restore from Backup..." button now accepts a selection from
EITHER list (kept mutually exclusive -- selecting one clears the
other), routing to the same already-built `RestorePanel` unchanged.
Stage/Clone/View Screens stay gated to the live list only.
`RestorePanel.on_restore()`'s confirmation dialog and its status line
now say "RECREATING" instead of "REPLACING" when the selected profile
isn't currently live, citing the 2026-08-11 on-device confirmation
that `NewFiles` correctly recreates a deleted profile. `gui_app.py` is
now v0.19.0. No `garmin_device.py` CLI-facing changes beyond the one
new helper (plus its `deleted-profiles` subcommand, added the same
day). Prior rev (44, 2026-08-15) follows.*

*Doc rev 44 — refreshed 2026-08-15. **f10=32 renamed "GroupTrack" ->
"Reserved", Doug's decision.** This Conditional-only runtime record
has been present on every profile examined so far, active or not,
regardless of whether GroupTrack has ever actually been used -- that
always-present, content-independent behavior never actually confirmed
a GroupTrack identity, just an early assumption that was never
re-verified. f10=57 ("GroupTrack List," the literal on-device menu
entry for the feature) is unaffected and remains correctly
GroupTrack-specific. Doc-only in code terms -- `fit_dump.py` (now
v2.4.12) and `fit_patch.py` (now v1.14.2) had every comment/docstring
asserting the old identity corrected, `gui_app.py` (now v0.18.1) had
its two user-facing display strings updated to match; no
functional/behavioral change anywhere, `screen_type_name(32)` just
returns a different string. See "f10=32 'Reserved'... and f10=57
'GroupTrack List'" above for the full writeup. Prior rev (43,
2026-08-14) follows.*

*Doc rev 43 — refreshed 2026-08-14. **Real bug fix, Doug's report from
actually using the new Startup Message editor:** the message text
showed a blank line between every real line of his existing message,
even though the same file opened with no blank lines in BBEdit and
vi. Best-evidenced explanation, flagged honestly as inferred rather
than independently byte-confirmed (no hex dump of the real file was
taken): the file is likely CRLF-terminated, which both those editors
silently auto-normalize on open (so it looks identical to an LF file
either way), but `wx.TextCtrl.SetValue()` has documented bad behavior
when fed a string with embedded `\r\n` -- each `\r` can contribute its
own line break on top of the `\n` that follows it, exactly matching a
blank-line-per-line symptom. Fixed at the single read entry point:
`garmin_device.py`'s `read_startup_txt()` (now v0.12.1) normalizes all
line endings to plain `\n` immediately after decoding, before the
content is ever split or displayed -- fixes the display regardless of
whether the CRLF theory is exactly right, and is a safe no-op for a
file that was already LF-only. Headlessly verified both ways: a
simulated CRLF file now round-trips through `parse_startup_txt()`/
`build_startup_txt()` with zero blank lines and zero stray `\r` bytes;
the existing all-LF round-trip test is unaffected, still byte-
identical. Side effect, noted honestly: saving through this toolkit
from now on normalizes a file's line endings to LF even if it started
CRLF -- not expected to matter to the device's own boot-message
renderer (no evidence either way), but a real, deliberate departure
from a plain byte-for-byte round-trip. Prior rev (42, 2026-08-14)
follows.*

*Doc rev 42 — refreshed 2026-08-14. **`startup.txt` (custom boot
message) BUILT end to end, Doug's go-ahead.** Both real open questions
from the "startup.txt" section below (exact path, write mechanism) are
now RESOLVED via Doug's own real Edge 530 (direct `ls -l`/`cat` of the
mounted device) rather than secondhand corroboration alone: the file
lives at `garmin_root` itself (same level as `Sports`/`NewFiles`), and
a write is a direct overwrite while mounted — NOT a NewFiles import —
confirmed by the file's own on-device comment ("Allow one full power
cycle after editing for your message to be updated"). New
`garmin_device.py` (v0.12.0) functions `read_startup_txt()`/
`parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`, a
new `startup-txt` CLI subcommand, and `gui_app.py`'s (v0.18.0) new
`StartupTxtPanel`, reached via a "Startup Message..." button on
`DetectPanel`. Editable fields are the `<display=N>` seconds value and
the free-form message text; Garmin's own comment scaffolding is
preserved byte-for-byte via a split-at-last-comment parse, headlessly
round-trip-tested against Doug's real file content. Char/line-count
guidance (256 chars / 6 lines, the developer-documented reference
limits) is shown live but deliberately NOT enforced as a hard block —
Doug's own explicit call (2026-08-14): actual on-device wrapping is
character-width-dependent and can't be reliably predicted from typed
character count, so the real safety net is the automatic pre-write
backup, not a refusal to save. See "`startup.txt` — custom boot
message" below for the full technical writeup, now updated throughout
with this confirmed information. Prior rev (41, 2026-08-14) follows.*

*Doc rev 41 — refreshed 2026-08-14. **"Delete Screen" GUI wrapper
BUILT, Doug's go-ahead.** New "Remove Selected Screen" button on
`ViewScreensPanel`, next to Move Up/Down per the earlier placement
decision — completes the two-phase build plan (backend, device test,
GUI) now that both prior steps are confirmed. Reuses the exact same
two hard guards `--remove` enforces at the CLI level
(`hide_unsupported_screen_type()`/`would_hide_last_visible_screen()`),
each with its own explicit error dialog and no override, plus a
confirmation dialog stating plainly this is permanent (Restore-from-
Backup only undo). `gui_app.py` now v0.17.0. SAME COMMIT: split
`ViewScreensPanel`'s single 9-button row into two, per Doug's request
after the row ran the full window width. Prior rev (40, 2026-08-14)
follows.*

*Doc rev 40 — refreshed 2026-08-14. **Real hardware feedback on all
three items built in doc rev 39.** (1) `--remove` CONFIRMED via a real
on-device round-trip test (Doug) -- target screen correctly removed
from the on-device order, and the removed screen was wiped by NewFiles
rather than surviving as recoverable (as expected, matching
`--un-remove`'s own retirement reasoning). `fit_patch.py` now v1.14.1.
Backend + device test are both done; the `ViewScreensPanel` GUI button
is the one remaining, now-unblocked step. (2) Real bug found using the
Graph/Bars warning: the warning text blew out `EditScreenPanel`'s
window width, pushing the layout diagram off-screen -- the FOURTH time
this exact codebase has hit this bug class (see "Corrections and
lessons learned"). Fixed via `textwrap.fill()`-based hard wrapping
(new `graph_bars_warning_text()`/`GRAPH_WARNING_WRAP_WIDTH`), NOT
`wx.StaticText.Wrap()` -- deliberately, since that can't be exercised
in the dev sandbox and has documented bad behavior with pre-existing
newlines. (3) Doug felt the Back-button warning's "before returning
here" wrongly implied a resumable state -- reworded to his own more
direct wording. `gui_app.py` now v0.16.17. Full details in
`FIT_PATCH.md` doc rev 19. Prior rev (39, 2026-08-14) follows.*

*Doc rev 39 — refreshed 2026-08-14. **Three Open Items built, Doug's
prioritization pass over the pending list.** (1) `ViewScreensPanel`'s
Back-button data-loss bug (scoped 2026-08-13) is FIXED -- `on_back()`
now checks `frame.editing_path` and confirms before navigating away
(`gui_app.py` v0.16.14). (2) The Graph/Bars full-width warning (scoped
2026-08-11) is BUILT -- new `GRAPH_OR_BARS_FIELD_IDS` (`fit_dump.py`
v2.4.11, the 10 confirmed fields), new `is_position_full_width()`/
`graph_bars_warnings()` helpers derived from the existing
`LAYOUT_GRIDS` data, surfaced in `FieldPickerDialog` (a static note,
independent of placement) and `EditScreenPanel`/`AddScreenPanel` (a
context-aware warning reflecting the field's CURRENT position,
recomputed on every refresh) (`gui_app.py` v0.16.15). Headlessly
verified the layout-membership logic against real `LAYOUT_GRIDS`
geometry across several field-count/layout/position combinations. (3)
"Delete Screen"'s backend half is BUILT -- new `--remove` flag and
`remove_screen()` primitive in `fit_patch.py` (v1.14.0), mirroring
`--new-slot` in reverse (f1=0, f9/f10 cleared, f3/f7 preserved),
reusing `--hide`'s exact two hard guards
(`hide_unsupported_screen_type()`/`would_hide_last_visible_screen()`)
with no new guard logic needed, exactly as planned when this was
scoped. Headless-verified against a real profile copy: correct state
transition, f3/f7 preserved byte-for-byte, no effect on other slots,
valid CRC, and both guards block exactly as designed (tested directly
against a Map screen and a profile's last visible user screen) -- but
NOT YET VERIFIED ON REAL HARDWARE, so the GUI wrapper (`ViewScreensPanel`,
per the earlier placement decision) is still deliberately NOT built --
see its Open Item below for the two-phase plan, unchanged. `FIT_PATCH.md`
now doc rev 18. Prior rev (38, 2026-08-13) summary follows.*

*Doc rev 38 — refreshed 2026-08-13. **Clarification, not a new
finding: closes the gap the previous rev flagged.** Doug's "GroupTrack"
in his confirmed-active-Remove list meant the on-device editor's
actual label "GroupTrack List" (`f10=57`) — already covered, not a
separate untested type. The genuinely different `f10=32` GroupTrack
Conditional record never appears as a row in the on-device Data
Screens editor at all (no real `f9`), so it has no Remove-button
status to check, and it's already structurally out of reach of the
future `--remove` flag/`ViewScreensPanel`'s planned button regardless
(Conditional screens are never interactive/selectable there). Also
recorded, prompted by Doug's own question: an early, already-removed
`SYSTEM_SLOT_HINTS` hardcode once claimed "slot 10 = GroupTrack" by
message_index — confirmed WRONG on the Indoor profile (slot 10 there
is a genuine Cadence screen) and dropped from the codebase entirely;
slot/message_index numbers were never a reliable way to identify
GroupTrack or anything else, only `f10` values are. `NO_SHOW_TOGGLE_
TYPES` (Map, ClimbPro) is now documented as the COMPLETE confirmed
Remove-block set, no remaining gap. Updated the canonical Map/ClimbPro
section, both "Delete Screen" Open Item paragraphs, and `fit_patch.py`
(now v1.13.2, doc-only) to match. Prior rev (37, 2026-08-13) summary
follows.*

*Doc rev 37 — refreshed 2026-08-13. **Remove availability for named
screen types RESOLVED (Doug, confirmed directly on-device).** Of the
common Garmin Edge special/named screens, Map and ClimbPro are the
ONLY two with Remove disabled -- Elevation, GroupTrack, Cycling
Dynamics, Lap Summary, Virtual Partner, Compass, and Segment all show
an active Remove option. This is the exact same two-type boundary
`fit_patch.py`'s `NO_SHOW_TOGGLE_TYPES` already hard-codes for the
Show Screen toggle (`{25, 104}`) -- Hide and Remove share the
identical availability boundary for these types. Closes the open
question the "Delete Screen" Open Item and its `ViewScreensPanel`
placement decision both flagged as needing an answer: the future
`--remove` flag's type-check guard can reuse `NO_SHOW_TOGGLE_TYPES`
directly rather than needing a separate census. One small gap flagged,
not closed: GroupTrack List (`f10=57`) wasn't part of Doug's tested
list, still needs its own confirmation. Updated the canonical Map/
ClimbPro reference section, the "Delete Screen" Open Item (both the
guard-reuse paragraph and the placement-decision paragraph), and
`fit_patch.py`'s `NO_SHOW_TOGGLE_TYPES` comment (now v1.13.1,
doc-only) to match. Prior rev (36, 2026-08-13) summary follows.*

*Doc rev 36 — refreshed 2026-08-13. **"Delete Screen" placement
decided (Doug, recorded ahead of building it).** `ViewScreensPanel`
(the screen order view), not `EditScreenPanel` -- a new "Remove
Selected Screen" button next to the existing Move Up/Down buttons,
reusing that panel's already-proven row-select-then-act pattern
(`on_row_selected()`/`on_row_deselected()`), plus a confirmation
dialog stating plainly this can't be undone except via
Restore-from-Backup. Confirmed this is a strong structural fit, not
just workable: Delete is a list-level operation like Add/Move Up/Down,
not a screen property like Show/Hide (which is why Show/Hide lives in
`EditScreenPanel` instead). Surfaced one concrete nuance this
placement exposes: `screens_list` includes named Garmin screen types
(Map, ClimbPro, etc.) alongside plain user screens, so the button will
need its own type-check guard, not just the last-visible-screen guard
-- reinforcing the open "can named types even be Removed on-device"
question as something to resolve before or during the build, not
after. Still backend-first per the two-phase discipline -- nothing to
wire up yet until `--remove` exists and is confirmed on real hardware.
See the Open Item below for the full update. Prior rev (35,
2026-08-13) summary follows.*

*Doc rev 35 — refreshed 2026-08-13. **`--un-remove` RETIRED entirely
(Doug's decision, `fit_patch.py` now v1.13.0).** Reasoning: Restore-
from-Backup already covers real recovery from an accidental delete at
the whole-profile level (confirmed on real hardware), so a per-screen
un-remove was never load-bearing; `--un-remove` also carried a
confirmed historical device-side data-loss hazard (pre-v1.12.0,
root-caused to the same f10=0 collision `--new-slot` had) that was
never re-verified live after the general fix; and Garmin's own editor
doesn't offer an un-remove workflow either -- Hide (temporary) and
Remove + Add New (permanent) are its only two lifecycle actions. This
resolves the "final call deferred" note the "Product note on
`--un-remove`" section had carried since 2026-08-05. Removed the flag,
its `--new-slot` mutual-exclusion check, and its Removed-state
validation from `fit_patch.py`; updated `fit_dump.py` (v2.4.10) and
`gui_app.py` (v0.16.13) comments that referenced it; `FIT_PATCH.md`
(now doc rev 17) keeps the old OPTIONS entry as a marked-RETIRED
historical record rather than deleting it outright. One clarifying
nuance recorded in the "Product note" update, not a disagreement with
the decision: the specific NewFiles mechanism Doug described isn't
quite how this project's own earlier testing had characterized the
purge behavior, but the decision to retire stands on solid independent
grounds regardless. Updated the "Delete Screen" Open Item to reflect
that its future `--remove` flag was always going to be one-way by
design -- no change to that plan. Prior rev (34, 2026-08-13) summary
follows.*

*Doc rev 34 — refreshed 2026-08-13. **"Delete Screen" scoped (Doug's
request, not yet built).** This closes a gap `MVP_SCOPE.md` has
tracked as open since early in the project ("Remove a screen -- not
yet built"). Good news: Garmin's own editor really does expose Remove
as a permanent counterpart to Hide (see the "Product note on
`--un-remove`" finding), so this fills a real feature-parity gap
rather than inventing new behavior, and the existing last-visible-
screen guard (`would_hide_last_visible_screen()`) is documented as
already covering Remove's identical on-device floor-of-one rule, not
just Hide's -- no new guard logic needed there. The real work is a
brand-new `--remove` flag in `fit_patch.py` (mirrors `--un-remove` in
reverse: f1=0, f9/f10 cleared, f3/f7 preserved) -- genuinely new,
unverified write-path code, not GUI wiring around an already-proven
backend like Restore/Clone had. Known risk carried over from earlier
testing: any NewFiles deploy purges the Removed-state list regardless
of trigger, so a toolkit-deleted screen likely won't survive as
`--un-remove`-recoverable after its own deploy -- matches Garmin's own
"permanent" framing, but means Restore-from-Backup (whole profile) is
the only real undo path, not a per-screen undo. See the Open Items
entry below for the full backend/guard/GUI breakdown and the two-phase
build path (headless-verify the new flag, then a real on-device
round-trip, before any GUI wrapper). Prior rev (33, 2026-08-13)
summary follows.*

*Doc rev 33 — refreshed 2026-08-13. **Second real bug, same test
session: `install.sh` v1.0.1 died with `PIP_EXTRA[@]: unbound
variable`** the moment it tried to install `garmin-fit-sdk`, right
after cleanly passing the v1.0.1 CLT fix (Doug had run `xcode-select
--install`, Homebrew python3 3.14 detected fine). Root cause: bash
3.2 -- confirmed for real via Doug's `bash-3.2$` prompt, macOS's
actual stock `/bin/bash` -- has a genuine, long-documented bug where
`set -u` throws unbound-variable on an EMPTY array's `[@]` expansion
instead of expanding to nothing (fixed upstream in bash 4.4, 2016;
macOS still ships 3.2 for GPLv3-avoidance reasons). `PIP_EXTRA=()`
plus `"${PIP_EXTRA[@]}"` when `--upgrade` wasn't passed (the normal
case) hit this exactly. Invisible in the dev sandbox because that
sandbox runs bash 5.1.16, which doesn't have the bug -- a real,
now-identified gap between sandbox and real-hardware test coverage.
Fixed in v1.0.2: `PIP_EXTRA` array removed entirely, replaced with a
`pip_install()` function branching on `$UPGRADE` directly -- zero
arrays left in the script (`grep '\[@\]'` confirms), so the bug class
is eliminated structurally, not patched around. Tried to get a real
bash 3.2 into the sandbox to close the coverage gap properly (compile
from source) -- blocked by the sandbox's network allowlist (GNU
mirrors all returned `blocked-by-allowlist`); fell back to structural
elimination plus this being a well-known, well-documented historical
bash bug. Re-verified both the plain-install and `--upgrade` paths in
the dev sandbox. Not yet re-confirmed end-to-end on Doug's Mac past
this fix. See the toolkit table entry below for the full writeup.
Prior rev (32, 2026-08-13) summary follows.*

*Doc rev 32 — refreshed 2026-08-13. **Real bug found via real Mac
hardware test: `install.sh` v1.0.0 crashed silently on a fresh
machine with no Xcode Command Line Tools installed.** Doug's report:
`bash-3.2$ ./install.sh` got through the platform check and "Found
python3" cleanly, then died right there -- only output was macOS's own
`xcode-select: note: No developer tools were found, requesting
install` message, no error from the script itself, prompt just
returned. Root cause: invoking python3 for its version check was the
first real python3 execution, and a CLT-less `/usr/bin/python3` can't
actually run -- it exited non-zero, `set -e` turned that into a silent
stop. The script's only CLT check existed, but was buried inside the
"Python < 3.10" warning branch, reachable only AFTER a version check
that could never succeed without CLT in the first place -- backwards
ordering. Fixed in v1.0.1: Command Line Tools check moved to its own
step immediately after the platform check, before python3 is touched
at all, with a clear message (install dialog may have just opened --
let it finish, or run `xcode-select --install` yourself, then
re-run). Also added defense-in-depth error handling around the
version-check python3 invocation itself, and a `--version` flag.
Verified the fix in the dev sandbox (both the no-CLT-stops-cleanly
path and the CLT-present-proceeds-normally path); not yet re-tested
end to end on Doug's Mac. Bonus confirmation: Doug's `bash-3.2$`
prompt confirms the script really is running under real macOS stock
bash 3.2 as designed, not just assumed compatible. See the toolkit
table entry below for the full writeup. Prior rev (31, 2026-08-13)
summary follows.*

*Doc rev 31 — refreshed 2026-08-13. **Pre-release consistency check,
one cosmetic fix.** Doug asked directly whether `fit_dump.py` and
`gui_app.py` reflect all field IDs gathered so far, ahead of testing
`install.sh` on real Mac hardware and a possible v1.0.1 tag. Confirmed
yes -- `fit_dump.py` v2.4.9 (117 entries, field 320 "Perf. Conditioning"
the latest); `gui_app.py` has no separate field ID list, it imports
`FIELD_ID_NAMES` live, so it can never go stale on data. Did catch one
purely cosmetic drift while checking: `FieldPickerDialog`'s docstring
still said "105 confirmed entries" (last updated at v0.16.5, before
the 2026-08-11 batches). Fixed, `gui_app.py` now v0.16.12. Prior rev
(30, 2026-08-13) summary follows.*

*Doc rev 30 — refreshed 2026-08-13. **New `install.sh` setup script**
(real user request: "make it easier to plug and play"). macOS-only
per Doug's decision (matches the toolkit's current real platform
support -- Windows/Linux device detection still isn't implemented).
Checks python3 presence/version (hard floor 3.9, warns plus checks for
Xcode Command Line Tools below 3.10, since `wxPython` only ships
pre-built PyPI wheels from 3.10 up -- verified directly against PyPI's
JSON API), creates/reuses a dedicated `.venv` (user-confirmed choice
over the README's existing bare system-Python `pip install
--break-system-packages` pattern, which this also sidesteps entirely
since a venv's pip is never PEP-668 externally-managed), installs
`garmin-fit-sdk`/`wxPython` into it, then imports both back to confirm
the install actually works, not just that pip exited 0. Idempotent,
`--upgrade`/`--help` flags. Verified in the dev sandbox (Linux) with
the platform gate patched out: version-check arithmetic, venv
creation, pip upgrade, and `garmin-fit-sdk` install/import all
confirmed working; `wxPython`'s install predictably fails there
(no macOS wheel, no GTK headers to build from source in this sandbox)
-- expected, not a real bug, since real macOS would fetch the prebuilt
wheel instead. Not yet run on Doug's actual Mac. README.md Setup/GUI
sections now lead with it, manual `pip install` steps kept as an
explicit fallback. See the toolkit table entry below for the full
writeup. Prior rev (29, 2026-08-11) summary follows.*

*Doc rev 29 — refreshed 2026-08-11. **Field 320 corrected.** Doug
reported the "Conditioning" field's full concept name is "Performance
Conditioning," but the actual on-device DATA FIELD display reads
"Perf. Conditioning" (abbreviated). Renamed to match this toolkit's
established convention of naming fields as they display on-device
rather than by their full/conceptual name -- same convention behind
"Lap Dist." and "Dest. Location" (`fit_dump.py` now v2.4.9, still 117
entries, rename only; `FIT_PATCH.md` now doc rev 16). Prior rev (28,
2026-08-11) summary follows.*

*Doc rev 28 — refreshed 2026-08-11. **Field 49 corrected; important
methodological caution for the Graph/Bars marker theory.** Doug
followed up by deploying field 49 (old placeholder "Avg Speed (Alt)")
into a full-width screen slot and visually confirming on-device: it's
plain text, no graph or bars. Renamed to "Avg Speed"
(`fit_dump.py` now v2.4.8, `FIT_PATCH.md` now doc rev 15). Flagged as
a caution, not a falsification -- unlike 23/348/349, there's no record
this field's old "(Alt)" label was ever a literal on-device marker
transcription, so it may simply have been an old, undocumented naming
guess. Practical takeaway for the eventual GUI feature: the confirmed
Graph/Bars set should only grow from fields where a real on-device
marker was directly observed and recorded, not from any old name that
happens to contain "(Alt)". Prior rev (27, 2026-08-11) summary
follows.*

*Doc rev 27 — refreshed 2026-08-11. **12 new field IDs, plus 3
placeholder names corrected now that the "*"/"(Alt)" marker is
understood.** Doug's continued census (separate session): 2 Course Pt
Dist., 15 Lap HR, 18 Lap %Max HR, 32 Next Pt Location, 165 Last Lap
HR, 347 HR Bars, 350 Power Bars, 433 Anaerobic TE, 452 Respiration,
478 EPOC, 495 60s Grit, 497 60s Flow. Corrected: 23 "Heart Rate (Alt)"
→ "HR Zone Graph", 348 "Speed *" → "Speed Bars", 349 "Cadence *" →
"Cadence Bars" — confirming the marker denotes Graph/Bars-type
rendering. `fit_dump.py` now v2.4.7 (117 confirmed entries, no
collisions), `FIT_PATCH.md` now doc rev 14 with a regenerated
reference table. Graph/Bars full-width warning Open Item updated with
the now-10-field confirmed set. Prior rev (26, 2026-08-11) summary
follows.*

*Doc rev 26 — refreshed 2026-08-11. **"*" marker mystery likely
resolved; Graph/Bars full-width warning scoped.** Doug confirmed the
long-open "*"/"(Alt)" field-name marker (fields 348/349, 23, 49, and
the self-evidently-named Graph cluster) denotes a Graph- or Bars-style
rendering that needs a full-width screen slot, falling back to plain
text otherwise — corrected throughout (`fit_dump.py` now v2.4.6,
`FIT_PATCH.md` now doc rev 13, doc-only, not independently re-verified
by this project yet). New Open Item: a GUI warning surfacing this,
fully computable from `LAYOUT_GRIDS`'s existing row-width data with no
new geometry model needed — see "Graph/Bars full-width warning" below.
Prior rev (25, 2026-08-11) summary follows.*

*Doc rev 25 — refreshed 2026-08-11. **Redundant-backup reduction
scoped and batched as low priority.** A tester's complaint (repeated
"Backed up X profile(s)..." messages just from reselecting a different
profile, no edits involved) traced to `ProfileListPanel` re-backing-up
everything on every visit rather than once per meaningful device-state
change. Scoped correctly (the naive "once ever" version would silently
skip the backup taken right after a real deploy — the most important
one). Doug's call: worth doing, but low priority — his own real usage
numbers (~1MB backup folder even after heavy testing, ~4-5GB across
1098 files over this project's whole prior history) confirm disk
footprint was never really the issue. He also flagged a possibly
better-value alternative: a real backup retention/pruning routine,
already an existing (until now unscoped) Open Item — updated with his
numbers and his own suggestion that it may be worth doing first. Prior
rev (24, 2026-08-11) summary follows.*

*Doc rev 24 — refreshed 2026-08-11. **Two field names corrected,
real user report.** Fields 58 and 87 were transcribed as "Lap
Timer"/"Last Lap Timer" — a mistaken analogy to the separate,
correctly-named field 56 "Timer" — but a closer on-device relabeling
check found the real display text is "Lap Time"/"Last Lap Time," no
"r." Corrected in `fit_dump.py` (now v2.4.5, `FIELD_ID_NAMES` still
105 entries, none added/removed) and `FIT_PATCH.md` (now doc rev 12).
Field 56 "Timer" is unaffected. Prior rev (23, 2026-08-11) summary
follows.*

*Doc rev 23 — refreshed 2026-08-11. **Design chosen for "restore a
deleted profile"; both it and `startup.txt` deferred to a future
batched release.** `ProfileListPanel` gets a second list section below
the existing on-device one ("Deleted, but available to restore"),
implemented as a separate widget rather than an inline divider row
(deliberately avoiding a repeat of this session's wx.ListCtrl/ListBox
issues) — the existing Restore button/`RestorePanel` need no changes
at all, since neither has ever cared whether a filename is currently
live. Doug's decision: hold off building this and `startup.txt` for
now (a confirmed-working CLI workaround exists via `garmin_device.py
deploy`), watch for anything else that surfaces over the next few
days, and fold whatever accumulates into one future release. Prior rev
(22, 2026-08-11) summary follows.*

*Doc rev 22 — refreshed 2026-08-11. **"Restore a deleted profile"
fully de-risked.** Doug directly tested the exact scenario that
enhancement is about — `garmin_device.py deploy` with a backup of a
profile deliberately deleted from the device, targeting that
now-absent filename — and confirmed via on-device verification that
NewFiles correctly recreates it. This is a stronger, more direct
confirmation than rev 21's Clone Profile finding (same underlying
mechanism, but this is the literal restore-a-deleted-profile path, not
an analogous one). The backend/CLI side of this feature is now fully
proven; only the GUI entry-point gap remains. `gui_app.py` reached
v0.16.11 (doc-only). Prior rev (21, 2026-08-11) summary follows.*

*Doc rev 21 — refreshed 2026-08-11. **Clone Profile's real-hardware
status corrected.** Doug reported (after the fact) that Clone Profile
has actually been confirmed working on real hardware for some time —
two clones deployed via NewFiles under brand-new filenames, `Clonebox`
and `CloneRoad` — which had never been logged here; this document (and
README.md) had been carrying a stale "not yet tested through the
actual GUI" note against it. Corrected throughout. This also resolves
what had just been flagged (rev 20, below) as the single biggest open
risk for the newly-scoped "restore a deleted profile" enhancement,
since both features write a NewFiles filename not currently present in
`Sports/` — that mechanism is now confirmed working. `gui_app.py`
reached v0.16.10 (doc-only, logging this confirmation). Prior rev (20,
2026-08-11) summary follows.*

*Doc rev 20 — refreshed 2026-08-11. **Repo is live on GitHub; first
external user-reported gap scoped.** A user working from
`garmin_device.py` (GUI restore path not yet used) found that a
profile deleted from the device has no way to be selected for Restore
in the GUI — correctly diagnosed as a real gap (`ProfileListPanel`'s
list is sourced entirely from the live device), not user error.
Scoped, not yet built — see "Restore a profile that's no longer on the
device" under Open Items below; flags a shared unconfirmed-on-real-
hardware risk with Clone Profile (both write a NewFiles filename not
currently present in `Sports/`). Prior rev (19, 2026-08-11) summary
follows.*

*Doc rev 19 — refreshed 2026-08-11. **Pre-publish/GitHub-release
housekeeping pass.** Landed: `LICENSE` (MIT, copyright `Doug
(fullcarbonbike)`), a License/Disclaimer section merged into
`README.md`, `gui_app.py`'s v0.16.7 window-title rename ("Activity
Profile Screen Editor for Garmin Edge"), v0.16.8's About button/dialog,
and v0.16.9's working-directory fix — cross-platform default
(`~/GarminBackups`) plus persistence across restarts via a small
config file, replacing a hardcoded Mac-specific path that reset every
launch. Also landed (discussed and documented, neither built yet): a
Windows-support scoping assessment — device detection is the only real
gap, `_find_garmin_root_windows()` is a clearly-marked stub and
everything else in the toolkit is already OS-agnostic — and a scoping
writeup for a tester-requested "Favorite Screen" feature (save a
screen's field set + layout, reuse it across other profiles). See
"Publishing to GitHub" and the two newest entries under Open Items
below for full detail. Prior rev (18, 2026-08-06) summary follows.*

*Doc rev 18 — refreshed 2026-08-06. **Clone Profile is now built in
the GUI** (`gui_app.py` v0.16.0, `ClonePanel`) — see "Clone Profile"
below. This was the last item in the GUI feature backlog; all ten
agreed flow steps plus Restore-from-Backup and Clone are now built,
headless-verified, with only Clone's real-hardware GUI pass still
outstanding. Prior rev (17, 2026-08-05) summary follows.*

*Doc rev 17 — refreshed 2026-08-05. **MAJOR REVERSAL: Adding a
brand-new screen via `fit_patch.py --new-slot` is now CONFIRMED
WORKING.** The "reliably fails" conclusion in rev 16 and earlier —
documented as settled and root-caused to the NewFiles delivery
mechanism itself — has been superseded. Root cause, now confirmed: an
f10 IDENTITY COLLISION. `--new-slot`'s old default silently wrote
f10=0, and f10=0 is a real, specific identity ("Screen 1") that almost
every real profile already has — not an inert sentinel as assumed at
the time. `fit_patch.py` v1.12.0 adds `next_available_field10()` and
uses it as the new auto-default. Live-tested 2026-08-05 on
`CyclingRoadSandbox`: a new screen (fields Gears/Front Gear, f10=2,
"Screen 3") survived a full deploy → restart → remount cycle intact,
independently re-confirmed against the live mounted device by both
`fit_dump.py` and `garmin_device.py`. See "Adding a new screen" below
for the full rewrite, including an honest note on a loose end this
doesn't fully explain. Prior rev (16, 2026-08-04) summary follows.*

*Doc rev 16 — refreshed 2026-08-04. Major update from a side-thread
field-exploration session (see `MEMO_FINDINGS.md`): **f10 is now
CONFIRMED as a real, content-independent screen TYPE identifier** —
named Garmin types (Map=25, Virtual Partner=26, GroupTrack=32,
Compass=35, Elevation=44, Segment=56, GroupTrack List=57, Cycling
Dynamics=63, Lap Summary=74, ClimbPro=104) get a fixed global code;
plain user screens use a per-profile counter shown on-device as
"Screen N" (f10=N → "Screen N+1"). This solves the previously-open
"tell a user screen from a Garmin screen" problem outright. Landed
this session: `fit_dump.py` 2.4.2 (bug fix — `classify_screens()` no
longer misses screens with no `f3`, e.g. Virtual Partner; added
`NAMED_SCREEN_TYPES`/`screen_type_name()`, `screens` output now shows
real type names; 86 confirmed field IDs, with 84/87 — Last Lap
Dist/Last Lap Timer — closing the toolkit's last open field-ID
mystery), `fit_patch.py` 1.11.0 (same `f3`-gate bug fixed in
`read_current_state()`; `would_hide_last_visible_screen()` rewritten
to count only real user screens via f10, fixing a confirmed
undercounting bug; `check_system_screen_guard()` also made f10-based,
fixing a real reported false positive where a confirmed user screen
still triggered the old "possibly a system screen" pause; NEW
`hide_unsupported_screen_type()` hard-blocks `--hide` on Map or
ClimbPro entirely, confirmed via direct on-device inspection that
neither has a Show Screen toggle at all — see CORRECTIONS), a
correction to the Screen State Model's Removed-state persistence
claim, and `gui_app.py` 0.6.3 (ViewScreensPanel gets a Type column,
EditScreenPanel's title shows the real screen name, all guard-warning
dialogs reworded to match the confirmed model, and a third HARD block
against hiding Map/ClimbPro at all). Not auto-synced with ongoing
work — regenerate from `MEMORY_LOG.md` (or the live project context)
if this drifts again.*

Reverse-engineering project to read and edit Garmin Edge 530 Activity
Profile screen configurations (data screens, fields, layouts, display
order, and the device connection/write workflow itself) — with the
goal of a GUI editor to replace the on-device menu workflow for the
single most-requested capability on Garmin's own forums: reordering
screens and fields from a computer.

**Status:** The full CLI toolkit is validated end-to-end on real
hardware. Every core capability — field edits (both replacing a
screen's whole field list and increasing its field count), layout
A/B, show/hide, screen reordering, multi-step chaining before a single
write, and profile clone-and-retarget — has a confirmed real-device
round trip, not just a simulated one. The device connection layer
(`garmin_device.py`) is fully validated end-to-end: detect → list →
backup → stage → patch → deploy → eject → power-button restart →
remount → re-verify. Field ID census: 80 of an estimated ~200 possible
IDs confirmed. **GUI implementation is underway**: `gui_app.py` covers
steps 1-8 of the agreed flow (detect device + show device info; list
profiles via an automatic backup of every profile; select a profile
and stage it for editing; view its current screens read-only, with
screen-level Move Up/Down reordering as of v0.7.0; a real
Add-New-Screen panel as of v0.8.0, not a redirect -- see "Adding a new
screen" below), plus step 6 -- editing one screen's fields
(reorder/add/remove/change-type as of v0.9.0), A/B layout with a live
visual diagram of the on-device grid layout (see "On-device layout
geometry", below), and a guarded Show/Hide toggle -- all built and
syntax-verified, including a fix for a window-close crash found during
real use, and CONFIRMED on real hardware for Add-New-Screen and Change
Type both. Steps 7-8 (v0.10.0): a "Review & Deploy..." pre-flight
panel showing a diff against the staged file plus a real CRC check --
see "Agreed high-level flow" below for why this ended up as a pure
review+verify step rather than the originally-planned "apply changes"
step; the diff itself became a plain-English, per-screen change
summary in v0.12.0 after real user feedback that the byte-level diff
was too technical for the GUI's actual audience (a rider, not a
developer). Step 9 (v0.13.0): a `DeployPanel` writes the working copy
to NewFiles/, then walks the user through eject and reconnect via a
manual "Check for Reconnected Device" button rather than background
polling -- see "Agreed high-level flow" below for the reasoning.
Post-write verification (step 10, v0.14.0) automatically re-pulls the
live profile the moment reconnect is confirmed and compares it against
what was sent, sharing the same plain-English comparison as steps 7-8.
Restore-from-Backup (v0.15.0) is built too -- a `RestorePanel` lists a
profile's backup history with a per-candidate screen summary and hands
off straight to `DeployPanel`, skipping the staged-vs-editing review
entirely since it doesn't apply to a restore. Clone Profile (v0.16.0)
is also built -- a `ClonePanel` clones the selected profile under a new
display name (`fit_clone_profile.py`, CLI-validated on real hardware
already) with live filename-collision checking, and hands off straight
to `DeployPanel` the same way Restore does. **All ten flow steps, plus
Restore and Clone, are now built -- this closes out the GUI's full
feature backlog** -- see "Agreed high-level flow" below.

---

## Background

The Edge 530 stores each Activity Profile as a `.FIT` file at
`Garmin/Sports/<ProfileName>.fit`. Screen layouts are stored using an
**undocumented** message type (`data_screen`, global `mesg_num=14`)
absent from Garmin's public FIT SDK. Everything below was reverse-
engineered by making a single, isolated change (on the device itself,
or via a custom byte-patcher), pulling the resulting file, diffing it
byte-for-byte against a known "before" state, and confirming the
change matches exactly what was intended before generalizing.

Dev environment: working directory is
`/Volumes/UserDCbu/dougcurtis/garmindev` (a separate external volume,
deliberately not under `$HOME`, to avoid home-volume space
constraints), with a working `.venv` containing `garmin_fit_sdk`. Git
repo lives here specifically — an earlier `git init` accidentally
scoped to the home directory and was caught before any commit landed
(an obviously-too-broad untracked-file list was the tell), then fixed
by deleting that `.git` and reinitializing in `garmindev` directly.
Backups and staged edits live in `/Volumes/UserDCbu/dougcurtis/GarminBackups`
— one level above `garmindev`, same volume, outside the git repo
entirely (cleaner than relying on `.gitignore` alone). Use this same
path consistently for both backup and stage.

---

## Toolkit

| File | Version | Purpose |
|---|---|---|
| `install_windows.bat` | 1.0.1 | **CONFIRMED on real Windows 11 hardware (v1.0.1, 2026-08-22).** Doug uninstalled `garmin-fit-sdk`/`wxPython` via `py -3 -m pip uninstall -y`, confirmed both failed to import, then ran this script fresh: Python detection, version check, install, and post-install import verification all worked cleanly against real Python 3.14 (prebuilt `wxPython` 4.3.1 wheel available, confirming the 3.10-floor wheel-availability assumption holds at the current end of that range too). One benign pip warning seen and confirmed harmless: `wxPython`'s bundled demo/dev console scripts (`helpviewer.exe`, `img2py.exe`, `wxdemo.exe`, etc.) installed to a Scripts folder not on PATH -- unused by this toolkit, `gui_app.py` never touches that folder. Double-click launch of `gui_app.py` in File Explorer reconfirmed working post-reinstall -- Windows showed a one-time "how do you want to open this file" dialog on the very first double-click; Doug picked Python, checked "Always," and every double-click since has launched directly with no dialog. Doug confirmed this dialog was NOT something he recalled seeing during his original install either -- most likely just normal first-use `.py` file-association behavior triggered by this being the first `.py` file double-clicked since a change somewhere in that chain (fresh pip reinstall, or simply the first time Windows needed to ask), not something this script causes or needs to handle. This script is no longer "written blind" -- confirmation-only entry, no code changed. Original entry (v1.0.0, Doug's go-ahead, 2026-08-20) -- prompted by real external feedback (a rider who wanted to try the toolkit found the install burden more than he wanted to take on) plus Doug's own real-hardware discovery that double-clicking `gui_app.py` in File Explorer already works once dependencies are installed. Scoped directly against Doug's own confirmed real Windows 11 install (see Doc rev 54/README.md's Windows Setup section) rather than guessed at. Checks for the `py` launcher (falling back to `python.exe`) and a version >= 3.10; if missing or too old, detects and guides -- opens the python.org download page, prints instructions, stops -- rather than silently downloading/running a Python installer, Doug's explicit call (`AskUserQuestion`, chose "Detect and guide" over "Auto-download and silently install"), matching `install.sh`'s own treatment of missing Xcode CLT: no elevation, nothing modified without the user's own click. One deliberate platform-specific DEVIATION from `install.sh`'s design: the 3.10 floor is a HARD requirement here (`install.sh` only warns-and-offers-to-continue at the same threshold on macOS) -- reason: `wxPython` ships pre-built wheels for 3.10+ on both platforms, but building from source below that needs a full C++ toolchain, which is a single free command (Xcode CLT) on macOS versus a multi-GB Visual Studio Build Tools install on Windows; "continue anyway, pip will build from source" is reasonable on macOS and a bad offer on Windows for this toolkit's actual audience. Installs `garmin-fit-sdk`/`wxPython` directly with NO virtual environment -- also deliberately different from `install.sh` -- because Doug's real Windows install skipped one entirely, and a venv would break the double-click-`gui_app.py` behavior his install produced (only works because the python.org installer associates `.py` files with the SAME python `pip install`, no venv, puts packages into). Verifies both packages import after install; `--upgrade`/`--help`/`--version` flags; `cd /d "%~dp0"` at the top so it runs from its own folder even if launched via "Run as administrator" (which can otherwise start a batch file in `C:\Windows\System32`). **Written blind with respect to Windows batch syntax and NOT YET CONFIRMED on real hardware** -- there is no `cmd.exe` in this project's dev sandbox at all, so unlike `garmin_device.py`'s `_find_garmin_root_windows()` (which got a headless `ntpath`-monkeypatched dry run before Doug's real hardware confirmed it), this script has had no dry run of any kind; needs Doug's real run on the laptop before it can be trusted the way every other confirmed-on-hardware piece of this toolkit now is. Doug's own plan: uninstall the toolkit from the Windows laptop and re-test a fresh install specifically via this script before the next release. README.md's Windows Setup section now leads with it, keeping the manual sequence as a documented, already-confirmed fallback. Prior entry: n/a (new file). |
| `install.sh` | 1.0.2 | macOS-only setup script, real user request ("make it easier to plug and play"). Bash, `set -euo pipefail`, written to also run correctly under macOS's stock bash 3.2 (no associative arrays, no `[[ ]]` regex-only features from bash 4+) even though it was authored/tested against bash 5 in the dev sandbox -- **CONFIRMED running under real bash 3.2 on Doug's actual Mac** (`bash-3.2$` prompt visible in his terminal output), so that compatibility goal is now verified, not just theoretical. **REAL BUG FOUND AND FIXED (v1.0.1, 2026-08-13):** Doug's first real-hardware test was on a genuinely fresh Mac laptop that had never had Xcode Command Line Tools installed. v1.0.0 got through the platform check and "Found python3" cleanly, then died silently: invoking `python3 -c '...'` for the version check triggered macOS's own `xcode-select` "note: No developer tools were found, requesting install" message on stderr, python3 itself exited non-zero (CLT-less `/usr/bin/python3` can't actually run), and `set -e` turned that into an immediate, unexplained script exit -- no `die()` message, nothing actionable, just the raw OS message and a dead prompt. Root cause: the script's only CLT check (`xcode-select -p`) was buried inside the "Python < 3.10" warning branch, reachable only AFTER a successful version check -- exactly backwards, since CLT has to exist before python3 can run AT ALL on a fresh install, not just before building wxPython from source. Fix: moved the Command Line Tools check to its own step, immediately after the platform check and before python3 is touched in any way -- on failure it now explains plainly that macOS may have just opened an install dialog (let it finish) or to run `xcode-select --install` directly, then re-run. Also hardened the version-check python3 invocation itself with explicit `if ! ... ; then die ...` error handling (previously bare `set -e`-reliant) as defense-in-depth against any other python3-fails-to-run scenario, not just this one. Added `SCRIPT_VERSION`/`--version` (this class of tool had no version string at all before -- every other file in this toolkit tracks one). **Verified the fix in the dev sandbox** by reproducing both branches: no-`xcode-select`-on-PATH now stops cleanly at the new step with the intended message (confirmed NOT reaching python3 at all); a stubbed `xcode-select -p` that reports success now proceeds correctly through python3 detection, version check, venv creation, and `garmin-fit-sdk` install/import exactly as before. **SECOND real bug found and fixed, same test session (v1.0.2, 2026-08-13):** Doug ran `xcode-select --install`, got past the v1.0.1 fix cleanly (CLT found, python3 found -- Homebrew's, freshly installed, reporting 3.14 -- version check passed), then hit a new failure the instant the script tried "Installing garmin-fit-sdk...": `./install.sh: line 174: PIP_EXTRA[@]: unbound variable`. Root cause: `PIP_EXTRA=()` followed later by `"${PIP_EXTRA[@]}"` when `--upgrade` wasn't passed (the common case) means expanding a genuinely EMPTY array -- and bash 3.2 has a real, long-documented bug where `set -u` treats an empty array's `[@]` expansion as an unbound variable and errors, instead of correctly expanding to zero words the way POSIX/modern bash does. Fixed in bash 4.4 (2016), but macOS still ships 3.2 as `/bin/bash` for licensing reasons (GPLv3 avoidance) and has for over a decade -- exactly the environment `install.sh` was written to target, confirmed for real this session via Doug's own `bash-3.2$` shell prompt in his pasted output. This bug was INVISIBLE in the dev/test sandbox specifically because that sandbox runs bash 5.1.16 (`bash --version` confirmed), which doesn't have it -- every earlier "verified in the dev sandbox" claim for this script was genuinely accurate for what it tested, it just couldn't have caught this one, a real gap in the sandbox-vs-real-hardware coverage that's now closed. Fix: removed `PIP_EXTRA` entirely, replaced with a `pip_install()` shell function that takes a package name and internally branches `if (( UPGRADE )); then ... --upgrade ...; else ...; fi` -- no array anywhere in the script now, so this isn't a patch around one instance, the whole bug class is structurally gone. Re-verified in the dev sandbox: both the plain-install path and `--upgrade` path exercised end to end (confirmed `garmin-fit-sdk` installs/imports correctly either way; `wxPython`'s build-from-source failure at that point remains the expected, sandbox-is-Linux-not-macOS limitation, unrelated to this fix). Attempted to get real bash 3.2 into the dev sandbox for a true repro (compile from source) specifically to close this coverage gap properly -- blocked by the sandbox's network allowlist (ftp.gnu.org and mirrors all returned `blocked-by-allowlist`); relying instead on eliminating the array construct structurally (confirmed via `grep '\[@\]'` returning zero matches in the whole file) plus the well-documented nature of this specific historical bash bug. Not yet re-confirmed end-to-end on Doug's Mac past this fix. Prior entry (v1.0.0, 2026-08-13, initial version): macOS-only setup script. Sequence: (1) `uname -s == Darwin` gate, dies with a clear message otherwise -- explicitly scoped to macOS only per Doug's decision, since `garmin_device.py`'s Windows path is still a `NotImplementedError` stub and Linux isn't even stubbed; cross-platform version deferred until Doug has Windows hardware to test against; (2) `python3` presence check; (3) version check -- hard floor 3.9 (dies below that), warns below 3.10 specifically because PyPI's `wxPython` wheels are only pre-built for cp310 and up (verified directly against the live PyPI JSON API before picking this cutoff -- 3.9 and older would silently fall through to a from-source build, 10-20 min, requiring the Command Line Tools); (4) creates/reuses a dedicated `.venv` in the toolkit's own directory via `python3 -m venv` -- deliberate choice over installing to system/Homebrew Python (Doug's explicit choice over the alternative), which also sidesteps PEP 668's "externally managed environment" block entirely, since a venv's own pip is never marked externally-managed -- no `--break-system-packages` needed anywhere in this script, unlike the manual README instructions it supplements; (5) upgrades pip inside the venv; (6) installs `garmin-fit-sdk` and `wxPython` into it (`--upgrade` CLI flag threads through to both if passed); (7) imports both back inside the venv's own Python and reports version strings, so a "successful" pip install that's actually broken doesn't get reported as done. Idempotent by construction. User-confirmed design decisions (2026-08-13): macOS-only for now (cross-platform revisited once Windows access exists); dedicated venv rather than the README's existing bare `pip install ... --break-system-packages` pattern, specifically to avoid touching system/Homebrew Python at all. README.md's Setup and GUI sections lead with `./install.sh`, keeping the original manual `pip install` commands as an explicit fallback. |
| `fit_raw_walk.py` | 1.0.0 | Generic FIT definition/data message byte-offset walker. No SDK dependency — needed because the SDK doesn't recognize `data_screen` at all. |
| `fit_crc.py` | 1.0.0 | FIT file CRC-16 (Garmin's nibble-table algorithm). Self-verifies against known-good files before being trusted for writes. |
| `fit_dump.py` | 2.4.25 | SDK-based (`garmin_fit_sdk`) read/inspect tool. **CONFIRMED via GUI, real hardware (v2.4.25, 2026-08-22)** -- Doug spot-checked `gui_app.py`'s field picker directly against several of the 169 confirmed entries added across the three 2026-08-20 batches (v2.4.21/2.4.23/2.4.24 below), confirming the labels shown match what's on-device -- closes the loop from "correctly typed in the dict" to "actually wired through and displayed correctly in the running GUI." No dict values changed, confirmation-only entry. Prior entry, **13 new confirmed field IDs** (v2.4.24, 2026-08-20 batch #3), Doug's cross-check of his confirmed-field list against the Garmin Edge 530 Owner's Manual's own data-field appendix, then locating each remaining gap on-device: 98 Watts/kg, 439 3s W/kg (fills the last two gaps in the W/kg family, was Avg/10s/30s only), 207-213 Power Z1-Z7, 418 Power Z8, 419 Power Z9 (Time in Power Zone 1-9, the Power-Zone analog of the existing 199-203 HR Zone 1-5 (time) fields -- 9 zones, not 5), 24 Laps and 41 Max Lap Power (resolve an earlier same-day ambiguous "Laps Max" note -- turned out to be two separate fields Doug had conflated, not one; 41 extends Power's own Lap/Max/Last-Lap set with the one remaining combination). No collisions with any existing entry (confirmed via AST parse before insertion). `FIELD_ID_NAMES` now 169 confirmed entries (was 156). Closes out the manual-appendix cross-check -- no further appendix-listed fields remain unconfirmed. One real gap still open, not part of this batch: "Trainer Resistance" -- working hypothesis, unverified, is that it needs a paired ANT+ FE-C smart trainer to appear in the on-device picker at all, the same sensor-gated pattern already documented for eBike Metrics fields; Doug doesn't currently have one to test against. Same batch, fixed a factual error in this file's own v2.4.23 comment (data-only correction, not a functional change): had wrongly said the pre-existing W/kg family included field 159 -- 159 is actually "3s Balance," an unrelated field; corrected inline. `FIT_PATCH.md`'s FIELD ID REFERENCE table regenerated to match (Doc rev 31); `gui_app.py`'s `FieldPickerDialog` docstring updated (v0.19.12, doc-only). Prior entry, **10 new confirmed field IDs** (v2.4.23, 2026-08-20 batch #2), Doug's continued field census: 265 Lap PCO, 267 Avg Right PP, 268 Lap Right PP, 269 Right PPP, 271 Lap Right PPP, 273 Avg Left PP, 274 Lap Left PP, 275 Left PPP, 277 Lap Left PPP, 440 10s W/kg. Fills out the L/R Power Phase/Peak Power Phase family alongside the existing 263/264/266/270/272/276 entries -- values are the on-device display labels (this dict's established convention); Doug also supplied each field's full concept name, recorded inline (e.g. "Avg Right PP" = "Avg Right Pwr Phase"). No collisions with any existing entry (confirmed via AST parse before insertion). `FIELD_ID_NAMES` now 156 confirmed entries (was 146). Same batch, doc-only: Doug investigated the last unmapped on-device label he'd been tracking, "Battery Status" (Lights category) -- confirmed it's an alias/duplicate menu entry that navigates straight to field 317 "Light Battery," not a separate field; noted inline at 317's entry, no new dict entry. `FIT_PATCH.md`'s FIELD ID REFERENCE table regenerated to match (Doc rev 30); `gui_app.py`'s `FieldPickerDialog` docstring updated (v0.19.11, doc-only). Prior entry, **Correction, same day, Doug's own catch** (v2.4.22, 2026-08-20): the v2.4.21 batch's "Target" was mistyped as field 512 -- the real ID is 521 (512 never existed on-device under either name, a simple mistyped digit, not a raw-ID/name mismatch the way the 2026-08-17 batch's screen-3/4 transposition was). Fixed before this ever shipped in a tagged release. Doug also confirmed, unprompted, that all 9 fields from that batch are verified against the real on-device screen -- same confirmation standard as every other batch in this dict, upgrading the batch's status from "field names, not yet independently stress-tested" to fully confirmed. No count change, still 146 entries (a corrected key, not a new/removed ID). `FIT_PATCH.md`'s FIELD ID REFERENCE table and NOTE updated to match (Doc rev 29). Prior entry, **9 new confirmed field IDs** (v2.4.21, 2026-08-20 batch), Doug's continued field census: 45 Workout Step, 100 Last Lap Power, 258 Lap Time Standing, 260 Lap Time Seated, 264 Avg PCO, 511 Workout Comparison, 521 Target (see correction above), 522 Duration, 523 Step Time. No collisions with any existing entry (confirmed via AST parse before insertion). Notable: 5 of these 9 (45, 511, 521, 522, 523) read by name as Workout/structured-step fields -- directly adjacent to this project's still-open f10=38 "Workout" SCREEN-TYPE question (`FIELD_EDIT_UNCERTAIN_TYPES`, see below and the "f10=38 'Workout' field-reading anomaly" Open Item history) -- a separate, still-unconfirmed question from these fields' own identity, which Doug's on-device verification establishes with the same confidence as any other entry here. The other 4 extend already-populated families: Power (100, matching the existing 3s/10s/30s/Lap/Avg pattern) and Cycling Dynamics (258/260/264, standing/seated lap time + PCO, alongside the existing 257/259/263/266/270/272/276 entries). `FIELD_ID_NAMES` now 146 confirmed entries (was 137). `FIT_PATCH.md`'s FIELD ID REFERENCE table regenerated to match (Doc rev 28); `gui_app.py`'s `FieldPickerDialog` docstring updated (v0.19.10, doc-only). Prior entry, **FULLY CONFIRMED via direct raw-byte inspection** (v2.4.20, 2026-08-17): `CyclingRoadRoadtemp.fit` (the original census profile, Screen 3/4 still intact at 10 fields each) came through on a second upload attempt and was dumped directly -- raw arrays slot 6 = `[150, 149, 177, 176, 43, 437, 40, 408, 411, 441]`, slot 7 = `[80, 42, 148, 147, 82, 83, 151, 161, 160, 159]` -- match all 20 corrected pairs from v2.4.19 position-for-position exactly, including 177 "Torque Effect" under its own ID, closing the one residual flag v2.4.19 was still carrying. No dict values changed -- this is the independent confirmation that was pending. Same direct byte-level verification standard as every other confirmed batch in this dict now. Prior entry, **RESOLVED** (v2.4.19, 2026-08-17): the whole 2026-08-17 batch had raw IDs and names correctly identified but WRONGLY PAIRED -- Doug's census screens 3 and 4 got transposed when the original list was written up, so all 10 IDs from one screen's block were paired with the 10 names from the other's (same 20 raw IDs, only the pairing changed, not scattered individual errors). Doug re-derived the correct pairing directly from the census screens; it resolves all three known real-device mismatches exactly (437 -> Avg W/kg, 147 -> Lap NP, 148 -> Last Lap NP). All 20 entries corrected, SUSPECT warnings removed. Not independently re-confirmed via a raw byte dump (upload sync issue this session, same class as the earlier `CyclingEbike.fit` episode) -- treated as sufficiently confirmed on the 3-for-3 match against observed device behavior. One residual flag: field 177 (now "Torque Effect") wasn't independently re-tested under its own ID after the swap was found. See the (now-resolved) Open Item and "Corrections and lessons learned" for the methodology takeaway. Prior entry, **URGENT flag, no value changes yet** (v2.4.18, 2026-08-17): Doug's real device testing found editing Screen 4 via the GUI to 437/147/148/320 ("Intensity Factor (IF)"/"Pedal Smoothness"/"Torque Effect"/"Perf. Conditioning") actually displays "Avg W/kg, Lap NP, Last Lap NP, Perf. Cond." on the device -- 3 of 4 wrong. `FieldPickerDialog` reviewed directly, no picker/write bug -- points to a census/transcription error in the original v2.4.16 batch. All 20 entries in that batch now carry a prominent SUSPECT warning pending re-verification; no dict values changed without raw-byte confirmation. See the new Open Item ("data integrity issue in the 2026-08-17 field ID batch") for the full writeup and what's needed to resolve it (a raw dump of `CyclingRoadROAD.fit`). Prior entry, real bug fix, Doug's report from checking the device (v2.4.17, 2026-08-17): field 148 was stored as "Torque Effect." -- a guessed abbreviated form, by analogy to field 320's "Perf. Conditioning" convention, added in the v2.4.16 batch below without a direct on-device check. Doug directly confirmed the real on-device text in a half-width (1/2 side-by-side) field: "Torque Effect", no trailing period. Corrected; `FIT_PATCH.md`'s FIELD ID REFERENCE table/note updated to match. No count change, still 137 confirmed entries. Prior entry, 20 new confirmed field IDs, Doug's continued field census (v2.4.16, 2026-08-17 batch) -- this project's first batch touching power-meter/Di2-electronic-shifting metrics: Balance family (42 Balance, 80 Avg Balance, 40 Lap Balance, 441 3s Balance, 411 10s Balance, 408 30s Balance), Power/W-kg (150 30s Power, 151 Max Power, 83 Avg W/kg, 159 30s W/kg), training load (149 %FTP, 43 TSS, 437 Intensity Factor (IF)), Normalized Power (176 Lap NP, 177 Last Lap NP), pedaling metrics (148 Torque Effect. -- reported full concept name "Torque Effectiveness (Torque Effect.)," stored abbreviated per this dict's on-device-display convention, e.g. 320 "Perf. Conditioning"; 147 Pedal Smoothness; 82 Power Zone), Shimano Di2 (161 Di2 Battery, 160 Di2 Shift Mode). Notable: confirms the Power family's 3s/10s/30s/Lap/Avg naming pattern (79/146, pre-existing) repeats identically for L/R Power Balance, with 42 "Balance" as the base metric mirroring 36 "Power" -- a clean, self-consistent family, not one-off guesses. No collisions with any existing entry (confirmed via AST parse before insertion). `FIELD_ID_NAMES` now 137 confirmed entries (was 117); `KNOWN_UNRESOLVED_IDS` still empty. `gui_app.py`'s `FieldPickerDialog` docstring updated to match (v0.19.5, doc-only) -- same recurring stale-count drift class as v0.16.5/v0.16.12's fixes. Prior entry, new constant, Doug's go-ahead (v2.4.15, 2026-08-16): `FIELD_EDIT_UNCERTAIN_TYPES = {38}` ("Workout"), backing a new `EditScreenPanel` warning (`gui_app.py` v0.19.4) -- Doug raised a real concern that this screen doesn't appear in the on-device scroll list during a normal ride (same conditional-trigger family as ClimbPro/Segment) and separately noticed an empty `Workouts/Guided`/`Scheduled` folder structure at `garmin_root`, asking whether "Workout" needs loaded workout data to mean anything. Confirmed against Garmin's own Edge 530 manual: structured Workouts (Training > Workouts) are a separate subsystem entirely, dynamically displaying "each step of the workout, the target (if any), and current workout data" only while one is actively running -- almost certainly what f10=38 renders, matching every piece of evidence gathered (empty Workouts folders, no on-device field-editing option, byte-identical field content to Cycling Dynamics). Prior entry (v2.4.14, 2026-08-16): CORRECTION to v2.4.13, once Doug's `CyclingEbike.fit` was actually inspected: the new `NAMED_SCREEN_TYPES` keys were WRONG (39/59/96, read off this tool's own `f10+1` display fallback rather than the raw byte) -- corrected to the REAL f10 values, 38 "Workout", 58 "eBike Metrics", 95 "STEPS Metrics (Shimano)". Also RESOLVED the f10=38 "Workout" field question: CONFIRMED via direct raw-byte comparison that its field-ID array is byte-for-byte identical to Cycling Dynamics' (f10=63) on the same profile -- real, accurately-read data, not a `classify_screens()` bug; two more exact-duplicate pairs found the same way (Removed slots vs. the currently-active eBike Metrics/STEPS Metrics records). See PROJECT_NOTES.md "Corrections and lessons learned" and the "f10=38 'Workout' field-reading anomaly" Open Item for the full writeup. Prior entry (v2.4.13, SUPERSEDED, wrong f10 keys, kept for the record): New confirmed f10 screen types (2026-08-16 batch, `CyclingEbike.fit`): `NAMED_SCREEN_TYPES` gains 39 "Workout", 59 "eBike Metrics", 96 "STEPS Metrics (Shimano)" -- no collision with any existing entry or with `FIELD_ID_NAMES` (field ID 39 already exists there as "Lap Power," a numeric coincidence across two independent namespaces, not a real collision). f10=39 "Workout" is FLAGGED, not resolved -- no `classify_screens()`/field-reading behavior changed, only the display name. Prior entry (v2.4.12, 2026-08-15): Rename only, Doug's decision: `NAMED_SCREEN_TYPES[32]` renamed "GroupTrack" -> "Reserved" -- this Conditional-only runtime record is present on every profile seen so far regardless of GroupTrack usage, so its real purpose was never actually confirmed; every comment/docstring in this file asserting the old identity updated to match (f10=57 "GroupTrack List" unaffected, remains correctly GroupTrack-specific). No functional change -- `screen_type_name(32)` just returns a different string. Prior entry (v2.4.11, 2026-08-14): new `GRAPH_OR_BARS_FIELD_IDS` set (the 10 fields confirmed to need a full-width screen slot to render as a graph/bar -- 23, 343-350, 368), kept separate from `FIELD_ID_NAMES`, backing `gui_app.py`'s new Graph/Bars full-width warning (v0.16.15). No `FIELD_ID_NAMES` entries changed, still 117. Prior entry (v2.4.10, doc-only, 2026-08-13): the verbose `screens` subcommand's "Removed screens" note referenced `fit_patch.py`'s now-RETIRED `--un-remove` flag -- updated to point at Restore-from-Backup instead (see `fit_patch.py` v1.13.0). Subcommands: `dump`, `unknown`, `diff`, `screens` (sorted by true display order, shows all three screen states plus real f10-derived screen-type names). `classify_screens()`/`active_field_ids()`/`screen_type_name()` are print-free functions, importable directly by the GUI. `NAMED_SCREEN_TYPES` holds the 10 confirmed f10 codes. `FIELD_ID_NAMES` has 117 confirmed entries (v2.4.9, real user report: field 320 corrected "Conditioning" -> "Perf. Conditioning" -- full concept name is "Performance Conditioning," but the actual on-device DATA FIELD display reads "Perf. Conditioning" (abbreviated), matching this toolkit's on-device-display naming convention (same as "Lap Dist.", "Dest. Location"); v2.4.8, real user report: field 49 corrected "Avg Speed (Alt)" -> "Avg Speed" -- deployed into a full-width slot and visually confirmed on-device as plain text, no graph/bars; a METHODOLOGICAL CAUTION for the Graph/Bars marker theory, not a falsification -- no record exists that this field's old "(Alt)" label was ever a real on-device marker transcription the way 23/348/349 were; v2.4.7, 2026-08-11 batch: 12 new IDs -- 2, 15, 18, 32, 165, 347, 350, 433, 452, 478, 495, 497 -- plus 3 corrected placeholder names (23 "Heart Rate (Alt)" -> "HR Zone Graph", 348 "Speed *" -> "Speed Bars", 349 "Cadence *" -> "Cadence Bars"), confirming the "*"/"(Alt)" marker denotes a Graph/Bars-style field needing a full-width screen slot, else falls back to plain text; v2.4.6, doc-only: the long-open "*" marker mystery on fields 348/349 is likely resolved -- Graph/Bars-style rendering needing a full-width screen slot, else falls back to plain text, per Doug's report; v2.4.5, real user report: fields 58/87 corrected from "Lap Timer"/"Last Lap Timer" to "Lap Time"/"Last Lap Time" -- a mistaken analogy to the separate, correctly-named field 56 "Timer," caught via a closer on-device relabeling check; 2026-08-10 batch: 18 IDs -- 7, 30, 31, 39, 50, 57, 61, 62, 63, 67, 86, 88, 94, 95, 295, 442, 443, 445 -- confirmed by arranging two screens to 10 fields each on a real profile for this census, entering each field by its on-device name, then cross-referencing raw ID against known on-screen position via the GUI) -- `KNOWN_UNRESOLVED_IDS` is still empty. |
| `fit_patch.py` | 1.14.2 | Surgical byte-level patcher/writer. Doc-only, no functional change, Doug's decision (v1.14.2, 2026-08-15): comments referencing the f10=32 Conditional record as "GroupTrack"/"the GroupTrack Conditional record" updated to "Reserved" -- `read_current_state()`'s docstring, `NO_SHOW_TOGGLE_TYPES`' comment block, and `count_shown_active_screens()`'s docstring all updated to note the record's real purpose was never actually confirmed rather than asserting a GroupTrack identity (display name itself lives in `fit_dump.py` v2.4.12's `NAMED_SCREEN_TYPES` -- this file has no code path that special-cases f10=32, only prose describing it). f10=57 "GroupTrack List" untouched. Prior entry (v1.14.1, doc-only, 2026-08-14): `--remove` CONFIRMED via a real on-device round-trip test (Doug) -- target screen correctly removed from the on-device order, and the removed screen was wiped by NewFiles rather than surviving as recoverable, matching `--un-remove`'s own retirement reasoning. STATUS/BUGS updated from unverified to CONFIRMED; GUI wrapper (`ViewScreensPanel`) is now unblocked but still unbuilt until asked for. Prior entry (v1.14.0, 2026-08-14): `--remove`/`remove_screen()` -- the backend half of "Delete Screen" -- transitions a slot to Removed (f1=0, f9/f10 cleared, f3/f7 preserved), reusing `hide_unsupported_screen_type()`/`would_hide_last_visible_screen()` directly as its two hard guards. Headless-verified (correct state transition, guards block Map and a last-visible-user-screen exactly as designed, valid CRC). Prior entry (v1.13.0, 2026-08-13, Doug's decision): `--un-remove` RETIRED entirely -- Restore-from-Backup already covers real recovery (whole-profile undo, confirmed on real hardware), `--un-remove` had a confirmed historical device-side data-loss hazard never re-verified after the v1.12.0 fix, and Garmin's own editor has no un-remove workflow either (see PROJECT_NOTES.md "Product note on `--un-remove`" for the full history). Removed the flag, its `--new-slot` mutual-exclusion check, its Removed-state validation, and simplified every `args.new_slot or args.un_remove` conditional down to plain `args.new_slot` -- confirmed via grep that zero real code references remain. No behavior change to `--new-slot`. `next_available_field10()` auto-assigns a collision-free screen identity for `--new-slot`, replacing the old hardcoded f10=0 default -- root-caused and RESOLVED the long-standing "Add New Screen always fails" limitation; CONFIRMED working via live on-device round-trip (2026-08-05). `check_system_screen_guard()` (`--force` to override) is f10-based and CERTAIN for any Active screen, not a guess -- old content-pattern/low-field-count heuristics kept only as a fallback for Removed-state slots with no real f10. `would_hide_last_visible_screen()` is a HARD, non-heuristic guard (no `--force`) blocking `--hide`/`--disable` on a profile's last remaining REAL USER screen, correctly counted via f10. `hide_unsupported_screen_type()` is a SECOND hard guard (no `--force`) blocking `--hide` on Map or ClimbPro entirely -- CONFIRMED via direct on-device inspection that neither has a Show Screen toggle at all, on any profile type. |
| `fit_chain.py` | 1.0.0 | Chains multiple `fit_patch.py` operations into one file before a single device write, avoiding a restart per change. CRC-verified after every step. |
| `fit_clone_profile.py` | 1.0.1 | Clones a profile under a new display name by patching `sport_mesgs[0].name` — a standard, SDK-known message, unlike `data_screen`. v1.0.1 (2026-08-19): new reference constant `PROFILE_NAME_MAX_CHARS = 15`, backed by Doug's real on-device test -- Garmin's own Activity Profile name editor hard-blocks typing a 16th character (typing past it switches straight to the checkmark/complete control instead of accepting more input). Distinct from, and much stricter than, the existing `NAME_FIELD_SIZE` byte-capacity check (31 usable bytes) `patch_profile_name()` already enforces safely -- a name between 16 and 31 bytes would patch through fine at the byte level, but Garmin's own software could never have produced one, so how the device renders it is genuinely untested. No functional change to `patch_profile_name()` itself -- this is a new constant only; `gui_app.py`'s `ClonePanel` (v0.19.9) does the actual enforcing, mirroring how `NO_SHOW_TOGGLE_TYPES` (`fit_patch.py`) backs a GUI-side hard block from a confirmed device fact. |
| `garmin_device.py` | 0.12.8 | Device connection layer: detect (+ `get_device_info()` device identification), list, backup (lineage-tracked), stage, write to `NewFiles` with read-back verification, eject/remount-wait. `screens` subcommand shells out to `fit_dump.py screens` directly -- no separate classification logic to fix. **v0.12.8 (2026-08-25), new feature, Doug's go-ahead -- backup retention/pruning.** New `prune_old_backups(working_dir, older_than_days, dry_run=True)` deletes (or, under `dry_run`, just reports) entire `working_dir/backups/<timestamp>/` folders older than `older_than_days` -- decided by each folder's OWN NAME (its `%Y%m%d_%H%M%S` timestamp), not filesystem mtime, since mtime can reset on a copy/restore of the working directory while the embedded name is always correct by construction. Design chosen from three options put to Doug: time-based folder deletion [CHOSEN], keep-latest-N-per-profile (rejected -- each `backups/<timestamp>/` folder snapshots EVERY profile together via `backup_profiles()`, not one folder per profile, so per-profile retention would mean deleting individual files out of a shared folder rather than whole folders, plus awkward interaction with `list_backup_history()`'s existing consecutive-byte-identical display dedup), and keep-only-the-single-latest-backup (rejected -- cuts against Restore-from-Backup's whole reason for existing, and Doug's own real usage numbers -- ~1098 backed-up `.fit` files, ~4-5GB, over this project's entire prior history -- confirmed disk space was never the actual constraint that would justify losing all older restore points). Manual-only, Doug's explicit choice -- no automatic/silent pruning anywhere; the only entry points are a deliberate user action (new `prune-backups` CLI subcommand, or `gui_app.py` v0.19.19's new "Clean Up Old Backups..." dialog), same posture as every other destructive action already in this toolkit (Restore, permanent Remove, Favorite overwrite). New `prune-backups <working_dir> [--older-than-days N] [--dry-run] [--yes]` CLI subcommand (default 30 days, matching the GUI dialog's own default): always previews the folder list + total size first, then -- unless `--dry-run` -- prompts an interactive [y/N] confirm before deleting (same style as `eject_device()`'s own confirm), skippable via `--yes` for scripting. New `_format_bytes()` helper (plain stdlib, no new dependency), shared by the CLI summary and `gui_app.py`'s dialog. Any folder whose name doesn't parse as the expected timestamp format is left alone entirely -- defensive against anything unexpected ever ending up in `backups/`. Headlessly verified: a fake working_dir with folders at several ages (90/45/31/10/0 days) plus one non-timestamp junk folder correctly identifies only the >=30-day folders for both dry-run preview and real deletion, leaves recent/today/junk untouched, and a second run against an already-pruned tree correctly reports nothing left to prune; the CLI subcommand exercised end-to-end (dry-run, `--yes` deletion, re-run confirms empty) against a real temp directory. Prior entry follows. **v0.12.7 (2026-08-24), real safety fix, Doug's go-ahead.** `write_to_newfiles()` gained an optional `working_dir` parameter: if given, and a profile currently exists on the device under `target_profile_filename`, it's copied to `working_dir/backups/<timestamp>/` (same naming convention `backup_profiles()` uses, so it's immediately browsable via the normal Restore-from-Backup picker -- not a separate parallel mechanism) BEFORE being overwritten. Closes a real gap surfaced while scoping "Import an external profile" (see Open Items below): every GUI-driven write already gets this protection for free, since visiting the profile list always runs `backup_profiles()` first -- but a bare CLI `deploy` call bypassed that entirely, so `garmin_device.py deploy <patched> <existing_filename>` with no prior `backup` call would overwrite a live profile with zero safety net. Deliberately NOT a hard block or an interactive confirm: overwriting the target filename is the normal, INTENDED outcome of every deploy (that's how an edit gets written back), so blocking or prompting would break the core workflow for no benefit -- the fix is a silent, automatic backup instead, matching the posture of every other write path in this toolkit. `working_dir` stays optional (not required) so existing callers/scripts that omit it keep working exactly as before. CLI `deploy` subcommand gained a new optional `--working-dir DIR` flag wired straight through; omitting it now prints a one-line NOTE to stderr about the missing safety net rather than staying silent about the gap. `gui_app.py`'s `DeployPanel` (the single GUI call site for `write_to_newfiles()`, covering every write path) now passes `frame.working_dir` too, for defense-in-depth on top of the profile-list backup it already gets. Headlessly verified: a fake `garmin_root` with an existing target profile correctly gets backed up before overwrite (byte-identical, correct timestamp folder); omitting `working_dir` is a byte-identical no-op to pre-fix behavior; a target filename with no existing profile correctly skips the backup attempt. Prior entry, confirmation-only (v0.12.6, 2026-08-19), Windows support CONFIRMED on real hardware -- -- Doug ran `detect`, `screens` (both CLI tools), and the full GUI workflow (add a screen to the Sandbox profile, deploy, restart, NewFiles round-trip) against a real Edge 530 on a real Windows 11 laptop; all worked with zero code changes beyond copying the toolkit's `.py` files over (one early CLI-only test that copied just this file hit `ModuleNotFoundError: No module named 'fit_dump'`, since `get_device_info()` imports it -- resolved by copying the whole folder). `D:\Garmin` has `Sports`/`NewFiles` flat at the drive root, resolving the v0.12.5 open question -- Level 1 of the two-level check matched; Level 2 (one-subfolder-deep) is still unexercised on real hardware. Confirmation-only entry, no code changed. Prior entry, new feature, Doug's go-ahead (v0.12.5, 2026-08-17): `_find_garmin_root_windows()` implemented -- was `find_garmin_root()`'s one deliberately-stubbed half (the module's own docstring calls this "the ONLY function that needs a platform-specific implementation"), raising `NotImplementedError` until now. Scans drive letters C: through Z: (A:/B: skipped, historically floppy) for the same `Sports`/`NewFiles` structure check the macOS half uses, at both the drive root and one level of subfolder -- mirrors macOS's own two-level check exactly, since Doug's real Edge 530 nests `Sports`/`NewFiles` one folder down under the mounted volume on his Mac; whether Windows exposes the same nesting or puts them flat at the drive letter is the biggest open unknown and the first thing real-hardware testing should settle. Deliberately plain `os.path.exists()`/`os.listdir()` iteration rather than a Windows API (`win32api.GetLogicalDriveStrings()`) -- avoids adding `pywin32` as a new dependency, at the minor cost of checking 24 drive letters unconditionally. Per-letter `OSError` (e.g. an empty card reader) caught and skipped, same defensive posture as the macOS half's `PermissionError` handling. NOT YET confirmed against real Windows hardware -- headlessly verified only, via `ntpath`-monkeypatched fake drive trees (nested case, flat case, no-device case, flaky-drive case all correct; A:/B: skip and C:-Z: order confirmed; `find_garmin_root()`'s dispatch to this function on `platform.system() == "Windows"` confirmed). Doug has Windows 11 access lined up to run `garmin_device.py detect` as the real test. Prior entry, real bug fix, Doug's report from actually using the GUI (v0.12.4, 2026-08-16, same-day follow-up to v0.12.3): even after v0.12.3's smart-char fix, 3 literal "?" kept reappearing at the very front of `startup.txt`'s preserved header comment line -- invisible in the GUI's message editor (which only shows the editable message text), found by Doug opening the raw file in BBEdit. Different mechanism from v0.12.3: `read_startup_txt()` decodes raw bytes as ASCII with `errors="replace"`, so a leading UTF-8 BOM (3 bytes, EF BB BF, each individually invalid for ASCII) decoded to 3 U+FFFD characters, which rode through the "preserve header byte-for-byte" split/rejoin (preserved from the DECODED string, not the raw bytes) and got re-encoded to 3 literal "?" bytes on every save -- self-perpetuating, since the header is never regenerated, only carried forward. `read_startup_txt()` now strips a leading UTF-8 BOM before decoding, making it a silent no-op. Matches Doug's own observation exactly: manually removing the "?" via BBEdit and re-saving (no BOM) stopped them from reappearing on the next `gui_app` edit. BOM's original source still unknown/unconfirmed -- possibly an editor that defaults to "UTF-8 with BOM" touching the file outside this toolkit at some point. Headlessly verified: a fake `garmin_root` with a BOM-prefixed `startup.txt` now reads back with zero "?"/U+FFFD in the header; a file with no BOM is a byte-identical no-op. Prior entry (v0.12.3, 2026-08-16): new `_SMART_CHAR_REPLACEMENTS`/`_normalize_smart_chars()`, applied in `write_startup_txt()` before the ASCII encode -- reverses common macOS/Cocoa smart-substitution characters (curly quotes, en/em dash, ellipsis) back to plain ASCII, fixing a real bug where typed "..." silently became a single "?" on save (`wx.TextCtrl` on macOS auto-substitutes as you type; the old `.encode("ascii", errors="replace")` then replaced each resulting non-ASCII character with "?"). Any character outside the table still degrades honestly to "?", unchanged. See Doc rev 51 above for the full writeup. Prior entry (v0.12.2, 2026-08-15): `list_backed_up_profile_filenames(working_dir)` scans every `backups/<timestamp>/` folder and returns the union of every `.fit` filename ever backed up, regardless of current on-device presence -- filtered to `.fit` only (matching `list_profiles()`'s own convention) specifically because `write_startup_txt()` (v0.12.0) backs `startup.txt` up into this SAME folder structure, so without the filter a boot-message backup would be mistaken for a deleted profile. New `deleted-profiles` CLI subcommand for parity -- needs a connected device (to know what's live), subtracts live from all-ever-backed-up, prints the difference. Backs `gui_app.py`'s new second list in `ProfileListPanel` (v0.19.0). Headlessly verified end to end via a monkeypatched `find_garmin_root()`. Prior entry (v0.12.1, 2026-08-14, Doug's report from actually using the GUI): `read_startup_txt()` now normalizes all line endings (`\r\n` and lone `\r`) to plain `\n` immediately after decoding -- the GUI's message editor was showing a blank line between every real line of Doug's own existing message, even though the same file opened with no blank lines in BBEdit and vi (both silently auto-normalize CRLF on open, so a CRLF file looks identical to LF there; `wx.TextCtrl.SetValue()` has documented bad behavior with embedded `\r\n`, matching the symptom exactly). Not independently byte-confirmed via a hex dump, flagged honestly as the best-evidenced explanation rather than a certainty -- the fix is a safe no-op either way for a file that was already LF-only. Headlessly verified against a simulated CRLF file (zero blank lines, zero stray `\r` after the fix) with the existing all-LF round-trip test unaffected. Side effect: saving through this toolkit now normalizes a file's line endings to LF even if it started CRLF. Prior entry (v0.12.0, 2026-08-14, Doug's go-ahead): `startup.txt` support -- `read_startup_txt()`/`parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`, plus a new `startup-txt` CLI subcommand (view, or `--write FILE` to overwrite). CONFIRMED via Doug's own real Edge 530 (direct `ls -l`/`cat` of the mounted device): the file lives at `garmin_root` itself, same level as `Sports`/`NewFiles`/`Settings` -- no `find_garmin_root()` change needed. CONFIRMED write mechanism, from the file's own on-device comment ("Allow one full power cycle after editing for your message to be updated"): a DIRECT overwrite while mounted, not a NewFiles import -- `write_startup_txt()` backs up any existing file first, into the same `working_dir/backups/<timestamp>/` structure `backup_profiles()` already uses. `parse_startup_txt()`/`build_startup_txt()` split/rejoin the file at its last comment block -- Garmin's own instructional text is preserved byte-for-byte, only the `<display=N>` value and the free-form message are ever regenerated -- headlessly round-trip-tested byte-identical against Doug's real file. `STARTUP_TXT_MAX_CHARS`/`STARTUP_TXT_MAX_LINES` are reference constants only, not enforced -- Doug's own call, since actual wrapping is character-width-dependent. Headlessly verified: parse/build round-trip; `write_startup_txt()`'s backup-then-overwrite via a fake filesystem `garmin_root` (plain file I/O, no real device needed here unlike every other write in this file); the `startup-txt` CLI subcommand end-to-end via a monkeypatched `find_garmin_root()`. Backs `gui_app.py`'s new `StartupTxtPanel` (v0.18.0). Prior entry (v0.11.0): `list_backup_history(working_dir, profile_filename)` lists every backup of one profile under `working_dir/backups/<timestamp>/`, newest first, de-duplicating consecutive byte-identical entries (a real characteristic of this app: every visit to the GUI's profile list re-backs-up all profiles, not just on real changes, so an untouched profile accumulates many identical timestamped backups per session -- collapsing those keeps the history meaningful, one entry per REAL change). Backs the GUI's `RestorePanel`; also a new `backup-history` CLI subcommand for parity. |
| `gui_app.py` | 0.19.19 | **v0.19.19 (2026-08-25), new feature, Doug's go-ahead -- backup retention/pruning GUI.** New "Clean Up Old Backups..." button on `ProfileListPanel` (next to "Change...", in the working-directory row -- a working_dir-level maintenance action, not tied to any profile selection) opens a new `BackupCleanupDialog`: type a day count (default 30), see a live preview of exactly how many `backups/<timestamp>/` folders and how much disk space would be freed, then an explicit YES/NO confirm before anything is actually deleted -- same destructive-action-confirmation posture as Restore/permanent Remove/Favorite overwrite elsewhere in this app. Wraps `garmin_device.py` v0.12.8's new `prune_old_backups()` directly -- that function owns the actual folder-selection/deletion logic; this dialog is purely UI around it. Time-based-only and manual-only were both deliberate choices put to Doug and confirmed by him -- see `garmin_device.py` v0.12.8's toolkit-table entry above for the full three-options writeup. Plain `wx.TextCtrl` for the day count, not `wx.SpinCtrl` -- consistent with every other validated-text-field pattern already used elsewhere in this app (ClonePanel/ImportPanel filenames) rather than introducing an untested widget class into a file that can't be run in the dev sandbox at all. Headlessly verified: the day-count parsing/validation logic, and the preview/clean-up decision logic (both reimplemented standalone and run against the REAL `garmin_device.prune_old_backups()` against a fake `backups/` tree) all behave correctly -- invalid input disables the button with a clear message, zero matches shows "nothing to clean up," a real match previews the correct count/size and deletes only the correct folders on confirm. CONFIRMED via Doug's own real hardware test (2026-08-25). Prior entry follows. **v0.19.18 (2026-08-24), two more real bugs found via Doug's hardware testing of Import, same session as v0.19.17's deploy-path fix.** (1) Window width: the app window expanded to near-screen-width by the time Doug reached Deploy. `ViewScreensPanel`'s title_text embeds the full absolute `editing_path`, and `DeployPanel`'s status_text embeds `profile_filename` -- both plain, unwrapped `wx.StaticText` (the same recurring bug class this codebase has hit before -- see `GRAPH_WARNING_WRAP_WIDTH`'s own comment), and `_relayout()` only ever grows the window, never shrinks it, so a long value on the Screens page carries forward to Deploy even though the text visibly on screen there looked too short to explain it. Fixed via the established `textwrap.fill()`/`GRAPH_WARNING_WRAP_WIDTH` hard-wrap pattern; new `_wrap_status_paragraphs()` helper wraps each paragraph separately before rejoining with blank lines, since wrapping the whole joined string in one `textwrap.fill()` call would collapse the intentional `\n\n` breaks. (2) CONFIRMED root cause of the actual long value: `ImportPanel.on_show()` suggested `os.path.basename(source)` verbatim -- Doug picked an old file already sitting in his own `working_dir/staging/` (one of this toolkit's OWN artifacts, not a genuinely external profile) as the Import source, and its basename carried every layer of this toolkit's own internal `_staged_<timestamp>`/`_clone_<timestamp>` naming, CHAINED across repeat passes through Stage/Clone/Import, straight into the suggested filename. Doug's real case: `CyclingRoadTClone_clone_20260823_124234_staged_20260824_182004_staged_20260824_182104.fit` (92 characters), deployed to `NewFiles/`, CONFIRMED to sit there unconsumed even after a full power cycle -- the device silently declined to import it. New `strip_internal_staging_suffixes()` (module-level, next to `filename_collision_problem()`) iteratively strips these chained internal suffixes off the SUGGESTED default filename only -- the field stays free-text editable either way, so a user can always type over it. Deliberately does NOT invent/enforce a hard length limit -- the device's real filename-length tolerance for NewFiles import isn't independently confirmed anywhere (Doug's own point: "I'm not sure how the total .fit filename works"), so this fixes the one concrete, reproducible cause actually found rather than guessing at a number; see the new Open Item below for the still-open question. Both fixes headlessly verified (suffix-stripping against Doug's own real 92-character filename plus single-layer/untouched/false-positive cases; wrap-width math confirmed <=42 chars/line with paragraph breaks preserved); real GUI behavior needs Doug's own run. Prior entry follows. **v0.19.17 (2026-08-24), real bug fix, Doug's report from actually using Import External Profile right after it shipped.** The Screens review page for a freshly imported profile had no way to reach Deploy ("Review & Deploy..." never enabled), and going Back silently dropped the staged import with no warning. Root cause: `ImportPanel.on_import()` left `editing_path` at `None`, correct for the normal Stage-for-Edit flow (staged file already matches the device) but wrong for Import, where the staged file is content the device has never had at all -- it needs to be deployable immediately, before any screen edit. Now creates the scratch working copy right away and sets a new `frame.import_pending` flag; `PreflightPanel`'s deploy gating (previously pure byte-diff) now also allows deploying a byte-identical freshly-imported file, with accurate messaging instead of "nothing to deploy"; the Back-button warning fires correctly for an abandoned import too, with import-specific wording. `ViewScreensPanel.on_discard()` no longer re-strands the session either -- for an import it re-copies from the staged file instead of nulling `editing_path` outright, so Deploy stays reachable after discarding screen edits. `import_pending` is cleared alongside `editing_path` by `frame.discard_edits()` (already called on deploy-done, re-staging a different profile, Restore, and Clone), so it can't leak into an unrelated session. Headlessly verified via a standalone simulation of the import/discard/deploy-gating logic; real GUI behavior needs Doug's own run. Prior entry follows. **v0.19.16 (2026-08-24), real bug fix, Doug's report from actually using Favorite Screen right after it shipped.** `ViewScreensPanel.on_save_favorite()` let a second Save silently overwrite an existing favorite with zero warning -- since it's a single slot by design (Doug's own 2026-08-15 call, Open Items "Favorite Screen" below), an accidental second Save loses the first favorite for good with no undo path. Now checks `load_saved_favorite()` FIRST, before reading anything about the currently-selected screen -- if a favorite already exists, a YES/NO confirm names how many fields it has and which profile it was captured from; canceling costs nothing, the selected screen's own data is never even read in that case. No change to save/load semantics -- still exactly one slot, still overwritten on confirm. Doug's own explicit scope for this fix: add the warning, nothing more -- he separately floated a possible FUTURE idea (not scoped, not built, logged only) of a `GarminBackups`-style `favorites/` folder alongside the existing `staging/`/`backups/` structure, to hold multiple named favorites if this feature turns out to be popular -- his own framing: a sport/discipline with similar screen needs could get a quick-replicate option across several profiles instead of rebuilding it by hand in the on-device menu each time, and overwriting the single slot already covers that same use case today, just without the ability to keep more than one at once. See the new Open Item below for the full future-idea note. Compiled clean; AST-confirmed no duplicate methods introduced. Real GUI behavior needs Doug's own run. Prior entry, **v0.19.15 (2026-08-24), new feature, Doug's go-ahead: Import an external profile.** Closes the gap in Open Items "Import an external profile" below -- before this, the GUI had no `wx.FileDialog` anywhere, every source in every panel (Stage/View, Clone, Restore) was a list selection populated from what this toolkit already knew about. New "Import Profile..." button on `ProfileListPanel` (always enabled, unlike its siblings -- there's nothing to select first) opens a `wx.FileDialog` (*.fit filter), hands the picked path to `frame.import_source_path`, navigates to a new `ImportPanel`. New module-level `filename_collision_problem(filename, known_profiles)`, extracted from `ClonePanel`'s own `_filename_problem()` (now a thin wrapper) so Clone and Import share ONE collision rule rather than two that could drift -- hard-blocks (not warns) a filename that already exists on the device, same as Clone always has. `ImportPanel.on_import()` calls `garmin_device.stage_for_edit()` directly on the external path -- same lineage-sidecar treatment as any other staged file, honestly recording the real external source -- then routes to the normal "screens" (`ViewScreensPanel`) review step, NOT straight to Deploy like Clone/Restore (those source from already-known-safe content; an external file is unverified, and `ViewScreensPanel`'s existing `decode_file()` try/except already handles a genuinely invalid file with no new validation needed). Headlessly verified: `filename_collision_problem()` matches `ClonePanel`'s pre-refactor behavior exactly (empty/path-separator/wrong-extension/case-insensitive-collision all correctly rejected, clean filename accepted); `stage_for_edit()` against a fake external file lands it byte-identical in staging with a lineage sidecar correctly recording the external path. Prior entry, **v0.19.14 (2026-08-24), new feature, Doug's go-ahead: Favorite Screen.** Closes Open Items "Favorite Screen" below -- a SINGLE favorite slot (Doug's design decision, 2026-08-15), not a named list, so no management UI needed. New module-level `load_saved_favorite()`/`save_favorite()` (small JSON sidecar, `~/.garmin_screen_editor_favorite.json`, same best-effort/never-raise pattern as `load_saved_working_dir()`/`save_working_dir()`). `ViewScreensPanel` gets "Save as Favorite" next to Edit Selected Screen (same row-select-then-act pattern, enabled/disabled in lockstep with `edit_btn`/`remove_btn` everywhere those toggle) -- captures the selected screen's field IDs + layout variant directly from the current working file, rejects 0-field screens (Map/Compass etc.) with a clear message. `AddScreenPanel` gets "Load from Favorite..." next to Change Type -- pre-fills `self.field_ids`/`self.layout_variant` (falling back to layout A if the saved B variant isn't valid for the loaded field count), then falls through the SAME already-confirmed add-screen path unchanged, no new patch-layer logic. Cross-profile risk is WARN ONLY, Doug's explicit call -- this toolkit has no per-sport-type field validity data to actually enforce correctness, only enough to flag "captured from a different profile, worth a look." Headlessly verified: load/save round-trip exact; a second save correctly overwrites the first (confirms single-slot semantics); corrupt/missing/empty-field-list favorite all correctly return None without raising. Prior entry, **v0.19.13 (2026-08-24), defense-in-depth safety fix:** `DeployPanel.on_write()` now passes `working_dir=self.frame.working_dir` to `garmin_device.write_to_newfiles()` (v0.12.7) -- see that file's own changelog entry for the full safety-net writeup this backs. No new UI, purely a backend call-site update. All three same-day entries: compiled clean; AST-confirmed no duplicate methods introduced anywhere; real GUI behavior needs Doug's own run, wxPython can't be installed in the dev sandbox. Prior entry (v0.19.12): wxPython GUI. Cosmetic doc-only fix (v0.19.12, 2026-08-20): `FieldPickerDialog`'s docstring said "156 confirmed entries" -- stale after `fit_dump.py` v2.4.24's third 2026-08-20 batch (Doug's Garmin manual appendix cross-check) added 13 new field IDs, bringing `FIELD_ID_NAMES` to 169. No functional change -- same recurring drift class as v0.16.5/v0.16.12/v0.19.5/v0.19.10/v0.19.11. Prior entry, cosmetic doc-only fix (v0.19.11, 2026-08-20): `FieldPickerDialog`'s docstring said "146 confirmed entries" -- stale after `fit_dump.py` v2.4.23's second 2026-08-20 batch added 10 new field IDs (L/R Power Phase/Peak Power Phase family + 10s W/kg), bringing `FIELD_ID_NAMES` to 156. No functional change -- same recurring drift class as v0.16.5/v0.16.12/v0.19.5/v0.19.10. Prior entry, cosmetic doc-only fix (v0.19.10, 2026-08-20): `FieldPickerDialog`'s docstring said "137 confirmed entries" -- stale after `fit_dump.py` v2.4.21's 2026-08-20 batch added 9 new field IDs, bringing `FIELD_ID_NAMES` to 146. No functional change -- `FIELD_ID_NAMES` is imported live from `fit_dump.py`, so the field picker itself was never wrong, only this comment; same recurring drift class as v0.16.5/v0.16.12/v0.19.5. Prior entry, new hard block, Doug's report + direct on-device confirmation (v0.19.9, 2026-08-19): `ClonePanel`'s "New display name" field had no length check at all -- only the "New filename" field was validated (`.fit` suffix required, case-insensitive collision check against every device profile, both already correct, confirmed while scoping this). Doug found a note that Garmin limits Activity Profile display names to 15 characters; asked whether that should be soft guidance (like `startup.txt`'s unconfirmed character/line counts) or a hard block (like `NO_SHOW_TOGGLE_TYPES`'s confirmed Map/ClimbPro fact), Doug settled it with a direct real-device test: typing a 16th character in Garmin's own name editor does nothing at all -- it switches straight to the checkmark/complete control instead of accepting more input. A confirmed device fact, not a guess, so this got the hard-block treatment. New `_name_problem()` helper (same shape as the existing `_filename_problem()`) -- empty-name check plus the new length check, wired into both `_update_validation()` (now shows a live "(N/15 characters)" count on success) and `on_create()`'s own belt-and-suspenders guard. Backed by `fit_clone_profile.py` v1.0.1's new `PROFILE_NAME_MAX_CHARS` constant. Compiled clean; AST-confirmed `ClonePanel` has no duplicate methods. Real GUI behavior needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry, real bug fix, Doug's report from actually using the GUI (v0.19.8, 2026-08-19): unchecking "Show Screen" for a named Garmin type (Lap Summary, Cycling Dynamics, Elevation, and others he confirmed have an on-device checkbox) popped a dialog claiming hiding it via a raw file write was "genuinely UNTESTED" -- even though Doug had already confirmed it worked, repeatedly. Root cause: `EditScreenPanel._confirm_hide_guard()` fired for ANY named-type match from `fit_patch.py`'s `check_system_screen_guard()`, downstream of two HARD blocks in `on_show_toggle()` that already run first -- `hide_unsupported_screen_type()` (Map/ClimbPro, `NO_SHOW_TOGGLE_TYPES`, an EXHAUSTIVE list per direct on-device inspection, not a sample) and `would_hide_last_visible_screen()`. Since the Map/ClimbPro list is exhaustive, anything reaching the soft guard is, by elimination, a type with a working toggle -- the "untested" claim was already logically stale, and Doug's real-device testing across the full remaining named-type set just caught up with that fact. See PROJECT_NOTES.md Doc rev 66 for the full scoping discussion (Doug chose full removal over softening the wording). `_confirm_hide_guard()` DELETED entirely (method + its one call site in `on_show_toggle()`); hiding a named type now behaves exactly like hiding a plain user screen, no popup. The two HARD blocks (Map/ClimbPro, last-visible-user-screen) are completely untouched. The SEPARATE guard on editing a named screen's fields (`_confirm_guard()`, used by Add/Remove Field) is also untouched -- genuinely different, still-legitimate territory. Compiled clean; AST-confirmed no duplicate methods and zero remaining `_confirm_hide_guard` references anywhere in the file. Real GUI behavior needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry, real bug fix, Doug's report from actually editing one of his main profiles (v0.19.7, 2026-08-19): "Stage Selected for Edit" and "View Screens" were two separate buttons/clicks in `ProfileListPanel` -- staging set `self.staged_path`/`frame.staged_path`/`frame.profile_filename` and enabled `next_btn` ("View Screens"), but `on_profile_selected()` (fires on every list-selection change) only ever touched Restore/Clone's enabled state, never `next_btn` or the staged-profile pointers. So staging profile A, then clicking a DIFFERENT profile B in the list, left `next_btn` enabled and still pointed at A -- View Screens silently opened whichever profile was staged first, not the one visually highlighted, matching Doug's exact report. Doug asked to discuss/scope before fixing, correctly suspecting the button logic depended on the underlying CLI/backend calls; see PROJECT_NOTES.md Doc rev 65 for the full scoping discussion and Doug's chosen fix (merge Stage into View Screens, over two smaller alternatives) once `stage_for_edit()` was confirmed to be a plain local file copy with no device I/O at all. `stage_btn` removed entirely; `on_stage()` folded into `on_next()`, which now stages the currently-selected profile immediately before navigating, on every click -- no second piece of state left to go stale relative to the list selection. `next_btn`'s enabled state now follows the list selection directly, same as `restore_btn`/`clone_btn`. Compiled clean; AST-confirmed no duplicate methods, zero remaining `stage_btn`/`on_stage` references. Real GUI behavior needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry, real bug fix, Doug's report from Windows 11 testing (v0.19.6, 2026-08-19): `StartupTxtPanel.message_text` (the multiline `TextCtrl` showing `startup.txt`'s message) showed only ~2 lines on Windows vs. ~5 on the Mac for the SAME file -- no platform-specific code anywhere in this panel, so the difference traced to the control having proportion=1/EXPAND in its vertical sizer but no explicit minimum height: its actual visible size was whatever leftover space remained after every fixed-size sibling control (title, spin row, warning label, buttons), and that leftover genuinely differs by platform font metrics/DPI scaling even with identical code and window size. The "5 lines on Mac" figure documented back at v0.18.0 was never a designed guarantee, just an incidental result of the Mac's own leftover space. Fixed with `self.message_text.SetMinSize((-1, self.message_text.GetCharHeight() * garmin_device.STARTUP_TXT_MAX_LINES + 10))` -- a floor sized in actual character-height units, not a hardcoded pixel guess tuned to one machine, so the guarantee (at least `STARTUP_TXT_MAX_LINES`, 6, lines visible with no scrolling for a message at the documented guidance limit) holds on any platform's real font metrics. Proportion=1/EXPAND untouched, so the control still grows taller than this floor whenever more room exists -- Doug's Mac should now show 6 lines instead of the previous incidental 5, more room than before, not less. Compiled clean; real visual confirmation on both platforms needs Doug's own next run. Prior entry, cosmetic doc-only fix (v0.19.5, 2026-08-17): `FieldPickerDialog`'s docstring said "117 confirmed entries" -- stale after `fit_dump.py`'s 2026-08-17 batch (v2.4.16) added 20 confirmed field IDs, bringing `FIELD_ID_NAMES` to 137. No functional change -- `FIELD_ID_NAMES` is imported live from `fit_dump.py`, so the actual field picker was never wrong, only this comment; same recurring drift class as v0.16.5/v0.16.12. Prior entry (v0.19.4, 2026-08-16): `EditScreenPanel` gets a new non-blocking warning, `field_edit_uncertain_warning_text()`, backed by `fit_dump.py`'s new `FIELD_EDIT_UNCERTAIN_TYPES` set (currently just `{38}`, "Workout") -- fires only for that screen type, explaining the on-device editor offers no field editing for it at all so this toolkit's edit may have no visible on-device effect (though the write itself is mechanically safe, same proven mechanism as every other screen). Same `textwrap.fill()`/`GRAPH_WARNING_WRAP_WIDTH` hard-wrap pattern as `graph_bars_warning_text()`. Built in response to Doug's own question about the "Workout" screen's edit guard -- see PROJECT_NOTES.md Doc rev 54 and the "f10=38 'Workout'" Open Item for the full evidence chain (Garmin Edge 530 manual citation plus byte-level Cycling Dynamics field-array match). Headless-verified via a wx-module stub: `field_edit_uncertain_warning_text(38)` produces the full wrapped warning, `(63)` and `(None)` both return `''`. Compiled clean; AST duplicate-method check clean. Real GUI rendering needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry (v0.19.3, 2026-08-15): "Restore a Deleted Profile" (v0.19.0) CONFIRMED via Doug's own real GUI test -- a deliberately-deleted profile correctly appeared in the "Deleted, but available to restore" list, and restoring it worked cleanly end to end. Closes the one remaining real-GUI-behavior gap this feature was carrying. Prior entry (v0.19.2, 2026-08-15): Real bug fix, Doug's report from testing: v0.19.1's `needs_backup` fix didn't actually reduce redundant backups -- `DetectPanel.on_show()` calls `on_detect()` unconditionally every time that panel becomes active, and `ProfileListPanel.on_back()` always routes there, so every ordinary Back click was itself setting `needs_backup = True` again. Fixed by only setting it when `on_detect()`'s root actually differs from what it was a moment before (a genuine reconnect), not on every redundant re-verification of the same connected device. Prior entry (v0.19.1, 2026-08-15): "Reduce redundant profile backups" (low priority, scoped 2026-08-11) -- `ProfileListPanel` no longer calls `garmin_device.backup_profiles()` on every ordinary visit, only when a new frame-level `needs_backup` flag is set (by `DetectPanel.on_detect()` or `DeployPanel.on_check()` confirming reconnect) or there's no cached list yet; the "Refresh (re-backup + re-list)" button still always forces a real backup, honoring its own label. Contained entirely to `gui_app.py`. Prior entry (v0.19.0, 2026-08-15): "Restore a Deleted Profile," built exactly to the DESIGN CHOSEN back on 2026-08-11 -- `ProfileListPanel` gets a second, separate `wx.ListBox` ("Deleted, but available to restore," own header label; the existing "On Device" list picked up a matching header label too), NOT a new button or new panel, populated from `garmin_device.list_backed_up_profile_filenames()` (v0.12.2) minus whatever's currently live. The existing "Restore from Backup..." button now accepts a selection from either list (mutually exclusive -- selecting one clears the other), routing to the same already-built `RestorePanel` unchanged. Stage/Clone/View Screens stay gated to the live list only. `RestorePanel.on_restore()`'s confirmation dialog and status line now say "RECREATING" instead of "REPLACING" when the selected profile isn't currently live, citing the 2026-08-11 on-device confirmation that `NewFiles` correctly recreates a deleted profile. Compiled clean; AST-confirmed no duplicate classes/methods. Real GUI behavior needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry (v0.18.1, 2026-08-15): the f10=32 "GroupTrack" -> "Reserved" rename lives entirely in `fit_dump.py`'s `NAMED_SCREEN_TYPES` (`screen_type_name(32)` is read live from there); this file's own two user-facing display strings updated to match -- `ViewScreensPanel`'s "Conditional screens" summary line and a comment in `AddScreenPanel`'s screen-count logic. Prior entry (v0.18.0, 2026-08-14, Doug's go-ahead): `StartupTxtPanel` -- view/edit the device's `startup.txt` custom boot message, reached via a new "Startup Message..." button on `DetectPanel` (enabled in lockstep with `next_btn`, since both need a detected device). Built on `garmin_device.py` v0.12.0. Editable fields, per Doug's own scoping answer: the `<display=N>` seconds value (`wx.SpinCtrl`) and the free-form message text (`wx.TextCtrl`, multiline) -- everything else (Garmin's own comment scaffolding, exact spacing) is preserved byte-for-byte via `parse_startup_txt()`'s split, never regenerated from scratch. Live char/line-count guidance via a new `warning_text` label, hard-wrapped with the same `textwrap.fill()`/`GRAPH_WARNING_WRAP_WIDTH` helper the Graph/Bars warning uses (v0.16.16), to not reproduce that bug class a fifth time -- deliberately NOT a hard block on Save, per Doug's explicit call that on-device wrapping is character-width-dependent and unpredictable from typed character count; the real safety net is `write_startup_txt()`'s automatic pre-write backup, not a refusal to save. Save flow: YES/NO confirm (states plainly this is a direct device write, no NewFiles, backs up first) -> `write_startup_txt()` -> stage flips to "saved," showing eject controls (`Eject Now (diskutil)`/`I Ejected It Myself`, same pattern as `DeployPanel`, reusing `garmin_device._volume_mount_point()`) and a Done button back to Detect. Deliberately NO post-write verification step the way `DeployPanel` has one -- a boot-time message can't be read back by this app, so the eject/power-cycle instructions are the end of this flow. Back button warns on unsaved edits (same `wx.YES_NO`/`ICON_WARNING` style as `ViewScreensPanel`'s v0.16.17 fix), via a new `_is_dirty()` check against baseline values captured on `on_show()`. Compiled clean; AST-confirmed every `StartupTxtPanel` method is defined exactly once. Real GUI behavior needs Doug's own run -- wxPython can't be installed in the dev sandbox. Prior entry (v0.17.0, 2026-08-14, Doug's go-ahead): "Remove Selected Screen" on `ViewScreensPanel` -- the GUI wrapper for `--remove`, completing "Delete Screen" now that both the backend and the real device test are confirmed. Reuses `--remove`'s exact two CLI guards, each with its own error dialog and no override, plus an explicit permanent-deletion confirmation. Same commit: split the panel's single 9-button row into two, per Doug's feedback that it ran the full window width. Prior entry (v0.16.17, 2026-08-14): reworded the Back-button warning per Doug's feedback -- "before returning here" wrongly implied a resumable state; now his own direct wording, no logic change. NEW (v0.16.16, 2026-08-14): real bug found using v0.16.15's new warning -- it blew out `EditScreenPanel`'s window width (the FOURTH time this codebase has hit this bug class, see "Corrections and lessons learned"). Fixed via a new `graph_bars_warning_text()` helper that hard-wraps through stdlib `textwrap.fill()` rather than `wx.StaticText.Wrap()` (untestable in the dev sandbox, documented bad behavior with pre-existing newlines). Prior entry (v0.16.15, 2026-08-14): Graph/Bars full-width warning -- new `is_position_full_width()`/`graph_bars_warnings()` helpers, derived from `LAYOUT_GRIDS`, surfaced in `FieldPickerDialog` (static note) and `EditScreenPanel`/`AddScreenPanel` (context-aware, recomputed on every refresh). NEW (v0.16.14, 2026-08-14): real bug fix -- `ViewScreensPanel.on_back()` now checks `frame.editing_path` and confirms before navigating away, so an in-progress, undeployed edit (e.g. from Add New Screen) can no longer be silently lost by clicking Back. `EditScreenPanel`/`AddScreenPanel`'s own Back buttons deliberately untouched -- neither ever holds unpersisted state. Prior entry (v0.16.13, doc-only, 2026-08-13): two comment blocks (`describe_screen_changes()`, `DeployPanel.on_check()`) said `fit_patch.py`'s `--un-remove` was merely "not exposed in the GUI" -- updated now that it's RETIRED entirely (`fit_patch.py` v1.13.0), not just unsurfaced. No functional change -- the GUI never called `--un-remove` directly. Prior entry (v0.16.12, cosmetic doc-only fix, 2026-08-13): `FieldPickerDialog`'s docstring said "105 confirmed entries" -- stale after `fit_dump.py` grew to 117 across the 2026-08-11 batch (v2.4.7) and the field 49/320 rename-only corrections (v2.4.8/2.4.9); same class of drift already fixed once before at v0.16.5 (87->105). No functional change -- `FIELD_ID_NAMES` is imported live from `fit_dump.py`, so the actual field picker was never wrong, only this comment. Caught while confirming pre-release state ahead of a possible v1.0.1 tag (Doug asked directly whether `fit_dump.py`/`gui_app.py` reflect all field IDs gathered so far -- yes, both do; `FIELD_ID_NAMES` has no separate copy in `gui_app.py` to go stale). Prior entry (v0.16.11, doc-only, no code change): the "restore a profile no longer on the device" enhancement's one real open risk -- whether NewFiles can RECREATE a deleted profile, not just replace an existing one or accept a never-before-seen filename -- is now RESOLVED. Doug tested the exact scenario via `garmin_device.py deploy` with a backup of a deliberately-deleted profile, targeting that now-absent filename; CONFIRMED via on-device verification. Only the GUI entry-point itself remains unbuilt (see Open Items). Prior entry (v0.16.10, doc-only, no code change): Clone Profile CONFIRMED via real hardware, reported after the fact by Doug -- two working clones deployed via NewFiles under brand-new filenames (`Clonebox`, `CloneRoad`), correcting a stale "not yet tested through the actual GUI" note that had been sitting in both this table and the "DONE" section below, and resolving a previously-open question shared with the newly-scoped "restore a deleted profile" enhancement: NewFiles does correctly accept a genuinely new filename, not just a replacement of an existing one. Prior entry (v0.16.9, pre-Windows-support housekeeping): `DEFAULT_WORKING_DIR` was hardcoded to Doug's own actual Mac path (`/Volumes/UserDCbu/dougcurtis/GarminBackups`) -- harmless for Doug alone, but wrong for any other user and outright broken on Windows, where `/Volumes/...` doesn't exist. Now `os.path.join(os.path.expanduser("~"), "GarminBackups")`, resolving sanely on any OS/user. Also, `working_dir` was never persisted across restarts even after being changed via "Change..." -- every launch reset to the default. New `load_saved_working_dir()`/`save_working_dir()` persist the choice to a small JSON sidecar (`~/.garmin_screen_editor_config.json`); `MainFrame.__init__` seeds `working_dir` from the saved value if present (falling back to `DEFAULT_WORKING_DIR` only on a genuine first-ever launch), and `on_change_working_dir()` saves immediately on every pick. Both best-effort/never-raise -- a missing/corrupt config file or read-only home directory just falls back to in-memory-only behavior for that session, never blocks the app. User-confirmed design (2026-08-11) over two simpler alternatives (plain default with no persistence; first-use-only prompt) -- both would have needed the same persistence layer anyway, so this solves it for good. Prior entry (v0.16.8): "About" button on `DetectPanel` opens `AboutDialog` -- a short modal summary (name/version, "not affiliated with Garmin" trademark disclaimer, a one-paragraph note that `data_screen` was reverse-engineered via black-box observation rather than reverse-engineering Garmin's own software, MIT license mention pointing to `LICENSE`/`README.md` for the full text). Deliberately short, not an attempt to embed the full legal text verbatim -- keeps this dialog from ever needing to track the README disclaimer word-for-word. Read-only word-wrapped `wx.TextCtrl` body; as a modal dialog with its own fixed size (not embedded in `MainFrame`'s resizable sizer tree) it can't reproduce the v0.16.2/v0.16.3/v0.16.6 best-size bug class regardless, wrapping is just the right call for a paragraph this long either way. Headless-verified the template string's line-continuation formatting collapses correctly (real string-literal evaluation, not regex extraction). Prior entry (v0.16.7): cosmetic rename ahead of a possible public GitHub release -- window title changed from "Garmin Edge Screen Editor" to "Activity Profile Screen Editor for Garmin Edge" (this is an independent, unofficial project, not a Garmin product; "for Garmin Edge" is the standard nominative-fair-use naming pattern, user-confirmed over two other candidates). No functional change -- part of the same pre-publish pass as the new `LICENSE` (MIT) and the disclaimer draft, see Open Items below ("Publishing to GitHub"). Prior entry (v0.16.6): real reported bug fix that also corrects a WRONG previous fix -- v0.16.3's 460px ceiling on the Fields column stopped the frame from growing but silently broke something else: `wx.ListCtrl` clips a cell's text to its column's pixel width with no wrap/ellipsis, and the control's own horizontal scrollbar only engages when the SUM of all column widths exceeds the control's rendered area, which a single capped column mostly never triggers -- confirmed on a real 10-field screen with several of the new longer field names, only 6-7 visible, no way to see the rest, no error. New `ScreensListCtrl(wx.ListCtrl)` subclass overrides `DoGetBestSize()` to cap only the WIDTH the sizer system sees (height still comes from the normal calculation, preserving v0.11.0's grow-taller-for-more-rows intent) -- decoupling the FRAME's size from the COLUMN's width entirely, rather than trying to control one by capping the other. `ViewScreensPanel.screens_list` and `RestorePanel.history_list` (same exposure, proactively fixed too -- it had never even gotten the v0.16.3 ceiling) both switched to it. The Fields column reverted to floor-only auto-size (280px minimum, no ceiling) -- safe again now that content width can't reach the frame; genuine overflow now correctly triggers the `ListCtrl`'s real native horizontal scroll, since assigned-area-smaller-than-content is finally the true state of affairs. See PROJECT_NOTES.md "Corrections and lessons learned" for the full three-strikes story on this widget. Prior entry (v0.16.5): cosmetic doc-only fix -- `FieldPickerDialog`'s docstring said "87 confirmed entries," stale after `fit_dump.py` v2.4.4's 2026-08-10 batch of 18 new field IDs brought `FIELD_ID_NAMES` to 105; no functional change. Prior entry (v0.16.4): readability fix -- real reported feedback (with a side-by-side screenshot) that `LayoutDiagramPanel`'s cell-label text (9pt) was noticeably smaller than the rest of the window's controls. Bumped to 13pt (10pt for the italic note/placeholder text) and `SetMinSize()` from (280,220) to (340,280) for more breathing room at the bigger font in dense 8-10 field layouts. Confirmed via code review this carries NONE of the v0.16.2/v0.16.3 width-blowup risk -- `LayoutDiagramPanel` is custom-painted with an explicit per-cell clipping region, its reported size is only ever the fixed `SetMinSize()` value, never derived from font/content the way `wx.ListBox`/`wx.ListCtrl` are. One flagged trade-off to watch during testing: a longer known field name in a busy layout is now somewhat more likely to get silently clipped (no ellipsis) at the bigger font. Prior entry (v0.16.3): same-day follow-up to v0.16.2 -- the identical root cause also hit `ViewScreensPanel`'s "Fields" `ListCtrl` column, not just `EditScreenPanel`/`AddScreenPanel`'s `wx.ListBox`: a real profile with 9 of 10 fields unresolved on two screens still widened the window from "View Screens." The v0.11.1 fix's assumption -- that a report-mode `ListCtrl`'s column content never grows the frame, since its own native horizontal scrollbar takes over -- didn't hold for large enough overflow, confirmed via real testing. Fixed both the trigger and the mechanism together: the Fields column and the Conditional/Removed summary lines (`self.other_text`, a plain `wx.StaticText` with no scrollbar at all -- actually more exposed to this than the `ListCtrl` was) now use `field_name(fid, terse=True)`; `SetColumnWidth(6, wx.LIST_AUTOSIZE)`'s result is now capped on both ends -- the existing 280px floor plus a new 460px ceiling -- with overflow relying on the `ListCtrl`'s own horizontal scroll rather than a frame resize. `wx.ListCtrl` report mode has no built-in per-cell wrap (that's a `wx.grid.Grid` feature, not applied here), so cap-plus-shorten is the practical equivalent without a heavier widget swap. Prior entry (v0.16.2): real reported bug fix -- editing a screen with an unresolved/unknown field ID pushed the whole window off the left edge of the screen, with a large gap between the field list and the diagram, and the diagram column stretched wider than needed too; the oversized window then persisted across every subsequent panel. Root cause: `wx.ListBox` sizes itself to its longest item string, and `field_name()`'s default non-terse form returns a long descriptive sentence for unknown IDs (~40 chars) vs. a normal field name (~10-20 chars) -- that inflated best-size propagated through the shared-proportion `body_row` sizer (explaining why the diagram column grew too, not just the field list) into `MainFrame._relayout()`'s v0.11.0 grow-only behavior, which has no ceiling once triggered. Fixed at the source (`field_name(fid, terse=True)` in both `EditScreenPanel` and `AddScreenPanel`'s field list AND diagram labels -- "id58?" instead of the full sentence) and hardened `_relayout()` itself as defense-in-depth: growth is now clamped to the current display's usable work area, so this whole *category* of bug (any future content-driven best-size spike, not just this one) degrades to tight/scrolled content instead of an off-screen, restart-required lockout. Headless-verified (`field_name(9999, terse=True)` -> `"id9999?"`, 7 chars vs. 40 for the old form); compiled clean. Prior entry (v0.16.1): two minor UX fixes, no behavioral change -- the "no device connected" message now says "Connect your Garmin Edge device via USB" instead of naming the 530 specifically (detection has always been structure-based, not model-specific -- see "Model portability" note below); the window title now shows the running version (`f"Garmin Edge Screen Editor v{__version__}"`) so it's visible in-app, not just in the file. **Covers steps 1-10**, plus Restore-from-Backup and Clone Profile as sibling actions to editing: detect, list+backup, select+stage, view screens (Type column showing real f10-derived screen names, plus screen-level Move Up/Down reordering), add a brand-new screen, edit one screen's fields (reorder/add/remove/change type), A/B layout (live visual diagram), and Show/Hide, review accumulated changes, deploy to the device, post-write verification, restore any profile from its backup history, and clone a profile under a new name. **This closes out the GUI's full feature backlog -- nothing left unscoped.** NEW (v0.16.0): `ClonePanel` -- "Clone..." on `ProfileListPanel` patches `sport_mesgs[0].name` via `fit_clone_profile.py`'s `patch_profile_name()` (a completely different message than `data_screen` -- already CONFIRMED full-fidelity on real hardware at the CLI level, see MVP_SCOPE.md "Clone-and-retarget"). Live filename-collision validation against `frame.known_profiles` (kept fresh by `ProfileListPanel.on_refresh()` every visit) blocks "Create Clone" until the chosen filename is guaranteed not to match anything currently on the device -- deploying under an existing filename would silently OVERWRITE that profile instead of creating a new one. Auto-suggests a filename from the display name (alnum-only) but never overwrites one the user has typed directly. Sources from the selected profile's just-taken backup, never the live device file, same discipline as Stage/Restore. Hands off straight to `DeployPanel` (steps 9-10) exactly like Restore does -- no staged-vs-editing diff applies to a clone either. `frame.deploy_return_panel` gains a third value ("clone"), handled by the same context-aware Back button and belt-and-suspenders `editing_path` cleanup pattern `RestorePanel` already uses. Headless-verified against a real backup file: filename validation (missing extension, path separators, case-insensitive collision) all behave correctly; `patch_profile_name()` produces a byte-for-byte-structurally-identical clone (same screens/fields/order, only the name field bytes differ, source untouched); `describe_screen_changes()` confirms zero screen differences between source and clone, matching the confirmed real-hardware CLI result. Prior entry (v0.15.2): cosmetic doc-only fix -- `FieldPickerDialog`'s docstring said "86 confirmed entries," stale after `fit_dump.py` v2.4.3 added field 58 (Lap Timer); no functional change. v0.15.1: fixed a REAL bug found via testing (2026-08-06) -- `frame.editing_path` was only ever cleared by `DeployPanel.on_done()`, so backing out of a Restore attempt without completing it left `editing_path` pointed at the abandoned restore's backup file; since `get_working_path()` prefers `editing_path` over `staged_path`, a subsequent normal Stage then silently showed that stale leftover instead of what was just staged (reported symptom: "View Screens shows the backup I was about to restore, not what I just staged" -- it happened to produce a plausible-looking Preflight diff purely by coincidence, not because anything was actually correct). Fixed in two places: `ProfileListPanel.on_stage()` now unconditionally discards any prior session's `editing_path` before staging (the real fix -- a fresh Stage should always start clean; this also covers the same latent risk when switching to a different profile mid-session, which existed even before Restore was added); `RestorePanel.on_back()` also proactively discards when `frame.deploy_return_panel == "restore"` (cleans up immediately rather than waiting for the next Stage). v0.15.0: `RestorePanel` -- "Restore from Backup..." on `ProfileListPanel` lists the selected profile's backup history (`list_backup_history()`, newest first) with a per-candidate screen-type summary (e.g. "8 screen(s): Screen 1, Lap Summary, Map, ..."), then hands off straight to `DeployPanel` (steps 9-10), deliberately skipping `PreflightPanel` (steps 7-8) -- there's no staged-vs-editing diff to review when the user already picked a specific, known backup from a summarized list. `frame.editing_path` points at the chosen backup file directly (never copied -- `DeployPanel`/`describe_screen_changes()` only ever read it). `DeployPanel`'s "Back" button is now context-aware (`frame.deploy_return_panel`) so it returns to wherever Deploy was actually reached from. Headless-verified against real backup files (row summaries build correctly, including reflecting a screen-order swap between two backups). v0.14.0: `DeployPanel.on_check()` now re-pulls the LIVE profile from the device's `Sports/` folder the instant reconnect is confirmed, and compares it against `editing_path` (what was actually sent) via a new module-level `describe_screen_changes()` -- factored out of `PreflightPanel`'s former `_describe_changes()` so both panels share one implementation. Runs automatically on reconnect, not a separate manual step. User-confirmed design decision (2026-08-06): compares visible/active screens only, no Removed-list bookkeeping -- Garmin's own editor has no un-remove option and neither does this GUI, so the device's known Removed-list wipe on NewFiles import isn't reported; `describe_screen_changes()` already does this for free (only reports slots ACTIVE on at least one side, so Removed/Unconfigured-only transitions are invisible to it by construction) -- headless-verified by simulating the exact Removed→Unconfigured flip and confirming zero diff lines while a real field/position change on the same file pair still reports correctly. v0.13.0: `DeployPanel` (step 9) writes `editing_path` to the device's `NewFiles/` via `write_to_newfiles()` (byte-for-byte write-back verification), then walks the user through eject (confirm-then-`diskutil eject`, reusing `_volume_mount_point()` for the real ejectable target, plus an "I Ejected It Myself" fallback) and reconnect. User-confirmed design decision (2026-08-06): reconnect detection is a manual "Check for Reconnected Device" button rather than background-thread polling of `wait_for_remount()` -- this app has never used a background thread, and the manual-click tradeoff avoids introducing a new class of failure mode (thread lifetime vs. panel teardown) for the sake of a few saved clicks. `eject_device(auto_eject=True)`'s own `input()`-based confirmation isn't reused since it would hang a GUI handler -- the eject confirmation is a `wx.MessageBox` instead. "Done" clears `editing_path` (`discard_edits()`) and returns to the profile list. **CONFIRMED live on real hardware** (2026-08-06): full deploy of a new 10-field screen, plus the change summary and Fields-column fixes below, all verified end to end. v0.12.0: `PreflightPanel`'s change summary is now a plain-English, per-screen description (`_describe_changes()`) instead of a raw `fit_dump.py diff`-style unified diff -- real user feedback: the byte-level diff was too technical for the GUI's actual audience (a rider, not a developer); anyone who wants that level of detail still has the CLI tools directly. Compares the staged file against the working copy by slot (message_index) and reports plain lines like "Screen 4: added Cadence, removed Grade" or "Screen 2: moved from position 3 to position 2" -- new/removed screens, field set changes, field-order-only changes, layout A/B changes, show/hide changes, and position changes are all covered; a generic fallback line covers any future edit type not yet described in plain English, so real byte-level changes are never silently under-reported. Whether there's anything to deploy at all is still decided from the raw bytes directly, independent of the summary's coverage. v0.11.1: fixed `ViewScreensPanel`'s "Fields" column being a fixed 280px width, which silently CLIPPED (not wrapped) any screen's field list wider than ~3-4 short names -- real reported bug: a 10-field screen only showed 3 fields plus part of the 4th. `on_refresh()` now auto-sizes that column to its actual widest content on every refresh (never below the original 280px floor); overflow beyond the window's own width falls to the ListCtrl's native horizontal scrollbar instead of clipping. v0.11.0: fixed `MainFrame._relayout()` to only GROW the window when content needs more room, never shrink it -- real reported bug: manually enlarging the window (e.g. to see more of the screens list) snapped back to a smaller size on the next button click, since nearly every handler ends with `self.frame._relayout()`, which called `self.Fit()` unconditionally (Fit() resizes to the sizer's ideal size in both directions). The original v0.1.1 anti-overlap intent (grow when content needs more room) is preserved via `GetBestSize()`; only the unwanted shrink is gone. No call sites needed to change. v0.9.0: "Change Type..." on both `EditScreenPanel` and `AddScreenPanel` -- swaps one field's ID in place via the existing `FieldPickerDialog`, without the Remove+Add+reposition workaround ("Replace Field" from the original design notes, now built) -- **CONFIRMED live on real hardware** (2026-08-05), including a guard-overridden field change on ClimbPro that survived a full deploy/restart/reconnect cycle. v0.8.0: `AddScreenPanel` (step 5) replicates `--new-slot`'s exact defaulting logic via direct function calls -- picks the lowest unconfigured slot (never shown to the user), sets f1/f12 like every real device-created screen, auto-assigns collision-free f9/f10 via `next_available_field9()`/`next_available_field10()`, and enforces the confirmed 10-user-screen cap with a friendly message rather than a raw failure -- **CONFIRMED live on real hardware** (2026-08-05). v0.7.0: `ViewScreensPanel` Move Up/Down buttons swap two screens' on-device display order via `swap_display_order()` (the `--swap-order` backend) -- select-plus-buttons, same UX pattern as field reordering, enabled/disabled based on the selected row's position (top/bottom can't move further that direction). `_confirm_guard()`/`_confirm_hide_guard()` no longer show a false-positive "possibly a system screen" dialog for confirmed user screens. `on_show_toggle()` HARD-blocks (no override) hiding Map or ClimbPro at all, ahead of the last-visible-user-screen check. Deploy and restore-from-backup's picker not yet built. |

Design principle throughout: **patch bytes in place, never re-encode
the whole file.** Every edit observed on real devices — ours and the
device's own — has been a minimal, isolated byte change. The patcher
follows the same pattern: locate exact byte offsets, overwrite only
what's changing, recompute the trailing CRC, leave everything else,
including fields we don't fully understand, completely untouched.

---

## The `data_screen` message (mesg_num=14)

One message instance per screen "slot" (all ~30 preallocated from
profile creation, whether populated or not). Key fields:

| Field | Meaning |
|---|---|
| `254` | `message_index` — raw slot number. NOT stable across a NewFiles write (physically relocated during cap-eviction compaction) — never treat this as a screen's identity; use `f9` for identity/order instead. |
| `1` | Active/Removed flag (see Screen State Model) |
| `3` | Field count. Key absent entirely (not `0`) when the slot has never been configured. |
| `7` | 10-slot array of field IDs (uint16) |
| `8` | Layout variant: `0`=A/default, `1`=B/alternate. Only field counts **3, 4, 5, 6, 7** have a real B option — enforced as a hard error by the patcher if violated. |
| `9` | Screen creation-order stamp **and** literal on-device display order, ascending. Dense `0..N-1`, must be globally unique among Active screens (a duplicate is silently discarded on reboot). |
| `10` | **CONFIRMED screen TYPE identifier** (see "Screen identity — SOLVED", below) — NOT just a Conditional-state marker as earlier thought. Named Garmin types get a fixed global code (Map=25, Elevation=44, ClimbPro=104, etc.); plain user screens use a per-profile counter shown on-device as "Screen N" (`f10=N` → "Screen `N+1`"). Persists through content edits; actively re-applied when a named type is re-added from the device's own menu. `fit_dump.py`'s `NAMED_SCREEN_TYPES`/`screen_type_name()`. |
| `12` | Enabled/disabled ("Show Screen" toggle). `0`=shown, `1`=hidden. Independent of the Removed state. |
| `11` | **DISPROVEN as a user-vs-template signal** (tested on-device, side-thread, 2026-08-04) — four screens created via genuine on-device Add New all came back `f11=1`, identical to factory template screens, not absent as the earlier 2-data-point theory predicted. `f11=1` appears to be set by ANY device-side creation, template or Add New alike; doesn't distinguish authorship at all. (The user-vs-Garmin screen problem this was meant to solve is now solved anyway, via `f10` — see above.) One unexplained anomaly remains: Indoor profile slot 2 has `f11=2`, the only such value seen across 114 sample files — unresolved, unrelated to either theory. Unused by the toolkit. |

## Display order — solved

**Field `9`, ascending, is the literal on-device viewing order.**
Confirmed by matching a user-verified on-device editor sequence
exactly, and by a real device round-trip (`--swap-order`, swapping two
screens' `f9` and nothing else) producing the exact predicted
on-screen position swap.

## Screen State Model — three states, not two

| State | `f1` | `f9` | `f10` | Notes |
|---|---|---|---|---|
| **Active/Display** | `1` | real, unique | real | Normal, in the ordered sequence |
| **Conditional** (e.g. GroupTrack) | `1` | absent | **real** (seen: `32`) | Active feature, structurally exempt from ordering |
| **Removed** | `0` | absent | absent | Content (`f3`/`f7`) preserved -- ONLY until the next NewFiles-mediated write (see correction below) |

"Removed" is a soft delete — field count and the field ID array
survive completely intact at the moment of removal. Discovered via the
on-device "Remove" button; independently confirmed by finding this
exact signature on five "orphaned" screens in a real profile, and
again — byte-for-byte identical — on a **brand-new profile built
fresh from Garmin's own template with zero edits**. Every profile
ships pre-populated with these in the Removed state; it has nothing to
do with a user's own edit history.

**CORRECTION (2026-08-04, side-thread finding):** an earlier version
of this document implied Removed content is stably, indefinitely
preserved. That's wrong. **A NewFiles-mediated deploy purges whatever
is currently in the Removed state, every time — not a one-time
cleanup, but standing behavior of the NewFiles import/rebuild
pathway** (the same pathway already documented below as the root cause
of the Add-New-Screen failure). Confirmed via two independent Sandbox
deploys, each wiping a *different* Removed-state screen the deploy
itself never touched — once on long-standing factory-template content,
once on a screen the developer had Removed on-device only seconds
earlier. Both came back fully **Unconfigured** (not Removed, not
present at all) after the deploy and restart, even though neither
deploy edited that screen. Crucially, this is specific to the
**NewFiles pathway**, not to "any device write": Removed screens
edited or created purely through the on-device editor (no toolkit
deploy involved) are left alone and continue to show up normally in
`fit_dump.py screens`'s Removed section. Only a *toolkit*-mediated
deploy — a field edit, a layout change, a Show/Hide toggle, a reorder,
completely unrelated to the Removed screen itself — triggers the
purge. **Practical implication:** since most profiles ship with at
least one Removed-state screen from their factory template, any GUI
deploy of any kind will likely purge it, silently. Not a reason to
avoid the toolkit's core editing capabilities — none of them relied on
Removed content surviving — but worth knowing before treating a
Removed screen as a safe, permanent fallback.

A structurally normal Active screen is not a guarantee it will show
while riding, either: on the Indoor profile, Map and Elevation are
both ordinary Active screens (real `f9`) that never appear live —
confirmed there's a separate, undocumented runtime filtering layer
(near-certain cause on Indoor: GPS-dependent screens auto-suppressed
on a trainer profile) that nothing in `data_screen` predicts. This is
a real limitation of what the file format can tell you, not a bug in
the toolkit.

---

## Adding a new screen — CONFIRMED WORKING (2026-08-05), root cause revised

**Status as of `fit_patch.py` v1.12.0: activating a brand-new screen
via `--new-slot` and pushing it through NewFiles is CONFIRMED to
survive a live device round-trip**, including on a profile already
touched by NewFiles many times before. Test: `CyclingRoadSandbox`,
2026-08-05 — `--new-slot --slot 6 --fields 178,179 --field10 2`
(fields Gears/Front Gear; f10=2, collision-free, shows on-device as
"Screen 3"). After deploy → automatic restart → power-cycle → remount,
the new screen was present and correct, verified two independent ways
against the live mounted `/Volumes/GARMIN/Garmin/Sports/` file: once
via `fit_dump.py screens` run directly against that path, once via
`garmin_device.py screens` (which also reads the live device, no
staging). Both agreed exactly. The only side effect was the profile's
Removed-state screen being purged — already-known standing behavior of
*any* NewFiles deploy, unrelated to this change (see Screen State Model
above).

**Root cause, revised.** The previous conclusion — reached before f10's
meaning was understood, and documented for a long time as settled and
root-caused to the NewFiles delivery mechanism itself — turned out to
be explainable by something much narrower: `--new-slot`'s old default
silently wrote f10=0 whenever `--field10` wasn't given explicitly. f10
is a real, specific per-profile identity (0 = "Screen 1"), not an
inert sentinel as assumed when that default was written, and almost
every real profile already has a Screen 1. Writing a second screen
with the same f10 collides with that identity, and the device's
NewFiles reconciliation appears to merge/discard on that collision —
which matches every observed failure signature (new content vanishing,
sometimes grafted onto or destroying whichever existing slot shared the
colliding identity). `fit_patch.py` v1.12.0's `next_available_field10()`
auto-assigns a collision-free value instead, fixing this at the source.

**Loose end, noted for honesty rather than swept under the rug:** an
earlier test (predating this section's original writeup) reported that
a *synthetic* push built to byte-match a genuinely successful native
on-device "Add New" — same `f9`, same `f10`, same `f12`, same byte
positions, confirmed via a full whole-file diff — still failed when
delivered via NewFiles. If that test's f10 really was captured from a
successful native add, it would by definition already have been
collision-free, which the new theory doesn't obviously explain. Since
that older result can't be re-examined byte-for-byte here (it predates
this project's current file set), and the new result is fresh,
reproducible, and independently double-confirmed against the live
device by two separate tools, the new result is what current guidance
is based on — but this discrepancy is worth keeping in mind if a future
`--new-slot` attempt fails despite a collision-free f10. Possible
explanations not yet ruled out: some other field besides f9/f10/f12
mattering, a difference in which slot/`message_index` the synthetic
push targeted versus where the device itself placed the real one, or
NewFiles behavior that isn't fully deterministic across firmware
versions or profile history.

**Practical guidance:** `--new-slot` no longer requires manually
computing `--field10` — the auto-default handles it — but verify with
`fit_dump.py screens` and `fit_crc.py` before every deploy regardless,
same discipline as any other change, and expect the Removed-screen list
to be purged as a side effect. `--un-remove` shared the same fixed
default but was never re-tested live since that fix before being
retired outright (see below) — stayed unverified-but-plausibly-fixed
for its entire remaining lifetime in this codebase.

**Product note on `--un-remove`, added after further side-thread
testing (2026-08-05):** Garmin's own on-device editor has no
un-remove option at all — Hide (temporary) and Remove + Add New
(permanent) are the only workflows it exposes. Two related, now-
confirmed facts: a factory-shipped profile's Removed list already
contains a few entries the user never touched (seen on a brand-new
template with zero edits), and that list survives ordinary on-device
editing (adding screens, changing fields, etc.) but is wiped the
moment the profile goes through NewFiles, regardless of what the
NewFiles-mediated change actually touched. Together these suggest
Garmin itself may not treat "Removed" as a meaningfully distinct,
user-facing state the way this toolkit has had to reverse-engineer it
as. Current lean: keep `--un-remove` in the codebase for deliberate
future testing, but likely don't expose it as a first-class GUI
feature — final call deferred, not yet made.

**RESOLVED (2026-08-13) — the final call above has now been made:
Doug decided to retire `--un-remove` entirely, not just leave it
unexposed.** Reasoning, in his own words: "if the user mistakenly
deletes a screen, they can always recover the previous state using
restore from backup" — Restore-from-Backup already covers the real
recovery use case at the whole-profile level (confirmed working on
real hardware), so a per-screen un-remove was never load-bearing to
begin with. Combined with the confirmed historical data-loss hazard
above (never re-verified after the fix) and Garmin's own product not
offering an equivalent, keeping `--un-remove` around only added an
unverified, effectively-dead code path. `fit_patch.py` v1.13.0 removes
the flag, its argparse entry, its `--new-slot` mutual-exclusion check,
and its Removed-state validation, collapsing every `args.new_slot or
args.un_remove` conditional down to plain `args.new_slot`. One
clarifying nuance worth recording, not a disagreement with the
decision: the specific mechanism Doug described ("our process using
NewFiles won't allow the un-remove to occur") isn't quite how this
project's own testing had characterized it -- the confirmed purge
behavior targets screens still SITTING in the Removed state at deploy
time, whereas `--un-remove` flips the target screen to Active (fresh
f9/f10, mirroring `--new-slot`'s now-proven mechanics) BEFORE the
deploy, which should in principle escape that specific purge. Whether
it actually would have worked was never tested either way, so this
isn't a correction of a confirmed fact, just a note that the DECISION
to retire it stands on solid ground regardless (the data-loss history,
the lack of re-verification, and Garmin's own product surface are all
independently sufficient) even if the precise NewFiles mechanism isn't
the one this project had documented. See `FIT_PATCH.md` (now doc rev
17) for the retired OPTIONS entry kept as a historical record, and the
"Delete Screen" Open Item below for how this affects that still-scoped
feature (short answer: no change to the plan -- a future `--remove`
flag was always going to be one-way by design).

**Design decision, updated -- DONE (2026-08-05, gui_app.py v0.8.0):**
built a real Add-New-Screen panel (`AddScreenPanel`) rather than
redirecting the user to the on-device "Add New" menu, which was the
prior design's workaround for what's now a fixed limitation. Picks the
lowest unconfigured slot automatically (never shown to the user), lets
the user set fields/layout via the same widgets EditScreenPanel uses,
and auto-assigns f9/f10 via the fixed `next_available_field9()`/
`next_available_field10()`. Enforces the confirmed 10-user-screen cap
with a friendly message. Verified headlessly (replicated the panel's
exact call sequence outside wx, since wxPython can't be installed in
the dev sandbox) against a clean profile copy -- output byte-shape
matched the live-tested CLI success exactly (f1/f9/f10/f12 set the
same way, only the target slot touched, CRC valid). **CONFIRMED live
through the actual GUI widgets on real hardware (2026-08-05,
CyclingRoadSandbox)**: created a new screen via the GUI, deployed
through the normal eject/restart/remount flow, and verified on-device
-- the Active ride profile shows the new screen at the right position
with the correct fields. Add-New-Screen is now fully validated at
every level: fit_patch.py backend, headless GUI-logic replication, and
the real GUI end to end.

---

## Write path

- **Direct overwrite is unreliable** — works once, then permanently
  stops taking effect for a given profile once it's been touched by
  NewFiles even a single time.
- **NewFiles is the reliable path** — copy the patched file into the
  device's `NewFiles/` folder using the profile's exact existing
  filename, eject, restart.
- **Device quirk (important for the GUI):** after ejecting, the
  device auto-restarts to run the NewFiles import, but does **not**
  remount as USB storage on its own afterward — it settles into
  charging mode. It needs exactly **one power-button press**, after
  the restart finishes, to come back as a mounted drive. Any GUI must
  surface this instruction explicitly or a user will be stuck
  watching a spinner that never resolves.
- **Timestamps:** the `Sports` folder's timestamp updates on *any*
  restart (not diagnostic). The `Backup` folder's timestamp updates
  *only* on a genuine content change — a reliable signal, confirmed
  via a clean no-op control test and multiple real edits.
- **Screen-count cap: CONFIRMED via real testing.** 10 fields per
  screen, and 10 USER-definable screens per profile. Additional
  Garmin-predefined/overlay screens are allowed beyond that 10 and do
  NOT count against it -- consistent with the Conditional screen
  state and the pre-Removed factory-shipped screens already documented
  in the Screen State Model above. This resolves the earlier "not
  fully pinned down" uncertainty (a flat 13-total-slots cap was ruled
  out -- a 17-screen profile was fine -- and an isolated eviction had
  been observed at only 6-7 user screens on another profile; the
  10-user figure is the real, confirmed cap, with the earlier
  early-eviction case likely reflecting NewFiles' own rebuild trigger
  interacting with something else, still not isolated in detail but no
  longer the open question it was). When eviction does happen: the
  lowest-`f9` screen is evicted and every remaining `f9` is renumbered
  to close the gap (same renumbering also happens on a plain native
  Remove, not just via NewFiles).

---

## Field ID dictionary

105 of an estimated ~200 possible field IDs confirmed (this count was
stale here for several updates -- last synced 2026-08-10; `fit_dump.py`
itself is always the source of truth via `len(FIELD_ID_NAMES)`),
cross-referenced against on-device visual verification across six
profiles (Road, Gravel, Tourtst, Mountain2, Indoor, plus the 2026-08-10
census pass on a Sandbox clone). Full table lives in
[`FIT_PATCH.md`](FIT_PATCH.md).

Lessons from the census process worth remembering for future work:
- Don't assume a field's position in the raw storage array matches
  its on-screen display position — caused one real mis-identification,
  corrected via on-ride photo verification against a second,
  independent screen using the same field.
- An on-device UI marker (a `*` shown only in the field picker, never
  while actually riding) revealed two field IDs (348/349, "Speed
  \*"/"Cadence \*") that would otherwise have looked like duplicates
  of already-known ones (48/3).
- **DONE (2026-08-10)** — 18 new field IDs confirmed in one batch: 7
  Lap Dist., 30 Time to Next, 31 Dest. Location, 39 Lap Power, 50 Lap
  Speed, 57 Avg Lap Time, 61 Total Descent, 62 Dest. Ahead, 63 Time
  Ahead, 67 Reps to Go, 86 Last Lap Speed, 88 30s VAM, 94 ETA to Next,
  95 Odometer, 295 Target Power, 442 Lap VAM, 443 Avg VAM, 445 Asc to
  Next Crs Pt. Method: arranged two screens to 10 fields each on a real
  profile specifically for this census, entered/selected each field by
  its on-device name (so the name itself came straight from Garmin's
  own UI, not a guess), then cross-referenced each field's raw ID
  against its known on-screen position using this toolkit's own GUI —
  the same direct-verification standard as every other entry, just
  batched at scale rather than one disposable test screen per ID. This
  batch is also what surfaced the two window-sizing bugs fixed in
  `gui_app.py` v0.16.2/v0.16.3 (a screen with 9 of 10 fields unresolved
  was an unusually good stress test for exactly that failure mode) —
  see the toolkit table entry for those versions. `FIELD_ID_NAMES` now
  105 confirmed entries; `KNOWN_UNRESOLVED_IDS` still empty.
- **DONE** — the last deliberately-unresolved IDs, 84/87 (seen on
  GroupTrack's Conditional record), were closed 2026-08-04 via a
  forced-field test screen deployed successfully through NewFiles,
  rather than waiting on a live multi-rider session: `84` = Last Lap
  Dist, `87` = Last Lap Timer. Turned out to have nothing to do with
  GroupTrack at all — they'd only been assumed GroupTrack-related by
  association with the screen they happened to be seen on. Lesson:
  don't assume a field's meaning from which screen it's seen on,
  especially a Conditional-state one — the safer, faster path (a
  disposable forced-field test, the same low-risk method used for the
  VAM/Lap Cadence/Max Speed/Lap Flow census) should have been tried
  before assuming a live session was the only option.

---

## On-device layout geometry

Supplied directly by the developer as a text-based Edge 530 reference
(one entry per field count, A/B where applicable) and encoded as
`LAYOUT_GRIDS` in `gui_app.py`, driving the GUI's live layout diagram.
Cross-checked against `fit_patch.py`'s `COUNTS_WITH_B_VARIANT` (3, 4,
5, 6, 7 have a real A/B choice) — matches exactly, no discrepancies.

| Count | A (or only) layout | B layout |
|---|---|---|
| 1 | 1 full-width row | — |
| 2 | 2 full-width rows | — |
| 3 | 3 full-width rows (equal) | 3 full-width rows (top field renders smaller — not a row/column difference, just a size one) |
| 4 | 4 full-width rows | row1: 2 side-by-side, rows 2-3: full-width |
| 5 | 5 full-width rows | rows 1-2: full-width, row3: 2 side-by-side, row4: full-width |
| 6 | rows 1-4: full-width, row5: 2 side-by-side | row1: 2 side-by-side, rows 2-3: full-width, row4: 2 side-by-side |
| 7 | rows 1-3: full-width, rows 4-5: 2 side-by-side each | row1: 2 side-by-side, row2: full-width, rows 3-4: 2 side-by-side each |
| 8 | rows 1-2: full-width, rows 3-5: 2 side-by-side each | — (no B variant) |
| 9 | row1: full-width, rows 2-5: 2 side-by-side each | — (no B variant) |
| 10 | rows 1-5: 2 side-by-side each | — (no B variant) |

This also confirms two hard caps via real device testing, not just
inference: **10 fields per screen**, and **10 user-definable screens
per profile** (additional Garmin-predefined/overlay screens are
allowed beyond that 10 and don't count against it) — see Write Path,
below, which previously had this only partially pinned down.

---

## Activity Profile settings (outside `data_screen`)

- `sport_mesgs` (`mesg_num=13`), field 53 = Segments toggle
  (1=on/0=off). Large, sparse message (~40 fields); the rest is
  unmapped and out of scope for now.
- `training_settings_mesgs[0]`, field 63 = ClimbPro toggle
  (1=on/0=off) — a **different** message than Segments. (An early
  test showed zero diff and briefly suggested a device-wide setting;
  it turned out to be an accidental duplicate file upload, caught via
  a CRC check. Treat any "zero difference" toggle result as suspect
  until file identity is verified.)
- `mesg_num=280`: likely a Power Curve cache (3 rolling time windows,
  15 shared duration-bucket boundaries, monotonically decreasing peak
  wattage per window). Populated only when real ride data exists and
  Graph-type fields are active. Tangential to the core goal, not
  pursued further.

## `startup.txt` — custom boot message (BUILT, 2026-08-14)

Outside `data_screen` entirely, and outside any Activity Profile too —
a plain-text file, not a `.fit` file, living at the device-root level
(directly inside the `Garmin` folder itself — i.e. at `garmin_root`,
the SAME level `Sports`/`NewFiles`/`Settings` live at — NOT under
`Sports/`/`NewFiles/` where every other file this toolkit touches
lives). Displays a custom message at device boot. Discussed 2026-08-06
as a candidate GUI feature (see Open Items / GUI scoping below for the
original "Show startup.txt" button design) and BUILT 2026-08-14 on
Doug's go-ahead, once both open questions below were confirmed
directly against his own real hardware — `garmin_device.py` v0.12.0
(`read_startup_txt()`/`parse_startup_txt()`/`build_startup_txt()`/
`write_startup_txt()`, plus a `startup-txt` CLI subcommand) and
`gui_app.py` v0.18.0 (`StartupTxtPanel`, reached via DetectPanel's
"Startup Message..." button).

**Syntax:** a `<display=N>` directive controls how many seconds the
message shows at boot (a duration, not a screen-position or content
directive).

**Limits, per Garmin Support + community testing (GPLama) — supplied
by the developer 2026-08-07, not yet independently confirmed on real
hardware by this project:**

- **256 characters total**, across the entire custom text area.
- **7-bit ASCII only** — standard letters/numbers/basic punctuation.
  Special characters, emojis, or extended-ASCII text-art won't render
  correctly.
- **No hard line-count cap in the file itself** — but the physical
  screen truncates anything beyond its own layout allocation, and that
  allocation is **model-specific**:

| Edge model | Max visible lines |
|---|---|
| Edge 520 / 820 | 5 |
| Edge 530 / 830 / 1030 | 6 |
| Edge 800 | 7 |

This is the same shape of problem as the "Model portability" Open Item
above — a real constraint that varies by physical device, not
something `data_screen`/field-count logic predicts — and would fit the
same eventual `DEVICE_PROFILES`-keyed-by-`garmin_product` approach if
that ever gets built, rather than needing its own separate mechanism.
For now, since the 530 is the only confirmed/owned device, a future
"Edit startup.txt" GUI feature could hard-code the 530's own limits
(256 chars, 6 visible lines, 7-bit ASCII) as a live character-count/
line-count warning while typing, without needing the full
`DEVICE_PROFILES` machinery just for this one file.

**RESOLVED (2026-08-14) — both open questions above, now CONFIRMED
directly on Doug's real device**, not just corroborated secondhand:

- **Path**: `startup.txt` sits directly inside the `Garmin` folder --
  `os.path.join(garmin_root, "startup.txt")`, no extra nesting, using
  `find_garmin_root()`'s EXISTING return value as-is (confirmed
  elsewhere in this file that `garmin_root` already resolves to
  `/Volumes/GARMIN/Garmin`, the same level `Sports`/`NewFiles`/
  `Settings` live at -- see `_volume_mount_point()`'s docstring).
  Doug's own `ls -l` of that folder shows `startup.txt` sitting right
  alongside `Sports`, `NewFiles`, `Settings`, etc. Same path a Windows
  build would need too, once that platform exists.
- **Write mechanism**: Doug's real `startup.txt` (`cat`'d directly,
  2026-08-14) contains Garmin's OWN first-party comment, undercutting
  any need to guess: `<!-- Allow one full power cycle after editing
  for your message to be updated -->`. This confirms two things at
  once -- it's a PLAIN direct file overwrite while the device is
  mounted (no NewFiles reconciliation, no CRC, nothing this toolkit's
  `data_screen` machinery has to worry about at all), and what's
  needed afterward is a full power cycle (off, then on), not just an
  eject/remount -- makes sense, since a boot-time message can't
  re-render without an actual boot. Independently corroborated by a
  DC Rainmaker how-to (dcrainmaker.com, 2013, plus a 2020 comment
  thread citing gplama.com -- the SAME source the 256-char/7-bit-
  ASCII/5-6-7-line limits above were already sourced from) describing
  the identical edit-directly-and-save workflow, with no eject step at
  all beyond a normal safe-remove before power-cycling.

**Real file content, for reference (Doug's actual Edge 530,
2026-08-14)** -- confirms the file's real shape, not just a
description of it:
```
<!-- Edit this file to display a message while your unit is powering on                -->
<!-- Allow one full power cycle after editing for your message to be updated           -->

<!-- Set the display number to the minimum number of seconds your message is displayed -->
<display = 3>

<!-- Type your message on the next line -->
Connecting to Cloud
Location sent to...
Owner: Doug Curtis
dscurtis@gmail.com
(262)-391-3235
```
Garmin's own template ships with explanatory `<!-- ... -->` HTML-style
comment lines ABOVE the `<display=N>` directive and again right before
the message -- these are template instructions, not something the
device is known to strip at render time (untested either way, but the
safest assumption for a GUI editor is to treat the WHOLE file as
one editable text blob and preserve those comment lines exactly as
Garmin shipped them, rather than trying to parse out "just the
message" and reconstruct the file -- less to get wrong, and it matches
exactly what Doug's own file still looks like after he filled in his
message). Also notable: Doug's message is a deliberate light misdirect
("Connecting to Cloud" / "Location sent to...") ahead of his real
contact info -- not a toolkit concern, just confirms the field is
freely user-authored text, not template-constrained beyond the
character/line/ASCII limits above.

Both real remaining unknowns before writing (not reading) `startup.txt`
are now closed. See Open Items below -- the view half needs nothing
further; the edit half is also now fully scoped, just not yet built.

## Screen identity — SOLVED via field 10 (f10)

**CONFIRMED (side-thread Test 4, 2026-08-04) — this section previously
called the problem unsolvable at the file-format level; it isn't.**
Field 10 (f10) is a real, content-independent screen TYPE identifier,
fully independent of `f9` (display order):

- **Named Garmin screen types** get a FIXED global code, the same
  value regardless of profile/template or what content the user has
  since customized the screen to show. Proven, not inferred: patching
  Cycling Dynamics' fields via `--force` and redeploying left `f10`
  unchanged at 63 -- the tag marks *type*, not *displayed content*.
  Also actively RE-APPLIED, not just inherited from original template
  creation: removing GroupTrack List on-device and re-adding it from
  the device's own named-screen menu brought it back tagged `f10=57`
  again, not the next free counter value.
- **Plain user-created screens** use a per-profile, zero-indexed
  counter; the on-device editor displays `f10=N` as "Screen `N+1`"
  (confirmed exactly across 6 independent instances on one profile, no
  exceptions).

Ten named types confirmed so far (see `fit_dump.py`'s
`NAMED_SCREEN_TYPES` / `screen_type_name()`):

| f10 | Screen type | f10 | Screen type |
|---|---|---|---|
| 25 | Map | 57 | GroupTrack List |
| 26 | Virtual Partner | 63 | Cycling Dynamics |
| 32 | Reserved (Conditional record, renamed from "GroupTrack" 2026-08-15 -- see note below) | 74 | Lap Summary |
| 35 | Compass | 104 | ClimbPro |
| 44 | Elevation | 56 | Segment |

This directly fixes `would_hide_last_visible_screen()` (see
`fit_patch.py` v1.9.0, CORRECTIONS below) -- "how many real user
screens does this profile have left" is now a straightforward f10
filter, not a guess, and it only counts plain `Screen N` entries, not
every visible screen of any kind.

**Also fixes `check_system_screen_guard()` (v1.10.0), confirmed via
real GUI testing:** the pre-f10 heuristic guard (content-pattern match
OR field count ≤2) fired on ANY low-field-count screen, including
genuine user screens -- exactly the false positive it was designed to
avoid, just moved rather than eliminated. The guard now checks f10
first: a confirmed plain user screen gets NO warning at all, and a
confirmed named Garmin type gets a CERTAIN message naming it directly
rather than a guess. The old heuristics are now a fallback used only
for Removed-state slots, which have no real f10 to read.

### f10=32 "Reserved" (renamed from "GroupTrack", 2026-08-15) and f10=57 "GroupTrack List" — two independent structural representations

`f10=32` is a Conditional-state runtime record (`f1=1`, `f9` absent,
`f10` real) -- exempt from `f9` ordering entirely. Its two fields, 87
and 84, are now resolved (Last Lap Timer, Last Lap Dist -- confirmed
2026-08-04 via a forced-field test rather than waiting on a live
multi-rider session) and turn out to have nothing to do with
GroupTrack at all; they'd only been assumed GroupTrack-specific by
association with the screen they were seen on. That was the first
crack in the original "this is GroupTrack's record" assumption. The
second, decisive one: this record has been present on EVERY profile
examined so far, active or not, regardless of whether GroupTrack has
ever actually been used on that profile -- a real feature-specific
runtime record should plausibly track feature usage somehow, and this
one never has. **Doug's decision (2026-08-15): rename the display name
from "GroupTrack" to "Reserved"** (`fit_dump.py` `NAMED_SCREEN_TYPES`,
now v2.4.12) -- stops asserting an identity this project was never
actually sure of, while keeping the record's real, confirmed
characteristics (always-present, Conditional-only, exempt from `f9`
ordering, content fields 87/84 unrelated to GroupTrack) fully
documented. What it actually IS remains an open question -- "Reserved"
reflects that honestly rather than guessing a replacement theory.

`f10=57`, "GroupTrack List," is a SEPARATE, always-orderable Active
screen (real `f9`) that's simply excluded from the active-ride scroll
list by firmware, the same pattern as ClimbPro and Segment below --
and unlike f10=32, THIS one is genuinely GroupTrack-specific: it's the
literal on-device named-screen menu entry for the feature, unaffected
by the rename above. Confirmed structurally independent from f10=32:
removing GroupTrack List on-device and re-adding it left the `f10=32`
record completely unaffected.

### ClimbPro, Segment — conditionally visible, structurally ordinary

Both (`f10=104` and `f10=56`) are structurally normal Active screens
(real `f9`, real `f12`), indistinguishable from any other screen by
shape alone -- their "only visible under some condition" behavior
(entering a qualifying climb; entering a course segment, per Garmin's
own Edge 530 manual) is pure firmware logic layered on top, nothing in
`data_screen` predicts it. ClimbPro additionally: content-identical to
a plain Elevation overlay by default (Grade + Elevation) since content
is freely customizable regardless of type tag; and has at least two
more on-device-only behaviors never reflected in `data_screen` -- an
"Upcoming Climbs" list screen inserted when a qualifying course is
loaded, and a scrollable-away-from (not full-takeover) hijack of the
display while actually climbing.

**ClimbPro has two entirely separate on/off controls, confirmed
directly on-device, not to be conflated:** an overall profile-wide
enable/disable that lives one level up in the Profile menu
(`training_settings_mesgs[0]` field 63) -- and, within the per-screen
Data Screens editor itself, **no Show Screen toggle at all** for
ClimbPro's own screen entry, same as Map (below). `fit_patch.py`
v1.11.0's `hide_unsupported_screen_type()` hard-blocks `--hide` on
ClimbPro for exactly this reason -- forcing `f12=1` on it would
produce a state with no on-device action to compare it against.

### Map, Compass, Virtual Partner

Map (`f10=25`) has **no Show Screen toggle at all, on ANY profile
type** -- confirmed directly on-device, not a per-profile-type
exception. `hide_unsupported_screen_type()` (`fit_patch.py` v1.11.0)
hard-blocks `--hide` on Map for exactly this reason, universally.

**Remove availability, separately confirmed (2026-08-13, Doug,
directly on-device):** of the common Garmin Edge named screen types,
Map and ClimbPro are the ONLY two with the on-device Remove option
disabled -- Elevation, GroupTrack, Cycling Dynamics, Lap Summary,
Virtual Partner, Compass, and Segment all show an active Remove
option. This is the exact same two-type set `NO_SHOW_TOGGLE_TYPES`
already hard-codes for the Show Screen toggle -- Hide and Remove share
the identical availability boundary for these types, not just for the
"can't touch the profile's last screen" floor rule documented
separately above. Directly useful for the scoped-but-not-built
`--remove`/"Delete Screen" feature (see Open Items): its own
type-check guard can reuse this existing set rather than needing a
separate census. CLARIFIED (2026-08-13, same day): "GroupTrack" in
Doug's tested list was the on-device editor's actual label,
"GroupTrack List" (`f10=57`) -- already included, Remove confirmed
active, no gap there. `f10=32`, the GroupTrack Conditional runtime
record, is a genuinely separate thing (see "GroupTrack -- two
independent structural representations" above) -- it never appears as
a row in the on-device Data Screens editor at all (no real `f9`), so
it has no Remove-button status to check, and it's structurally outside
this feature's reach regardless (Conditional screens are never
interactive/selectable in `ViewScreensPanel`). Also worth recording:
an early, now-removed `SYSTEM_SLOT_HINTS` hardcode once claimed
"slot 10 = GroupTrack" by message_index -- confirmed WRONG on the
Indoor profile (slot 10 there is a genuine Cadence screen) and dropped
from the codebase; slot/message_index numbers were never a reliable
way to identify GroupTrack or anything else, only `f10` is (see
"Corrections and lessons learned" above).

**What the Indoor profile actually does is a different mechanism
entirely, not a Show Screen toggle:** it exposes a control that
changes Map's state between "Always" and "While Navigating" -- a
genuinely different axis (when Map is relevant, not whether it's
shown/hidden in the reorderable sense this project's `f12` models).
**Working hypothesis, not yet confirmed:** this may be exactly what
sets `f11=2` on Indoor's slot 2 -- the only occurrence of that value
across all 114 sample files (see Open items) -- i.e. Garmin may be
using `f11` as the field for this specific state, on this specific
screen type, rather than reusing `f12`. Not yet tested directly (would
need toggling Indoor's Map between Always/While-Navigating on-device
and diffing the result). Compass (`f10=35`) is
structurally ordinary, nothing special. Virtual Partner (`f10=26`) is
structurally DIFFERENT from every other screen in this project: no
`f3`, `f4`, `f7`, `f8`, or `f11` at all -- just `f1`, `f9`, `f10`,
`f12`, `254`. It has no editable field list (hence no field picker
on-device), but DOES have real Reorder and Show/Hide controls (`f9`
and `f12` are both present and real). Its displayed content (Dist
Ahead/Time Ahead) and its speed setting are both firmware-rendered
from a separate, not-yet-located profile-level setting, the same
pattern already established for the Segments toggle
(`sport_mesgs`) and ClimbPro's toggle (`training_settings_mesgs`) --
neither lives in `data_screen`.

**Bug this uncovered:** `classify_screens()` (`fit_dump.py`) and
`read_current_state()` (`fit_patch.py`) both used to gate
configured/Active status on field 3 (`f3`) presence. Virtual Partner's
missing `f3` caused it to silently vanish into "unconfigured" in both.
Fixed in `fit_dump.py` 2.4.1 / `fit_patch.py` 1.9.0 -- both now gate on
`f1`/`f9`/`f10` instead, confirmed via live RoadClone data (Virtual
Partner now appears correctly in the reorderable list) and a synthetic
regression test covering all four states.

---

## Device connection layer (`garmin_device.py`)

Automates the full manual workflow this project used throughout
testing, and is now confirmed **end-to-end on real hardware**: detect
(+ `get_device_info()` — manufacturer/product/serial/software version,
for a multi-device user to confirm the right one is connected) → back
up all profiles to a working directory (never `/tmp`) → let the user
pick one → view current screens → stage a patched copy (tagged with
exactly which backup it was derived from, preventing a repeat of an
earlier v5/v6 chaining mistake where the source backup for a patch got
lost track of) → verify the device is still connected → write to
`NewFiles` with an immediate read-back verification → prompt for eject
(never silent/automatic without confirmation) → poll for reconnect,
with the power-button instruction surfaced explicitly → re-dump to
confirm the change landed, both byte-level and visually.

Also hardening-tested: a disconnect mid-deploy fails cleanly with no
corruption, and `--auto-eject` correctly asks for confirmation before
running.

Detection is structure-based (looks for `Sports/` + `NewFiles/`
directories, checking up to two levels of nesting) rather than
name-based, so it doesn't depend on what the volume happens to be
called. **Both macOS and Windows are now implemented and CONFIRMED
working on real hardware for the full pipeline** (Windows confirmed
2026-08-19, Doug, real Windows 11 laptop + real Edge 530): `detect`
(printed the same device info as the Mac), `fit_dump.py screens` and
`garmin_device.py screens`, the full GUI workflow including adding a
new screen to the Sandbox profile and a successful NewFiles
deploy/restart round-trip -- all worked with no code changes needed
beyond copying the toolkit's `.py` files over. `D:\Garmin` on Doug's
test laptop has `Sports`/`NewFiles` flat at the drive root (Level 1 of
`_find_garmin_root_windows()`'s two-level check), resolving the one
open question from the implementation -- the Level 2 (one-subfolder-
deep) branch exists for symmetry with the macOS half but hasn't itself
been exercised against real hardware yet. `install.sh` remains
macOS-only by earlier design choice; Windows setup for now is the
manual `pip install garmin-fit-sdk wxPython` path, run directly with
NO virtual environment (installed via python.org's standard Windows
installer), which is what Doug used here. A nice side effect of that
no-venv install: double-clicking `gui_app.py` in File Explorer
launches the GUI directly, no wrapper script needed -- the python.org
installer associates `.py` files with the same Python `pip` installed
into, unlike macOS's Python Launcher, which pointed at a different
`python3` than the one `wx` was installed into via `.venv` (real
report, same week -- see Doc rev 68 above for the full writeup). No
Linux testing has been done.

---

## Corrections and lessons learned

Kept deliberately, for pattern-recognition on future work:

- **Hardcoded slot-number labels were wrong twice.** An earlier
  `SYSTEM_SLOT_HINTS` table in `fit_dump.py` (e.g. "slot 8 =
  terminator", "slot 10 = GroupTrack") was confirmed wrong on the
  Indoor profile — slot 8 there is a genuine populated screen, slot 10
  a genuine Cadence screen. Slot numbers are **not** stable across
  profiles; this had been documented as a risk once before but not
  acted on until it broke on real data. It was removed entirely and
  replaced with the structural (f1/f9/f10-based) Conditional
  classification, which found the real GroupTrack signature correctly
  with zero dependency on slot number.
- **`diskutil eject` needs the volume mount point, not the deeper
  functional root.** `garmin_device.py` originally tried to eject
  `garmin_root` (e.g. `/Volumes/GARMIN/Garmin`); the real Edge 530
  mounts one level deeper than the ejectable volume
  (`/Volumes/GARMIN`). Fixed with a `_volume_mount_point()` helper
  used only for eject.
- **The power-button remount step wasn't obvious from the first
  successful test** — Doug pressed the button without mentioning it,
  so the requirement only surfaced when a later inconsistency prompted
  asking directly. Now stated explicitly in `eject_device()` and
  `wait_for_remount()` output, and in this doc.
- **A one-way "grow, never shrink" fix (v0.11.0) had no ceiling until
  v0.16.2.** The v0.11.0 fix (never shrink a manually-enlarged window)
  and the v0.11.1 fix (auto-size the Fields column to its content) were
  each correct in isolation, but combining "the window only ever grows"
  with "a widget's reported size is driven by its content" meant any
  content that could transiently demand too much room would inflate
  the window PERMANENTLY, with no automatic way back -- which is
  exactly what happened in v0.16.2 (an unresolved field ID's verbose
  label blew out `wx.ListBox`'s best-size). The narrow fix (shorter
  labels) addressed this one trigger; the general fix (clamp growth to
  the display's work area in `_relayout()` itself) addresses the whole
  category, so the next unanticipated wide-content case degrades
  gracefully instead of requiring another bug report and an app
  restart. Lesson: a one-directional size policy needs an explicit
  ceiling from the start, not just a floor.
- **A confidently-stated assumption in a code comment (v0.11.1) turned
  out to be wrong, and the FIX for it (v0.16.3) made a second wrong
  assumption of its own -- three unverified claims about the same
  widget's behavior in three days, each one caught only by real
  testing, not by review.** The v0.11.1 comment claimed a `wx.ListCtrl`
  in report mode never grows the FRAME from column content -- "if
  that's wider than the window can show, the ListCtrl's own native
  horizontal scrollbar takes over rather than clipping." True for
  ordinary field lists, false for a real profile with 9 of 10 fields
  unresolved on two screens (v0.16.3's bug report). v0.16.3's own fix
  then claimed capping the column's width would make "content past the
  ceiling rely on the ListCtrl's own native horizontal scroll" --
  ALSO false: a capped column just clips its cell text with no wrap and
  no ellipsis, since the control's real horizontal scrollbar only
  engages when the SUM of every column's width exceeds the control's
  own rendered area, a completely different, coarser trigger than "one
  cell's text doesn't fit." Confirmed the hard way (2026-08-10): real
  testing on newly-added longer field names showed only 6-7 of 10
  fields, silently truncated, no scrollbar, no error. The actual fix
  (v0.16.6) had to stop trying to control the FRAME by capping the
  COLUMN at all -- the two need to be decoupled at a different layer
  entirely (a `DoGetBestSize()` override), not reasoned about via
  assumptions about how the column and the scrollbar interact. Lesson,
  sharpened from the first time this happened: "the framework handles
  this automatically" claims about a specific widget's behavior deserve
  the same skepticism this project already applies to file-format
  claims, AND a fix built on top of an unverified assumption can just
  as easily introduce a second one -- the fix itself needs the same
  scrutiny as the bug it's fixing, not a pass because it's "the fix."
- **An early `git init` was accidentally scoped to the home
  directory** instead of the project folder — caught via an obviously
  too-broad untracked-file list (personal `Documents/`, `.ssh/`, etc.)
  before any commit landed. Fixed by deleting that `.git` and
  reinitializing directly in `garmindev`.
- **Added 3 new `NAMED_SCREEN_TYPES` entries (v2.4.13) using the WRONG
  keys, before ever seeing the raw file they were based on.** Doug
  reported 3 new screen types by the numbers he read off this tool's
  own output ("59," "96," "39"), but `screen_type_name()`'s own
  documented fallback for an unnamed type is `f10 + 1` -- the numbers
  Doug (reasonably) read were already display labels, not raw f10
  bytes. Added entries at 39/59/96 anyway, without independently
  checking against real data, since the uploaded `.fit` file wasn't
  accessible in this environment yet. The real f10 values, confirmed
  once the file finally came through and got dumped directly, are
  38/58/95. Because the wrong keys (39/59/96) happen to equal the
  CORRECT keys' own `f10+1` display fallback (38+1=39, 58+1=59,
  95+1=96), the bug was invisible by inspection alone -- `screen_type_
  name()` would have kept silently falling through to the generic
  "Screen N" label for the real profile, producing the exact same text
  it always had, giving no visual sign anything was wrong. Caught only
  because the raw file was inspected directly (v2.4.14) before this
  went any further. Lesson: a "confirmed by Doug" batch addition is
  only as solid as the number actually being what's claimed -- when a
  number comes from a tool's own OUTPUT rather than an independent
  source (a raw byte, an on-device menu, a developer reference), check
  whether that tool applies any transform before displaying it, before
  trusting the number as ground truth. This project has generally been
  good about this (matching prior "Corrections" entries above), but
  this is the first time it slipped through into a real dict key,
  not just a comment.
- **The 2026-08-17 field-ID batch (20 entries) had every raw ID and
  every name correctly identified individually, but wrongly PAIRED --
  a whole-block transposition, not a one-off typo.** Doug's census
  method for this batch put 10 fields on Screen 3 and 10 on Screen 4
  of a dedicated test profile, then wrote up the list by reading names
  and IDs off each screen -- but the two screens' blocks got swapped
  relative to each other in the writeup, so field 437's real name
  ("Avg W/kg") ended up paired with field 148's raw ID slot in the
  list, 147's real name ("Lap NP") ended up paired with 437's ID slot,
  and so on across all 10 pairs on one side (mirrored the same way on
  the other side). Nothing about the individual numbers or names was
  wrong -- every single one of the 20 (ID, name) facts Doug reported
  was independently true -- only the CROSS-PAIRING between the two
  blocks was off, which is a much harder class of error to catch by
  inspection than a single wrong digit: the resulting list still reads
  as 20 perfectly plausible, internally consistent field entries, with
  no obvious tell. It only surfaced because Doug happened to test 4 of
  the 20 fields together on one real screen and directly compared what
  the toolkit claimed against what the device actually rendered.
  Lesson: for a multi-field batch verified by arranging several fields
  across MULTIPLE screens (not one), the position-to-name mapping step
  needs to happen per-screen, in the moment, not reconstructed
  afterward from separate notes about each screen -- the earlier
  2026-08-10/2026-08-11 batches that used a single screen for the
  whole census never had this failure mode available to them. Going
  forward, this project's stated practice for future batches is to
  verify one field at a time (add ONE field via the on-device native
  menu, immediately check its raw ID via this toolkit, before moving
  to the next) rather than batch-arranging several fields across
  screens and matching everything up from notes afterward.

---

## Open items

- **CLOSED, OUT OF SCOPE (2026-08-24) — "Delete an entire Activity
  Profile" (not just a screen within one).** Doug asked (2026-08-22)
  whether deleting a profile might be as simple as removing its `.fit`
  file from `Sports/` and `Sports/Backups/` directly. Investigated
  directly, black-box, on real hardware, in two clean steps:
  **Test 1 (2026-08-22/24):** deleted the `Sandbox` profile's `.fit`
  file from `Sports/` only, power-cycled the device. Result: the
  profile came BACK. This alone was informative -- it ruled out "just
  delete the one file" and pointed at `Sports/Backups/` (a folder this
  toolkit already knew existed on-device -- see `garmin_device.py`'s
  `BACKUPS_SUBDIR` constant, deliberately never descended into by
  `backup_profiles()`) as a plausible restore source, since Garmin
  device firmware restoring from ITS OWN backup folder on next boot
  would explain the symptom exactly.
  **Test 2 (2026-08-24), the actual disambiguating test:** deleted the
  SAME profile's `.fit` file from BOTH `Sports/` AND `Sports/Backups/`
  this time, power-cycled again. Result: the profile STILL came back.
  This rules out the `Sports/Backups/`-restore hypothesis entirely --
  whatever governs a profile's real existence on-device is not simply
  "a `.fit` file present in `Sports/`" the way this toolkit's entire
  reverse-engineered `data_screen`/screen-editing model has always
  assumed for SCREENS within a profile. Two live possibilities, NEITHER
  confirmed and neither likely to be confirmable without deeper
  device-internals access this project doesn't have: an internal
  database/index the device maintains that's simply never exposed over
  USB mass storage at all (the `.fit` files could be more like an
  export/serialization view than the actual source of truth), or a
  minimum-profile-count floor Garmin enforces per activity type that
  silently recreates something once you drop below it.
  **CONCLUSION, Doug's own call:** since this toolkit's entire method
  is black-box manipulation of files exposed over USB mass storage, and
  whole-profile deletion has now been directly tested and demonstrated
  NOT achievable that way (unlike every other feature in this project,
  which all started from exactly this kind of black-box test and then
  got built once confirmed), this is logged as explicitly OUT OF SCOPE
  for this tool's goals at this time -- not a "not yet built" gap to
  revisit later, a genuine dead end for this project's approach. See
  `MVP_SCOPE.md`'s "Explicitly excluded from MVP" table (Doc rev 17)
  for the scope-document version of this same conclusion. Worth noting
  for anyone who revisits this: per-screen deletion (`fit_patch.py`
  `--remove`) works completely differently and IS fully supported --
  this closes out only the WHOLE-PROFILE case, which was always a
  separate, harder question.
- **RESOLVED (2026-08-17), data integrity issue in the 2026-08-17
  field ID batch** — Doug edited Screen 4 (slot 7) on a real profile
  (`CyclingRoadROAD.fit`) via this toolkit's GUI to fields named
  "Intensity Factor (IF)" (437), "Pedal Smoothness" (147), "Torque
  Effect" (148), "Perf. Conditioning" (320), but the profile as it
  actually displays on the Edge 530 shows "Avg W/kg, Lap NP, Last Lap
  NP, Perf. Cond." for those same 4 positions — 3 of 4 wrong (320 was
  always fine, "Perf. Cond." is just this dict's own name further
  truncated at that field width). `FieldPickerDialog` (`gui_app.py`)
  reviewed directly — no indexing/lookup bug there, it writes exactly
  the raw ID paired with the selected name — so this was always a
  data problem in the dict itself, not a code bug in the read/write/
  picker path. ROOT CAUSE, diagnosed by Doug himself: his census
  screens 3 and 4 (Roadtemp profile) got transposed when the original
  20-entry list was written up, so all 10 IDs from one screen's block
  were paired with the 10 NAMES from the other screen's block — a
  clean systematic offset (the SET of 20 raw IDs was always correct,
  only which name each pointed to was wrong), not scattered individual
  errors. Doug re-derived the correct pairing directly from Roadtemp's
  screen 3/4 field order; it resolves ALL THREE mismatches exactly
  (437 → Avg W/kg, 147 → Lap NP, 148 → Last Lap NP — this dict's own
  separate, independently-added entries for those three names from the
  SAME batch turned out to be exactly right, and were the tell that
  something had gotten crossed). All 20 entries corrected in
  `fit_dump.py` v2.4.19; the SUSPECT warnings from v2.4.18 removed.
  **FULLY CLOSED OUT, same day (v2.4.20):** `CyclingRoadRoadtemp.fit`
  (the original census profile, with Screen 3/Screen 4 still intact at
  10 fields each) came through on a second upload attempt and was
  dumped directly via `fit_dump.py dump`. Raw arrays — slot 6 (Screen
  3) = `[150, 149, 177, 176, 43, 437, 40, 408, 411, 441]`, slot 7
  (Screen 4) = `[80, 42, 148, 147, 82, 83, 151, 161, 160, 159]` — match
  all 20 corrected pairs position-for-position exactly, including
  field 177 "Torque Effect" under its own ID, closing the one residual
  flag this item was still carrying (that on-device string had only
  been confirmed against ID 148 before the transposition was found).
  This is now the same direct byte-level verification standard as
  every other confirmed batch in this project. See "Corrections and
  lessons learned" for the methodology takeaway (verify one field at a
  time, not by batch-selecting several and matching names up afterward
  from notes — the transposition this time was traced to exactly that
  pattern).
- The very first test profile's original opening screen (WindField
  Widget, evicted during early cap-testing on "Roadtest") is
  recoverable from a full external device backup, if wanted.
- **DONE** — the screen-count cap itself is now confirmed (10 fields/
  screen, 10 user screens/profile, see Write Path above). The
  narrower residual question -- why one early test ("Roadtest")
  evicted at only 6-7 user screens rather than the full 10 -- is still
  unexplained, but no longer blocks anything; not worth pursuing
  further given the eviction risk of testing it directly.
- **DONE** — the last two unidentified field IDs, 84/87 (seen on
  GroupTrack's Conditional record), resolved 2026-08-04: `84` = Last
  Lap Dist, `87` = Last Lap Timer, confirmed via a forced-field test
  deployed successfully through NewFiles — the disposable-test method
  worked without needing a live multi-rider session after all. Turned
  out unrelated to GroupTrack itself, just two ordinary lap-stat
  fields that happened to appear on that particular screen.
  `FIELD_ID_NAMES` now has 86 confirmed entries;
  `KNOWN_UNRESOLVED_IDS` is empty.
- **DONE** — field `58` = Lap Timer, resolved 2026-08-06: surfaced
  incidentally by real GUI testing (Restore-from-Backup on a restored
  8/3/2026 `CyclingRoadSandbox` backup showed a field the GUI's picker
  didn't recognize), confirmed via direct visual comparison against
  the live device display (`fit_dump.py` 2.4.3). Not the result of an
  active field-ID hunt -- those stay in the other thread per the
  earlier decision to keep this thread focused on GUI work.
  `FIELD_ID_NAMES` now has 87 confirmed entries.
- **DONE** — user-built vs. Garmin-authored screen identification,
  previously this section's biggest open question, is now solved via
  `f10` (see "Screen identity — SOLVED", above).
- **DONE (2026-08-05)** — Add-New-Screen via `--new-slot`/NewFiles,
  previously documented as a settled, root-caused hard limitation, is
  now CONFIRMED WORKING. Root-caused to an f10 identity collision
  (old default wrote f10=0, colliding with the profile's existing
  "Screen 1"), fixed via `next_available_field10()` in `fit_patch.py`
  v1.12.0, verified via a live on-device round-trip. One honest loose
  end remains -- an earlier, exact-byte-match synthetic push also
  failed and isn't fully explained by this theory -- see "Adding a new
  screen" above. `--un-remove` shares the fix but hasn't itself been
  re-tested live yet.
- **Indoor profile's Map "Always"/"While Navigating" state, and the
  slot-2 `f11=2` anomaly — likely the same open question, not yet
  confirmed.** Map has NO Show Screen toggle on any profile type
  (confirmed, now hard-guarded in the toolkit -- see "Map, Compass,
  Virtual Partner" above), so what the Indoor profile actually exposes
  for Map is a different control entirely: a toggle between "Always"
  and "While Navigating," not a show/hide in the `f12` sense. Working
  hypothesis: this may be what sets `f11=2` on Indoor's slot 2 -- the
  only occurrence of that value across all 114 sample files, previously
  logged as a bare anomaly with no theory attached. Next step to
  confirm: toggle Indoor's Map between Always/While-Navigating
  on-device and diff the result -- now trivial to locate by name via
  `f10=25` in `screens` output, whereas previously it required guessing
  among several 0-field candidates.
- `sport_mesgs`' other ~39 fields (name/color/ride type/alerts/auto
  features/etc.) remain unmapped — same toggle-and-diff method would
  work, low priority, outside the core Data Screens MVP.
- Where Virtual Partner's speed setting (and the Segments on/off
  toggle) actually live is still unknown — confirmed NOT to be in
  `data_screen` itself (Virtual Partner has no `f3`/`f4`/`f7`/`f8`/`f11`
  at all to hold it), same unresolved-location pattern as ClimbPro's
  toggle before it was traced to `training_settings_mesgs`. Not chased
  down yet; low priority.
- The Map "(Always)" vs. "(when navigating)" qualifier text seen in
  the on-device editor is a distinct, UI-only axis not yet traced to
  any byte field — low priority.
- **Publishing to GitHub — license/disclaimer landed (2026-08-11).**
  Doug asked about licensing/hosting ahead of a possible public
  release. Landed: `LICENSE` (MIT, standard "AS IS" no-warranty text,
  copyright holder `Doug (fullcarbonbike)` — Doug's own choice, name
  and GitHub handle together), a License/Disclaimer section merged
  into `README.md` (right after the intro, before Setup — "not
  affiliated with Garmin" trademark disclaimer, black-box
  reverse-engineering method note, device-write use-at-your-own-risk
  warning; reviewed and approved by Doug; `README_DISCLAIMER_DRAFT.md` is now
  superseded and can be deleted), and the `gui_app.py` v0.16.7
  window-title rename ("Activity Profile Screen Editor for Garmin
  Edge" -- the standard nominative-fair-use "for X" pattern,
  user-confirmed over two other candidates). Researched (not just
  assumed) before drafting: Garmin's SDK Terms of Use prohibit reverse-
  engineering the SDK *software* itself, but this project never did
  that -- it used `garmin_fit_sdk` as a normal dependency and separately
  reverse-engineered the undocumented `data_screen` message via
  black-box observation of real files, a meaningfully different
  activity; Garmin's separate FIT Protocol licensing is more permissive
  about building compatible tools; and several comparable community
  FIT-file tools have existed publicly on GitHub for years with no
  known enforcement action found. None of this is legal certainty --
  flagged to Doug as such. Also landed (v0.16.8): an "About" button on
  `DetectPanel` opening a short in-app summary dialog (name/version,
  trademark disclaimer, reverse-engineering method note, MIT mention)
  — Doug's own idea, matching a pattern he'd seen in other tools.
  **RESOLVED (2026-08-25) — "Publishing housekeeping cleanup."** Doug
  clarified the canonical name -- "Activity Profile Editor for Garmin
  Edge," no "Screen," no "530," matching his GitHub repo name
  ("Activity-Profile-Editor") and Release titles ("Activity Profile
  Editor for Garmin Edge Devices") -- and it's now applied consistently
  everywhere: `gui_app.py`'s window title/module docstring/About text
  (v0.19.20), README.md's/this file's own H1, `MVP_SCOPE.md`'s heading,
  and `FIT_PATCH.md`'s banner. `README_DISCLAIMER_DRAFT.md` (the other
  half of this Open Item) was found already deleted -- nothing left to
  do there either. See Doc rev 83 above for the full writeup, including
  what was deliberately left unchanged (`MEMORY_LOG.md`, the
  RELEASE_NOTES files -- both point-in-time historical records).
- **`startup.txt` custom boot message — BUILT (2026-08-14), Doug's
  go-ahead.** New "Startup Message..." button on `DetectPanel`
  (alongside Detect Garmin/About), opening `StartupTxtPanel`
  (`gui_app.py` v0.18.0): shows the current message, edits the
  `<display=N>` seconds value and the free-form message text, and
  preserves Garmin's own comment scaffolding byte-for-byte (built on
  `garmin_device.py` v0.12.0's `read_startup_txt()`/
  `parse_startup_txt()`/`build_startup_txt()`/`write_startup_txt()`,
  plus a `startup-txt` CLI subcommand). The two real open questions
  this item was waiting on — exact on-device path, and whether a write
  needs the eject/remount cycle — are now RESOLVED via Doug's own real
  device, not just the developer-supplied secondary-source findings
  (256 chars, 7-bit ASCII, ~5-7 visible lines) that were the only
  reference available before: see "`startup.txt` — custom boot
  message" above for the full confirmation. Character/line-count
  guidance is shown live in the GUI but deliberately NOT a hard block
  on Save — Doug's own explicit call (2026-08-14): actual on-device
  wrapping is character-width-dependent, so the real safety net is the
  automatic pre-write backup (`write_startup_txt()`), not a refusal to
  save; a user who doesn't like how it wrapped can just edit and retry.
  No FIT parsing, CRC, or NewFiles pathway involved at all, unlike
  everything else in this toolkit -- confirmed correct in practice, not
  just in the original estimate. Headlessly verified: parse/build
  round-trip is byte-identical against Doug's real file content;
  write_startup_txt()'s backup-then-overwrite behavior against a fake
  filesystem `garmin_root` (plain file I/O, no real device needed for
  this one, unlike every other write in this toolkit); the
  `startup-txt` CLI subcommand exercised end-to-end via a monkeypatched
  `find_garmin_root()`. Real GUI behavior on Doug's actual hardware is
  still pending his own run, same as every other GUI feature in this
  project. "Restore a profile that's no longer on the device" below
  was originally batched alongside this item (2026-08-11 decision) but
  has since been handled as its own separately-scoped item.
- **Graph/Bars full-width warning (raised by Doug, 2026-08-11,
  discussed not yet built).** Doug confirmed (see the corrected "*"
  mystery note under field 348/349 above) that fields marked with a
  "*" or "(Alt)" suffix are Graph- or Bars-style fields that need a
  FULL-WIDTH screen slot to actually render as a graph/bar; placed in
  a shared/split row instead, they silently fall back to plain text
  with no on-device indication anything's wrong. UPDATE (2026-08-11,
  same day): confirmed set now stands at 10 fields following Doug's
  continued census -- 343 Heart Rate Graph, 344 Speed Graph, 345
  Cadence Graph, 346 Power Graph, 347 HR Bars, 348 Speed Bars, 349
  Cadence Bars, 350 Power Bars, 368 Elevation Graph, and 23 HR Zone
  Graph (renamed from the placeholder "Heart Rate (Alt)" now that its
  real on-device name and Graph-type nature are both confirmed).
  UPDATE (2026-08-11, same day): field 49 was checked next and turned
  out NOT to be Graph/Bars -- Doug deployed it into a full-width
  screen slot via the GUI and visually confirmed on-device it's a
  plain text "Avg Speed" value. Renamed from the old placeholder "Avg
  Speed (Alt)" accordingly. IMPORTANT METHODOLOGICAL CAUTION, not a
  falsification of the marker theory: unlike 23/348/349, there's no
  record that 49's old "(Alt)" label was ever a literal transcription
  of a real on-device UI marker -- it may simply have been an old,
  undocumented naming guess (predating this project's later discipline
  of noting confirmation method per field) that happened to reuse the
  same word. Practical implication for the eventual GUI feature: the
  confirmed Graph/Bars set (the 10 fields above) should only ever grow
  from fields where an actual on-device marker was directly observed
  and recorded at confirmation time -- an OLD placeholder name merely
  containing "(Alt)" is not itself sufficient evidence on its own.
  Question: should the GUI flag this so a user doesn't unknowingly end
  up with a "graph" field that's actually just showing a number?
  Good news on feasibility: this is fully computable from data the GUI
  already has, no new geometry model needed. `LAYOUT_GRIDS` (in
  `gui_app.py`) already represents each row as a list of field
  positions -- a row with exactly one position (e.g. `[0]`) is
  full-width; a row with more than one (e.g. `[2, 3]`) means those
  fields split the row, each less than full width. So "is position P
  full-width for this field count + A/B layout" is a small, pure,
  already-derivable lookup -- no new geometry data to maintain. What's
  actually needed: (1) a small NEW curated set (e.g.
  `GRAPH_OR_BARS_FIELD_IDS`, kept separate from `FIELD_ID_NAMES` in
  `fit_dump.py` rather than folding a category flag into it, to avoid
  touching every existing consumer of that dict) -- listing only the
  fields individually confirmed as Graph/Bars type, same discipline as
  every other confirmed entry in this toolkit's field data; (2) a
  helper function checking row membership/width for a given
  count+layout+position; (3) UI surfacing in two natural, complementary
  places -- a static note in `FieldPickerDialog` when a Graph/Bars
  field is being picked at all (independent of placement), and a
  CONTEXT-AWARE warning in `EditScreenPanel`/`AddScreenPanel` once a
  field is actually placed, reflecting whether ITS CURRENT position is
  full-width or not (recomputed whenever fields are reordered, since a
  position's row membership can change as neighbors are added/
  removed). `LayoutDiagramPanel` could optionally reinforce this
  visually later, but isn't essential to the core value. Real
  limitation to flag: the Graph/Bars membership set can only ever be as
  complete as what's been individually confirmed -- there could be
  other Graph/Bars-type fields not yet caught by the "*"/"(Alt)"
  marker pattern that simply haven't been identified yet, so this
  would have false negatives (unflagged fields that actually need full
  width) but should have no false positives (nothing flagged incorrectly).
  BUILT (2026-08-14), matching this scoping almost exactly: new
  `GRAPH_OR_BARS_FIELD_IDS` (`fit_dump.py` v2.4.11, the 10 fields
  listed above, kept separate from `FIELD_ID_NAMES` as planned) and new
  `is_position_full_width()`/`graph_bars_warnings()` helpers in
  `gui_app.py`, derived from `LAYOUT_GRIDS` exactly as scoped -- no new
  geometry model needed. Surfaced in the two places planned: (1)
  `FieldPickerDialog` shows a static note (independent of placement)
  whenever the highlighted field is a Graph/Bars type, updated live via
  a new `EVT_LISTBOX` handler; (2) `EditScreenPanel`/`AddScreenPanel`
  both show a context-aware warning naming any CURRENTLY PLACED
  Graph/Bars field whose position isn't full-width for the screen's
  current field count + layout variant, recomputed on every refresh --
  automatically stays correct as fields are added/removed/reordered or
  the layout is toggled, per the recompute requirement noted above.
  `LayoutDiagramPanel` was NOT touched -- the scoping flagged this as
  optional visual reinforcement, not essential, and it wasn't built.
  Headlessly verified the layout-membership logic (not the actual wx
  widgets, which need Doug's own run) against real `LAYOUT_GRIDS`
  geometry across several field-count/layout/position combinations,
  including confirming non-Graph/Bars fields never trigger a warning.
  `gui_app.py` now v0.16.15.
  REAL BUG FOUND USING IT (2026-08-14, Doug): the warning text blew
  out `EditScreenPanel`'s window width, pushing the layout diagram
  off the right edge of his screen -- the FOURTH time this exact
  codebase has hit the "wx widget reports best-size from an
  unwrapped string's full pixel width" class (v0.16.2/v0.16.3/
  v0.16.6, see "Corrections and lessons learned"). Fixed via a new
  `graph_bars_warning_text()` helper that hard-wraps each warning
  through Python's stdlib `textwrap.fill()` (new
  `GRAPH_WARNING_WRAP_WIDTH = 42` chars) before it ever reaches the
  widget -- deliberately NOT `wx.StaticText.Wrap()`, since that can't
  be exercised at all in the dev sandbox (no wxPython) and its
  documented behavior with a label that already contains newlines
  (which stacking multiple warnings would) is explicitly "not going
  to be rewrapped in a sensible way." Also shortened the warning
  wording itself and applied the same wrap to `FieldPickerDialog`'s
  note for consistency. Headlessly verified via `textwrap.fill()`
  directly against the real warning strings -- confirmed every
  wrapped line stays within the target width, including with two
  warnings stacked. `gui_app.py` now v0.16.16.
- **`ViewScreensPanel`'s "‹ Back" button silently discards pending
  edits with no warning (real bug report, Doug, 2026-08-13, discussed
  not yet built).** Confirmed via code inspection, not hypothetical:
  `ViewScreensPanel.on_back()` is a bare `self.frame.show_panel
  ("profiles")` -- no check of `frame.editing_path` at all. If a user
  has added or edited a screen this session (`frame.editing_path` set,
  e.g. via Add New Screen or any EditScreenPanel change -- both apply
  immediately to the scratch `.editing.fit` file per this app's
  "every click is a real, immediately-applied operation" architecture)
  and clicks Back, they land back on the profile list with zero
  indication anything is pending. If they then click "Stage Selected
  for Edit" on that same profile again, `ProfileListPanel.on_stage()`
  unconditionally calls `frame.discard_edits()` first (v0.15.1's own
  fix, deliberately unconditional, for an unrelated stale-reference
  bug) -- which only clears the in-memory `editing_path` reference, not
  the underlying scratch file on disk, but since the GUI has no way to
  rediscover an orphaned `<staged_path>.editing.fit` it can no longer
  reference, the edit is practically unrecoverable through the app
  either way. Real, confirmed silent-data-loss path.
  Precisely scoped fix: `ViewScreensPanel.on_back()` should check
  `frame.editing_path is not None` before navigating away, and show a
  confirm dialog (matching this app's existing guard-dialog style,
  e.g. the last-visible-screen/system-screen confirms) warning that
  going back will lose changes made this session, with Cancel (stay)
  as an option. Deliberately NOT needed on `EditScreenPanel.on_back()`
  or `AddScreenPanel.on_back()` -- both return to "screens" (staying
  inside the same editing session, not exiting it), and neither panel
  ever has a "pending, not-yet-applied" state to lose in the first
  place, per the immediately-applied editing architecture. So this is
  a single, small, well-contained fix, not a systemic multi-panel
  change.
  Two related-but-separate observations, not in scope unless Doug
  wants them folded in: (1) the existing "Discard Edits" button also
  has zero confirmation today (fires `discard_edits()` immediately) --
  arguably fine as-is since the button's own label makes the action
  unambiguous, unlike a bare "‹ Back"; (2) there's no `EVT_CLOSE`
  handler anywhere in `gui_app.py` at all, so quitting the app outright
  while `editing_path` is set is the same silent-loss shape, just via
  the window's close button/Cmd-Q instead of Back -- worth knowing
  about even if out of scope for this specific fix.
  BUILT (2026-08-14, `gui_app.py` v0.16.14): exactly the fix scoped
  above, nothing more -- `on_back()` now checks `frame.editing_path is
  not None` and shows a `wx.MessageBox(wx.YES_NO | wx.ICON_WARNING)`
  confirm before navigating away, same style as `RestorePanel.on_
  restore()`'s existing destructive-action confirm. `EditScreenPanel`/
  `AddScreenPanel` deliberately untouched, per the reasoning above.
  Both related observations (Discard Edits' own missing confirm, no
  `EVT_CLOSE` handler at all) remain open/unactioned -- Doug hasn't
  asked for either.
  REWORDED (2026-08-14, Doug's feedback after actually using it): the
  original wording's "...before returning here, they'll be lost for
  good" implied a user could come back later and pick up where they
  left off -- not true, there's no resumable state at all. Replaced
  with Doug's own more direct wording: "You have edits from this
  session that haven't been deployed to the device yet. If you go
  back you will lose those edits and have to start over!" No change
  to the underlying check/guard logic, purely the message text.
  `gui_app.py` now v0.16.17.
- **"Delete Screen" -- a real GUI/CLI way to remove a screen, not just
  Hide it (requested by Doug, 2026-08-13, discussed not yet built).**
  Doug's own recollection is correct: this was identified as a gap
  from early on and never closed -- `MVP_SCOPE.md`'s feature table has
  carried "Remove a screen -- *(not yet built)*, structurally
  understood, not yet wired into `fit_patch.py`" since the Screen
  State Model was first worked out. Today only Show/Hide (field 12)
  exists as a write path; nothing in this toolkit can ever set field 1
  to 0 (the actual Active -> Removed transition). Good news first:
  this is filling a real, Garmin-sanctioned gap, not inventing new
  behavior -- the "Product note on `--un-remove`" above already
  established that Garmin's own on-device editor exposes exactly two
  screen-lifecycle actions, Hide (temporary) and Remove + Add New
  (permanent). Delete is the second half of that pair; this toolkit
  has only ever had the first half.
  UPDATE (2026-08-13, same day): `--un-remove` -- the flag this Backend
  paragraph originally described as the mirror image to build `--remove`
  from -- has since been RETIRED entirely (`fit_patch.py` v1.13.0, see
  "Product note on `--un-remove`" above for Doug's reasoning). This
  doesn't change the plan here at all: `--remove` was always going to
  be a one-way operation with no CLI or GUI un-remove counterpart, and
  it still needs to be written from scratch either way. If anything
  it's a cleaner slate now -- no leftover `--new-slot`/`--un-remove`
  mutual-exclusion special case to coordinate with, and no ambiguity
  about whether a future `--remove` should someday grow its own
  restore counterpart (it deliberately won't).
  Backend: needs a brand-new `--remove` flag in `fit_patch.py` that
  sets f1=0 and clears f9/f10 back to sentinel, leaving f3/f7 (field
  count + field ID array) untouched, matching the confirmed
  Removed-state signature -- the retired `--un-remove`'s old code (set
  f1=1, assign fresh f9/f10) is a useful reference for the general
  shape of a screen-state-transition flag, even though it's gone from
  the codebase now. This is genuinely new, unverified write-path code
  either way, not GUI wiring around an already-proven backend the way
  Restore/Clone were when their GUI panels were built.
  Guard reuse is a real bright spot, though: `would_hide_last_visible_
  screen()`'s own docstring already documents that it reproduces the
  SAME rule the on-device editor uses for BOTH Hide and Remove --
  confirmed on a real profile where the device grayed out "Hide/Remove"
  together for the profile's one remaining visible user screen. So the
  floor-of-one-user-screen guard Doug is asking about doesn't need to
  be reinvented, just reused (or wrapped under a `--remove`-specific
  name) for the new flag.

  RESOLVED (2026-08-13, Doug, confirmed directly on-device): of the
  common Garmin Edge special/named screens, **Map and ClimbPro are the
  only two with Remove disabled** -- every other named type checked
  (Elevation, GroupTrack, Cycling Dynamics, Lap Summary, Virtual
  Partner, Compass, Segment) shows an active Remove option. This is
  the SAME two-type boundary `hide_unsupported_screen_type()` already
  hard-codes as `NO_SHOW_TOGGLE_TYPES = {25, 104}` (Map, ClimbPro) for
  the Show Screen toggle -- Doug's finding confirms that exact set
  also governs Remove availability, not just Hide. Practical
  implication for the future `--remove` flag: `hide_unsupported_
  screen_type()`'s existing type set can very likely be reused as-is
  for a Remove-availability guard too, rather than maintaining a
  second, separately-curated list -- though the function should
  probably grow a `--remove`-specific name/wrapper rather than being
  called directly under its Hide-specific name, since the underlying
  fact (which types this set names) is shared but the two guards serve
  different flags.
  CLARIFIED (2026-08-13, same day): Doug's "GroupTrack" in the tested
  list above referred to the on-device editor's actual screen label,
  "GroupTrack List" (f10=57, the always-orderable Active placeholder) --
  it WAS one of his seven confirmed-active-Remove types, closing what
  had briefly been flagged as a gap. Genuinely separate and NOT
  covered by any of this: `f10=32`, the GroupTrack Conditional runtime
  record (`f1=1`, `f9` absent -- structurally exempt from the normal
  ordering system, see Screen State Model / "GroupTrack -- two
  independent structural representations" above). It never appears as
  a row in the on-device Data Screens editor at all (no real `f9` means
  it's not part of that reorderable list), so it has no Remove-button
  status to check, and it's already out of scope for this feature
  regardless -- `ViewScreensPanel` only ever shows Conditional/Removed
  screens as plain read-only text, never as an interactive, selectable
  row (see that panel's own docstring). Historical note, not a live
  concern: an early `SYSTEM_SLOT_HINTS` table once hardcoded "slot 10 =
  GroupTrack" by message_index/slot NUMBER -- that was confirmed WRONG
  on the Indoor profile (slot 10 there is a genuine Cadence screen) and
  removed from the codebase entirely; slot numbers were never a
  reliable way to identify GroupTrack or anything else, only `f10`
  values are (see "Corrections and lessons learned" above). So: `--remove`'s
  future guard can now safely reuse `NO_SHOW_TOGGLE_TYPES` as-is, with
  Map and ClimbPro as the complete, confirmed block-list -- no
  remaining gap.
  Real risk to flag plainly, already known from unrelated testing: ANY
  NewFiles-mediated deploy purges whatever's currently in the Removed
  state, regardless of what triggered the deploy -- so a screen deleted
  through this toolkit will almost certainly NOT land in a stable,
  `--un-remove`-recoverable state after the very deploy that performs
  the deletion; it will most likely settle into genuinely Unconfigured
  instead. That's not a flaw to work around, it actually matches
  Garmin's own "permanent" framing for Remove -- but it means the ONLY
  practical undo path is the existing whole-profile Restore-from-Backup,
  not a per-screen un-delete, and the GUI's confirmation dialog should
  say so plainly rather than implying anything is reversible in place.
  Path to build, following the same two-phase discipline every other
  write-path feature in this toolkit has gone through: (1) implement
  `--remove` in `fit_patch.py`, headless-verify the byte output; (2) a
  REAL on-device round-trip test -- deploy a `--remove`'d screen,
  restart, confirm it's actually gone and the rest of the profile is
  unaffected -- BEFORE any GUI wrapper gets built, exactly like Add-
  New-Screen/Clone/Restore all were.

  PLACEMENT DECIDED (Doug, 2026-08-13, recorded ahead of building it,
  same convention as the Move Up/Down and field-reorder UX decisions
  above): `ViewScreensPanel` -- the screen ORDER view -- not
  `EditScreenPanel`. A new "Remove Selected Screen" button next to the
  existing Move Up/Down buttons, acting on whichever row is currently
  selected in `screens_list`, plus a confirmation dialog stating
  plainly that this can't be undone except via Restore-from-Backup.
  This is a strong fit, not just a workable one: `ViewScreensPanel`
  already has the exact interaction pattern this needs, wired and
  proven -- select a row in `screens_list`, a button acts on it,
  enabled/disabled via `on_row_selected()`/`on_row_deselected()`
  (currently driving `move_up_btn`/`move_down_btn`/`edit_btn`). Delete
  is structurally a list-level operation (remove an item from the
  sequence), same category as Add/Move Up/Move Down, not a property of
  a screen being actively edited -- which is why it fits more naturally
  here than alongside Show/Hide in `EditScreenPanel` (Show/Hide lives
  there because that panel is already open for other edits; Delete
  doesn't need that context first). Doug's stated warning framing --
  "can't be un-done except by the restore backup process" -- matches
  exactly what this Open Item already flagged as necessary wording, not
  by coincidence: this is the direct consequence of `--un-remove`
  having been retired the same day (see above) and NewFiles purging the
  Removed state on any deploy regardless.
  One concrete nuance this placement surfaces, worth flagging now
  rather than at build time: `screens_list` (`data["orderable"]` from
  `classify_screens()`) includes EVERY Active screen with a real f9 --
  that's both plain "Screen N" user screens AND named Garmin types
  (Map, Compass, ClimbPro, etc., confirmed via `count_shown_active_
  screens()`'s own logic, which has to specifically EXCLUDE named types
  from its user-screen count precisely because they're otherwise mixed
  in with everything else in that same list). So a "Remove Selected
  Screen" button in this exact list will be selectable against a Map or
  ClimbPro row too -- RESOLVED (2026-08-13, Doug, on-device): those two
  are exactly the types that need blocking. Doug confirmed Map and
  ClimbPro are the only common named types with Remove disabled;
  Elevation, GroupTrack, Cycling Dynamics, Lap Summary, Virtual
  Partner, Compass, and Segment all show an active Remove option --
  same two-type boundary `hide_unsupported_screen_type()` already
  hard-codes for Hide (`NO_SHOW_TOGGLE_TYPES = {25, 104}`), so the
  button's type-check guard can reuse that existing set rather than
  needing new field census work. CLARIFIED (same day): "GroupTrack" in
  Doug's tested list meant the on-device label "GroupTrack List"
  (f10=57) -- it was already covered, no remaining gap there. The
  genuinely separate `f10=32` GroupTrack Conditional record never
  appears as a row in `screens_list` at all (no real `f9`), so it's
  already out of reach of this button regardless of Remove status.
  Only once the backend is confirmed does this become a GUI wiring job:
  the button above, reuse the last-visible-screen guard, block Map/
  ClimbPro specifically (confirmed, reusing `NO_SHOW_TOGGLE_TYPES`
  directly -- no other named type needs blocking), and note that a
  deleted slot becomes available to Add-New-Screen again afterward. Estimated
  comparable in size to the
  original Add-New-Screen build (new backend flag + guard
  reuse + real-hardware test + one GUI panel/button) -- not a huge
  lift, but it carries the "brand-new, unverified write path" risk
  class rather than the lower "wire up an already-proven backend" risk
  class most recent features (Restore, Clone) have had.
  STEP (1) OF THE PATH-TO-BUILD ABOVE WAS DONE (2026-08-14):
  `--remove`/`remove_screen()` built in `fit_patch.py` v1.14.0, reusing
  `hide_unsupported_screen_type()`/`would_hide_last_visible_screen()`
  directly as its two hard guards, exactly as this Open Item planned --
  no new guard logic needed, only reuse. Headless-verified against a
  real profile copy: correct Removed-state transition, f3/f7 preserved
  byte-for-byte, no effect on any other slot, valid trailing CRC, and
  both guards block exactly as designed (tested directly against a Map
  screen, and against a profile's last visible user screen).
  STEP (2) IS NOW ALSO DONE (2026-08-14, Doug, real on-device
  round-trip): the target screen was correctly removed from the
  on-device Data Screens order, matching a real Remove button press.
  Also confirmed the expected corollary, matching `--un-remove`'s own
  retirement reasoning: the removed screen does NOT survive as a
  recoverable Removed-state slot after the deploy that removes it --
  NewFiles wipes it, same as every other Removed-state slot on any
  NewFiles deploy. `fit_patch.py` now v1.14.1 (doc-only, STATUS/BUGS
  updated from OPEN/unverified to RESOLVED/CONFIRMED); `FIT_PATCH.md`
  now doc rev 19.
  STEP (3) IS NOW ALSO DONE (2026-08-14, Doug's go-ahead): "Remove
  Selected Screen" built on `ViewScreensPanel`, next to Move Up/Down
  exactly as placed above. `on_remove()` runs the same two hard guards
  --remove enforces at the CLI level (each with its own explicit
  error dialog, no override), then a confirmation dialog stating
  plainly this is permanent and undoable only via Restore-from-Backup,
  then calls `remove_screen()` against `frame.editing_path` via the
  same "first edit creates the scratch copy" pattern `on_edit()`/
  `_swap_screen_order()` already use. `gui_app.py` now v0.17.0. This
  closes "Delete Screen" end to end -- backend, real device test, and
  GUI are all done. Real end-to-end GUI confirmation (does the button
  actually work when clicked on real hardware) still needs Doug's own
  run, same as every other GUI feature in this project -- wxPython
  can't be installed in the dev sandbox.
- **"Favorite screen" -- save a screen, reuse it across profiles
  (requested by a tester, 2026-08-11, discussed not yet built).** A
  tester wants to save his favorite "dashboard" screen (a specific
  field set + layout) and add it to other profiles without rebuilding
  it field-by-field each time. Scope assessment: what actually needs
  saving is small -- just the ordered field ID list, field count, and
  A/B layout variant (f7/f3/f8's content). f9 (display order) and f10
  (screen identity) are already auto-assigned per-profile by
  `next_available_field9()`/`next_available_field10()` and must stay
  that way regardless, so a favorite is NOT a raw copy of a
  `data_screen` message, just its field-content triple. Estimated
  moderate, and smaller than either Restore-from-Backup or Clone
  Profile were, since it reuses more existing infrastructure than new:
  (1) persistence -- a small JSON favorites file (e.g.
  `~/.garmin_screen_editor_favorites.json`, list of {name, field_ids,
  layout}), same pattern as v0.16.9's new working_dir config sidecar;
  (2) capture -- a "Save as Favorite" action on an already-staged
  screen (EditScreenPanel/ViewScreensPanel already hold the field
  list + layout in memory, just needs a name prompt and a JSON
  append); (3) apply -- a "Load from Favorite..." entry point on
  `AddScreenPanel` that pre-fills its field list/layout picker from a
  saved favorite instead of building it manually, then falls through
  to the SAME already-confirmed-working add-screen path (auto f9/f10,
  10-field/10-screen caps, deploy) -- no new patch-layer logic needed
  at all. DESIGN CHOSEN (2026-08-15, Doug): scoped down to a SINGLE
  favorite slot, not a named list -- no management UI needed at all as
  a result, since there's nothing to browse/rename/delete, just one
  slot that gets overwritten on every new Save. Entry points are both
  on panels that already exist, no new panel and no new top-level
  button on `DetectPanel`: "Save as Favorite" sits next to Edit/Remove
  on `ViewScreensPanel`'s screens list (captures the selected screen's
  field ID list + layout + count, overwriting whatever was saved
  before); "Load from Favorite..." is a new option on `AddScreenPanel`
  (pre-fills the field list/layout picker from the saved favorite if
  one exists, then continues through the unchanged add-screen path).
  Persistence: a small JSON sidecar (single {field_ids, layout} object,
  not a list), same pattern as v0.16.9's working-directory config
  file. Cross-sport-type risk (a field valid on the sport type a
  favorite was captured from might not be valid/meaningful on a
  DIFFERENT sport type it's applied to -- not yet tested) is WARN
  ONLY, Doug's call: show a note that the field was captured from a
  different sport type and hasn't been confirmed to work there, but
  let the user apply it anyway -- matches this toolkit's general
  policy of guiding rather than blocking on uncertain-but-not-
  dangerous cases. **BUILT (2026-08-24), Doug's go-ahead -- see `gui_app.py`
  v0.19.14's toolkit-table entry above for the final implementation,
  which followed this design exactly (single slot, WARN-ONLY
  cross-profile note, reuses the existing add-screen path unchanged).
  Real GUI behavior on Doug's own hardware still pending, same as every
  other GUI feature in this project. UPDATE (2026-08-24): real bug
  found via Doug's own use right after shipping -- a second Save
  silently overwrote the first favorite with no warning at all. Fixed
  (v0.19.16, see toolkit table above) with a YES/NO confirm naming
  what's currently saved before it's replaced. Doug also floated a
  possible FUTURE idea while discussing the fix, explicitly NOT scoped
  or built now: a `GarminBackups`-style `favorites/` folder alongside
  the existing `staging/`/`backups/` structure, to hold MULTIPLE named
  favorites rather than one slot, if this feature turns out to be
  popular. His own framing for why it'd be useful: a sport/discipline
  with similar screen needs (e.g. several road bikes each wanting the
  same power-meter screen) could get a quick way to replicate that
  screen across profiles without going through the on-device menu each
  time -- overwriting the single slot already covers exactly this use
  case today, one favorite at a time, just without the ability to keep
  more than one around simultaneously. No design work done on this
  yet -- worth reusing the confirm-dialog pattern just built, plus
  something like a name-to-file mapping (rather than one fixed
  filename) if/when it's actually scoped.**
- **Import an external profile -- one not backed up by this toolkit
  (raised by Doug, 2026-08-19, discussed not yet built; deliberately
  bundled with "Favorite screen" above as a candidate to build
  together, at Doug's call, rather than scoped as its own release).**
  Doug asked whether a user who wants to install/restore a `.fit`
  profile that never passed through this toolkit -- pulled from Garmin
  Connect, emailed by another rider, an old manual copy -- can do that
  via the GUI, and whether it would land in `working_dir/backups/`
  with its own timestamped folder the way toolkit-tracked profiles do.
  Answer, confirmed by reading the code (not yet built, this is the
  gap writeup): NO on both counts. The GUI has no `wx.FileDialog`
  anywhere in `gui_app.py` -- every source in every panel (Stage/View,
  Clone, Restore) is a `ListBox`/`ListCtrl` selection populated from
  what this toolkit already knows about (the live device via
  `backup_profiles()`, or its own `backups/<timestamp>/` history), so
  a foreign file has no entry point at all today. The CLI CAN do it --
  `garmin_device.py deploy <path> <target_filename>` accepts any local
  file and calls `write_to_newfiles()`, a plain copy-into-`NewFiles/`-
  and-verify with no `backup_profiles()`/`stage_for_edit()` involved --
  but that surfaced a second, real gap while investigating: `deploy`
  doesn't back up whatever profile is CURRENTLY live on the device
  under the target filename before overwriting it, unlike every
  GUI-driven write (which always gets a fresh `backup_profiles()` pass
  just by visiting the profile list first). Current guidance given to
  Doug: use the CLI `deploy` command directly, and manually run
  `garmin_device.py backup <working_dir>` immediately beforehand as a
  safety net, since `deploy` alone won't do it. Two candidate fixes if
  this gets built, not yet decided between: (1) a GUI "Import
  Profile..." entry point (`wx.FileDialog` + a filename-collision
  check reusing `ClonePanel`'s existing validation, landing the picked
  file straight into `staging/` via a `stage_for_edit()`-style copy so
  it behaves like any other staged profile from that point on -- Edit
  Screens, Deploy, etc. all already work unchanged); (2) closing the
  `deploy`-doesn't-backup-the-outgoing-profile gap itself, independent
  of the GUI question, since that's a real safety hole any CLI user
  hits today, not just the external-file case. **BUILT (2026-08-24),
  Doug's go-ahead -- chose candidate fix (1), the GUI "Import
  Profile..." entry point, built alongside "Favorite screen" above per
  his own suggestion (both touch `AddScreenPanel`/the
  add-a-screen-from-somewhere-else shape). Candidate fix (2), the
  `deploy`-doesn't-backup-the-outgoing-profile gap, was ALSO closed the
  same day -- see `garmin_device.py` v0.12.7's toolkit-table entry
  above -- since it's a real safety hole independent of the GUI
  question. See `gui_app.py` v0.19.15's toolkit-table entry above for
  the final Import implementation. Real GUI behavior on Doug's own
  hardware still pending.**
  **UPDATE (2026-08-24): real bug found testing this the same day --
  Doug's report: "in the review screen, I don't see a button to deploy
  it... if I go back, I don't see the imported Profile to move forward
  with deploying from there either." `ImportPanel.on_import()` had set
  `editing_path = None`, which works for the normal Stage-for-Edit flow
  but left the Screens review page with nothing to review/deploy for a
  fresh import (no screen edited yet) and no Back-button warning either.
  Fixed same day -- see `gui_app.py` v0.19.17's toolkit-table entry
  above for the full root-cause/fix writeup. Real GUI behavior on
  Doug's own hardware still pending.**
  **SECOND UPDATE (2026-08-24): two more real bugs found on the very
  next retest.** (1) A window-width blowup reaching Deploy (unwrapped
  `wx.StaticText` embedding a long dynamic path/filename -- established
  bug class for this codebase). (2) CONFIRMED on real hardware: picking
  an old file from this toolkit's own `working_dir/staging/` as the
  Import source (not a genuinely external file) produced a
  chained-suffix, 92-character suggested filename
  (`CyclingRoadTClone_clone_20260823_124234_staged_20260824_182004_staged_20260824_182104.fit`)
  that Doug confirmed sat unconsumed in `NewFiles/` even after a full
  power cycle -- the device silently declined to import it. Both fixed
  same day -- see `gui_app.py` v0.19.18's toolkit-table entry above for
  the full writeup. Real GUI behavior on Doug's own hardware still
  pending. This also surfaced a genuinely open question -- see new Open
  Item "On-device NewFiles filename constraints (unconfirmed)" below.**
- **On-device NewFiles filename constraints (unconfirmed) -- raised by
  Doug, 2026-08-24, while diagnosing the Import filename bug above.**
  What's actually confirmed: the device matches an incoming `NewFiles/`
  file to a profile BY FILENAME (`write_to_newfiles()`'s own docstring),
  and a 92-character chained-suffix filename was silently never
  consumed after a full power cycle -- some real limit or rejection
  rule exists. What's NOT confirmed: where the real threshold is, or
  what rule governs it. Doug's own theory, worth testing directly:
  the filename (leading up to `.fit`) might need to match -- or at
  least relate to -- the profile's own internal display name as shown
  on the Edge's profile-selection screen, which can include a
  sport/sub-sport prefix Garmin generates itself (his example:
  "CyclingRoad" leading a profile named "TClone"). That's a DIFFERENT
  string from the two length limits already confirmed and enforced
  elsewhere in this toolkit -- `NAME_FIELD_SIZE` (31-byte storage cap
  on `sport_mesgs[0].name`, the internal display-name FIELD) and
  `PROFILE_NAME_MAX_CHARS` (15-character on-device editor hard block,
  `fit_clone_profile.py` v1.0.1) -- neither of which is the FILENAME on
  the FAT/exFAT filesystem `NewFiles/`/`Sports/` live on; those two
  govern the separate `sport_mesgs[0].name` field's contents, not the
  filename string at all. No fix scoped or built for this -- v0.19.18
  addresses the one concrete, reproducible cause found (this toolkit's
  own chained internal suffixes inflating a SUGGESTED filename) without
  guessing at what the device's real filename rule is. Worth deliberate
  testing later if it comes up again: try a range of filename lengths
  against a real device and see exactly where NewFiles import starts
  silently failing, and whether it's really about matching the internal
  profile name specifically or just a flat length cutoff.
- **Restore a profile that's no longer on the device (first external
  GitHub user report, 2026-08-11; BUILT 2026-08-15, `gui_app.py`
  v0.19.0 -- see Doc rev 45 above for the full writeup of the final
  implementation, which followed the DESIGN CHOSEN note below exactly;
  CONFIRMED via Doug's own real GUI test, same day -- see Doc rev 50).**
  A user
  (currently on `garmin_device.py` directly, not the GUI yet) deleted a
  profile from the device and found no way in the GUI to restore it --
  correctly identified as a real gap, not user error. Root cause:
  `ProfileListPanel`'s profile list -- the ONLY entry point into
  `RestorePanel` (via its "Restore from Backup..." button, which
  requires a selection from that list) -- is sourced entirely from
  `garmin_device.backup_profiles()`'s read of the LIVE device's
  `Sports/` folder. A deleted profile vanishes from that list
  immediately, so it can never be selected again, even though its
  backup history is still sitting untouched under
  `working_dir/backups/<timestamp>/` -- `list_backup_history()` only
  needs a profile filename + working_dir, no device dependency at all.
  So this is purely a missing GUI entry point, not a missing backend
  capability -- good news for scope. `RestorePanel` itself needs ZERO
  changes; it already only depends on `frame.profile_filename` +
  `frame.working_dir`, never on whether that profile currently exists
  on the device. What's actually needed: (1) a new
  `garmin_device.py` helper (e.g. `list_all_backed_up_profiles
  (working_dir)`) that scans every `backups/<timestamp>/` folder and
  returns the UNION of every filename ever backed up, not just what's
  live now -- small, mirrors `list_backup_history()`'s existing
  directory-walk logic closely; (2) a new GUI entry point surfacing
  profile names that are in that backup-history set but NOT in the
  current live list (i.e. "deleted" from the device's point of view),
  then setting `frame.profile_filename` to the chosen one and routing
  straight to the existing `RestorePanel`/`DeployPanel` flow unchanged.
  DESIGN CHOSEN (2026-08-11, Doug): `ProfileListPanel` gets a second,
  visually separated section below the existing "On Device" list --
  something like "Deleted, but available to restore" -- populated from
  the new backup-history-union helper minus whatever's currently live.
  Implemented as a SECOND, separate list widget with its own header
  label rather than one list with an inline divider row, deliberately
  avoiding the kind of custom-selectable-divider hackery that would
  reopen the exact class of wx.ListCtrl/ListBox trouble this project
  has already hit three times this session. The existing "Restore from
  Backup..." button and `RestorePanel` need NO changes at all -- a
  selection from either section just sets `frame.profile_filename` and
  routes to the same already-built date-history picker, which has
  never cared whether that filename currently exists on the device.
  Stage/Clone/View Screens stay gated to the top (live) section only,
  since those genuinely require the profile to currently exist.
  Net effect: no new button, no new panel -- just one new list, one
  new backend helper, and the copy fix below. Also needs a small copy
  fix either way: `RestorePanel.on_restore()`'s confirmation dialog currently says
  "REPLACING what's currently on it," which is only true for the
  existing live-profile case -- restoring a deleted profile would be
  closer to *recreating* it, not replacing anything. UPDATE
  (2026-08-11, same day): the one real open technical risk flagged
  here — whether NewFiles correctly handles a filename that isn't
  currently present in `Sports/` at all, as opposed to replacing an
  existing file — is now RESOLVED. Doug reported Clone Profile (which
  shares this exact mechanism) has in fact already been confirmed live
  on real hardware: at least two working clones, `Clonebox` and
  `CloneRoad`, both deployed under brand-new filenames via NewFiles.
  See the corrected Clone Profile entry above (which had incorrectly
  been carrying a stale "not yet tested" note) for the full
  confirmation. SECOND, MORE DIRECT CONFIRMATION (2026-08-11, same
  day): Doug tested the exact scenario this feature is about, via
  `garmin_device.py deploy <backup_of_a_deleted_profile.fit>
  <target_profile_filename>` — a backup of a profile he'd deleted from
  the device, targeting that now-absent filename. Confirmed via
  on-device verification: NewFiles correctly RECREATED the deleted
  profile, not just accepted a never-before-seen name (Clone's case).
  This is the stronger of the two confirmations, since it's the actual
  restore-a-deleted-profile path, not just an analogous one — the
  backend/CLI mechanics this feature would wrap are now fully proven
  end to end. This removes what was the single biggest open risk for
  this feature — the remaining work is genuinely just the GUI
  entry-point gap described above. Also worth a documentation caveat rather than a
  code fix: `list_backup_history()` (and any new helper built on it)
  identifies a profile purely by filename, so if a filename is ever
  reused for an unrelated profile after the original was deleted, its
  backup history would silently mix both profiles' snapshots together
  -- an existing characteristic of the backup system, not new to this
  feature, but more likely to surface once "browse backups of
  something not currently live" becomes a normal, supported action
  instead of an edge case. IMPLEMENTATION DEFERRED (2026-08-11, Doug's
  decision): fully scoped and de-risked, design chosen, but not
  urgent -- `garmin_device.py deploy` is a confirmed-working manual
  workaround in the meantime. Holding off building this alone; plan is
  to watch for anything else that turns up over the next few days and
  fold multiple changes into one future release, alongside the
  `startup.txt` feature below. BUILT (2026-08-15, Doug's go-ahead) --
  see Doc rev 45 at the top of this document for the final
  implementation writeup, which matches the DESIGN CHOSEN note above
  exactly, including the "no new button, no new panel" constraint.
- **Reduce redundant profile backups -- LOW PRIORITY (requested by a
  tester, scoped 2026-08-11; BUILT 2026-08-15, Doug's go-ahead,
  `gui_app.py` v0.19.1 -- see Doc rev 46 above for the full writeup).**
  `ProfileListPanel` used to unconditionally re-back-up all profiles
  on every visit to the profile list, not just when
  something actually changed -- a tester reported the confusing
  side-effect directly (going back and re-selecting a different
  profile printed another "Backed up X profile(s)..." message, with no
  edits in between). Scoped fix: track a frame-level `needs_backup`
  flag, reset to `True` on either of the two real "device state may
  have changed" events -- a fresh `DetectPanel.on_detect()`, or
  `DeployPanel.on_check()` confirming reconnect after a deploy (the
  naive "just back up once ever this session" version would miss that
  second case, silently skipping the backup that captures state right
  after a real edit -- the one that matters most). "Refresh (re-backup
  + re-list)" would still always force a real backup regardless of the
  flag, honoring its own label. Contained entirely to `gui_app.py`, no
  changes needed to `garmin_device.py` or any CLI tool. Doug's call
  (2026-08-11): worth doing, but LOW priority -- his own
  `~/GarminBackups` folder is only ~1MB (plus ~160KB staging) even
  after heavy recent testing, and even the much larger prior dev
  folder (~4-5GB across 1098 `.fit` files accumulated over this whole
  project) isn't a real problem at these file sizes. The redundant
  copies are annoying (terminal noise, wasted I/O) but not a resource
  concern. Batched with the other low-priority/deferred items.
- **Keep backups of separate physical devices apart -- LOW PRIORITY
  (requested by a tester, scoped 2026-08-15, not yet built).** A
  tester who alternates between two Garmin Edge units wants their
  backups kept separate rather than folding together into one folder.
  The base capability already exists and shipped a while back: the
  "Change..." button on `ProfileListPanel` lets a user redirect
  `working_dir` to any folder at any time, remembered across restarts
  (`load_saved_working_dir()`/`save_working_dir()`, v0.16.9). The real
  gap: that's one GLOBAL setting, remembered as "whatever was used
  last," not "which folder belongs to which device" -- someone
  swapping between two units has to remember to click Change every
  time, and forgetting once mixes both devices' backups into whichever
  folder happened to be active. DESIGN CHOSEN (2026-08-15, Doug):
  auto-switch by device serial number rather than leave it fully
  manual. `garmin_device.get_device_info()` already reads a
  `serial_number` off `Device.fit` on every Detect (existing call,
  `DetectPanel.on_detect()`) -- a reliable per-device key that's
  already sitting in memory unused for this purpose. Scope: extend the
  existing JSON config sidecar
  (`~/.garmin_screen_editor_config.json`) with a serial-keyed mapping
  alongside the current single `working_dir` value (which remains the
  fallback/default). On a successful Detect, if the connected device's
  serial number has a saved mapping, `frame.working_dir` auto-switches
  to it; if the serial is new (never seen before) or unreadable (no
  `Device.fit` -- the existing "device info unavailable" case
  `DetectPanel` already handles), behavior falls back to today's
  manual-Change/last-used default, unchanged. The existing "Change..."
  button's handler additionally saves the newly-picked folder keyed to
  whichever serial is currently connected (if any), so a manual
  override while a specific device is connected becomes that device's
  remembered folder going forward -- no separate "assign to device"
  UI action needed, it piggybacks on the button that already exists.
  Worth a small UI touch: the working-directory label on
  `ProfileListPanel` should indicate when a folder was auto-selected
  for the connected device's serial, vs. the plain global default, so
  the switch is visible rather than silent. Contained entirely to
  `gui_app.py` -- no `garmin_device.py`/CLI changes needed beyond
  reading a field (`serial_number`) that `get_device_info()` already
  returns. Doug's call: worth doing, but LOW priority, same batch as
  the redundant-backups item above. Not yet built -- scoped and
  design-locked only.
  **SCOPE REVIEW (2026-08-26), ahead of possibly building this:**
  reviewed against everything shipped since August (backup pruning,
  Import, the deploy safety fix) -- no conflicts, all downstream
  features just read whatever `frame.working_dir` currently is,
  transparent to switching WHEN that gets set. One real implementation
  wrinkle found: `save_working_dir()` currently does a blind
  `json.dump({"working_dir": path}, ...)` overwrite of the whole config
  file -- adding a serial map means it needs to become read-modify-write
  instead, or a plain "Change..." click would silently wipe the map.
  Also raised: the internal `serial_number` (Device.fit) is a DIFFERENT
  number from the case-printed serial Garmin support asks for (Doug's
  own earlier observation) -- judged NOT a blocker for this feature,
  since it only needs to be a stable, unique per-unit key, which the
  FIT protocol's `file_id.serial_number` convention should already
  guarantee; it just means the number won't be human-cross-referenceable
  against the sticker on the device.

  **NEW, related finding (2026-08-26) -- Activity Profile files embed
  the SAME device serial number, CONFIRMED on real hardware, opening up
  a genuinely separate, valuable addition: a cross-device profile
  safety check.** Doug asked whether Activity Profiles contain a copy
  of the device serial, specifically to make sure a profile from one
  Edge can't accidentally get written to a different one (unknown
  effect, never tested). Checked directly (not assumed): `fit_dump.py
  dump` against a real profile (`CyclingRoadROAD.fit`) shows
  `file_id_mesgs[0]` with the SAME structure `get_device_info()` already
  reads from `Device.fit` -- `serial_number`, `manufacturer`,
  `garmin_product`, plus `product`/`number`/`type` fields `Device.fit`
  doesn't carry. Independently re-verified by running `fit_dump.py`
  directly against Doug's uploaded file in this session (not just
  trusting his pasted output) -- byte-for-byte matching values. THE
  deciding question -- does this profile-embedded serial actually match
  THIS SAME PHYSICAL UNIT's `Device.fit` serial, or is it some other
  identifier (e.g. baked in once at profile-template creation) --
  CONFIRMED YES via Doug's own `garmin_device.py detect` output against
  the SAME device: both read `3356943454` exactly. This makes a
  cross-device check technically sound: before a deploy (or Restore/
  Clone/Import crossing devices), compare the connected device's serial
  (`frame.device_serial`, already read at Detect time for the folder
  auto-switch feature above) against the TARGET profile's own
  `file_id_mesgs[0].serial_number` (would need a new small
  `garmin_device.py` read -- `fit_dump.py`'s `decode_file()` already
  does the actual decoding, so this is a thin wrapper, not new
  low-level work) and WARN (not hard-block, matching this project's
  existing posture for possible-but-unconfirmed-effect situations, same
  as the "Workout" screen edit warning) on a mismatch, since the actual
  on-device EFFECT of importing a profile whose internal serial doesn't
  match the receiving unit is still unknown/untested -- this check
  would only be a heads-up, not a proven-necessary guard. Not yet
  scoped in implementation detail (which write paths get the check,
  exact warning wording, whether Clone-from-a-different-device's-backup
  needs the same treatment as a straight Deploy) or built -- this is
  confirmation that the DATA exists and matches as needed, a
  prerequisite finding, not a finished design. Worth building alongside
  the folder auto-switch feature above if/when Doug gives the
  go-ahead, since both lean on the exact same `frame.device_serial`
  value.

  **REAL HARDWARE TEST (2026-08-26), Doug -- cross-device deploy
  actually tried, not just theorized.** Generated a test file (patched
  from Doug's real `CyclingRoadROAD.fit`): `file_id_mesgs[0].
  serial_number` forced to a fake `1234567890` (was `3356943454`,
  Doug's real device serial) and `sport_mesgs[0].name` changed to
  "SerialTest," verified via `fit_dump.py diff`/CRC before handing it
  over -- confirmed as the ONLY two changes from the original, nothing
  else touched. Doug placed it in `NewFiles/` on his real Edge 530 and
  restarted. Result, independently re-verified against his uploaded
  post-restart file (not just his description): the device imported it
  cleanly, keeping the name and EVERY screen/field/zone byte-identical
  to what was sent, but silently rewrote `file_id_mesgs[0].
  serial_number` back to its own real serial (`3356943454`) --
  confirming Doug's own read of the result. A second, unplanned finding
  from the same diff: `file_id_mesgs[0].number` also changed, `0` ->
  `6` -- not something either of us was testing for, and not something
  this project has ever tracked before. Unconfirmed what it represents
  (a plausible guess: some kind of internal sequence/instance count the
  device assigns to sport-type files as it processes them, but that's
  a guess, not verified -- would need `number` checked across Doug's
  other existing profiles to say anything definite). Logged as a new,
  small, low-priority open question, not chased further right now.

  **IMPLICATIONS, Doug's own conclusions from the result:** (1) This
  is real, positive evidence for the warranty-replacement/device-
  upgrade scenario Doug raised when this whole side-investigation
  started -- restoring a backup from an old physical unit onto a new
  one via NewFiles appears to work cleanly, at least for this one test,
  since the device self-corrects the identity field rather than
  rejecting the file or corrupting anything. (2) REFRAMES the proposed
  cross-device warning above -- since a serial mismatch is now
  demonstrated harmless-and-self-correcting rather than an unknown
  risk, a scary "this could be dangerous" warning would overstate what
  the evidence actually shows. Doug's own framing, adopted: a quieter,
  informational nudge along the lines of "this profile was backed up
  from a different device -- are you sure this is the right one plugged
  in?" fits the evidence better than a caution/danger-styled warning.
  (3) NEW use case for the underlying serial-based device-identity
  plumbing, broadening this beyond Doug's own single-user, two-device
  case: Doug described a bicycle CLUB scenario where a technically able
  "admin" member manages devices for several less-technical members --
  the same per-device serial identification this Open Item already
  needs could let an admin push shared "club standard" profiles out to
  multiple members' devices AND keep each individual member's own
  personal profiles correctly separated and backed up by device serial,
  rather than everyone's files folding together into one folder. Not
  scoped in implementation detail (this would likely need more than the
  single-global-`working_dir`-with-a-serial-override shape already
  planned -- e.g. a real multi-member folder structure, and some way to
  distinguish "push this profile to many devices" from "back up this
  one device's own profiles") -- flagged here as a real, broader
  motivation for eventually prioritizing this Open Item higher than
  "low," not a commitment to build the club-admin shape specifically.
- **Set/reset a profile's odometer total (`Totals.fit`) -- UNDER
  CONSIDERATION, LOW PRIORITY (raised and scoped 2026-08-28, Doug's own
  call: not building for now, riskier than he wants to take on).**
  Doug wanted a toolkit way to set a profile's lifetime mileage total to
  a known-accurate figure (e.g. Strava YTD/all-time), or reset it to
  zero, rather than relying only on the on-device "History > Totals >
  Delete Totals" reset. The store was located and fully mapped this same
  session (see Doc rev 86 above for the full writeup): `Garmin/Totals/
  Totals.fit`, FIT mesg_num 33 (`totals_mesgs`), one message per profile
  slot, `distance` at def_num 1 (uint32, plain meters, no scale factor)
  -- confirmed exact against Doug's real odometer reading (9377167 raw =
  5,826.70 mi). Patch mechanics would be straightforward, reusing this
  toolkit's existing byte-patch-plus-CRC pattern
  (`fit_clone_profile.py`'s approach) and the existing `NewFiles/`
  deploy mechanism unchanged. NOT SCOPED FURTHER, BY DESIGN -- two real
  risks were flagged and Doug decided they outweigh the value right now:
  (1) a profile slot is identified purely by positional
  `message_index`, since the 32-byte name field FIT stores alongside it
  is only partially decoded (shows as garbled fragments) -- no reliable
  name-based lookup exists yet, so picking the wrong slot without a
  careful preview/confirm step is a real hazard; (2) `message_index` 0
  looks like a cross-profile aggregate total that doesn't cleanly sum
  from the other entries, and how the device recomputes it (if at all)
  after an externally-edited totals file is untested. Compounding
  factor Doug pointed out: `Totals.fit` also retains zeroed-out entries
  for every test/sandbox/clone profile created during this project's
  own field-ID exploration work and since deleted from the device --
  Doug's currently-active profiles are only MOUNTAIN, INDOOR, ROAD, and
  GRAVEL -- adding clutter that makes confidently identifying the right
  slot harder. If revisited later, a name-lookup improvement (fully
  decoding the def_num 10 packed field) and a firm answer on how
  `message_index` 0 behaves would both need to land before this is safe
  to build.
  **REFINEMENT (2026-08-28, same day) -- risk (1) partially resolved.**
  Doug spotted, and direct byte inspection confirmed, a real active/
  deleted flag in the def_num=10 field: active profiles have their name
  starting at byte offset 0; deleted-profile remnants have a `\x00` at
  offset 0 instead, with the (name minus its first character) starting
  at offset 1 -- everything else in the record untouched. So `raw[0] ==
  0x00` reliably flags a deleted (or the aggregate `message_index` 0)
  slot, and `raw[0] != 0x00` flags an active one with its full name
  intact -- a real name-based lookup is feasible after all, not just
  positional `message_index`. Risk (2), `message_index` 0's aggregate
  behavior after an edit, is still unknown. Doug also sketched a rough
  UI shape for whenever this is revisited: read `Totals/Totals.fit` when
  a profile is selected, offer the odometer value as a display/edit
  option (Reset or set-to-value), hold the change in the same
  in-progress edit session as screen edits (not written immediately),
  and on Apply/Deploy write the modified `Totals.fit` to `NewFiles/`
  alongside any pending profile `.fit` -- reusing the existing staged-
  edit/Apply/Deploy pattern rather than a new mechanism. Still not
  scoped further or built -- logged for a later revisit.
  **ADDENDUM (2026-08-31) -- risk (2) downgraded from "unknown" to
  "known and addressable," plus a design answer for a SET (not just
  RESET) operation. See Doc rev 93 at the top of this document for the
  full writeup.** Short version: a real Edge 530 forum thread (Doug's
  own model) confirms the `message_index` 0 aggregate row must equal the
  sum of all profile rows -- editing a profile's own row without also
  adjusting the aggregate by the same delta produces exactly this Open
  Item's worst-case symptom, the edited profile's value silently
  reverting to 0 on reboot, even though the write itself "succeeded."
  So: any future SET (not RESET-to-zero) implementation must patch BOTH
  the target profile's row and the `message_index` 0 aggregate row's
  `distance` by the same delta, not just the one row. Design answer to
  Doug's separate question (how to handle `timer_time`/`calories`/
  `sessions` when SETTING a distance): scale `timer_time` and `calories`
  proportionally to the distance-change ratio; leave `sessions`
  untouched by default (a real ride count, not a quantity that should be
  fabricated/rounded); be explicit in any future UI/docs that scaled
  values are best-effort/consistency-preserving, not literal history.
  Real-world confirmation the `NewFiles/`-based write path itself works
  on this exact model when the aggregate/profile rows are kept
  consistent and the file's structure is otherwise left untouched
  (matches this toolkit's existing byte-patch-plus-CRC approach, not a
  CSV-roundtrip rebuild). Still NOT SCOPED FURTHER OR BUILT -- no
  go-ahead given, stays low-priority.
  **BACK-BURNERED (2026-09-01, Doug's call) -- see Doc rev 94 at the top
  of this document for the full writeup.** Short version: the write-path
  mechanics are now reasonably de-risked, but Doug's conclusion is that
  a SET operation only pays off if the user can also supply sensible
  `timer_time`/`calories`/`sessions` values alongside the new distance
  -- otherwise the proportional-scaling answer from Doc rev 93 has
  nothing real to scale from, and the result looks as broken as leaving
  those fields untouched. More involved than the "just re-enter your
  mileage" model people expect from a plain bicycle computer's single
  odometer counter. Deprioritized to "won't build unless specifically
  requested" -- not closed, just off the active list.
- **f10=38 "Workout" field-reading anomaly (reported 2026-08-16, Doug,
  `CyclingEbike.fit` -- RESOLVED, real data confirmed AND a real,
  citable explanation of what this screen actually is; edit-warning
  BUILT).** Doug found 3 new confirmed screen types on this profile:
  38 "Workout", 58 "eBike Metrics", 95 "STEPS Metrics (Shimano)"
  (corrected from an initial 39/59/96 -- see "Corrections and lessons
  learned" above for how that happened), all added to
  `NAMED_SCREEN_TYPES` (`fit_dump.py` v2.4.14). eBike Metrics and
  STEPS Metrics behave like ordinary named types. "Workout" (f10=38)
  is different: on the real device, selecting this screen in the
  on-device editor shows NO fields or options at all -- only "Remove"
  and "Reorder Screen," the same restricted menu Map/ClimbPro get
  (those two also can't have fields edited, per `NO_SHOW_TOGGLE_TYPES`/
  `hide_unsupported_screen_type()`). This toolkit's own `screens`/
  `ViewScreensPanel`/`EditScreenPanel` views show this same f10=38
  slot with real field content -- CONFIRMED, via a direct raw-byte
  comparison of Doug's actual uploaded file (not just field-name
  matching), that slot 6's f10=38 record's field-ID array is byte-
  for-byte IDENTICAL, all 10 positions, to slot 1's Cycling Dynamics
  (f10=63) record on the SAME profile. This is real, accurately-read
  data -- `classify_screens()`/`active_field_ids()` are working
  correctly, there is no field-reading bug. While inspecting the raw
  dump, found the SAME pattern twice more: this profile's two Removed
  screens with real field content (slots 11, 12) are each byte-for-
  byte identical to the currently-active eBike Metrics/STEPS Metrics
  records (slots 4, 5) -- three confirmed exact-duplicate pairs on one
  profile, not a single coincidence -- consistent with Garmin's
  firmware auto-creating these types from a FIXED default field
  template each time, the same way Map/Elevation/ClimbPro already do.
  WHAT "WORKOUT" ACTUALLY IS, now backed by an official source rather
  than pure inference: Doug independently noticed a `Workouts` folder
  (with empty `Guided`/`Scheduled` subfolders, since he's never used
  the feature) sitting at `garmin_root` alongside `Sports`, and asked
  whether the Workout screen might need loaded workout data to mean
  anything -- exactly right. Garmin's own Edge 530 Owner's Manual
  (Training > Workouts) confirms structured Workouts are a completely
  separate subsystem from Activity Profile screens: workouts are
  created in Garmin Connect or on-device and synced into
  `GARMIN/Workouts/Guided` or `/Scheduled`, and starting one "displays
  each step of the workout, the target (if any), and current workout
  data" -- a dynamically-rendered display, not a field-based screen at
  all. This is almost certainly what f10=38 renders, only while a
  Workout is actively running -- the same "only meaningful under a
  specific runtime condition" pattern already established for
  ClimbPro/Segment/GroupTrack, which is exactly the comparison Doug
  drew himself before this was confirmed. Matches every piece of
  evidence: Doug's empty Workouts subfolders (never seen it render),
  the on-device editor offering no field options for it, and the
  byte-for-byte duplicate field content (real bytes present, likely
  never consulted by this screen's actual renderer). BUILT (Doug's
  go-ahead): a new, narrow WARNING in `EditScreenPanel` -- `fit_dump.
  py`'s new `FIELD_EDIT_UNCERTAIN_TYPES = {38}` backs a new
  `field_edit_uncertain_warning_text()` (`gui_app.py`), shown only
  when editing an f10=38 screen, explaining plainly that the edit is
  mechanically safe (same proven write path as every other screen)
  but likely has no visible on-device effect. Deliberately a WARNING,
  not a hard block like Map/ClimbPro's Show-toggle guard (that one's
  backed by independent on-device confirmation neither has a toggle
  at all; this is one profile's worth of evidence, and the downside of
  a wrong edit here is a no-op, not device damage). `fit_dump.py` now
  v2.4.15, `gui_app.py` now v0.19.4.
  UPDATE (2026-08-20): Doug's field census turned up 5 new IDs (45
  Workout Step, 511 Workout Comparison, 521 Target -- corrected same
  day from an initial mistyped 512, Doug's own catch, see `fit_dump.py`
  v2.4.22 -- 522 Duration, 523 Step Time) that read by name as exactly
  the kind of structured-step data the Owner's Manual describes for a
  running Workout. Doug confirmed all 9 fields from this batch,
  including these 5, are verified against the real on-device screen --
  same confirmation standard as every other entry in `FIELD_ID_NAMES`,
  so their ID->name identity itself is solid. Still not treated as
  resolving anything HERE, though -- that confirmation establishes
  what each field IS, not where or how it renders when placed on the
  f10=38 "Workout" screen specifically, and none of the 9 were
  individually tied to f10=38 by direct testing. Worth Doug's
  attention if he ever loads a
  real Workout and can check whether any of these 5 actually populate
  on that dynamically-rendered display; until then this stays exactly
  as RESOLVED/WARNING-only above, just with a slightly warmer lead.
- **Backup retention/pruning.** Backups accumulate indefinitely right
  now — nothing deletes old ones. Deliberately left out of MVP.
  UPDATE (2026-08-11): Doug's real usage numbers (see above) confirm
  this genuinely isn't urgent at Garmin-profile file sizes -- even
  ~1098 backed-up `.fit` files over the life of this project only came
  to ~4-5GB. His own suggestion, worth weighing against the
  once-per-session change above: a cleanup/pruning routine (e.g.
  auto-delete backups older than N days, or cap total count/size) may
  be the more useful thing to build here than reducing HOW OFTEN
  backups happen -- it addresses the same "backups accumulate" root
  concern but as a real, permanent feature (worth having regardless of
  file-count growth over a long project lifetime) rather than a minor
  redundant-work optimization. Not yet scoped in detail; worth doing
  before the once-per-session change if only one gets built, since it
  solves a longer-term problem the other doesn't touch at all.
  **BUILT (2026-08-25), Doug's go-ahead -- chose time-based folder
  deletion (delete entire `backups/<timestamp>/` folders older than a
  chosen day count), manual-only trigger (a "Clean Up Old Backups..."
  button, live preview, explicit confirm -- no automatic/silent
  pruning), 30-day default window. Rejected the two alternatives put to
  him: keep-latest-N-per-profile (too complex -- folders snapshot every
  profile together, not one per profile) and keep-only-latest (cuts
  against Restore-from-Backup's whole purpose, not justified by his own
  disk numbers above). See `garmin_device.py` v0.12.8 and `gui_app.py`
  v0.19.19's toolkit-table entries above for the full implementation
  writeup. CONFIRMED via Doug's own real hardware test (2026-08-25) --
  worked as designed.**
- **Model portability (discussed 2026-08-06, not yet built).** The
  `data_screen` layout mechanism is count-driven, not geometry-stored —
  a screen's grid shape comes from field 3 (count) + field 8 (A/B flag)
  alone, looked up against a firmware-side table (`LAYOUT_GRIDS` in
  `gui_app.py`, sourced from the developer's own Edge 530 reference),
  never computed or stored per screen. This means the *architecture*
  plausibly generalizes to other Edge models, but the *numbers*
  (`MAX_FIELDS_PER_SCREEN`, the 10-user-screen cap, which counts get a
  B variant, and `LAYOUT_GRIDS` itself) are tied to each model's actual
  screen size/firmware and do NOT — each would need its own on-device
  confirmation, same process used for the 530, before being trusted.
  `garmin_device.get_device_info()` already surfaces `garmin_product`
  (e.g. `'edge_530'`) from the device's own FIT identification message
  on every connect, so model detection itself is not a gap. Sketched
  approach for when a second model's numbers exist: a `DEVICE_PROFILES`
  dict keyed by `garmin_product`, each entry holding that model's caps/
  `LAYOUT_GRIDS`, with `edge_530` as the seed entry and an unrecognized
  model falling back to the 530's numbers with a visible non-blocking
  warning (530-as-floor is the safe fallback direction — understating a
  bigger screen's real limits is just annoying, overstating a smaller
  one's is the dangerous direction, a screen that builds fine in the
  GUI but fails/truncates on-device). Deliberately NOT built yet — no
  second model's real numbers exist to plug in, and guessing at the
  dict's shape ahead of real data would just be speculative scaffolding,
  same reasoning applied throughout this project. Doug noted he can't
  personally test other models but may be able to seed
  `DEVICE_PROFILES` with values sourced from Garmin's published specs/
  product pages online, pending confirmation from a beta tester with
  different hardware, rather than needing a live device in hand purely
  to get started.
  **Supporting evidence, not a confirmation (2026-08-30, Doug's own
  research, no device in hand):** a demo video of on-device screen
  editing on the Edge 850/1050 (current touchscreen models) showed the
  same 10-field-per-screen cap and the same screen layouts already
  confirmed on the 530 -- just rendered on a larger touchscreen, not a
  different structure. Doug also noted the touchscreen models have a
  nicer on-device editing UX, but it's still purely on-device (same
  category this toolkit works around, not a new interface this toolkit
  would need to integrate with), and that Garmin Connect's phone app can
  also edit profiles, but Doug found that path "a little tedious" in
  his own look at it. This is real supporting evidence for the
  count-driven layout theory above, but explicitly secondhand (a video,
  not a real device this toolkit has touched) -- still logged as NOT
  built/NOT confirmed the way this project requires before trusting a
  number, same standard as everything else here.

---

## GUI scoping and implementation

**Scoping is complete; implementation is underway, one step at a
time.** `gui_app.py` currently covers steps 1-3:

- **Step 1** (`DetectPanel`) — detect device, show device info via
  `get_device_info()`. Detection is manual/on-demand (a "Detect
  Garmin" button, also fired once automatically whenever this panel
  becomes active), matching `garmin_device.py`'s own polling model —
  there's no USB hot-plug listener.
- **Steps 2+3** (`ProfileListPanel`) — list profiles and back all of
  them up in the same call (`garmin_device.backup_profiles()` already
  enumerates every profile in `Sports/` to back each one up, so the
  list shown to the user is just that result's keys — no separate,
  redundant `list_profiles()` call needed). A working-directory field
  (defaulting to the path used throughout manual CLI testing, but
  user-changeable) controls where backups and staged files land.
  Selecting a profile and clicking "Stage Selected for Edit" calls
  `stage_for_edit()` (lineage-tracked, as always). A "Restore from
  Backup..." button exists as a stub for a later slice.
- **Step 4** (`ViewScreensPanel`) — shows the staged profile's current
  screens, read-only, built directly on `fit_dump.py`'s
  `classify_screens()`/`active_field_ids()`/`field_name()` (imported
  in-process, no subprocess call). The reorderable/Active screens are
  a `wx.ListCtrl` in report mode (Pos/Slot/Count/Layout/Flag/Fields)
  — deliberately a list control even though this slice is read-only,
  since step 6's Move Up/Move Down buttons will act on whichever row
  is selected here. Conditional and Removed screens are shown
  underneath as plain text, since editing them is out of MVP scope.
  Selecting a row and clicking "Edit Selected Screen →" drills into
  step 6. A "Discard Edits" button resets the working copy back to
  the untouched staged file.
- **Step 6, partial** (`EditScreenPanel`) — edit one screen's fields
  and layout. Field list (`wx.ListBox`) with Move Up/Move Down
  (swap-fields-equivalent, no system-screen guard since a pure
  reorder doesn't change content); "+ Add Field..."/"− Remove Field"
  (both replace the whole field array via `patch_screen`, guarded by
  `check_system_screen_guard()`, with a confirmation dialog on a
  match rather than a hard block); a two-option A/B layout radio,
  auto-restricted to "B" only when the current count is in
  `COUNTS_WITH_B_VARIANT`; and a live read-only `LayoutDiagramPanel`
  showing the actual on-device grid (full-width rows vs. side-by-side
  pairs) from `LAYOUT_GRIDS`, driven by the developer's own text-based
  Edge 530 layout reference (see "On-device layout geometry", above).
  A "Show Screen" checkbox toggles field 12, matching the on-device
  wording exactly (Garmin's own UI uses "Show," not "Hide," per the
  developer). Turning it OFF (hiding) is gated two ways, checked in
  order: first a HARD, non-overridable block
  (`would_hide_last_visible_screen()`, `fit_patch.py` v1.9.0) if this
  would leave zero visible plain user screens on the profile -- now
  correctly f10-based, see "Screen identity — SOLVED" above --
  followed by `check_system_screen_guard()`'s softer heuristic
  confirm dialog for likely system/overlay content. Map is confirmed
  to have no on-device Show Screen toggle at all on standard outdoor
  profiles; forcing `f12=1` on it via a raw file write is genuinely
  untested, not just a possible misidentification -- same caution
  applies to any named Garmin screen type, since none of them have
  been deliberately hidden this way and confirmed safe. Turning it
  back ON (showing) is NOT gated, since that's a normal,
  well-understood on-device action with no equivalent risk. Every
  change is applied
  immediately to `MainFrame.editing_path` (a scratch working copy of
  the staged file) via direct `fit_patch.py` function calls -- never a
  subprocess, never simulated -- and the panel always re-reads the
  actual resulting bytes afterward. **DONE (v0.7.0):** screen-level
  reordering -- `ViewScreensPanel` has its own Move Up/Down pair,
  acting on `swap_display_order()` (`--swap-order`'s backend), same
  select-plus-buttons pattern as field reordering.

Architecture: `MainFrame` owns app state (`garmin_root`,
`working_dir`, `staged_path`, `profile_filename`, `editing_path`,
`editing_slot`) and swaps between panel instances in one window
rather than opening a new top-level window per step. `editing_path`
IS the pending-edit queue -- see the `gui_app.py` module docstring's
"Editing architecture" note -- rather than an abstract in-memory list
that could drift from real file semantics; it persists across edits
to multiple screens within one session. Build order going forward
follows the same pattern established from step 1: wire one step of
the flow below to its already-validated backend function, test
against real hardware, then move to the next step.

### Editing UX decision (for step 6, decided ahead of building it)

Reordering screens and fields will be **select + Move Up/Move Down
buttons, not drag-and-drop**. Every reorder capability already
validated on real hardware is a *swap* — `--swap-order` swaps two
screens' display positions, `--swap-fields` swaps two field
positions within a screen — and "move up" is exactly "swap with the
row above," so buttons map onto the tested primitives with zero new
backend logic. Drag-and-drop in wxPython has no built-in reorderable
list control, behaves inconsistently across platforms, and is much
harder to make keyboard-accessible; not worth the cost here.

Field count changes and reassigning which fields appear on a screen
don't map onto a swap at all — `--fields` replaces a screen's entire
field list and derives the count from its length (why both
same-count-replace and count-increase were separately validated).
So "Add Field" / "Remove Field" / "Replace Field" in the GUI all
funnel into one operation: take the screen's current list, apply the
one change, queue a `--fields` call with the resulting full list —
fed from a picker over the known `FIELD_ID_NAMES` catalog, not
free-text entry, so a user can't accidentally queue an unresolved or
mistyped ID.

**Status:** Add Field and Remove Field are built (`EditScreenPanel`
since v0.2.0, `AddScreenPanel` since v0.8.0). **DONE (v0.9.0):**
"Replace Field" -- a "Change Type..." button on both panels that swaps
one field's ID in place, without the Remove+Add+reposition workaround.
In `EditScreenPanel` it funnels into the exact same
`_apply_field_list()`/`check_system_screen_guard()` path Add/Remove
Field already use; in `AddScreenPanel` it's a pure in-memory edit
since nothing's written until Create Screen. Headless-verified against
a real user screen (Screen 2, VAM -> Max Speed) -- guard correctly
passed through with no false warning, only the target field changed,
CRC valid. **CONFIRMED live through the actual GUI on real hardware**:
changing a field on an existing user-defined data screen worked as
expected; attempting the same on ClimbPro correctly triggered the
named-Garmin-type confirmation dialog (f10=104) instead of silently
proceeding -- the guard is doing its job on a real, non-user screen,
not just in headless testing. **Follow-up, CONFIRMED (2026-08-05):**
the developer went ahead and overrode the guard on ClimbPro, deployed,
and verified on the reconnected/restarted Sandbox profile -- the field
change took and survived the round-trip. This closes the loose end
just above: overriding check_system_screen_guard() to edit a named
Garmin type's field content via a raw file write is now confirmed
SAFE for ClimbPro specifically, not just theoretically possible. Not
yet extended to any other named type (Map, Compass, GroupTrack List,
etc.) -- each would need its own confirmation before being treated as
equally safe, since "this is genuinely untested" language elsewhere in
the docs (FIT_PATCH.md's `--force` section, the GUI's confirmation
dialog wording) was written before this result and should be read as
"untested for types other than ClimbPro" going forward.

**Toolkit choice:** leaning **wxPython** over CustomTkinter —
`wx.grid.Grid` / `wx.propgrid` map naturally onto "list of screens,
each with editable properties," avoiding the need for two separate
toolkits.

**Agreed high-level flow**, as the scoping baseline going forward:

1. Detect the device, and show device info (`get_device_info()`) so a
   multi-device user can confirm the right one is connected.
2. List profiles on the device.
3. Back up all profiles (cheap — do it on every connect, regardless
   of which profile ends up being touched) and let the user select
   one, then stage it (lineage-tracked).
4. Alongside editing, offer **"Restore from a previous backup"** as a
   sibling action to editing, not a buried settings option — see
   *Restore from backup*, below.
5. Show the selected profile's current screens, read-only.
6. Present available actions, including a real "Add New Screen" panel
   (pick an unconfigured slot, set fields/layout, f9/f10 auto-assigned)
   — CONFIRMED working as of `fit_patch.py` v1.12.0, BUILT as of
   `gui_app.py` v0.8.0, no longer an on-device-menu redirect; see
   *Adding a new screen*, above.
7. ~~Apply changes in a loop — a pending/preview state, not immediate
   writes~~ **SUPERSEDED by the architecture actually built (see
   "Editing architecture" above):** every change (field edits, layout,
   reorder, Add-New-Screen, Change Type) is already applied
   immediately to `MainFrame.editing_path` the moment it's made, one
   real `fit_patch.py` call per click, with the guarded-operation
   confirmation dialog (`check_system_screen_guard()`) already
   happening at that same moment. There's no separate abstract
   pending-changes queue to build or apply — `editing_path` already IS
   that queue, in real bytes, so this step turned out to have nothing
   left to do by the time steps 1-6 were finished.
8. Do a final pre-flight verification (diff + CRC) of the accumulated
   result before touching the device -- **DONE (`gui_app.py` v0.10.0,
   `PreflightPanel`, "Review & Deploy...")**: shows a `fit_dump.py
   diff`-style comparison of `editing_path` against the untouched
   staged file, plus a real `fit_crc()` check against the working
   file's current bytes -- the automated version of what the CLI docs
   already tell a user to do by hand before every deploy. Given step 7
   turned out to be a no-op, this is effectively where steps 7 and 8
   merged into one panel.
9. Deploy → verify the write → explicit eject prompt → power-button
   instruction → wait-for-remount -- **DONE (`gui_app.py` v0.13.0,
   `DeployPanel`)**: writes `editing_path` to `NewFiles/` via
   `write_to_newfiles()` (byte-for-byte write-back verification, same
   as the CLI), then a confirm-then-`diskutil eject` button (reusing
   `_volume_mount_point()` for the real ejectable target -- NOT
   `garmin_root` itself, confirmed via testing that only the volume
   root works) plus an "I Ejected It Myself" fallback for non-macOS/
   Finder-eject preference, then a manual "Check for Reconnected
   Device" button. Deliberately NOT the CLI's `wait_for_remount()`
   directly (blocks with `time.sleep()` for up to 180s) and
   deliberately NOT background-thread polling either -- user-confirmed
   design decision (2026-08-06): this app has never used a background
   thread, and introducing one here would trade a few extra clicks for
   a new class of failure mode (thread lifetime vs. panel teardown --
   the same species of bug already hit once with `EVT_SIZE` during
   teardown, see `LayoutDiagramPanel.on_size()`). Each "Check" click is
   one immediate, non-blocking `find_garmin_root()` call instead.
10. Automatic post-write verification — re-pull the profile and
    confirm the change actually landed, rather than leaving that as a
    manual afterthought -- **DONE (`gui_app.py` v0.14.0,
    `DeployPanel.on_check()`)**: the moment reconnect is confirmed,
    re-pulls the LIVE profile straight from the device's `Sports/`
    folder and runs it through the same `describe_screen_changes()`
    used in steps 7-8 (now factored out to module level so both panels
    share one implementation), comparing it against `editing_path`
    (what was actually sent). Runs automatically, not a separate
    manual step, since the device is already confirmed connected at
    that point. User-confirmed design decision (2026-08-06): compare
    visible/active screens only — no Removed-list bookkeeping in the
    result, matching the "Product note on `--un-remove`" reasoning
    below (Garmin's own editor has no un-remove option, neither does
    this GUI, so the device's known Removed-list wipe on NewFiles
    import isn't something to surface). This falls out of
    `describe_screen_changes()` for free — it only ever reports a slot
    that's ACTIVE (field 1 == 1) on at least one side, so a
    Removed-only or Unconfigured-only transition never produces a
    line, no special-casing needed (headless-verified: simulated the
    exact Removed→Unconfigured flip and confirmed zero diff lines,
    while a real field/position change on the same file pair still
    reports correctly).

### Restore from backup

Added to the flow after realizing edit-and-regret needs an easy way
back. Mechanically this needs **no new toolkit capability** — a
restore is identical to a normal deploy, just sourced from an old
backup file instead of a freshly patched one; `garmin_device.py`'s
existing `write_to_newfiles()` → eject → power-button → remount →
verify pipeline handles it as-is.

**DONE (`gui_app.py` v0.15.0, `RestorePanel`)**: "Restore from
Backup..." on `ProfileListPanel` (enabled the moment a profile is
selected — a sibling action to Stage, not buried in a menu) opens a
list of that profile's backup history, newest first, each row showing
a plain-English screen-type summary (e.g. "8 screen(s): Screen 1, Lap
Summary, Map, Elevation, ...") via `classify_screens()`/
`screen_type_name()` — no guessing "which one was before I broke it"
from a bare date string. Picking one and confirming hands off straight
to `DeployPanel` (steps 9-10), reusing it completely unchanged —
`frame.editing_path` just points at the chosen backup file directly
(never copied; `DeployPanel`/`describe_screen_changes()` only ever
read it). `PreflightPanel` (steps 7-8) is deliberately skipped for a
restore — there's no staged-vs-editing diff to show when the user
already picked a specific, known backup from a summarized list.
`DeployPanel`'s "Back" button is now context-aware
(`frame.deploy_return_panel`) so it returns to the right place either
way.

- Since every connect backs up *all* profiles (step 3), by the time
  someone wants to undo something there's usually already a stack of
  timestamped backups to choose from. **NEW:** `garmin_device.py`
  v0.11.0's `list_backup_history()` de-duplicates consecutive
  byte-identical backups (every visit to the profile list re-backs-up,
  not just real changes, so an untouched profile would otherwise
  accumulate many identical entries per session) — one entry per REAL
  change, nothing lost.
- The GUI needs to list a given profile's backups specifically (filter
  the timestamped backup folders down to that one filename), and
  should show more than a raw timestamp per entry — **DONE**, see
  above.
- **Before restoring, back up the current (about-to-be-overwritten)
  on-device state first**, exactly like any other write. This makes a
  restore itself always undoable — no dead end where someone restores
  to the wrong backup with no way back. **Satisfied by construction,
  no extra logic needed**: `ProfileListPanel.on_show()`/`on_refresh()`
  already re-backs-up unconditionally every time that panel is
  displayed, which happens right before a user ever reaches "Restore
  from Backup..." — so the pre-restore on-device state is always
  already the newest entry in the very history list being restored
  from.
- Backup retention is an open question, not an MVP blocker — see Open
  Items.

### Clone Profile

The last remaining item in the GUI feature backlog — `fit_clone_profile.py`
(CLI-validated on real hardware, see MVP_SCOPE.md "Clone-and-retarget")
was written early in this project but not yet wired to a GUI button.

**DONE (`gui_app.py` v0.16.0, `ClonePanel`)**: "Clone..." on
`ProfileListPanel` (enabled alongside Stage/Restore the moment a
profile is selected) opens a simple form — a new display name, with a
filename auto-suggested from it (editable, but never silently
overwritten once the user types into it directly). Clicking "Create
Clone" patches `sport_mesgs[0].name` (mesg_num=12, field 3, a fixed
32-byte null-padded string) via `patch_profile_name()` against the
source profile's just-taken backup — never the live device file, same
discipline as Stage/Restore — and hands off straight to `DeployPanel`
(steps 9-10), reusing it completely unchanged, exactly the way Restore
does. There's no staged-vs-editing diff to review for a clone either,
so `PreflightPanel` is skipped.

- **The one real risk with cloning: deploying under a filename that
  already matches an existing on-device profile silently overwrites
  it** instead of creating a new one — `fit_clone_profile.py`'s own
  docstring warns of this. Guarded by live validation against
  `frame.known_profiles` (a new frame-level dict, kept in sync by
  `ProfileListPanel.on_refresh()` on every visit) — "Create Clone"
  stays disabled until the chosen filename is confirmed to not collide
  with anything currently on the device, case-insensitively.
- Same state-leak risk as Restore (see the v0.15.1 bug entry above)
  applies here too, since Clone reaches `DeployPanel` the same way —
  proactively fixed from the start rather than waiting to reproduce it:
  `ClonePanel.on_back()` discards `frame.editing_path` when abandoned,
  same pattern as `RestorePanel.on_back()`.
- Headless-verified against a real backup file (`patch_profile_name()`
  can't be exercised through actual wx widgets in this sandbox):
  filename validation correctly rejects a missing/blank name, a
  filename with no `.fit` extension, a filename containing a path
  separator, and a case-insensitive collision with an existing
  profile; the produced clone is structurally identical to the source
  (`classify_screens()` reports the same screens/fields/order) with
  only the name field bytes different, and `describe_screen_changes()`
  reports zero differences — matching the already-confirmed real-
  hardware CLI result for `fit_clone_profile.py` itself. **CONFIRMED
  via real hardware (2026-08-11, reported after the fact by Doug,
  hadn't been logged here yet):** at least two clones deployed and
  working correctly through NewFiles under brand-new filenames not
  previously present on the device — `Clonebox` (from `Sandbox`) and
  `CloneRoad` (from `Road`). This also settles a previously-open
  question relevant beyond Clone itself: NewFiles correctly accepts a
  genuinely NEW filename, not just a replacement of an existing one —
  see "Restore a profile that's no longer on the device" under Open
  Items, which shares this exact mechanism and was flagged as carrying
  the identical unconfirmed risk as of the last revision of this
  document.

See [`MVP_SCOPE.md`](MVP_SCOPE.md) for the feature-level scope this
flow is built around, and [`MEMORY_LOG.md`](MEMORY_LOG.md) for the
complete, unabridged project history and findings.
