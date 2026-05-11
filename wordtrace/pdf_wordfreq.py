import re
import subprocess
from collections import Counter
from pathlib import Path
import requests


STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "down",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "here",
    "his",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "may",
    "me",
    "more",
    "most",
    "might",
    "my",
    "not",
    "of",
    "on",
    "one",
    "only",
    "or",
    "other",
    "our",
    "out",
    "over",
    "she",
    "should",
    "so",
    "some",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "three",
    "through",
    "to",
    "two",
    "under",
    "up",
    "us",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "would",
    "you",
    "your",
}

EXAM_STRUCTURE_WORDS = {
    "answer",
    "answers",
    "author",
    "authors",
    "bank",
    "based",
    "blank",
    "blanks",
    "center",
    "centre",
    "choice",
    "choices",
    "comprehension",
    "conversation",
    "conversations",
    "following",
    "listening",
    "mark",
    "marked",
    "news",
    "passage",
    "passages",
    "part",
    "question",
    "questions",
    "report",
    "reports",
    "section",
    "sheet",
    "statement",
    "statements",
    "translation",
    "writing",
}

ULTRA_BASIC_WORDS = {
    "around",
    "become",
    "better",
    "both",
    "change",
    "child",
    "children",
    "day",
    "days",
    "different",
    "doing",
    "even",
    "feel",
    "feeling",
    "feelings",
    "find",
    "first",
    "get",
    "good",
    "help",
    "home",
    "kid",
    "kids",
    "know",
    "less",
    "life",
    "like",
    "long",
    "make",
    "man",
    "many",
    "much",
    "need",
    "new",
    "now",
    "often",
    "one",
    "other",
    "others",
    "own",
    "part",
    "people",
    "problem",
    "same",
    "say",
    "school",
    "see",
    "self",
    "something",
    "student",
    "students",
    "take",
    "thing",
    "things",
    "think",
    "time",
    "too",
    "use",
    "want",
    "way",
    "well",
    "woman",
    "women",
    "work",
    "world",
    "year",
    "years",
}

LOW_VALUE_REAL_WORDS = {
    "according",
    "already",
    "always",
    "another",
    "back",
    "best",
    "between",
    "book",
    "books",
    "booking",
    "booked",
    "done",
    "during",
    "easily",
    "every",
    "everyone",
    "far",
    "food",
    "foods",
    "given",
    "going",
    "hear",
    "heard",
    "hearing",
    "left",
    "little",
    "live",
    "lives",
    "living",
    "lot",
    "lots",
    "mean",
    "meaning",
    "means",
    "minute",
    "minutes",
    "off",
    "really",
    "show",
    "showed",
    "showing",
    "shows",
    "simply",
    "still",
    "such",
    "sure",
    "themselves",
    "today",
    "until",
    "very",
    "whether",
    "without",
    "worth",
    "yourself",
}

IRREGULAR_NORMALIZATION = {
    "children": "child",
    "changed": "change",
    "changing": "change",
    "companies": "company",
    "contributed": "contribute",
    "contributing": "contribute",
    "caused": "cause",
    "causing": "cause",
    "did": "do",
    "does": "do",
    "employees": "employee",
    "found": "find",
    "getting": "get",
    "got": "get",
    "having": "have",
    "heard": "hear",
    "increased": "increase",
    "increasing": "increase",
    "living": "live",
    "made": "make",
    "making": "make",
    "men": "man",
    "said": "say",
    "says": "say",
    "studies": "study",
    "studied": "study",
    "studying": "study",
    "using": "use",
    "used": "use",
    "women": "woman",
}


def extract_pdf_text(pdf_path: str | Path) -> str:
    return subprocess.check_output(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        text=True,
    )


def is_page_artifact(line: str) -> bool:
    if not line:
        return True
    if re.search(r"https?://\S*burningvocabulary\.(?:cn|com)/?", line):
        return True
    if re.fullmatch(r"\d+", line):
        return True
    return False


def is_heading_line(line: str) -> bool:
    return bool(
        re.match(r"^Part\s+[IVX]+\b", line)
        or re.match(r"^Section\s+[A-Z]\b", line)
    )


def clean_extracted_text(text: str) -> str:
    cleaned_lines: list[str] = []
    skipping_directions = False

    for raw_line in text.splitlines():
        line = raw_line.replace("’", "'").strip()
        if not line:
            skipping_directions = False
            continue

        line = re.sub(r"[\(\（][^\)\）]*[\u4e00-\u9fff][^\)\）]*[\)\）]", "", line)
        line = re.sub(r"[\u4e00-\u9fff]+", " ", line)
        line = re.sub(r"\s+", " ", line).strip()

        if not line:
            continue
        if is_page_artifact(line):
            continue

        if line.startswith("Directions:"):
            skipping_directions = True
            continue
        if skipping_directions:
            if line.startswith("Questions "):
                skipping_directions = False
            else:
                continue

        if is_heading_line(line):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def count_words(text: str) -> Counter:
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    normalized = []
    for word in words:
        if word.endswith("'s"):
            word = word[:-2]
        elif word.endswith("n't"):
            word = word[:-3]
        elif word.endswith("'re") or word.endswith("'ve") or word.endswith("'ll") or word.endswith("'d") or word.endswith("'m"):
            word = word.split("'", 1)[0]
        if len(word) < 3:
            continue
        if word in STOPWORDS:
            continue
        normalized.append(word)
    return Counter(normalized)


