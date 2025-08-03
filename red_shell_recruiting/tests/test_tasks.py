import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from celery.exceptions import Ignore, Retry
from django.test import TestCase

from red_shell_recruiting.models import (
    CandidateProfile,
    CandidateResume,
    CandidateDocument,
    CandidateCulinaryPortfolio,
    CandidateProfileTitle,
    SearchVectorProcessingLog,
)
from red_shell_recruiting.tasks import (
    update_resume_search_vector,
    update_document_search_vector,
    update_portfolio_search_vector,
)


class TaskTestCase(TestCase):
    """Base test case for task tests with common setup."""

    def setUp(self) -> None:
        """Set up test data for task tests."""
        self.title = CandidateProfileTitle.objects.create(display_name="Test Title")
        self.candidate = CandidateProfile.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            state="CA",
            city="San Francisco",
            compensation_from=50000,
            compensation_to=80000,
            title=self.title,
        )

    def create_mock_s3_response(self, content: bytes) -> dict:
        """Create a mock S3 response with specified content.

        :param content: The binary content to return from S3
        :return: Mock S3 response dict
        """
        mock_body = Mock()
        mock_body.read.return_value = content
        return {"Body": mock_body}


class ResumeSearchVectorTaskTest(TaskTestCase):
    """Test cases for resume search vector processing task."""

    def setUp(self) -> None:
        """Set up test data specific to resume tests."""
        super().setUp()
        self.resume = CandidateResume.objects.create(
            candidate=self.candidate, file="resumes/test_resume.pdf"
        )

    @patch("red_shell_recruiting.tasks.os.remove")
    @patch("red_shell_recruiting.tasks.textract")
    @patch("red_shell_recruiting.tasks.boto3")
    def test_update_resume_search_vector_success(
        self, mock_boto3: Mock, mock_textract: Mock, mock_os_remove: Mock
    ) -> None:
        """Test successful resume search vector update."""
        # Setup mocks
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = self.create_mock_s3_response(
            b"Test resume content"
        )
        mock_textract.process.return_value = b"Extracted resume text content"

        # Execute task directly (not via .apply())
        update_resume_search_vector(self.resume.id)

        # Verify resume was updated
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.extracted_text, "Extracted resume text content")
        self.assertIsNotNone(self.resume.search_document)

        # Verify candidate profile was updated
        self.candidate.refresh_from_db()
        self.assertIsNotNone(self.candidate.search_document)

        # Verify log entries
        logs = SearchVectorProcessingLog.objects.filter(resume=self.resume)
        self.assertEqual(logs.count(), 2)  # One for resume, one for profile

        resume_log = logs.get(document_type="resume")
        self.assertEqual(resume_log.status, "success")

        profile_log = logs.get(document_type="profile")
        self.assertEqual(profile_log.status, "success")

    def test_update_resume_search_vector_not_found(self) -> None:
        """Test resume search vector update with non-existent resume."""
        # Execute task with invalid ID and expect ignore
        with self.assertRaises(Ignore):
            update_resume_search_vector(99999)

        # Verify failure log exists
        self.assertTrue(
            SearchVectorProcessingLog.objects.filter(
                document_type="resume", status="failed", message="Resume not found."
            ).exists()
        )

    @patch("red_shell_recruiting.tasks.os.remove")
    @patch("red_shell_recruiting.tasks.textract")
    @patch("red_shell_recruiting.tasks.boto3")
    def test_update_resume_search_vector_empty_text(
        self, mock_boto3: Mock, mock_textract: Mock, mock_os_remove: Mock
    ) -> None:
        """Test resume search vector update with empty extracted text."""
        # Setup mocks
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = self.create_mock_s3_response(
            b"Test resume content"
        )
        mock_textract.process.return_value = b"   "  # Empty/whitespace text

        # Execute task and expect ignore
        with self.assertRaises(Ignore):
            update_resume_search_vector(self.resume.id)

        # Verify ignore log
        log = SearchVectorProcessingLog.objects.get(
            resume=self.resume, document_type="resume"
        )
        self.assertEqual(log.status, "ignored")
        self.assertIn("No extracted text found", log.message)

    @patch("red_shell_recruiting.tasks.textract")
    @patch("red_shell_recruiting.tasks.boto3")
    def test_update_resume_search_vector_textract_error(
        self, mock_boto3: Mock, mock_textract: Mock
    ) -> None:
        """Test resume search vector update with textract error."""
        # Setup mocks
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = self.create_mock_s3_response(
            b"Test resume content"
        )
        mock_textract.process.side_effect = Exception("Textract processing failed")

        # Execute task and expect an exception to be raised
        with self.assertRaises(Exception) as context:
            update_resume_search_vector(self.resume.id)

        # Verify the exception contains textract error information
        self.assertIn("Textract processing failed", str(context.exception))


