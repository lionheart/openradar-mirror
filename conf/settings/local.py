import os

BASE = os.path.abspath(os.path.dirname(__name__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'openradarmirror_local',
        'USER': 'openradarmirror_local',
        'PASSWORD': 'openradarmirror_local',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'openradarmirror'
    }
}

RAVEN_CONFIG = {
    'dsn': ""
}

# Uncomment if you'd like to use S3 for local file storage.
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATICFILES_STORAGE = 'statictastic.backends.VersionedFileSystemStorage'

STATIC_URL = "/static/"

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'

BASE_URL = "http://local.openradarmirror.com"
