import os
import re
import shlex

from django.contrib.staticfiles.utils import get_files

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
        asset.content = content.lstrip()

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

    def resolve(self, asset, path):
        if not path.startswith('.'):
            return path
        return os.path.normpath(os.path.join(asset.attributes.dirname, path))

    # Directives ================================

    def process_require(self, asset, path):
        asset.require_asset(self.resolve(asset, path))

    def process_require_directory(self, asset, path):
        path = self.resolve(asset, path)
        asset.depend_on(asset.storage.path(path))
        directories, files = asset.storage.listdir(path)
        for filename in files:
            asset.require_asset(os.path.join(path, filename))

    def process_require_dir(self, asset, path):
        self.process_require_directory(asset, path)

    def process_require_tree(self, asset, path):
        path = self.resolve(asset, path)
        asset.depend_on(asset.storage.path(path))
        for filename in get_files(asset.storage, location=path):
            asset.require_asset(filename)

    def process_depend_on(self, asset, path):
        name, storage = asset.finder.resolve(self.resolve(asset, path))
        asset.depend_on(storage.path(name))
