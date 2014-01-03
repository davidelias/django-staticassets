import re
import os

from .base import BaseProcessor


class ResolvePathsProcessor(BaseProcessor):

    url_re = re.compile(r"""(url\(['"]{0,1}\s*(.*?)["']{0,1}\))""")

    import_re = re.compile(r"""@import\s*["']\s*(.*?)["']""")


    def process(self, asset):
        content = self.url_re.sub(self.resolve_path(asset), asset.content)
        # asset.content = self.import_re.sub(self.resolve_path(asset), content)
        asset.content = content

    def resolve_path(self, asset):
        attrs = asset.attributes
        def replace(m):
            matched, url = m.groups()
            # Completely ignore http(s) prefixed URLs,
            # absolute, fragments and data-uri URLs
            if url.startswith(('#', 'http:', 'https:', 'data:', '//', '/')):
                return matched
            filepath = os.path.normpath(url)
            fullpath =  os.path.normpath(os.path.join(attrs.dirname, filepath))
            name = fullpath.replace(os.path.normcase(asset.storage.location), '')
            return 'url(%s)' % asset.storage.url(name.strip(os.path.sep))
        return replace
