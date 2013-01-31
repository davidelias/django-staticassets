from django.contrib.staticfiles.handlers import StaticFilesHandler

from . import views


class AssetsHandler(StaticFilesHandler):
    def serve(self, request):
        return views.serve(request, self.file_path(request.path), insecure=True)
