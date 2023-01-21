from django.test import Client

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Helps check csrf'

    def handle(self, *args, **kwargs):
        print(Client(enforce_csrf_checks=True))
