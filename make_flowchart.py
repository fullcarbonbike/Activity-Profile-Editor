#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__version__ = "2.0.0"  # THREE PAGES, LETTER PORTRAIT, AND HEIGHTS THAT ARE MEASURED (2026-10-28, Doug: the one-page A3 version "feels compressed and is hard to read"). v1.0.0 put the whole decision tree on one A3 sheet at 7.6pt body text; readable on a screen at 200%, not readable on paper. Now: page 1 is the branch and a mode-comparison table, page 2 is device mode top to bottom, page 3 is offline mode, at 9.6pt. THE REAL FIX WAS measure(): v1.0.0 hand-guessed every box height, which survived A3 by luck and spilled text past six borders the moment the type got bigger. measure() mirrors box()'s own cursor arithmetic and step() sizes from content -- change one, change both. Caught by rendering each page to PNG and looking at it, not by reading the code. ROOT DECISION IS DELIBERATE: the chart branches on "does the Edge mount as a disk?", not on the model number. Model numbers appear as a hint because that is how people think about it, but 530-vs-840 is a proxy for mass-storage-vs-MTP, the mount test is what find_garmin_root() actually does, and offline mode is also correct for a mass-storage Edge with nothing plugged in -- which a model-based question gets wrong. Needs reportlab; it is the only non-stdlib dependency in the repo and it is a DOC tool, not part of the app.

"""Regenerate GUI_FLOWCHART.pdf.

Usage:  python3 make_flowchart.py

Panel behaviour here was read out of gui_app.py, not recalled -- notably
that Restore is hidden offline, which is easy to assume works.
"""
import os, math
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

W, H = letter
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GUI_FLOWCHART.pdf")
c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle("Activity Profile Editor for Garmin Edge - GUI flow")

INK=(0.12,0.13,0.15); MUTE=(0.42,0.45,0.50)
DEV=(0.08,0.34,0.58); OFF=(0.60,0.32,0.04)
STOP=(0.58,0.12,0.12); GREEN=(0.09,0.40,0.25)
PALE_D=(0.937,0.957,0.988); PALE_O=(0.999,0.969,0.918)

M = 17*mm                      # page margin
CW = W - 2*M                   # content width

def wrap(txt, font, size, w):
    return simpleSplit(txt, font, size, w)

def measure(w, title, lines=(), ts=12, bs=9.6, lead=4.0):
    """Exact height box() needs. Mirrors box()'s cursor arithmetic --
    if you change one, change both. Guessing these by eye is what made
    every step on page 2 spill past its own border."""
    h = ts + 3
    if title:
        h += len(wrap(title, "Helvetica-Bold", ts, w-14)) * (ts + 2) + 3
    for raw in lines:
        bold = raw.startswith("*"); t = raw[1:] if bold else raw
        if not t.strip():
            h += bs*0.55; continue
        f = "Helvetica-Bold" if bold else "Helvetica"
        h += len(wrap(t, f, bs, w-16)) * (bs + lead)
    return h + 5


def box(x, y, w, h, title, lines=(), accent=INK, fill=(1,1,1), dash=None,
        ts=12, bs=9.6, lead=4.0, radius=4):
    c.saveState(); c.setLineWidth(1.3)
    c.setStrokeColorRGB(*accent); c.setFillColorRGB(*fill)
    if dash: c.setDash(*dash)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1); c.setDash()
    ty = y + h - (ts + 3)
    if title:
        c.setFillColorRGB(*accent); c.setFont("Helvetica-Bold", ts)
        for ln in wrap(title, "Helvetica-Bold", ts, w-14):
            c.drawString(x+7, ty, ln); ty -= ts + 2
        ty -= 3
    c.setFillColorRGB(*INK)
    for raw in lines:
        bold = raw.startswith("*"); s = raw[1:] if bold else raw
        f = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(f, bs)
        if not s.strip():
            ty -= bs*0.55; continue
        for ln in wrap(s, f, bs, w-16):
            c.drawString(x+8, ty, ln); ty -= bs + lead
    c.restoreState()
    return y

def diamond(cx, cy, w, h, text, accent=INK, size=11.5):
    c.saveState(); c.setLineWidth(1.4); c.setStrokeColorRGB(*accent)
    c.setFillColorRGB(1,1,1)
    p=c.beginPath(); p.moveTo(cx,cy+h/2); p.lineTo(cx+w/2,cy)
    p.lineTo(cx,cy-h/2); p.lineTo(cx-w/2,cy); p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.setFillColorRGB(*accent); c.setFont("Helvetica-Bold", size)
    ls = wrap(text, "Helvetica-Bold", size, w-60)
    ty = cy + (len(ls)-1)*(size+2)/2
    for ln in ls:
        c.drawCentredString(cx, ty-size*0.36, ln); ty -= size+2
    c.restoreState()

