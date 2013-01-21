from .base import BaseCompiler, CommandCompiler


JST_SOURCE = "(function() { %(namespace)s || (%(namespace)s = {}); %(namespace)s['%(name)s'] = %(content)s;}).call(this);"

EJS_COMPILER = """
var u = require('underscore'), source = '';
process.stdin.resume();
process.stdin.setEncoding('utf8');
process.stdin.on('data', function(chunk) { source += chunk; });
process.stdin.on('end', function() { process.stdout.write(u.template(source).source); });
""".strip('\n')


class JstCompiler(BaseCompiler):
    content_type = 'application/javascript'
    options = {
        'namespace': 'this.JST',
        'source': JST_SOURCE
    }

    def compile(self, asset):
        asset.content = self.source % {
            'namespace': self.namespace,
            'name': asset.attributes.path_without_extensions,
            'content': asset.content
        }


class EjsCompiler(CommandCompiler):
    command = 'node'
    params = ['-i', '-e', EJS_COMPILER]
