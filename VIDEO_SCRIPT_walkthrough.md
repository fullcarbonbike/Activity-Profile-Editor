# TOOLKIT WALKTHROUGH — VIDEO SCRIPT

Drafted 2026-11-25 for #175. Brief as agreed:

| decision | choice |
|---|---|
| audience | Edge owners who want better data screens — rider-facing, FIT internals out of sight |
| length | one video, ~10 minutes |
| scope | GUI start to finish, clone with Ride Type, `fit_odometer` |
| device | real device, live write and restart on camera |
| camera device | **the factory-reset 530** — no personal data, default profiles, zeroed odometer |

Every button label and panel name below is taken from `gui_app.py`
0.34.2, not from memory. If a label reads oddly on screen, the code is
right and this script is stale — check before re-recording.

---

# PART 1 — BEFORE THE CAMERA IS ON

## 1A. Why the reset 530 is the right camera device

It solves four problems at once: no personal data to redact, default
profiles that look like the viewer's own device, a zeroed odometer that
makes the `fit_odometer` segment legible, and a mass-storage mount
that's far easier to film than MTP.

One cost: **the 530 mounts as a filesystem and the 840 is MTP**, so the
deploy step looks different from what an 840/540/1040 owner will do.
Part 4 is a short insert that covers it. Don't skip it — deploy is the
one step where a viewer following along can get stuck.

## 1B. Do not sign the 530 into Garmin Connect

The clean odometer only stays clean if nothing can arrive. Rides sync
**both ways** between two Edges on one Connect account, matched by
profile name, and they land in record 0 as well as the profile record.
A reset 530 with a profile called ROAD, paired to the same account as
the 840, can pull the 840's history straight back in — and the
odometer segment is then showing your real mileage on camera.

## 1C. Redaction checklist

| item | where it shows | what to do |
|---|---|---|
| **device serial** | `fit_dump dump` prints `file_id_mesgs[0].serial_number` in the clear | **do not run `dump` on camera.** `screens` output is safe |
| **serial-keyed backup folder** | the backup path, which is named by device serial | set the working folder somewhere short, and frame the path area out |
| **`startup.txt`** | the Startup Message panel | survives a factory reset — confirm it is already cleared |
| **Finder / desktop** | any full-screen shot | clean desktop, no other windows, notifications off |
| **Connect / browser tabs** | if you show Connect at all | don't, in this video — it isn't in the brief |

## 1D. Rehearsal, once, before recording

Do the whole run silently end to end. The point is not practice, it's
to find out what the device actually does on the day:

- [ ] how long the restart really takes (time it — the narration has to cover it)
- [ ] that the new screen appears where you expect in the scroll order
- [ ] that the clone shows up with the right Ride Type
- [ ] that `fit_odometer list` reads the reset totals cleanly
- [ ] take a **verified backup** before the first take, so a bad take costs a restore and not a rebuild

## 1E. Recording setup

- Screen capture at the window, not the whole display, except where a Finder shot is needed.
- The GUI window grows and never shrinks by design — size it once, before recording, and leave it.
- A phone or second camera on the 530 for the reveal shot. Lock the exposure; the Edge screen is brighter than the desk.

---

# PART 2 — SHOT LIST AND TIMINGS

Ten segments, ~10 minutes. Timings are targets, not a metronome.

| # | time | segment | shot |
|---|---|---|---|
| 1 | 0:00–0:40 | the problem | device in hand, scrolling its own screens |
| 2 | 0:40–1:10 | what this is | GUI first screen |
| 3 | 1:10–1:45 | getting it running | terminal, `install.sh` |
| 4 | 1:45–2:25 | Detect the device | DetectPanel |
| 5 | 2:25–3:05 | profiles, and the backup you didn't ask for | ProfileListPanel |
| 6 | 3:05–4:05 | what a profile actually contains | ViewScreensPanel |
| 7 | 4:05–5:35 | **the edit** — a four-field climbing screen | AddScreenPanel |
| 8 | 5:35–7:25 | review, write, restart, verify | Preflight → Deploy |
| 9 | 7:25–8:00 | **the reveal** | the 530 itself |
| 10 | 8:00–8:50 | clone for another bike | ClonePanel |
| 11 | 8:50–9:35 | the odometer | terminal, `fit_odometer` |
| 12 | 9:35–10:05 | the safety net, and where to get it | RestorePanel, then repo |

---

# PART 3 — NARRATION

Written to be spoken, not read. Short sentences. No hype — the tool is
unusual enough that overselling it only makes it sound less real.

## 1. The problem (0:00–0:40)

> This is a Garmin Edge. It's a good bike computer, and it will let you
> arrange your data screens — up to a point. You get the fields Garmin
> decided belong on that kind of screen, in the arrangements Garmin
> decided to offer.
>
> If you've ever wanted one more field on a screen, or a field the menu
> won't put where you want it, you've hit that point. I did, so I spent
> a few months working out how the Edge actually stores its activity
> profiles, and built a tool that edits them directly.
>
> This is a walkthrough of that tool, on a real device, start to finish.

