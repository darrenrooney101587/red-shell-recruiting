import base64
import os
import time
from urllib.parse import urlparse

import psutil
from django.conf import settings
from django.shortcuts import redirect

from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from two_factor.utils import default_device
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import devices_for_user

class RestrictSSOAccessMiddleware:
    """Middleware to allow SSO users but with no permissions until assigned."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.path.startswith(
                "/accounts/auth/otp-entry/"
        ) or request.path.startswith("/accounts/auth/login/"):
            return self.get_response(request)

        is_sso_user = (
                request.session.get("_auth_user_backend")
                == "accounts.views.CustomSAMLBackend"
        )
        if is_sso_user and not request.user.groups.exists():
            messages.warning(
                request,
                "You have successfully logged in via SSO, but an administrator must assign permissions before you can access anything.",
            )
            return redirect("home")

        return self.get_response(request)

class CaptureSAMLResponseMiddleware:
    """Middleware to capture the raw SAMLResponse XML before processing."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/saml2/acs/" and "SAMLResponse" in request.POST:
            raw_saml_response = base64.b64decode(request.POST["SAMLResponse"]).decode(
                "utf-8"
            )
            request.saml_raw_response = raw_saml_response
        return self.get_response(request)


class ForceCustomLoginMiddleware(MiddlewareMixin):
    """Redirects any built-in Django login attempts to the custom login page."""

    def process_request(self, request):
        path = urlparse(request.path_info).path
        if path.strip() in {"/accounts/login", "/account/login"}:
            return redirect(settings.LOGIN_URL)


class EnforceAdminOTP:
    """
    Middleware to enforce OTP authentication for Django Admin.
    Users must have an OTP device and must have verified it to access the admin panel.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings

        if request.path.startswith("/admin/") and request.user.is_authenticated:
            otp_expiry_time = getattr(settings, "OTP_EXPIRY_TIME", 21600)
            otp_verified_key = getattr(settings, "OTP_SESSION_KEY", "otp_verified")
            otp_timestamp_key = getattr(
                settings, "OTP_TIMESTAMP_KEY", "otp_verified_timestamp"
            )

            is_verified = request.session.get(otp_verified_key, False)
            otp_timestamp = request.session.get(otp_timestamp_key, 0)
            current_time = time.time()
            otp_expired = (current_time - otp_timestamp) > otp_expiry_time
            time_left = max(0, otp_expiry_time - (current_time - otp_timestamp))
            has_device = user_has_device(request.user)

            # print(f"Session data in OTP mixin: {request.session.items()}")
            # print(f"Current time: {current_time}")
            # print(f"OTP timestamp: {otp_timestamp}")
            # print(f"OTP expiry time: {otp_expiry_time} seconds")
            # print(f"Time left Until expiry: {time_left} seconds")
            # print(f"OTP Expired: {otp_expired}")
            # print(f"Has device: {has_device}")

            is_sso_user = (
                    request.session.get("_auth_user_backend")
                    == "accounts.views.CustomSAMLBackend"
            )
            if is_sso_user:
                return self.get_response(request)

            if not has_device:
                messages.warning(
                    request,
                    "You must set up Two-Factor Authentication to access the admin panel.",
                )
                return redirect("/")

            if otp_expired:
                messages.warning(
                    request,
                    "OTP verification has expired. Please verify again to access the admin panel.",
                )
                request.session.pop(otp_verified_key, None)
                request.session.pop(otp_timestamp_key, None)
                return redirect("otp-entry")

            if not is_verified:
                messages.warning(
                    request,
                    "You must complete OTP verification to access the admin panel.",
                )
                return redirect("otp-entry")

        return self.get_response(request)


class OTPRequiredMiddleware(MiddlewareMixin):
    """
    Middleware that enforces OTP verification on views using CustomOTPRequiredMixin.
    Instead of redirecting to login, it shows a Django message.
    Works with both:
    - Traditional Django authentication (OTP required)
    - Azure AD SSO authentication (bypasses OTP)
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None  # important, allows unauthenticated users to reach login pages

        view_class = getattr(view_func, "view_class", None)
        otp_required = (
                view_class
                and hasattr(view_class, "otp_required")
                and view_class.otp_required
        )

        if not otp_required:
            return None

        is_sso_user = (
                request.session.get("_auth_user_backend")
                == "accounts.views.CustomSAMLBackend"
        )
        if is_sso_user:
            return None

        otp_verified_key = request.session.get("otp_verified", False)
        devices = TOTPDevice.objects.filter(user=request.user, confirmed=True)
        device = default_device(request.user) or devices.first()

        if device is None:
            messages.warning(
                request,
                "Two-Factor Authentication is required. Please enable 2FA in your profile.",
            )
            return redirect("home")

        if not otp_verified_key:
            messages.warning(
                request, "OTP verification is required to access this page."
            )
            return redirect("otp-entry")

        return None


class ProfilingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if profiling is enabled via the `?profile_page=true` query parameter
        if request.GET.get('profile_page') == 'true':
            process = psutil.Process(os.getpid())

            mem_before = process.memory_info().rss / 1024 / 1024
            cpu_before = process.cpu_percent(interval=None)
            start_time = time.time()

            response = self.get_response(request)

            end_time = time.time()
            mem_after = process.memory_info().rss / 1024 / 1024
            cpu_after = process.cpu_percent(interval=None)

            elapsed_time = end_time - start_time

            print(f"Request profiling: Path={request.path}")
            print(
                f"Start: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
            )
            print(
                f"End: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
            )
            print(f"Duration: {elapsed_time:.2f}s")
            print(f"Memory: {mem_before:.2f}MB -> {mem_after:.2f}MB")
            print(f"CPU: {cpu_before:.1f}% -> {cpu_after:.1f}%")

            if elapsed_time > 90:
                print(
                    f"WARNING: Request took longer than 90 seconds! Path={request.path}, Duration={elapsed_time:.2f}s"
                )

            response['X-Request-Start-Time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(start_time)
            )
            response['X-Request-End-Time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(end_time)
            )
            response['X-Request-Duration'] = f"{elapsed_time:.2f} seconds"
            response['X-Request-Memory-Before'] = f"{mem_before:.2f} MB"
            response['X-Request-Memory-After'] = f"{mem_after:.2f} MB"
            response['X-Request-CPU-Before'] = f"{cpu_before:.1f} %"
            response['X-Request-CPU-After'] = f"{cpu_after:.1f} %"

            return response

        return self.get_response(request)
