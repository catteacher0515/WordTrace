import unittest

from wordtrace.wordbook_html import render_wordbook_html


class WordbookHtmlTests(unittest.TestCase):
    def test_render_wordbook_html_includes_progress_and_persistence_hooks(self):
        rows = [
            {
                "序号": "1",
                "重点词汇": "study",
                "中文义项": "学习；研究",
                "常见词形": "study, studied, studies, studying",
                "备考建议": "优先掌握",
                "总出现次数": "151",
                "覆盖真题套数": "28",
            },
            {
                "序号": "2",
                "重点词汇": "research",
                "中文义项": "研究；科研",
                "常见词形": "research, researching",
                "备考建议": "重点熟悉",
                "总出现次数": "134",
                "覆盖真题套数": "28",
            },
        ]

        html = render_wordbook_html(rows, "测试词书")

        self.assertIn("localStorage", html)
        self.assertIn("wordtrace-cet4-top300-progress-v1", html)
        self.assertIn('id="overall-progress-text"', html)
        self.assertIn('data-word-key="1-study"', html)
        self.assertIn("记忆进度", html)
        self.assertIn("已记住", html)
        self.assertIn("优先掌握", html)
        self.assertIn("重点熟悉", html)

    def test_render_wordbook_html_renders_mastery_buttons_and_group_counts(self):
        rows = [
            {
                "序号": "1",
                "重点词汇": "study",
                "中文义项": "学习；研究",
                "常见词形": "study, studied, studies, studying",
                "备考建议": "优先掌握",
                "总出现次数": "151",
                "覆盖真题套数": "28",
            },
            {
                "序号": "2",
                "重点词汇": "learn",
                "中文义项": "学习；学会",
                "常见词形": "learn, learned, learning, learns",
                "备考建议": "优先掌握",
                "总出现次数": "148",
                "覆盖真题套数": "28",
            },
            {
                "序号": "3",
                "重点词汇": "company",
                "中文义项": "公司；企业",
                "常见词形": "company, companies",
                "备考建议": "重点熟悉",
                "总出现次数": "117",
                "覆盖真题套数": "20",
            },
        ]

        html = render_wordbook_html(rows, "测试词书")

        self.assertIn("2 词", html)
        self.assertIn("1 词", html)
        self.assertIn("class=\"mastery-toggle\"", html)
        self.assertIn("section-progress", html)
        self.assertIn("aria-pressed", html)
        self.assertIn("--mastered-fill", html)

    def test_render_wordbook_html_includes_unmastered_filter_controls(self):
        rows = [
            {
                "序号": "1",
                "重点词汇": "study",
                "中文义项": "学习；研究",
                "常见词形": "study, studied, studies, studying",
                "备考建议": "优先掌握",
                "总出现次数": "151",
                "覆盖真题套数": "28",
            }
        ]

        html = render_wordbook_html(rows, "测试词书")

        self.assertIn("只看待记", html)
        self.assertIn("filter-unmastered-toggle", html)
        self.assertIn("wordbook-filter-unmastered-v1", html)
        self.assertIn("show-unmastered-only", html)

    def test_render_wordbook_html_includes_reset_progress_control(self):
        rows = [
            {
                "序号": "1",
                "重点词汇": "study",
                "中文义项": "学习；研究",
                "常见词形": "study, studied, studies, studying",
                "备考建议": "优先掌握",
                "总出现次数": "151",
                "覆盖真题套数": "28",
            }
        ]

        html = render_wordbook_html(rows, "测试词书")

        self.assertIn("重置进度", html)
        self.assertIn("reset-progress-button", html)
        self.assertIn("localStorage.removeItem(STORAGE_KEY)", html)
        self.assertIn("localStorage.removeItem(FILTER_STORAGE_KEY)", html)


if __name__ == "__main__":
    unittest.main()
