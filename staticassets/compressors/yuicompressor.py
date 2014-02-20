from .base import CommandCompressor


class YUICompressor(CommandCompressor):
    command = 'yuicompressor'

    def get_args(self, asset):
        return super(YUICompressor, self).get_args(asset) + \
            ['--type', asset.attributes.format_extension[1:]]
