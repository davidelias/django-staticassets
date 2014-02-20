import sys

from django.core.files.base import ContentFile
from django.contrib.staticfiles.storage import StaticFilesStorage, CachedStaticFilesStorage

from . import settings


class StaticAssetsMixin(object):

    def post_process(self, paths, dry_run=False, **options):
        from .assets import AssetBundle
        from .finder import default_finder as finder

        if dry_run:
            return

        manifests = settings.MANIFESTS
        if not manifests:
            sys.stdout.write("No manifests to process."
                "You have to define the STATICASSETS_MANIFESTS in your settings\n")
            return

        for path in manifests:
            # always use a fresh uncached AssetBundle
            asset = AssetBundle(*finder.resolve(path))
            for dependency in asset.processed:
                self.delete(self.path(dependency.name))

            name = asset.attributes.format_name
            # self.delete(self.path(name))
            self.save(name, ContentFile(asset.content.encode('utf-8')))

            if asset.name in paths:
                del paths[asset.name]
            paths[name] = (self, name)

            yield asset.name, name, True

        super_obj = super(StaticAssetsMixin, self)
        if hasattr(super_obj, 'post_process'):
            for result in super_obj.post_process(paths, dry_run, **options):
                yield result


class StaticAssetsStorage(StaticAssetsMixin, StaticFilesStorage):
    pass


class CachedStaticAssetsStorage(StaticAssetsMixin, CachedStaticFilesStorage):
    pass
