import tempfile
import unittest
from pathlib import Path

from app import create_app


class TodoAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = Path(self.temp_dir.name) / "test.sqlite"
        self.app = create_app(
            {"TESTING": True, "DATABASE": str(database), "SECRET_KEY": "test"}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_render_task(self):
        response = self.client.post("/", data={"title": "Write tests"})

        self.assertEqual(response.status_code, 302)
        page = self.client.get("/")
        self.assertContainsTask(page, "Write tests")

    def test_blank_task_is_ignored(self):
        self.client.post("/", data={"title": "  "})

        page = self.client.get("/")
        self.assertIn(b"No tasks yet", page.data)

    def test_toggle_and_delete_task(self):
        self.client.post("/", data={"title": "Take a break"})
        with self.app.app_context():
            from app import get_db

            task_id = get_db().execute("SELECT id FROM tasks").fetchone()["id"]

        toggled = self.client.post(f"/tasks/{task_id}/toggle")
        self.assertEqual(toggled.status_code, 302)
        self.assertIn(b"completed", self.client.get("/").data)

        deleted = self.client.post(f"/tasks/{task_id}/delete")
        self.assertEqual(deleted.status_code, 302)
        self.assertIn(b"No tasks yet", self.client.get("/").data)

    def assertContainsTask(self, response, title):
        self.assertEqual(response.status_code, 200)
        self.assertIn(title.encode(), response.data)


if __name__ == "__main__":
    unittest.main()
