#!/usr/bin/env python3
import argparse
from pathlib import Path

from wordtrace.pdf_wordfreq import (
    clean_extracted_text,
    count_words,
    count_words_from_pdfs,
    extract_pdf_text,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract cleaned word frequencies from a PDF.")
    parser.add_argument("pdf", nargs="+", help="One or more source PDF paths")
    parser.add_argument("--top", type=int, default=100, help="Number of top words to output")
    parser.add_argument(
        "--save-cleaned",
        type=Path,
        help="Optional path to save cleaned text. Only valid for a single PDF.",
    )
    args = parser.parse_args()

    if len(args.pdf) == 1:
        raw_text = extract_pdf_text(args.pdf[0])
        cleaned = clean_extracted_text(raw_text)
        if args.save_cleaned:
            args.save_cleaned.parent.mkdir(parents=True, exist_ok=True)
            args.save_cleaned.write_text(cleaned, encoding="utf-8")
        counts = count_words(cleaned)
    else:
        if args.save_cleaned:
            parser.error("--save-cleaned only supports a single PDF input")
        counts = count_words_from_pdfs(args.pdf)

    for rank, (word, freq) in enumerate(counts.most_common(args.top), start=1):
        print(f"{rank}\t{word}\t{freq}")


if __name__ == "__main__":
    main()