*Shot: scroll through the device's own screens while you talk. End on the Elevation screen with its two fields — that's what you'll be replacing.*

## 2. What this is (0:40–1:10)

> It's a Python program with a graphical interface. It runs on macOS and
> on Windows. It reads the profile files off the device, lets you change
> them, writes them back, and then checks that what landed is what you
> asked for.
>
> It backs up everything it touches before it touches it, and there's a
> restore button for when you change your mind. I'll show both.
>
> It's free, the source is public, and the link is in the description.

## 3. Getting it running (1:10–1:45)

> There's an install script. It checks for Python, sets up a virtual
> environment, and installs the one dependency — Garmin's own FIT SDK.
> On Windows there's a `.bat` that does the same thing.

*Shot: run `./install.sh`, let it scroll, then launch the GUI. Don't narrate over the whole install — cut it short in the edit.*

> Then you start it, and this is the first screen.

## 4. Detect the device (1:45–2:25)

> Plug the Edge in and press **Detect Garmin**.

*Shot: click `Detect Garmin`. The panel reports the device.*

> It found the device and it's telling me what it is. That matters more
> than it looks: some things on an Edge are model-specific — which data
> fields exist, how many fit on a screen — so the tool checks the model
> rather than assuming.
>
> There's also **Work Without a Device**, if you want to edit a profile
> file you already have a copy of. Not what I'm doing here.

## 5. Profiles, and the backup you didn't ask for (2:25–3:05)

> **List Profiles**.

*Shot: click `List Profiles →`.*

> These are the activity profiles on the device. This one's just been
> factory reset, so they're Garmin's defaults.
>
> Something already happened that's worth saying out loud: listing them
> backed every one of them up. Not when you save — now, before anything
> is edited. The backup folder is keyed to this device's serial number,
> so if you own two Edges their backups can't get mixed up.

*Beat. This is the trust moment of the video — don't rush it.*

> I'll pick ROAD, and **View Screens**.

## 6. What a profile actually contains (3:05–4:05)

*Shot: `ViewScreensPanel`. Let it sit for a second before talking.*

> This is the part the device doesn't show you.
>
> Top section: the screens you actually scroll through, in order, with
> the fields on each one. Here's that Elevation screen from the start of
> the video — Percent Grade and Elevation, two fields.
>
> Below that, screens the profile is carrying but not showing. Some are
> types held in reserve, which the device's own editor can bring back.
> Some are removed — the content is still in the file, but the device
> has pulled them out of the sequence, and there's no menu on the Edge
> that restores them.
>
> And the buttons: reorder with **Move Up** and **Move Down**, change a
> screen with **Edit Selected Screen**, or add one that isn't there.
>
> That's what I want — a climbing screen with more on it than two
> fields.

## 7. The edit (4:05–5:35) — THE CENTREPIECE

> **Add New Screen.**

*Shot: `+ Add New Screen...`*

> I'll give it four fields: Percent Grade, 30-second VAM, Total Ascent,
> and Elevation.

*Shot: `+ Add Field...` four times, picking each from the picker.*

> VAM is climbing rate — metres of ascent per hour. The 30-second
> version is the one that's actually useful on a climb, because the
> instant value jumps around too much to read.
>
> Four fields, chosen by me, on a screen that didn't exist. That's the
> whole point of the tool.

*Shot: the layout diagram updating as fields are added.*

> The diagram shows how they'll be arranged, and the tool checks the
> arrangement is one this model supports — because that differs between
> models, and getting it wrong is how you end up with a screen the
> device won't draw.
>
> **Create Screen**, and it's in the list.

> **(If you prefer a different edit:** this segment is the only part
> that changes. Swap the four fields for whatever you'd actually use —
> all four here were chosen because they appear in the 530's own
> factory ROAD profile, so they're known-supported on this model.
> Everything after this is identical.**)**

## 8. Review, write, restart, verify (5:35–7:25)

> **Review and Deploy.**

*Shot: `Review && Deploy...` → PreflightPanel.*

> Before anything is written, it shows what's about to change and
> re-checks the file it built. If something's wrong, this is where it
> stops.
>
> **Write to Device.**

*Shot: `Write to Device (NewFiles) →`*

> It goes into the `NewFiles` folder, which is how the Edge takes a
> profile in — drop it there, and the device imports it on restart.
> There's only one route that works, and that's it.
>
> Now it has to be ejected properly, and then the device restarts and
> imports the file.

*Shot: eject, then the device restarting. This is the dead air you timed in rehearsal.*

> This takes about [N] seconds. It's doing the import during that
> restart — nothing to do but wait.

*When it comes back:*

> And now the part I actually care about: it reads the profile back off
> the device and compares it to what it meant to write.

*Shot: the verification result.*

> That's not the tool trusting itself. That's the tool checking the
> device.

## 9. The reveal (7:25–8:00)

*Shot: the 530 in hand. No narration for the first few seconds — just scroll to the new screen.*

> There it is. Four fields, on a screen the device's own menu wouldn't
> have built, on a profile it's perfectly happy to use.

## 10. Clone for another bike (8:00–8:50)

