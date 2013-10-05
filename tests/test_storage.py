import os

from staticassets.finder import StaticFilesFinder
from staticassets.storage import StaticAssetsStorage

from .test import TestCase, read_file
from . import settings


class StorageTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()
        self.storage = StaticAssetsStorage()

    def tearDown(self):
        super(StorageTest, self).tearDown()

        for name in settings.STATICASSETS_MANIFESTS:
            self.storage.delete(name)

    def test_collectstatic_post_process(self):
        for result in self.storage.post_process([]):
            self.assertEqual((
                self.fixture_path('app.js'), self.storage.path('app.js'), True
            ), result)

        for name in settings.STATICASSETS_MANIFESTS:
            asset = self.finder.find(name, bundle=True)
            content = read_file(self.storage.path(name))
            self.assertEqual(content, asset.content)
