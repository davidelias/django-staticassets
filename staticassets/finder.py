import os
import re
import json

from django.contrib.staticfiles.finders import get_finders, get_finder
from django.utils.functional import LazyObject

from .assets import Asset, AssetBundle, AssetAttributes, AssetNotFound
from . import settings


class BaseFinder(object):
    assets = {}

    def __getitem__(self, path):
        return self.find(path, bundle=True)

    def find(self, path, bundle=False, **kwargs):
        # TODO: apply cache here
        try:
            name, storage = self.resolve(path)
        except AssetNotFound:
            return None
        return AssetBundle(name, storage, self) if bundle else Asset(name, storage, self)

    def resolve(self, path, base_dir=None):
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


class StaticFilesFinder(BaseFinder):
    def list(self):
        for finder in get_finders():
            for result in finder.list(None):
                yield result


class AssetFinder(object):

    def find(self, path, bundle=False):
        attrs = AssetAttributes(path)
        for path in attrs.search_paths:
            result = self.find_in_finders(path)
            if result:
                return AssetBundle(*result) if bundle else Asset(*result)
        raise AssetNotFound('File "{0}" not found. Tried "{1}"'.format(attrs.path, '", "'.join(attrs.search_paths)))

    def find_in_finders(self, path):
        for finder in get_finders():
            regex = self.get_search_regex(path)
            for name, storage in finder.list(path):
                if regex.search(name):
                    return name, storage
        return None

    def get_asset(self, path):
        pass

    def cache_key(path, **options):
        return '{path}:{bundle}'.format(path=path, **options)

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


def find(path):
    return default_finder.find(path)


class ConfiguredFinder(LazyObject):
    def _setup(self):
        self._wrapped = get_finder(settings.FINDER)

default_finder = ConfiguredFinder()