def arrow(x1,y1,x2,y2,label=None,accent=MUTE,lw=1.3,lab_dx=0,lab_dy=0,ls=9.5):
    c.saveState(); c.setStrokeColorRGB(*accent); c.setLineWidth(lw)
    c.line(x1,y1,x2,y2)
    a=math.atan2(y2-y1,x2-x1); L=6.5
    c.setFillColorRGB(*accent)
    p=c.beginPath(); p.moveTo(x2,y2)
    p.lineTo(x2-L*math.cos(a-0.40), y2-L*math.sin(a-0.40))
    p.lineTo(x2-L*math.cos(a+0.40), y2-L*math.sin(a+0.40)); p.close()
    c.drawPath(p,stroke=0,fill=1)
    if label:
        c.setFont("Helvetica-Bold", ls); c.setFillColorRGB(*accent)
        c.drawCentredString((x1+x2)/2+lab_dx, (y1+y2)/2+lab_dy, label)
    c.restoreState()

def header(title, sub, accent=INK):
    c.setFillColorRGB(*accent); c.setFont("Helvetica-Bold", 17)
    c.drawString(M, H-20*mm, title)
    c.setFillColorRGB(*MUTE); c.setFont("Helvetica", 10)
    y = H-26*mm
    for ln in wrap(sub, "Helvetica", 10, CW):
        c.drawString(M, y, ln); y -= 12
    c.setStrokeColorRGB(0.86,0.87,0.89); c.setLineWidth(0.9)
    c.line(M, y-1, W-M, y-1)
    return y - 9*mm

def footer(page, note):
    c.setFont("Helvetica-Oblique", 8); c.setFillColorRGB(*MUTE)
    c.drawString(M, 12*mm, "Activity Profile Editor for Garmin Edge · v1.7.5 · 2026-10-28")
    c.drawCentredString(W/2, 12*mm, note)
    c.drawRightString(W-M, 12*mm, f"page {page} of 3")

# =====================================================================
# PAGE 1 -- which mode
# =====================================================================
y = header("Which path do I take?",
  "The toolkit works two ways, and which one you get depends on how your Edge connects to the computer — not on how old it is. "
  "Model numbers are a useful hint; the mount behaviour is the actual test.")

bh = 14*mm
box(M+CW*0.18, y-bh, CW*0.64, bh, "Launch  gui_app.py  \u2014  the \u201cDetect\u201d screen",
    accent=INK, fill=(0.955,0.957,0.965), ts=13)
arrow(W/2, y-bh, W/2, y-bh-9*mm)

# Diamond kept narrow enough that its text clears the sloping sides;
# the qualifier sits BELOW it rather than inside, which is what made
# the first draft overflow its own shape.
dy = y-bh-9*mm-19*mm
diamond(W/2, dy, CW*0.62, 38*mm, "Does your Edge show up as a disk?", size=13)
c.setFont("Helvetica", 9.6); c.setFillColorRGB(*MUTE)
c.drawCentredString(W/2, dy-23*mm, "a volume on macOS  \u00b7  a drive letter on Windows")

lx, rx = M + CW*0.245, W - M - CW*0.245
ay = dy
arrow(W/2-CW*0.31, ay, lx, ay, accent=DEV)
arrow(W/2+CW*0.31, ay, rx, ay, accent=OFF)
c.setFont("Helvetica-Bold", 11)
c.setFillColorRGB(*DEV); c.drawCentredString((W/2-CW*0.31+lx)/2, ay+4*mm, "YES")
c.setFillColorRGB(*OFF); c.drawCentredString((W/2+CW*0.31+rx)/2, ay+4*mm, "NO")
# Clear the diamond's lower point (19mm) AND the caption under it
# before dropping into the mode boxes -- the first pass put the boxes
# 13mm below the diamond's CENTRE, so they covered its bottom half.
top = ay - 31*mm
arrow(lx, ay, lx, top, accent=DEV)
arrow(rx, ay, rx, top, accent=OFF)

MW = CW*0.47
D_LINES = ["*Press \u201cList Profiles \u2192\u201d", "",
           "Edge 530 and other USB Mass Storage models.", "",
           "The toolkit reads and writes the device itself, and can verify the write afterwards.", "",
           "*\u2192  see page 2"]
O_LINES = ["*Press \u201cWork Without a Device...\u201d", "",
           "Edge 840 (tested); 540 / 1040 / 1050 reported MTP. Also the right mode for ANY Edge with nothing plugged in.", "",
           "You move the file onto the device yourself.", "",
           "*\u2192  see page 3"]
