import os

from django.conf import settings


DEBUG = getattr(settings, 'STATICASSETS_DEBUG', settings.DEBUG)

MIMETYPES = {
    '.css': 'text/css',
    '.js': 'application/javascript'
}
MIMETYPES.update(**getattr(settings, 'MIMETYPES', {}))

DIRS = getattr(settings, 'STATICASSETS_DIRS', getattr(settings, 'STATICFILES_DIRS'))

CACHE_DIR = os.path.join(getattr(settings, 'STATIC_ROOT', '/tmp'), 'staticassets-cache')

FINDER = getattr(settings, 'STATICASSETS_FINDER', 'staticassets.finder.AssetFinder')

PREPROCESSORS = getattr(settings, 'STATICASSETS_PREPROCESSORS', (
    ('application/javascript', 'staticassets.processors.DirectiveProcessor'),
    ('text/css', 'staticassets.processors.DirectiveProcessor')
))

POSTPROCESSORS = getattr(settings, 'STATICASSETS_POSTPROCESSORS', (
    ('text/css', 'staticassets.processors.ResolvePathsProcessor'),
))

BUNDLEPROCESSORS = getattr(settings, 'STATICASSETS_BUNDLEPROCESSORS', tuple())

COMPILERS = {
    '.sass': 'staticassets.compilers.SassCompiler',
    '.scss': 'staticassets.compilers.SassCompiler',
    '.styl': 'staticassets.compilers.StylusCompiler',
    '.less': 'staticassets.compilers.LessCompiler',
    '.jst': 'staticassets.compilers.JstCompiler',
    '.ejs': 'staticassets.compilers.EjsCompiler',
    '.coffee': 'staticassets.compilers.CoffeeScriptCompiler'
}
COMPILERS.update(**getattr(settings, 'STATICASSETS_COMPILERS', {}))

COMPRESSION = getattr(settings, 'STATICASSETS_COMPRESSION', not DEBUG)

COMPRESSORS = {
    'application/javascript': 'staticassets.compressors.UglifyJSCompressor',
    'text/css': 'staticassets.compressors.YUICompressor'
}
COMPRESSORS.update(**getattr(settings, 'STATICASSETS_COMPRESSORS', {}))

AVAILABLE_EXTENSIONS = MIMETYPES.keys() + COMPILERS.keys()

MANIFESTS = getattr(settings, 'STATICASSETS_MANIFESTS', tuple())

EJS_TEMPLATE_SETTINGS = getattr(settings, 'STATICASSETS_EJS_TEMPLATE_SETTINGS', '{}')
