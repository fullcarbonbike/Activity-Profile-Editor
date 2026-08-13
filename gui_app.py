#!/usr/bin/env python3
__version__ = "0.16.12"  # Cosmetic doc-only fix (2026-08-13): FieldPickerDialog's docstring said "105 confirmed entries" -- stale after fit_dump.py grew to 117 across the 2026-08-11 batch (v2.4.7) and the 49/320 rename-only corrections (v2.4.8/2.4.9); same class of drift already fixed once before at v0.16.5 (87->105). No functional change -- FIELD_ID_NAMES is imported live from fit_dump.py, so the actual field picker was never wrong, only this comment. Caught while confirming pre-release state ahead of a possible v1.0.1 tag. Prior entry (v0.16.11): Doc-only, no code change (2026-08-11): the "restore a profile no longer on the device" enhancement (scoped, not yet built -- see PROJECT_NOTES.md Open Items, task list #57) had one real open technical risk: whether the device's NewFiles import can actually RECREATE a profile that's been deleted from Sports/, not just replace an existing one or accept a brand-new never-before-seen filename (Clone Profile's case, confirmed separately this same day). Doug tested this exact scenario directly via garmin_device.py deploy <backup_of_a_deleted_profile.fit> <target_profile_filename>, targeting a filename he'd deliberately deleted from the device -- CONFIRMED via on-device verification: NewFiles correctly recreated the deleted profile. This is the stronger of the two related confirmations logged today, since it's the literal restore-a-deleted-profile path, not just an analogous one -- the backend mechanics this GUI feature would wrap are now fully proven end to end; only the GUI entry-point gap itself remains unbuilt. Prior entry (v0.16.10): Doc-only, no code change (2026-08-11): Clone Profile (v0.16.0, ClonePanel) has been CONFIRMED via real hardware -- Doug reported this after the fact, it just hadn't been logged yet. At least two clones deployed and working correctly through NewFiles under brand-new filenames not previously present on the device: Clonebox (from Sandbox) and CloneRoad (from Road). This also resolves a question that had been open since v0.16.0: whether NewFiles correctly accepts a genuinely NEW filename via the same pathway used to replace an existing one, rather than just the latter -- confirmed yes. Directly relevant to the newly scoped "restore a profile no longer on the device" enhancement (see PROJECT_NOTES.md Open Items), which shares this exact mechanism and had been carrying this as its single biggest open risk; that risk is now cleared. README.md and PROJECT_NOTES.md corrected to match (both had carried a stale "not yet tested through the actual GUI on real hardware" note against Clone Profile). Prior entry (v0.16.9): Real fix, pre-Windows-support housekeeping (2026-08-11): DEFAULT_WORKING_DIR was hardcoded to "/Volumes/UserDCbu/dougcurtis/GarminBackups" -- Doug's own actual Mac path, harmless as long as only Doug ran this, but a real problem for anyone else (wrong user, and outright broken on Windows where /Volumes/... isn't a thing at all). Now os.path.join(os.path.expanduser("~"), "GarminBackups") -- resolves sanely on any OS/user. Also, working_dir was NEVER persisted across app restarts even after being changed via ProfileListPanel's "Change..." button -- every launch reset to the default, forcing a re-browse for anyone using a custom location. Added load_saved_working_dir()/save_working_dir(), a small JSON sidecar at ~/.garmin_screen_editor_config.json: MainFrame.__init__ now seeds working_dir from the saved value if one exists (falling back to DEFAULT_WORKING_DIR only on a true first-ever launch), and on_change_working_dir() saves immediately whenever the user picks a new directory. Both are best-effort/never-raise (missing file, corrupt JSON, read-only home dir all just fall back to in-memory-only behavior for that session) so a config-file problem can never block using the app. User-confirmed design choice (2026-08-11) over two simpler alternatives (plain default with no persistence; first-use-only prompt) -- this one needed the persistence layer either way, so it solves it for good rather than just changing what the default looks like. Compiled clean. Prior entry (v0.16.8): New "About" button on DetectPanel (part of the same pre-publish pass as v0.16.7's rename) -- opens AboutDialog, a short modal summary (app name/version, "not affiliated with Garmin" trademark disclaimer, a one-paragraph note that the undocumented data_screen format was reverse-engineered via black-box observation of real files rather than reverse-engineering Garmin's own SDK/software, and an MIT license mention pointing to LICENSE/README.md for the full text) -- deliberately a SHORT summary, not an attempt to embed the full legal text verbatim, so this dialog's wording never has to track README.md's disclaimer word-for-word. New module-level ABOUT_TEXT template string, formatted with __version__ at dialog-open time. Body uses a read-only word-wrapped wx.TextCtrl rather than wx.StaticText -- not because of the v0.16.2/v0.16.3/v0.16.6 best-size bug class (this is a modal wx.Dialog with its own fixed size, not embedded in MainFrame's resizable sizer tree, so it can't reproduce that regardless), just because wrapping is the right call for a paragraph this long either way. Headless-verified the string's backslash-continuation formatting collapses to clean single-line paragraphs with real paragraph breaks (evaluated the literal directly, not via regex extraction, to actually exercise Python's string-literal line-continuation parsing). Compiled clean. Prior entry (v0.16.7): Cosmetic rename ahead of a possible public GitHub release: window title changed from "Garmin Edge Screen Editor" to "Activity Profile Screen Editor for Garmin Edge" -- this is an independent, unofficial project, not a Garmin product, and the old title read too much like one. "For Garmin Edge" is the standard nominative-fair-use pattern (naming the compatible device without claiming official status), user-confirmed choice over two safer/more-Garmin-referencing alternatives. No functional change. See LICENSE and the README disclaimer draft (README_DISCLAIMER_DRAFT.md, pending review) for the rest of the pre-publish housekeeping this is part of. Prior entry (v0.16.6): Real reported bug fix, corrects a wrong fix (2026-08-10): v0.16.3's 460px ceiling on the Fields column stopped the frame from growing, but silently broke something else -- wx.ListCtrl clips a cell's text to its column's pixel width with NO wrap/ellipsis, and the control's own horizontal scrollbar only engages when the SUM of ALL column widths exceeds the control's rendered area, which a single capped column mostly never triggers. Net effect: text silently truncated mid-character instead of the window growing -- confirmed on a real 10-field screen with several of the new longer field names (only 6-7 visible, no way to see the rest). The v0.16.3 comment's "content past the ceiling relies on the ListCtrl's own native horizontal scroll" claim was simply wrong -- the SECOND unverified assumption about this exact widget's real behavior in three days (see PROJECT_NOTES.md "Corrections and lessons learned"). Correct fix: stop trying to control the FRAME's size by capping the COLUMN -- decouple them instead. New ScreensListCtrl(wx.ListCtrl) subclass overrides DoGetBestSize() to cap only the WIDTH the sizer system sees (height still comes from the normal calculation, preserving v0.11.0's grow-taller-for-more-rows behavior); ViewScreensPanel.screens_list and RestorePanel.history_list (same exposure, proactively fixed too -- it had never even gotten the v0.16.3 ceiling) both now use it instead of a plain wx.ListCtrl. With the frame's size no longer tied to column content at all, the Fields column is safe to auto-size to its FULL real content again (reverted to floor-only 280px, no ceiling) -- and when that's genuinely wider than the space available, the ListCtrl's real native horizontal scrollbar engages for real this time, since assigned-area-smaller-than-content is now the true state of affairs rather than being masked by a frame that always grows to match. Compiled clean; AST-confirmed ScreensListCtrl is defined and both call sites use it. Prior entry (v0.16.5): Cosmetic doc-only fix: FieldPickerDialog's docstring said "87 confirmed entries" -- stale after fit_dump.py v2.4.4 added 18 confirmed field IDs (2026-08-10 batch), bringing FIELD_ID_NAMES to 105. No functional/behavioral change. Prior entry (v0.16.4): Readability fix, real reported feedback with a side-by-side screenshot: LayoutDiagramPanel's cell-label text (9pt) was noticeably smaller than the rest of the window's controls, hard to read. Bumped to 13pt (10pt for the italic B-layout note and the "(no layout to show)" placeholder), and bumped SetMinSize() from (280,220) to (340,280) to give the bigger font more room in the smallest cells (8-10 field layouts have the most rows/cells). Confirmed via code review that this has NO width/height side effect of the kind fixed in v0.16.2/v0.16.3: unlike wx.ListBox/wx.ListCtrl, LayoutDiagramPanel is custom-painted (on_paint(), wx.EVT_PAINT) with an explicit per-cell wx.DC clipping region -- its reported size is only ever the fixed SetMinSize() value, never derived from font size or label content, so there was no risk of this reproducing the same window-growth bug. One flagged (not yet acted on) readability trade-off: a longer known field name in a busy 8-10 field layout is now somewhat more likely to get silently clipped (DrawLabel() has no ellipsis) at the bigger font than it was at 9pt -- worth watching for during testing on dense screens. Prior entry (v0.16.3): Same-day follow-up to v0.16.2 -- that fix only covered EditScreenPanel/AddScreenPanel's wx.ListBox; a real reported regression showed the identical root cause ALSO hits ViewScreensPanel's "Fields" ListCtrl column: a real profile with 9 of 10 fields unresolved on two different screens still widened the window from "View Screens." The v0.11.1 fix's assumption -- that a wx.ListCtrl in report mode never grows the FRAME from column content, relying instead on the control's own native horizontal scrollbar -- turned out not to hold for large enough overflow (confirmed via real testing, not just theory this time). Fixed two ways together: (1) the Fields column now uses field_name(fid, terse=True) same as the v0.16.2 fix, and so do the Conditional/Removed screen summary lines feeding self.other_text (a plain wx.StaticText with NO scrollbar at all -- actually MORE exposed to this bug shape than the ListCtrl was, just not yet reported); (2) SetColumnWidth(6, wx.LIST_AUTOSIZE)'s result is now capped on BOTH ends -- the existing 280px floor (v0.11.1, unchanged) plus a NEW 460px ceiling -- with content past the ceiling relying on the ListCtrl's own native horizontal scroll, not a frame resize. wx.ListCtrl in report mode has no built-in per-cell text wrap (that's a wx.grid.Grid feature, not applied here -- a wider widget swap than this warranted), so capping the column width and shortening the unknown-ID text together is the practical equivalent of "wrap," without the heavier refactor. Prior entry (v0.16.2): Real reported bug fix (2026-08-07): editing a screen with an unresolved/unknown field ID pushed the whole window off the left edge of the screen, with a large empty gap between the field list and the diagram, and the diagram column stretched wider than needed too. Root cause: wx.ListBox reports its own best-size based on the full pixel width of its longest item string; field_name() in its default (non-terse) mode returns long descriptive strings for unknown IDs (e.g. "UNKNOWN (id=58, NEW - not seen before)", ~39 chars) versus normal field names (~10-20 chars). That inflated best-size propagates up through EditScreenPanel's/AddScreenPanel's body_row sizer (both columns share equal HORIZONTAL proportion, which is why the diagram column stretched too, not just the field list), and because MainFrame._relayout() only ever GROWS the window (v0.11.0, deliberately, so a manually-enlarged window wouldn't snap back down on every refresh), the inflated size stuck permanently across every subsequent panel -- exactly matching the reported "expanded screen is retained when I go back." Fixed at the source: fields_list.Set() and the diagram's label-building both now call field_name(fid, terse=True) in EditScreenPanel AND AddScreenPanel (short forms like "id58?" instead of the full descriptive sentence -- AddScreenPanel can't actually hit this today since Add Field/Change Type are FieldPickerDialog-only over the known catalog, fixed there anyway for consistency and as cheap insurance). Also hardened _relayout() itself as defense-in-depth: growth is now clamped to the current display's usable work area (via wx.Display.GetFromWindow(), falling back to the primary display if the frame isn't fully within one), so no FUTURE content-driven best-size spike -- from this bug's category, not just this specific instance -- can ever push the window off-screen/unusable again; at worst some content would be tight/scrolled instead, a recoverable degradation rather than a lockout requiring an app restart. Headless-verified: field_name(58, terse=True) returns "id58?" (5 chars) vs the old ~39-46 char forms; compiled clean. Prior entry (v0.16.1): Two minor UX fixes, no behavioral change. (1) DetectPanel's not-connected message said "Connect your Edge 530 via USB" -- genericized to "Connect your Garmin Edge device via USB" now that Clone/Restore/detection are all already model-agnostic (structure-based detection, no Edge-530-specific logic anywhere in the connection layer) and the toolkit's own analysis (this session) concluded the data_screen mechanism -- field-count + A/B flag only, no stored geometry -- likely generalizes to other Edge models even though the actual caps/LAYOUT_GRIDS would need per-model confirmation before being trusted. (2) MainFrame's window title now includes the running version (f"Garmin Edge Screen Editor v{__version__}") -- previously only visible by opening this file, no in-app way to tell which build was running. Prior entry (v0.16.0): ClonePanel -- "Clone..." on ProfileListPanel, a sibling action to Stage/Restore: patches sport_mesgs[0].name via fit_clone_profile.py's patch_profile_name() (a completely different message than data_screen -- CONFIRMED full-fidelity on real hardware already at the CLI level, see MVP_SCOPE.md "Clone-and-retarget"). Live filename-collision validation against frame.known_profiles (kept fresh by ProfileListPanel.on_refresh() every visit) blocks "Create Clone" until the chosen filename is guaranteed to not match anything currently on the device -- deploying under an existing filename would silently OVERWRITE that profile instead of creating a new one, per fit_clone_profile.py's own docstring warning. Auto-suggests a filename from the display name (alnum-only, matching Garmin's own plain filenames) but never overwrites a filename the user has actually typed into directly. Sources from the selected profile's just-taken backup, never the live device file, same discipline as Stage/Restore. Hands off straight to DeployPanel (steps 9-10) exactly like Restore does -- no staged-vs-editing diff applies to a clone either -- with frame.profile_filename set to the NEW filename (the deploy target) rather than the source's. frame.deploy_return_panel gains a third value ("clone") alongside "review"/"restore", handled identically by DeployPanel's existing context-aware Back button/label and by the same belt-and-suspenders editing_path cleanup pattern RestorePanel already uses. Headless-verified against a real backup file: filename validation (missing extension, path separators, case-insensitive collision) all behave correctly; patch_profile_name() produces a byte-for-byte-structurally-identical clone (same file size, same screens/fields/order, only the name field bytes differ) with the source file itself completely untouched; describe_screen_changes() confirms zero screen differences between source and clone, matching the confirmed real-hardware result. This closes out the GUI's full feature backlog -- see PROJECT_NOTES.md Open Items. Prior entry (v0.15.2): cosmetic doc-only fix: FieldPickerDialog's docstring said "86 confirmed entries" -- stale after fit_dump.py v2.4.3 added field 58 (Lap Timer), bringing FIELD_ID_NAMES to 87. No functional/behavioral change. Prior entry (v0.15.1): fix real bug found via testing (2026-08-06): frame.editing_path was only ever cleared by DeployPanel.on_done(), so backing out of a Restore attempt without completing it (RestorePanel's/DeployPanel's "Back" buttons) left editing_path pointed at the abandoned restore's backup file. Since get_working_path() prefers editing_path over staged_path, a subsequent normal Stage on a profile then silently showed/would-have-edited that stale leftover instead of what was just staged -- reported symptom: "View Screens shows the backup I was about to restore, not what I just staged," which happened to look plausible in PreflightPanel's diff by coincidence (a stale backup vs. current-device-state diff can look like real intended changes) rather than because anything was actually correct. Fixed in two places: ProfileListPanel.on_stage() now unconditionally discards any prior session's editing_path before staging (the real fix -- a fresh Stage should always start clean, covering this case AND the same latent risk when switching to a different profile mid-session); RestorePanel.on_back() also proactively discards when frame.deploy_return_panel == "restore" (the only site that ever sets it to that), cleaning up immediately rather than leaving it to the next Stage. Prior entry (v0.15.0): RestorePanel -- "Restore from Backup..." on ProfileListPanel now goes somewhere: lists every backup of the selected profile (garmin_device.list_backup_history(), NEW in garmin_device.py v0.11.0, newest first, de-duplicated for identical-content runs) with a quick per-candidate screen-type summary, then hands off straight to DeployPanel (skipping PreflightPanel entirely -- there's no staged-vs-editing diff to review for a restore, the user already picked a specific known backup). DeployPanel/describe_screen_changes() work completely unchanged, since both only care that frame.editing_path points at real .fit bytes, not how it got set -- the backup file is used directly, never copied. DeployPanel's "Back" button is context-aware (frame.deploy_return_panel) so it returns to wherever Deploy was actually reached from ("review" or "restore") instead of always assuming the normal edit flow. Prior entry (v0.14.0): post-write verification (step 10) -- DeployPanel.on_check() now re-pulls the LIVE profile from the device's Sports/ folder the moment reconnect is confirmed, and compares it against editing_path (what was actually sent) via a new module-level describe_screen_changes() -- factored out of PreflightPanel's former _describe_changes() so both panels share one implementation. User-confirmed design (2026-08-06): compare visible/active screens only, no Removed-list bookkeeping -- Garmin's own editor has no un-remove option and neither does this GUI, so the device's known Removed-list wipe on NewFiles import isn't something to report on; describe_screen_changes() already does this for free, since it only ever reports slots ACTIVE (field 1==1) on at least one side, so Removed/Unconfigured-only transitions are invisible to it by construction, no special-casing needed. Runs automatically on reconnect (not a separate manual step) since the device is already confirmed connected at that point. Prior entry (v0.13.0): DeployPanel (step 9) -- write the CRC-verified working copy to NewFiles/, then walk the user through eject and reconnect. User-confirmed design (2026-08-06): no background polling/threading for the remount wait (this app's first would-be background thread, a new failure-mode class) -- reconnect detection is a manual "Check for Reconnected Device" button, one non-blocking find_garmin_root() call per click. Eject is a wx.MessageBox-confirmed diskutil call (garmin_device.py's own eject_device(auto_eject=True) uses a terminal input() prompt, which would hang a GUI handler), reusing garmin_device._volume_mount_point() for the real ejectable target; "I Ejected It Myself" is the always-available fallback. Prior entry (v0.12.0): replace PreflightPanel's raw fit_dump.py-diff-style unified diff with a plain-English, per-screen change summary (_describe_changes()) -- user feedback: the byte-level diff was too technical for the GUI's actual audience (a rider, not a developer); hardcore users who want that level of detail can still use the CLI tools directly. See PreflightPanel's docstring for the full reasoning. Prior entry (v0.11.1): fix ViewScreensPanel's "Fields" column being a fixed 280px width, which silently CLIPPED (not wrapped) any screen's field list wider than ~3-4 short names -- reported bug: a 10-field screen only showed 3 fields + part of the 4th. on_refresh() now calls SetColumnWidth(6, wx.LIST_AUTOSIZE) after populating rows, so the column sizes to its actual widest content (never below the original 280px floor); overflow beyond the window's own width falls to the ListCtrl's native horizontal scrollbar instead of clipping. Prior entry (v0.11.0): fix MainFrame._relayout() to only GROW the window (max of best-size vs current size), never shrink it. Reported bug: manually enlarging the window (e.g. to see more than ~6 rows of the screens list) snapped back to the smaller size the moment any button triggered a refresh, since nearly every handler ends with self.frame._relayout(), which called self.Fit() unconditionally -- Fit() resizes to the sizer's ideal size in BOTH directions, including shrinking. The anti-overlap behavior Fit() was added for in v0.1.1 (growing when content needs more room) is preserved via GetBestSize(); the unwanted shrink is gone. No call sites needed to change -- _relayout() keeps its bare no-arg signature.
"""
gui_app.py -- Garmin Edge 530 Screen Editor GUI.

Covers steps 1-10 of the agreed high-level flow (PROJECT_NOTES.md /
"GUI scoping and implementation"), plus Restore-from-Backup and Clone
Profile as sibling actions to editing (RestorePanel, v0.15.0; ClonePanel,
v0.16.0 -- see MVP_SCOPE.md / "Restore from backup" and
"Clone-and-retarget"). This is the full GUI feature backlog -- nothing
left unscoped as of v0.16.0.
    1. Detect the device, show device info.
    2. List profiles on the device.
    3. Back up all profiles (cheap -- done regardless of which profile
       ends up being edited) and let the user select one, then stage
       it (lineage-tracked) for editing.
    4. Show the staged profile's current screens, read-only, with
       screen-level reordering (Move Up/Move Down on the main list).
    5. Add a brand-new screen (AddScreenPanel, v0.8.0) -- pick fields
       and layout, the tool auto-assigns everything else. CONFIRMED
       working (fit_patch.py v1.12.0, live on-device round-trip,
       2026-08-05) -- no longer an on-device-menu redirect.
    6. Edit a single screen: reorder/add/remove its fields, change its
       A/B layout (with a live visual diagram of the actual on-device
       grid, built from the developer's own text-based Edge 530 layout
       reference -- see PROJECT_NOTES.md / "On-device layout
       geometry"), and toggle Show/Hide (field 12).

    7-8. Review accumulated changes (a plain-English, per-screen
       change summary against the untouched staged file -- see the
       module-level describe_screen_changes(), v0.12.0) and a real CRC
       check, before Deploy is reachable at all (PreflightPanel,
       v0.10.0). See "Editing architecture" below for why this is a
       pure review+verify step rather than an "apply" step -- there's
       no separate pending-changes queue to apply.
    9. Deploy (DeployPanel, v0.13.0): write the working copy to the
       device's NewFiles/ folder, then walk the user through eject and
       manual reconnect (one power-button press, confirmed via real
       device testing -- see DeployPanel's docstring).
    10. Post-write verification (DeployPanel.on_check(), v0.14.0): the
       moment reconnect is confirmed, re-pull the LIVE profile from
       the device and run it through the same describe_screen_changes()
       used in steps 7-8, comparing it against what was actually sent.

Restore-from-Backup (RestorePanel, v0.15.0): reached from
ProfileListPanel's "Restore from Backup..." button, NOT from Stage --
picks a specific backup from that profile's history and hands off
straight to DeployPanel/step 9-10, skipping PreflightPanel (steps 7-8)
entirely, since there's no staged-vs-editing diff to review for a
restore.

Editing architecture (step 6): rather than an abstract in-memory list
of "pending changes" that could drift from real file semantics, the
scratch working copy (MainFrame.editing_path) IS the queue. Every
button click in EditScreenPanel is one real, immediately-applied
fit_patch.py operation (via direct function calls -- patch_screen(),
read_current_field_array(), etc. -- not a subprocess), and the panel
always re-reads the actual resulting bytes afterward via
decode_file()/classify_screens() rather than trusting an in-memory
guess. This is exactly what fit_chain.py already does non-
interactively; here it's just one step at a time, driven by clicks.
editing_path starts as a copy of the staged file the first time ANY
screen is opened for editing, and persists across edits to MULTIPLE
screens within one session (a user can edit screen A, then screen B,
before ever deploying) -- "Discard Edits" on ViewScreensPanel resets
it back to a fresh copy of the staged file.

Editing UX decision: reordering screens/fields is SELECT + Move
Up/Move Down buttons, not drag-and-drop -- "move up" is just "swap
with the row above," which maps directly onto the already-validated
--swap-order/--swap-fields primitives with no new backend logic, and
is far less platform-fiddly than implementing wx drag-and-drop from
scratch. Field count changes and reassigning which fields appear on a
screen go through --fields (which replaces the whole list and derives
count from its length -- both same-count-replace and count-increase
are already validated), fed from a picker over FIELD_ID_NAMES rather
than free-text entry. Every field-array replacement is checked against
fit_patch.py's check_system_screen_guard() (v1.7.0) first -- the same
heuristic the CLI's --fields uses, shared rather than reimplemented,
surfaced here as a confirmation dialog instead of a hard refusal.

Architecture: MainFrame owns a single content area and swaps between
panel instances (DetectPanel, ProfileListPanel, ViewScreensPanel,
EditScreenPanel, ...) as the user moves through the flow, rather than
opening new top-level windows. Frame state (garmin_root, working_dir,
staged_path, profile_filename, editing_path, editing_slot) lives on
MainFrame; panels read/write it through their `frame` reference.

Layout note (carried over from the v0.1.1 fix): wx.StaticText/
wx.ListBox/wx.ListCtrl don't automatically resize their container
when their content changes. Every place that changes what's displayed
calls frame._relayout() -- skipping this was the cause of the
original button/text overlap bug in v0.1.0.

Run with:
    python3 gui_app.py

Requires:
    pip install wxPython --break-system-packages
    pip install garmin-fit-sdk --break-system-packages   (needed now
        that this file imports fit_dump.py directly for step 4 --
        already installed in the developer's .venv per
        PROJECT_NOTES.md)

This file must live alongside garmin_device.py, fit_dump.py,
fit_patch.py, fit_raw_walk.py, fit_crc.py, and fit_clone_profile.py
(plain local imports, no packaging yet -- that's a fine later cleanup,
not needed for this slice).
"""
import json
import os
import platform
import shutil
import struct
import subprocess
from datetime import datetime

