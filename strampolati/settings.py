"""
Django settings for strampolati project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""
import os
from datetime import timedelta
from pathlib import Path
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-na#1e$-!+y_-_hz%9u$qq0m8l*47y&@_cuic&wbc(fr&(xz58x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django_extensions',
    'unfold',
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.forms",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'debug_toolbar',
    'import_export',
    'guardian',
    'simple_history',
    'django_celery_beat',
    'django_svelte_jsoneditor',
    'djmoney',
    "api.apps.ApiConfig",
    "frontend.apps.FrontendConfig",

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.apple',

    'log_viewer',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt.token_blacklist',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'drf_spectacular'
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    "guardian.backends.ObjectPermissionBackend",
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}

REST_AUTH_SERIALIZERS = {
    'USER_DETAILS_SERIALIZER': 'api.serializers.user.AuthUserSerializer'
}

OLD_PASSWORD_FIELD_ENABLED = True

REST_SESSION_LOGIN = False
REST_USE_JWT = True

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Strampolati API',
    'DESCRIPTION': 'Api ad uso esclusivo della Applicazione Strampolati',
    'VERSION': '1.0.0',
    'CONTACT': {
        "name": "Francesco Miccolis",
        "url": "https://strampolati.it",
        "email": "francesco@strampolati.it",
    },
    'TAGS': ['article', 'audio', 'text'],
    'SCHEMA_PATH_PREFIX': r'/api/v[0-9]',
}

# DataFlair
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_PORT = 587
EMAIL_HOST_USER = 'brandbook00@gmail.com'
EMAIL_HOST_PASSWORD = 'Brvand.B00k2021!'

LOG_VIEWER_FILES_PATTERN = 'strampolati*'
LOG_VIEWER_FILES_DIR = os.path.join(BASE_DIR, 'logs')
LOG_VIEWER_MAX_READ_LINES = 1000  # total log lines will be read
LOG_VIEWER_PAGE_LENGTH = 25  # total log lines per-page
# LOG_VIEWER_PATTERNS = [']OFNI[', ']GUBED[', ']GNINRAW[', ']RORRE[', ']LACITIRC[']
# LOG_VIEWER_PATTERNS = ['INFO]', 'DEBUG]', 'WARNING]', 'ERROR]', 'CRITICAL]']
# LOG_VIEWER_PATTERNS = [' ]OFNI ', ' ]GUBED ', ' ]GNINRAW ', ' ]RORRE ', ' ]LACITIRC ']
LOG_VIEWER_PATTERNS = ['[INFO]', '[DEBUG]', '[WARNING]', '[ERROR]', '[CRITICAL]']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            'format': "[%(levelname)s] [%(asctime)s] [%(relativepath)s:%(lineno)s] - \033[34m%(message)s\033[0m",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'full': {
            'format': "[%(levelname)s] [%(asctime)s] [%(relativepath)s:%(lineno)s] - %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'debug': {
            'format': '[%(levelname)s] %(asctime)s - %(relativepath)s:%(lineno)d\n\033[34m%(message)s\033[0m'
        }
    },
    'filters': {
        'user_filter': {
            '()': 'strampolati.utils.PackagePathFilter'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'strampolati.utils.CustomTimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/strampolati_{0}.log'),
            'when': 'midnight',  # this specifies the interval
            'backupCount': 30,  # how many backup file to keep, 30 days
            'templateName': 'strampolati_{0}.log',
            'formatter': 'full'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'colored'
        },
        'null': {
            'class': 'logging.NullHandler'
        }
    },
    'loggers': {
        'django.server': {
            'handlers': ['console' if DEBUG else 'null'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'filters': ['user_filter'],
            'propagate': False
        },
        'custom': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'filters': ['user_filter']
        }
    },
}

ACCOUNT_EMAIL_VERIFICATION = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = "https://google.com"

AUTH_USER_MODEL = 'api.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "simple_history.middleware.HistoryRequestMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    "strampolati.middleware.ReadonlyExceptionHandlerMiddleware",
]

ROOT_URLCONF = 'strampolati.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'strampolati.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = "admin:login"


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "it-IT"

TIME_ZONE = "Europe/Rome"

USE_I18N = True

USE_TZ = True

LANGUAGES = (
    ("de", _("German")),
    ("en", _("English")),
    ("it", _("Italian")),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"

# STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# MEDIA_ROOT = BASE_DIR / "media"

# MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGOUT_REDIRECT_URL = reverse_lazy("admin:index")
LOGIN_REDIRECT_URL = reverse_lazy("admin:index")

X_FRAME_OPTIONS = 'SAMEORIGIN'

UNFOLD = {
    "SITE_HEADER": _("Strampolati Manager"),
    "SITE_TITLE": _("Strampolati Manager"),
    "SITE_SYMBOL": "settings",
    "SHOW_HISTORY": False,
    "ENVIRONMENT": "strampolati.utils.environment_callback",
    "DASHBOARD_CALLBACK": "strampolati.views.dashboard_callback",
    "LOGIN": {
        "image": lambda request: static("images/login-bg.jpg"),
    },
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "SCRIPTS": [
        # lambda request: static("js/chart.min.js"),
    ],
    "TABS": [
        {
            "models": ["api.expensecategory", "api.expense"],
            "items": [
                {
                    "title": _("Expense Categories"),
                    "icon": "precision_manufacturing",
                    "link": reverse_lazy("admin:api_expensecategory_changelist"),
                },
                {
                    "title": _("Expenses"),
                    "icon": "users",
                    "link": reverse_lazy("admin:api_expense_changelist"),
                },
            ],
        },
        {
            "models": ["api.event", "api.note"],
            "items": [
                {
                    "title": _("Events"),
                    "icon": "globe",
                    "link": reverse_lazy("admin:api_event_changelist"),
                },
                {
                    "title": _("Notes"),
                    "icon": "event_note",
                    "link": reverse_lazy("admin:api_note_changelist"),
                },
            ],
        },
        {
            "models": [
                "django_celery_beat.clockedschedule",
                "django_celery_beat.crontabschedule",
                "django_celery_beat.intervalschedule",
                "django_celery_beat.periodictask",
                "django_celery_beat.solarschedule",
            ],
            "items": [
                {
                    "title": _("Clocked"),
                    "icon": "hourglass_bottom",
                    "link": reverse_lazy(
                        "admin:django_celery_beat_clockedschedule_changelist"
                    ),
                },
                {
                    "title": _("Crontabs"),
                    "icon": "update",
                    "link": reverse_lazy(
                        "admin:django_celery_beat_crontabschedule_changelist"
                    ),
                },
                {
                    "title": _("Intervals"),
                    "icon": "arrow_range",
                    "link": reverse_lazy(
                        "admin:django_celery_beat_intervalschedule_changelist"
                    ),
                },
                {
                    "title": _("Periodic tasks"),
                    "icon": "task",
                    "link": reverse_lazy(
                        "admin:django_celery_beat_periodictask_changelist"
                    ),
                },
                {
                    "title": _("Solar events"),
                    "icon": "event",
                    "link": reverse_lazy(
                        "admin:django_celery_beat_solarschedule_changelist"
                    ),
                },
            ],
        },
    ],
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navigation"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Agents"),
                        "icon": "group",
                        "link": lambda request: reverse_lazy(
                            "admin:api_user_changelist"
                        ),
                        # "link": reverse_lazy("admin:formula_driver_changelist"),
                    },
                    {
                        "title": _("Locations"),
                        "icon": "map",
                        "link": reverse_lazy("admin:api_location_changelist"),
                    },
                    {
                        "title": _("Providers"),
                        "icon": "account_balance",
                        "link": reverse_lazy("admin:api_provider_changelist"),
                        # "badge": "strampolati.utils.badge_callback",
                    },
                    {
                        "title": _("Events"),
                        "icon": "globe",
                        "link": reverse_lazy("admin:api_event_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Types"),
                        "icon": "question_mark",
                        "link": reverse_lazy("admin:api_type_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Contacts"),
                        "icon": "person",
                        "link": reverse_lazy("admin:api_contact_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Expenses"),
                        "icon": "payments",
                        "link": reverse_lazy("admin:api_expense_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Notes"),
                        "icon": "event_note",
                        "link": reverse_lazy("admin:api_note_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Items"),
                        "icon": "inbox",
                        "link": reverse_lazy("admin:api_item_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Standings"),
                        "icon": "grade",
                        "link": reverse_lazy("admin:api_type_changelist"),
                        "permission": "strampolati.utils.permission_callback",
                        # "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "separator": True,
                "items": [
                    {
                        "title": _("Tasks"),
                        "icon": "task_alt",
                        "link": reverse_lazy(
                            "admin:django_celery_beat_clockedschedule_changelist"
                        ),
                    },
                ],
            },
        ],
    },
}