MH = max(44*mm, measure(MW, "DEVICE MODE", D_LINES), measure(MW, "OFFLINE MODE", O_LINES))
box(lx-MW/2, top-MH, MW, MH, "DEVICE MODE",  D_LINES, accent=DEV, fill=PALE_D)
box(rx-MW/2, top-MH, MW, MH, "OFFLINE MODE", O_LINES, accent=OFF, fill=PALE_O)

ty = top-MH-12*mm
# comparison table
c.setFont("Helvetica-Bold", 12); c.setFillColorRGB(*INK)
c.drawString(M, ty, "What you can do in each mode")
ty -= 7*mm

rows = [
  ("Edit screens, fields, layout, order, show/hide", "yes", "yes"),
  ("Add or remove a screen · save a Favorite",      "yes", "yes"),
  ("Clone a profile under a new name",                "yes", "yes"),
  ("Import a .fit profile from anywhere",             "yes", "yes"),
  ("Edit the boot message (startup.txt)",             "yes", "yes"),
  ("Restore from a backup, or re-create a deleted profile", "yes", "no"),
  ("Pre-Flight review before writing",                "yes", "no"),
  ("Write to the device, then verify it landed",      "yes", "no"),
]
colx = [M+3, M+CW*0.66, M+CW*0.83]
c.setFont("Helvetica-Bold", 9); c.setFillColorRGB(*MUTE)
c.drawString(colx[0], ty, "")
c.drawCentredString(colx[1]+12, ty, "DEVICE"); c.drawCentredString(colx[2]+12, ty, "OFFLINE")
ty -= 4.5*mm
for i,(lab, a, b) in enumerate(rows):
    if i % 2 == 0:
        c.setFillColorRGB(0.965,0.967,0.973)
        c.rect(M, ty-1.5*mm, CW, 5.3*mm, stroke=0, fill=1)
    c.setFillColorRGB(*INK); c.setFont("Helvetica", 9.6)
    c.drawString(colx[0]+3, ty, lab)
    for x, v in ((colx[1], a), (colx[2], b)):
        if v == "yes":
            c.setFillColorRGB(*GREEN); c.setFont("Helvetica-Bold", 9.6); t="yes"
        else:
            c.setFillColorRGB(*STOP);  c.setFont("Helvetica-Bold", 9.6); t="no"
        c.drawCentredString(x+12, ty, t)
    ty -= 5.3*mm

# (the "Restore is hidden offline" note that used to sit here was cut:
#  the table row above already says it, and page 3 explains why.)

# ---- shared facts, bottom of page 3
fy = ty - 7*mm
c.setStrokeColorRGB(0.86,0.87,0.89); c.setLineWidth(0.9); c.line(M, fy+6*mm, W-M, fy+6*mm)
c.setFont("Helvetica-Bold", 11); c.setFillColorRGB(*GREEN)
c.drawString(M, fy, "True in both modes, and worth knowing")
c.setFont("Helvetica", 9.4); c.setFillColorRGB(*INK)
ty = fy - 5.6*mm
for f in [
 "Garmin/NewFiles/ is the only import route — copying into Garmin/Sports/ does not import a profile.",
 "The Edge renames every profile it imports, from the file’s own sport and display name.",
 "New profile or replacement is decided by the display name inside the file, never by the filename.",
 "A restart is required after copying — the Edge imports on boot, not on connect.",
 "The on-device editor manages at most 10 user screens, so the toolkit refuses to create an 11th.",
]:
    c.setFillColorRGB(*GREEN); c.drawString(M+2, ty, "•")
    c.setFillColorRGB(*INK)
    for i, ln in enumerate(wrap(f, "Helvetica", 9.4, CW-18)):
        c.drawString(M+10, ty, ln); ty -= 10.6
    ty -= 1.4


footer(1, "start here")
c.showPage()

# =====================================================================
# PAGE 2 -- device mode
# =====================================================================
y = header("Device mode — the Edge mounts as a disk",
  "Everything happens in the app. The toolkit backs up before it touches anything, shows you exactly what will change, and checks the write afterwards.",
  DEV)

SW = CW*0.80
sx = M + (CW-SW)/2
def step(yy, h, title, lines, accent=DEV, fill=(1,1,1), dash=None):
    """h is ignored -- kept so the call sites read as a minimum. The
    real height is measured from the content."""
    hh = max(h, measure(SW, title, lines))
    box(sx, yy-hh, SW, hh, title, lines, accent=accent, fill=fill, dash=dash)
    return yy-hh

