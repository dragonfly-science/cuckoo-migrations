import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from .. import models

help_string = """cuckoo will run any database patches that haven't yet been applied
"""
commands = {
    'run':     models.models.run,
    'dryrun':  models.models.dryrun,
    'force':   models.models.force,
    'fake':    models.models.fake,
    'status':  models.models.status,
    'clean':   models.models.clean,
    'refresh': models.models.refresh,
    'create':  models.models.create,
    }
command_list = ['status', 'run', 'dryrun', 'force', 'fake', 'clean', 'refresh', 'create']
command_arguments = {
    'status':  ('directory',),
    'run':     ('directory', 'quiet', 'dba'),
    'dryrun':  ('directory',),
    'force':   ('directory', 'quiet', 'dba'),
    'fake':    ('directory', 'quiet'),
    'clean':   (),
    'refresh': ('dumpfile', 'create', 'quiet', 'yes', 'pgformat'),
    'create':  ('drop', 'quiet', 'yes'),
    }

for command in command_list:
    help_string += '\n%15s   %s'%(command, commands[command].__doc__)

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    make_option('--path', '-p', dest='directory',
        help='Directory where patches are stored'),
    make_option('--dumpfile', '-d', dest='dumpfile',
        help='Dump file for refreshing database'),
    make_option('--yes', '-y', dest='yes',
        action="store_true", default=False,
        help='Answer questions with yes'),
    make_option('--create', '-C', dest='create',
        action="store_true", default=False,
        help='Create database first'),
    make_option('--quiet', '-q', dest='quiet',
        action="store_true", default=False,
        help='Suppress output of logging information'),
    make_option('--dba', '-D', dest='dba',
        action="store_true", default=False,
        help='Run psql scripts as user = dba'),
    make_option('--drop', '-x', dest='drop',
        action="store_true", default=False,
        help='Drop existing database'),
    make_option('--pgformat', '-f', dest='pgformat',
        action="store_true", default=False,
        help='Use pg_restore and postgresql custom format'),
        )
    args = '[run, dryrun, force, fake, clean, refresh, create]'
    help = help_string

    def handle(self, *args, **options):
        results = []

        # check that the database has been initialised
        try:
            list(models.models.Patch.objects.all())
        except:
            if 'refresh' not in args:
                print "The database has not been initialised yet."
                print "Please run 'cuckoo init' first"
                sys.exit(1)

        if not args:
            args = ['run']
        for command in args:
            try:
                kwargs = {}
                for argument in command_arguments[command]:
                    kwargs[argument] = options.get(argument)
                results = commands[command](stream=self.stdout, **kwargs)
            except KeyError:
                raise CommandError('Unknown command %s' % command)
