from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

from staticassets.handlers import AssetsHandler


class Command(RunserverCommand):
    def get_handler(self, *args, **options):
        handler = super(Command, self).get_handler(*args, **options)
        use_static_handler = options.get('use_static_handler', True)
        insecure_serving = options.get('insecure_serving', False)
        if use_static_handler and (settings.DEBUG or insecure_serving):
            return AssetsHandler(handler)
        return handler
