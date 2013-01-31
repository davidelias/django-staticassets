import os
import codecs
import hashlib

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


def get_handler(import_path):
    module, attr = import_path.rsplit('.', 1)
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' % (module, e))
    try:
        Handler = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, attr))

    return Handler()
