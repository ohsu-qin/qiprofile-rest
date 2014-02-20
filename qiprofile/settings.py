"""
Django settings for qiprofile project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

import os
import glob

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Fred Loney', 'loneyf@ohsu.edu'),
)

MANAGERS = ADMINS

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # Uncomment the line below and set the SITE_ID to enable multiple sites.
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'qiprofile',
    # Uncomment the next line to enable manage.py test utilities.
    #'django_jasmine',
    # Uncomment the next line to enable manage.py development utilities.
    #'django_extensions',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    # The djangotoolbox NoSQL adapter overrides the standard admin.
    'djangotoolbox',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = dict(
   default=dict(ENGINE='django_mongodb_engine', NAME='qiprofile',
                HOST='localhost', USER='loneyf', PASSWORD='3nigma')
)

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['ohsu.edu']

REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # The REST authentication permission.
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    
    # The query filters.
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
}

# If django.contrib.sites is enabled in the INSTALLED_APPS, then
# make the site before running the initial syncdb 
# (cf. http://stackoverflow.com/questions/8819456/django-mongodb-engine-error-when-running-tellsiteid/9780984#9780984) 
# SITE_ID = u''

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'America/Los_Angeles'

# The project root directory.
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = PROJECT_PATH + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = '/media/'

# Absolute path to the directory static files.
# Don't put anything in this directory yourself; store your static files
# in the STATICFILES_DIRS.
STATIC_ROOT = PROJECT_PATH + '/static'

# URL prefix for static files.
STATIC_URL = '/static/'

# Additional locations of static files.
STATICFILES_DIRS = (
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'b^#exv2=v^!@pyz-w+)2^tf^7x_^kwnt@9rbphpou_6*$vf!2*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    # The TEMPLATE_DIRS loader.
    'django.template.loaders.filesystem.Loader',
    # The app templates directory loader.
    'django.template.loaders.app_directories.Loader',
    # The Python package loader.
    #'django.template.loaders.eggs.Loader',
)

ROOT_URLCONF = 'qiprofile.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'qiprofile.wsgi.application'

# The additional project-level template directories.
TEMPLATE_DIRS = (
)

# The parent directory of the spec subdirectory.
JASMINE_TEST_DIRECTORY = PROJECT_PATH

# The logging performed by this configuration is as follows:
#
# * Send an email to the site admins on every HTTP 500 error when
#   DEBUG=False.
#
# See http://docs.djangoproject.com/en/dev/topics/logging for
# details on logging configuration customization.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
