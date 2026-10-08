# Data field slot heights — fill-in sheet

*Generated 2026-10-08 from the measured grids.*

Numbers in the cells are **`f7` field positions**, so `[ 0 | 1 ]` is one row
holding two half-width fields and `[   2   ]` is one full-width row.

Heights are **fractions of total screen height**, in the notation you already
used: `1/5`, `2/5`, `1/3`.

Anything marked **`(rule)`** follows from your finding that a half-width row is
always 1/5 — so the screen is 5 units tall and the full-width rows share what
is left. Those need no work. **If any of them looks wrong on the device, that
matters far more than the blanks**, because it would falsify the rule.

---

## Edge 840 — user screens

### Only these four are open

#### 2 fields, layout A    <<< NEEDS YOUR DATA

    row 0   [   0   ]      height: _____
    row 1   [   1   ]      height: _____

    2 full-width rows share 5 of the 5 units. Equal division would be
    5/2 of the screen each. Or the units may split unevenly — if so,
    which row is the tall one?

#### 4 fields, layout A    <<< NEEDS YOUR DATA

    row 0   [   0   ]      height: _____
    row 1   [   1   ]      height: _____
    row 2   [   2   ]      height: _____
    row 3   [   3   ]      height: _____

    4 full-width rows share 5 of the 5 units. Equal division would be
    5/4 of the screen each. Or the units may split unevenly — if so,
    which row is the tall one?

#### 5 fields, layout B    <<< NEEDS YOUR DATA

    row 0   [   0   ]      height: _____
    row 1   [   1   ]      height: _____
    row 2   [ 2 | 3 ]      height: 1/5    (rule)
    row 3   [   4   ]      height: _____

    3 full-width rows share 4 of the 5 units. Equal division would be
    4/3 of the screen each. Or the units may split unevenly — if so,
    which row is the tall one?

#### 6 fields, layout B    <<< NEEDS YOUR DATA

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [   2   ]      height: _____
    row 2   [   3   ]      height: _____
    row 3   [ 4 | 5 ]      height: 1/5    (rule)

    2 full-width rows share 3 of the 5 units. Equal division would be
    3/2 of the screen each. Or the units may split unevenly — if so,
    which row is the tall one?

---

### Already settled — listed so you can spot-check, not fill in

#### 1 fields, layout A

    row 0   [   0   ]      height: 5/5    (rule — the only full-width row takes the remaining 5 units)

#### 3 fields, layout A

    row 0   [   0   ]      height: 1/3    (already known)
    row 1   [   1   ]      height: 1/3    (already known)
    row 2   [   2   ]      height: 1/3    (already known)

    source: Doug, 2026-10-08 — equal thirds

#### 3 fields, layout B

    row 0   [   0   ]      height: 1/5    (already known)
    row 1   [   1   ]      height: 2/5    (already known)
    row 2   [   2   ]      height: 2/5    (already known)

    source: Doug, 2026-10-08 — regular row on top

#### 3 fields, layout C

    row 0   [   0   ]      height: 2/5    (already known)
    row 1   [   1   ]      height: 2/5    (already known)
    row 2   [   2   ]      height: 1/5    (already known)

    source: Doug, 2026-10-08 — regular row at bottom

#### 4 fields, layout B

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [   2   ]      height: 2/5    (rule — 2 rows share 4 units evenly)
    row 2   [   3   ]      height: 2/5    (rule — 2 rows share 4 units evenly)

#### 4 fields, layout C

    row 0   [   0   ]      height: 2/5    (rule — 2 rows share 4 units evenly)
    row 1   [   1   ]      height: 2/5    (rule — 2 rows share 4 units evenly)
    row 2   [ 2 | 3 ]      height: 1/5    (rule)

#### 5 fields, layout A

    row 0   [   0   ]      height: 1/5    (rule — 5 full-width rows share 5 units)
    row 1   [   1   ]      height: 1/5    (rule — 5 full-width rows share 5 units)
    row 2   [   2   ]      height: 1/5    (rule — 5 full-width rows share 5 units)
    row 3   [   3   ]      height: 1/5    (rule — 5 full-width rows share 5 units)
    row 4   [   4   ]      height: 1/5    (rule — 5 full-width rows share 5 units)

#### 5 fields, layout C

    row 0   [   0   ]      height: 1/5    (already known)
    row 1   [   1   ]      height: 2/5    (already known)
    row 2   [   2   ]      height: 1/5    (already known)
    row 3   [ 3 | 4 ]      height: 1/5    (already known)

    source: derived: recorded note 'SECOND row is TALLER' + the rule

