import os
import re

from django.utils.functional import cached_property

from .. import processors, compilers, settings


AVAILABLE_EXTENSIONS = {

}


class AssetAttributes(object):
    def __init__(self, path, content_type=None):
        self.path = path
        self._content_type = content_type

    @property
    def search_paths(self):
        paths = [self.path]
        paths.append('%s/component.json' % self.path_without_extensions)
        if os.path.basename(self.path_without_extensions) != 'index':
            paths.append('%s/index%s' % (self.path_without_extensions, ''.join(self.extensions)))
        return paths

    @property
    def dirname(self):
        return os.path.dirname(self.path)

    @cached_property
    def available_extensions(self):
        if not self.content_type:
            return settings.AVAILABLE_EXTENSIONS[:]

        if not self.content_type in AVAILABLE_EXTENSIONS:
            extensions = [e for e, m in settings.MIMETYPES.items() if m == self.content_type]
            extensions += [e for e, m in compilers.get_mimetypes().items() if m == self.content_type]
            AVAILABLE_EXTENSIONS[self.content_type] = extensions

        return AVAILABLE_EXTENSIONS[self.content_type][:]

    @cached_property
    def path_without_extensions(self):
        index = len(''.join(self.extensions))
        return self.path[:-index] if index > 0 else self.path

    @cached_property
    def suffix(self):
        return ''.join([e for e in self.extensions
            if not e in settings.AVAILABLE_EXTENSIONS])

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