> One more thing, and it's the feature I use most.
>
> If you ride more than one bike, you want more than one profile — and
> you want the rides to land in the right category. Garmin Connect
> sorts by sport *and* sub-sport, so a gravel ride logged as a road
> ride counts toward the wrong goals.

*Shot: ProfileListPanel → `Clone...`*

> **Clone**, give it a name, and pick the **Ride Type** — the same list
> the device shows: Road, Mountain, Indoor, Gravel, Cyclocross,
> Commute, Tour, Ebike, Emountain.
>
> So you get your screens, on a profile that counts as the right kind
> of riding. Leave the picker alone and it changes nothing.
>
> One warning it gives you, and it's a real one: the device's own
> templates differ by ride type. A native Emountain profile has screens
> a road profile doesn't. A clone carries the screens it came from — so
> if you clone ROAD into an e-bike profile, you won't get those, and
> nothing on the device would ever tell you.

## 11. The odometer (8:50–9:35)

> Last one, and this is a command-line tool rather than part of the GUI.
>
> The Edge keeps a per-profile odometer, and there's no menu anywhere to
> set it. If you've replaced a device, or reset one, or just want the
> number to match reality, you've had no way to fix it.

*Shot: terminal.*

> `fit_odometer list` reads the totals for every profile.

*Shot: run it. On the reset device they're zeros — say so, it makes the point.*

> This one's just been reset, so everything's zero. `set` writes a
> distance — and time, calories and ride count, which are all stored in
> there too, though nothing on the device displays them. `reset` puts a
> profile back to zero.
>
> Same deal as the GUI: it writes through `NewFiles`, it keeps a backup,
> and you restart to import.

## 12. The safety net, and where to get it (9:35–10:05)

> I'll finish on the button I hope you never need.

*Shot: `Restore from Backup...`*

> Every profile the tool has seen is backed up, and this restores any of
> them. Whole profile, not a per-screen undo — that's deliberate, and
> it's the honest answer: some things the Edge does are not reversible
> from the device, so the recovery path is the file you had before.
>
> The source, the install instructions, and a fairly long write-up of
> how the Edge actually stores this stuff are all in the repository. If
> you find something it gets wrong on your model, I'd like to hear it —
> most of what's in there was worked out one device at a time.

---

# PART 4 — THE 840 / MTP INSERT (optional, ~20 seconds)

Drop in right after the `Write to Device` shot in segment 8.

*Shot: the 840 connected, in OpenMTP or Windows Explorer.*

> Quick note if you have an 840, 540, 1040 or 1050. Those connect over
> MTP rather than as a disk, so you don't get a drive on the desktop and
> you can't drag to it in Finder. You need something that speaks MTP —
> OpenMTP on a Mac, Explorer on Windows — and the destination is the
> same: the `NewFiles` folder inside `Garmin`.
>
> Everything else in this video is identical.

---

# PART 5 — ACCURACY GUARDRAILS

**Things that are true and tempting to overstate.** A wrong claim on
video is permanent, and several of these are retractions the project
already had to make once.

| do NOT say | because |
|---|---|
| "Connect IQ fields break when you clone" | retracted. It was an early-project bug, fixed in #123–#128; cloning has been reliable since |
| "the tool predicts the filename the device will use" | deleted as false in #170. The device renames on import; profiles are resolved by display name |
| "you can un-remove a removed screen" | `--un-remove` was retired in v1.13.0 after a confirmed data-loss hazard. Recovery is restore-from-backup |
| "the first row of Totals.fit must equal the sum of the rest" | widely repeated on the forums and measured to be false |
| "it works the same on every Edge" | field availability and screen layouts are **per-model**, and at least one behaviour is per-firmware |
| anything about field 331 | identified as last-completed-lap duration, but which variant is still open. Leave it out of a rider-facing video entirely |

**Say this instead, if the subject comes up:** "measured on the models I
own, which is two of them."

---

# PART 6 — AFTER RECORDING

## Chapter marks for the description

```
0:00  The problem
0:40  What this is
1:10  Installing it
1:45  Detecting the device
2:25  Profiles and automatic backups
3:05  What a profile actually contains
4:05  Building a four-field climbing screen
5:35  Writing it to the device
7:25  The result on the Edge
8:00  Cloning a profile for another bike
8:50  Setting the odometer
9:35  Restoring, and where to get it
```

## Description — put in it

- The repo link.
- One line that it's free and the source is public.
- The models it's been tested on, and that other Edge models are untested.
- That it backs up before writing, and has a restore.
- An invitation to report what breaks on other models. This is the most
  valuable thing the video can collect — every per-model finding in the
  project so far came from owning the hardware, which does not scale.

## Do NOT put in the description

- The device serial, obviously, or any frame containing it.
- Your Connect account or any Strava link.
- A claim that it works on models you haven't tried.

## If a take goes wrong

The order is chosen so the expensive takes are late and independent.
Segments 1–6 are re-recordable at zero cost. Segment 7 can be re-run by
restoring the backup you took in 1D and starting again. Segments 10–12
don't depend on 7–9 at all, so a bad edit take doesn't cost you the
clone or odometer footage.
