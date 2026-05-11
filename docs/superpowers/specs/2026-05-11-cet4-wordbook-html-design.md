# CET4 Wordbook HTML Design

## Goal

Turn the current CSV-based CET4 word list into a single-file HTML wordbook that is comfortable to read and memorize without spreadsheet interaction.

## Scope

Input:
- `output/四级备考重点词表-2021到2025-top300-含中文义项.csv`

Output:
- One standalone HTML page for local use

## Design

- Use a reading-first layout instead of a tool/dashboard layout.
- Present the content as a long-form wordbook page.
- Group words by `备考建议`:
  - `优先掌握`
  - `重点熟悉`
  - `可以积累`
- Each word is shown as a fully expanded card with:
  - English word
  - Chinese meaning
  - Common forms
  - Total frequency
  - Paper coverage
  - Study recommendation
- Keep interactions minimal:
  - top anchor navigation only
  - no spreadsheet-like behavior
  - no dense filter panel

## Visual Direction

- Editorial wordbook rather than app dashboard
- Warm light theme with paper-like background
- Large English headings, compact Chinese support text
- Multi-column card grid on desktop, single column on mobile

## Constraints

- Single HTML file
- Local-open friendly
- Mobile readable
- No dependency on external build steps
