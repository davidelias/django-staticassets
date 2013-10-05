import sys

from django.core.files.base import ContentFile
from django.contrib.staticfiles.storage import StaticFilesStorage

from .finder import default_finder as finder
from .assets import AssetBundle
from . import settings


class StaticAssetsStorage(StaticFilesStorage):

    def post_process(self, paths, dry_run=False, **options):
        sys.stdout.write("\nStarting asset preprocessing...\n")

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
            self.save(asset.name, ContentFile(asset.content.encode('utf-8')))
            yield asset.path, self.path(asset.name), True
