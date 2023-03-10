import environ
import os

env = environ.Env(
    DEBUG=(bool, False),
    CAPTCHA=(bool, False),
    API_ON=(bool, True),
    WWW_ON=(bool, True),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
CAPTCHA = env('CAPTCHA')
ALLOWED_HOSTS = env('ALLOWED_HOSTS').split()

SITE_ID = 1

API_ON = env('API_ON')
WWW_ON = env('WWW_ON')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'core',  # djangochan
    'precise_bbcode',
    'simplemathcaptcha',
    'siteprofile',
    'sorl.thumbnail',
]

if API_ON:
    INSTALLED_APPS += [
        'api',  # djangochan
        'rest_framework',
    ]

if WWW_ON:
    INSTALLED_APPS += [
        'boards',  # djangochan
    ]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'djangochan.middleware.timezone_middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'djangochan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'siteprofile.context_processors.site_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangochan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR + '/db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, "staticfiles"),)
STATIC_ROOT = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache set up
# https://docs.djangoproject.com/en/4.1/topics/cache/

if DEBUG or not WWW_ON:
    CACHE_BACKEND = 'django.core.cache.backends.dummy.DummyCache'
else:
    CACHE_BACKEND = 'django.core.cache.backends.locmem.LocMemCache'

CACHES = {
    'default': {
        'BACKEND': CACHE_BACKEND,
        'LOCATION': 'djangochan-cache',
    }
}
