from django.conf import settings


MIMETYPES = {
    '.css': 'text/css',
    '.js': 'application/javascript'
}
MIMETYPES.update(**getattr(settings, 'MIMETYPES', {}))

DIRS = getattr(settings, 'STATICASSETS_DIRS', getattr(settings, 'STATICFILES_DIRS'))

FINDER = getattr(settings, 'STATICASSETS_FINDER', 'staticassets.finder.StaticFilesFinder')

PREPROCESSORS = getattr(settings, 'STATICASSETS_PREPROCESSORS', (
    ('application/javascript', 'staticassets.processors.DirectiveProcessor'),
    ('text/css',               'staticassets.processors.DirectiveProcessor')
))

POSTPROCESSORS = getattr(settings, 'STATICASSETS_POSTPROCESSORS', tuple())

COMPILERS = getattr(settings, 'STATICASSETS_COMPILERS', {})
