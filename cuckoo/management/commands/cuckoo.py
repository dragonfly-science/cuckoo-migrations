from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from .. import models

help_string = """Run database patches using cuckoo
./python manage.py cuckoo will run any patches that haven't yet been applied
"""
commands = {'run':models.models.run, 
    'dryrun': models.models.dryrun,
    'force':models.models.force, 
    'fake':models.models.fake, 
    'clean': models.models.clean,
    }
command_list = ['run', 'dryrun', 'force', 'fake', 'clean']
command_arguments = {'run': ('directory', 'quiet'), 'dryrun': ('directory',),
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
        if not args:
            args = ['run']
        for command in args:
            try:
                kwargs = {}
                for argument in command_arguments[command]:
                    kwargs[argument] = options.get(argument)
                results = commands[command](**kwargs)
            except KeyError:
                raise CommandError('Unknown command %s' % command)
