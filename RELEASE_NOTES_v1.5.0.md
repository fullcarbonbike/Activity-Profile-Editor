# v1.5.0 — Offline mode, Export, and per-model layout rules

*Released 2026-09-29.*

Two things happen in this release. The toolkit becomes usable on Edge
models that connect over **MTP** and can never be mounted as a disk
(540, 840, 1040, 1050), and it stops treating one device's measurements
as universal truth.

---

## Work without a device

**"Work Without a Device..."** on the detect screen takes a folder of
`.fit` profiles instead of a mounted Edge. Everything downstream is the
same: the profile list, the screens view, the editor, backups,
Restore-from-Backup, Clone, and the boot-message editor.

**Export** replaces Deploy. It writes the edited profile to a folder you
choose, then reads it back and byte-compares before reporting success —
and checks the file's own CRC before writing anything at all. You move
the result onto the device yourself.

**The filename matters, and the dialog handles it for you.** The Edge
matches profiles by filename when it imports them and silently ignores
anything that doesn't match — no error, no indication, the profile
simply doesn't change. The save dialog pre-fills the profile's original
filename rather than the internal staging name. Change it anyway and
you'll get a warning naming the consequence, not a refusal: exporting a
spare copy under another name is legitimate.

**`startup.txt` works offline too**, reading from and writing to files
rather than the device.

This has carried real work end to end: an 840 ROAD profile edited
offline, exported, moved with OpenMTP, and rendering correctly on the
device — including a Connect IQ field that survived three chained edits.

---

## Layout rules are per-model now

Every layout table in this toolkit was measured on an Edge 530 and
applied to every device. That was fine with one model. With two it
started **refusing states the hardware permits**: Compass is locked to
2 data fields on a 530, and the 840's own editor offers 0, 1 or 2.

The toolkit now reads `file_id.product` from the profile itself — which
works offline, on a backup, with nothing plugged in — and applies each
model's rules only to that model.

**Where a model's rules haven't been measured, the toolkit advises
instead of refusing.** It will tell you a field count looks unusual and
write it anyway, rather than blocking an edit on a device it has never
surveyed. Refusing is reserved for states known to be illegal on the
model in hand.

The Edge 840's rules are now measured and included: user screens with
A/B/C layouts at 3–9 fields, Compass at 0/1/2, eBike and STEPS Metrics
at 1–8, Segment's full set, and the 840-only screen types (Power Guide,
Stamina, GroupRide, Music Control).

### Why this couldn't be derived

Segment's variants store different values on the two models — the
same screen type, the same visible layout, the same field geometry, a
different stored number. There's no rule that generates that. It has to
be measured per model, which is why unmeasured combinations are allowed
rather than guessed at.

---

## Fixes

- **A guard that protected the wrong number of screens.** The check
  that stops you hiding your last remaining data screen counted
  switched-off screens as active ones. On an 840 profile holding
  exactly one user screen it counted seven. It now counts one.
- **Switched-off screens were listed as editable.** The 840 keeps
  screen records the device isn't currently offering — hardware-
  conditional ones like Lights and eBike Metrics. They were reported as
  ordinary active screens. They're now listed separately as held in
  reserve, with an explanation.
- **New screens on an 840 were named absurdly** ("Screen 164") because
  the numbering counted named Garmin screens as user screens.
- **The window stretched to screen width** when a profile's details ran
  long. The details pane is now a scrolling panel that wraps and never
  widens the window.
- **The screens list shows ten rows** rather than six.
- **A false "unsaved edits" warning** when backing out of a profile you
  only looked at. The check now asks whether anything actually differs.
- Four new data field names: **Compass**, **Map**, **Location**, and
  corrections elsewhere.

---

## Devices

Tested on **Edge 530** (USB mass storage) and **Edge 840** (MTP).

Offline mode is what makes newer models usable, but it isn't only for
them — it's also how you edit a profile you pulled last week with
nothing plugged in.

---

## Upgrading

Replace the `.py` files. No configuration changes, and existing backups
stay exactly where they are and stay restorable — new backups are filed
per device, old ones are still found.
