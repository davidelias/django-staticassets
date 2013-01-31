from django.utils.functional import memoize

from staticassets import settings
from staticassets.filters import BaseFilter, CommandMixin, get_filter


_preprocessors = {}
_postprocessors = {}
_bundleprocessors = {}


class BaseProcessor(BaseFilter):
    method = 'process'


class CommandProcessor(BaseFilter, CommandMixin):
    def process(self, asset):
        asset.content = self.run(asset.content)


def pre(content_type):
    return get_preprocessors(content_type, settings.PREPROCESSORS)


def post(content_type):
    return get_postprocessors(content_type, settings.POSTPROCESSORS)


def bundle(content_type):
    return get_bundleprocessors(content_type, settings.BUNDLEPROCESSORS)


def _get_processors(content_type, processors_conf):
    processors = []
    for processor in processors_conf:
        processor = list(processor)
        if content_type != processor.pop(0):
            continue

        processors.append(get_filter(processor))
    return processors
get_preprocessors = memoize(_get_processors, _preprocessors, 1)
get_postprocessors = memoize(_get_processors, _postprocessors, 1)
get_bundleprocessors = memoize(_get_processors, _bundleprocessors, 1)
