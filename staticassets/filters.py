from subprocess import Popen, PIPE

from django.utils.datastructures import SortedDict
from django.utils.functional import memoize

from .utils import get_class

_filters = SortedDict()
_processes = SortedDict()


class BaseFilter(object):
    method = None
    options = {}

    def __init__(self, *args, **kwargs):
        for option, default in self.options.items():
            setattr(self, option, kwargs[option] if option in kwargs else default)
        self.options.update(**kwargs)

    def __call__(self, asset):
        if not self.method:
            raise Exception("'%s' filter must specify a method to execute" % self.__class__.__name__)

        method = getattr(self, self.method)
        if method:
            method(asset)


class CommandMixin(object):
    command = None
    params = []

    def get_args(self):
        return [self.options.get('command', self.command)] + self.options.get('params', self.params)

    def run(self, input):
        args = self.get_args()
        process = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, errors = process.communicate(input=input.encode('utf-8'))
        if process.returncode != 0:
            raise Exception("'%s'\n%s" % (' '.join(args), errors))
        return output.decode('utf-8')


def get_filter(filter_conf):
    if isinstance(filter_conf, (tuple, list)):
        filter_conf = list(filter_conf)
    else:
        filter_conf = [filter_conf]
    import_path = filter_conf.pop(0)
    args, kwargs = get_arguments(filter_conf)
    key = ','.join(args) + ','.join(['%s:%s' % (k, v) for k, v in kwargs.items()])
    return get_cached_filter(import_path, key, args, kwargs)


def _get_filter(import_path, key, args, kwargs):
    return get_class(import_path, BaseFilter)(*args, **kwargs)
get_cached_filter = memoize(_get_filter, _filters, 2)


def _get_process(key, args):
    print _processes
    return Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
get_process = memoize(_get_process, _processes, 1)


def get_arguments(conf):
    args, kwargs = [], {}
    for arg in conf:
        if isinstance(arg, dict):
            kwargs = arg
        elif isinstance(arg, (tuple, list)):
            args = arg
        else:
            args.append(arg)
    return args, kwargs
