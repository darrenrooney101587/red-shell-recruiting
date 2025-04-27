""" Views that are associated with the account and authentication """
import logging
import random
import string
import time

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.views.generic import TemplateView

from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import base64
from io import BytesIO
from PIL import Image
from djangosaml2.backends import Saml2Backend
from django.contrib.auth.models import Group, User

from account.models import LoginAttempt
from account.utilities import get_client_ip_address

logger = logging.getLogger(__name__)


def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password-change')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})


def custom_login_view(request):
    client_ip = get_client_ip_address(request)
    username = request.POST.get("username", "")

    failure_limit = 3
    lockout_time = 3

    last_attempt = (
        LoginAttempt.objects.filter(
            username=username, ip_address=client_ip, success=False
        )
        .order_by('-attempt_time')
        .first()
    )

    failed_attempts_count = LoginAttempt.objects.filter(
        username=username, ip_address=client_ip, success=False
    ).count()

    is_locked_out = False
    remaining_time = None

    if last_attempt:
        elapsed_time = (now() - last_attempt.attempt_time).total_seconds()
        remaining_time = max(0, lockout_time * 60 - elapsed_time)

        if failed_attempts_count >= failure_limit and remaining_time > 0:
            is_locked_out = True

    attempts = LoginAttempt.objects.filter(username=username, ip_address=client_ip)

    context = {
        "is_locked_out": is_locked_out,
        "remaining_time": remaining_time,
        "login_attempts": attempts,
        "failed_attempts_count": failed_attempts_count,
    }

    if request.method == "POST":
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if is_locked_out:
            messages.error(
                request,
                f"Too many login attempts. Try again in {remaining_time // 60:.0f} min {remaining_time % 60:.0f} sec.",
            )
            return render(request, "account/login.html", context)

        if user is not None:
            login(request, user)
            LoginAttempt.clear_attempts(username, client_ip)

            if settings.ENABLE_OTP and settings.ENABLE_OTP == True:
                has_otp_device = TOTPDevice.objects.filter(
                    user=user, confirmed=True
                ).exists()

                if has_otp_device:
                    return redirect("otp-entry")
                else:
                    messages.warning(
                        request, "You need to set up Two-Factor Authentication."
                    )
                    return redirect("setup-2fa")
            else:
                return redirect("/")

        else:
            LoginAttempt.record_attempt(username, client_ip, success=False)
            messages.error(request, "Invalid username or password")

    return render(request, "account/login.html", context)


def custom_logout_view(request):
    otp_verified_key = getattr(settings, "OTP_SESSION_KEY", "otp_verified")
    otp_timestamp_key = getattr(settings, "OTP_TIMESTAMP_KEY", "otp_verified_timestamp")
    request.session.pop(otp_verified_key, None)
    request.session.pop(otp_timestamp_key, None)
    logout(request)
    return redirect("login")


@login_required
def otp_entry_view(request):
    """View for users to enter and verify their OTP"""

    otp_verified_key = getattr(settings, "OTP_SESSION_KEY", "otp_verified")
    otp_timestamp_key = getattr(settings, "OTP_TIMESTAMP_KEY", "otp_verified_timestamp")
    otp_failed_attempts_key = "otp_failed_attempts"

    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

    if not device:
        messages.warning(
            request, "You need to set up Two-Factor Authentication before logging in."
        )
        return redirect("setup-2fa")

    if request.method == "POST":
        otp_token = request.POST.get("otp_token", "")
        otp_failed_attempts = request.session.get(otp_failed_attempts_key, 0)

        if device.verify_token(otp_token):
            otp_timestamp = float(time.time())

            request.session[otp_verified_key] = True
            request.session[otp_timestamp_key] = otp_timestamp
            request.session.pop(otp_failed_attempts_key, None)
            request.session.modified = True
            messages.success(request, "OTP verified successfully!")

            return redirect("/")
        else:
            otp_failed_attempts += 1
            request.session[otp_failed_attempts_key] = otp_failed_attempts

            if otp_failed_attempts >= 2:
                failure_log = {
                    "user": str(request.user),
                    "timestamp": time.time(),
                    "failed_attempts": otp_failed_attempts,
                    "session_data": dict(request.session.items()),
                }
                logger.warning(f"OTP Failure: {failure_log}")

            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, "account/enter_otp.html")


