import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from garden_core import GardenError, build_site, plant_page


GARDEN_DIR = Path(__file__).resolve().parents[1]
CLI_PATH = GARDEN_DIR / "garden_cli.py"


class GardenCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "templates").mkdir()
        (self.root / "templates" / "blog.md").write_text(
            "---\ntitle: {{TITLE}}\ncreated: {{TODAY}}\ntype: blog\n---\n\nNotes.\n",
            encoding="utf-8",
        )
        (self.root / "pages").mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plant_validates_slug_and_existing_page(self):
        created = plant_page("field-note", root_dir=self.root)
        self.assertTrue(created.is_file())
        with self.assertRaises(GardenError):
            plant_page("../outside", root_dir=self.root)
        with self.assertRaises(GardenError):
            plant_page("outside", page_type="../blog", root_dir=self.root)
        with self.assertRaises(GardenError):
            plant_page("field-note", root_dir=self.root)

    def test_build_uses_root_and_converts_youtube_url(self):
        page_dir = self.root / "pages" / "blog" / "video-note"
        page_dir.mkdir(parents=True)
        (page_dir / "content.md").write_text(
            "---\ntitle: Video Note\ntype: blog\ncreated: 2026-10-05\n---\n\n"
            "https://www.youtube.com/watch?v=ipVFRH6TQfM\n",
            encoding="utf-8",
        )

        result = build_site(root_dir=self.root)

        self.assertEqual(result.updated_pages, 1)
        self.assertTrue(result.index_path.is_file())
        generated_page = (page_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("youtube-nocookie.com/embed/ipVFRH6TQfM", generated_page)


class GardenCliTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *arguments],
            cwd=Path(tempfile.gettempdir()),
            capture_output=True,
            text=True,
        )

    def test_help_accepts_single_dash_alias(self):
        result = self.run_cli("-help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: garden", result.stdout)
        self.assertIn("plant", result.stdout)
        self.assertIn("deploy", result.stdout)

    def test_missing_plant_name_has_usage_error(self):
        result = self.run_cli("plant")
        self.assertEqual(result.returncode, 2)
        self.assertIn("the following arguments are required: name", result.stderr)

    def test_unknown_command_has_usage_error(self):
        result = self.run_cli("publsih")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)

    def test_invalid_page_type_lists_available_types(self):
        result = self.run_cli("plant", "field-note", "--type", "medai")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown page type 'medai'", result.stderr)
        self.assertIn("adventure", result.stderr)


if __name__ == "__main__":
    unittest.main()