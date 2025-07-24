from django.urls import path, include
from account.views import *

# from djangosaml2.views import LoginView

urlpatterns = [
    # retain legacy login and 2fa urls
    path("password/", change_password_view, name="password-change"),
    # login.html
    path("auth/login/", custom_login_view, name="login"),
    path("auth/logout/", custom_logout_view, name="logout"),
    # entry_opt.html
    path("auth/otp-etnry/", otp_entry_view, name="otp-entry"),
    path(
        "auth/twofactor/disable-confirmation/",
        Disable2FAConfirmation.as_view(),
        name="disable-2fa-confirmation",
    ),
    # backup_tokens.html
    path(
        "auth/twofactor/backup-tokens/",
        BackupTokensView.as_view(),
        name="backup-tokens",
    ),
    # setup_2fa.html
    path("auth/twofactor/setup/", Setup2FAView.as_view(), name="setup-2fa"),
    # ajax calls
    path(
        "auth/twofactor/backup-tokens/regenerate/",
        regenerate_backup_tokens,
        name="regenerate-backup-tokens",
    ),
    path(
        "auth/twofactor/backup-tokens/verify/",
        verify_backup_token,
        name="verify-backup-token",
    ),
    path("auth/twofactor/verify/", verify_2fa_view, name="verify-2fa"),
    path("auth/twofactor/disable/", custom_disable_two_factor, name="disable-2fa"),
    # Azure SAML login
    # path("saml2/", include("djangosaml2.urls")),
    # path("saml2/login/", LoginView.as_view(), name="saml2_login"),
    path("request-access/", request_access_view, name="request-access"),
    path("approve-access/", approve_access_view, name="approve-access"),
]
