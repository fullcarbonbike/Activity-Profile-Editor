# Data field names this toolkit already knows

*213 confirmed names, regenerated 2026-11-18 from
`fit_dump.FIELD_ID_NAMES` — the module is the source of truth, this
file is a readable copy of it.*

Scan the Edge's own field picker against this list and note
anything the device offers that is NOT here. Those are the
targets -- you are looking for ABSENCES, which is far less work
than transcribing the whole picker.

**⚠ This file was 41 names stale until 2026-11-18.** It claimed 172
names and listed `520, 578, 579` as unresolved; all three have since
been named (Primary Target, Secondary Target, Smart Travel Range) and
the module had grown to 213. Found while chasing field 331, not by
anything that checks. If you add names to `fit_dump.py`, regenerate
this file in the same sitting or it drifts again.

### Ids seen in profiles that have no name

Do **not** read the unnamed ids in the corpus as a to-do list. Most of
them are probe residue: the field-ID census (#146, #154) worked by
filling a screen with ten consecutive candidate ids and reading the
labels off the device, so profiles like `ROAD 4` carry runs such as
`330, 331, 332 … 338` that the device may not support at all.

**One id is in a different category: `331`.** It is not merely
unidentified, it is confirmed to have **no label anywhere**:

| surface | what it shows for 331 |
|---|---|
| Edge 840 field editor | **blank** — no name (358, 371, 395 beside it do have names) |
| Garmin Connect phone app | Field number shown, **description blank** — and blank for 358/371/395 too |
| Edge 530 | **unsupported** — renders as Speed, the fallback for an unknown plain field id |

So 331 needs no further label-hunting on the 840 or in Connect. Both
have been checked and neither has a string for it.

**Its BEHAVIOUR is now identified, even though its label is not:** 331
displays the **duration of the most recently completed lap** — the
workout step, inside a structured workout. Established 2026-11-25 from
seventeen readings taken at each change during a `7x2:00@185W` indoor
workout, 15 of 16 landing within 4 seconds of the lap that had just
closed (`TEST_331_RESULT_2026-11-25.md`, Doc rev 228).

It is therefore **not** given a name in the table below, for a reason
worth stating: **id 87 is already "Last Lap Time"**, from the device's
own label, so 331 is a sibling of that field and naming it the same
thing would assert an identity that has not been shown. The remaining
question is which variant — last-lap elapsed vs timer time, or last
*step* time rather than last *lap* time. Two three-minute tests settle
it; rev 228 has them.

Doc revs 220–227 hold the candidates eliminated along the way; note
that rev 227's power-dependence reading is superseded by rev 228.

| Name | id |
| %FTP | 42 |
| %Heart Rate Reserve | 19 |
| %Max Heart Rate | 16 |
| 10s Balance | 160 |
| 10s Force | 852 |
| 10s Power | 146 |
| 10s W/kg | 440 |
| 24-Hour Maximum Temperature | 214 |
| 24-Hour Minimum Temperature | 215 |
| 30s Balance | 161 |
| 30s Force | 853 |
| 30s Power | 80 |
| 30s VAM | 88 |
| 30s Vertical Descent Speed | 787 |
| 30s W/kg | 441 |
| 3s Balance | 159 |
| 3s Force | 851 |
| 3s Power | 79 |
| 3s W/kg | 439 |
| 60s Flow | 497 |
| 60s Grit | 495 |
| Aerobic Training Effect | 99 |
| Anaerobic TE | 433 |
| Asc to Next Crs Pt | 445 |
| Ascent Remaining | 444 |
| Assist Mode | 491 |
| Avg %HRR | 20 |
| Avg %Max Heart Rate | 17 |
| Avg Balance | 150 |
| Avg Cadence | 4 |
| Avg Force | 847 |
| Avg Heart Rate | 14 |
| Avg L. Peak Pwr Phase | 276 |
| Avg Lap Time | 57 |
| Avg Left PP | 273 |
| Avg PCO | 264 |
| Avg Power | 37 |
| Avg R. Peak Pwr Phase | 270 |
| Avg Right PP | 267 |
| Avg Speed | 49 |
| Avg VAM | 443 |
| Avg W/kg | 437 |
| Avg. Vertical Descent Speed | 220 |
| Balance | 149 |
| Battery Hours | 395 |
| Battery Level | 96 |
| Beam Angle Status | 318 |
| Cadence | 3 |
| Cadence (Avg/Max) | 353 |
| Cadence Bars | 349 |
| Cadence Graph | 345 |
| Calories | 0 |
| Calories to Go | 64 |
| CIQ Data Field | 216 |
| Compass | 529 |
| Course Pt Dist. | 2 |
| Dest. Ahead | 62 |
| Dest. Location | 31 |
| Di2 Battery | 408 |
| Di2 Shift Mode | 411 |
| Dist. to Point | 595 |
| Distance | 6 |
| Distance to Destination | 27 |
| Distance to Go | 65 |
| Distance to Next | 29 |
| Duration | 522 |
| eBike Battery | 493 |
| Elapsed Time | 55 |
| Elevation (Asc/Desc) | 358 |
| Elevation (ft) | 9 |
| Elevation Graph | 368 |
| EPOC | 478 |
| Estimated Distance | 582 |
| Estimated Time | 583 |
| ETA at Destination | 93 |
| ETA to Next | 94 |
| Flow | 488 |
| Force | 860 |
| Front Gear | 179 |
| Gear Battery | 181 |
| Gear Combo | 409 |
| Gear Ratio | 182 |
| Gears | 178 |
| GPS Signal Strength | 97 |
| Grit | 486 |
| Heading | 12 |
| Heart Rate | 13 |
| Heart Rate (Avg/Max) | 351 |
| Heart Rate Graph | 343 |
| Heart Rate to Go | 66 |
| Heart Rate Zone | 22 |
| HR Bars | 347 |
| HR Zone 1 (time) | 199 |
| HR Zone 2 (time) | 200 |
| HR Zone 3 (time) | 201 |
| HR Zone 4 (time) | 202 |
| HR Zone 5 (time) | 203 |
| HR Zone Graph | 23 |
| Intensity Factor (IF) | 83 |
| Kilojoules | 38 |
| Lap %HRR | 21 |
| Lap %Max HR | 18 |
| Lap Ascent | 223 |
| Lap Balance | 151 |
| Lap Cadence | 5 |
| Lap Descent | 224 |
| Lap Dist. | 7 |
| Lap Flow | 489 |
| Lap Force | 848 |
| Lap Grit | 487 |
| Lap HR | 15 |
| Lap Left PP | 274 |
| Lap Left PPP | 277 |
| Lap Norm. Force | 857 |
| Lap NP | 147 |
| Lap PCO | 265 |
| Lap Power | 39 |
| Lap Right PP | 268 |
| Lap Right PPP | 271 |
| Lap Speed | 50 |
| Lap Time | 58 |
| Lap Time Seated | 260 |
| Lap Time Standing | 258 |
| Lap VAM | 442 |
| Lap Vertical Descent Speed | 788 |
| Lap Watts/kg | 438 |
| Laps | 24 |
| Last Lap Dist | 84 |
| Last Lap Force | 854 |
| Last Lap HR | 165 |
| Last Lap Norm. Force | 858 |
| Last Lap NP | 148 |
| Last Lap Power | 100 |
| Last Lap Speed | 86 |
| Last Lap Time | 87 |
| Left PPP | 275 |
| Light Battery | 317 |
| Light Mode | 319 |
| Lights Connected | 316 |
| Location | 240 |
| Map | 725 |
| Max Lap Power | 41 |
| Max Power | 40 |
| Max Speed | 91 |
| Max. Force | 849 |
| Max. Lap Force | 850 |
| Next Pt Location | 32 |
| Normalized Force | 856 |
| Normalized Power | 81 |
| Odometer | 95 |
| Pedal Smoothness | 176 |
| Percent Grade | 11 |
| Perf. Conditioning | 320 |
| Platform Center Offset | 263 |
| Potential | 580 |
| Power | 36 |
| Power (Avg/Max) | 354 |
| Power Bars | 350 |
| Power Graph | 346 |
| Power Phase Left | 272 |
| Power Phase Right | 266 |
| Power Z1 | 207 |
| Power Z2 | 208 |
| Power Z3 | 209 |
| Power Z4 | 210 |
| Power Z5 | 211 |
| Power Z6 | 212 |
| Power Z7 | 213 |
| Power Z8 | 418 |
| Power Z9 | 419 |
| Power Zone | 43 |
| Primary Target | 520 |
| Rear Gear | 180 |
| Reps to Go | 67 |
| Resistance | 294 |
| Respiration | 452 |
| Right PPP | 269 |
| Secondary Target | 578 |
| Segment Time | 654 |
| Shifting Advice | 492 |
| Smart Travel Range | 579 |
| Speed | 48 |
| Speed (Avg/Max) | 352 |
| Speed Bars | 348 |
| Speed Graph | 344 |
| Speed Over Ground | 371 |
| Stamina | 581 |
| Step Distance | 302 |
| Step Time | 523 |
| Sunrise | 53 |
| Sunset | 54 |
| Target | 521 |
| Target Power | 295 |
| Temperature | 78 |
| Time Ahead | 63 |
| Time of Day (TOD) | 59 |
| Time Seated | 259 |
| Time Standing | 257 |
| Time to Destination | 28 |
| Time to Go | 68 |
| Time to Next | 30 |
| Time to Point | 596 |
| Timer | 56 |
| Torque Effect | 177 |
| Total Ascent | 60 |
| Total Descent | 61 |
| Travel Range | 494 |
| TSS | 82 |
| VAM | 77 |
| Vertical Descent Speed | 786 |
| Watts/kg | 98 |
| Workout Comparison | 511 |
| Workout Step | 45 |
