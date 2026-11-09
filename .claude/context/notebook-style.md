# Notebook style context (loaded when a prompt mentions notebook, cell, style, log, csv or plot)

Matches the style of CS440 Lab 2 and Lab 3.

## Layout
1. Title markdown cell: `***LAB N***` plus 2-3 sentences on what the lab does.
2. One setup code cell: imports, `MOVES`, `SLIPS`, `X = None`, `GRID`, `START`, terminals, constants in CAPS.
3. `show_grid(grid, title)` cell that prints the grid with `S` on the start cell.
4. A `## Section` markdown cell before each main idea, then the code for it.
5. Test sections named `## Test N — <setting>` or `## Episode N` with one sentence of expectation.
6. `## Saving the logs` writing CSVs (tuples converted to `str`, outcome on the last row).
7. `## Results and discussion` as short bullets with bold labels.

## Code
- Plain functions and one small class; no extra frameworks beyond `random`, `pandas`, `IPython.display`.
- Short comments only where the logic is not obvious.
- Path log columns: `Step, From, Action/Intended, Actual, To, Note, Reward, Total`.
- `Note` uses the words `slipped` and `stopped`.
- Show tables with `display(pd.DataFrame(log).style.hide(axis="index").format(precision=2))`.
- Final print: `Path: a -> b -> c` and `Outcome: ...   Steps: n   Total reward: x`.
