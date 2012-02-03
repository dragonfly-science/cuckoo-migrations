import sys
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from .. import models

help_string = """cuckoo will run any database patches that haven't yet been applied
"""
commands = {'run':models.models.run, 
    'dryrun': models.models.dryrun,
    'force':models.models.force, 
    'fake':models.models.fake, 
    'status':models.models.status,
    'clean': models.models.clean,
    }
command_list = ['status', 'run', 'dryrun', 'force', 'fake', 'clean']
command_arguments = {'status':('directory',), 'run': ('directory', 'quiet'), 'dryrun': ('directory',),
    'force': ('directory', 'quiet'), 'fake': ('directory', 'quiet'), 'clean':()}

for command in command_list:
    help_string += '\n%15s   %s'%(command, commands[command].__doc__)
    
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    make_option('--path', '-p', dest='path',
        help='Directory where patches are stored'),
    make_option('--quiet', '-q', dest='quiet',
        action="store_true", default=False,
        help='Suppress output of logging information'),
        )
    args = '[run, dryrun, force, fake, clean]'
    help = help_string

    def handle(self, *args, **options):
        results = []

        # check that the database has been initialised
        try:
            list(models.models.Patch.objects.all())
        except:
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
