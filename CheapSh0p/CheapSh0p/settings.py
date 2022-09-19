import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os.environ.get('SECRET_KEY', config('SECRET_KEY', default='khjkkhjsewcrdgASFD#RFdaSFaw-2fom-mco-mazsiind'))

DEBUG = int(os.environ.get('DEBUG', default=1))

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

PORT = ['8000']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'online_store.apps.OnlineStoreConfig',
    'API_online_store.apps.ApiOnlineStoreConfig',
    'betterforms',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'online_store.middleware.middleware_views.MiddlewareForAddingViews'
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

ROOT_URLCONF = 'CheapSh0p.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'CheapSh0p.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', config('SQL_ENGINE', default='django.db.backends.sqlite3')),
        'NAME': os.environ.get('POSTGRES_DB', config('POSTGRES_DB', default=os.path.join(BASE_DIR, 'db.sqlite3'))),
        'USER': os.environ.get('POSTGRES_USER', config('POSTGRES_USER', default='user')),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', config('POSTGRES_PASSWORD', default='password')),
        'HOST': os.environ.get('SQL_HOST', config('SQL_HOST', default='localhost')),
        'PORT': os.environ.get('SQL_PORT', config('SQL_PORT', default='5432')),
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache')
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


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


LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = []


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STANDARD_SIZES = os.environ.get('STANDARD_SIZES', config('STANDARD_SIZES',
                                                         default=['S', 'M', 'L', 'XL'],
                                                         cast=lambda v: v.split(',')))
if isinstance(STANDARD_SIZES, str):
    STANDARD_SIZES = STANDARD_SIZES.split(',')

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 5,

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

if DEBUG:
    import socket
    INTERNAL_IPS = ['localhost', '127.0.0.1']
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
