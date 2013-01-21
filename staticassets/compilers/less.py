from .base import CommandCompiler


class LessCompiler(CommandCompiler):
    content_type = 'text/css'
    command = 'lessc'
    params = ['-']