yy = y
yy = step(yy, 16*mm, "1.  Press “List Profiles →”",
   ["Every profile on the device is backed up first, automatically. Backups are keyed by the device serial, so two Edges never share a folder."],
   fill=PALE_D)
arrow(W/2, yy, W/2, yy-8*mm, accent=DEV); yy -= 8*mm

yy = step(yy, 40*mm, "2.  Choose what to do",
   ["*View Screens →        edit the profile",
    "        Change fields and layout variant, reorder or hide screens, add or remove one. Save any screen as a Favorite to reuse in another profile.",
    "*Clone...                     copy it under a new name",
    "        The suggested filename matches what the Edge will generate. Screens copy across; the odometer starts at zero.",
    "*Restore from Backup...",
    "        Any earlier snapshot — including profiles you deleted from the device, which are re-created.",
    "*Import Profile...       a .fit from anywhere",
    "*Startup Message...   the text shown at boot"])
arrow(W/2, yy, W/2, yy-8*mm, accent=DEV); yy -= 8*mm

yy = step(yy, 15*mm, "3.  “Review & Deploy...”  —  Pre-Flight",
   ["A plain list of exactly what will change on the device, and a fresh CRC check of the file. Nothing has been written yet; you can still go back."],
   fill=PALE_D)
arrow(W/2, yy, W/2, yy-8*mm, accent=DEV); yy -= 8*mm

yy = step(yy, 15*mm, "4.  “Write to Device”",
   ["The file is copied into Garmin/NewFiles/, then read straight back and compared byte for byte before the app calls it done."])
arrow(W/2, yy, W/2, yy-8*mm, accent=DEV); yy -= 8*mm

yy = step(yy, 14*mm, "5.  Eject, then RESTART the Edge",
   ["The Edge imports on boot, not on connect. On restart it reads NewFiles, applies the profile, renames the file, and empties the folder."])
arrow(W/2, yy, W/2, yy-8*mm, accent=DEV); yy -= 8*mm

yy = step(yy, 22*mm, "6.  Reconnect and press “Check”",
   ["The toolkit finds your profile by the DISPLAY NAME stored inside it, because the Edge has renamed the file by now. It compares what is live on the device against what was sent.",
    "*“No differences” is the PASS — it means the write landed."],
   fill=PALE_D)

footer(2, "device mode")
c.showPage()

# =====================================================================
# PAGE 3 -- offline mode
# =====================================================================
y = header("Offline mode — the Edge does not mount",
  "Newer Edges connect over MTP and never appear as a disk, so the toolkit cannot reach them. You copy the files across yourself, edit them on the computer, and copy the result back.",
  OFF)

yy = y
yy = step(yy, 20*mm, "1.  Copy your profiles off the device  (outside the app)",
   ["Browse the Edge with OpenMTP or Commander One on macOS, or Explorer on Windows, and copy everything in Garmin/Sports/ into a folder on your computer.",
    "*That folder is what the toolkit will read."],
   accent=OFF, fill=PALE_O)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 13*mm, "2.  Press “Work Without a Device...” and pick that folder",
   ["Nothing is ever written back into it — Export always asks where to save."], accent=OFF)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 33*mm, "3.  Choose what to do",
   ["*View Screens →        edit the profile",
    "        The same editor with the same guards. Everything about screens, fields and layouts works offline.",
    "*Clone...                     works offline",
    "*Import Profile...       works offline",
    "*Startup Message...   reads and writes startup.txt in the folder",
    "",
    "*Restore from Backup is NOT available here — restoring writes to a device. Open your BACKUP folder as the source folder and Export from it instead."],
   accent=OFF)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 19*mm, "4.  “Export...”  —  save it wherever you like",
   ["Verified twice before the app reports success: the file’s own checksum against its contents, then a byte-for-byte read-back of the saved copy.",
    "*The filename is yours to choose. The Edge renames it on import anyway."],
   accent=OFF, fill=PALE_O)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 15*mm, "5.  Copy it into Garmin/NewFiles/  (outside the app)",
   ["Same MTP browser you used in step 1. NewFiles is the only folder the Edge imports from."],
   accent=OFF)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 13*mm, "6.  Disconnect and RESTART the Edge",
   ["It imports on boot. Your profile is updated, the file renamed, and NewFiles emptied."],
   accent=OFF)
arrow(W/2, yy, W/2, yy-5.5*mm, accent=OFF); yy -= 5.5*mm

yy = step(yy, 16*mm, "There is no Pre-Flight and no Check offline",
   ["Both have to read the live device to tell you anything, and offline there is no device to read. To confirm a change landed, pull the profile back off and look at it."],
   accent=STOP, dash=(3,2))

footer(3, "offline mode")
c.showPage(); c.save()
print("written", OUT)
