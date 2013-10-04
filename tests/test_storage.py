import os

from staticassets.finder import StaticFilesFinder
from staticassets.storage import StaticAssetsStorage

from .test import TestCase, read_file
from . import settings


class StorageTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()
        self.path = settings.STATICASSETS_MANIFESTS[0]

    def tearDown(self):
        super(StorageTest, self).tearDown()

        try:
            os.remove(self.path)
        except OSError:
            pass

    def test_collectstatic_collects_file(self):
        StaticAssetsStorage().post_process([])

        manifest = self.finder.find(self.path, bundle=True)
        file = read_file(self.path)
        self.assertEqual(file, manifest.content)
