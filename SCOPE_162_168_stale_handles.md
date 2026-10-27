# Scope — #162 + #168, handles that go stale across a deploy

*Scoping only, 2026-10-27. Nothing built. The hardware evidence is Doc
revs 182–185.*

---

## One problem, two symptoms

Both items are the same mistake in different places: **the toolkit
remembers an identifier, the device changes it during import, and the
toolkit keeps using the remembered one.**

| | remembered | the device changes it to |
|---|---|---|
| **#168** | the filename you deployed under | its own generated `Cycling<Sport><Name>.fit` |
| **#162** | a screen's `message_index` | a different slot, content preserved |

Scoping them together because a fix that re-reads the device after
reconnect addresses both, and two separate fixes would each re-read the
same directory.

## What the device actually does — established, with the evidence

| behaviour | rev | strength |
|---|---|---|
| renames an imported profile from its sport + display name | 182 | observed once |
| accepts a non-matching filename — new profile **and** replacement | 182, 184 | observed |
| renumbers `message_index`, content preserved | 171, 184 | observed on 2 files |
| …but left a canonically-named file **byte-identical** | 179 | observed once |
| **f10 survived every import unchanged** | 171–185 | 4 imports, no exceptions |
| the toolkit itself renumbers nothing — edit, export and clone all preserve slots | 185 | full chain |

**f10 is the stable identity.** That is the one thing every observation
agrees on, and it is what any fix should key on.

**What is NOT established:** whether the renumbering is triggered by the
filename differing, by the profile being new, or by something else.
Those are confounded (rev 184). *The fix must not depend on knowing.*

## The audit — every remembered identifier that crosses a deploy

Grepped rather than recalled:

| holder | what it stores | survives a deploy? | risk |
|---|---|---|---|
| `frame.profile_filename` | the deployed filename | **yes, and goes stale on rename** | **#168 — real** |
| `frame.editing_slot` | `message_index` of the open screen | yes, never cleared | latent |
| `DeployPanel.on_check()` | builds `Sports/<profile_filename>` | — | **the actual #168 failure** |
| Favorite store | **field ids only**, no slot | n/a | **safe** |
| Lineage sidecar | `profile_filename`, `source_backup`, `staged_at` | yes | **needs checking** |
| Backups | taken from `Sports/` after reconnect | n/a | **safe** — they carry the post-rename name |
| `fit_patch` CLI `--slot` | user-supplied per invocation | n/a | safe, but see below |

Three things fall out of that table:

1. **`DeployPanel.on_check()` is the only confirmed user-visible
   failure.** It reports "couldn't verify" after a clone deploy.
2. **The lineage sidecar is unchecked.** It records the filename at
   stage time; after a rename that name no longer exists on the device.
   Whether anything reads it back and cares is the first thing to look
   at, and it may be nothing.
3. **`frame.editing_slot` is never cleared**, including by
   `discard_edits()`. Today it is always overwritten before use, so this
   is hygiene rather than a bug — but it is exactly the shape that
   becomes a bug when someone adds a new path.

## The fix

**Ask the device, do not model it.** After reconnect, re-resolve the
profile by reading `Sports/` rather than trusting what was remembered.

```
on_check():
    candidates = list_profiles(Sports/)
    match the one whose profile NAME equals what we deployed
    verify against that file
```

Matching on the **display name inside the file** rather than on the
filename, because the name is what the device preserves and the
filename is what it rewrites.

The alternative — predict the device's generated name — is rejected:
it requires a sport-to-prefix table, it bakes in a rule observed once,
and it breaks silently the first time Garmin changes the convention.

**And `describe_screen_changes()` must compare by f10, not by slot.**

**CHECKED, 2026-10-27**, rather than left as an assertion. It pairs by
`message_index`, and its own docstring says so while asserting the
thing that is now false:

> *"Compares by message_index (slot), the same **stable** per-screen
> identity used throughout the rest of the GUI."*

That was true of every path the toolkit controls — rev 185 confirmed
edit, export and clone all preserve slots exactly. It is not true
across a device import.

### ⚠ And the two bugs currently mask each other

This is the reason to fix them together, and it is sharper than "they
are related":

| deploy | filename | `on_check()` today |
|---|---|---|
| under the device's own name | matches | file found, **no renumbering observed**, pairing works |
| under any other name | differs | **file not found** — fails before pairing ever runs |

So the f10-pairing bug is **currently unreachable**: the only case that
renumbers is the case where `on_check()` cannot find the file at all.

**Fixing #168 alone would expose it.** Resolve the renamed profile
correctly and the verification will, for the first time, successfully
open a file whose slots have moved — and then pair unrelated screens
and describe changes that did not happen. A verification that reports
confident nonsense is worse than one that says it could not run.

**So #168 must not ship without the f10 pairing.**

## What NOT to do

- **Do not key on the filename.** That is the thing the device rewrites.
- **Do not try to determine why the device sometimes renumbers.** The
  fix should hold either way; the cause is a separate curiosity.
- **Do not reuse `message_index` as a cross-session identifier
  anywhere**, including in anything new. f10 is the identity.
- **Do not touch the export dialog's filename warning here.** Its
  wording is wrong (rev 183) and that is its own job.

## The one experiment still worth running

Change a field in the current `CyclingRoadROAD_22.fit` and import it
**under that exact canonical name**. Unchanged slots means the filename
is the trigger; renumbered means it is something else.

**Not a blocker.** The fix works either way — this is for the model, not
the code.

## Rough size

| piece | where | note |
|---|---|---|
| resolve the live profile by display name | `garmin_device.py` or `fit_dump.py` | new, small; needs `is_profile_file()` and a name reader, both of which exist |
| `on_check()` uses it | `gui_app.py` | the #168 fix |
| pair by f10 | `describe_screen_changes()` | confirmed slot-paired; **must ship with #168, not after** |
| clear `editing_slot` in `discard_edits()` | `gui_app.py` | hygiene, one line |
| lineage sidecar | `garmin_device.py` | check before changing — may be a no-op |

## Testing

Device-mode only, so it needs the 530 or the 840:

1. **Clone + deploy, then Check** — must verify cleanly instead of
   reporting failure. This is the whole of #168.
2. **Edit an existing profile, deploy under its own name, Check** — the
   case that works today; must still work.
3. **Deploy a profile the device renumbers, then Check** — must report
   the real differences, not a screen-by-screen false alarm.

Case 3 is the one that only exists because of rev 184, and the only one
that tests the f10 pairing.
