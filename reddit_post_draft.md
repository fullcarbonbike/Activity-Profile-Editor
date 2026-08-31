# Draft Reddit post for r/Garmin

*Check the subreddit's rules/sidebar before posting — some subs require a specific flair for tools/side projects, or limit self-promotion to certain days. Since you're the author, say so plainly (the draft below already does) rather than posting it as if you just "found" the tool.*

---

**Title:** I reverse-engineered the Garmin Edge's Activity Profile format and built a free, open-source tool to back up, clone, and edit your data screens from a computer

**Body:**

Garmin doesn't publish the file format behind Activity Profiles (the data screens, fields, and layouts you set up per activity type), and the on-device editor is workable but slow to use if you're doing anything more than a small tweak — especially rebuilding a similar screen across several profiles, or recovering after you've deleted something by mistake.

I got tired of that friction and spent a while reverse-engineering the format directly from real `.fit` files pulled off my own Edge 530 — every field ID, screen type, and layout rule in the tool is confirmed against a real device, not guessed from documentation, because there mostly isn't any. The result is a small open-source toolkit (Python, MIT license) with both a GUI and command-line tools:

- Back up and restore Activity Profiles, including recovering a profile you've deleted from the device
- Edit a screen's fields, layout, and order without the on-device menu diving
- Clone a profile under a new name
- Save a screen as a "favorite" and reuse it on other profiles
- Import a profile from someone else / another source
- Automatic backup pruning so old snapshots don't pile up forever
- Edit the device's custom boot message

One thing Clone Profile happens to solve that I hadn't fully appreciated until I saw it mentioned as a complaint back when the 530 launched: creating a new profile on-device doesn't carry over any of your other settings — navigation, alerts, sensor pairing, and everything else you'd already tuned on an existing profile — so you're stuck redoing all of it by hand for every new profile. Cloning through this toolkit duplicates the entire file, not just the screens, so all of that comes along automatically; you only need to touch the data screens/fields for whatever makes the new profile different.

It's plain USB mass-storage file manipulation — no account, no cloud, no Garmin Connect integration, nothing installed on the device itself. Runs on macOS and Windows; I've even gotten it running on a 32-bit-only Windows 10 machine for a bike club's donated laptop, if anyone's dealing with genuinely old hardware.

**The catch:** the field IDs and screen-layout data are confirmed on an Edge 530 specifically. The underlying mechanism looks like it should generalize to other Edge models (a demo video of the 850/1050 showed the same 10-field-per-screen cap and layouts, just on a bigger touchscreen), but I don't have another model to verify against — if anyone's willing to try it on a different Edge and report back what does/doesn't match, that's exactly the kind of testing that would help most right now.

Not affiliated with Garmin in any way — just an independent project born out of wanting a faster way to manage my own profiles.

GitHub: https://github.com/fullcarbonbike/Activity-Profile-Editor

Happy to answer questions about how it works or what it can/can't do.
