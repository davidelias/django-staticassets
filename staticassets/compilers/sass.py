from .base import CommandCompiler


class SassCompiler(CommandCompiler):
    content_type = 'text/css'
    options = {'compass': True}
    command = 'sass'
    params = ['--trace']

    def compile(self, asset):
        if self.compass:
            self.params.append('--compass')
        if '.scss' in asset.attributes.extensions:
            self.params.append('--scss')
        return super(SassCompiler, self).compile(asset)
