from django.template import loader, Context

from staticassets.finder import StaticFilesFinder

from .test import TestCase


TEMPLATE = """
{% load staticassets %}

{% javascript "app.js" %}
<script src="{{ asset.url }}"></script>
{% endjavascript %}
"""


class TemplateTagsTest(TestCase):
    def setUp(self):
        self.template = loader.get_template_from_string(TEMPLATE)
        self.finder = StaticFilesFinder()

    def test_asset_tag(self):
        self.assertEqual('\n'.join([
            '<script src="/static/models/User.js"></script>',
            '<script src="/static/models/index.js"></script>',
            '<script src="/static/app.js"></script>'
        ]), self.template.render(Context()).strip())
