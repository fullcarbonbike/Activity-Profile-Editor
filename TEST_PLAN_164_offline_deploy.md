# Test plan — #164, offline deploy (`gui_app.py` 0.30.0)

*Nothing headless can drive wx, so all of this is by hand.*

## What actually changed, so you know where to look

- `DeployPanel` gained an offline mode — **Export** instead of Write.
- `ProfileListPanel.on_export()` was **extracted** to a shared
  `export_working_copy()`. Both panels call it. **So the connected path
  and the existing offline Export both run changed code**, even though
  neither was supposed to change behaviour.
- `PreflightPanel`'s deploy-time `assert_mode` was **deleted**.

That middle point is why **section A matters as much as B**. The bug was
offline, but the refactor touched the path you use every day.

---

## A. Connected path — the regression side

Device plugged in, normal edit → Pre-Flight → Deploy.

| # | check | expect |
|---|---|---|
| A1 | panel heading | **"Deploy to Device"** |
| A2 | main button | **"Write to Device (NewFiles) →"** |
| A3 | eject / check buttons | **visible** |
| A4 | the four stages | ready → written → waiting → reconnected, exactly as before |
| A5 | post-write verification box | fills on reconnect as it always did |
| A6 | Pre-Flight heading above the diff | "What will change on the device:" |

**A4 is the one that matters.** If anything about the eject/reconnect
machine behaves differently, that is my fault and not a device quirk.

## B. Offline edit flow — ⚠ REWRITTEN 2026-10-25, the original was wrong

**What section B first said:** offline, edit a screen → Pre-Flight →
Deploy, and check the Deploy page shows Export.

**That path does not exist**, and Doug walked into the discrepancy
rather than the bug. Offline, `ViewScreensPanel`'s button becomes
**"Export Profile..."** and dispatches **straight to the save dialog** —
by design since #141. `show_panel("review")` has exactly one caller and
it is the device-mode branch, so **Pre-Flight and Deploy are unreachable
offline by this route.**

So #164 never affected the ordinary offline edit flow. It affects the
two flows that navigate DIRECTLY to `DeployPanel` — **clone** and
restore — which is section C.

**What Doug saw is a PASS, and a useful one.** That flow now runs the
extracted `export_working_copy()`, so walking it exercises the
refactor:

| # | check | expect | 2026-10-25 |
|---|---|---|---|
| B1 | the button on the screens view | "Export Profile..." | **pass** |
| B2 | pressing it | save dialog straight away, no intervening page | **pass** |
| B3 | after saving | "Verified twice" message naming the CRC | **pass** |
| B4 | where you land | back on the screens view, button still live | **pass** |
| B5 | no Deploy page appears at all | correct — it is not on this path | **pass** |

B4 is right rather than a leftover: you may want to export again, to a
second location or under another name.

## C. The reported bug — clone, offline

The original report. Offline, clone a profile, and at the final page:

| # | expect |
|---|---|
| C1 | **Export...**, not "Write to Device" |
| C2 | the save dialog pre-fills **the filename you typed in the clone dialog**, not the `..._clone_<timestamp>` staging name |
| C3 | the exported file opens as a valid profile |

C2 is the bit I reasoned about rather than tested — `ClonePanel` sets
`frame.profile_filename` to what you typed, so it *should* come through.
If it shows a staging name, say so.

## D. The filename guard still guards

Offline, Export, and deliberately **rename the file** in the save dialog.

Expect the warning that the Edge matches by filename and will accept-
then-ignore anything else, offering to save under the right name
instead. That warning is one of the three behaviours the extraction had
to preserve, so it is worth provoking once.

## E. Mode switching in one session — the thing most likely to be broken

The panel instance is **reused** across mode switches, and the labels
are set in `_refresh()`. If I got that wrong, a label from one mode
survives into the other.

1. Start **connected**, go as far as the Deploy page, note the heading.
2. Go back, switch to **offline**, reach the Deploy page again.
3. Switch back to **connected** and reach it a third time.

Each visit must show the right heading, right button, and right
visibility of eject/check. **A stale label here is a real bug**, and it
is exactly the class that bit `StartupTxtPanel` before.

---

## Pass criteria

- **A4** — the connected four-stage deploy is unchanged. **Passed.**
- **B** — the offline edit flow still exports cleanly through the
  extracted helper. **Passed.**
- **C1** — the reported dead end is gone. **This is now the only test
  of the actual fix**, since B turned out not to touch it.
- **D** — the filename guard survived the extraction.
- **E** — no label survives a mode switch.

## If something fails

The clone is written to disk before any of this matters, at
`<working_dir>/staging/<stem>_clone_<timestamp>.fit`, so nothing is
lost either way.
