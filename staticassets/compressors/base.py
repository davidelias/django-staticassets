from staticassets.filters import BaseFilter, CommandMixin


class BaseCompressor(BaseFilter):
    method = 'compress'


class CommandCompressor(BaseCompressor, CommandMixin):
    def compress(self, asset):
        try:
            asset.content = self.run(asset)
        except Exception as e:
            raise Exception("Error compressing '%s' with command %s" % (asset.path, e))
