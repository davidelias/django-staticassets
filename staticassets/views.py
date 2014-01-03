import mimetypes

from django.conf import settings as django_settings
from django.http import HttpResponse, HttpResponseNotModified, Http404
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views import static

from staticassets import finder, settings
from .exceptions import AssetNotFound


def serve(request, path, **kwargs):
    mimetype, encoding = mimetypes.guess_type(path)
    if not mimetype in settings.MIMETYPES.values():
        try:
            return staticfiles_serve(request, path, **kwargs)
        except Http404:
            return static.serve(request, path, document_root=django_settings.STATIC_ROOT)

    bundle = request.GET.get('bundle') in ('1', 't', 'true') or not settings.DEBUG
    try:
        asset = finder.find(path, bundle=bundle)
    except AssetNotFound:
        return static.serve(request, path, document_root=django_settings.STATIC_ROOT)

    # Respect the If-Modified-Since header.
    modified_since = request.META.get('HTTP_IF_MODIFIED_SINCE')
    if not static.was_modified_since(modified_since, asset.mtime, asset.size):
        return HttpResponseNotModified(content_type=asset.attributes.content_type)

    response = HttpResponse(asset.content, content_type=asset.attributes.content_type)
    response['Last-Modified'] = static.http_date(asset.mtime)
    response['Content-Length'] = asset.size

    return response