@login_required
def verify_backup_token(request):
    """Verify backup token manually without Django forms."""
    if request.method == "POST":
        backup_token = request.POST.get("backup_token", "").strip()
        user = request.user
        device = StaticDevice.objects.filter(user=user, confirmed=True).first()

        if device:
            token_obj = StaticToken.objects.filter(
                device=device, token=backup_token
            ).first()
            if token_obj:
                token_obj.delete()  # Backup tokens are one-time use

                otp_verified_key = getattr(settings, "OTP_SESSION_KEY", "otp_verified")
                otp_timestamp_key = getattr(
                    settings, "OTP_TIMESTAMP_KEY", "otp_verified_timestamp"
                )
                otp_timestamp = float(time.time())

                request.session[otp_verified_key] = True
                request.session[otp_timestamp_key] = otp_timestamp
                request.session.modified = True

                messages.success(
                    request,
                    "Backup token verified successfully! You are now logged in.",
                )
                return redirect("/")

        messages.error(request, "Invalid backup token. Please try again.")

    return redirect("backup-tokens")


class Disable2FAConfirmation(LoginRequiredMixin, TemplateView):
    template_name = 'account/disable_2fa_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=True)
        if not device:
            context['has_no_device'] = True

        return context


@login_required
def custom_disable_two_factor(request):
    """Custom view to disable 2FA and remove backup tokens."""
    if request.method == 'POST':

        user = request.user
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()

        if not device:
            messages.error(request, "2FA is already disabled or no device found.")
            return redirect("/")

        device.delete()  # remove device
        backup_codes = StaticDevice.objects.filter(user=user, confirmed=True)
        backup_codes.delete()

        return JsonResponse(
            {"message": "Two-Factor Authentication has been successfully disabled."},
            status=200,
        )
    else:
        return JsonResponse({"message": "Method not allowed"}, status=405)


class BackupTokensView(LoginRequiredMixin, TemplateView):
    template_name = "account/backup_tokens.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        device_exists = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        if not device_exists:
            context['has_no_device'] = True
            return context

        backup_codes = StaticDevice.objects.filter(user=user, confirmed=True).first()
        tokens = (
            list(backup_codes.token_set.values_list("token", flat=True))
            if backup_codes
            else []
        )
        context["tokens"] = tokens
        context["has_existing_tokens"] = len(tokens) == 10
        return context


@login_required
def check_backup_tokens(request):
    """Check if the user already has 10 backup tokens."""
    user = request.user
    device = StaticDevice.objects.filter(user=user, confirmed=True).first()
    has_tokens = device and device.token_set.count() == 10
    return JsonResponse({"has_tokens": has_tokens})


@login_required
def regenerate_backup_tokens(request):
    """AJAX call to generate backup tokens but restricts regeneration."""
    user = request.user
    device, _ = StaticDevice.objects.get_or_create(user=user, confirmed=True)
    existing_tokens = list(device.token_set.values_list("token", flat=True))

    if existing_tokens:
        return JsonResponse(
            {
                "error": "You have already generated backup tokens. Please contact the DINO team for assistance."
            },
            status=403,
        )

    def generate_token():
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

    new_tokens = [generate_token() for _ in range(10)]
    for token in new_tokens:
        StaticToken.objects.create(device=device, token=token)

    return JsonResponse({"tokens": new_tokens})


class Setup2FAView(LoginRequiredMixin, TemplateView):
    template_name = "account/setup_2fa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        confirmed_device = TOTPDevice.objects.filter(user=user, confirmed=True)
        if confirmed_device:
            context['already_setup'] = True

        device, created = TOTPDevice.objects.get_or_create(user=user, confirmed=False)
        otp_uri = device.config_url
        qr = qrcode.make(otp_uri)

        if not isinstance(qr, Image.Image):
            qr = qr.get_image()

        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        context["qr_code"] = qr_base64
        return context


