import shutil

from django.test.utils import override_settings
from django.core.management import call_command

from staticassets.finder import StaticFilesFinder
from staticassets.storage import StaticAssetsStorage, CachedStaticAssetsStorage

from .test import TestCase, read_file
from . import settings


class StorageTest(TestCase):
    def setUp(self):
        self.finder = StaticFilesFinder()
        self.storage = StaticAssetsStorage()
        self.cached_storage = CachedStaticAssetsStorage()

    def run_collectstatic(self):
        call_command('collectstatic', interactive=False, verbosity='0')

    def tearDown(self):
        super(StorageTest, self).tearDown()
        # shutil.rmtree(settings.STATIC_ROOT)

    @override_settings(STATICFILES_STORAGE='staticassets.storage.StaticAssetsStorage')
    def test_post_process(self):
        self.run_collectstatic()

        self.assertTrue(self.storage.exists('app.js'))
        self.assertTrue(self.storage.exists('app.css'))

        for name in settings.STATICASSETS_MANIFESTS:
            asset = self.finder.find(name, bundle=True)
            content = read_file(self.storage.path(name))
            self.assertEqual(content, asset.content)

    @override_settings(STATICFILES_STORAGE='staticassets.storage.CachedStaticAssetsStorage')
    def test_cached_storage(self):
        self.run_collectstatic()

        self.assertTrue(self.storage.exists('app.733b025a89a1.js'))
        self.assertTrue(self.storage.exists('app.8b57d02a0b57.css'))

        content = read_file(self.storage.path('app.8b57d02a0b57.css'))
        self.assertIn('body {\n    background: url("/static/img/empty.b44917055649.gif");\n}', content)
