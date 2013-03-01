import re

from .base import CommandCompiler


class SassCompiler(CommandCompiler):
    content_type = 'text/css'
    options = {'compass': False, 'scss': False}
    command = 'sass'
    params = ['-s', '-g', '--trace']

    def get_args(self):
        args = super(SassCompiler, self).get_args()
        if self.compass:
            args.append('--compass')
        if self.scss:
            args.append('--scss')
        args += ['-I', self.asset.storage.path(self.asset.attributes.dirname)]
        return args
