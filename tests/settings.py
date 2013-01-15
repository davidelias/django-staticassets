import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev.db'),
    }
}

INSTALLED_APPS = (
    'django_nose',
    'django.contrib.staticfiles',
    'staticassets',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'fixtures', 'default'),
)

STATICASSETS_COMPILERS = {
    '.coffee': 'staticassets.compilers.CoffeeScriptCompiler'
}

STATICASSETS_DEBUG = True

STATIC_URL = '/static/'
