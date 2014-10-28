from .base import BaseProcessor


class CommonjsProcessor(BaseProcessor):

    options = {
        'extensions': ['.module', '.cjs'],
        'namespace': 'this.require',
        'wrapper': "{namespace}.define({{'{module_name}': function(exports, require, module){{{content};}}}});\n"
    }

    def process(self, asset):
        if any((True for ext in self.extensions if ext in asset.attributes.extensions)):
            asset.content = self.wrapper.format(
                namespace=self.namespace,
                module_name=asset.attributes.path_without_extensions,
                content=asset.content)
            print asset.attributes.path_without_extensions, asset.attributes.extensions
