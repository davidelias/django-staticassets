from unittest2 import TestCase

from staticassets import utils

from ..settings import asset_path


class FindAssetTest(TestCase):

    def test_find_with_an_extension(self):
        name, storage = utils.find('mod/index.js')
        self.assertEqual(asset_path('mod/index.js'), storage.path(name))

    def test_find_without_an_extension(self):
        name, storage = utils.find('mod/index')
        self.assertEqual(asset_path('mod/index.js'), storage.path(name))

    def test_find_nonexistent_file(self):
        self.assertIsNone(utils.find('nonexistent.html'))

    def test_find_file_with_multiple_extensions(self):
        name, storage = utils.find('bar.js')
        self.assertEqual(asset_path('bar.js.coffee'), storage.path(name))
