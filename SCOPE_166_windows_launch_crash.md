# Scope — #166, the GUI will not launch on Windows

*Scoping only, 2026-10-26, from Doug updating the bike-club Win10
laptop. Nothing changed.*

---

## This is not a version problem

Both of us started from the wrong premise. Doug recalled the laptop
needing "older versions of some files"; I went looking for a Python or
wxPython incompatibility. The traceback says otherwise:

```
File "...\gui_app.py", line 6324, in __init__
    self.message_text.OSXDisableAllSmartSubstitutions()
NotImplementedError
```

Line 6324 of **v1.7.3** is exactly that call, so the laptop is running
the current release. Nothing is stale and nothing needs downgrading.

*(The `Unable to set default locale` line above it is the known
cosmetic wx/Windows message from Doc rev 88 — unrelated, harmless.)*

## The guard is there, and it is the wrong kind of guard

```python
# through. hasattr-guarded: this method exists only on macOS
# builds of wxWidgets.
if hasattr(self.message_text, "OSXDisableAllSmartSubstitutions"):
    self.message_text.OSXDisableAllSmartSubstitutions()
```

**The comment states the assumption, and the assumption is false.**
wxPython exposes this method on *every* port; the non-macOS
implementation raises `NotImplementedError` when called. So `hasattr()`
returns True on Windows and the guard passes straight through to a call
that cannot work.

A guard testing for the wrong thing is worse than no guard: it reads as
handled, so nobody looks again.

## Why it is fatal rather than cosmetic

`MainFrame.__init__` builds **all eleven panels eagerly**:

```python
self.panels = {
    "detect": DetectPanel(...), ...
    "startup_txt": StartupTxtPanel(self.container, self),
}
```

So `StartupTxtPanel.__init__` runs at launch whether or not the user
ever opens the boot-message editor. The exception escapes `OnInit`,
which returns false, and the app exits before showing a window.

**There is no partial failure and no workaround from inside the app.**

## ⚠ How long this has shipped, and why nobody saw it

| | |
|---|---|
| the call landed | **2026-09-27**, in the v1.5.0 offline-mode work |
| Windows 11 last confirmed | **2026-08-19** |
| Windows 10 32-bit last confirmed | **2026-08-29** |

Both confirmations predate the call. **No Windows machine has run any
version containing it.** That means v1.5.0, v1.6.0, v1.6.1, v1.7.0,
v1.7.1, v1.7.2 and v1.7.3 — seven releases over a month — are untested
on Windows, and at least on this build the GUI does not start at all.

The README still advertises Windows as confirmed, citing the August
dates. That is true of what was tested and misleading about what
shipped.

**Unknown, and not to be guessed at:** whether Windows 11 with wxPython
4.3.1 also crashes. It may raise identically, or a newer wx may make the
call a harmless no-op. Doug has that laptop; one launch answers it, and
the answer decides whether this is "all Windows" or "some Windows".

## The fix

Use the test the project already uses twice for platform behaviour:

```python
if platform.system() == "Darwin":
    self.message_text.OSXDisableAllSmartSubstitutions()
```

`platform` is already imported, and `DeployPanel` gates its eject button
on exactly this expression. A `try/except NotImplementedError` would
also work but is the weaker choice — it would swallow the signal if the
same mistake is made again elsewhere.

**The comment must be corrected too**, not just the code. It is the
thing that would otherwise reproduce the error: anyone reading
"this method exists only on macOS builds" has no reason to doubt the
`hasattr`.

**No other instance exists.** Grepped for `.OSX*(`, `.MSW*(`, `.GTK*(`
across the GUI: this is the only platform-specific wx call in the file,
and the only `hasattr` guard on a wx object.

## What it says about the shape of the app

Eager construction of every panel means **any** platform-specific
failure in **any** constructor is fatal at launch rather than confined
to the feature it belongs to. That is a reasonable trade — panels switch
instantly and there is no lazy-init complexity — but it raises the cost
of a constructor-time mistake from "one broken screen" to "the app does
not start".

Not proposing lazy construction. Recording it, because it explains why
a one-line error in an optional feature took down everything.

## Scope of the change

| piece | size |
|---|---|
| the guard | one line |
| the comment | three lines |
| README Windows claim | a dated qualifier, since the August confirmations no longer describe what ships |
| a Doc rev | the testing gap is the finding, not the one-liner |

## Before it ships

This needs a **Windows launch test**, which is the one thing that was
missing for a month. Both machines if possible:

1. the Win10 32-bit laptop — the one that reported it
2. Windows 11 with current wxPython — to learn whether it was affected
   too, which is still unknown

A fix for a crash nobody can reproduce on the fixer's machine is
exactly the kind that wants confirming on the hardware that found it.
