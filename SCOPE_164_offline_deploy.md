# Scope — #164, the deploy chain has no offline mode

*Scoping only, 2026-10-23, from Doug hitting it while cloning a profile
to move to the 530. Nothing built.*

---

## The defect

Offline, after cloning a profile, the final page offers **"Write to
Device (NewFiles)"** and nothing else. Pressing it refuses. There is no
way to get the cloned file out of the app.

`DeployPanel` contains **zero** references to `offline_mode`. It calls
`assert_mode()` three times — at the button, which is far too late to be
useful. `PreflightPanel` is the same: one `assert_mode()`, no mode
awareness. So the whole chain is device-shaped offline:

```
ViewScreensPanel  -->  PreflightPanel  -->  DeployPanel
 (mode-aware)          (assert only)        (assert only)
```

Export exists, and works, in `ProfileListPanel` — a panel this flow
never returns to.

## This is the third occurrence of one pattern

| release | guard added | path it missed |
|---|---|---|
| v0.20.0 | CIQ guard on six `EditScreenPanel` call sites | the Favorite pipeline, via `AddScreenPanel.on_create()` — fixed in v0.20.1 |
| v0.27.0 | offline dead end closed on the **restore** path | — |
| **now** | — | the **clone** path, same shape v0.27.0 fixed |

v0.27.0's own entry says it: *"The guard worked and fired far too late
to be of use."* That sentence describes today's bug exactly, one flow
over. Guarding the paths you are looking at and missing the one you are
not is this project's most repeated mistake, and a scope that does not
say so invites a fourth.

## The fix, and why it differs from v0.27.0's

v0.27.0 **hid** the restore controls offline, on the reasoning that
restoring is a device operation with no offline meaning — correct for
that case.

**Deploying a clone is not that case.** The file has to go somewhere;
the user has done real work and the result is sitting in `staging/`
with no way out. So the answer is not to hide the button but to
**change what it does**:

| | device mode | offline mode |
|---|---|---|
| final action | Write to Device (NewFiles) | **Export...** — save dialog |
| verification | read-back + CRC via Pre-Flight | `export_profile()`'s read-back byte-compare + CRC |
| after | eject / reconnect / verify | "saved, transfer it yourself" |

`export_profile()` already does the read-back and CRC check and is
already used by `ProfileListPanel`, so the offline write path is
**reused, not written**.

## Pieces

| piece | where | note |
|---|---|---|
| mode-aware labels + button | `DeployPanel` | the pattern `StartupTxtPanel` already uses — labels set before any early return |
| offline branch at the action | `DeployPanel` | save dialog → `export_profile()` |
| the four-stage machine | `DeployPanel` | eject / reconnect / re-read **do not apply offline** and must be hidden, not greyed — v0.23.0's posture for device-only controls |
| filename pre-fill | `DeployPanel` | the device matches by filename. A clone's staging name (`..._clone_<timestamp>.fit`) is **wrong** to offer — see below |
| Pre-Flight wording | `PreflightPanel` | it says what will happen "on the device". Offline, nothing happens on a device |

## The filename question, which is the one real design decision

Device-side, the toolkit deploys under the ORIGINAL profile filename,
because the device matches by filename and ignores anything else.

A clone has no original filename — that is the point of it. The staging
name is an internal artifact and must not be what the user is offered.
`ClonePanel` already collects a display name, and v0.23.0's export
dialog already pre-fills "the clean original filename", so the machinery
to ask is there. **What it should pre-fill for a clone is undecided and
should be Doug's call**, not guessed at here.

## What NOT to do

- **Do not hide the button offline.** That is v0.27.0's answer to a
  different question, and here it would leave the work unreachable.
- **Do not write a second export path.** `export_profile()` exists,
  verifies, and is proven.
- **Do not fix only `DeployPanel`.** `PreflightPanel` sits in the same
  chain with the same gap. Fixing one and not the other is precisely how
  this became a third occurrence.

## Audit, before building

The three occurrences above all came from fixing the instance rather
than the class. So before this is built, **every panel should be checked
for mode awareness**, not just the two in this chain:

| panel | `offline_mode` | `assert_mode` |
|---|---|---|
| DetectPanel | 1 | 0 |
| ProfileListPanel | 3 | 1 |
| ViewScreensPanel | 2 | 1 |
| StartupTxtPanel | 2 | 1 |
| **PreflightPanel** | **0** | 1 |
| **DeployPanel** | **0** | 3 |
| **RestorePanel** | **0** | **0** |
| **ClonePanel** | **0** | **0** |
| **ImportPanel** | **0** | **0** |
| EditScreenPanel / AddScreenPanel | 0 | 0 | pure file editing, no device contact — correctly none |

`RestorePanel`, `ClonePanel` and `ImportPanel` have **neither**. Two of
those are entry points into the broken chain. Whether each needs mode
awareness or is genuinely mode-neutral should be decided deliberately
and written down, so the next person does not have to re-derive it.

## Workaround until then

The clone is written to disk before any of this matters:

```
<working_dir>/staging/<original stem>_clone_<timestamp>.fit
```

A complete, valid profile. Copy it out and rename it.
