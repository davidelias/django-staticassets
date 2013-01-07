import os

from unittest2 import TestCase as BaseTestCase

from staticassets.utils import read_file, get_digest

from . import settings


FIXTURES_ROOT = os.path.join(settings.BASE_DIR, 'fixtures')


class TestCase(BaseTestCase):
    fixtures_dir = 'default'

    def fixture_path(self, path):
        return os.path.join(FIXTURES_ROOT, self.fixtures_dir, path)

    def fixture(self, path):
        return read_file(self.fixture_path(path))

    def file_digest(self, path):
        return get_digest(read_file(path))
