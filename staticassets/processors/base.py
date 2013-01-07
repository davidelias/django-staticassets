from django.utils.functional import memoize, lazy

from .. import settings
from ..utils import get_handler


_processors = {}
_preprocessors = {}
_postprocessors = {}

get_processor = memoize(get_handler, _processors, 1)


class BaseProcessor(object):
    def __call__(self, *args):
        self.process(*args)

    def process(self, asset):
        raise NotImplementedError()


# @lazy(list)
def get_pre(content_type):
    if not _preprocessors:
        prepare_processors(_preprocessors, settings.PREPROCESSORS)
    return _preprocessors.get(content_type, [])


# @lazy(list)
def get_post(content_type):
    if not _postprocessors:
        prepare_processors(_postprocessors, settings.POSTPROCESSORS)
    return _postprocessors.get(content_type, [])


def prepare_processors(cache, processors):
    for processor in processors:
        processor = list(processor)
        content_type = processor.pop(0)
        if not content_type in cache:
            cache[content_type] = []
        cache[content_type].append(get_processor(*processor))

# prepare_processors(_preprocessors, settings.PREPROCESSORS)
# prepare_processors(_postprocessors, settings.POSTPROCESSORS)