import wx

import garmin_device
from fit_dump import (
    decode_file,
    classify_screens,
    field_name,
    active_field_ids,
    FIELD_ID_NAMES,
    screen_type_name,
    NAMED_SCREEN_TYPES,
)
from fit_crc import fit_crc
from fit_clone_profile import patch_profile_name
from fit_patch import (
    patch_screen,
    read_current_field_array,
    read_current_count_and_layout,
    pack_field_count,
    pack_field_id_array,
    pack_layout_variant,
    pack_enabled,
    pack_configured_flag,
    pack_uint8,
    check_system_screen_guard,
    would_hide_last_visible_screen,
    hide_unsupported_screen_type,
    swap_display_order,
    next_available_field9,
    next_available_field10,
    COUNTS_WITH_B_VARIANT,
)


DEVICE_INFO_LABELS = [
    ("manufacturer", "Manufacturer"),
    ("garmin_product", "Product"),
    ("serial_number", "Serial"),
    ("software_version", "Software version"),
]

# Cross-platform fallback default -- only used on a brand-new install
# with no saved config yet (see load_saved_working_dir()/save_working_dir()
# below). Previously hardcoded to a specific Mac path used during this
# project's own manual CLI testing; that broke on any other machine
# (wrong user, wrong OS entirely on Windows) and never got remembered
# across restarts even when changed via the "Change..." button. Now:
# this is just the seed value for a first-ever launch, and whatever the
# user actually picks (default or custom) is persisted from then on.
DEFAULT_WORKING_DIR = os.path.join(os.path.expanduser("~"), "GarminBackups")

# Small JSON sidecar in the user's home directory recording the
# last-used working directory, so it's remembered across app restarts
# without needing a special "is this the very first launch" check --
# just "is there a saved value, and if so use it."
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".garmin_screen_editor_config.json")


def load_saved_working_dir():
    """
    Return the working directory saved from a previous run, or None if
    there's no config file yet (first-ever launch) or it can't be read
    (missing, corrupt, permissions). Never raises -- worst case is
    just falling back to DEFAULT_WORKING_DIR, not a startup failure.
    """
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
    except (OSError, ValueError):
        return None
    wd = config.get("working_dir")
    return wd if isinstance(wd, str) and wd else None


def save_working_dir(path):
    """
    Persist the current working directory choice so the NEXT launch
    remembers it instead of resetting to DEFAULT_WORKING_DIR. Called
    whenever the user picks a directory via "Change...". Best-effort --
    a write failure here (e.g. read-only home directory) shouldn't
    block using the app for the rest of this session, just means the
    choice won't survive a restart.
    """
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump({"working_dir": path}, f, indent=2)
    except OSError:
        pass

# Confirmed via real device testing: a hard cap of 10 fields per
# screen, and 10 USER-definable screens per profile (additional
# Garmin-predefined/overlay screens are allowed beyond that and don't
# count against the 10 -- consistent with the "Conditional" screen
# state and the pre-Removed factory-shipped screens documented in
# PROJECT_NOTES.md / SCREEN STATE MODEL).
MAX_FIELDS_PER_SCREEN = 10
MAX_USER_SCREENS = 10

# On-device grid geometry, per field count and layout variant --
# which field positions (0-based) stack vertically (each its own row)
# vs. sit side-by-side (grouped in the same row list). Supplied
# directly from the developer's own text-based Edge 530 layout
# reference; cross-checked against fit_patch.py's COUNTS_WITH_B_VARIANT
# (3/4/5/6/7 have a real A/B choice) -- matches exactly, no
# discrepancies. Counts 3 A vs B are visually the SAME row structure on
# this reference (B just renders the top field smaller) -- that size
# difference isn't representable by row/column grouping alone, so it's
# noted in a comment rather than faked into the geometry.
LAYOUT_GRIDS = {
    1: {0: [[0]]},
    2: {0: [[0], [1]]},
    3: {
        0: [[0], [1], [2]],  # "A" -- equal sized fields
        1: [[0], [1], [2]],  # "B" -- same rows; on-device the TOP field renders smaller
    },
    4: {
        0: [[0], [1], [2], [3]],
        1: [[0, 1], [2], [3]],
    },
    5: {
        0: [[0], [1], [2], [3], [4]],
        1: [[0], [1], [2, 3], [4]],
    },
    6: {
        0: [[0], [1], [2], [3], [4, 5]],
        1: [[0, 1], [2], [3], [4, 5]],
    },
    7: {
        0: [[0], [1], [2], [3, 4], [5, 6]],
        1: [[0, 1], [2], [3, 4], [5, 6]],
    },
    8: {0: [[0], [1], [2, 3], [4, 5], [6, 7]]},
    9: {0: [[0], [1, 2], [3, 4], [5, 6], [7, 8]]},
    10: {0: [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]},
}


ABOUT_TEXT = """Activity Profile Screen Editor for Garmin Edge
Version {version}

An independent, unofficial toolkit for viewing and editing Garmin Edge \
Activity Profile screen layouts (fields, order, and A/B layout) from a \
computer, without the on-device menu.

This project is not affiliated with, endorsed by, or sponsored by \
Garmin Ltd. or its subsidiaries. "Garmin" and "Edge" are trademarks of \
Garmin Ltd., used here only to describe device compatibility.

The undocumented data_screen message this toolkit relies on was \
reverse-engineered entirely through black-box observation -- making \
isolated changes on a real device and diffing the resulting files -- \
never by reverse-engineering Garmin's own software or SDK.

Licensed under the MIT License -- see the LICENSE file for the full \
text. No warranty of any kind is provided; this tool patches \
undocumented file structures and writes to your device through an \
undocumented pathway. Use at your own risk. See README.md for the \
full disclaimer."""


class AboutDialog(wx.Dialog):
    """
    A short "About" summary (name, version, trademark disclaimer,
    reverse-engineering method, license) reachable from DetectPanel --
    added ahead of a possible public GitHub release so this information
    is visible in-app, not just in LICENSE/README.md for anyone who
    happens to read the repo. Deliberately a SHORT summary that points
    to LICENSE/README.md for the full text, not an attempt to embed the
    entire legal text verbatim in a dialog -- the standard pattern for
    an About box, and it sidesteps ever needing this dialog's wording
    to track README.md's disclaimer word-for-word.

    Uses a read-only, word-wrapped wx.TextCtrl for the body rather than
    a plain wx.StaticText -- this is a modal dialog with its own fixed
    size, not embedded in MainFrame's resizable sizer tree, so it can't
    reproduce the v0.16.2/v0.16.3/v0.16.6 best-size-propagation bugs
    either way, but wrapping is still the right call for a paragraph
    this long regardless of that.
    """

    def __init__(self, parent):
        super().__init__(parent, title="About", size=(480, 420))

        outer = wx.BoxSizer(wx.VERTICAL)

        body = wx.TextCtrl(
            self,
            value=ABOUT_TEXT.format(version=__version__),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.BORDER_NONE,
        )
        body.SetBackgroundColour(self.GetBackgroundColour())
        outer.Add(body, 1, wx.ALL | wx.EXPAND, 12)

        close_btn = wx.Button(self, wx.ID_CLOSE, label="Close")
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CLOSE))
        outer.Add(close_btn, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 12)

        self.SetSizer(outer)
        self.SetEscapeId(wx.ID_CLOSE)


