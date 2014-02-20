from .base import CommandCompiler


class LessCompiler(CommandCompiler):
    content_type = 'text/css'
    command = 'lessc'
    params = ['-']

    def get_args(self, asset):
        args = super(LessCompiler, self).get_args(asset)
        return args + ['--include-path=%s' % asset.storage.path(asset.attributes.dirname)]
