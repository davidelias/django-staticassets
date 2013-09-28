import mimetypes

from django.http import HttpResponse, HttpResponseNotModified, Http404
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views.static import was_modified_since, http_date

from staticassets import finder, settings


def serve(request, path, **kwargs):
    mimetype, encoding = mimetypes.guess_type(path)
    if not mimetype in settings.MIMETYPES.values():
        return staticfiles_serve(request, path, **kwargs)

    bundle = request.GET.get('bundle') in ('1', 't', 'true') or not settings.DEBUG
    asset = finder.find(path, bundle=bundle)
    if not asset:
        raise Http404("Static asset not found")

    # Respect the If-Modified-Since header.
    modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
    if not was_modified_since(modified_since, asset.mtime, asset.size):
        return HttpResponseNotModified(content_type=asset.attributes.content_type)

    response = HttpResponse(asset.content, content_type=asset.attributes.content_type)
    response['Last-Modified'] = http_date(asset.mtime)
    response['Content-Length'] = asset.size

    return response
