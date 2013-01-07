import re
import shlex

from .base import BaseProcessor


class DirectiveProcessor(BaseProcessor):

    header_re = re.compile(r"""
      ^ (\s* (
        (/\* .*? \*/) |
        (\#\#\# .*? \#\#\#) |
        (// [^\n]*)+ |
        (\# [^\n]*)+
      ))+
    """, re.S | re.X)

    directive_re = re.compile(r"""
      ^ \W* = \s* (\w+.*?) (?:\*/)? $
    """, re.X)

    def process(self, asset):
        directives, content = self.parse(asset.content)
        self.process_directives(asset, directives)
        asset.content = content.lstrip()  # self.process_content(content)

    def parse(self, content):
        match = self.header_re.match(content)
        if not match:
            return [], content

        header, processed_header, directives = match.group(0), [], []

        for line in header.splitlines():
            match = self.directive_re.match(line)
            if match:
                directives.append(shlex.split(match.group(1).encode('utf-8')))
            else:
                processed_header.append(line)

        return directives, '\n'.join(processed_header) + content[len(header):]

    def process_directives(self, asset, directives):
        for args in directives:
            method = 'process_{0}'.format(args.pop(0))
            if hasattr(self, method):
                getattr(self, method)(asset, *args)

    def process_content(self, content):
        content = [content]
        for path in self.included_paths:
            asset = finder.find(path)
            content.append(asset.content)
        return '\n'.join(content)

    # Directives ================================

    def process_require(self, asset, path):
        asset.require_asset(path)

    def process_require_tree(self, asset, path):
        pass
