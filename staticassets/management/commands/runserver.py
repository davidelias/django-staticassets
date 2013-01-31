from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

from staticassets.handlers import AssetsHandler


class Command(RunserverCommand):
    def get_handler(self, *args, **options):
        handler = super(Command, self).get_handler(*args, **options)
        return AssetsHandler(handler)
