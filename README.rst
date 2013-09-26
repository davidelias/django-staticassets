=============
Static Assets
=============

django-staticassets is a django app to compile and bundle static assets, it
works together with django's contrib staticfiles app. Heavly inspired by ruby's
`Sprockets <https://github.com/sstephenson/sprockets>`_. it has the same directive processor to declare dependencies
directly in asset source files.


Changelog
=========

0.1
---
initial version


Requirements
============

* Python 2.6+
* Django 1.4+


Instructions
============

to install and use django-static assets just download it using pip and add it to the installed apps on your project settings file::

$ pip install django-staticassets

if your gonna use Sass or Less files you'll also need the sass and less compiler on your path

then You will need to include ``staticassets`` in your ``INSTALLED_APPS``::

  INSTALLED_APPS = (
      ...
      'staticassets',
  )

if ``staticassets`` is not the last app in the list, and you have more applications overriding ``runserver`` command, you will also need to add ``staticassets`` static files handler view in the urls.py::

  from django.conf.urls.static import static

  if settings.DEBUG and settings.STATIC_URL:
  urlpatterns += static(settings.STATIC_URL, view='staticassets.views.serve')

Then in the templates file, load the staticassets and link your manifests (no need to specify the file extension), the path is appended to the STATIC_ROOT location::

  {% load staticassets %}

  {% block stylesheets %}
    {% stylesheet "css/application" %}
      <link rel="stylesheet" href="{{ asset.url }}"/>
    {% endstylesheet %}
  {% endblock %}

  {% block javascripts %}
    {% javascript "js/application" %}
      <script src="{{ asset.url }}"></script>
    {% endjavascript %}
  {% endblock %}

Manifests files
============

``staticassets`` uses the same directives syntax  and preprocessing as  `Sprockets <http://guides.rubyonrails.org/asset_pipeline.html#manifest-files-and-directives>`_
just put your manifest files in the

Example
-------
stylesheets::

   *= require application/styles/fonts/lato
   *= require application/styles/fonts/awesome

scripts::

  //= require foundation/jquery
  //= require foundation


Changelog
=========

- 0.1 initial version

- 0.1.1 fix pypi package missing packages
