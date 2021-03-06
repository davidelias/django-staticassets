import os
import re
import logging

from time import time

from django.core.cache import get_cache
from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles import finders
from django.utils.functional import SimpleLazyObject

from .assets import Asset, AssetAttributes
from .exceptions import AssetNotFound
from .utils import expand_component_json, get_class
from . import settings


logger = logging.getLogger(__name__)

cache = SimpleLazyObject(lambda: get_cache('django.core.cache.backends.filebased.FileBasedCache', **{
    'LOCATION': os.path.join(settings.CACHE_DIR),
    'TIMEOUT': 60 * 60 * 24 * 30
}))


class BaseAssetFinder(object):
    """
    A base asset finder to be used for custom asset finder classes.
    """
    def find(self, path, bundle=False, **options):
        raise NotImplementedError()


class AssetFinder(BaseAssetFinder):
    """
    Finder to locate any asset, it will use app `django.contrib.staticfiles`
    finders and allow search with or without extensions
    """

    def __init__(self):
        # cache in memory
        self.assets = {}
        self.search_regex = {}

    def find(self, path, **options):
        options.setdefault('bundle', False)

        start = time()
        name, storage = self.resolve(path, **options)
        logger.debug('Resolved %s into %s in %.3f\n' % (path, name, (time() - start)))

        key = self.get_cache_key(storage.path(name), options)
        asset = self.assets.get(key, cache.get(key))
        if not asset or asset.expired:
            asset = self.assets[key] = Asset.create(name, storage, **options)
            cache.set(key, asset)
        return asset

    def resolve(self, path, **options):
        # first try to match the exact filename
        absolute_path = finders.find(path)
        if absolute_path and os.path.isfile(absolute_path):
            return path, FileSystemStorage(location=absolute_path[:-len(path)])

        attrs = AssetAttributes(path, content_type=options.get('content_type'))
        for search_path in attrs.search_paths:
            regex = self.get_search_regex(search_path, options.get('content_type'))
            for name, storage in self.list():
                if search_path.endswith('.json') and search_path == name:
                    for expanded_name in expand_component_json(storage.path(name)):
                        if not attrs.content_type or AssetAttributes(expanded_name).content_type == attrs.content_type:
                            return os.path.join(os.path.dirname(search_path), expanded_name), storage
                elif regex.search(name):
                    return name, storage

        raise AssetNotFound('File "%s" not found. Tried "%s"' % (
            attrs.path, '", "'.join(attrs.search_paths)))

    def list(self):
        for finder in finders.get_finders():
            for result in finder.list(None):
                yield result

    def get_search_regex(self, path, content_type=None):
        if not (path, content_type) in self.search_regex:
            attrs = AssetAttributes(path, content_type)
            # remove all extensions except non compiler and mimetype extensions
            path = attrs.path_without_extensions + attrs.suffix
            pattern = '|'.join([r'\%s' % ext for ext in attrs.available_extensions])
            self.search_regex[(path, content_type)] = re.compile(r'^%s(%s)*$' % (path, pattern))
        return self.search_regex[(path, content_type)]

    def get_cache_key(self, path, options):
        return '%s:bundle:%s' % (path, 1 if options.get('bundle') else 0)


def find(*args, **kwargs):
    return default_finder.find(*args, **kwargs)


def resolve(*args, **kwargs):
    return default_finder.resolve(*args, **kwargs)


default_finder = SimpleLazyObject(lambda: get_class(settings.FINDER, BaseAssetFinder)())

StaticFilesFinder = AssetFinder

