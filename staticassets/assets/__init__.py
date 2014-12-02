import os
import logging

from time import time

from django.conf import settings as django_settings
from django.core.files.storage import get_storage_class
from django.utils.functional import cached_property

from .. import utils
from ..exceptions import CircularDependencyError
from .attributes import AssetAttributes

import staticassets


logger = logging.getLogger(__name__)

Storage = get_storage_class(django_settings.STATICFILES_STORAGE)


class AssetCacheMixin(object):

    def __getstate__(self):
        return {
            'name': self.name,
            'mtime': self.mtime,
            'content': self.content,
            'content_type': self.attributes.content_type,
            'location': self.storage.location
        }

    def __setstate__(self, state):
        self.name = state['name']
        self.mtime = state['mtime']
        self.content = state['content']

        self.attributes = AssetAttributes(self.name, state['content_type'])
        self.storage = Storage(location=state['location'])
        self.finder = staticassets.default_finder


class Asset(object):

    def __init__(self, name, storage, content_type=None):
        self.name = name
        self.storage = Storage(location=storage.location)
        self.attributes = AssetAttributes(name, content_type)
        self.finder = staticassets.finder

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.path)

    def __iter__(self):
        yield self

    @staticmethod
    def create(*args, **kwargs):
        bundle = kwargs.pop('bundle') is True
        return AssetBundle(*args, **kwargs) if bundle else AssetProcessed(*args, **kwargs)

    @cached_property
    def source(self):
        return utils.read_file(self.path)

    def _get_content(self):
        return self._content if hasattr(self, '_content') else self.source

    def _set_content(self, content):
        self._content = content

    content = property(_get_content, _set_content)

    @cached_property
    def size(self):
        return len(self.content.encode('utf-8'))

    @cached_property
    def digest(self):
        return utils.get_digest(self.content)

    @property
    def path(self):
        return self.storage.path(self.name)

    @cached_property
    def url(self):
        return self.storage.url(self.attributes.format_name)

    @property
    def expired(self):
        return False

    def process(self, processors):
        start = time()
        for processor in processors:
            processor(self)
        stop = time()
        duration = stop - start
        logger.debug('Processed %s in %.3f\n' % (self.name, duration))


class AssetProcessed(Asset, AssetCacheMixin):
    def __init__(self, *args, **kwargs):
        calls = kwargs.pop('calls', set())
        super(AssetProcessed, self).__init__(*args, **kwargs)

        # prevent require the same dependency per asset
        # copied from http://github.com/gears/gears
        self.calls = calls.copy()
        if self.path in self.calls:
            raise CircularDependencyError("'%s' has already been required" % self.path)
        self.calls.add(self.path)

        self.mtime = os.path.getmtime(self.path)
        self.process(self.attributes.processors)

    def _reset(self):
        self._required_paths = []
        self.dependencies = []
        self.requirements = []
        self.depend_on_asset(self)

    def process(self, *args, **kwargs):
        self._reset()
        super(AssetProcessed, self).process(*args, **kwargs)
        self.mtime = max([d[1] for d in self.dependencies])

    @property
    def expired(self):
        for path, mtime, digest in self.dependencies:
            stat = os.stat(path)
            if not stat:
                return True
            if stat.st_mtime > mtime:
                return True
            if digest != utils.get_path_digest(path):
                return True
        return False

    # Dependencies ==============================

    def depend_on(self, path):
        if isinstance(path, (list, tuple)):
            path, mtime, digest = path
        else:
            mtime, digest = os.path.getmtime(path), utils.get_path_digest(path)
        self.dependencies.append([path, mtime, digest])

    def depend_on_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.find_asset(asset)

        if asset.path == self.path:
            self.depend_on([self.path, self.mtime, self.digest])
        else:
            self.dependencies += asset.dependencies

    def require_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.find_asset(asset, calls=self.calls)

        if not asset.path in self._required_paths:
            self._required_paths.append(asset.path)
            self.requirements.append(asset)
            self.depend_on_asset(asset)

    def find_asset(self, path, **kwargs):
        return self.finder.find(path, bundle=False,
            content_type=self.attributes.content_type, **kwargs)

    def __iter__(self):
        for requirement in self.requirements:
            for asset in requirement:
                yield asset
        yield self

    def __getstate__(self):
        state = super(AssetProcessed, self).__getstate__()
        state['calls'] = self.calls
        state['dependencies'] = self.dependencies
        state['requirements'] = self.requirements
        state['_required_paths'] = getattr(self, '_required_paths', [])
        return state

    def __setstate__(self, state):
        super(AssetProcessed, self).__setstate__(state)
        self.calls = state['calls']
        self.dependencies = state['dependencies']
        self.requirements = state['requirements']
        self._required_paths = state['_required_paths']


class AssetBundle(Asset, AssetCacheMixin):
    def __init__(self, *args, **kwargs):
        super(AssetBundle, self).__init__(*args, **kwargs)

        self.processed = self.finder.find(self.name, bundle=False)
        self.content = ''.join([asset.content for asset in self.processed])
        self.mtime = self.processed.mtime
        self.process(self.attributes.bundle_processors)

    @property
    def expired(self):
        return self.processed.expired

    def __getstate__(self):
        state = super(AssetBundle, self).__getstate__()
        state['processed'] = self.processed
        return state

    def __setstate__(self, state):
        super(AssetBundle, self).__setstate__(state)
        self.processed = state['processed']
