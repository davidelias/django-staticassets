from .base import CommandCompiler


class SassCompiler(CommandCompiler):
    content_type = 'text/css'
    options = {'compass': False, 'scss': False}
    command = 'sass'
    params = ['-s', '--trace']

    def get_args(self):
        args = super(SassCompiler, self).get_args()
        if self.compass:
            args.append('--compass')
        if self.scss:
            args.append('--scss')
        args += ['-I', self.asset.storage.path(self.asset.attributes.dirname)]
        return args

    def compile(self, asset):
        self.asset = asset
        return super(SassCompiler, self).compile(asset)