@login_required
def verify_2fa_view(request):
    if request.method == "POST":
        user = request.user
        otp_token = request.POST.get("otp_token")

        try:
            device = TOTPDevice.objects.get(user=user, confirmed=False)
        except TOTPDevice.DoesNotExist:
            response_data = {
                "success": False,
                "failed_message": "No pending 2FA setup found.",
            }
            return JsonResponse(response_data, status=400)

        if device.verify_token(otp_token):
            response_data = {"success": True, "redirect_url": "/"}
            device.confirmed = True
            device.save()
            return JsonResponse(response_data, status=200)

        response_data = {"success": False, "failed_message": "Invalid code. Try again."}
        return JsonResponse(response_data, status=400)

    response_data = {"success": False, "failed_message": "Invalid request."}
    return JsonResponse(response_data, status=405)


class CustomSAMLBackend(Saml2Backend):
    """Custom SAML authentication backend to enforce MFA."""

    def authenticate(
            self, request, session_info=None, attribute_mapping=None, *args, **kwargs
    ):
        if session_info is None:
            return None

        attributes = session_info.get("ava", {})

        # authn_info is a dict item provided by djangosaml2 with the
        # auth information used via Azure.  However it doesnt parse the MFA
        # method or if MFA is present, possibly due to a mismatch in expected
        # format.  So we take a first pass at authn_info to check for <AuthnStatement>
        # to contain the MFA info before parsing saml response xml
        '''
            <AuthnStatement
                AuthnInstant="2024-12-27T15:31:57.857Z"
                SessionIndex="_da242938-a4d6-4da6-9b37-abeb99002900"
            >
                <AuthnContext>
                    <AuthnContextClassRef>urn:oasis:names:tc:SAML:2.0:ac:classes:Password</AuthnContextClassRef>
                </AuthnContext>
            </AuthnStatement>
        '''
        authn_methods = attributes.get("authn_methods", [])
        if isinstance(authn_methods, str):
            authn_methods = [authn_methods]

        if not authn_methods and "authn_info" in session_info:
            authn_methods = [method[0] for method in session_info["authn_info"]]

        # djangosaml2 does not parse out the <authnmethodsreferences> tag natively so
        # we need to use the middleware CaptureSAMLResponseMiddleware to capture the response
        # set it in the reqeust and parse it out ourselves.
        '''
            <Attribute Name="http://schemas.microsoft.com/claims/authnmethodsreferences">
                <AttributeValue>http://schemas.microsoft.com/ws/2008/06/identity/authenticationmethod/password</AttributeValue>
                <AttributeValue>http://schemas.microsoft.com/claims/multipleauthn</AttributeValue>
            </Attribute>
        '''
        if "http://schemas.microsoft.com/claims/multipleauthn" not in authn_methods:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(request.saml_raw_response, "xml")
            authn_refs = soup.find_all(
                "Attribute",
                {"Name": "http://schemas.microsoft.com/claims/authnmethodsreferences"},
            )
            authn_methods = [
                value.text
                for attr in authn_refs
                for value in attr.find_all("AttributeValue")
            ]

        # this is the actual check for the MFA presence
        if "http://schemas.microsoft.com/claims/multipleauthn" not in authn_methods:
            logger.warning("MFA is required but was not verified.")
            raise PermissionDenied("MFA is required but was not verified.")

        # extract email from NameID and fallback to emailAddress
        # since Azure is sending the email address as the NameID
        # we can move forward with NameID
        name_id_obj = session_info.get("name_id", None)
        name_id = (
            name_id_obj.text if name_id_obj else attributes.get("emailAddress", [""])[0]
        )
        email = name_id if name_id else attributes.get("mail", [""])[0]

        if not email:
            raise PermissionDenied("No email address found in SAML response")

        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email}
        )

        user.is_staff = True
        if created:
            user.groups.clear()
            user.is_superuser = False

        user.first_name = attributes.get("givenname", [""])[0]
        user.last_name = attributes.get("surname", [""])[0]
        user.save()

        return user
