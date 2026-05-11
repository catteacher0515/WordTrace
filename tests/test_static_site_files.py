import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent


class StaticSiteFilesTests(unittest.TestCase):
    def test_root_index_redirects_to_wordbook(self):
        index_path = ROOT / "index.html"

        self.assertTrue(index_path.exists(), "index.html should exist for static hosting")

        html = index_path.read_text(encoding="utf-8")
        self.assertIn("四级备考重点词书-2021到2025-top300.html", html)
        self.assertIn("window.location.replace", html)

    def test_vercel_config_marks_project_as_static(self):
        config_path = ROOT / "vercel.json"

        self.assertTrue(config_path.exists(), "vercel.json should exist for Vercel deploy")

        config = json.loads(config_path.read_text(encoding="utf-8"))
        self.assertEqual(config.get("framework"), None)


if __name__ == "__main__":
    unittest.main()
