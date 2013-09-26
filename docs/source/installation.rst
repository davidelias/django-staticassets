Installation
============

Requirements
------------

* Python 2.6+
* Django 1.4+


Instructions
------------

to install and use django-static assets just download it using pip

.. code-block:: bash

   $ pip install django-staticassets

or get it from source

.. code-block:: bash

    $ pip install  git+https://github.com/davidelias/django-staticassets.git#egg=django-staticassets


Then to add Django staticassets to your project, append the app ``staticassets`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
      ...
      'staticassets',
  )


if ``staticassets`` is not the last app in the list, and you have more applications overriding ``runserver`` command, you will also need to add ``staticassets`` static files handler view in the urls.py

.. code-block:: python

  from django.conf.urls.static import static

  if settings.DEBUG and settings.STATIC_URL:
  urlpatterns += static(settings.STATIC_URL, view='staticassets.views.serve')
