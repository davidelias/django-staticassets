import os
import re

from django.utils.functional import cached_property

from .. import processors, compilers, settings


class AssetAttributes(object):
    def __init__(self, path, content_type=None):
        self.path = path
        self._content_type = content_type

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
    def suffix(self):
        available_extensions = list(AssetAttributes.available_extensions())
        extensions = [e for e in self.extensions if not e in available_extensions]
        return ''.join(extensions + [self.format_extension])

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
        if self._content_type:
            return self._content_type
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
