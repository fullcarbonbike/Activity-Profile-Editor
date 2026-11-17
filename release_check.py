#!/usr/bin/env python3
__version__ = "1.2.0"  # UNWRAPPED-LABEL RATCHET (2026-11-13), from Doug's B1 bug. A wx.StaticText whose label interpolates a filename, path or exception message widens the window to fit, and _relayout() grows and never shrinks by design, so one long label widens the window for the rest of the session -- that is #69, #105, and TWICE MORE inside #171's own bench test (the ride-type note, then the name-collision warning one branch away from it). A sweep found 28 more in gui_app.py, all predating #171. Deliberately a RATCHET rather than a gate: demanding all 28 be fixed before a tag would either block the release or get this check deleted, whereas demanding the number not GROW costs nothing and makes the class visible. The check says when the baseline can be lowered. Prior entry (1.1.0): UNDEFINED-NAME CHECK ADDED (2026-11-12), because #171 shipped a NameError past every other check in this file. gui_app called fit_clone_profile.filename_prefix_for() without importing it; Doug's bench test found it as "the clone filename stops auto-filling, but only when you pick a ride type" -- only when, because the Unchanged branch never reaches the call. py_compile passes (the name resolves at call time), `import gui_app` passes for the same reason so even a machine with wx is blind to it, and the headless harness had RE-IMPLEMENTED the picker logic rather than importing it, so it tested a copy. Uses symtable, not a hand-rolled AST scope walk: the interpreter's own per-scope symbol tables already know what is global, assigned and imported, so this borrows that judgement instead of re-deriving it badly. One false-positive class over this repo -- module dunders -- allowlisted. Prior entry (1.0.0): BUILT WHEN THE TRIGGER FIRED (2026-11-09, for v1.8.0). PROJECT_NOTES.md kept this as a CONDITIONAL item on Doug's explicit instruction (2026-10-31): raise it only when a release with real complexity comes up, not for a typo fix. #171 touches both the CLI and the GUI, so it came up. The five checks below are the ones that were re-derived by hand before each of the last three tags, and TWO OF THEM HAVE ALREADY CAUGHT REAL PROBLEMS: the missing `git status` check is how v1.7.5 got tagged one commit early, carrying neither #170 nor its own release notes, and the personal-figure sweep caught two violations in two days, both headed for a public repo -- once in a source docstring, once in a Doc rev table. Deliberately NOT a test runner and not a linter: it checks the things that go wrong between "the code works" and "the tag is right", which is a different and much smaller list. Scoped to GIT-TRACKED files only, because the risk being managed is what reaches the public repo -- untracked working notes and forum drafts legitimately contain ride figures and are nobody else's business. stdlib only, like everything else here.
"""
release_check.py -- pre-tag checks for this repo.

    python3 release_check.py 1.8.0

Exits non-zero if anything fails, so it can gate a tag. Run it from
the repo root, with the version you are about to tag.

The checks, and why each exists:

  1. Working tree clean, and HEAD == origin/main.
     v1.7.5 was tagged one commit early because this was skipped.

  2. The release-notes file for this version exists and is tracked.
     An untracked release-notes file is invisible to everyone else.

  3. Every X.Y.Z version claimed in the release notes matches that
     file's actual __version__. Release notes are written last, which
     is exactly when a stale version number slips through.

  4. No personal ride figures in tracked .py or .md files. The repo is
     public. This has been violated twice.

  5. Every module compiles, and imports if its dependencies are here.

  6. No undefined names in any tracked module. Added after a #171 bug
     that every other check here was blind to: a function used in
     gui_app and never imported, which only fails on the code path
     that calls it.

  7. The count of unwrapped dynamic wx labels in gui_app.py has not
     grown. A ratchet, not a gate -- see UNWRAPPED_LABEL_BASELINE.

A third-party module that is not installed (wx, on a headless box) is
reported as SKIPPED, not failed -- that is a property of the machine,
not of the code. On Doug's own machine wx is present and the import
really happens.
"""
import os
import re
import subprocess
import sys
import py_compile
import symtable
import tempfile
import builtins

FAILED = []
PASSED = []
NOTES = []


def run(*args):
    """Run a git command, returning (ok, stdout)."""
    try:
        p = subprocess.run(args, capture_output=True, text=True)
    except OSError as e:
        return False, str(e)
    return p.returncode == 0, (p.stdout or p.stderr).strip()


def tracked(*suffixes):
    ok, out = run("git", "ls-files")
    if not ok:
        return []
    return [f for f in out.split("\n")
            if f and (not suffixes or f.endswith(suffixes))]


def check(label, ok, detail=""):
    (PASSED if ok else FAILED).append((label, detail))


