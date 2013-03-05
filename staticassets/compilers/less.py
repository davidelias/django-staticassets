from .base import CommandCompiler


class LessCompiler(CommandCompiler):
    content_type = 'text/css'
    command = 'lessc'
    params = ['-']

    def get_args(self):
        args = super(LessCompiler, self).get_args()
        return args + ['--include-path=%s' % self.asset.storage.path(self.asset.attributes.dirname)]

    def compile(self, asset):
        self.asset = asset
        return super(LessCompiler, self).compile(asset)
