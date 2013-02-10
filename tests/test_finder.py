from staticassets.finder import StaticFilesFinder, default_finder as staticassets_finder
from staticassets.exceptions import AssetNotFound

from .test import TestCase


class FinderTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()

    def test_default_finder(self):
        self.assertIsNotNone(staticassets_finder)

    def test_resolve_nonexistent_file(self):
        self.assertRaises(AssetNotFound, self.finder.resolve, 'nonexistent.js')

    def test_find_nonexistent_asset(self):
        self.assertRaises(AssetNotFound, self.finder.find, 'nonexistent.js')

    def test_resolve_file_with_extension(self):
        name, storage = self.finder.resolve('app.js')
        self.assertEqual(self.fixture_path('app.js'), storage.path(name))

    def test_resolve_file_without_extension(self):
        name, storage = self.finder.resolve('app')
        self.assertEqual(self.fixture_path('app.js'), storage.path(name))

        name, storage = self.finder.resolve('plugin.jquery')
        self.assertEqual(self.fixture_path('plugin.jquery.js'), storage.path(name))

    def test_resolve_file_with_multiple_extensions(self):
        name, storage = self.finder.resolve('style.css')
        self.assertEqual(self.fixture_path('style.css.sass'), storage.path(name))

    def test_find_asset_index(self):
        self.assertEqual('models/index.js', self.finder.find('models').name)

    def test_cached_assets_equal(self):
        asset1 = self.finder.find('app.js')
        asset2 = self.finder.find('app.js')

        self.assertTrue(asset1 is asset2)