#### 6 fields, layout A

    row 0   [   0   ]      height: 1/5    (rule — 4 full-width rows share 4 units)
    row 1   [   1   ]      height: 1/5    (rule — 4 full-width rows share 4 units)
    row 2   [   2   ]      height: 1/5    (rule — 4 full-width rows share 4 units)
    row 3   [   3   ]      height: 1/5    (rule — 4 full-width rows share 4 units)
    row 4   [ 4 | 5 ]      height: 1/5    (rule)

#### 6 fields, layout C

    row 0   [   0   ]      height: 1/5    (already known)
    row 1   [   1   ]      height: 2/5    (already known)
    row 2   [ 2 | 3 ]      height: 1/5    (already known)
    row 3   [ 4 | 5 ]      height: 1/5    (already known)

    source: derived: recorded note 'SECOND row is TALLER than the first' + the rule

#### 7 fields, layout A

    row 0   [   0   ]      height: 1/5    (rule — 3 full-width rows share 3 units)
    row 1   [   1   ]      height: 1/5    (rule — 3 full-width rows share 3 units)
    row 2   [   2   ]      height: 1/5    (rule — 3 full-width rows share 3 units)
    row 3   [ 3 | 4 ]      height: 1/5    (rule)
    row 4   [ 5 | 6 ]      height: 1/5    (rule)

#### 7 fields, layout B

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [   2   ]      height: 2/5    (rule — the only full-width row takes the remaining 2 units)
    row 2   [ 3 | 4 ]      height: 1/5    (rule)
    row 3   [ 5 | 6 ]      height: 1/5    (rule)

#### 7 fields, layout C

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [ 2 | 3 ]      height: 1/5    (rule)
    row 2   [   4   ]      height: 2/5    (rule — the only full-width row takes the remaining 2 units)
    row 3   [ 5 | 6 ]      height: 1/5    (rule)

#### 8 fields, layout A

    row 0   [   0   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 1   [   1   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 2   [ 2 | 3 ]      height: 1/5    (rule)
    row 3   [ 4 | 5 ]      height: 1/5    (rule)
    row 4   [ 6 | 7 ]      height: 1/5    (rule)

#### 8 fields, layout B

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [   2   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 2   [   3   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 3   [ 4 | 5 ]      height: 1/5    (rule)
    row 4   [ 6 | 7 ]      height: 1/5    (rule)

#### 8 fields, layout C

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [ 2 | 3 ]      height: 1/5    (rule)
    row 2   [   4   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 3   [   5   ]      height: 1/5    (rule — 2 full-width rows share 2 units)
    row 4   [ 6 | 7 ]      height: 1/5    (rule)

#### 9 fields, layout A

    row 0   [   0   ]      height: 1/5    (rule — the only full-width row takes the remaining 1 units)
    row 1   [ 1 | 2 ]      height: 1/5    (rule)
    row 2   [ 3 | 4 ]      height: 1/5    (rule)
    row 3   [ 5 | 6 ]      height: 1/5    (rule)
    row 4   [ 7 | 8 ]      height: 1/5    (rule)

#### 9 fields, layout B

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [   2   ]      height: 1/5    (rule — the only full-width row takes the remaining 1 units)
    row 2   [ 3 | 4 ]      height: 1/5    (rule)
    row 3   [ 5 | 6 ]      height: 1/5    (rule)
    row 4   [ 7 | 8 ]      height: 1/5    (rule)

#### 9 fields, layout C

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [ 2 | 3 ]      height: 1/5    (rule)
    row 2   [   4   ]      height: 1/5    (rule — the only full-width row takes the remaining 1 units)
    row 3   [ 5 | 6 ]      height: 1/5    (rule)
    row 4   [ 7 | 8 ]      height: 1/5    (rule)

#### 10 fields, layout A

    row 0   [ 0 | 1 ]      height: 1/5    (rule)
    row 1   [ 2 | 3 ]      height: 1/5    (rule)
    row 2   [ 4 | 5 ]      height: 1/5    (rule)
    row 3   [ 6 | 7 ]      height: 1/5    (rule)
    row 4   [ 8 | 9 ]      height: 1/5    (rule)

---

## Edge 530 — one question, not a sheet

**The rule has only been verified on the 840.** Its screen is a different size,
so nothing here should be assumed to carry over — that assumption is exactly
the class of error this project keeps catching.

So just one check, and the rest follows or it doesn't:

**On a 530, is a row of two half-width fields also 1/5 of the screen height?**

A 10-field layout is the easy test: if it is five equal rows of two, the answer
is yes and the whole model transfers. If those rows are not fifths, the 530 has
its own geometry and needs its own sheet.