class DetectPanel(wx.Panel):
    """Step 1: detect the device, show device info."""

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame

        outer = wx.BoxSizer(wx.VERTICAL)

        self.status_text = wx.StaticText(self, label="Not checked yet.")
        status_font = self.status_text.GetFont()
        status_font.PointSize += 2
        status_font = status_font.Bold()
        self.status_text.SetFont(status_font)
        outer.Add(self.status_text, 0, wx.ALL | wx.EXPAND, 12)

        self.info_text = wx.StaticText(self, label="")
        outer.Add(self.info_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)

        self.detect_btn = wx.Button(self, label="Detect Garmin")
        self.detect_btn.Bind(wx.EVT_BUTTON, self.on_detect)
        button_row.Add(self.detect_btn, 0, wx.RIGHT, 8)

        self.next_btn = wx.Button(self, label="List Profiles →")
        self.next_btn.Disable()
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        button_row.Add(self.next_btn, 0, wx.RIGHT, 8)

        self.about_btn = wx.Button(self, label="About")
        self.about_btn.Bind(wx.EVT_BUTTON, self.on_about)
        button_row.Add(self.about_btn, 0)

        outer.Add(button_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.SetSizer(outer)

    def on_about(self, event):
        dlg = AboutDialog(self)
        dlg.ShowModal()
        dlg.Destroy()

    def on_show(self):
        """Called by MainFrame every time this panel becomes active."""
        self.on_detect(None)

    def on_detect(self, event):
        self.frame.SetStatusText("Checking for a connected Garmin...")

        try:
            root = garmin_device.find_garmin_root()
        except garmin_device.GarminDeviceError as e:
            # e.g. unsupported platform -- surfaced exactly as
            # garmin_device.py itself would report it, no GUI-side
            # reinterpretation of the error.
            self.status_text.SetLabel("Detection error")
            self.info_text.SetLabel(str(e))
            self.next_btn.Disable()
            self.frame.SetStatusText("Error.")
            self.frame._relayout()
            return

        self.frame.garmin_root = root

        if root is None:
            self.status_text.SetLabel("No Garmin device connected.")
            self.info_text.SetLabel(
                "Connect your Garmin Edge device via USB, then click Detect Garmin again."
            )
            self.next_btn.Disable()
            self.frame.SetStatusText("Not connected.")
            self.frame._relayout()
            return

        self.status_text.SetLabel(f"Garmin connected at {root}")

        info = garmin_device.get_device_info(root)
        if info is None:
            self.info_text.SetLabel(
                "(No Device.fit found -- device info unavailable, but the "
                "Sports/NewFiles structure was found, so profile access "
                "should still work.)"
            )
        else:
            lines = [
                f"{label}: {info[key]}"
                for key, label in DEVICE_INFO_LABELS
                if key in info
            ]
            self.info_text.SetLabel(
                "\n".join(lines) if lines else "(no device info fields present)"
            )

        self.next_btn.Enable()
        self.frame.SetStatusText("Connected.")
        self.frame._relayout()

    def on_next(self, event):
        self.frame.show_panel("profiles")


class ProfileListPanel(wx.Panel):
    """
    Steps 2+3: list profiles on the device, back all of them up (cheap,
    done unconditionally regardless of which one gets edited -- see
    PROJECT_NOTES.md / "GUI scoping and implementation"), and let the
    user select one to stage for editing.

    Backup and listing are the SAME call here: garmin_device.
    backup_profiles() already enumerates every profile in Sports/ (via
    its own internal list_profiles() call) in order to back each one
    up, and returns {filename: backup_path} -- so the profile list
    shown to the user is just that dict's keys, rather than making a
    second, redundant directory listing.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.backup_paths = {}   # filename -> backup path, from the last backup_profiles() call
        self.staged_path = None  # set once the selected profile has been staged

        outer = wx.BoxSizer(wx.VERTICAL)

        # Working directory row
        wd_row = wx.BoxSizer(wx.HORIZONTAL)
        wd_row.Add(wx.StaticText(self, label="Working directory:"), 0,
                   wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.wd_text = wx.StaticText(self, label=self.frame.working_dir)
        wd_row.Add(self.wd_text, 1, wx.ALIGN_CENTER_VERTICAL)
        change_wd_btn = wx.Button(self, label="Change...")
        change_wd_btn.Bind(wx.EVT_BUTTON, self.on_change_working_dir)
        wd_row.Add(change_wd_btn, 0, wx.LEFT, 6)
        outer.Add(wd_row, 0, wx.ALL | wx.EXPAND, 12)

        self.status_text = wx.StaticText(self, label="")
        outer.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.profile_list = wx.ListBox(self, style=wx.LB_SINGLE)
        self.profile_list.Bind(wx.EVT_LISTBOX, self.on_profile_selected)
        outer.Add(self.profile_list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.selection_text = wx.StaticText(self, label="")
        outer.Add(self.selection_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)

        back_btn = wx.Button(self, label="‹ Back")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)

        refresh_btn = wx.Button(self, label="Refresh (re-backup + re-list)")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        button_row.Add(refresh_btn, 0, wx.RIGHT, 8)

        self.stage_btn = wx.Button(self, label="Stage Selected for Edit")
        self.stage_btn.Disable()
        self.stage_btn.Bind(wx.EVT_BUTTON, self.on_stage)
        button_row.Add(self.stage_btn, 0, wx.RIGHT, 8)

        self.restore_btn = wx.Button(self, label="Restore from Backup...")
        self.restore_btn.Disable()
        self.restore_btn.Bind(wx.EVT_BUTTON, self.on_restore)
        button_row.Add(self.restore_btn, 0, wx.RIGHT, 8)

        self.clone_btn = wx.Button(self, label="Clone...")
        self.clone_btn.Disable()
        self.clone_btn.Bind(wx.EVT_BUTTON, self.on_clone)
        button_row.Add(self.clone_btn, 0, wx.RIGHT, 8)

        self.next_btn = wx.Button(self, label="View Screens →")
        self.next_btn.Disable()
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        button_row.Add(self.next_btn, 0)

        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active."""
        self.staged_path = None
        self.next_btn.Disable()
        self.on_refresh(None)

    def on_change_working_dir(self, event):
        dlg = wx.DirDialog(self, "Choose a working directory for backups and staged edits",
                            defaultPath=self.frame.working_dir)
        if dlg.ShowModal() == wx.ID_OK:
            self.frame.working_dir = dlg.GetPath()
            save_working_dir(self.frame.working_dir)
            self.wd_text.SetLabel(self.frame.working_dir)
            self.frame._relayout()
        dlg.Destroy()

    def on_refresh(self, event):
        root = self.frame.garmin_root
        if root is None:
            self.status_text.SetLabel(
                "No device connected -- go Back and click Detect Garmin first."
            )
            self.profile_list.Clear()
            self.backup_paths = {}
            self.frame.known_profiles = {}
            self.stage_btn.Disable()
            self.restore_btn.Disable()
            self.clone_btn.Disable()
            self.frame._relayout()
            return

        try:
            self.backup_paths = garmin_device.backup_profiles(root, self.frame.working_dir)
        except OSError as e:
            self.status_text.SetLabel(
                f"Backup failed: {e} -- is the device still connected?"
            )
            self.profile_list.Clear()
            self.backup_paths = {}
            self.frame.known_profiles = {}
            self.stage_btn.Disable()
            self.restore_btn.Disable()
            self.clone_btn.Disable()
            self.frame._relayout()
            return

        # Promoted to frame level so ClonePanel can validate a new
        # filename against what's CURRENTLY on the device without
        # ProfileListPanel needing to be involved directly -- same
        # pattern as staged_path/profile_filename. Cloning under a
        # filename that collides with an existing profile silently
        # OVERWRITES that profile instead of creating a new one (see
        # fit_clone_profile.py's own docstring and MVP_SCOPE.md /
        # "Clone-and-retarget"), so this needs to always reflect the
        # most recent backup_profiles() call, not go stale.
        self.frame.known_profiles = dict(self.backup_paths)

        profiles = sorted(self.backup_paths.keys())
        self.profile_list.Set(profiles)
        self.selection_text.SetLabel("")
        self.stage_btn.Disable()
        self.restore_btn.Disable()
        self.clone_btn.Disable()

        if profiles:
            self.status_text.SetLabel(
                f"Backed up {len(profiles)} profile(s) to {self.frame.working_dir}. "
                f"Select one below."
            )
        else:
            self.status_text.SetLabel("No profiles found in Sports/ on this device.")

        self.frame._relayout()

    def on_profile_selected(self, event):
        selection = self.profile_list.GetStringSelection()
        self.selection_text.SetLabel(f"Selected: {selection}" if selection else "")
        self.stage_btn.Enable(bool(selection))
        self.restore_btn.Enable(bool(selection))
        self.clone_btn.Enable(bool(selection))
        self.frame._relayout()

    def on_stage(self, event):
        profile_filename = self.profile_list.GetStringSelection()
        if not profile_filename:
            return
        backup_path = self.backup_paths.get(profile_filename)
        if backup_path is None:
            wx.MessageBox(
                f"No backup on file for {profile_filename} -- click Refresh and try again.",
                "Can't stage", wx.OK | wx.ICON_ERROR,
            )
            return

        try:
            self.staged_path = garmin_device.stage_for_edit(
                profile_filename, backup_path, self.frame.working_dir
            )
        except OSError as e:
            wx.MessageBox(f"Staging failed: {e}", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Real bug found via testing (2026-08-06): frame.editing_path
        # is only ever cleared by DeployPanel.on_done() -- but a user
        # can back out of Restore/Deploy without ever reaching Done
        # (RestorePanel's/DeployPanel's "Back" buttons), leaving
        # editing_path pointed at whatever backup file Restore was
        # about to write. Since get_working_path() prefers
        # editing_path over staged_path, a fresh Stage right after
        # would silently show/operate on that stale leftover instead
        # of the profile just staged -- observed as "View Screens
        # shows the backup I was about to restore, not what I just
        # staged." A fresh Stage is always meant to start a clean
        # session (its own label says so), so discard any prior
        # session's scratch copy unconditionally here -- covers this
        # exact case AND the same latent risk when staging a
        # DIFFERENT profile while a previous one's edits were still
        # sitting in editing_path.
        self.frame.discard_edits()

        # Promote to frame-level state so ViewScreensPanel (and later
        # panels) can get at the staged file without ProfileListPanel
        # needing to be involved directly.
        self.frame.staged_path = self.staged_path
        self.frame.profile_filename = profile_filename

        self.selection_text.SetLabel(
            f"Selected: {profile_filename}\nStaged: {self.staged_path}"
        )
        self.next_btn.Enable()
        self.frame._relayout()

    def on_restore(self, event):
        profile_filename = self.profile_list.GetStringSelection()
        if not profile_filename:
            return
        # Restore doesn't go through Stage -- it's a separate path
        # straight to a backup-history picker. profile_filename still
        # needs to be set at frame level, though: DeployPanel and the
        # post-write verification both key off it, same as the normal
        # edit flow.
        self.frame.profile_filename = profile_filename
        self.frame.show_panel("restore")

    def on_clone(self, event):
        profile_filename = self.profile_list.GetStringSelection()
        if not profile_filename:
            return
        backup_path = self.backup_paths.get(profile_filename)
        if backup_path is None:
            wx.MessageBox(
                f"No backup on file for {profile_filename} -- click Refresh and try again.",
                "Can't clone", wx.OK | wx.ICON_ERROR,
            )
            return
        # Clone, like Restore, doesn't go through Stage -- ClonePanel
        # sources directly from the just-taken backup of the SELECTED
        # (source) profile. frame.profile_filename is deliberately NOT
        # set here -- ClonePanel sets it later, to the NEW filename the
        # user chooses, once Create Clone actually runs (DeployPanel
        # and post-write verification both key off frame.profile_filename
        # as the DEPLOY TARGET, which for a clone is the new name, not
        # the source's).
        self.frame.clone_source_filename = profile_filename
        self.frame.clone_source_backup_path = backup_path
        self.frame.show_panel("clone")

    def on_back(self, event):
        self.frame.show_panel("detect")

    def on_next(self, event):
        self.frame.show_panel("screens")


# v0.16.6 FIX (real reported bug, 2026-08-10): a plain wx.ListCtrl's
# DoGetBestSize() reflects its actual current column widths -- so any
# time the Fields column (below) auto-sizes wide to fit real content,
# that width propagates straight up through ViewScreensPanel's sizer
# into MainFrame._relayout()'s frame-growth calculation. v0.16.3 tried
# to prevent that by CAPPING the column's width at 460px -- which
# stopped the frame from growing, but broke something else instead:
# wx.ListCtrl clips a cell's text to its column's pixel width with no
# wrap and no ellipsis, and the control's own horizontal scrollbar only
# engages when the SUM of ALL column widths exceeds the control's own
# rendered area -- a single capped-width column mostly never triggers
# that. Net effect of the v0.16.3 "fix": text silently truncated
# mid-character instead of the window growing -- confirmed via real
# testing on a 10-field screen with several of the newly-added longer
# field names, only 6-7 names visible, no way to see the rest. The
# v0.16.3 comment's "content past the ceiling relies on the ListCtrl's
# own native horizontal scroll" claim was simply wrong, in the same
# spirit as the v0.11.1 comment that started this whole saga -- an
# unverified assumption about this exact widget's real-world behavior,
# the second one in three days (see PROJECT_NOTES.md "Corrections and
# lessons learned").
#
# Correct fix: stop trying to control the FRAME's size by capping the
# COLUMN's width -- decouple the two instead. This subclass overrides
# DoGetBestSize() to clamp only the WIDTH wx's sizer system sees,
# regardless of actual column content; HEIGHT still comes from the
# normal wx.ListCtrl calculation (untouched), preserving the original
# v0.11.0 "grow taller when more room is needed" behavior. With the
# frame's size no longer tied to column content at all, the Fields
# column is free to auto-size to its FULL real content again (reverted
# to a floor-only 280px minimum, no ceiling -- see on_refresh()) --
# and NOW, when that's genuinely wider than the space actually
# available, the ListCtrl's real native horizontal scrollbar engages
# for real, because the scenario it's designed for -- assigned render
# area smaller than content -- is finally the true state of affairs,
# rather than being masked by a frame that always grows to match.
class ScreensListCtrl(wx.ListCtrl):
    """wx.ListCtrl whose reported best-size WIDTH is capped, independent
    of actual column content -- see the fix note directly above."""

    MAX_BEST_WIDTH = 760

    def DoGetBestSize(self):
        best = super().DoGetBestSize()
        return wx.Size(min(best.width, self.MAX_BEST_WIDTH), best.height)


class ViewScreensPanel(wx.Panel):
    """
    Step 4: show the staged profile's current screens, read-only. All
    data comes from fit_dump.py's classify_screens()/active_field_ids()/
    field_name()/screen_type_name() -- the exact functions extracted
    specifically so this panel could import and call them directly,
    with no subprocess call and no CLI text to parse. The Type column
    (v0.6.0) shows the real, CONFIRMED f10-derived screen name (Map,
    Compass, "Screen N", etc.) -- see PROJECT_NOTES.md "Screen identity
    — SOLVED".

    The main list (reorderable/Active screens) is a wx.ListCtrl in
    report mode. Conditional and Removed screens are shown underneath
    as plain read-only text, since editing them is out of MVP scope
    (see MVP_SCOPE.md) -- no reason to give them an interactive list
    they'll never need.

    v0.7.0: Move Up/Move Down buttons act on whichever row is selected
    in the main list, swapping that screen's on-device DISPLAY ORDER
    with its neighbor via fit_patch.py's swap_display_order() (the
    same function backing --swap-order, already validated on real
    hardware). This is a screen-level reorder -- it swaps f9 between
    two slots, touching nothing about either screen's own content,
    layout, or field list. Uses the same "first edit creates the
    scratch copy" pattern as EditScreenPanel: if this is the first
    change made in the session, frame.editing_path is created from the
    staged file before writing.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.row_slots = []  # row index (in screens_list) -> message_index (slot)

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.edits_note = wx.StaticText(self, label="")
        outer.Add(self.edits_note, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        outer.Add(wx.StaticText(self, label="Screen order as viewed on-device "
                                              "(reorderable) -- select a row, then "
                                              "Edit Selected Screen:"),
                  0, wx.LEFT | wx.RIGHT, 12)

        self.screens_list = ScreensListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.screens_list.InsertColumn(0, "Pos", width=40)
        self.screens_list.InsertColumn(1, "Slot", width=45)
        self.screens_list.InsertColumn(2, "Count", width=55)
        self.screens_list.InsertColumn(3, "Layout", width=60)
        self.screens_list.InsertColumn(4, "Flag", width=45)
        self.screens_list.InsertColumn(5, "Type", width=110)
        self.screens_list.InsertColumn(6, "Fields", width=280)
        self.screens_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_row_selected)
        self.screens_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_row_deselected)
        outer.Add(self.screens_list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.other_text = wx.StaticText(self, label="")
        outer.Add(self.other_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)

        back_btn = wx.Button(self, label="‹ Back")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)

        refresh_btn = wx.Button(self, label="Re-read File")
        refresh_btn.Bind(wx.EVT_BUTTON, self.on_refresh)
        button_row.Add(refresh_btn, 0, wx.RIGHT, 8)

        self.discard_btn = wx.Button(self, label="Discard Edits")
        self.discard_btn.Bind(wx.EVT_BUTTON, self.on_discard)
        button_row.Add(self.discard_btn, 0, wx.RIGHT, 8)

        # Screen-level reordering (v0.7.0) -- select + Move Up/Down,
        # same UX decision as EditScreenPanel's field reordering, mapped
        # onto swap_display_order() (--swap-order's backend) instead of
        # the field-array swap. Enabled state depends on WHICH row is
        # selected, not just whether one is -- see on_row_selected().
        self.move_up_btn = wx.Button(self, label="▲ Move Up")
        self.move_up_btn.Disable()
        self.move_up_btn.Bind(wx.EVT_BUTTON, self.on_move_up)
        button_row.Add(self.move_up_btn, 0, wx.RIGHT, 8)

        self.move_down_btn = wx.Button(self, label="▼ Move Down")
        self.move_down_btn.Disable()
        self.move_down_btn.Bind(wx.EVT_BUTTON, self.on_move_down)
        button_row.Add(self.move_down_btn, 0, wx.RIGHT, 8)

        # Add-New-Screen (v0.8.0) -- CONFIRMED working at the
        # fit_patch.py level (v1.12.0, see PROJECT_NOTES.md "Adding a
        # new screen"). Enabled whenever a profile is staged -- unlike
        # Edit/Move Up/Down, it doesn't need a row selected, since it's
        # creating a screen rather than acting on an existing one.
        self.add_screen_btn = wx.Button(self, label="+ Add New Screen...")
        self.add_screen_btn.Disable()
        self.add_screen_btn.Bind(wx.EVT_BUTTON, self.on_add_screen)
        button_row.Add(self.add_screen_btn, 0, wx.RIGHT, 8)

        self.edit_btn = wx.Button(self, label="Edit Selected Screen →")
        self.edit_btn.Disable()
        self.edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        button_row.Add(self.edit_btn, 0, wx.RIGHT, 8)

        # Steps 7+8 (v1.0.0) -- enabled whenever there's something
        # accumulated to review (frame.editing_path is not None),
        # independent of whatever row happens to be selected.
        self.review_btn = wx.Button(self, label="Review && Deploy...")
        self.review_btn.Disable()
        self.review_btn.Bind(wx.EVT_BUTTON, self.on_review)
        button_row.Add(self.review_btn, 0)

        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active."""
        self.on_refresh(None)

    def on_refresh(self, event):
        # Independent of working_path/decode success below -- this only
        # cares whether anything has been accumulated to review yet.
        self.review_btn.Enable(self.frame.editing_path is not None)

        working_path = self.frame.get_working_path()
        if working_path is None:
            self.title_text.SetLabel("No profile staged yet.")
            self.edits_note.SetLabel("")
            self.other_text.SetLabel(
                "Go Back to the profile list and stage one for editing first."
            )
            self.screens_list.DeleteAllItems()
            self.row_slots = []
            self.edit_btn.Disable()
            self.move_up_btn.Disable()
            self.move_down_btn.Disable()
            self.add_screen_btn.Disable()
            self.frame._relayout()
            return

        self.title_text.SetLabel(f"{self.frame.profile_filename}  —  {working_path}")

        if self.frame.editing_path is not None:
            self.edits_note.SetLabel(
                "Showing accumulated edits from this session -- NOT yet deployed to "
                "the device. Click Discard Edits to go back to the untouched staged file."
            )
            self.discard_btn.Enable()
        else:
            self.edits_note.SetLabel("Showing the untouched staged file -- no edits yet.")
            self.discard_btn.Disable()

        try:
            messages = decode_file(working_path)
        except Exception as e:
            self.other_text.SetLabel(f"Failed to read file: {e}")
            self.screens_list.DeleteAllItems()
            self.row_slots = []
            self.edit_btn.Disable()
            self.move_up_btn.Disable()
            self.move_down_btn.Disable()
            self.add_screen_btn.Disable()
            self.frame._relayout()
            return

        data = classify_screens(messages)

        self.screens_list.DeleteAllItems()
        self.row_slots = []
        for position, (f9, idx, m) in enumerate(data["orderable"], start=1):
            # v0.6.0: field_count can genuinely be None (Virtual
            # Partner-style screens have no f3 key at all) -- default to
            # 0 for display, same fix as fit_dump.py v2.3.0.
            field_count = m.get(3) or 0
            active_ids = active_field_ids(m, field_count)
            # v0.16.3 FIX: terse=True -- see the SetColumnWidth() note
            # below for why. A screen with several unresolved field IDs
            # (the full non-terse form is ~40 chars EACH, e.g. "UNKNOWN
            # (id=58, NEW - not seen before)") could make this one cell
            # a 300+ char string even after this fix cuts each unknown
            # ID down to ~"id58?" (~6 chars).
            names = ", ".join(field_name(fid, terse=True) for fid in active_ids)

            layout_variant = m.get(8)
            if layout_variant == 1:
                layout_col = "B"
            elif layout_variant == 0:
                layout_col = "A"
            else:
                layout_col = "-"

            flag = "OFF" if m.get(12) == 1 else ""

            # v0.6.0: real screen-type name from f10 (CONFIRMED -- see
            # fit_dump.py's NAMED_SCREEN_TYPES) -- "Map"/"Compass"/etc.
            # for named Garmin types, "Screen N" for plain user screens.
            type_name = screen_type_name(m.get(10)) or "?"

            row = self.screens_list.InsertItem(self.screens_list.GetItemCount(), str(position))
            self.screens_list.SetItem(row, 1, str(idx))
            self.screens_list.SetItem(row, 2, str(field_count))
            self.screens_list.SetItem(row, 3, layout_col)
            self.screens_list.SetItem(row, 4, flag)
            self.screens_list.SetItem(row, 5, type_name)
            self.screens_list.SetItem(row, 6, names)
            self.row_slots.append(idx)

        # v0.11.1: the Fields column was a fixed 280px, which clipped
        # (not wrapped) any comma-joined field list wider than ~3-4
        # short names -- reported bug: a 10-field screen only showed
        # the first 3 fields and part of the 4th, with no way to see
        # the rest. Auto-size it to the actual widest cell content on
        # every refresh instead.
        #
        # v0.16.3 (SUPERSEDED by v0.16.6, see below): tried capping
        # AUTOSIZE's result at a 460px ceiling to stop the column's
        # width from inflating the FRAME's size. That stopped the frame
        # from growing, but silently broke something else instead --
        # see ScreensListCtrl's fix note above ViewScreensPanel for the
        # full story. Reverted here.
        #
        # v0.16.6 FIX (real reported bug, 2026-08-10): back to floor-
        # only AUTOSIZE (never below 280px, no ceiling) -- safe again
        # now that self.screens_list is a ScreensListCtrl, whose
        # DoGetBestSize() caps the WIDTH the frame ever sees independent
        # of this column's actual width. The column is free to be as
        # wide as real content needs; when that's wider than the space
        # actually available, the ListCtrl's real native horizontal
        # scrollbar engages -- for real this time, since the mismatch
        # between assigned render area and content width is now the
        # true state of affairs instead of being masked by a frame that
        # always grows to match.
        self.screens_list.SetColumnWidth(6, wx.LIST_AUTOSIZE)
        if self.screens_list.GetColumnWidth(6) < 280:
            self.screens_list.SetColumnWidth(6, 280)

        self.edit_btn.Disable()
        self.move_up_btn.Disable()
        self.move_down_btn.Disable()
        self.add_screen_btn.Enable()  # doesn't need a row selected, unlike the others

        other_lines = []
        if data["conditional"]:
            other_lines.append(
                f"Conditional screens (active, exempt from ordering — e.g. "
                f"GroupTrack): {len(data['conditional'])}"
            )
            for idx, m in data["conditional"]:
                field_count = m.get(3) or 0
                # v0.16.3 FIX: terse=True -- same reasoning as the Fields
                # column above. self.other_text is a plain wx.StaticText
                # with no wrapping and no scrollbar of its own, so a long
                # unwrapped line here is actually MORE exposed to this
                # bug category than the ListCtrl column was, not less.
                names = ", ".join(field_name(fid, terse=True) for fid in active_field_ids(m, field_count))
                type_name = screen_type_name(m.get(10)) or "?"
                other_lines.append(f"    slot {idx} ({type_name}): {names}")
        if data["removed"]:
            other_lines.append(
                f"Removed screens (content preserved, not shown on-device): "
                f"{len(data['removed'])}"
            )
            for idx, m in data["removed"]:
                field_count = m.get(3) or 0
                names = ", ".join(field_name(fid, terse=True) for fid in active_field_ids(m, field_count))
                other_lines.append(f"    slot {idx}: {names}")
        if data["unknown_ids_seen"]:
            other_lines.append(
                f"Unknown field IDs on this file: {sorted(data['unknown_ids_seen'])}"
            )
        self.other_text.SetLabel("\n".join(other_lines))

        self.frame._relayout()

    def on_row_selected(self, event):
        self.edit_btn.Enable()
        self._update_move_buttons()

    def on_row_deselected(self, event):
        self.edit_btn.Disable()
        self.move_up_btn.Disable()
        self.move_down_btn.Disable()

    def _update_move_buttons(self):
        """
        Move Up/Down enabled state depends on WHERE the selected row is,
        not just whether one is selected -- top row can't move up,
        bottom row can't move down. Called after selection changes and
        after every reorder (the selection follows the moved row, so
        this needs re-evaluating at the new position too).
        """
        sel = self.screens_list.GetFirstSelected()
        if sel == -1:
            self.move_up_btn.Disable()
            self.move_down_btn.Disable()
            return
        self.move_up_btn.Enable(sel > 0)
        self.move_down_btn.Enable(sel < len(self.row_slots) - 1)

    def on_move_up(self, event):
        sel = self.screens_list.GetFirstSelected()
        if sel <= 0:
            return
        self._swap_screen_order(sel - 1, sel)
        self._reselect_row(sel - 1)

    def on_move_down(self, event):
        sel = self.screens_list.GetFirstSelected()
        if sel == -1 or sel >= len(self.row_slots) - 1:
            return
        self._swap_screen_order(sel, sel + 1)
        self._reselect_row(sel + 1)

    def _swap_screen_order(self, row_a, row_b):
        """
        Swap the on-device display order of the screens currently shown
        at list rows row_a/row_b, via fit_patch.py's
        swap_display_order() -- the exact function backing --swap-order,
        already validated on real hardware. Only touches f9 on the two
        target slots; field count/content/layout are untouched.

        Same "first edit creates the scratch copy" pattern as
        EditScreenPanel.on_edit(): if no screen in this session has been
        edited yet, frame.editing_path is still None, so this creates it
        from the staged file before writing -- the staged file itself is
        never touched directly.
        """
        slot_a = self.row_slots[row_a]
        slot_b = self.row_slots[row_b]

        if self.frame.editing_path is None:
            source = self.frame.staged_path
            self.frame.editing_path = source + ".editing.fit"
            shutil.copy2(source, self.frame.editing_path)

        swap_display_order(self.frame.editing_path, self.frame.editing_path, slot_a, slot_b)
        self.on_refresh(None)

    def _reselect_row(self, row):
        """
        After on_refresh() rebuilds screens_list from scratch (losing
        selection), re-select the row the just-moved screen ended up
        at, so a user can click Move Up/Down repeatedly without having
        to re-click the row each time.
        """
        if 0 <= row < self.screens_list.GetItemCount():
            self.screens_list.Select(row)
            self.screens_list.Focus(row)
            self.screens_list.EnsureVisible(row)
            self.edit_btn.Enable()
        self._update_move_buttons()

    def on_discard(self, event):
        self.frame.discard_edits()
        self.on_refresh(None)

    def on_add_screen(self, event):
        self.frame.show_panel("add_screen")

    def on_review(self, event):
        self.frame.show_panel("review")

    def on_back(self, event):
        self.frame.show_panel("profiles")

    def on_edit(self, event):
        selected_row = self.screens_list.GetFirstSelected()
        if selected_row == -1:
            return
        slot = self.row_slots[selected_row]

        # First edit of this session: create the scratch working copy
        # now, from whatever get_working_path() currently is (staged
        # file, or an already-edited copy from a PRIOR screen this
        # same session -- edits accumulate across multiple screens).
        if self.frame.editing_path is None:
            source = self.frame.staged_path
            self.frame.editing_path = source + ".editing.fit"
            shutil.copy2(source, self.frame.editing_path)

        self.frame.editing_slot = slot
        self.frame.show_panel("edit_screen")


class LayoutDiagramPanel(wx.Panel):
    """
    Draws a simple box diagram of a screen's on-device layout -- which
    field positions stack vertically (each its own full-width row) vs.
    sit side-by-side, per LAYOUT_GRIDS. Purely a read-only preview;
    all actual editing happens through the field list and its buttons
    in EditScreenPanel, not by interacting with this diagram directly.
    """

    def __init__(self, parent):
        super().__init__(parent, style=wx.BORDER_SIMPLE)
        # v0.16.4 FIX: bumped from (280, 220) -- real reported feedback
        # (with a side-by-side screenshot) that the cell-label font was
        # much smaller than the rest of the window's text, hard to read.
        # Safe to just make the font bigger with NO knock-on width/height
        # risk -- unlike the wx.ListBox/wx.ListCtrl bugs fixed in
        # v0.16.2/v0.16.3, this panel's size is this fixed SetMinSize()
        # call and nothing else; it's custom-painted with an explicit
        # per-cell clipping region in on_paint(), so font size and label
        # length never feed back into the panel's own reported best-size
        # the way ListBox/ListCtrl content does. Bumped the floor here
        # too, though, so the bigger font has more breathing room in the
        # smallest cells (8-10 field layouts, the most rows/cells) before
        # clipping becomes an issue -- purely a fixed-size adjustment,
        # same "safe" category as the font change itself.
        self.SetMinSize((340, 280))
        self.SetBackgroundColour(wx.WHITE)
        self.grid_rows = []      # list of rows, each a list of 0-based field positions
        self.field_labels = []   # field_labels[i] = display name for position i
        self.note = ""
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

    def on_size(self, event):
        # v0.4.1 fix: a stray EVT_SIZE can fire during window teardown,
        # after the top-level frame has started being destroyed but
        # before this panel object is fully gone. Calling Refresh() at
        # that point tries to compute screen coordinates relative to a
        # top-level window that no longer exists, which crashes the
        # whole app with wx._core.wxAssertionError ("TopLevel Window
        # missing") right as MainLoop() exits -- confirmed via a real
        # run: no visible glitch during use, only a traceback in the
        # terminal after the window had already closed. IsBeingDeleted()
        # is the standard guard for exactly this class of teardown-race
        # issue.
        event.Skip()
        if not self.IsBeingDeleted():
            self.Refresh()

    def set_layout(self, grid_rows, field_labels, note=""):
        self.grid_rows = grid_rows
        self.field_labels = field_labels
        self.note = note
        if not self.IsBeingDeleted():
            self.Refresh()

    def on_paint(self, event):
        if self.IsBeingDeleted():
            return
        dc = wx.PaintDC(self)
        dc.Clear()
        width, height = self.GetClientSize()
        if width <= 0 or height <= 0:
            return

        # v0.16.4 FIX: 8/9pt bumped to 10/13pt throughout on_paint() --
        # real reported feedback (with a side-by-side screenshot) that
        # this panel's text was noticeably smaller than the rest of the
        # window's controls. See __init__'s SetMinSize() note for why
        # this is safe with no width/height side effect.
        note_h = 0
        if self.note:
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(100, 100, 100))
            note_h = 20
            dc.DrawText(self.note, 8, height - note_h + 2)

        if not self.grid_rows:
            dc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            dc.SetTextForeground(wx.Colour(140, 140, 140))
            dc.DrawText("(no layout to show)", 8, 8)
            return

        margin = 8
        n_rows = len(self.grid_rows)
        available_h = height - 2 * margin - note_h
        row_h = available_h / n_rows if n_rows else available_h

        dc.SetPen(wx.Pen(wx.Colour(70, 70, 70), 1))
        dc.SetBrush(wx.Brush(wx.Colour(233, 241, 250)))
        dc.SetTextForeground(wx.Colour(30, 30, 30))
        # 9 -> 13pt, the main part of this fix. Note (not yet acted on,
        # just flagged): a longer known field name in a busy 8-10 field
        # layout (smallest cells, most rows) is more likely to get
        # clipped at this bigger size than it was at 9pt -- DrawLabel()
        # clips silently, no ellipsis. Not a size/layout risk (see
        # __init__), just a readability trade-off to watch for during
        # testing on dense screens.
        dc.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        y = margin
        for row in self.grid_rows:
            n_cells = len(row) if row else 1
            available_w = width - 2 * margin
            cell_w = available_w / n_cells

            x = margin
            for pos in row:
                rect = wx.Rect(int(x), int(y), max(int(cell_w) - 2, 1), max(int(row_h) - 2, 1))
                dc.DrawRectangle(rect)

                label = self.field_labels[pos] if pos < len(self.field_labels) else "(empty)"
                dc.SetClippingRegion(rect)
                dc.DrawLabel(label, rect, wx.ALIGN_CENTER)
                dc.DestroyClippingRegion()

                x += cell_w
            y += row_h


class FieldPickerDialog(wx.Dialog):
    """
    Modal picker over the known field ID catalog (fit_dump.py's
    FIELD_ID_NAMES, 117 confirmed entries) for Add Field -- deliberately
    NOT free-text entry, so a user can't accidentally queue an
    unresolved or mistyped field ID (see the "Editing UX decision"
    note at the top of this file).
    """

    def __init__(self, parent, exclude_ids):
        super().__init__(parent, title="Add Field", size=(360, 420))
        self.selected_id = None
        self._all_choices = sorted(
            ((name, fid) for fid, name in FIELD_ID_NAMES.items() if fid not in exclude_ids),
            key=lambda t: t[0].lower(),
        )
        self._filtered = []

        outer = wx.BoxSizer(wx.VERTICAL)

        outer.Add(wx.StaticText(self, label="Search:"), 0, wx.TOP | wx.LEFT | wx.RIGHT, 8)
        self.search = wx.TextCtrl(self)
        self.search.Bind(wx.EVT_TEXT, self.on_search)
        outer.Add(self.search, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        self.listbox = wx.ListBox(self, style=wx.LB_SINGLE)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_ok)
        outer.Add(self.listbox, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 8)

        btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        outer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 8)

        self.SetSizer(outer)
        self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)
        self._refresh_list("")

    def _refresh_list(self, query):
        query = query.lower()
        self._filtered = [(name, fid) for (name, fid) in self._all_choices if query in name.lower()]
        self.listbox.Set([f"{name}  (id={fid})" for name, fid in self._filtered])
        if self._filtered:
            self.listbox.SetSelection(0)

    def on_search(self, event):
        self._refresh_list(self.search.GetValue())

    def on_ok(self, event):
        sel = self.listbox.GetSelection()
        if sel != wx.NOT_FOUND and sel < len(self._filtered):
            self.selected_id = self._filtered[sel][1]
            self.EndModal(wx.ID_OK)
        else:
            self.EndModal(wx.ID_CANCEL)


