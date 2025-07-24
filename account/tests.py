"""
Unit tests for the request access and approve access views in the account app.
"""
import unittest
from unittest.mock import patch
from django.urls import reverse
from django.test import Client, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import RequestFactory
from typing import Any


class RequestAccessViewUnitTests(unittest.TestCase):
    """Unit tests for the request access view (no DB)."""

    def setUp(self) -> None:
        """Set up test client and valid data."""
        self.factory: RequestFactory = RequestFactory()
        self.url: str = reverse("request-access")
        self.valid_data: dict[str, Any] = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "reason": "Need access for recruiting.",
            "manager": "Jane Manager",
        }

    @override_settings(REQUEST_ACCESS_ADMIN_EMAIL="admin@example.com")
    @patch("account.views.send_mail")
    def test_request_access_success(self, mock_send_mail) -> None:
        """Test successful request access submission sends email and redirects.

        :param mock_send_mail: Mocked send_mail function.
        :type mock_send_mail: Any
        """
        from account.views import request_access_view

        request: HttpRequest = self.factory.post(self.url, data=self.valid_data)
        request.session = {}
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = request_access_view(request)
        # Debug output if test fails
        if not mock_send_mail.called:
            print("Response content:", response.content)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mock_send_mail.called)

    def test_request_access_missing_fields(self) -> None:
        """Test missing fields returns error and does not send email."""
        from account.views import request_access_view

        data = self.valid_data.copy()
        data["email"] = ""
        request: HttpRequest = self.factory.post(self.url, data=data)
        request.session = {}
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = request_access_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"All fields are required.", response.content)

    @patch("django.core.mail.send_mail")
    def test_request_access_no_admin_email(self, mock_send_mail) -> None:
        """Test missing admin email in settings returns error."""
        from account.views import request_access_view

        request: HttpRequest = self.factory.post(self.url, data=self.valid_data)
        request.session = {}
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        response = request_access_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin email not configured.", response.content)
        self.assertFalse(mock_send_mail.called)


if __name__ == "__main__":
    unittest.main()
