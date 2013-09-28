from django.template import Library, Node

from .. import finder, settings


register = Library()

MIMETYPES = {
    'javascript': 'application/javascript',
    'stylesheet': 'text/css'
}


class AssetNode(Node):
    def __init__(self, name, mimetype, nodelist):
        self.name = name
        self.nodelist = nodelist
        self.asset = None
        self.options = {
            'content_type': mimetype,
            'bundle': not settings.DEBUG
        }

    def render(self, context):
        if not self.asset:
            self.asset = finder.find(self.name, **self.options)
        return '\n'.join([self.render_asset(a, context) for a in self.asset])

    def render_asset(self, asset, context):
        context['asset'] = asset
        return self.nodelist.render(context).strip()


@register.tag(name='javascript')
@register.tag(name='stylesheet')
def asset(parser, token):
    bits = token.split_contents()
    tag = bits.pop(0)
    name = bits.pop(0).strip('"').strip("'")
    nodelist = parser.parse(('end%s' % tag,))
    parser.delete_first_token()

    return AssetNode(name, MIMETYPES[tag], nodelist)
