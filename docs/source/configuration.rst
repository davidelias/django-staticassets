Configuration
=============

In your project settings, override Django's default static files storage with the staticassets storage to compile and collect your assets to be served in production,
and define which manifests you want to compile

.. code-block:: python

   STATICFILES_STORAGE = 'staticassets.storage'

   STATICASSETS_MANIFESTS = ('css/application', 'js/application')

Templates
---------

In the templates file, load the staticassets and link your manifests (no need to specify the file extension), the path is appended to the ``STATIC_ROOT`` location

.. code-block:: html

  {% load staticassets %}

    {% stylesheet "css/application" %}
      <link rel="stylesheet" href="{{ asset.url }}"/>
    {% endstylesheet %}

    {% javascript "js/application" %}
      <script src="{{ asset.url }}"></script>
    {% endjavascript %}

Manifests files
---------------

``staticassets`` uses the same directives syntax  and preprocessing as  `Sprockets <http://guides.rubyonrails.org/asset_pipeline.html#manifest-files-and-directives>`_
you can use `Sass <http://sass-lang.com/>`_,  `Less <http://lesscss.org/>`_ and `Stylus <http://learnboost.github.io/stylus/>`_ for stylesheets, and `Coffeescript <http://coffeescript.org/>`_ or `EJS <http://embeddedjs.com/>`_ for scripts, Their compilers just have to be available on the path

Example
*******

stylesheets::

   /*
    *= require application/styles/fonts/lato
    *= require application/styles/fonts/awesome
   */

scripts::

  //= require foundation/jquery
  //= require foundation


Compiling and collecting
------------------------

To compile and collect your assets to the ``STATIC_ROOT`` location, use the ``collectstatic`` command

.. code-block:: bash

   $ manage.py collectstatic

Aditional compilers
-------------------
If you need to develop an aditional compiler for css or javascript, just follow the same directives as the other `compilers <https://github.com/davidelias/django-staticassets/blob/master/staticassets/compilers/coffeescript.py#L4>`_ : extend them from the ``CommandCompiler`` and specify the command and the params, then add them to the ``COMPILERS`` dictionary on the ``static`` assets settings
