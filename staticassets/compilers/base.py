from staticassets import settings
from staticassets.filters import BaseFilter, CommandMixin, get_filter, get_arguments


class BaseCompiler(BaseFilter):
    method = 'compile'

    content_type = None


class CommandCompiler(BaseCompiler, CommandMixin):
    def compile(self, asset):
        asset.content = self.run(asset.content)


def get(extension):
    for ext, compiler in settings.COMPILERS.items():
        if ext != extension:
            continue

        if isinstance(compiler, (tuple, list)):
            compiler = list(compiler)
        else:
            compiler = [compiler]
        return get_filter(compiler.pop(0), *get_arguments(compiler))
