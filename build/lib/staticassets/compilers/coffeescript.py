from .base import CommandCompiler


class CoffeeScriptCompiler(CommandCompiler):
    content_type = 'application/javascript'
    command = 'coffee'
    params = ['-sp']
