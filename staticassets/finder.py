import os
import re
import json

from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles import finders
from django.utils.functional import LazyObject

from .assets import Asset, AssetAttributes, AssetNotFound
from . import settings


class BaseAssetFinder(finders.BaseFinder):

    def __init__(self):
        self.assets = {}

    def __getitem__(self, path):
        return self.find(path, bundle=True)

    def find(self, path, bundle=False, **kwargs):
        asset = self.assets.get(path)
        if not asset or asset.expired:
            try:
                name, storage = self.resolve(path)
            except AssetNotFound:
                return None
            asset = Asset.create(name, storage, self, bundle=bundle, **kwargs)
            self.assets[path] = asset
        return asset

    def resolve(self, path):
        exact = self.resolve_exact(path)
        if exact:
            return exact

        attrs = AssetAttributes(path)
        for path in attrs.search_paths:
            regex = self.get_search_regex(path)
            for name, storage in self.list():
                if not regex.search(name):
                    continue
                if os.path.basename(name) == 'component.json':
                    comp = json.load(storage.open(name))
                    main = comp['main'] if isinstance(comp['main'], list) else [comp['main']]
                    _, ext = os.path.splitext(name)
                    for comp_name in main:
                        _, comp_ext = os.path.splitext(comp_name)
                        if ext == '' or ext == comp_ext:
                            return os.path.join(os.path.dirname(name), comp_name), storage
                else:
                    return name, storage
        raise AssetNotFound('File "{0}" not found. Tried "{1}"'.format(attrs.path, '", "'.join(attrs.search_paths)))

    @property
    def extensions(self):
        for extension in settings.MIMETYPES.keys():
            yield extension
        for extension in settings.COMPILERS.keys():
            yield extension

    def get_search_regex(self, path):
        available_extensions = list(self.extensions)
        basename = os.path.basename(path)
        for ext in re.findall(r'\.[^.]+', basename):
            if ext in available_extensions:
                basename = basename.replace(ext, '')
        extension_pattern = '|'.join([r'\{0}'.format(ext) for ext in available_extensions])
        path = os.path.join(os.path.dirname(path), basename)
        return re.compile(r'{0}({1})*$'.format(path, extension_pattern))

    def list(self):
        raise NotImplementedError()

    def resolve_exact(self):
        raise NotImplementedError()


class StaticFilesFinder(BaseAssetFinder):
    def list(self):
        for finder in finders.get_finders():
            for result in finder.list(None):
                yield result

    def resolve_exact(self, path):
        result = finders.find(path)
        if result and os.path.isfile(result):
            return path, FileSystemStorage(location=result[:-len(path)])


class ConfiguredFinder(LazyObject):
    def _setup(self):
        self._wrapped = finders.get_finder(settings.FINDER)

default_finder = ConfiguredFinder()


def find(*args, **kwargs):
    return default_finder.find(*args, **kwargs)
