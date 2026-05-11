# WordTrace

WordTrace is a small local workflow for extracting English words from CET-4 past papers, cleaning the text, building frequency-based study lists, and rendering a reading-first HTML wordbook with local progress tracking.

## Included

- PDF word extraction and cleaning logic
- CET-4 word-frequency aggregation scripts
- Generated study outputs and HTML wordbook
- Tests for text cleaning and wordbook rendering

## Not Included

- Raw PDF source files under `四六级真题/`

Those files stay local because they are large source materials and are not needed to review or reuse the code/output structure in this repository.

## Main Files

- `wordtrace/pdf_wordfreq.py`: PDF extraction, cleaning, and frequency counting
- `wordtrace/wordbook_html.py`: HTML wordbook renderer
- `scripts/pdf_wordfreq.py`: simple CLI entry for extraction and counting
- `output/四级备考重点词书-2021到2025-top300.html`: current reading-first CET-4 wordbook

## Verification

```bash
python3 -m unittest tests/test_pdf_wordfreq.py tests/test_wordbook_html.py
```
