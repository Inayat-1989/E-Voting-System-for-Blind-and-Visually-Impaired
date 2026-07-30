import os
import tempfile
import unittest

from app import app, init_db


class VotingAppTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        app.config.update(TESTING=True, DATABASE=self.db_path)
        with app.app_context():
            init_db()
        self.client = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_register_login_and_vote_flow(self):
        self.client.post(
            "/register",
            data={"username": "admin", "password": "secret123", "confirm_password": "secret123", "role": "admin"},
            follow_redirects=True,
        )
        self.client.post(
            "/login",
            data={"username": "admin", "password": "secret123"},
            follow_redirects=True,
        )
        resp = self.client.post(
            "/admin/elections",
            data={"title": "Student Council", "description": "Choose the new council", "candidates": "Ava\nBen"},
            follow_redirects=True,
        )
        self.assertIn(b"Student Council", resp.data)

        self.client.get("/logout")
        self.client.post(
            "/register",
            data={"username": "voter1", "password": "secret123", "confirm_password": "secret123"},
            follow_redirects=True,
        )
        self.client.post(
            "/login",
            data={"username": "voter1", "password": "secret123"},
            follow_redirects=True,
        )
        resp = self.client.get("/vote/1", follow_redirects=True)
        self.assertIn(b"Ava", resp.data)
        resp = self.client.post(
            "/vote/1",
            data={"candidate_id": "1"},
            follow_redirects=True,
        )
        self.assertIn(b"Your vote was recorded", resp.data)
        resp = self.client.get("/results/1")
        self.assertIn(b"Ava", resp.data)


if __name__ == "__main__":
    unittest.main()
