import os

from django.core.files.base import ContentFile
from django.contrib.staticfiles.storage import StaticFilesStorage

from .finder import default_finder as finder
from . import settings

class StaticAssetsStorage(StaticFilesStorage):

    def post_process(self, paths, dry_run=False, **options):
        if dry_run:
            return []
        try:
            manifests = settings.STATICASSETS_MANIFESTS
        except AttributeError:
            print "you have to define the STATICASSETS_MANIFESTS in the django settings"
            return []
        for manifest in manifests:
            asset = finder.find(manifest, bundle=True)
            try:
                os.remove(self.path(asset.name))
            except OSError:
                pass
            self.save(asset.name, ContentFile(asset.content))
        return []
