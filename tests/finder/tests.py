from staticassets.finder import StaticFilesFinder, default_finder as staticassets_finder
from staticassets.assets import AssetNotFound

from ..test import TestCase


class AssetFinderTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()

    def test_default_finder(self):
        self.assertIsNotNone(staticassets_finder)

    def test_available_extensions(self):
        self.assertItemsEqual(['.js', '.css', '.coffee', '.sass'], self.finder.extensions)

    def test_find_pattern(self):
        self.assertRegexpMatches('some/style.css', self.finder.get_search_regex('some/style.css'))
        self.assertRegexpMatches('some/style.css.sass', self.finder.get_search_regex('some/style.css.sass'))

    def test_find_nonexistent_file(self):
        self.assertRaises(AssetNotFound, self.finder.resolve, 'nonexistent.js')

    def test_find_nonexistent_asset(self):
        self.assertIsNone(self.finder.find('nonexistent.js'))

    def test_find_file_with_extension(self):
        name, storage = self.finder.resolve('app.js')
        self.assertEqual(self.fixture_path('app.js'), storage.path(name))

    def test_find_file_without_extension(self):
        name, storage = self.finder.resolve('app')
        self.assertEqual(self.fixture_path('app.js'), storage.path(name))

    def test_find_file_with_multiple_extensions(self):
        name, storage = self.finder.resolve('style.css')
        self.assertEqual(self.fixture_path('style.css.sass'), storage.path(name))

    def test_find_asset_index(self):
        self.assertEqual('models/index.js', self.finder.find('models').name)
