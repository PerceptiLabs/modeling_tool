import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    cmd = 'pkill -f "celery -A rygg worker"'
    subprocess.call(shlex.split(cmd))
    cmd = 'celery -A rygg worker --hostname ryggworker --loglevel=DEBUG --queues=rygg'
    subprocess.call(shlex.split(cmd))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting celery worker with autoreload...')
        autoreload.run_with_reloader(restart_celery)
