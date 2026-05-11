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

    def test_github_pages_workflow_exists(self):
        workflow_path = ROOT / ".github" / "workflows" / "deploy-pages.yml"

        self.assertTrue(workflow_path.exists(), "deploy-pages workflow should exist")

        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("actions/configure-pages", workflow)
        self.assertIn("actions/upload-pages-artifact", workflow)
        self.assertIn("actions/deploy-pages", workflow)
        self.assertIn("cp index.html _site/index.html", workflow)
        self.assertIn("cp output/四级备考重点词书-2021到2025-top300.html", workflow)


if __name__ == "__main__":
    unittest.main()
