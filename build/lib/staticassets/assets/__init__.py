import os
import sys
from time import time

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.functional import cached_property

import staticassets

from .. import utils
from ..exceptions import CircularDependencyError
from .attributes import AssetAttributes


class Asset(object):

    def __init__(self, name, storage, content_type=None, calls=set()):
        self.name = name
        self.storage = StaticFilesStorage(location=storage.location)
        self.attributes = AssetAttributes(name, content_type)
        self.finder = staticassets.finder

        # prevent require the same dependency per asset
        # copied from http://github.com/gears/gears
        self.calls = calls.copy()
        if self.path in self.calls:
            raise CircularDependencyError("'%s' has already been required" % self.path)
        self.calls.add(self.path)

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.path)

    def __iter__(self):
        for requirement in self.requirements:
            for asset in requirement:
                yield asset
        yield self

    def _reset(self):
        self._required_paths = []
        self.dependencies = []
        self.requirements = []
        self.depend_on_asset(self)

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

    @property
    def size(self):
        return len(self.content)

    @property
    def digest(self):
        return utils.get_digest(self.content)

    @property
    def path(self):
        return self.storage.path(self.name)

    @cached_property
    def url(self):
        return self.storage.url(
            self.attributes.path_without_extensions +
            self.attributes.suffix +
            self.attributes.format_extension)

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

    def process(self, processors=None):
        self._reset()

        start = time()
        for processor in processors or self.attributes.processors:
            processor(self)
        stop = time()
        duration = stop - start
        sys.stdout.write('Processed %s in %.3f\n' % (self.name, duration))

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

    # Cache/Pickling ============================

    def __getstate__(self):
        return {
            'name': self.name,
            'mtime': self.mtime,
            'content': self.content,
            'dependencies': self.dependencies,
            'requirements': self.requirements,
            '_required_paths': getattr(self, '_required_paths', []),
            'calls': self.calls,
            'content_type': self.attributes.content_type,
            'location': self.storage.location
        }

    def __setstate__(self, state):
        self.name = state['name']
        self.mtime = state['mtime']
        self.content = state['content']
        self.dependencies = state['dependencies']
        self.requirements = state['requirements']
        self._required_paths = state['_required_paths']
        self.calls = state['calls']

        self.attributes = AssetAttributes(self.name, state['content_type'])
        self.storage = StaticFilesStorage(location=state['location'])
        self.finder = staticassets.finder


class AssetProcessed(Asset):
    def __init__(self, *args, **kwargs):
        super(AssetProcessed, self).__init__(*args, **kwargs)

        self.mtime = os.path.getmtime(self.path)
        self.process()
        self.mtime = max([d[1] for d in self.dependencies])


class AssetBundle(Asset):
    def __init__(self, *args, **kwargs):
        super(AssetBundle, self).__init__(*args, **kwargs)

        self.asset = self.finder.find(self.name, bundle=False)
        self.dependencies = self.asset.dependencies
        self.requirements = list(self.asset)
        self.content = ''.join([asset.content for asset in self.requirements])
        self.mtime = max([d[1] for d in self.dependencies])

    def __iter__(self):
        yield self

    @property
    def expired(self):
        return self.asset.expired

    def __getstate__(self):
        state = super(AssetBundle, self).__getstate__()
        state['asset'] = self.asset
        return state

    def __setstate__(self, state):
        super(AssetBundle, self).__setstate__(state)
        self.asset = state['asset']
