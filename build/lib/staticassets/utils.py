import os
import codecs
import hashlib
import json

from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module


def read_file(path):
    with codecs.open(path, 'r', encoding='utf-8') as f:
        return f.read()


def get_digest(source):
    return hashlib.md5(source.encode('utf-8')).hexdigest()


def get_path_digest(path):
    if os.path.isfile(path):
        return get_digest(read_file(path))
    elif os.path.isdir(path):
        return get_digest(','.join(os.listdir(path)))


def expand_component_json(self, path):
    component = json.loads(read_file(path))
    if not 'main' in component:
        yield
    elif isinstance(component['main'], list):
        for name in component['main']:
            yield name
    else:
        yield component['main']


def get_class(import_path, class_type):
    """
    """
    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" class.' % (module, attr))
    if not issubclass(cls, class_type):
        raise ImproperlyConfigured('Filter "%s" is not a subclass of "%s"' % (cls, class_type))
    return cls
