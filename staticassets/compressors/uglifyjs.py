from .base import CommandCompressor


class UglifyJSCompressor(CommandCompressor):
    command = 'uglifyjs'
    params = ['-c', '--max-line-len', '32']
