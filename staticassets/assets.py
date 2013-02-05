import os
import re

from django.contrib.staticfiles.storage import StaticFilesStorage
from django.utils.functional import cached_property

from . import utils, processors, compilers, settings


class AssetNotFound(Exception):
    pass


class CircularDependencyError(Exception):
    pass


class AssetAttributes(object):
    def __init__(self, path):
        self.path = path

    @staticmethod
    def available_extensions():
        for extension in settings.MIMETYPES.keys():
            yield extension
        for extension in settings.COMPILERS.keys():
            yield extension

    @staticmethod
    def get_path_search_regex(path):
        available_extensions = list(AssetAttributes.available_extensions())
        basename = os.path.basename(path)
        for ext in re.findall(r'\.[^.]+', basename):
            if ext in available_extensions:
                basename = basename.replace(ext, '')
        extension_pattern = '|'.join([r'\{0}'.format(ext) for ext in available_extensions])
        path = os.path.join(os.path.dirname(path), basename)
        return re.compile(r'^{0}({1})*$'.format(path, extension_pattern))

    @property
    def search_paths(self):
        paths = [(self.path, AssetAttributes.get_path_search_regex(self.path))]

        paths.append(('{0}/component.json'.format(self.path_without_extensions), None))

        if os.path.basename(self.path_without_extensions) != 'index':
            path = '{0}/index{1}'.format(self.path_without_extensions, ''.join(self.extensions))
            paths.append((path, AssetAttributes.get_path_search_regex(path)))

        return paths

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @cached_property
    def path_without_extensions(self):
        index = len(''.join(self.extensions))
        return self.path[:-index] if index > 0 else self.path

    @cached_property
    def url(self):
        try:
            path = self.path[:self.path.index(self.format_extension)]
            return path + self.format_extension
        except ValueError:
            available_extensions = list(AssetAttributes.available_extensions())
            extensions = [e for e in self.extensions if not e in available_extensions]
            return self.path_without_extensions + ''.join(extensions) + self.format_extension

    @cached_property
    def extensions(self):
        return re.findall(r'\.[^.]+', os.path.basename(self.path))

    @cached_property
    def format_extension(self):
        for ext in reversed(self.extensions):
            if ext in settings.MIMETYPES and not compilers.get(ext):
                return ext
        for ext, mimetype in settings.MIMETYPES.items():
            if mimetype == self.compiler_content_type:
                return ext

    @cached_property
    def content_type(self):
        for ext in self.extensions:
            if settings.MIMETYPES.get(ext):
                return settings.MIMETYPES.get(ext)
        return self.compiler_content_type

    @cached_property
    def compiler_content_type(self):
        for compiler in self.compilers:
            if compiler.content_type:
                return compiler.content_type

    @property
    def compilers(self):
        for ext in self.extensions:
            compiler = compilers.get(ext)
            if compiler:
                yield compiler

    @property
    def preprocessors(self):
        return processors.pre(self.content_type)

    @property
    def postprocessors(self):
        return processors.post(self.content_type)

    @property
    def bundle_processors(self):
        return processors.bundle(self.content_type)

    @property
    def processors(self):
        return self.preprocessors + list(reversed(list(self.compilers))) + self.postprocessors


class Asset(object):

    def __init__(self, name, storage, finder, content_type=None, calls=set()):
        self.name = name
        self.storage = StaticFilesStorage(location=storage.location)
        self.finder = finder
        self.content_type = content_type
        self.attributes = AssetAttributes(name)

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

    @property
    def url(self):
        return self.storage.url(self.attributes.url)

    @property
    def expired(self):
        for dependency in self.dependencies:
            path, mtime, digest = dependency
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

        for processor in processors or self.attributes.processors:
            processor(self)

    # Dependencies ==============================

    def depend_on(self, path):
        if isinstance(path, (list, tuple)):
            path, mtime, digest = path
        else:
            mtime, digest = os.path.getmtime(path), utils.get_path_digest(path)
        self.dependencies.append([path, mtime, digest])

    def depend_on_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.finder.find(asset, bundle=False)

        if asset.path == self.path:
            self.depend_on([self.path, self.mtime, self.digest])
        else:
            self.dependencies += asset.dependencies

    def require_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.finder.find(asset, bundle=False, calls=self.calls)

        if not asset.path in self._required_paths:
            self._required_paths.append(asset.path)
            self.requirements.append(asset)
            self.depend_on_asset(asset)

    # Cache/Pickling ============================

    def __getstate__(self):
        return {
            'content': self.content,
            'dependencies': self.dependencies,
            'requirements': self.requirements
        }

    def __setstate__(self, state):
        self.content = state['content']
        self.dependencies = state['dependencies']
        self.requirements = state['requirements']


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
        return iter(self.asset)

    @property
    def expired(self):
        return self.asset.expired
