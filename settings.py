import os
import imp
# from S3 import CallingFormat
# from boto.s3.connection import OrdinaryCallingFormat

BASE = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
# SERVER_EMAIL = "hi@example.com"

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

MANAGERS = ADMINS
TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

WSGI_APPLICATION = "wsgi.application"

USE_I18N = True
USE_L10N = True
USE_TZ = True

TEMPLATE_DIRS = (
    os.path.join(BASE, "templates"),
)

STATICFILES_DIRS = (os.path.join(BASE, "openradarmirror", "static"),)
STATIC_ROOT = os.path.join(BASE, "collected")

SECRET_KEY = '60-m$$196@=3_qc-b*cfemuo8p-1^7#0$fh_*^a(sueuiike5y'

ALLOWED_HOSTS = [".herokuapp.com"]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.webdesign',
    'django.contrib.staticfiles',

    'app',
    'devserver',
    'statictastic',
    # 'django_object_actions',
    # 'sorl.thumbnail',
    # 'djcelery',
    # 'raven.contrib.django.raven_compat',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'INFO',
        'handlers': ['syslog', 'papertrail', 'sentry', 'console'],
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'condensed': {
            'format': '[%(levelname)s] %(name)s#%(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'papertrail': {
            'format': ':[%(levelname)s] %(name)s#%(lineno)d: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'condensed'
        },
        'syslog': {
            'level': 'INFO',
            'address': '/dev/log',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'condensed',
            'filters': ['require_debug_false'],
        },
        'papertrail': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': ('logs.papertrailapp.com', 22222),
            'filters': ['require_debug_false'],
            'formatter': 'papertrail',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
            'filters': ['require_debug_false'],
        },
    },
   'loggers': {
        'sorl': {
            'handlers': ['syslog', 'console'],
            'propagate': False,
        },
        'raven': {
            'handlers': ['sentry'],
            'propagate': False
        },
#        'django.db.backends': {
#            'level': 'INFO',
#            'propagate': False,
#            'handlers': ['syslog', 'console', 'sentry'],
#        },
#        'django.request': {
#            'level': 'INFO',
#            'propagate': False,
#            'handlers': ['syslog', 'console', 'sentry'],
#        },
    },
}

if not os.path.exists('/dev/log'):
    del LOGGING['handlers']['syslog']['address']
    LOGGING['handlers']['syslog']['class'] = 'logging.StreamHandler'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/account/login'
LOGOUT_URL = '/account/logout'

INTERNAL_IPS = ['127.0.0.1', '0.0.0.0']

DEVSERVER_IGNORED_PREFIXES = ['/static', '/media']
DEVSERVER_MODULES = (
    'devserver.modules.sql.SQLSummaryModule',
    'devserver.modules.profile.ProfileSummaryModule',
)

# Uncomment imports at top to enable S3 integration
#
# AWS_CALLING_FORMAT = CallingFormat.PATH
# AWS_GZIP = True

from boto.s3.connection import OrdinaryCallingFormat
AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
AWS_S3_SECURE_URLS = True
AWS_QUERYSTRING_AUTH = False

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
if AWS_STORAGE_BUCKET_NAME:
    # Optionally change to full CDN url
    STATIC_URL = "https://s3.amazonaws.com/{}/".format(AWS_STORAGE_BUCKET_NAME)
else:
    STATIC_URL = "/static/"

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AWS_STATIC_STORAGE_BUCKET_NAME = os.environ.get("AWS_STATIC_STORAGE_BUCKET_NAME")
AWS_HEADERS = {
        'Cache-Control': "max-age:5, public"
    }

# EMAIL_BACKEND = "django_ses.SESBackend"
# AWS_SES_ACCESS_KEY_ID = ''
# AWS_SES_SECRET_ACCESS_KEY = ''

# SESSION_REDIS_PREFIX = "session"
# SESSION_ENGINE = 'redis_sessions.session'

# SENTRY_PUBLIC_KEY = ""
# SENTRY_SECRET_KEY = ""
# RAVEN_CONFIG = {
#     'dsn': "https://{}:{}@app.getsentry.com/4195".format(SENTRY_PUBLIC_KEY, SENTRY_SECRET_KEY)
# }

DEVSERVER_DEFAULT_ADDR = "0.0.0.0"
DEVSERVER_DEFAULT_PORT = "80"

# django-statictastic querystring support
COMMIT_SHA = ""

settings_path = lambda env: os.path.join(BASE, 'conf', 'settings', '{}.py'.format(env))

GITHUB_API_KEY = os.environ.get("GITHUB_API_KEY")

try:
    from local_settings import *
except ImportError:
    try:
        environment = os.environ['APP_ENVIRONMENT']
    except KeyError:
        raise Exception("""Please set your app environment (APP_ENVIRONMENT).""")
    else:
        config = imp.load_source('local_settings', settings_path(environment))
        from local_settings import *

# Uncomment if using django-celery
# try:
#     import djcelery
#     djcelery.setup_loader()
#     import celeryconfig
# except ImportError:
#    raise ImportError("""Please link the appropriate settings file from conf/settings/celery to `celeryconfig.py` in the project root. E.g.
#
#    (openradarmirror)$ ln -s conf/settings/celery/local.py celeryconfig.py""")

