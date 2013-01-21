from .base import CommandCompiler


class StylusCompiler(CommandCompiler):
    content_type = 'text/css'
    command = 'stylus'