# ---------------------------------------------------------------- 1
def check_git_state():
    ok, out = run("git", "status", "--porcelain")
    if not ok:
        check("git state", False, "not a git repo, or git unavailable")
        return
    check("working tree clean", out == "",
          "uncommitted changes:\n    " + "\n    ".join(out.split("\n")) if out else "")

    ok_head, head = run("git", "rev-parse", "HEAD")
    ok_up, up = run("git", "rev-parse", "origin/main")
    if not (ok_head and ok_up):
        NOTES.append("origin/main not available locally -- run `git fetch` "
                     "and re-check before tagging")
        return
    check("HEAD == origin/main", head == up,
          f"HEAD {head[:12]} vs origin/main {up[:12]} -- push before tagging")


# ---------------------------------------------------------------- 2
def check_release_notes_file(version):
    name = f"RELEASE_NOTES_v{version}.md"
    exists = os.path.exists(name)
    check(f"{name} exists", exists)
    if exists:
        check(f"{name} is tracked by git", name in tracked(),
              "it exists but git does not know about it -- `git add` it")
    return name if exists else None


# ---------------------------------------------------------------- 3
def module_version(path):
    """The __version__ string a module declares, or None."""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'__version__\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def check_versions_in_notes(notes_path):
    """
    Every `module.py ... X.Y.Z` pairing in the release notes has to
    match what that module actually declares.

    Looks for a module filename and a version on the SAME line, which
    is how these notes have always been written. A line naming a module
    with no version on it is not a claim and is skipped.
    """
    if notes_path is None:
        return
    mods = {os.path.basename(p): p for p in tracked(".py")}
    try:
        with open(notes_path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        check("release notes readable", False, str(e))
        return

    claims = 0
    in_fence = False
    for n, line in enumerate(lines, 1):
        # SKIP FENCED CODE. Release notes show how to run things, and
        # `python3 release_check.py 1.8.0` is a command, not a claim
        # that the module is at version 1.8.0 -- which is exactly what
        # this check reported on its first run against its own notes.
        # Version claims live in prose and tables; commands live in
        # fences. Caught the same day the undefined-name check was
        # added, and it is the same lesson: a gate that reports things
        # that are not wrong gets switched off.
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Inline code spans carrying BOTH the module name and a
        # version are invocations, not claims: `python3
        # release_check.py 1.8.0` is how you run it, and the version
        # there is the TAG being checked. A version table separates
        # them -- the name sits in its own span, the version in
        # another cell -- so "same span as the name" is the test.
        # Fence-skipping above did not catch this one because the
        # usage line is inline code, not a fenced block.
        spans = re.findall(r"`([^`]*)`", line)
        for name in mods:
            if name not in line:
                continue
            in_cmd = {v for sp in spans if name in sp
                      for v in re.findall(r"\b(\d+\.\d+\.\d+)\b", sp)}
            for ver in re.findall(r"\b(\d+\.\d+\.\d+)\b", line):
                if ver in in_cmd:
                    continue
                actual = module_version(mods[name])
                if actual is None:
                    continue
                claims += 1
                check(f"{name} == {ver} (notes line {n})", actual == ver,
                      f"notes say {ver}, {name} declares {actual}")
    if claims == 0:
        NOTES.append(f"{notes_path} makes no module/version claims to verify "
                     f"-- check by hand that it lists what changed")


# ---------------------------------------------------------------- 4
# The repo is PUBLIC. Doug's lifetime odometer totals and Garmin
# Connect figures are his, and twice they have reached a tracked file:
# once in a fit_odometer.py docstring, once in a PROJECT_NOTES table.
#
# A figure is suspicious when it is big and carries a distance unit.
# Short measured deltas -- "68 m", "98 m", a single ride -- are what
# the findings actually rest on and are fine; it is the four-and-more
# digit lifetime distances that are personal. Comma-grouped numbers are
# flagged at any size because that is how Connect prints them.
# A FIGURE ALONE IS NOT THE PROBLEM, and the first version of this
# check got that wrong -- it flagged 24 lines, nearly all of them
# invented examples (`--distance 2240mi` in help text) or the measured
# ride deltas the findings actually rest on (`+98 m`, `17,387 m`).
# A check that cries wolf 20 times gets ignored, which is worse than
# not having it.
#
# What makes a figure personal is being ATTRIBUTED to the rider. Both
# real violations read that way -- "Doug's real odometer reading",
# "his own rough recollection" -- so the test is co-occurrence: a
# distance-shaped figure AND a possessive marker, in the same sentence.
DISTANCE_SHAPED = (
    r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\s*(?:mi|miles|km|m)\b",
    r"\b\d{4,}(?:\.\d+)?\s*(?:mi|miles|km)\b",
)

# A BARE metre value, no unit attached. Added after the first run: the
# check found a mileage on a line that ALSO carried the raw
# `distance = <metres>` it converted from, and missed the raw number
# entirely -- just as personal, and the form this file quotes device
# data in.
#
# ⚠ The first attempt at this was `\d{6,9}` plus a personal marker,
# and it immediately flagged a forum thread ID and a backup path
# timestamp -- re-introducing exactly the noise the rewrite above had
# just removed. A bare number needs DISTANCE CONTEXT, not merely
# attribution: the keyword has to sit right in front of it. Timestamps
# and IDs do not read "distance = ...".
BARE_WITH_CONTEXT = (
    r"\b(?:distance|odometer|mileage|met(?:re|er)s?)\b[^\d\n]{0,25}"
    r"(\d{6,9})(?![\d.])",
)
# Possessives and ground-truth phrasings. Deliberately includes the
# maintainer's name: in a public repo "Doug's 5,826.70 mi" is the
# exact shape of the thing being prevented.
PERSONAL_MARKERS = (
    "doug's", "doug’s", "his own", "his real", "my own",
    "real odometer", "real-world ground truth", "ground truth",
    "lifetime total", "lifetime odometer", "his odometer", "my odometer",
)
# This file necessarily contains both the patterns and the examples.
SELF = "release_check.py"


def check_no_personal_figures():
    """
    Flag a distance figure only when the surrounding sentence
    attributes it to the rider.

    WINDOW, not line: prose in these files wraps at ~70 columns, so
    "Doug's" and the figure routinely land on different lines. Two
    lines either side covers every real case in the corpus without
    reaching across paragraph boundaries.
    """
    hits = []
    for path in tracked(".py", ".md"):
        if os.path.basename(path) == SELF:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            continue
        for n, line in enumerate(lines, 1):
            figures = [m.group(0) for pat in DISTANCE_SHAPED
                       for m in re.finditer(pat, line)]
            figures += [m.group(1) for pat in BARE_WITH_CONTEXT
                        for m in re.finditer(pat, line, re.IGNORECASE)]
            if not figures:
                continue
            window = " ".join(lines[max(0, n - 3):n + 2]).lower()
            marker = next((k for k in PERSONAL_MARKERS if k in window), None)
            if marker:
                hits.append(f"{path}:{n}: {', '.join(figures)} "
                            f"-- attributed via {marker!r}")
    check("no rider-attributed distance figures in tracked .py/.md", not hits,
          "\n    ".join(hits) +
          ("\n    The repo is public. Redact the figure and keep the finding."
           if hits else ""))


# ---------------------------------------------------------------- 5
def check_modules_build():
    broken, skipped = [], []
    for path in tracked(".py"):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                py_compile.compile(path, cfile=os.path.join(tmp, "o.pyc"),
                                   doraise=True)
            except py_compile.PyCompileError as e:
                broken.append(f"{path}: {e.msg.strip().splitlines()[-1]}")
                continue
        mod = os.path.basename(path)[:-3]
        p = subprocess.run([sys.executable, "-c", f"import {mod}"],
                           capture_output=True, text=True)
        if p.returncode:
            last = (p.stderr.strip().splitlines() or [""])[-1]
            if "ModuleNotFoundError" in last:
                skipped.append(f"{path}: {last}")
            else:
                broken.append(f"{path}: {last}")
    check("every tracked module compiles and imports", not broken,
          "\n    ".join(broken))
    for s in skipped:
        NOTES.append(f"import SKIPPED (dependency not on this machine) -- {s}")


# ---------------------------------------------------------------- 6
# Module dunders: present at runtime, never assigned in the source.
MODULE_DUNDERS = {
    "__file__", "__name__", "__doc__", "__spec__", "__package__",
    "__loader__", "__builtins__", "__debug__",
}


def undefined_globals(src, fname):
    """
    Names a module reads as globals but never binds and that are not
    builtins -- i.e. NameErrors waiting for the right code path.

    ADDED FOR A BUG THIS CHECK WOULD HAVE CAUGHT (2026-11-12). #171's
    filename fix called fit_clone_profile.filename_prefix_for() from
    gui_app and never added it to the import list. The symptom reached
    Doug's bench: the clone filename stopped auto-filling, but ONLY
    when a ride type was picked, because the Unchanged branch never
    reaches the call. Nothing before this caught it --
    - py_compile passes: the name resolves at call time, not compile time
    - `import gui_app` passes for the same reason, so even on a machine
      with wx the import check is blind to it
    - and the headless harness RE-IMPLEMENTED the picker's logic
      instead of importing it, so it exercised a copy, not the code
    Uses symtable rather than a hand-rolled AST scope walk: the
    interpreter's own symbol tables already know what is global,
    assigned and imported per scope, so this borrows that judgement
    instead of re-deriving it badly. Over this repo it reports exactly
    one class of false positive -- module dunders -- which is
    allowlisted above.
    """
    top = symtable.symtable(src, fname, "exec")
    bound = {s.get_name() for s in top.get_symbols()
             if s.is_assigned() or s.is_imported() or s.is_namespace()}
    found = set()

    def walk(tbl):
        for s in tbl.get_symbols():
            if s.is_global() and not s.is_assigned():
                n = s.get_name()
                if (n not in bound and n not in dir(builtins)
                        and n not in MODULE_DUNDERS):
                    found.add((tbl.get_name(), n))
        for child in tbl.get_children():
            walk(child)

    walk(top)
    return sorted(found, key=lambda x: (x[1], x[0]))


def check_undefined_names():
    hits = []
    for path in tracked(".py"):
        try:
            src = open(path, encoding="utf-8").read()
        except OSError:
            continue
        try:
            for scope, name in undefined_globals(src, path):
                hits.append(f"{path}: {name!r} used in {scope}() but never "
                            f"imported or defined")
        except SyntaxError as e:
            hits.append(f"{path}: will not parse -- {e}")
    check("no undefined names in tracked modules", not hits,
          "\n    ".join(hits))


# ---------------------------------------------------------------- 7
# A wx.StaticText whose label interpolates a filename, a path or an
# exception message grows the window to fit it, and _relayout() grows
# and never shrinks by design -- so one long label widens the window
# for the rest of the session. That is #69, #105, and twice more in
# #171's own bench test.
#
# A RATCHET, NOT A GATE. There are 28 such labels left in gui_app.py,
# all predating #171, and most will never see a long value. Demanding
# they all be fixed before a tag would either block the release or get
# this check deleted. Demanding the number not GROW costs nothing and
# makes the class visible. Lower it whenever a batch gets fixed; the
# check says so when it can be lowered.
UNWRAPPED_LABEL_BASELINE = 28
WRAPPERS = ("textwrap.fill", "wrapped_label", "_wrap_status_paragraphs")


def unwrapped_dynamic_labels(path):
    """Lines where SetLabel() gets interpolated text with no wrapper."""
    import ast
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return []
    lines = src.split("\n")
    out = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr == "SetLabel" and n.args):
            continue
        arg = n.args[0]
        if isinstance(arg, ast.Constant):
            continue  # a literal cannot grow
        seg = "\n".join(lines[n.lineno - 1:(n.end_lineno or n.lineno)])
        if any(w in seg for w in WRAPPERS):
            continue
        if isinstance(arg, (ast.JoinedStr, ast.Name, ast.BinOp,
                            ast.Call, ast.IfExp)):
            out.append(n.lineno)
    return sorted(out)


