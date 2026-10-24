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

## B. Offline path — the fix

Offline mode against a folder, edit a screen → Pre-Flight → Deploy.

| # | check | expect |
|---|---|---|
| B1 | panel heading | **"Export Profile"** |
| B2 | main button | **"Export..."** |
| B3 | eject / check buttons | **gone, not greyed** |
| B4 | status text | says no device is connected and you transfer it yourself |
| B5 | press Export | save dialog, pre-filled with the profile's own filename |
| B6 | save it | "Verified twice" message naming the CRC |
| B7 | after saving | status says Exported, **Export disabled**, **Done enabled** |
| B8 | Done | returns to the profile list |
| B9 | Pre-Flight heading | "What will change **when you put this on the device**:" |

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

- **A4** — the connected four-stage deploy is unchanged.
- **B2, B3, B7** — offline offers Export, hides the device controls, and
  ends in a state you can leave.
- **C1** — the reported dead end is gone.
- **E** — no label survives a mode switch.

## If something fails

The clone is written to disk before any of this matters, at
`<working_dir>/staging/<stem>_clone_<timestamp>.fit`, so nothing is
lost either way.
