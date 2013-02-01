import os
import re
import json

from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles import finders
from django.utils.datastructures import SortedDict
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
            name, storage = self.resolve(path)
            asset = self.assets[path] = Asset.create(name, storage, self, bundle=bundle, **kwargs)
        return asset

    def resolve(self, path):
        exact = self.resolve_exact(path)
        if exact:
            return exact

        attrs = AssetAttributes(path)
        for path, regex in attrs.search_paths:
            for name, storage in self.list():
                if regex and regex.search(name):
                    return name, storage
                if os.path.basename(name) == 'component.json':
                    comp = json.load(storage.open(name))
                    main = comp['main'] if isinstance(comp['main'], list) else [comp['main']]
                    _, ext = os.path.splitext(name)
                    for comp_name in main:
                        _, comp_ext = os.path.splitext(comp_name)
                        if ext == '' or ext == comp_ext:
                            return os.path.join(os.path.dirname(name), comp_name), storage

        searched_paths = SortedDict(attrs.search_paths).keys()
        raise AssetNotFound('File "{0}" not found. Tried "{1}"'.format(attrs.path, '", "'.join(searched_paths)))

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
