import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from django.contrib.messages import constants as messages

load_dotenv()


def os_env_boolean(name, default):
    """Checks to see of the environment variable maps to true or false"""
    return os.getenv(name, default) in ["true", "True", "TRUE", "1", "t", "y", "yes"]


def get_hostname_from_allowed_hosts():
    """Retrieve the first valid hostname from ALLOWED_HOSTS, ignoring localhost and 0.0.0.0."""
    raw_allowed_hosts = os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost")
    cleaned_allowed_hosts = raw_allowed_hosts.strip().strip('"').strip("'")
    host_list = cleaned_allowed_hosts.split()
    is_local = all(host in ("127.0.0.1", "localhost") for host in host_list)
    valid_hosts = [
        host for host in host_list if host not in ("127.0.0.1", "localhost", "0.0.0.0")
    ]  # first non-localhost hostname

    # all entries are local, return "localhost", otherwise return the first valid hostname
    return "localhost" if is_local else (valid_hosts[0] if valid_hosts else "localhost")


DEBUG = os_env_boolean("DEBUG", default="false")
if DEBUG:
    print("[STARTUP] Found DEBUG flag TRUE, setting Log level to DEBUG")
    DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "DEBUG")
else:
    print("[STARTUP] Setting Log level to INFO")
    DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = os.path.join(BASE_DIR, "..")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
if not AWS_ACCESS_KEY_ID:
    exit("AWS_ACCESS_KEY_ID environment variable not set")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
if not AWS_SECRET_ACCESS_KEY:
    exit("AWS_SECRET_ACCESS_KEY environment variable not set")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
if not AWS_STORAGE_BUCKET_NAME:
    exit("AWS_STORAGE_BUCKET_NAME environment variable not set")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-2")
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_QUERYSTRING_AUTH = False
ROOT_URLCONF = "app_admin.urls"
WSGI_APPLICATION = "app_admin.wsgi.application"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "< change me >")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEBUG_TOOLBAR = os_env_boolean("DEBUG_TOOLBAR", os.getenv("DEBUG_TOOLBAR"))
DJANGO_BACKEND_LOG_LEVEL = os.getenv("DJANGO_BACKEND_LOG_LEVEL", "ERROR")
CORS_ALLOW_ALL_ORIGINS = os_env_boolean("CORS_ALLOW_ALL_ORIGINS", "True")
OTP_EXPIRY_TIME = 21600  # 6 hours in seconds
OTP_SESSION_KEY = "otp_verified"
OTP_TIMESTAMP_KEY = "otp_verified_timestamp"
ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "127.0.0.1 localhost").replace('"', "").split()
)
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
ENABLE_OTP = os_env_boolean("ENABLE_OTP", "True")
ENABLE_SSO = os_env_boolean("ENABLE_SSO", "True")
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",
    "app_admin",
    "account",
    "red_shell_recruiting",
    "mechanic",
    "django_otp",  # Ensure this is installed
    "django_otp.plugins.otp_static",  # Required for Static OTP
    "django_otp.plugins.otp_totp",  # Required for TOTP-based OTP
]

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    print("[STARTUP] Installed DEBUG_TOOLBAR")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        # use localhost reference to "db" which is our docker-compose service id
        "HOST": "db"
        if os_env_boolean("LOCAL_DOCKER", False)
        else os.getenv("POSTGRES_HOST"),
        "PORT": 5324
        if os_env_boolean("LOCAL_DOCKER", False)
        else os.getenv("POSTGRES_PORT"),
    }
}

MIDDLEWARE = [
    "app_admin.middleware.CaptureSAMLResponseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "app_admin.middleware.ForceCustomLoginMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware"
    # "djangosaml2.middleware.SamlSessionMiddleware",  # sml SSO Middleware
]

if ENABLE_SSO:
    MIDDLEWARE += ["app_admin.middleware.RestrictSSOAccessMiddleware"]