class EditScreenPanel(wx.Panel):
    """
    Step 6: edit one screen's fields (reorder/add/remove) and layout
    A/B. See the module docstring's "Editing architecture" and "Editing
    UX decision" notes for the full design reasoning -- summary:

    - Reordering (Move Up/Down) = select + buttons, mapped onto a
      --swap-fields-equivalent operation (swap two adjacent positions
      in the field-ID array, touching only field 7). No system-screen
      guard on pure reorders -- they don't change WHAT content a
      screen has, only its order.
    - Add/Remove/Change Type Field = pick from the known field catalog
      (never free text), then replace the WHOLE field array via a
      --fields-equivalent operation (patch_screen on fields 3+7) --
      the file format has no way to add/remove/replace a single field
      in isolation. Guarded by fit_patch.py's check_system_screen_guard()
      (v1.7.0) -- a match pops a confirmation dialog rather than
      silently blocking, mirroring --force. Change Type (v0.9.0) is
      "Replace Field" from the original design notes -- swaps one
      field's ID in place via the same FieldPickerDialog and
      _apply_field_list() Add/Remove already use, without the
      Remove+Add+reposition workaround.
    - Layout A/B = a two-option radio control, restricted to "B" only
      when the CURRENT field count is in COUNTS_WITH_B_VARIANT.
    - The visual diagram (LayoutDiagramPanel) is read-only, driven by
      LAYOUT_GRIDS -- purely a preview, never itself a control surface.

    Every change is applied immediately, directly to
    frame.editing_path (the scratch working copy), via real
    fit_patch.py function calls -- never a subprocess, never an
    in-memory simulation. The panel always re-reads the actual
    resulting bytes afterward (refresh_from_file()) rather than
    trusting what it assumes just happened.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.slot = None
        self.field_ids = []
        self.layout_variant = 0
        self.type_name = "?"  # set for real by refresh_from_file() (f10 -- see screen_type_name())

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        body_row = wx.BoxSizer(wx.HORIZONTAL)

        # Left column: field list + its controls
        left_col = wx.BoxSizer(wx.VERTICAL)
        left_col.Add(wx.StaticText(self, label="Fields (top to bottom = display order):"),
                     0, wx.BOTTOM, 4)
        self.fields_list = wx.ListBox(self, style=wx.LB_SINGLE)
        left_col.Add(self.fields_list, 1, wx.EXPAND | wx.BOTTOM, 8)

        field_btn_row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.move_up_btn = wx.Button(self, label="▲ Move Up")
        self.move_up_btn.Bind(wx.EVT_BUTTON, self.on_move_up)
        field_btn_row1.Add(self.move_up_btn, 0, wx.RIGHT, 6)
        self.move_down_btn = wx.Button(self, label="▼ Move Down")
        self.move_down_btn.Bind(wx.EVT_BUTTON, self.on_move_down)
        field_btn_row1.Add(self.move_down_btn, 0)
        left_col.Add(field_btn_row1, 0, wx.BOTTOM, 6)

        field_btn_row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.add_field_btn = wx.Button(self, label="+ Add Field...")
        self.add_field_btn.Bind(wx.EVT_BUTTON, self.on_add_field)
        field_btn_row2.Add(self.add_field_btn, 0, wx.RIGHT, 6)
        self.remove_field_btn = wx.Button(self, label="− Remove Field")
        self.remove_field_btn.Bind(wx.EVT_BUTTON, self.on_remove_field)
        field_btn_row2.Add(self.remove_field_btn, 0, wx.RIGHT, 6)
        self.change_type_btn = wx.Button(self, label="Change Type...")
        self.change_type_btn.Bind(wx.EVT_BUTTON, self.on_change_type)
        field_btn_row2.Add(self.change_type_btn, 0)
        left_col.Add(field_btn_row2, 0, wx.BOTTOM, 8)

        layout_row = wx.BoxSizer(wx.HORIZONTAL)
        layout_row.Add(wx.StaticText(self, label="Layout:"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.layout_a_radio = wx.RadioButton(self, label="A", style=wx.RB_GROUP)
        self.layout_b_radio = wx.RadioButton(self, label="B")
        self.layout_a_radio.Bind(wx.EVT_RADIOBUTTON, self.on_layout_choice)
        self.layout_b_radio.Bind(wx.EVT_RADIOBUTTON, self.on_layout_choice)
        layout_row.Add(self.layout_a_radio, 0, wx.RIGHT, 6)
        layout_row.Add(self.layout_b_radio, 0)
        left_col.Add(layout_row, 0, wx.BOTTOM, 8)

        # "Show Screen" -- matches the on-device wording exactly (per
        # the developer: Garmin's own UI uses "Show" with the toggle,
        # not "Hide"). Backed by field 12 (0=shown/1=hidden). Turning
        # this OFF (hiding) is guarded -- see on_show_toggle().
        self.show_checkbox = wx.CheckBox(self, label="Show Screen")
        self.show_checkbox.Bind(wx.EVT_CHECKBOX, self.on_show_toggle)
        left_col.Add(self.show_checkbox, 0, wx.BOTTOM, 4)

        self.count_text = wx.StaticText(self, label="")
        left_col.Add(self.count_text, 0)

        body_row.Add(left_col, 1, wx.EXPAND | wx.RIGHT, 12)

        # Right column: visual layout diagram (read-only preview)
        right_col = wx.BoxSizer(wx.VERTICAL)
        right_col.Add(wx.StaticText(self, label="On-device layout (read-only preview):"),
                      0, wx.BOTTOM, 4)
        self.diagram = LayoutDiagramPanel(self)
        right_col.Add(self.diagram, 1, wx.EXPAND)
        body_row.Add(right_col, 1, wx.EXPAND)

        outer.Add(body_row, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.status_text = wx.StaticText(self, label="")
        outer.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(self, label="‹ Back to Screens")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active."""
        self.slot = self.frame.editing_slot
        self.refresh_from_file()

    def refresh_from_file(self):
        """
        Re-derive EVERYTHING shown from the actual current bytes of
        frame.editing_path -- never trust in-memory state alone. This
        is what lets every button handler apply a change and just call
        this again rather than manually updating widgets to match what
        it assumes happened.
        """
        messages = decode_file(self.frame.editing_path)
        data = classify_screens(messages)

        mesg = None
        position = None
        for pos, (f9, idx, m) in enumerate(data["orderable"], start=1):
            if idx == self.slot:
                mesg, position = m, pos
                break
        if mesg is None:
            for idx, m in data["conditional"] + data["removed"]:
                if idx == self.slot:
                    mesg = m
                    break

        if mesg is None:
            self.title_text.SetLabel(f"Slot {self.slot}: not found in the working file.")
            self.field_ids = []
            self.fields_list.Set([])
            self.diagram.set_layout([], [])
            self.frame._relayout()
            return

        field_count = mesg.get(3) or 0
        self.field_ids = list(active_field_ids(mesg, field_count))
        self.layout_variant = mesg.get(8) or 0
        # v0.6.0: real screen-type name from f10 (CONFIRMED -- see
        # fit_dump.py's NAMED_SCREEN_TYPES).
        self.type_name = screen_type_name(mesg.get(10)) or "?"

        pos_label = f"position {position} in the on-device order" if position is not None \
            else "not in the main reorderable list (Conditional or Removed)"
        self.title_text.SetLabel(
            f"Editing slot {self.slot} ({self.type_name}) -- {pos_label}"
        )

        # v0.16.2 FIX: terse=True here, not the full descriptive form --
        # see the fix note on the diagram's `labels` a few lines down
        # for why (an unknown field ID's full label is what blew up the
        # window width).
        self.fields_list.Set([field_name(fid, terse=True) for fid in self.field_ids])

        count = len(self.field_ids)
        self.count_text.SetLabel(f"Field count: {count} / {MAX_FIELDS_PER_SCREEN}")

        supports_b = count in COUNTS_WITH_B_VARIANT
        self.layout_b_radio.Enable(supports_b)
        if self.layout_variant == 1 and supports_b:
            self.layout_b_radio.SetValue(True)
        else:
            self.layout_a_radio.SetValue(True)

        # field 12: 0 = shown/enabled, 1 = hidden/disabled -- matches
        # the on-device "Show Screen" toggle exactly.
        self.show_checkbox.SetValue(mesg.get(12) != 1)

        variant_for_diagram = self.layout_variant if supports_b else 0
        grid_rows = LAYOUT_GRIDS.get(count, {}).get(variant_for_diagram, [])
        # v0.16.2 FIX (real reported bug, 2026-08-07): terse=True, not
        # the full "UNKNOWN (id=N, ...)" form -- see fields_list.Set()
        # above for the full explanation. The diagram itself doesn't
        # grow from long labels (its cells clip text via a wx.DC
        # clipping region during on_paint(), never resize the panel),
        # but wx.ListBox DOES report its best-size based on the full
        # width of its longest item string -- and that best-size
        # propagates up through body_row's sizer into EditScreenPanel's
        # overall best size. Combined with MainFrame._relayout()'s
        # v0.11.0 "only grow, never shrink" behavior (deliberately added
        # so a manually-enlarged window wouldn't snap back down), a
        # single unresolved field ID on the screen being edited
        # permanently inflated the whole window -- reported symptom:
        # editing a screen with an unrecognized field ID pushed the
        # window off the left edge of the screen, with a large empty
        # gap between the field list and the diagram (the diagram
        # column also stretched wider than needed, since both columns
        # share body_row's HORIZONTAL proportion), and the oversized
        # window persisted on every subsequent panel, since nothing
        # ever shrinks it back down.
        labels = [field_name(fid, terse=True) for fid in self.field_ids]
        note = ""
        if count == 3 and variant_for_diagram == 1:
            note = "B: top field renders smaller on-device (not shown to scale here)"
        self.diagram.set_layout(grid_rows, labels, note)

        self.move_up_btn.Enable(count > 1)
        self.move_down_btn.Enable(count > 1)
        self.add_field_btn.Enable(count < MAX_FIELDS_PER_SCREEN)
        self.remove_field_btn.Enable(count > 1)
        self.change_type_btn.Enable(count > 0)

        self.status_text.SetLabel("")
        self.frame._relayout()

    def _confirm_guard(self):
        """
        Returns True if it's OK to proceed with a field-array-replacing
        change (add/remove), False if the user declined after seeing
        the system-screen guard's warning. Checked against the file's
        CURRENT on-disk state via fit_patch.py's
        check_system_screen_guard() -- the exact same function the CLI
        uses for --fields, so the two never drift apart.

        v0.6.2: check_system_screen_guard() (fit_patch.py v1.10.0) is
        now f10-aware -- returns None (no dialog) for any screen
        CONFIRMED to be a plain user screen via field 10, and a
        CERTAIN, named message ("is a Garmin 'Map' screen...") rather
        than a guess when it does identify a named Garmin type. The
        "this is only a heuristic" framing below now only genuinely
        applies to the rare fallback case (a Removed-state slot with
        no real f10) -- reworded accordingly.
        """
        warning = check_system_screen_guard(self.frame.editing_path, self.slot)
        if warning is None:
            return True
        answer = wx.MessageBox(
            f"This screen {warning}\n\n"
            "Proceed anyway?",
            "Named or possible system/predefined screen",
            wx.YES_NO | wx.ICON_WARNING,
        )
        return answer == wx.YES

    def _confirm_hide_guard(self):
        """
        Gate for HIDING a screen specifically (not showing one). Reuses
        check_system_screen_guard() like _confirm_guard() does, but
        with a stronger, more specific warning.

        v0.6.2 CORRECTION: check_system_screen_guard() itself (see
        fit_patch.py v1.10.0) is now f10-aware -- it returns None
        immediately, with NO dialog at all, for any screen CONFIRMED
        (not guessed) to be a plain user screen via field 10. This
        directly fixes a real reported false positive: a confirmed
        user screen with only 1 field was still popping this dialog's
        old ambiguous "might be a system screen, no reliable way to
        tell" wording, even though the toolkit can now tell for
        certain. This method no longer needs its own f10 check (the
        v0.6.0 type_note logic is gone) -- check_system_screen_guard()
        already returns a CERTAIN, named message ("is a Garmin 'Map'
        screen...") when f10 does identify a named Garmin type, so
        there's nothing left to add here. The "last remaining visible
        user screen" case is a separate HARD, non-overridable block
        (see on_show_toggle()) that already ran before this method is
        even reached.
        """
        warning = check_system_screen_guard(self.frame.editing_path, self.slot)
        if warning is None:
            return True
        answer = wx.MessageBox(
            f"This screen {warning}\n\n"
            "Hiding it via a raw file write (not the on-device editor) "
            "is genuinely UNTESTED.\n\n"
            "Proceed anyway?",
            "Named Garmin screen -- hide is untested",
            wx.YES_NO | wx.ICON_WARNING,
        )
        return answer == wx.YES

    def on_show_toggle(self, event):
        new_enabled = self.show_checkbox.GetValue()  # True = show, False = hide
        if not new_enabled:
            # HARD block #1 -- is this screen type CONFIRMED (not
            # guessed) to have no on-device Show Screen toggle at all?
            # Map and ClimbPro, specifically -- directly observed on
            # the device, on every profile type, so there's no
            # "proceed anyway" here either.
            unsupported_type = hide_unsupported_screen_type(self.frame.editing_path, self.slot)
            if unsupported_type is not None:
                wx.MessageBox(
                    f"This is a '{unsupported_type}' screen. CONFIRMED via "
                    f"direct on-device inspection that this screen type has "
                    f"no Show Screen toggle at all in the Data Screens "
                    f"editor, on any profile -- there's nothing to force "
                    f"here, because that state has no on-device equivalent "
                    f"to compare it against.",
                    f"Can't hide {unsupported_type}",
                    wx.OK | wx.ICON_ERROR,
                )
                self.show_checkbox.SetValue(True)  # revert -- stays shown
                return
            # HARD block #2 -- would this leave zero visible USER
            # screens? Confirmed via real on-device testing that the
            # editor refuses this outright too, so no "proceed anyway"
            # here either.
            if would_hide_last_visible_screen(self.frame.editing_path, self.slot):
                wx.MessageBox(
                    "This is currently the only visible USER screen on this "
                    "profile -- Garmin-named screens (Map, Elevation, etc.) "
                    "don't count toward this. Confirmed via real on-device "
                    "testing that Garmin's own editor refuses to hide or "
                    "remove a profile's last remaining user screen even "
                    "while other named screens are still visible -- this "
                    "isn't a guess, so it can't be overridden here either. "
                    "Show another user screen first if you want to hide "
                    "this one.",
                    "Can't hide the last visible user screen",
                    wx.OK | wx.ICON_ERROR,
                )
                self.show_checkbox.SetValue(True)  # revert -- stays shown
                return
            # Softer heuristic guard third -- only reached if both hard
            # checks above passed.
            if not self._confirm_hide_guard():
                self.show_checkbox.SetValue(True)  # revert -- stays shown
                return
        changes = {12: pack_enabled(new_enabled)}
        patch_screen(self.frame.editing_path, self.frame.editing_path, self.slot, changes)
        self.refresh_from_file()

    def on_move_up(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND or sel == 0:
            return
        self._swap_fields(sel - 1, sel)
        self.fields_list.SetSelection(sel - 1)

    def on_move_down(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND or sel >= len(self.field_ids) - 1:
            return
        self._swap_fields(sel, sel + 1)
        self.fields_list.SetSelection(sel + 1)

    def _swap_fields(self, pos_a, pos_b):
        current_array = read_current_field_array(self.frame.editing_path, self.slot)
        current_array[pos_a], current_array[pos_b] = current_array[pos_b], current_array[pos_a]
        changes = {7: struct.pack('<10H', *current_array)}
        patch_screen(self.frame.editing_path, self.frame.editing_path, self.slot, changes)
        self.refresh_from_file()

    def _apply_field_list(self, new_ids):
        if not self._confirm_guard():
            return
        changes = {
            3: pack_field_count(len(new_ids)),
            7: pack_field_id_array(new_ids),
        }
        # If the new count no longer supports the CURRENT layout
        # variant, fall back to A automatically -- mirrors fit_patch.py's
        # own hard validation error, just resolved here instead of
        # erroring, since the GUI already knows the effective count.
        _, current_layout = read_current_count_and_layout(self.frame.editing_path, self.slot)
        if current_layout == 1 and len(new_ids) not in COUNTS_WITH_B_VARIANT:
            changes[8] = pack_layout_variant(0)

        patch_screen(self.frame.editing_path, self.frame.editing_path, self.slot, changes)
        self.refresh_from_file()

    def on_add_field(self, event):
        if len(self.field_ids) >= MAX_FIELDS_PER_SCREEN:
            wx.MessageBox(f"A screen can have at most {MAX_FIELDS_PER_SCREEN} fields.",
                           "Can't add", wx.OK | wx.ICON_WARNING)
            return
        dlg = FieldPickerDialog(self, exclude_ids=set(self.field_ids))
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id is not None:
            self._apply_field_list(self.field_ids + [dlg.selected_id])
        dlg.Destroy()

    def on_remove_field(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        if len(self.field_ids) <= 1:
            wx.MessageBox("A screen needs at least 1 field.", "Can't remove",
                           wx.OK | wx.ICON_WARNING)
            return
        new_ids = self.field_ids[:sel] + self.field_ids[sel + 1:]
        self._apply_field_list(new_ids)

    def on_change_type(self, event):
        """
        Swap the selected field's ID in place, without disturbing its
        position -- the "Replace Field" action named in the original
        design notes (PROJECT_NOTES.md / "Editing UX decision") but
        never built until now. Funnels into the exact same
        _apply_field_list() -> --fields-equivalent patch_screen() call
        Add/Remove Field already use, so it's covered by the same
        check_system_screen_guard() confirmation dialog -- no separate
        guard logic needed.
        """
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        # Exclude every OTHER field currently on the screen (no
        # duplicates), but leave the field being replaced itself
        # selectable -- picking the same ID back is a harmless no-op,
        # not worth a separate disabled-option case.
        exclude = set(self.field_ids) - {self.field_ids[sel]}
        dlg = FieldPickerDialog(self, exclude_ids=exclude)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id is not None:
            new_ids = list(self.field_ids)
            new_ids[sel] = dlg.selected_id
            self._apply_field_list(new_ids)
        dlg.Destroy()

    def on_layout_choice(self, event):
        new_layout = 1 if self.layout_b_radio.GetValue() else 0
        if new_layout == self.layout_variant:
            return
        count = len(self.field_ids)
        if new_layout == 1 and count not in COUNTS_WITH_B_VARIANT:
            wx.MessageBox(
                f"Layout B isn't available for a {count}-field screen -- only "
                f"{sorted(COUNTS_WITH_B_VARIANT)}-field screens have a real A/B choice.",
                "Layout not available", wx.OK | wx.ICON_WARNING,
            )
            self.layout_a_radio.SetValue(True)
            return
        changes = {8: pack_layout_variant(new_layout)}
        patch_screen(self.frame.editing_path, self.frame.editing_path, self.slot, changes)
        self.refresh_from_file()

    def on_back(self, event):
        self.frame.show_panel("screens")


class AddScreenPanel(wx.Panel):
    """
    Step 5: create a brand-new screen. CONFIRMED working as of
    fit_patch.py v1.12.0 (live on-device round-trip, 2026-08-05 -- see
    PROJECT_NOTES.md "Adding a new screen"). This panel replicates
    --new-slot's exact defaulting logic via direct function calls (no
    subprocess): pick the lowest unconfigured slot, set f1 (configured)
    and f12 (shown) the same way every real device-created screen has
    them, auto-assign a collision-free f9 (next_available_field9()) and
    f10 (next_available_field10()), and write the chosen field list and
    layout. Internal slot number is deliberately never surfaced in the
    UI -- see MVP_SCOPE.md's "message_index should never be shown to
    the user" design constraint.

    Field list/layout controls intentionally mirror EditScreenPanel's
    left column -- same widgets, same FieldPickerDialog, same
    LayoutDiagramPanel preview, and (v0.9.0) the same Change Type
    action -- so building a new screen's content feels identical to
    editing an existing one. The only real difference is what
    on_create() does with the result.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.field_ids = []
        self.layout_variant = 0

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="Add New Screen")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.cap_text = wx.StaticText(self, label="")
        outer.Add(self.cap_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        body_row = wx.BoxSizer(wx.HORIZONTAL)

        left_col = wx.BoxSizer(wx.VERTICAL)
        left_col.Add(wx.StaticText(self, label="Fields (top to bottom = display order):"),
                     0, wx.BOTTOM, 4)
        self.fields_list = wx.ListBox(self, style=wx.LB_SINGLE)
        left_col.Add(self.fields_list, 1, wx.EXPAND | wx.BOTTOM, 8)

        field_btn_row1 = wx.BoxSizer(wx.HORIZONTAL)
        self.move_up_btn = wx.Button(self, label="▲ Move Up")
        self.move_up_btn.Bind(wx.EVT_BUTTON, self.on_move_up)
        field_btn_row1.Add(self.move_up_btn, 0, wx.RIGHT, 6)
        self.move_down_btn = wx.Button(self, label="▼ Move Down")
        self.move_down_btn.Bind(wx.EVT_BUTTON, self.on_move_down)
        field_btn_row1.Add(self.move_down_btn, 0)
        left_col.Add(field_btn_row1, 0, wx.BOTTOM, 6)

        field_btn_row2 = wx.BoxSizer(wx.HORIZONTAL)
        self.add_field_btn = wx.Button(self, label="+ Add Field...")
        self.add_field_btn.Bind(wx.EVT_BUTTON, self.on_add_field)
        field_btn_row2.Add(self.add_field_btn, 0, wx.RIGHT, 6)
        self.remove_field_btn = wx.Button(self, label="− Remove Field")
        self.remove_field_btn.Bind(wx.EVT_BUTTON, self.on_remove_field)
        field_btn_row2.Add(self.remove_field_btn, 0, wx.RIGHT, 6)
        self.change_type_btn = wx.Button(self, label="Change Type...")
        self.change_type_btn.Bind(wx.EVT_BUTTON, self.on_change_type)
        field_btn_row2.Add(self.change_type_btn, 0)
        left_col.Add(field_btn_row2, 0, wx.BOTTOM, 8)

        layout_row = wx.BoxSizer(wx.HORIZONTAL)
        layout_row.Add(wx.StaticText(self, label="Layout:"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.layout_a_radio = wx.RadioButton(self, label="A", style=wx.RB_GROUP)
        self.layout_b_radio = wx.RadioButton(self, label="B")
        self.layout_a_radio.Bind(wx.EVT_RADIOBUTTON, self.on_layout_choice)
        self.layout_b_radio.Bind(wx.EVT_RADIOBUTTON, self.on_layout_choice)
        layout_row.Add(self.layout_a_radio, 0, wx.RIGHT, 6)
        layout_row.Add(self.layout_b_radio, 0)
        left_col.Add(layout_row, 0, wx.BOTTOM, 8)

        self.count_text = wx.StaticText(self, label="")
        left_col.Add(self.count_text, 0)

        body_row.Add(left_col, 1, wx.EXPAND | wx.RIGHT, 12)

        right_col = wx.BoxSizer(wx.VERTICAL)
        right_col.Add(wx.StaticText(self, label="On-device layout (read-only preview):"),
                      0, wx.BOTTOM, 4)
        self.diagram = LayoutDiagramPanel(self)
        right_col.Add(self.diagram, 1, wx.EXPAND)
        body_row.Add(right_col, 1, wx.EXPAND)

        outer.Add(body_row, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.status_text = wx.StaticText(self, label="")
        outer.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(self, label="‹ Cancel")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)
        self.create_btn = wx.Button(self, label="Create Screen")
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        button_row.Add(self.create_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active -- always starts blank."""
        self.field_ids = []
        self.layout_variant = 0
        self._refresh_widgets()

    def _count_user_screens(self):
        """
        How many real user screens (f10 not a named Garmin type) exist
        right now, in ANY show state -- this is what the confirmed
        10-screen cap counts against, not just currently-visible ones.
        Computed directly via classify_screens()/NAMED_SCREEN_TYPES,
        the same primitives ViewScreensPanel's Type column already
        uses -- no new fit_patch.py function needed for this.
        """
        working_path = self.frame.get_working_path()
        if working_path is None:
            return 0
        messages = decode_file(working_path)
        data = classify_screens(messages)
        count = sum(1 for f9, idx, m in data["orderable"] if m.get(10) not in NAMED_SCREEN_TYPES)
        # Every Conditional screen observed so far is a named Garmin
        # type (GroupTrack, etc.), but check this bucket too for
        # completeness rather than assuming that always holds.
        count += sum(1 for idx, m in data["conditional"] if m.get(10) not in NAMED_SCREEN_TYPES)
        return count

    def _refresh_widgets(self):
        working_path = self.frame.get_working_path()
        if working_path is None:
            self.cap_text.SetLabel("No profile staged yet -- go back and stage one first.")
            self.fields_list.Set([])
            self.diagram.set_layout([], [])
            self.create_btn.Disable()
            self.frame._relayout()
            return

        user_count = self._count_user_screens()
        at_cap = user_count >= MAX_USER_SCREENS
        cap_msg = f"{user_count} of {MAX_USER_SCREENS} user-definable screens used."
        if at_cap:
            cap_msg += (" Profile is AT THE CAP -- remove or hide an existing "
                        "user screen before adding another.")
        self.cap_text.SetLabel(cap_msg)

        # v0.16.2 FIX: terse=True -- see EditScreenPanel.refresh_from_file()
        # for the full explanation (an unknown field ID's full label is
        # what blew up the window width). AddScreenPanel can't actually
        # pick up an unknown ID today (Add Field/Change Type are both
        # FieldPickerDialog-only, over the known catalog), but fixed here
        # too for consistency and as cheap insurance against any future
        # path that could feed it one.
        self.fields_list.Set([field_name(fid, terse=True) for fid in self.field_ids])
        count = len(self.field_ids)
        self.count_text.SetLabel(f"Field count: {count} / {MAX_FIELDS_PER_SCREEN}")

        supports_b = count in COUNTS_WITH_B_VARIANT
        self.layout_b_radio.Enable(supports_b)
        if not (self.layout_variant == 1 and supports_b):
            self.layout_variant = 0
        if self.layout_variant == 1:
            self.layout_b_radio.SetValue(True)
        else:
            self.layout_a_radio.SetValue(True)

        variant_for_diagram = self.layout_variant if supports_b else 0
        grid_rows = LAYOUT_GRIDS.get(count, {}).get(variant_for_diagram, [])
        # v0.16.2 FIX: terse=True -- see EditScreenPanel's equivalent
        # fix note for the full explanation.
        labels = [field_name(fid, terse=True) for fid in self.field_ids]
        note = ""
        if count == 3 and variant_for_diagram == 1:
            note = "B: top field renders smaller on-device (not shown to scale here)"
        self.diagram.set_layout(grid_rows, labels, note)

        self.move_up_btn.Enable(count > 1)
        self.move_down_btn.Enable(count > 1)
        self.add_field_btn.Enable(count < MAX_FIELDS_PER_SCREEN)
        self.remove_field_btn.Enable(count > 0)
        self.change_type_btn.Enable(count > 0)
        self.create_btn.Enable(count >= 1 and not at_cap)

        self.frame._relayout()

    def on_move_up(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND or sel == 0:
            return
        self.field_ids[sel - 1], self.field_ids[sel] = self.field_ids[sel], self.field_ids[sel - 1]
        self._refresh_widgets()
        self.fields_list.SetSelection(sel - 1)

    def on_move_down(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND or sel >= len(self.field_ids) - 1:
            return
        self.field_ids[sel], self.field_ids[sel + 1] = self.field_ids[sel + 1], self.field_ids[sel]
        self._refresh_widgets()
        self.fields_list.SetSelection(sel + 1)

    def on_add_field(self, event):
        if len(self.field_ids) >= MAX_FIELDS_PER_SCREEN:
            wx.MessageBox(f"A screen can have at most {MAX_FIELDS_PER_SCREEN} fields.",
                           "Can't add", wx.OK | wx.ICON_WARNING)
            return
        dlg = FieldPickerDialog(self, exclude_ids=set(self.field_ids))
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id is not None:
            self.field_ids.append(dlg.selected_id)
            self._refresh_widgets()
        dlg.Destroy()

    def on_remove_field(self, event):
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        del self.field_ids[sel]
        self._refresh_widgets()

    def on_change_type(self, event):
        """
        Swap the selected field's ID in place -- unlike EditScreenPanel's
        version, nothing has been written to disk yet at this point
        (that only happens in on_create()), so this just mutates the
        in-memory field_ids list and re-renders, no guard/patch_screen
        call needed here.
        """
        sel = self.fields_list.GetSelection()
        if sel == wx.NOT_FOUND:
            return
        exclude = set(self.field_ids) - {self.field_ids[sel]}
        dlg = FieldPickerDialog(self, exclude_ids=exclude)
        if dlg.ShowModal() == wx.ID_OK and dlg.selected_id is not None:
            self.field_ids[sel] = dlg.selected_id
            self._refresh_widgets()
            self.fields_list.SetSelection(sel)
        dlg.Destroy()

    def on_layout_choice(self, event):
        new_layout = 1 if self.layout_b_radio.GetValue() else 0
        count = len(self.field_ids)
        if new_layout == 1 and count not in COUNTS_WITH_B_VARIANT:
            wx.MessageBox(
                f"Layout B isn't available for a {count}-field screen -- only "
                f"{sorted(COUNTS_WITH_B_VARIANT)}-field screens have a real A/B choice.",
                "Layout not available", wx.OK | wx.ICON_WARNING,
            )
            self.layout_a_radio.SetValue(True)
            return
        self.layout_variant = new_layout
        self._refresh_widgets()

    def on_create(self, event):
        if not self.field_ids:
            wx.MessageBox("Add at least one field first.", "Can't create",
                           wx.OK | wx.ICON_WARNING)
            return
        if self._count_user_screens() >= MAX_USER_SCREENS:
            wx.MessageBox(
                f"This profile already has {MAX_USER_SCREENS} user-definable "
                f"screens -- the confirmed on-device cap. Remove or hide an "
                f"existing one first.",
                "At the screen cap", wx.OK | wx.ICON_ERROR,
            )
            return

        # First edit of this session: create the scratch working copy
        # (same pattern as ViewScreensPanel.on_edit()/_swap_screen_order()
        # and EditScreenPanel -- editing_path IS the pending-edit queue,
        # see module docstring).
        if self.frame.editing_path is None:
            source = self.frame.staged_path
            self.frame.editing_path = source + ".editing.fit"
            shutil.copy2(source, self.frame.editing_path)

        messages = decode_file(self.frame.editing_path)
        data = classify_screens(messages)
        if not data["unconfigured"]:
            wx.MessageBox(
                "No unconfigured slots remain in this file -- every one of "
                "the ~30 preallocated slots is already Active, Conditional, "
                "or Removed. This shouldn't normally happen.",
                "Can't create", wx.OK | wx.ICON_ERROR,
            )
            return
        # Internal slot number, never shown to the user -- see
        # MVP_SCOPE.md's design constraints.
        target_slot = min(idx for idx, m in data["unconfigured"])

        # Mirrors fit_patch.py --new-slot's exact defaulting logic
        # (v1.12.0) -- see PROJECT_NOTES.md "Adding a new screen".
        auto_f10 = next_available_field10(self.frame.editing_path)
        changes = {
            1: pack_configured_flag(),
            3: pack_field_count(len(self.field_ids)),
            7: pack_field_id_array(self.field_ids),
            8: pack_layout_variant(self.layout_variant),
            9: pack_uint8(next_available_field9(self.frame.editing_path)),
            10: pack_uint8(auto_f10),
            12: pack_enabled(True),
        }
        patch_screen(self.frame.editing_path, self.frame.editing_path, target_slot, changes)

        wx.MessageBox(
            f"New screen created in the working copy -- {len(self.field_ids)} "
            f"field(s), will show on-device as 'Screen {auto_f10 + 1}'. NOT "
            f"yet deployed -- verify it on the Screens view, then deploy when "
            f"ready.",
            "Screen created", wx.OK | wx.ICON_INFORMATION,
        )
        self.frame.show_panel("screens")

    def on_back(self, event):
        self.frame.show_panel("screens")


def describe_screen_changes(path_a, path_b):
    """
    Compare two .fit files screen-by-screen (by slot/message_index)
    and describe what's different between them in plain English --
    e.g. "Screen 4: added Cadence, removed Grade" or "Screen 2: moved
    from position 3 to position 2". Returns a list of one string per
    changed screen (new/removed screens included), in ascending slot
    order.

    Shared by PreflightPanel (staged file vs. working copy, before
    deploying) and DeployPanel (working copy vs. the live file
    re-pulled from the device after a deploy, i.e. post-write
    verification) -- same comparison, different pair of files.

    Only screens ACTIVE (field 1 == 1) on at least one side are ever
    reported -- Removed (f1=0) and Unconfigured (f1=0xFF) slots are
    invisible to this comparison by construction, since both
    before_active and after_active evaluate False for them and hit the
    "nothing to report" branch below. This is deliberate, not an
    oversight, and matters most for DeployPanel's use: the device's
    own NewFiles import is known to wipe the Removed list as a side
    effect (see PROJECT_NOTES.md / "Product note on --un-remove") even
    though it's untouched by ordinary on-device edits -- since Garmin's
    own editor has no un-remove workflow and this GUI doesn't offer
    one either, that wipe isn't something a user needs reported on
    post-deploy; only ACTUAL visible/active screen changes are. A user
    who doesn't want the deployed result as-is has Restore-from-Backup
    as the way back, not an un-remove workflow.

    Compares by message_index (slot), the same stable per-screen
    identity used throughout the rest of the GUI (see the "slot"
    vocabulary in ViewScreensPanel/EditScreenPanel) -- NOT by
    on-device position, since position itself is one of the things
    that can change (screen-level reordering).
    """
    data_a = classify_screens(decode_file(path_a))
    data_b = classify_screens(decode_file(path_b))

    def slot_map(data):
        slots = {}
        for bucket in ("orderable", "conditional", "removed", "unconfigured"):
            for entry in data[bucket]:
                idx, mesg = (entry[1], entry[2]) if bucket == "orderable" else entry
                slots[idx] = mesg
        return slots

    def position_map(data):
        return {idx: pos for pos, (f9, idx, mesg) in enumerate(data["orderable"], start=1)}

    slots_a = slot_map(data_a)
    slots_b = slot_map(data_b)
    pos_a = position_map(data_a)
    pos_b = position_map(data_b)

    def fields_of(mesg):
        return list(active_field_ids(mesg, mesg.get(3) or 0))

    lines = []
    for idx in sorted(set(slots_a) | set(slots_b)):
        before = slots_a.get(idx)
        after = slots_b.get(idx)

        before_active = before is not None and before.get(1) == 1
        after_active = after is not None and after.get(1) == 1

        if not before_active and after_active:
            names = ", ".join(field_name(fid) for fid in fields_of(after))
            type_name = screen_type_name(after.get(10)) or "New screen"
            lines.append(f"{type_name}: NEW -- fields: {names}")
            continue

        if before_active and not after_active:
            type_name = screen_type_name(before.get(10)) or "Screen"
            lines.append(f"{type_name}: REMOVED")
            continue

        if not before_active and not after_active:
            continue  # not active on either side (Removed/Unconfigured) -- nothing to report

        # Active on both sides -- compare content.
        type_name = screen_type_name(after.get(10)) or screen_type_name(before.get(10)) or "Screen"
        detail = []

        before_fields = fields_of(before)
        after_fields = fields_of(after)
        if set(before_fields) != set(after_fields):
            added = [field_name(fid) for fid in after_fields if fid not in before_fields]
            removed = [field_name(fid) for fid in before_fields if fid not in after_fields]
            if added:
                detail.append(f"added {', '.join(added)}")
            if removed:
                detail.append(f"removed {', '.join(removed)}")
        elif before_fields != after_fields:
            detail.append("field order changed")

        layout_name = {0: "A", 1: "B"}
        before_layout, after_layout = before.get(8), after.get(8)
        if before_layout != after_layout:
            detail.append(
                f"layout changed from {layout_name.get(before_layout, '-')} "
                f"to {layout_name.get(after_layout, '-')}"
            )

        before_shown = before.get(12) != 1
        after_shown = after.get(12) != 1
        if before_shown != after_shown:
            detail.append("shown on-device" if after_shown else "hidden on-device")

        before_p, after_p = pos_a.get(idx), pos_b.get(idx)
        if before_p is not None and after_p is not None and before_p != after_p:
            detail.append(f"moved from position {before_p} to position {after_p}")

        if detail:
            lines.append(f"{type_name}: {'; '.join(detail)}")

    return lines


class PreflightPanel(wx.Panel):
    """
    Steps 7+8: review accumulated changes, then a final pre-flight
    check before deploying.

    ARCHITECTURE NOTE: the original scoping (PROJECT_NOTES.md /
    "Agreed high-level flow") described step 7 as "a pending/preview
    state, not immediate writes." That's not how the GUI actually
    ended up working, and deliberately so -- see the module
    docstring's "Editing architecture" note: every button click on
    every panel already applies a REAL, immediate fit_patch.py
    operation to frame.editing_path. There never was a separate
    abstract "pending changes" queue to apply -- editing_path already
    IS that queue, in real bytes on disk, built up click by click as
    the user worked through Screens/Edit Screen/Add Screen. So this
    panel isn't an "apply" step (nothing left to apply); it's purely a
    REVIEW + VERIFY step -- exactly what the CLI docs already tell a
    user to do by hand before every deploy (`fit_dump.py diff` /
    `fit_crc.py`), just automated and shown before Deploy (DeployPanel,
    v0.13.0) is reachable at all.

    v0.12.0: the change summary is a plain-English, per-screen
    description (module-level describe_screen_changes(), shared with
    DeployPanel's post-write verification -- v0.14.0) rather than a raw
    fit_dump.py-diff-style unified diff. User feedback: the byte-level
    diff format was too technical for the GUI's actual audience (a
    rider, not a developer) -- "I don't foresee any but the most
    hardcore developer type understanding the diff as currently
    presented. If they want that, they might dig into the CLI tools."
    So this panel now describes changes the way a rider would think
    about them ("Screen 4: added Cadence, removed Grade", "Screen 2
    moved from position 3 to position 2"), grouped by screen. The raw
    unified diff (render_lines() + difflib, same format as the CLI's
    `fit_dump.py diff`) is intentionally NOT shown here anymore --
    that's exactly what the CLI tools remain for.

    Whether there's anything to deploy at all is still decided from
    the actual raw bytes (staged file vs. working copy), independent
    of whether describe_screen_changes() manages to produce a line for every
    kind of change -- if a future edit type isn't covered by the
    per-screen description yet, a generic fallback line says so rather
    than silently under-reporting. CRC uses fit_crc.py's fit_crc()
    directly against the working file's ACTUAL current bytes -- not
    assumed valid just because patch_screen() always recomputes it;
    this is the same "don't trust, re-read" discipline every other
    panel in this app already follows.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="Review Changes -- Pre-Flight Check")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.summary_text = wx.StaticText(self, label="")
        outer.Add(self.summary_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        outer.Add(wx.StaticText(self, label="Screens changed since you started editing:"),
                  0, wx.LEFT | wx.RIGHT, 12)
        self.diff_text = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.HSCROLL
        )
        outer.Add(self.diff_text, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.crc_text = wx.StaticText(self, label="")
        outer.Add(self.crc_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(self, label="‹ Back to Screens")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)
        self.deploy_btn = wx.Button(self, label="Continue to Deploy →")
        self.deploy_btn.Bind(wx.EVT_BUTTON, self.on_deploy)
        button_row.Add(self.deploy_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active -- always re-reads from disk."""
        self._refresh()

    def _refresh(self):
        if self.frame.staged_path is None or self.frame.editing_path is None:
            self.summary_text.SetLabel(
                "No changes to review yet -- go back and edit at least one screen first."
            )
            self.diff_text.SetValue("")
            self.crc_text.SetLabel("")
            self.deploy_btn.Disable()
            self.frame._relayout()
            return

        # Whether there's anything to deploy at all is decided from the
        # actual raw bytes, independent of whether _describe_changes()
        # below manages to describe every kind of change in plain
        # English -- see class docstring.
        with open(self.frame.staged_path, 'rb') as f:
            staged_bytes = f.read()
        with open(self.frame.editing_path, 'rb') as f:
            editing_bytes = f.read()
        bytes_changed = staged_bytes != editing_bytes

        summary_lines = describe_screen_changes(self.frame.staged_path, self.frame.editing_path)

        if bytes_changed and not summary_lines:
            # Defensive fallback -- some future edit type isn't covered
            # by describe_screen_changes() yet. Say so rather than
            # silently reporting "no changes" when the bytes disagree.
            summary_lines = [
                "Some changes were made that don't have a plain-language "
                "description yet, but the file has changed and is still "
                "valid to deploy."
            ]

        if bytes_changed:
            self.summary_text.SetLabel(
                f"{len(summary_lines)} screen(s) changed since you started editing."
            )
            self.diff_text.SetValue("\n\n".join(summary_lines))
        else:
            self.summary_text.SetLabel(
                "No differences from the staged file -- nothing to deploy."
            )
            self.diff_text.SetValue("(no changes yet)")

        # CRC check against the working file's actual current bytes --
        # same algorithm fit_crc.py's own self-check uses.
        body, trailer = editing_bytes[:-2], editing_bytes[-2:]
        expected = struct.unpack('<H', trailer)[0]
        computed = fit_crc(body)
        if computed == expected:
            self.crc_text.SetLabel(f"CRC check: PASS (0x{expected:04x})")
            self.deploy_btn.Enable(bytes_changed)
        else:
            self.crc_text.SetLabel(
                f"CRC check: FAIL -- expected 0x{expected:04x}, computed 0x{computed:04x}. "
                f"DO NOT DEPLOY THIS FILE -- this indicates a real bug, not a normal state."
            )
            self.deploy_btn.Disable()

        self.frame._relayout()

    def on_back(self, event):
        self.frame.show_panel("screens")

    def on_deploy(self, event):
        self.frame.deploy_return_panel = "review"
        self.frame.show_panel("deploy")


class DeployPanel(wx.Panel):
    """
    Step 9: write the reviewed, CRC-verified working copy to the
    device's NewFiles/ folder, then walk the user through eject and
    reconnect -- the two device-side steps that can't be automated
    away (the Edge 530 needs one manual power-button press to come
    back into mass-storage mode after its own auto-restart; confirmed
    via real device testing, see garmin_device.py's wait_for_remount()
    docstring/comments).

    Design decision (2026-08-06, user-confirmed): NO background
    polling/threading for the remount wait. write_to_newfiles() and
    its write-back verification are real, immediate, synchronous
    calls, consistent with every other button in this app -- but
    garmin_device.py's wait_for_remount() blocks with time.sleep() for
    up to 180s, which would freeze the whole GUI with no feedback if
    called directly from a handler. Rather than introduce this app's
    first background thread (a new class of failure mode -- e.g.
    thread lifetime vs. panel teardown, the same species of bug
    already hit once with EVT_SIZE during teardown, see
    LayoutDiagramPanel.on_size()), reconnect detection here is a
    manual "Check for Reconnected Device" button: each click is one
    immediate, non-blocking find_garmin_root() call. A few extra
    clicks in exchange for zero new failure modes.

    Eject is NOT done via garmin_device.py's eject_device(
    auto_eject=True) -- that function confirms via a terminal input()
    prompt, which would hang a GUI event handler (no stdin to read
    from in this context). Instead this panel reimplements just the
    confirm-then-diskutil-eject logic behind a wx.MessageBox, reusing
    garmin_device._volume_mount_point() for the actual eject target
    (ejecting garmin_root itself does NOT work on real hardware --
    confirmed via testing, see that function's docstring: the
    Sports/NewFiles structure sits one level deeper than the actual
    ejectable volume). "I Ejected It Myself" is the always-available
    fallback -- required on non-macOS, optional on macOS.

    Post-write verification (v0.14.0): the moment reconnect is
    confirmed, on_check() re-pulls the LIVE profile straight from the
    device's Sports/ folder and runs it through the same
    describe_screen_changes() the Preflight panel uses, comparing it
    against editing_path (what was actually sent) -- reusing the exact
    "only ACTIVE screens are ever reported" behavior documented on
    that function, which is what makes this safe to run automatically
    without needing to special-case the device's known Removed-list
    wipe on NewFiles import (see that function's docstring, and
    PROJECT_NOTES.md / "Product note on --un-remove" -- user-confirmed
    2026-08-06: the comparison should be "visible/active screens only,"
    not Removed-list bookkeeping; Restore-from-Backup is the way back
    if a deployed result isn't wanted, not an un-remove workflow).
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.stage = "ready"  # ready -> written -> waiting -> reconnected
        self.verify_lines = None   # describe_screen_changes() result, set by on_check()
        self.verify_error = None   # str if post-write verification itself failed to run

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="Deploy to Device")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.status_text = wx.StaticText(self, label="")
        outer.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        # Post-write verification output (v0.14.0) -- only populated
        # once self.stage == "reconnected"; empty/hidden-by-content
        # otherwise. Same read-only multiline style as PreflightPanel's
        # diff_text.
        self.verify_text = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.HSCROLL
        )
        outer.Add(self.verify_text, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.write_btn = wx.Button(self, label="Write to Device (NewFiles) →")
        self.write_btn.Bind(wx.EVT_BUTTON, self.on_write)
        outer.Add(self.write_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        eject_row = wx.BoxSizer(wx.HORIZONTAL)
        self.eject_auto_btn = wx.Button(self, label="Eject Now (diskutil) →")
        self.eject_auto_btn.Bind(wx.EVT_BUTTON, self.on_eject_auto)
        eject_row.Add(self.eject_auto_btn, 0, wx.RIGHT, 8)
        self.eject_manual_btn = wx.Button(self, label="I Ejected It Myself →")
        self.eject_manual_btn.Bind(wx.EVT_BUTTON, self.on_eject_manual)
        eject_row.Add(self.eject_manual_btn, 0)
        outer.Add(eject_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.check_btn = wx.Button(self, label="Check for Reconnected Device")
        self.check_btn.Bind(wx.EVT_BUTTON, self.on_check)
        outer.Add(self.check_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        self.done_btn = wx.Button(self, label="Done -- Back to Profile List")
        self.done_btn.Bind(wx.EVT_BUTTON, self.on_done)
        outer.Add(self.done_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        self.back_btn = wx.Button(self, label="‹ Back to Review")
        self.back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(self.back_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active -- always starts fresh."""
        self.stage = "ready"
        self.verify_lines = None
        self.verify_error = None
        # Label reflects wherever "Back" will actually go -- see
        # frame.deploy_return_panel / on_back().
        if self.frame.deploy_return_panel == "restore":
            self.back_btn.SetLabel("‹ Back to Backup List")
        elif self.frame.deploy_return_panel == "clone":
            self.back_btn.SetLabel("‹ Back to Clone Setup")
        else:
            self.back_btn.SetLabel("‹ Back to Review")
        self._refresh()

    def _refresh(self):
        working_path = self.frame.editing_path
        profile = self.frame.profile_filename
        is_macos = platform.system() == "Darwin"

        if self.stage == "ready":
            self.status_text.SetLabel(
                f"Ready to write the reviewed working copy to the device as "
                f"\"{profile}\".\n\nMake sure the device is still connected "
                f"before continuing."
            )
            self.write_btn.Enable(working_path is not None)
            self.eject_auto_btn.Disable()
            self.eject_manual_btn.Disable()
            self.check_btn.Disable()
            self.done_btn.Disable()
            self.verify_text.SetValue("")

        elif self.stage == "written":
            self.status_text.SetLabel(
                "Write complete and verified byte-for-byte. It is now safe "
                "to eject the Garmin.\n\nThe device will restart "
                "automatically once ejected -- that's when the NewFiles "
                "import actually happens.\n\n"
                ">>> Once the automatic restart finishes, the device will "
                "NOT remount on its own -- press the power button ONCE to "
                "bring it back into mass-storage mode. Without that press "
                "it settles into charging mode instead."
            )
            self.write_btn.Disable()
            self.eject_auto_btn.Enable(is_macos)
            self.eject_manual_btn.Enable()
            self.check_btn.Disable()
            self.done_btn.Disable()
            self.verify_text.SetValue("")

        elif self.stage == "waiting":
            self.status_text.SetLabel(
                "Waiting for the device to reconnect.\n\nOnce its automatic "
                "restart finishes, press the power button ONCE to bring it "
                "back into mass-storage mode, then click Check for "
                "Reconnected Device."
            )
            self.write_btn.Disable()
            self.eject_auto_btn.Disable()
            self.eject_manual_btn.Disable()
            self.check_btn.Enable()
            self.done_btn.Disable()
            self.verify_text.SetValue("")

        elif self.stage == "reconnected":
            if self.verify_error is not None:
                self.status_text.SetLabel(
                    f"Reconnected. The device has re-imported \"{profile}\" "
                    f"from NewFiles.\n\nCouldn't automatically verify the "
                    f"result: {self.verify_error}\n\nSpot-check manually via "
                    f"View Screens (re-stage the profile) or "
                    f"garmin_device.py's screens command, then click Done."
                )
                self.verify_text.SetValue("")
            elif self.verify_lines:
                self.status_text.SetLabel(
                    f"Reconnected. The device has re-imported \"{profile}\" "
                    f"from NewFiles.\n\n{len(self.verify_lines)} screen(s) on "
                    f"the device differ from what was sent:"
                )
                self.verify_text.SetValue("\n\n".join(self.verify_lines))
            else:
                self.status_text.SetLabel(
                    f"Reconnected. The device has re-imported \"{profile}\" "
                    f"from NewFiles, and it matches what was sent -- every "
                    f"screen on the device is exactly what you set up."
                )
                self.verify_text.SetValue("(no differences)")
            self.write_btn.Disable()
            self.eject_auto_btn.Disable()
            self.eject_manual_btn.Disable()
            self.check_btn.Disable()
            self.done_btn.Enable()

        self.frame._relayout()

    def on_write(self, event):
        root = self.frame.garmin_root
        if root is None:
            wx.MessageBox(
                "No device detected yet -- go back to Detect and connect "
                "the Garmin first.",
                "Not connected", wx.OK | wx.ICON_ERROR,
            )
            return
        try:
            garmin_device.write_to_newfiles(
                root, self.frame.editing_path, self.frame.profile_filename
            )
        except garmin_device.GarminDeviceError as e:
            wx.MessageBox(str(e), "Write failed", wx.OK | wx.ICON_ERROR)
            return
        except OSError as e:
            wx.MessageBox(f"Write failed: {e}", "Write failed", wx.OK | wx.ICON_ERROR)
            return

        self.stage = "written"
        self._refresh()

    def on_eject_auto(self, event):
        eject_target = garmin_device._volume_mount_point(self.frame.garmin_root)
        answer = wx.MessageBox(
            f"Eject '{eject_target}' now?\n\nThe device will restart "
            f"automatically, which is when the NewFiles import happens.",
            "Eject device", wx.YES_NO | wx.ICON_QUESTION,
        )
        if answer != wx.YES:
            return
        try:
            subprocess.run(["diskutil", "eject", eject_target], check=True)
        except (subprocess.CalledProcessError, OSError) as e:
            wx.MessageBox(
                f"Eject failed: {e}\n\nEject it yourself (Finder) and click "
                f"\"I Ejected It Myself\" instead.",
                "Eject failed", wx.OK | wx.ICON_ERROR,
            )
            return

        self.stage = "waiting"
        self._refresh()

    def on_eject_manual(self, event):
        self.stage = "waiting"
        self._refresh()

    def on_check(self, event):
        root = garmin_device.find_garmin_root()
        if root is None:
            wx.MessageBox(
                "Device not detected yet. If you haven't pressed the power "
                "button since the restart finished, do that first, then "
                "check again.",
                "Not reconnected yet", wx.OK | wx.ICON_INFORMATION,
            )
            return

        self.frame.garmin_root = root

        # Post-write verification (v0.14.0): re-pull the LIVE profile
        # straight from the device and compare it against what was
        # actually sent (editing_path), via the same
        # describe_screen_changes() the Preflight panel uses -- see
        # class docstring for why that's safe to run unconditionally
        # here (it only ever reports on ACTIVE screens, so the
        # device's own Removed-list wipe on NewFiles import never
        # shows up as a false "difference").
        live_path = os.path.join(root, garmin_device.SPORTS_SUBDIR, self.frame.profile_filename)
        try:
            self.verify_lines = describe_screen_changes(self.frame.editing_path, live_path)
            self.verify_error = None
        except Exception as e:
            self.verify_lines = None
            self.verify_error = str(e)

        self.stage = "reconnected"
        self._refresh()

    def on_done(self, event):
        self.frame.discard_edits()
        self.frame.show_panel("profiles")

    def on_back(self, event):
        # "Back" goes wherever this Deploy was reached FROM -- the
        # normal edit flow's PreflightPanel ("review"), or straight
        # back to the backup picker ("restore") if that's how we got
        # here. See frame.deploy_return_panel.
        self.frame.show_panel(self.frame.deploy_return_panel)


def _format_backup_timestamp(timestamp_str):
    """
    backup_profiles()'s raw folder-name timestamp ("%Y%m%d_%H%M%S") ->
    a human-readable string ("2026-08-06 09:00:00"). Falls back to the
    raw string unchanged if it's ever not in the expected format,
    rather than raising and breaking the whole Restore list over a
    display nicety.
    """
    try:
        return datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return timestamp_str


class RestorePanel(wx.Panel):
    """
    Restore-from-backup picker (step 4 side path / task from
    MVP_SCOPE.md "Restore from backup"): lists every backup of the
    selected profile (garmin_device.list_backup_history(), newest
    first, de-duplicated), with a quick screen-type summary per
    candidate so a user can recognize which backup they want without
    leaving this panel. Reached from ProfileListPanel's "Restore from
    Backup..." button -- a separate path from Stage/edit, not
    something that runs through EditScreenPanel/PreflightPanel at all.

    Mechanically a restore IS a deploy -- see MVP_SCOPE.md / "Restore
    from backup": "a restore is identical to a normal deploy, just
    sourced from an old backup file instead of a freshly patched one."
    So "Restore This Backup" just points frame.editing_path at the
    chosen backup file directly (never copied -- DeployPanel/
    describe_screen_changes() only ever READ editing_path, they never
    write to it, so there's nothing to protect the backup file from)
    and hands off straight to DeployPanel (step 9), skipping
    PreflightPanel entirely -- there's no "changes since staging" to
    review here (the user just picked a specific, known backup from a
    list with its contents already summarized on this panel), and
    PreflightPanel's staged-vs-editing diff logic doesn't apply to a
    restore anyway (there's no "staged" file in this flow). DeployPanel
    and its post-write verification work completely unchanged either
    way -- both only care that frame.editing_path points at real .fit
    bytes, not how it got set.
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self.rows = []  # row index -> (timestamp, backup_path)

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="Restore from Backup")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.status_text = wx.StaticText(self, label="")
        outer.Add(self.status_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        # v0.16.6 FIX: ScreensListCtrl (not a plain wx.ListCtrl) -- this
        # list has the exact same best-size-propagation exposure as
        # ViewScreensPanel's Fields column (a profile with many/long
        # screen-type names could inflate the frame the same way), and
        # had never gotten even the v0.16.3 ceiling attempt -- applying
        # the correct fix here proactively rather than waiting for a
        # separate bug report. See ScreensListCtrl's definition (above
        # ViewScreensPanel) for the full explanation.
        self.history_list = ScreensListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.history_list.InsertColumn(0, "Backup Date/Time", width=160)
        self.history_list.InsertColumn(1, "Screens", width=400)
        self.history_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_row_selected)
        self.history_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_row_deselected)
        outer.Add(self.history_list, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(self, label="‹ Back to Profile List")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)
        self.restore_btn = wx.Button(self, label="Restore This Backup →")
        self.restore_btn.Disable()
        self.restore_btn.Bind(wx.EVT_BUTTON, self.on_restore)
        button_row.Add(self.restore_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active -- always re-reads from disk."""
        self._refresh()

    def _refresh(self):
        profile = self.frame.profile_filename
        self.history_list.DeleteAllItems()
        self.rows = []
        self.restore_btn.Disable()

        if not profile:
            self.title_text.SetLabel("Restore from Backup")
            self.status_text.SetLabel("No profile selected -- go back and select one first.")
            self.frame._relayout()
            return

        self.title_text.SetLabel(f"Restore from Backup -- {profile}")

        history = garmin_device.list_backup_history(self.frame.working_dir, profile)
        if not history:
            self.status_text.SetLabel(
                f"No backups of \"{profile}\" found yet under {self.frame.working_dir} -- "
                f"visiting the profile list backs up automatically, so this shouldn't "
                f"normally happen if you got here from there."
            )
            self.frame._relayout()
            return

        self.status_text.SetLabel(
            f"{len(history)} backup(s) found, newest first. Select one, then Restore."
        )

        for timestamp, backup_path in history:
            try:
                data = classify_screens(decode_file(backup_path))
                names = [screen_type_name(m.get(10)) or "?" for f9, idx, m in data["orderable"]]
                summary = f"{len(names)} screen(s): " + ", ".join(names)
            except Exception as e:
                summary = f"(couldn't read this backup: {e})"

            row = self.history_list.InsertItem(
                self.history_list.GetItemCount(), _format_backup_timestamp(timestamp)
            )
            self.history_list.SetItem(row, 1, summary)
            self.rows.append((timestamp, backup_path))

        # Same auto-size-never-below-a-floor fix as ViewScreensPanel's
        # Fields column (v0.11.1) -- a profile with many screens would
        # otherwise clip here too.
        self.history_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        if self.history_list.GetColumnWidth(1) < 400:
            self.history_list.SetColumnWidth(1, 400)

        self.frame._relayout()

    def on_row_selected(self, event):
        self.restore_btn.Enable()

    def on_row_deselected(self, event):
        self.restore_btn.Disable()

    def on_restore(self, event):
        sel = self.history_list.GetFirstSelected()
        if sel == -1:
            return
        timestamp, backup_path = self.rows[sel]

        answer = wx.MessageBox(
            f"This will write the backup from {_format_backup_timestamp(timestamp)} "
            f"to the device, REPLACING what's currently on it as "
            f"\"{self.frame.profile_filename}\".\n\nContinue?",
            "Restore from backup", wx.YES_NO | wx.ICON_WARNING,
        )
        if answer != wx.YES:
            return

        self.frame.editing_path = backup_path
        self.frame.deploy_return_panel = "restore"
        self.frame.show_panel("deploy")

    def on_back(self, event):
        # Belt-and-suspenders cleanup (2026-08-06, real bug found via
        # testing): frame.deploy_return_panel is ONLY ever set to
        # "restore" by on_restore() above, so if it's set to that
        # right now, any current frame.editing_path is guaranteed to
        # be a leftover from a restore that was started but abandoned
        # (backed out via DeployPanel/here rather than clicking Done)
        # -- safe and correct to discard immediately rather than
        # leaving it to leak into whatever the user does next.
        # ProfileListPanel.on_stage() also discards unconditionally as
        # the actual fix for the reported symptom; this just cleans up
        # sooner, before the user even gets back to the profile list.
        if self.frame.deploy_return_panel == "restore":
            self.frame.discard_edits()
            self.frame.deploy_return_panel = "review"
        self.frame.show_panel("profiles")


class ClonePanel(wx.Panel):
    """
    Clone Profile: patches sport_mesgs[0].name via
    fit_clone_profile.py's patch_profile_name() (a standard, SDK-known
    message, unlike data_screen -- a completely different code path
    from every other panel in this app) and deploys the result under a
    NEW filename. CONFIRMED full-fidelity on real hardware already, at
    the CLI level -- see MVP_SCOPE.md / "Clone-and-retarget": the
    source profile is left completely untouched, and the clone is
    screen-for-screen identical (all reorderable/conditional slots,
    content, order, layout, flags). Reached from ProfileListPanel's
    "Clone..." button, a sibling action to Stage/Restore.

    The one hard constraint (per fit_clone_profile.py's own docstring):
    the clone MUST be deployed under a filename that does NOT match
    any EXISTING profile on the device -- deploying under an existing
    filename OVERWRITES that profile instead of creating a new one.
    This panel enforces that live, before "Create Clone" is even
    enabled, via frame.known_profiles (kept in sync by
    ProfileListPanel.on_refresh() every time that panel is shown).

    Sources the clone from the SELECTED profile's just-taken backup
    (frame.clone_source_backup_path, set by ProfileListPanel.on_clone()
    at the same moment as frame.known_profiles is guaranteed fresh) --
    same "always clone from a backup, never touch the live device file
    directly" discipline as Stage and Restore.

    Like RestorePanel, this hands off straight to DeployPanel (steps
    9-10) once Create Clone succeeds -- there's no staged-vs-editing
    diff to review for a clone either. frame.profile_filename is set
    to the NEW filename here (the deploy target), NOT the source's --
    DeployPanel and post-write verification both key off it as
    "whatever frame.editing_path should end up being on the device."
    """

    def __init__(self, parent, frame):
        super().__init__(parent)
        self.frame = frame
        self._filename_dirty = False  # True once the user has typed directly into the filename field -- stops name->filename auto-suggestion from overwriting a deliberate choice

        outer = wx.BoxSizer(wx.VERTICAL)

        self.title_text = wx.StaticText(self, label="Clone Profile")
        title_font = self.title_text.GetFont()
        title_font.PointSize += 2
        title_font = title_font.Bold()
        self.title_text.SetFont(title_font)
        outer.Add(self.title_text, 0, wx.ALL | wx.EXPAND, 12)

        self.source_text = wx.StaticText(self, label="")
        outer.Add(self.source_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        name_row = wx.BoxSizer(wx.HORIZONTAL)
        name_row.Add(wx.StaticText(self, label="New display name (shown on-device):"), 0,
                     wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.name_text = wx.TextCtrl(self)
        self.name_text.Bind(wx.EVT_TEXT, self.on_name_text)
        name_row.Add(self.name_text, 1)
        outer.Add(name_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        filename_row = wx.BoxSizer(wx.HORIZONTAL)
        filename_row.Add(wx.StaticText(self, label="New filename (on the device):"), 0,
                          wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.filename_text = wx.TextCtrl(self)
        self.filename_text.Bind(wx.EVT_TEXT, self.on_filename_text)
        filename_row.Add(self.filename_text, 1)
        outer.Add(filename_row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        self.validation_text = wx.StaticText(self, label="")
        outer.Add(self.validation_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 12)

        button_row = wx.BoxSizer(wx.HORIZONTAL)
        back_btn = wx.Button(self, label="‹ Back to Profile List")
        back_btn.Bind(wx.EVT_BUTTON, self.on_back)
        button_row.Add(back_btn, 0, wx.RIGHT, 8)
        self.create_btn = wx.Button(self, label="Create Clone →")
        self.create_btn.Disable()
        self.create_btn.Bind(wx.EVT_BUTTON, self.on_create)
        button_row.Add(self.create_btn, 0)
        outer.Add(button_row, 0, wx.ALL, 12)

        self.SetSizer(outer)

    def on_show(self):
        """Called by MainFrame every time this panel becomes active -- always starts fresh."""
        source = self.frame.clone_source_filename
        self.title_text.SetLabel("Clone Profile")
        self.source_text.SetLabel(
            f"Cloning: {source}" if source else "No source profile selected -- go back and pick one first."
        )
        self.name_text.ChangeValue("")
        self.filename_text.ChangeValue("")
        self._filename_dirty = False
        self._update_validation()
        self.frame._relayout()

    def _suggest_filename(self, name):
        """
        Turn a display name into a plausible filename: strip to
        alphanumerics only (Garmin's own filenames are plain
        alphanumeric, e.g. CyclingRoadSandbox.fit -- no spaces or
        punctuation), cap length generously, add the extension. Purely
        a starting point -- the user can freely overwrite it, and
        the moment they type into the filename field directly this
        stops auto-updating (see _filename_dirty).
        """
        cleaned = "".join(c for c in name if c.isalnum())
        if not cleaned:
            return ""
        return cleaned[:40] + ".fit"

    def on_name_text(self, event):
        if not self._filename_dirty:
            # ChangeValue(), not SetValue() -- deliberately does NOT
            # fire EVT_TEXT, so this auto-fill doesn't mark the
            # filename field "dirty" itself.
            self.filename_text.ChangeValue(self._suggest_filename(self.name_text.GetValue()))
        self._update_validation()

    def on_filename_text(self, event):
        self._filename_dirty = True
        self._update_validation()

    def _filename_problem(self, filename):
        """Returns a human-readable problem string, or None if filename is OK to use."""
        if not filename:
            return "Enter a filename for the new profile."
        if "/" in filename or "\\" in filename:
            return "Filename can't contain path separators."
        if not filename.lower().endswith(".fit"):
            return "Filename must end in .fit"
        # Case-insensitive: the device's filesystem (FAT/exFAT) treats
        # filenames case-insensitively, so "sandbox.fit" and
        # "Sandbox.FIT" collide even though they're not an exact
        # string match.
        known_lower = {f.lower() for f in self.frame.known_profiles}
        if filename.lower() in known_lower:
            return (
                f"\"{filename}\" already exists on the device -- deploying under "
                f"an existing profile's filename OVERWRITES that profile instead "
                f"of creating a new one. Choose a filename that doesn't match any "
                f"profile currently on the device."
            )
        return None

    def _update_validation(self):
        new_name = self.name_text.GetValue().strip()
        new_filename = self.filename_text.GetValue().strip()

        if not new_name:
            problem = "Enter a display name for the clone."
        else:
            problem = self._filename_problem(new_filename)

        if problem:
            self.validation_text.SetLabel(problem)
            self.create_btn.Disable()
        else:
            self.validation_text.SetLabel(
                f"Will create a new profile on the device as \"{new_filename}\", "
                f"showing as \"{new_name}\" on-device -- the source profile is "
                f"left completely untouched."
            )
            self.create_btn.Enable()

        self.frame._relayout()

    def on_create(self, event):
        new_name = self.name_text.GetValue().strip()
        new_filename = self.filename_text.GetValue().strip()
        if not new_name or self._filename_problem(new_filename):
            return  # Create is disabled in this state, but guard anyway

        if self.frame.clone_source_backup_path is None:
            wx.MessageBox(
                "No source profile backup on hand -- go back and select a "
                "profile to clone first.",
                "Can't clone", wx.OK | wx.ICON_ERROR,
            )
            return

        staging_dir = os.path.join(self.frame.working_dir, "staging")
        os.makedirs(staging_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = os.path.splitext(new_filename)[0]
        output_path = os.path.join(staging_dir, f"{stem}_clone_{timestamp}.fit")

        try:
            patch_profile_name(self.frame.clone_source_backup_path, output_path, new_name)
        except (ValueError, KeyError) as e:
            wx.MessageBox(f"Clone failed: {e}", "Error", wx.OK | wx.ICON_ERROR)
            return
        except OSError as e:
            wx.MessageBox(f"Clone failed: {e}", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.frame.editing_path = output_path
        self.frame.profile_filename = new_filename
        self.frame.deploy_return_panel = "clone"
        self.frame.show_panel("deploy")

    def on_back(self, event):
        # Same belt-and-suspenders cleanup as RestorePanel.on_back()
        # (see its comment for the full reasoning): frame.
        # deploy_return_panel is ONLY ever set to "clone" by
        # on_create() above, so if it's set to that right now, any
        # current frame.editing_path/profile_filename are leftovers
        # from a clone attempt that was started but abandoned --
        # discard immediately.
        if self.frame.deploy_return_panel == "clone":
            self.frame.discard_edits()
            self.frame.deploy_return_panel = "review"
        self.frame.show_panel("profiles")


class MainFrame(wx.Frame):
    """
    Owns app-wide state (garmin_root, working_dir) and swaps between
    panel instances as the user moves through the flow, rather than
    opening a new top-level window per step.

    Layout note (v0.1.1 fix, still in effect): wx widgets don't
    automatically resize their container when their content changes.
    _relayout() must be called after any change to what's on screen --
    skipping this was the cause of the original button/text overlap
    bug in v0.1.0. v0.11.0: _relayout() now only GROWS the window when
    needed, never shrinks it -- see _relayout()'s own docstring for why
    (a manually-enlarged window was snapping back to a smaller size on
    every button click).
    """

    def __init__(self):
        super().__init__(None, title=f"Activity Profile Screen Editor for Garmin Edge v{__version__}")

        self.garmin_root = None
        self.working_dir = load_saved_working_dir() or DEFAULT_WORKING_DIR
        self.staged_path = None
        self.profile_filename = None
        self.editing_path = None   # scratch working copy -- IS the pending-edit queue, see module docstring
        self.editing_slot = None   # message_index of whatever screen EditScreenPanel is currently open on
        self.deploy_return_panel = "review"  # where DeployPanel's "Back" goes -- "review" (normal edit flow), "restore" (arrived via Restore-from-Backup), or "clone" (arrived via Clone) -- the latter two skip PreflightPanel entirely
        self.known_profiles = {}  # filename -> latest backup path, refreshed by ProfileListPanel.on_refresh() -- lets ClonePanel validate a new filename doesn't collide with anything currently on the device
        self.clone_source_filename = None      # set by ProfileListPanel.on_clone()
        self.clone_source_backup_path = None   # set by ProfileListPanel.on_clone()

        self.container = wx.Panel(self)
        self.container_sizer = wx.BoxSizer(wx.VERTICAL)
        self.container.SetSizer(self.container_sizer)

        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(self.container, 1, wx.EXPAND)
        self.SetSizer(frame_sizer)

        self.panels = {
            "detect": DetectPanel(self.container, self),
            "profiles": ProfileListPanel(self.container, self),
            "screens": ViewScreensPanel(self.container, self),
            "edit_screen": EditScreenPanel(self.container, self),
            "add_screen": AddScreenPanel(self.container, self),
            "review": PreflightPanel(self.container, self),
            "deploy": DeployPanel(self.container, self),
            "restore": RestorePanel(self.container, self),
            "clone": ClonePanel(self.container, self),
        }
        for panel in self.panels.values():
            self.container_sizer.Add(panel, 1, wx.EXPAND)
            panel.Hide()

        self.CreateStatusBar()
        self.SetStatusText("Ready.")

        self.current_panel_name = None
        self.show_panel("detect")

        # Floor so the window doesn't start (or shrink back to) an
        # awkwardly cramped size -- Fit() calls after this still
        # respect it as a lower bound.
        self.SetMinSize((480, 320))

    def get_working_path(self):
        """
        The file everything downstream should read: the scratch
        editing copy if any screen has been edited this session,
        otherwise the pristine staged file. See module docstring --
        editing_path IS the pending-edit queue.
        """
        return self.editing_path if self.editing_path is not None else self.staged_path

    def discard_edits(self):
        """Drop the scratch working copy -- back to the pristine staged file."""
        self.editing_path = None

    def show_panel(self, name):
        for pname, panel in self.panels.items():
            panel.Show(pname == name)
        self.current_panel_name = name
        self.panels[name].on_show()
        self._relayout()

    def _relayout(self):
        """
        Re-run the sizer layout, growing the window if the active
        panel's content now needs more room than it currently has --
        but never shrinking it. Must be called after ANY change to a
        panel's visible content.

        v0.11.0 FIX: this used to call self.Fit(), which unconditionally
        resizes the frame to the sizer's calculated ideal size --
        including SHRINKING it. Reported real-world impact: a user
        manually enlarged the window to see the full screens list
        (e.g. more than the ListCtrl's default ~6-row best-size guess),
        then had it snap back to that smaller size the moment ANY
        button triggered a refresh (which is most of them -- nearly
        every handler in this file ends with self.frame._relayout()).
        Fit() was originally added in v0.1.1 to fix a DIFFERENT bug
        (content overlapping because the window was too SMALL for new
        content) -- growing when needed was always the actual intent;
        shrinking a window the user deliberately made bigger was never
        the goal, just an unwanted side effect of using Fit() for it.
        GetBestSize() returns the same value Fit() would have resized
        to; taking max(best, current) per dimension keeps that original
        anti-overlap behavior while respecting a manual enlargement.

        v0.16.2 FIX: clamp the grow direction to the current display's
        usable work area. Real reported bug: a screen with an unresolved
        field ID made EditScreenPanel's field list report an inflated
        best-size (see EditScreenPanel.refresh_from_file()'s fix note --
        now fixed at the source), and because this method only ever
        grows, that pushed the window off the left edge of the screen,
        permanently, with no way back short of a manual resize. That
        specific content bug is fixed, but "only grow, never shrink" by
        itself has no ceiling -- any future panel that transiently
        reports too large a best-size would reproduce the same
        off-screen lockout. Capping growth to the display's own client
        area (never smaller than the window's un-clamped current size,
        so this never FORCES a shrink either -- it only stops further
        growth once the screen's edge is reached) turns "window
        unusable until restarted" into, at worst, "some content is
        tight/scrolled" -- a real degradation, but a recoverable one.
        Falls back to the primary display if the frame isn't fully
        within any single display's bounds (GetFromWindow() can return
        wx.NOT_FOUND then, e.g. a window already straddling two
        displays or partly off-screen already).
        """
        self.container.Layout()
        self.Layout()
        best = self.GetBestSize()
        current = self.GetSize()
        new_size = wx.Size(max(best.width, current.width), max(best.height, current.height))

        display_index = wx.Display.GetFromWindow(self)
        if display_index == wx.NOT_FOUND:
            display_index = 0
        try:
            client_area = wx.Display(display_index).GetClientArea()
            max_w = max(client_area.width - 40, current.width)
            max_h = max(client_area.height - 40, current.height)
            new_size = wx.Size(min(new_size.width, max_w), min(new_size.height, max_h))
        except Exception:
            # Belt-and-suspenders only -- if display info is ever
            # unavailable for some reason, fall back to the un-clamped
            # grow-only behavior rather than crash the refresh.
            pass

        if new_size != current:
            self.SetSize(new_size)


class GarminEditorApp(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = GarminEditorApp()
    try:
        app.MainLoop()
    except wx._core.wxAssertionError:
        # v0.5.2: this specific assertion ("tlw" failed in
        # DoScreenToClient -- TopLevel Window missing) can still fire
        # deep inside wx's OWN internal event pump during teardown on
        # macOS, even with the per-panel IsBeingDeleted() guards added
        # in v0.4.1 (those cover our own EVT_SIZE/EVT_PAINT handlers on
        # LayoutDiagramPanel; this one isn't coming from our code -- it
        # happens at app.MainLoop() itself, after the window is already
        # gone). Confirmed to recur intermittently despite the v0.4.1
        # fix, so rather than chase an unreachable stack frame inside
        # wx's C++ layer, just swallow it here: by the time it fires the
        # GUI has already fully closed, so this is cosmetic-only (an
        # ugly traceback on exit), not a sign anything failed to save or
        # clean up.
        pass