class DocumentSearchVectorTaskTest(TaskTestCase):
    """Test cases for document search vector processing task."""

    def setUp(self) -> None:
        """Set up test data specific to document tests."""
        super().setUp()
        self.document = CandidateDocument.objects.create(
            candidate=self.candidate, file="documents/test_document.pdf"
        )

    @patch("red_shell_recruiting.tasks.textract")
    @patch("red_shell_recruiting.tasks.boto3")
    def test_update_document_search_vector_success(
        self, mock_boto3: Mock, mock_textract: Mock
    ) -> None:
        """Test successful document search vector update."""
        # Setup mocks
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = self.create_mock_s3_response(
            b"Test document content"
        )
        mock_textract.process.return_value = b"Extracted document text content"

        # Execute task directly
        update_document_search_vector(self.document.id)

        # Verify document was updated
        self.document.refresh_from_db()
        self.assertEqual(
            self.document.extracted_text, "Extracted document text content"
        )
        self.assertIsNotNone(self.document.search_document)

        # Verify log entry
        log = SearchVectorProcessingLog.objects.get(document=self.document)
        self.assertEqual(log.status, "success")
        self.assertEqual(log.document_type, "document")

    def test_update_document_search_vector_not_found(self) -> None:
        """Test document search vector update with non-existent document."""
        # Execute task with invalid ID and expect ignore
        with self.assertRaises(Ignore):
            update_document_search_vector(99999)

        # Verify failure log exists
        self.assertTrue(
            SearchVectorProcessingLog.objects.filter(
                document_type="document", status="failed", message="Document not found."
            ).exists()
        )


class PortfolioSearchVectorTaskTest(TaskTestCase):
    """Test cases for portfolio search vector processing task."""

    def setUp(self) -> None:
        """Set up test data specific to portfolio tests."""
        super().setUp()
        self.portfolio = CandidateCulinaryPortfolio.objects.create(
            candidate=self.candidate, file="portfolios/test_portfolio.pdf"
        )

    @patch("red_shell_recruiting.tasks.textract")
    @patch("red_shell_recruiting.tasks.boto3")
    def test_update_portfolio_search_vector_success(
        self, mock_boto3: Mock, mock_textract: Mock
    ) -> None:
        """Test successful portfolio search vector update."""
        # Setup mocks
        mock_s3_client = Mock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = self.create_mock_s3_response(
            b"Test portfolio content"
        )
        mock_textract.process.return_value = b"Extracted portfolio text content"

        # Execute task directly
        update_portfolio_search_vector(self.portfolio.id)

        # Verify portfolio was updated
        self.portfolio.refresh_from_db()
        self.assertEqual(
            self.portfolio.extracted_text, "Extracted portfolio text content"
        )
        self.assertIsNotNone(self.portfolio.search_document)

        # Verify log entry
        log = SearchVectorProcessingLog.objects.get(portfolio=self.portfolio)
        self.assertEqual(log.status, "success")
        self.assertEqual(log.document_type, "portfolio")

    def test_update_portfolio_search_vector_not_found(self) -> None:
        """Test portfolio search vector update with non-existent portfolio."""
        # Execute task with invalid ID and expect ignore
        with self.assertRaises(Ignore):
            update_portfolio_search_vector(99999)

        # Verify failure log exists
        self.assertTrue(
            SearchVectorProcessingLog.objects.filter(
                document_type="portfolio",
                status="failed",
                message="Portfolio not found.",
            ).exists()
        )


if __name__ == "__main__":
    unittest.main()
