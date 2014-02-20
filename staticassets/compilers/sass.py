from .base import CommandCompiler


class SassCompiler(CommandCompiler):
    content_type = 'text/css'
    options = {'compass': False, 'scss': False}
    command = 'sass'
    params = ['-s', '--trace']

    def get_args(self, asset):
        args = super(SassCompiler, self).get_args(asset)
        if self.compass:
            args.append('--compass')
        if self.scss:
            args.append('--scss')
        args += ['-I', asset.storage.path(asset.attributes.dirname)]
        return args