def check_unwrapped_labels():
    found = unwrapped_dynamic_labels("gui_app.py")
    n = len(found)
    if n > UNWRAPPED_LABEL_BASELINE:
        check(f"unwrapped dynamic labels <= {UNWRAPPED_LABEL_BASELINE}", False,
              f"{n} found, baseline is {UNWRAPPED_LABEL_BASELINE} -- new ones "
              f"at or near lines {found[-(n - UNWRAPPED_LABEL_BASELINE):]}. "
              f"Wrap them with wrapped_label().")
    else:
        check(f"unwrapped dynamic labels <= {UNWRAPPED_LABEL_BASELINE}", True)
        if n < UNWRAPPED_LABEL_BASELINE:
            NOTES.append(f"only {n} unwrapped labels left (baseline "
                         f"{UNWRAPPED_LABEL_BASELINE}) -- lower "
                         f"UNWRAPPED_LABEL_BASELINE in this file to {n}")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
        print(f"usage: {os.path.basename(sys.argv[0])} X.Y.Z\n"
              f"       (the version you are about to tag, without the 'v')",
              file=sys.stderr)
        return 2
    version = sys.argv[1]
    print(f"release_check {__version__} -- checking for v{version}\n")

    check_git_state()
    notes = check_release_notes_file(version)
    check_versions_in_notes(notes)
    check_no_personal_figures()
    check_modules_build()
    check_undefined_names()
    check_unwrapped_labels()

    for label, _ in PASSED:
        print(f"  PASS  {label}")
    for label, detail in FAILED:
        print(f"  FAIL  {label}")
        if detail:
            print(f"    {detail}")
    for note in NOTES:
        print(f"  NOTE  {note}")

    print(f"\n{len(PASSED)} passed, {len(FAILED)} failed, {len(NOTES)} note(s)")
    if FAILED:
        print("\nNOT ready to tag.")
        return 1
    print("\nChecks pass. Remember the tag goes on the release-notes commit:")
    print(f"  git rev-parse HEAD v{version}^{{commit}}   # must match after tagging")
    return 0


if __name__ == "__main__":
    sys.exit(main())
