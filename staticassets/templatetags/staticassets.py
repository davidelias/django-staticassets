from django.template import Library, Node

from .. import finder, settings


register = Library()


class AssetNode(Node):
    def __init__(self, name, debug, nodelist):
        self.name = name
        self.debug = debug
        self.nodelist = nodelist
        self.asset = None

    def render(self, context):
        if not self.asset:
            self.asset = finder.find(self.name)
        if settings.DEBUG or self.debug:
            return '\n'.join([self.render_asset(a, context) for a in self.asset])
        return self.render_asset(self.asset, context)

    def render_asset(self, asset, context):
        context['asset'] = asset
        return self.nodelist.render(context).strip()


@register.tag(name='javascript')
@register.tag(name='stylesheet')
def asset(parser, token):
    bits = token.split_contents()
    tag = bits.pop(0)
    name = bits.pop(0).strip('"').strip("'")
    debug = True if bits and bits.pop() == 'debug' else False
    nodelist = parser.parse(('end%s' % tag,))
    parser.delete_first_token()

    return AssetNode(name, debug, nodelist)