def normalize_study_word(word: str) -> str:
    if word in IRREGULAR_NORMALIZATION:
        return IRREGULAR_NORMALIZATION[word]
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("s") and len(word) > 3 and not word.endswith("ss") and not word.endswith("us"):
        return word[:-1]
    if word.endswith("ing") and len(word) > 5:
        base = word[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        if not base.endswith("e"):
            candidate = base + "e"
            if candidate in {
                "base",
                "live",
                "make",
                "take",
                "write",
                "drive",
                "move",
                "use",
                "close",
            }:
                return candidate
        return base
    if word.endswith("ed") and len(word) > 4:
        base = word[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        if not base.endswith("e"):
            candidate = base + "e"
            if candidate in {
                "base",
                "close",
                "move",
                "use",
            }:
                return candidate
        return base
    return word


def is_structure_word(word: str) -> bool:
    return word in EXAM_STRUCTURE_WORDS


def is_ultra_basic_word(word: str) -> bool:
    return word in ULTRA_BASIC_WORDS


def is_low_value_real_word(word: str) -> bool:
    return word in LOW_VALUE_REAL_WORDS


def count_words_from_pdfs(pdf_paths: list[str | Path]) -> Counter:
    total = Counter()
    for pdf_path in pdf_paths:
        text = extract_pdf_text(pdf_path)
        cleaned = clean_extracted_text(text)
        total.update(count_words(cleaned))
    return total


def summarize_words_from_pdfs(pdf_paths: list[str | Path]) -> dict[str, tuple[int, int]]:
    total = Counter()
    paper_count = Counter()

    for pdf_path in pdf_paths:
        text = extract_pdf_text(pdf_path)
        cleaned = clean_extracted_text(text)
        counts = count_words(cleaned)
        total.update(counts)
        paper_count.update(counts.keys())

    return {
        word: (total[word], paper_count[word])
        for word in total
    }


def summarize_study_words_from_pdfs(
    pdf_paths: list[str | Path],
    min_total_count: int = 15,
    min_paper_count: int = 5,
) -> list[dict[str, int | str]]:
    total = Counter()
    paper_count = Counter()
    forms: dict[str, set[str]] = {}

    for pdf_path in pdf_paths:
        text = extract_pdf_text(pdf_path)
        cleaned = clean_extracted_text(text)
        counts = count_words(cleaned)
        paper_seen: set[str] = set()

        for word, count in counts.items():
            if is_structure_word(word) or is_ultra_basic_word(word) or is_low_value_real_word(word):
                continue
            canonical = normalize_study_word(word)
            if (
                is_structure_word(canonical)
                or is_ultra_basic_word(canonical)
                or is_low_value_real_word(canonical)
            ):
                continue
            total[canonical] += count
            paper_seen.add(canonical)
            forms.setdefault(canonical, set()).add(word)

        paper_count.update(paper_seen)

    rows: list[dict[str, int | str]] = []
    sorted_words = sorted(
        total.keys(),
        key=lambda word: (-total[word], -paper_count[word], word),
    )
    rank = 1
    for word in sorted_words:
        if total[word] < min_total_count or paper_count[word] < min_paper_count:
            continue
        rows.append(
            {
                "序号": rank,
                "重点词汇": word,
                "总出现次数": total[word],
                "覆盖真题套数": paper_count[word],
                "常见词形": format_word_forms(word, forms[word]),
                "备考建议": learning_priority(total[word], paper_count[word]),
            }
        )
        rank += 1
    return rows


def learning_priority(total_count: int, paper_count: int) -> str:
    if total_count >= 100 and paper_count >= 20:
        return "优先掌握"
    if total_count >= 40 or paper_count >= 10:
        return "重点熟悉"
    return "可以积累"


def format_word_forms(canonical: str, forms: set[str]) -> str:
    ordered = sorted(forms)
    if canonical in ordered:
        ordered.remove(canonical)
        ordered.insert(0, canonical)
    return ", ".join(ordered)


def format_chinese_meaning(primary: str, candidates: list[str], limit: int = 3) -> str:
    ordered: list[str] = []
    for item in [primary, *candidates]:
        text = item.strip()
        if not text or text in ordered:
            continue
        ordered.append(text)
        if len(ordered) >= limit:
            break
    return "；".join(ordered)


def fetch_chinese_meaning(word: str, timeout: int = 15, retries: int = 3) -> str:
    url = "https://translate.googleapis.com/translate_a/single"
    params = [
        ("client", "gtx"),
        ("sl", "en"),
        ("tl", "zh-CN"),
        ("dt", "t"),
        ("dt", "bd"),
        ("q", word),
    ]
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException as exc:
            last_error = exc
            if attempt == retries - 1:
                raise
    else:
        raise last_error  # pragma: no cover

    primary = ""
    if data and len(data) > 0 and data[0] and data[0][0]:
        primary = (data[0][0][0] or "").strip()

    candidates: list[str] = []
    if len(data) > 1 and data[1]:
        for entry in data[1]:
            if len(entry) > 1 and entry[1]:
                for candidate in entry[1]:
                    if candidate:
                        candidates.append(candidate)

    return format_chinese_meaning(primary, candidates)


def build_learning_rows(summary_rows: list[tuple[str, tuple[int, int]]]) -> list[dict[str, int | str]]:
    rows: list[dict[str, int | str]] = []
    for rank, (word, (total_count, paper_count)) in enumerate(summary_rows, start=1):
        rows.append(
            {
                "序号": rank,
                "单词": word,
                "总出现次数": total_count,
                "覆盖真题套数": paper_count,
                "学习优先级": learning_priority(total_count, paper_count),
            }
        )
    return rows


def top_words_from_pdf(pdf_path: str | Path, limit: int = 100) -> list[tuple[str, int]]:
    text = extract_pdf_text(pdf_path)
    cleaned = clean_extracted_text(text)
    return count_words(cleaned).most_common(limit)
