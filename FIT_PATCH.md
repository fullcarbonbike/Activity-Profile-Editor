```
FIT_PATCH(1)              Garmin Edge FIT Toolkit             FIT_PATCH(1)

Doc rev 16 -- refreshed 2026-08-11. Field 320 corrected: "Conditioning"
-> "Perf. Conditioning" -- full concept name is "Performance
Conditioning," but Doug confirmed the actual on-device DATA FIELD
display reads "Perf. Conditioning" (abbreviated), matching this
toolkit's naming convention (see NOTE on 320 below). fit_dump.py now
v2.4.9, still 117 entries (rename only). Prior rev (15, 2026-08-11)
follows.

Doc rev 15 -- refreshed 2026-08-11. Field 49 corrected: "Avg Speed
(Alt)" -> "Avg Speed" -- Doug deployed it into a full-width screen
slot and visually confirmed on-device it's plain text, no graph/bars.
No record exists of the original "(Alt)" naming's provenance; flagged
as a methodological caution for the Graph/Bars marker theory (see
NOTE on 49 below) rather than a falsification, since there's no
evidence this field's old label was ever a literal on-device marker
transcription like 23/348/349 were. fit_dump.py now v2.4.8, still 117
entries (rename only). Prior rev (14, 2026-08-11) follows.

Doc rev 14 -- refreshed 2026-08-11. Field ID reference now 117
confirmed entries (12 new this pass: 2, 15, 18, 32, 165, 347, 350,
433, 452, 478, 495, 497 -- see FIELD ID REFERENCE note below),
fit_dump.py v2.4.7. Also corrects 3 placeholder names built around the
"*"/"(Alt)" marker before its meaning was confirmed: 23 "Heart Rate
(Alt)" -> "HR Zone Graph", 348 "Speed *" -> "Speed Bars", 349
"Cadence *" -> "Cadence Bars". Prior rev (13, 2026-08-11) follows.

Doc rev 13 -- refreshed 2026-08-11. The long-open "*" marker mystery
(fields 348/349) is likely resolved -- Doug reported confirming it
marks a Graph/Bars-style rendering requiring a full-width screen slot,
falling back to plain text otherwise; same for the "(Alt)" suffix on
fields 23/49. Not yet independently re-verified by this project, noted
as the working explanation rather than certain. fit_dump.py now
v2.4.6, doc-only. See PROJECT_NOTES.md for a scoped (not yet built)
GUI feature this unlocks. Prior rev (12, 2026-08-11) follows.

Doc rev 12 -- refreshed 2026-08-11. Two field names corrected: 58 and
87 were transcribed as "Lap Timer"/"Last Lap Timer" (assumed by
analogy to the separate, correctly-named field 56 "Timer"), but a
closer on-device relabeling check found the real display text is "Lap
Time"/"Last Lap Time," no "r." No field IDs added or removed, still
105 confirmed entries. Prior rev (11, 2026-08-10) follows.

Doc rev 11 -- refreshed 2026-08-10. Field ID reference now 105
confirmed entries (18 new this pass -- see FIELD ID REFERENCE note
below), fit_dump.py v2.4.4. No fit_patch.py functional changes this
pass. Prior rev (10, 2026-08-05), documents fit_patch.py v1.12.0.
MAJOR REVERSAL: Add New Screen via NewFiles is now CONFIRMED WORKING.
The long-standing "always fails" limitation was root-caused as an f10
IDENTITY COLLISION, not a hard device/NewFiles restriction -- the old
--new-slot default silently wrote f10=0, which collides with almost
every real profile's existing "Screen 1" (also f10=0). A collision-
free f10 survives the NewFiles restart cycle intact, CONFIRMED via a
live on-device round-trip (2026-08-05, CyclingRoadSandbox), verified
independently by both fit_dump.py and garmin_device.py reading the
live mounted device afterward. New: next_available_field10() computes
a safe value automatically, replacing the old hardcoded 0 default; see
FIELD 10 / SCREEN TYPES and the revised --new-slot/--un-remove/BUGS
sections below. Prior rev (9, 2026-08-04): field 10 (f10) confirmed as
a real screen TYPE identifier (side-thread Test 4) --
would_hide_last_visible_screen() fixed to count only real user screens
via f10, correcting a confirmed undercounting bug. Also corrects the
Removed-state persistence claim: purged by the NEXT NewFiles-mediated
deploy, not indefinitely preserved. Field ID reference now 86
confirmed entries -- 84/87 (Last Lap Dist/Last Lap Timer) resolved,
closing the toolkit's last open field-ID mystery.
check_system_screen_guard() is now f10-based (certain identity) rather
than purely heuristic, fixing a real false positive reported from GUI
testing on a confirmed low-field-count user screen. NEW (rev 9):
hide_unsupported_screen_type() hard-blocks --hide on Map or ClimbPro
entirely -- confirmed via direct on-device inspection that neither has
a Show Screen toggle at all, on any profile type.

NAME
       fit_patch.py -- patch a data_screen slot in a Garmin Edge activity
       profile .FIT file

SYNOPSIS
       python3 fit_patch.py input_file output_file --slot N [OPTIONS]
       python3 fit_patch.py input_file output_file --swap-order SLOT,SLOT

DESCRIPTION
       fit_patch.py surgically edits data_screen messages (mesg_num=14,
       one instance per screen slot) inside an existing .FIT file. It
       does NOT re-encode the file -- it locates the target message's
       exact byte offsets, overwrites only the specific field bytes
       requested, recomputes the trailing file CRC, and leaves every
       other byte untouched.

       input_file and output_file may be the same path only if you
       intend to overwrite in place; it is safer to always write to a
       new filename and copy it to the device separately.

OPTIONS
       --slot N
              message_index of the screen slot to patch (0-30).
              Required for all operations except --swap-order.

       --fields ID,ID,...
              Comma-separated field IDs, in display order, up to 10.
              Also sets the field count automatically. See FIELD ID
              REFERENCE below. Omit to leave the slot's current
              fields/count untouched. Mutually exclusive with
              --swap-fields. VALIDATED in both directions on real
              hardware: same-count content replacement, and a genuine
              field-count increase (existing fields preserved, new
              ones appended, layout recalculated correctly).

              Before writing, this checks the slot's CURRENT content
              against KNOWN_SYSTEM_CONTENT_PATTERNS (see --force,
              below) and refuses to proceed if it matches, unless
              --force is given.

       --force
              Proceed with --fields even if check_system_screen_guard()
              (v1.10.0, importable directly -- see RELATED TOOLS)
              identifies the target slot as a named Garmin screen type.

              v1.10.0 CORRECTION: this check is now f10-based, not
              heuristic-based, for any slot with a real f10 (i.e.
              every Active screen). Field 10 is CONFIRMED as a real,
              content-independent screen TYPE identifier (see FIELD 10
              / SCREEN TYPES below) -- the guard checks it FIRST:

              - If f10 identifies a NAMED Garmin type (Map, Elevation,
              Cycling Dynamics, etc.): blocks with a CERTAIN message
              naming the type directly, not a guess. --force overrides.

              - If f10 identifies a plain, user-created "Screen N":
              proceeds with NO warning at all. This is confirmed
              identity, not a guess -- there is nothing to second-guess
              here. Fixes a real reported false positive: a confirmed
              1-field user screen previously still triggered a "might
              be a system screen" pause under the old logic.

              Only when f10 itself is unavailable (a Removed-state
              slot, which has no real f10 by definition) does this
              fall back to the ORIGINAL two content/count heuristics --
              genuinely a guess in that one remaining case:

              (1) a content pattern that has recurred, across
              MULTIPLE different profiles, on likely system/overlay
              screens: an empty slot, Percent Grade + Elevation, or
              Power Phase Left + Right; or

              (2) a low field count -- 2 fields or fewer.

              Neither fallback heuristic is a certain identification
              (an earlier hardcoded slot-number version of this idea
              was proven wrong on a real profile and removed entirely,
              see PROJECT_NOTES.md / CORRECTIONS) -- but for any Active
              screen (the normal case), f10 answers this with certainty
              and neither fallback is even consulted.

       --swap-fields POS,POS
              Swap two field POSITIONS (0-based) within the slot's
              EXISTING field array, leaving field count and every
              other slot untouched. Reads the current array from the
              input file, swaps exactly those two entries, writes
              back only field 7. Useful for a minimal, single-
              variable content-change test.

       --layout 0|1
              Layout variant: 0=A/default, 1=B/alternate. Only valid
              when the EFFECTIVE field count (whatever --fields sets
              this call, or the slot's existing count if --fields is
              omitted) is one of 3, 4, 5, 6, 7 -- see LAYOUT VARIANTS.
              Requesting 1 outside those counts is a hard error, not
              a silent fallback to A.

              If omitted on an already-configured slot, field 8 is
              left untouched. If omitted AND --new-slot is given,
              field 8 is automatically set to 0/A.

       --enable / --show
       --disable / --hide
              Mutually exclusive (all four flags share one group).
              Sets field 12 (0=enabled/shown, 1=disabled/hidden),
              matching the on-device "Show Screen" toggle exactly --
              --show/--hide use that same on-device wording.

              --disable/--hide is blocked outright (parser.error, NO
              --force override) if the target slot is currently the
              ONLY visible, plain USER-CREATED screen left on the
              profile -- see would_hide_last_visible_screen() (v1.9.0).
              This is a HARD guard, not a heuristic: CONFIRMED via real
              on-device testing that Garmin's own editor refuses to
              hide or remove a profile's last remaining user screen, so
              unlike the --force-overridable checks above, there is
              nothing to second-guess here -- it's a directly
              computable fact, not a pattern match.

              v1.9.0 CORRECTION: earlier versions counted every
              currently-shown Active screen toward this guard,
              regardless of type. That undercounted the real
              constraint -- confirmed on a real profile where the
              device grayed out Hide/Remove on the profile's ONE user
              screen despite 7 OTHER visible Garmin-authored screens
              (Map, Elevation, Cycling Dynamics, etc.) still being
              shown. Field 10 (f10) is now confirmed as a genuine,
              content-independent screen TYPE identifier (see FIELD
              10 / SCREEN TYPES below) -- the guard now counts only
              screens whose f10 is NOT one of the known Garmin type
              codes, and only APPLIES when the slot being hidden is
              itself one of those plain user screens (hiding a named
              Garmin type is governed by a different, per-type rule
              entirely, not this constraint).

              v1.11.0 ADDITION: --disable/--hide is ALSO blocked
              outright (parser.error, NO --force override) if the
              target slot's f10 identifies it as Map or ClimbPro --
              see hide_unsupported_screen_type(). CONFIRMED via direct
              on-device inspection that NEITHER has a Show Screen
              toggle anywhere in the Data Screens editor, on ANY
              profile type (the Indoor profile's Map "Always"/"While
              Navigating" control is a different mechanism entirely,
              not this toggle -- see PROJECT_NOTES.md). This is a
              second, independent HARD guard checked BEFORE the
              last-visible-user-screen check above -- either one alone
              is sufficient to block the write.

       --new-slot
              Use when activating a previously-unconfigured slot.
              Sets field 1 (configured flag). Also auto-defaults
              field 12 to 0/enabled and field 8 to 0/A if not set
              explicitly -- every real device-created screen has
              both of these set, so a genuinely fresh slot never gets
              left with an untested sentinel value in either field.
              As of v1.12.0, also auto-assigns f9 (via
              next_available_field9()) and f10 (via
              next_available_field10()) unless overridden with
              --field9/--field10 -- see below.

              *** STATUS (v1.12.0): CONFIRMED WORKING ***
              Activating a brand-new screen (via --new-slot) and
              pushing it via NewFiles is now CONFIRMED to survive a
              live on-device round-trip, INCLUDING on a profile
              already touched by NewFiles before -- verified
              2026-08-05 on CyclingRoadSandbox, independently
              double-checked by both fit_dump.py and garmin_device.py
              reading the live mounted device after the restart. The
              prior "always fails" behavior is root-caused: the OLD
              default silently wrote f10=0, which collides with the
              f10 the profile's existing "Screen 1" already holds --
              the device's NewFiles reconciliation merges/discards on
              an f10 collision. A collision-free f10 (now the
              default) survives intact. This does NOT mean --new-slot
              is risk-free -- verify with fit_dump.py screens and
              fit_crc.py before every deploy, same as any other
              change, and note the profile's ENTIRE Removed-screen
              list is purged by any NewFiles deploy regardless of
              what it targets (see SCREEN STATE MODEL). --un-remove's
              own live-round-trip status is unchanged -- see below.

       --seed-from-slot N
              Copy fields 9 and 10 from an already-configured slot N
              in the SAME input file, verbatim (including duplicating
              slot N's own f9 value). Useful for deliberate testing,
              not for normal use -- an intentional f10 duplicate,
              which is exactly the collision the v1.12.0 auto-default
              now avoids.

       --field9 N
       --field10 N
              Explicit overrides for fields 9/10. Priority: explicit
              override > --seed-from-slot > --new-slot auto-default
              (next_available_field9()/next_available_field10() as of
              v1.12.0 -- previously f10 defaulted to a hardcoded 0,
              see STATUS above).

       --swap-order SLOT,SLOT
              Swap the DISPLAY ORDER of two already-configured
              screens by swapping their field 9 (creation-order
              stamp) values. Ascending f9 == on-device display order
              (CONFIRMED via a real device round-trip producing the
              exact predicted on-screen swap). Does NOT touch field
              count, content, or total screen count. Both slots must
              already have a real (non-sentinel) f9 -- refuses
              Conditional/Removed-state slots automatically, since
              they have no f9 to swap. Ignores --slot; this is a
              separate operation from everything else in this list.

       --un-remove
              Restore a screen from the Removed state back to Active.
              Requires --slot pointing at a slot CONFIRMED to be
              Removed (f1=0, f9/f10 absent, content preserved) --
              refuses otherwise. Does NOT touch f3/f7. As of v1.12.0
              its f9/f10 auto-defaults use the same collision-free
              logic as --new-slot (see above).

              *** WARNING: an EARLIER version of this tool (pre-
              v1.12.0) was CONFIRMED via live device round-trip to
              cause silent data loss on an UNRELATED, untouched
              screen -- root-caused to the old hardcoded f10=0
              default colliding with an existing screen's identity
              (see --new-slot STATUS above). The fix removes that
              specific collision, but --un-remove itself has NOT yet
              been re-tested live since the fix -- only --new-slot
              has (2026-08-05, CyclingRoadSandbox). Treat --un-remove
              as unverified-but-plausibly-fixed, not confirmed. Back
              up first regardless -- not just recommended, required.

              PRODUCT NOTE (2026-08-05): Garmin's own on-device editor
              has no un-remove option at all -- Hide (temporary) and
              Remove + Add New (permanent) are the only workflows it
              exposes. A factory-shipped profile's Removed list
              already contains a few entries the user never created
              (confirmed on a brand-new template, zero edits), which
              suggests Garmin itself may not treat Removed vs.
              Unconfigured as a meaningfully distinct, user-facing
              state the way this toolkit has had to. Current thinking
              is to keep this flag available for deliberate testing
              but likely NOT expose it as a first-class GUI feature --
              final call deferred, not yet made. ***

RELATED TOOLS
       fit_chain.py chains multiple fit_patch.py operations (each a
       full CLI argument string) into one file before a single device
       write, so a multi-change edit costs one restart instead of one
       per change. It shells out to this program per step rather than
       reimplementing any of its logic, and CRC-verifies after every
       step. See fit_chain.py --help.

       gui_app.py's EditScreenPanel imports patch_screen(),
       read_current_field_array(), read_current_count_and_layout(),
       the pack_*() helpers, check_system_screen_guard(),
       would_hide_last_visible_screen(), (v1.11.0)
       hide_unsupported_screen_type(), and (v1.12.0)
       next_available_field9()/next_available_field10(), plus
       COUNTS_WITH_B_VARIANT, directly from this module (no
       subprocess) -- every field/layout/visibility change made in the
       GUI is a real call to the same functions this CLI uses, applied
       to a scratch working copy of the staged file, and the GUI's
       Show/Hide checkbox is blocked by the same two independent hard
       guards (last-visible-user-screen, and
       Map/ClimbPro-can't-hide-at-all) the CLI enforces, checked in
       the same order. As of gui_app.py v0.6.3, the GUI's screen list
       also DISPLAYS the real f10 type names via fit_dump.py's
       screen_type_name(). As of gui_app.py v0.7.0, ViewScreensPanel
       also imports swap_display_order() directly -- Move Up/Move Down
       on the main screens list is the exact same function
       --swap-order uses, applied to whichever two rows are adjacent
       to the current selection. As of gui_app.py v0.8.0, the new
       AddScreenPanel imports pack_configured_flag(), pack_uint8(),
       next_available_field9(), and next_available_field10() directly
       -- it replicates --new-slot's exact defaulting logic via these
       same functions rather than reimplementing it, so the two paths
       (CLI and GUI) can't drift apart.

FIELD 10 / SCREEN TYPES (CONFIRMED, side-thread Test 4, 2026-08-04)
       Field 10 (f10) is a real screen TYPE identifier, independent of
       f9 (display order) and of the screen's current field content.
       Two categories:

       (1) Named Garmin screen types get a FIXED numeric code, the
           same regardless of profile/template or what content the
           user has since customized the screen to show (proven:
           patched Cycling Dynamics' fields via --force and
           redeployed -- f10 stayed 63; the tag marks TYPE, not
           displayed content). The 10 confirmed so far (see
           fit_dump.py's NAMED_SCREEN_TYPES):

               f10   Screen type
               ---   ---------------------------------------------
                25   Map
                26   Virtual Partner
                32   GroupTrack (the real Conditional runtime record)
                35   Compass
                44   Elevation
                56   Segment
                57   GroupTrack List (always-orderable Active
                     placeholder, structurally independent of f10=32)
                63   Cycling Dynamics
                74   Lap Summary
               104   ClimbPro

       (2) Plain user-created screens use a per-profile, zero-indexed
           counter; the on-device editor displays f10=N as "Screen
           N+1" (confirmed exactly across 6 independent instances on
           one profile, no exceptions).

       Named types are actively RE-APPLIED, not just inherited from
       original template creation: removing GroupTrack List on-device
       and re-adding it from the device's own named-screen menu
       brought it back tagged f10=57 again, not the next free counter
       value. This is what makes would_hide_last_visible_screen()'s
       v1.9.0 fix possible -- "how many real user screens are left" is
       now directly answerable from the file via f10, not a guess.

       fit_dump.py's screen_type_name(f10) renders either form; import
       it (or NAMED_SCREEN_TYPES directly) rather than re-deriving this
       table elsewhere.

FIELD ID REFERENCE (117 confirmed)
       ID     Name                       ID     Name
       ---    -----------------------    ---    -----------------------
         0    Calories                    94    ETA to Next
         2    Course Pt Dist.             95    Odometer
         3    Cadence                     96    Battery Level
         4    Avg Cadence                 97    GPS Signal Strength
         5    Lap Cadence                 99    Aerobic Training Effect
         6    Distance                   146    10s Power
         7    Lap Dist.                  165    Last Lap HR
         9    Elevation (ft)             178    Gears
        11    Percent Grade              179    Front Gear
        12    Heading                    180    Rear Gear
        13    Heart Rate                 181    Gear Battery
        14    Avg Heart Rate             182    Gear Ratio
        15    Lap HR                     199    HR Zone 1 (time)
        16    %Max Heart Rate            200    HR Zone 2 (time)
        17    Avg %Max Heart Rate        201    HR Zone 3 (time)
        18    Lap %Max HR                202    HR Zone 4 (time)
        19    %Heart Rate Reserve        203    HR Zone 5 (time)
        20    Avg %HRR                   216    WindField Widget
        22    Heart Rate Zone            257    Time Standing
        23    HR Zone Graph              259    Time Seated
        27    Distance to Destination    263    Platform Center Offset
        28    Time to Destination        266    Power Phase Right
        29    Distance to Next           270    Avg R. Peak Pwr Phase
        30    Time to Next               272    Power Phase Left
        31    Dest. Location             276    Avg L. Peak Pwr Phase
        32    Next Pt Location           295    Target Power
        36    Power                      316    Lights Connected
        37    Avg Power                  317    Light Battery
        38    Kilojoules                 318    Beam Angle Status
        39    Lap Power                  319    Light Mode
        48    Speed                      320    Perf. Conditioning
        49    Avg Speed                  343    Heart Rate Graph
        50    Lap Speed                  344    Speed Graph
        53    Sunrise                    345    Cadence Graph
        54    Sunset                     346    Power Graph
        55    Elapsed Time               347    HR Bars
        56    Timer                      348    Speed Bars (see note)
        57    Avg Lap Time               349    Cadence Bars (see note)
        58    Lap Time                   350    Power Bars
        59    Time of Day (TOD)          368    Elevation Graph
        60    Total Ascent               409    Gear Combo
        61    Total Descent              433    Anaerobic TE
        62    Dest. Ahead                442    Lap VAM
        63    Time Ahead                 443    Avg VAM
        64    Calories to Go             444    Ascent Remaining
        65    Distance to Go             445    Asc to Next Crs Pt
        66    Heart Rate to Go           452    Respiration
        67    Reps to Go                 478    EPOC
        68    Time to Go                 486    Grit
        77    VAM                        487    Lap Grit
        78    Temperature                488    Flow
        79    3s Power                   489    Lap Flow
        81    Normalized Power           491    Assist Mode
        84    Last Lap Dist              492    Shifting Advice
        86    Last Lap Speed             493    eBike Battery
        87    Last Lap Time              494    Travel Range
        88    30s VAM                    495    60s Grit
        91    Max Speed                  497    60s Flow
        93    ETA at Destination

       NOTE: 2026-08-10 batch (18 new: 7, 30, 31, 39, 50, 57, 61, 62,
       63, 67, 86, 88, 94, 95, 295, 442, 443, 445) -- confirmed by
       arranging two screens to 10 fields each on a real profile
       specifically for this census, entering/selecting each field by
       its on-device name, then cross-referencing every field's raw ID
       against its known on-screen position via the GUI. Same direct
       verification standard as every other entry in this table, no
       collisions with any prior entry.

       NOTE: 5/77/91/489 confirmed via a separate field-ID exploration
       thread, visually verified via isolated single-field test screens
       on a sandbox profile -- same verification standard as every
       other entry in this table.

       NOTE: 84/87 (Last Lap Dist / Last Lap Time) confirmed 2026-08-04
       via the same exploration thread -- a forced-field test screen
       deployed successfully through NewFiles. Previously assumed
       GroupTrack-specific purely by association (both IDs happened to
       appear on the f10=32 Conditional record) -- they aren't
       GroupTrack-related at all, just two ordinary lap-stat fields.
       This closes the toolkit's last open field-ID mystery;
       KNOWN_UNRESOLVED_IDS is now empty. CORRECTED 2026-08-11: field
       87 was originally transcribed as "Last Lap Timer" -- a closer
       on-device relabeling check found the real display text is
       "Last Lap Time," no "r" (same mixup as field 58 below).

       NOTE on 348/349 (now "Speed Bars"/"Cadence Bars", formerly
       "Speed *"/"Cadence *"): confirmed genuinely distinct from 48/3
       via an on-device UI marker (a "*" shown only in the field
       picker, never while actually riding). MEANING RESOLVED
       2026-08-11 (Doug verified directly): the "*" marks a Bars-type
       rendering; real on-device names confirmed and corrected above.
       Same marker family as field 23 (Graph-type, also corrected --
       see below) and the standalone Bars entries 347/350. All need a
       full-width screen slot to actually draw as a bar/graph --
       placed in a shared/split row instead, silently falls back to
       plain text. Not yet independently re-verified across multiple
       placements by this project. See PROJECT_NOTES.md "Graph/Bars
       full-width warning" for a scoped (not yet built) GUI feature to
       surface this.

       NOTE: 2026-08-11 batch (12 new: 2, 15, 18, 32, 165, 347, 350,
       433, 452, 478, 495, 497) -- Doug's continued field census in a
       separate session, same direct on-device verification standard
       as every other entry. Also corrects 3 placeholder names built
       around the "*"/"(Alt)" marker before its meaning was confirmed:
       23 "Heart Rate (Alt)" -> "HR Zone Graph" (a distinct Graph-type
       field, not an alternate view of plain Heart Rate), 348/349 (see
       note above). No collisions with any prior entry.

       NOTE on 49 (now "Avg Speed", formerly "Avg Speed (Alt)"),
       corrected same day (2026-08-11): no record exists of how/why
       this field was originally named "(Alt)" -- predates this
       project's later discipline of noting confirmation method per
       field, the same blind spot that produced field 58's earlier
       wrong "Lap Timer" guess. Doug deployed it into a full-width
       screen slot via the GUI and visually confirmed on-device: it's
       a plain text "Avg Speed" value, no graph or bars. CAUTION for
       the Graph/Bars marker theory (348/349's note above): unlike
       23/348/349, there's no record this field's old "(Alt)" label
       was ever a literal transcription of a real on-device UI marker
       -- treat this as a caution, not a falsification of the theory.
       An OLD placeholder name merely containing the word "(Alt)"
       isn't itself evidence of a real on-device marker unless that
       was actually recorded at confirmation time.

       NOTE on 320 (now "Perf. Conditioning", formerly
       "Conditioning"), corrected 2026-08-11: the full concept name is
       "Performance Conditioning," but Doug confirmed the actual
       on-device DATA FIELD display reads "Perf. Conditioning"
       (abbreviated). Renamed to match this toolkit's established
       convention of naming fields as they display on-device rather
       than by their full/conceptual name -- same convention behind
       "Lap Dist." and "Dest. Location."

       NOTE on the 343-346/368 graph cluster: confirmed via two
       independent screens plus on-ride photo verification. First-
       pass mapping assumed raw array position matched on-screen
       display position -- this was WRONG for 344/346 and had to be
       corrected. Don't assume array order = display order for
       future census entries, especially on B-variant layouts.

       NOTE on 58 (Lap Time): confirmed 2026-08-06, surfaced
       incidentally by real GUI testing rather than an active field-ID
       hunt -- a restored 8/3/2026 CyclingRoadSandbox backup contained
       a field the GUI's picker didn't recognize; confirmed via direct
       visual comparison against the live device display. CORRECTED
       2026-08-11: originally transcribed as "Lap Timer" (assumed by
       analogy to the separate, correctly-named field 56 "Timer"), but
       a closer on-device relabeling check found the real display text
       is "Lap Time," no "r." Field 56 "Timer" is unaffected.

LAYOUT VARIANTS
       Field 8 selects the grid arrangement for a given field count.
       Confirmed 0=A / 1=B via an isolated on-device edit (6-field
       screen, #6-A -> #6-B), and independently re-confirmed via a
       full device round-trip using this tool's own --layout flag.

       Per the developer's own on-device reference, only these field
       counts have a real A/B choice:
              3, 4, 5, 6, 7 fields  -- A/B variants exist
              1, 2, 8, 9, 10 fields -- single layout only

       This tool ENFORCES that table -- requesting --layout 1 outside
       {3,4,5,6,7} is a hard error, checked against the EFFECTIVE
       field count (including a stale value left over from a prior
       edit that didn't touch --layout this time).

SCREEN STATE MODEL
       Every data_screen slot is in one of three states, determined
       by fields 1/9/10:

       Active/Display    f1=1  f9=real,unique  f10=real
                          Normal, participates in on-device order.

       Conditional        f1=1  f9=absent       f10=REAL (seen: 32)
                          e.g. GroupTrack. An active feature exempt
                          from the normal f9 ordering system.

       Removed            f1=0  f9=absent       f10=absent
                          Content (fields 3/7) preserved AT THE MOMENT
                          OF REMOVAL -- a soft delete, confirmed via
                          the on-device "Remove" button. No on-device
                          "un-remove."

                          CORRECTION (2026-08-04): NOT persistent
                          indefinitely as earlier documented here. A
                          NewFiles-mediated (toolkit) deploy purges
                          whatever is currently in the Removed state,
                          EVERY TIME -- confirmed via two independent
                          test deploys, each wiping a DIFFERENT
                          Removed screen the deploy itself never
                          touched. Specific to the NewFiles pathway --
                          on-device-only editing does NOT purge Removed
                          screens; they continue to show up normally in
                          `screens` output until the next toolkit
                          deploy of ANY kind (a field edit, a
                          Show/Hide, a reorder -- unrelated to the
                          Removed screen itself). See PROJECT_NOTES.md
                          Screen State Model for the full writeup.

VERIFY BEFORE WRITING TO DEVICE
           python3 fit_crc.py out.fit
           python3 fit_dump.py screens out.fit

EXAMPLES
       Add a field-content change to an EXISTING screen, layout B:
           python3 fit_patch.py in.fit out.fit --slot 4 \
               --fields 178,179,180,181 --layout 1

       Force an edit past the system-content guard (verify on-device
       first!):
           python3 fit_patch.py in.fit out.fit --slot 3 \
               --fields 13,3 --force

       Swap two screens' on-device display positions:
           python3 fit_patch.py in.fit out.fit --swap-order 4,5

       Hide a screen without touching its fields:
           python3 fit_patch.py in.fit out.fit --slot 1 --hide

FILES
       fit_raw_walk.py      generic FIT def/data message byte-offset walker
       fit_crc.py            FIT CRC-16, self-verifying against known-good files
       fit_dump.py            SDK-based dump/unknown/diff/screens tool
       fit_patch.py           this program
       fit_chain.py           chains multiple fit_patch.py calls before one write
       fit_clone_profile.py   clones a profile under a new display name
       garmin_device.py       device detection/backup/write/eject workflow

BUGS
       RESOLVED (v1.12.0, 2026-08-05): adding a brand-new screen via
       --new-slot through NewFiles was PREVIOUSLY believed CONFIRMED
       BROKEN for any profile already touched by NewFiles -- the
       screen with the next-highest f9 appeared to get silently
       overwritten, and the new screen itself ended up wiped. That
       diagnosis was made before f10's meaning was understood. Root
       cause, now confirmed: the failing tests all left --new-slot's
       f10 at its old hardcoded default of 0, which collides with the
       f10 almost every real profile's existing "Screen 1" already
       holds -- NOT a NewFiles delivery-mechanism issue as previously
       believed. A collision-free f10 (now the auto-default via
       next_available_field10()) survives a live NewFiles round-trip
       intact, verified 2026-08-05 on CyclingRoadSandbox and
       independently double-checked against the live mounted device
       by both fit_dump.py and garmin_device.py. --un-remove uses the
       same corrected default but has not itself been re-tested live
       yet -- see its OPTIONS entry above. See PROJECT_NOTES.md for
       the full investigation and the original (now superseded)
       failure writeup.

       f10 has no confirmed pattern among NAMED Garmin screen types
       (field count does NOT reliably predict which named type a
       screen is) -- but among PLAIN USER screens it's a confirmed,
       simple 0-indexed counter (see FIELD 10 / SCREEN TYPES above).
       f11 has weak evidence (2 data points) of distinguishing user-
       added vs. template-origin screens; not used by this tool.

       The --force system-content guard is now f10-based (v1.10.0) and
       CERTAIN, not a guess, for any slot with a real f10 (every Active
       screen) -- it only falls back to the original content-pattern
       heuristic for a Removed-state slot, which has no real f10 to
       read. Still worth verifying on-device before overriding a named
       Garmin type with --force, since the guard being certain about
       WHAT a screen is doesn't guarantee a content overwrite there is
       consequence-free.

                                                          FIT_PATCH(1)
```
