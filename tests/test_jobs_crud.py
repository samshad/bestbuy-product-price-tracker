import unittest
from unittest.mock import patch, MagicMock
from app.db.jobs_crud import JobsCRUD, Jobs


class TestJobsCRUD(unittest.TestCase):
    @patch("app.db.jobs_crud.sessionmaker")
    def setUp(self, mock_sessionmaker):
        """Set up the mock database session for testing."""
        self.mock_session = MagicMock()
        mock_sessionmaker.return_value = MagicMock(return_value=self.mock_session)
        self.jobs_crud = JobsCRUD(session_factory=mock_sessionmaker)

    def test_insert_job_success(self):
        """Test successful insertion of a job."""
        self.mock_session.__enter__.return_value = self.mock_session
        self.mock_session.add = MagicMock()  # Ensure 'add' is properly mocked
        self.mock_session.commit = MagicMock()  # Ensure 'commit' is properly mocked

        result = self.jobs_crud.insert_job(
            job_id="123",
            webcode="ABC123",
            status="Pending",
            result="Job created",
            product_id=1,
        )
        self.assertTrue(result)
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_update_job_not_found(self):
        """Test updating a job that does not exist."""
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        self.mock_session.__enter__.return_value = self.mock_session
        self.mock_session.commit = MagicMock()  # Ensure 'commit' is properly mocked

        updates = {"status": "Success"}
        result = self.jobs_crud.update_job("999", updates)

        self.assertFalse(result)
        self.mock_session.commit.assert_not_called()

    def test_update_job_success(self):
        """Test successfully updating a job."""
        mock_job = MagicMock(spec=Jobs)
        mock_job.status = "Pending"  # Set initial status
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = mock_job
        self.mock_session.__enter__.return_value = self.mock_session
        self.mock_session.commit = MagicMock()  # Ensure 'commit' is properly mocked

        updates = {"status": "Success", "result": "Job completed"}
        result = self.jobs_crud.update_job("1", updates)

        self.assertTrue(result)
        mock_job.status = "Success"  # Simulate attribute change
        self.assertEqual(mock_job.status, "Success")
        self.mock_session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
