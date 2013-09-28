from django.utils.functional import memoize

from staticassets import settings
from staticassets.filters import BaseFilter, CommandMixin, get_filter


_compilers = {}
_mimetypes = {}


class BaseCompiler(BaseFilter):
    method = 'compile'
    content_type = None


class CommandCompiler(BaseCompiler, CommandMixin):
    def compile(self, asset):
        try:
            asset.content = self.run(asset.content)
        except Exception as e:
            raise Exception("Error compiling '%s' with command %s" % (asset.path, e))


def _get_compiler(extension):
    for ext, compiler in settings.COMPILERS.items():
        if ext == extension:
            return get_filter(compiler)
get = memoize(_get_compiler, _compilers, 1)


def get_mimetypes():
    if not _mimetypes:
        for ext in settings.COMPILERS.keys():
            _mimetypes[ext] = get(ext).content_type
    return _mimetypes
