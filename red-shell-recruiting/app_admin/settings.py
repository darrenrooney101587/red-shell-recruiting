import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from django.contrib.messages import constants as messages
load_dotenv()

def is_running_in_docker():
    """Check if running inside a Docker container."""
    return os.path.exists("/.dockerenv")

def os_env_boolean(name, default):
    """Checks to see of the environment variable maps to true or false"""
    return os.getenv(name, default) in ['true', 'True', 'TRUE', '1', 't', 'y', 'yes']

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

if is_running_in_docker():
    print('Running on Docker')

DEBUG = os.getenv('DEBUG', 'False') == 'True'
if DEBUG:
    print(f"...Found DEBUG flag TRUE, setting Log level to DEBUG")
    DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', "DEBUG")
else:
    print(f"...Setting Log level to INFO")
    DJANGO_LOG_LEVEL = os.getenv('DJANGO_LOG_LEVEL', "INFO")


BASE_DIR = Path(__file__).resolve().parent.parent
SITE_DIR = os.path.join(BASE_DIR, '..')
STATIC_DIR = os.path.join(SITE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = '/static/'
STATIC_ROOT = STATIC_DIR
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
ROOT_URLCONF = 'app_admin.urls'
WSGI_APPLICATION = 'app_admin.wsgi.application'
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    '< change me >'
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True") == "True"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEBUG_TOOLBAR = os_env_boolean('DEBUG_TOOLBAR', os.getenv('DEBUG_TOOLBAR'))
DJANGO_BACKEND_LOG_LEVEL = os.getenv('DJANGO_BACKEND_LOG_LEVEL', "ERROR")
CORS_ALLOW_ALL_ORIGINS = os_env_boolean("CORS_ALLOW_ALL_ORIGINS", "True")
OTP_EXPIRY_TIME = 21600  # 6 hours in seconds
OTP_SESSION_KEY = "otp_verified"
OTP_TIMESTAMP_KEY = "otp_verified_timestamp"
ALLOWED_HOSTS = (
    os.getenv('ALLOWED_HOSTS', '127.0.0.1 localhost').replace('"', '').split()
)
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_admin',
    'account',
    'red_shell_recruiting',
    'mechanic',
    'django_otp',  # Ensure this is installed
    'django_otp.plugins.otp_static',  # Required for Static OTP
    'django_otp.plugins.otp_totp',  # Required for TOTP-based OTP
]

if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    print('...Installed DEBUG_TOOLBAR')

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": 'db' if is_running_in_docker() else os.getenv("POSTGRES_HOST"),
        "PORT": 5432 if is_running_in_docker() else os.getenv("POSTGRES_PORT"),
    },
    'bms': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("BMS_DB", "postgres"),
        "USER": os.getenv("BMS_USER", "postgres"),
        "PASSWORD": os.getenv("BMS_PASSWORD", "postgres"),
        "HOST": os.getenv("BMS_HOST", "localhost"),
        "PORT": os.getenv("BMS_PORT", "5432"),
        'OPTIONS': {
            'options': '-c search_path=public',
            'application_name': f'reporting-sync-server',
        }
    }
}

MIDDLEWARE = [
    'app_admin.middleware.CaptureSAMLResponseMiddleware',
    'app_admin.middleware.ForceCustomLoginMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # OTP
    'app_admin.middleware.EnforceAdminOTP',
    'app_admin.middleware.OTPRequiredMiddleware',
    # "djangosaml2.middleware.SamlSessionMiddleware",  # sml SSO Middleware
    "app_admin.middleware.RestrictSSOAccessMiddleware",
]

if DEBUG_TOOLBAR:
    print('...Found DEBUG_TOOLBAR env. variables, setting toolbar middleware')
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

HOSTNAME = get_hostname_from_allowed_hosts()
DEFAULT_PORT = ":8000" if HOSTNAME == "localhost" else ""
SAML_ACS_URL = os.getenv("SAML_ACS_URL", f"http://{HOSTNAME}{DEFAULT_PORT}/saml2/acs/")
SAML_SLO_URL = os.getenv("SAML_SLO_URL", f"http://{HOSTNAME}{DEFAULT_PORT}/saml2/ls/")
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
                    (SAML_SLO_URL, "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect")
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
LOGIN_URL = "/accounts/auth/login/"
LOGOUT_URL = "/accounts/auth/logout/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/auth/login/"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

DEFAULT_LOGGING_FORMAT = os.getenv('DEFAULT_LOGGING_FORMAT', 'json')
LOGGING = {
    'version': 1,
    'filters': {'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'}},
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'moderate': {'format': '{asctime}[{levelname}] {message}', 'style': '{'},
        'simple': {'format': '{levelname} {message}', 'style': '{'},
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'fmt': '%(levelname)s %(asctime)s %(message)s',
        },
    },
    'handlers': {
        'sql_console': {
            'level': 'DEBUG',
            'filters': [
                'require_debug_true'
            ],  # NO Console logging unless DEBUG is on . This prevents production SQL.
            'class': 'logging.StreamHandler',
            'formatter': DEFAULT_LOGGING_FORMAT,
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': DEFAULT_LOGGING_FORMAT,
        },
    },
    'loggers': {
        '': {'level': 'ERROR', 'handlers': ['console']},
        'django.db.backends': {
            'level': DJANGO_BACKEND_LOG_LEVEL,  # A special log level statement specific to SQL
            'handlers': ['sql_console'],
            'propagate': False,
        },
        'services': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
        'worker': {
            'handlers': ['console'],
            'level': DJANGO_LOG_LEVEL,
            'propagate': False,
        },
    },
}
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # pbkdf2_sha256
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',  # pbkdf2_sha256
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'account.hashers.BMSBCryptPasswordHasher',
]

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning warning',
    messages.ERROR: 'alert-danger error',
}

APP_LOGGERS = {}
for app in INSTALLED_APPS:
    APP_LOGGERS[app] = {
        'handlers': ['console'],
        'level': DJANGO_LOG_LEVEL,
        'propagate': False,
    }
LOGGING['loggers'].update(APP_LOGGERS)
