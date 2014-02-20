from .base import CommandCompressor


class UglifyJSCompressor(CommandCompressor):
    command = 'uglifyjs'
    params = ['-c']
