import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev.db'),
    }
}

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'tests.assets',
    'tests.finder',
    'tests.directive_processor',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'fixtures', 'default'),
)

STATICASSETS_COMPILERS = {
    '.coffee': 'staticassets.compilers.CoffeeScriptCompiler',
    '.sass': 'staticassets.compilers.SassCompiler'
}
