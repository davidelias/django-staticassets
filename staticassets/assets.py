import os
import re

from django.utils.functional import cached_property

from . import utils, processors, settings


class AssetNotFound(Exception):
    pass


class AssetAttributes(object):
    def __init__(self, path):
        self.path = path

    @property
    def search_paths(self):
        paths = [self.path]

        if os.path.basename(self.path_without_extensions) != 'index':
            paths.append('{0}/index{1}'.format(self.path_without_extensions, ''.join(self.extensions)))

        paths.append('{0}/component.json'.format(self.path_without_extensions))

        return paths

    @property
    def path_without_extensions(self):
        return self.path[:-len(''.join(self.extensions))]

    @property
    def extensions(self):
        return re.findall(r'\.[^.]+', os.path.basename(self.path))

    @property
    def content_type(self):
        for extension in self.extensions:
            if settings.MIMETYPES.get(extension):
                return settings.MIMETYPES.get(extension)

    @property
    def preprocessors(self):
        return processors.get_pre(self.content_type)

    @property
    def postprocessors(self):
        return processors.get_post(self.content_type)

    @property
    def processors(self):
        return self.preprocessors + self.postprocessors


class Asset(object):

    def __init__(self, name, storage, finder, content_type=None):
        self.name = name
        self.storage = storage
        self.finder = finder
        self.content_type = content_type
        self.attributes = AssetAttributes(self.path)
        self.mtime = os.path.getmtime(self.path)
        self.dependencies = []
        self.requirements = []
        self.depend_on_asset(self)

        self.process()

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.path)

    def __iter__(self):
        for requirement in self.requirements:
            for asset in requirement:
                yield asset
        yield self

    @cached_property
    def source(self):
        return utils.read_file(self.path)

    def _get_content(self):
        return self._content if hasattr(self, '_content') else self.source

    def _set_content(self, content):
        self._content = content

    content = property(_get_content, _set_content)

    @property
    def digest(self):
        return utils.get_digest(self.content)

    @property
    def path(self):
        return self.storage.path(self.name)

    @property
    def expired(self):
        for dependency in self.dependencies:
            path, mtime, digest = dependency
            stat = os.stat(path)
            if not stat:
                return True
            if stat.st_mtime > mtime:
                return True
            # if digest != utils.get_file_digest(path):
            #     return True

        return False

    def process(self, processors=None):
        self.dependencies = []
        self.requirements = []
        self.depend_on_asset(self)

        for processor in processors or self.attributes.processors:
            processor(self)

    # Dependencies ==============================

    def depend_on(self, path):
        if isinstance(path, (list, tuple)):
            path, mtime, digest = path
        else:
            mtime, digest = os.path.getmtime(path), utils.get_digest(utils.read_file(path))
        self.dependencies.append([path, mtime, digest])

    def depend_on_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.finder.find(asset, bundle=False)

        # print "\ndepend_on_asset:", asset.name

        if asset.path == self.path:
            self.depend_on([self.path, self.mtime, self.digest])
        else:
            self.dependencies += asset.dependencies

    def require_asset(self, asset):
        if not isinstance(asset, Asset):
            asset = self.finder.find(asset)
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
        self.requirments = state['requirements']


class AssetBundle(object):
    pass

# class AssetBundle(Asset):
#     def __init__(self, *args, **kwargs):
#         super(AssetBundle, self).__init__(*args, **kwargs)

#         self.asset = finder.find(self.name, bundle=False)
#         self.dependencies = self.asset.dependencies
#         self.requirements = self.asset.requirements
#         self.content = ''.join([asset.content for asset in self.requirements])
#         self.mtime = max([d[1] for d in self.dependencies])

#         self.process(processors=self.attributes.bundle_processors)

#     def __iter__(self):
#         return iter(self.requirements)

#     @property
#     def expired(self):
#         return self.asset.expired
