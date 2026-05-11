import unittest
from unittest.mock import patch

from wordtrace.pdf_wordfreq import (
    build_learning_rows,
    clean_extracted_text,
    count_words,
    count_words_from_pdfs,
    format_chinese_meaning,
    normalize_study_word,
    summarize_study_words_from_pdfs,
    summarize_words_from_pdfs,
)


class PdfWordFreqTests(unittest.TestCase):
    def test_clean_extracted_text_keeps_all_non_direction_english_content(self):
        sample = """
Part II                                   Listening Comprehension                                     (25 minutes)
Section A
Directions: In this section, you will hear three news reports. At the end of each news report, you will hear two or
three questions. Both the news report and the questions will be spoken only once.
Questions 1 and 2 are based on the news report you have just heard.
1. A. Outside the office of a charity foundation.               C. Under the engine cover of a man's car.
   B. Inside the car of David King's neighbour.                 D. At the gate of a grade school in Kent.
Part IV                                         Translation                                          (30 minutes)
近年来，中国政府高度重视民营经济（private economy）的发展。
1                                                                                         https://zhenti.burningvocabulary.cn
"""
        cleaned = clean_extracted_text(sample)

        self.assertIn("Questions 1 and 2 are based on the news report you have just heard.", cleaned)
        self.assertIn("Outside the office of a charity foundation.", cleaned)
        self.assertIn("Under the engine cover of a man's car.", cleaned)
        self.assertIn("private economy", cleaned)
        self.assertNotIn("Directions:", cleaned)
        self.assertNotIn("https://zhenti.burningvocabulary.cn", cleaned)
        self.assertNotIn("中国政府", cleaned)
        self.assertNotIn("three news reports", cleaned)

    def test_count_words_filters_stopwords_and_normalizes_possessive(self):
        sample = """
A. Bike lanes help businesses and cyclists.
B. The city's businesses help people, and the people like bike lanes.
"""
        counts = count_words(sample)

        self.assertEqual(counts["bike"], 2)
        self.assertEqual(counts["lanes"], 2)
        self.assertEqual(counts["help"], 2)
        self.assertEqual(counts["businesses"], 2)
        self.assertEqual(counts["people"], 2)
        self.assertNotIn("the", counts)
        self.assertNotIn("and", counts)

    def test_clean_extracted_text_removes_multiline_directions_block(self):
        sample = """
Directions: Suppose the student union of your university is collecting opinions on improving its work for the
coming year. You are now to write a response by suggesting how it can better enrich student life.

Questions 8 to 11 are based on the conversation you have just heard.
"""
        cleaned = clean_extracted_text(sample)

        self.assertEqual(cleaned, "Questions 8 to 11 are based on the conversation you have just heard.")

    @patch("wordtrace.pdf_wordfreq.extract_pdf_text")
    def test_count_words_from_pdfs_aggregates_multiple_files(self, mock_extract_pdf_text):
        mock_extract_pdf_text.side_effect = [
            "Questions 1 and 2 are based on the news report you have just heard.\nA. Bike lanes help people.",
            "Questions 3 and 4 are based on the news report you have just heard.\nB. People like bike lanes.",
        ]

        counts = count_words_from_pdfs(["a.pdf", "b.pdf"])

        self.assertEqual(counts["people"], 2)
        self.assertEqual(counts["bike"], 2)
        self.assertEqual(counts["lanes"], 2)
        self.assertEqual(counts["questions"], 2)

    def test_clean_extracted_text_removes_footer_urls_for_both_domains(self):
        sample = """
Questions 1 and 2 are based on the news report you have just heard.
https://zhenti.burningvocabulary.cn
https://zhenti.burningvocabulary.com/
"""
        cleaned = clean_extracted_text(sample)

        self.assertEqual(cleaned, "Questions 1 and 2 are based on the news report you have just heard.")

    @patch("wordtrace.pdf_wordfreq.extract_pdf_text")
    def test_summarize_words_from_pdfs_tracks_total_and_paper_count(self, mock_extract_pdf_text):
        mock_extract_pdf_text.side_effect = [
            "People like bike lanes. People help.",
            "Bike lanes help students.",
            "Students like people.",
        ]

        summary = summarize_words_from_pdfs(["a.pdf", "b.pdf", "c.pdf"])

        self.assertEqual(summary["people"], (3, 2))
        self.assertEqual(summary["bike"], (2, 2))
        self.assertEqual(summary["lanes"], (2, 2))
        self.assertEqual(summary["help"], (2, 2))
        self.assertEqual(summary["students"], (2, 2))

    def test_build_learning_rows_uses_friendly_headers_and_priority(self):
        summary_rows = [
            ("people", (467, 29)),
            ("study", (85, 26)),
            ("hour", (15, 7)),
        ]

        rows = build_learning_rows(summary_rows)

        self.assertEqual(
            rows[0],
            {
                "序号": 1,
                "单词": "people",
                "总出现次数": 467,
                "覆盖真题套数": 29,
                "学习优先级": "优先掌握",
            },
        )
        self.assertEqual(rows[1]["学习优先级"], "重点熟悉")
        self.assertEqual(rows[2]["学习优先级"], "可以积累")

    def test_normalize_study_word_merges_common_forms(self):
        self.assertEqual(normalize_study_word("said"), "say")
        self.assertEqual(normalize_study_word("says"), "say")
        self.assertEqual(normalize_study_word("studies"), "study")
        self.assertEqual(normalize_study_word("companies"), "company")
        self.assertEqual(normalize_study_word("employees"), "employee")
        self.assertEqual(normalize_study_word("living"), "live")
        self.assertEqual(normalize_study_word("based"), "base")
        self.assertEqual(normalize_study_word("changing"), "change")
        self.assertEqual(normalize_study_word("causing"), "cause")
        self.assertEqual(normalize_study_word("increasing"), "increase")

    @patch("wordtrace.pdf_wordfreq.extract_pdf_text")
    def test_summarize_study_words_filters_structure_and_basic_words(self, mock_extract_pdf_text):
        mock_extract_pdf_text.side_effect = [
            "Questions passage people time said heard study studies company companies research financial based based.",
            "Question passages people work says hearing studying companies research financial based.",
            "Questions heard many work study company research financial based.",
            "Question based people said hear company research financial based.",
            "Passage many people says studies company research financial based.",
        ]

        rows = summarize_study_words_from_pdfs(
            ["a.pdf", "b.pdf", "c.pdf", "d.pdf", "e.pdf"],
            min_total_count=2,
            min_paper_count=2,
        )

        words = {row["重点词汇"]: row for row in rows}
        self.assertIn("study", words)
        self.assertIn("company", words)
        self.assertIn("research", words)
        self.assertIn("financial", words)
        self.assertNotIn("question", words)
        self.assertNotIn("passage", words)
        self.assertNotIn("based", words)
        self.assertNotIn("base", words)
        self.assertNotIn("people", words)
        self.assertNotIn("hear", words)
        self.assertEqual(words["study"]["常见词形"], "study, studies, studying")

    def test_format_chinese_meaning_deduplicates_and_limits_items(self):
        meaning = format_chinese_meaning(
            primary="兴趣",
            candidates=["兴趣", "利益", "利息", "爱好", "兴趣", "情趣"],
            limit=3,
        )
        self.assertEqual(meaning, "兴趣；利益；利息")


if __name__ == "__main__":
    unittest.main()
