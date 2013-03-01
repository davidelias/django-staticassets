import os

from staticassets import AssetAttributes
from staticassets.assets import CircularDependencyError
from staticassets.finder import StaticFilesFinder

from .test import TestCase


class AssetTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()

    def get_search_regex(self, path):
        return self.finder.get_search_regex(AssetAttributes(path))

    def test_attributes_search_paths(self):
        self.assertEqual([
            'index.js',
            'index/component.json'
        ], AssetAttributes('index.js').search_paths)

        self.assertEqual([
            'foo.min.js',
            'foo/component.json',
            'foo/index.min.js'
        ], AssetAttributes('foo.min.js').search_paths)

        self.assertEqual([
            'bar',
            'bar/component.json',
            'bar/index'
        ], AssetAttributes('bar').search_paths)

    def test_attributes_available_extensions(self):
        self.assertItemsEqual(
            ['.coffee', '.ejs', '.js', '.jst'],
            AssetAttributes('foo.js.coffee').available_extensions)

        self.assertItemsEqual(
            ['.coffee', '.css', '.ejs', '.js', '.jst', '.less', '.sass', '.scss', '.styl'],
            AssetAttributes('foo').available_extensions)

        self.assertItemsEqual(
            ['.css', '.less', '.sass', '.scss', '.styl'],
            AssetAttributes('foo', 'text/css').available_extensions)

    def test_attributes_extensions(self):
        self.assertEqual(['.js', '.coffee'], AssetAttributes('foo.js.coffee').extensions)

    def test_attributes_format_extension(self):
        self.assertEqual('.js', AssetAttributes('foo/bar.js.coffee').format_extension)
        self.assertEqual('.js', AssetAttributes('foo/bar.min.coffee').format_extension)
        self.assertEqual('.css', AssetAttributes('foo/bar.sass').format_extension)

    def test_attributes_path_without_extensions(self):
        self.assertEqual('foo/bar', AssetAttributes('foo/bar.js.coffee').path_without_extensions)
        self.assertEqual('foo', AssetAttributes('foo').path_without_extensions)

    def test_asset_source(self):
        self.assertEqual('//= require models\n\nvar App = {Models: {}};\n', self.finder.find('app.js').source)

    def test_asset_content(self):
        asset = self.finder.find('models/User.js')
        asset.content = '(function(){%s})' % asset.content
        self.assertEqual('(function(){App.Models.User = {};\n})', asset.content)

    def test_asset_path(self):
        self.assertEqual(self.fixture_path('models/index.js'), self.finder.find('models').path)

    def test_asset_url(self):
        self.assertEqual('/static/style.css', self.finder.find('style').url)
        self.assertEqual('/static/style.min.css', self.finder.find('style.min.sass').url)
        self.assertEqual('/static/foo.js', self.finder.find('foo.coffee').url)
        self.assertEqual('/static/foo.js', self.finder.find('foo.js').url)
        self.assertEqual('/static/plugin.jquery.js', self.finder.find('plugin.jquery.js').url)

    def test_dependencies(self):
        asset = self.finder.find('app.js')

        app_file = self.fixture_path('app.js')
        models_file = self.fixture_path('models/index.js')
        user_file = self.fixture_path('models/User.js')

        self.assertItemsEqual([
            [app_file, os.path.getmtime(app_file), self.file_digest(app_file)],
            [models_file, os.path.getmtime(models_file), self.file_digest(models_file)],
            [user_file, os.path.getmtime(user_file), self.file_digest(user_file)]
        ], asset.dependencies)

    def test_requirements(self):
        asset = self.finder.find('app.js')

        self.assertEqual([
            self.finder.find('models/index.js').path,
        ], [a.path for a in asset.requirements])

        self.assertEqual([
            self.finder.find('models/User.js').path,
            self.finder.find('models/index.js').path,
            self.finder.find('app.js').path,
        ], [a.path for a in asset])

    def test_circular_require_raises_exception(self):
        self.assertRaises(CircularDependencyError, self.finder.find, 'circular/a.js')
        self.assertRaises(CircularDependencyError, self.finder.find, 'circular/b.js')
        self.assertRaises(CircularDependencyError, self.finder.find, 'circular/c.js')

    def test_require_directory(self):
        self.assertEqual('var A = {};\nvar B = {};\n', self.finder.find('base.js', bundle=True).content)
