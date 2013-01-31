from .base import CommandCompiler


class SassCompiler(CommandCompiler):
    content_type = 'text/css'
    options = {'compass': True, 'scss': False}
    command = 'sass'
    params = ['--trace']

    def get_args(self):
        args = super(SassCompiler, self).get_args()
        if self.compass:
            args.append('--compass')
        if self.scss:
            args.append('--scss')
        return args