if ENABLE_OTP:
    MIDDLEWARE += [
        "django_otp.middleware.OTPMiddleware",
        "app_admin.middleware.EnforceAdminOTP",
        "app_admin.middleware.OTPRequiredMiddleware",
    ]

if DEBUG_TOOLBAR:
    print("[STARTUP] Found DEBUG_TOOLBAR env. variables, setting toolbar middleware")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

if os.getenv("SETUP_SSO"):
    AUTHENTICATION_BACKENDS += ["account.views.CustomSAMLBackend"]

HOSTNAME = get_hostname_from_allowed_hosts()

if os.getenv("SETUP_SSO"):
    DEFAULT_PORT = ":8000" if HOSTNAME == "localhost" else ""
    SAML_ACS_URL = os.getenv(
        "SAML_ACS_URL", f"http://{HOSTNAME}{DEFAULT_PORT}/saml2/acs/"
    )
    SAML_SLO_URL = os.getenv(
        "SAML_SLO_URL", f"http://{HOSTNAME}{DEFAULT_PORT}/saml2/ls/"
    )
    SAML_OUTPUT_FILE = os.path.join(BASE_DIR, "account/saml", "saml_metadata.xml")
    SAML_CONFIG = {
        "xmlsec_binary": os.getenv(
            "XMLSEC_BINARY", shutil.which("xmlsec1") or "/usr/bin/xmlsec1"
        ),
        "entityid": f"sp-bms-admin-local",
        "metadata": {"local": [SAML_OUTPUT_FILE]},
        "attribute_mapping": {
            "uid": ("username",),
            "mail": ("email",),
            "NameID": ("email",),
        },
        "service": {
            "sp": {
                "name": os.getenv("SAML_SP_NAME", "Local Django SAML Test"),
                "endpoints": {
                    "assertion_consumer_service": [
                        (SAML_ACS_URL, "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST")
                    ],
                    "single_logout_service": [
                        (
                            SAML_SLO_URL,
                            "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
                        )
                    ],
                },
                "allow_unsolicited": True,
                "authn_requests_signed": False,
                "logout_requests_signed": False,
                "want_assertions_signed": True,
                "want_response_signed": False,
            }
        },
    }
LOGIN_URL = "/account/auth/login/"
LOGOUT_URL = "/account/auth/logout/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/account/auth/login/"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DEFAULT_LOGGING_FORMAT = os.getenv("DEFAULT_LOGGING_FORMAT", "json")
LOGGING = {
    "version": 1,
    "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "moderate": {"format": "{asctime}[{levelname}] {message}", "style": "{"},
        "simple": {"format": "{levelname} {message}", "style": "{"},
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(levelname)s %(asctime)s %(message)s",
        },
    },
    "handlers": {
        "sql_console": {
            "level": "DEBUG",
            "filters": [
                "require_debug_true"
            ],  # NO Console logging unless DEBUG is on . This prevents production SQL.
            "class": "logging.StreamHandler",
            "formatter": DEFAULT_LOGGING_FORMAT,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": DEFAULT_LOGGING_FORMAT,
        },
    },
    "loggers": {
        "": {"level": "ERROR", "handlers": ["console"]},
        "django.db.backends": {
            "level": DJANGO_BACKEND_LOG_LEVEL,  # A special log level statement specific to SQL
            "handlers": ["sql_console"],
            "propagate": False,
        },
        "services": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        "worker": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
    },
}
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",  # pbkdf2_sha256
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",  # pbkdf2_sha256
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "account.hashers.BMSBCryptPasswordHasher",
]

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning warning",
    messages.ERROR: "alert-danger error",
}

APP_LOGGERS = {}
for app in INSTALLED_APPS:
    APP_LOGGERS[app] = {
        "handlers": ["console"],
        "level": DJANGO_LOG_LEVEL,
        "propagate": False,
    }
LOGGING["loggers"].update(APP_LOGGERS)
