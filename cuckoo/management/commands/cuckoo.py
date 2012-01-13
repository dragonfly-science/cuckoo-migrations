from .. import models
from django.core.management.base import BaseCommand, CommandError

help_string = """Run database patches using cuckoo
./python manage.py cuckoo will run any patches that haven't yet been applied
"""

commands = {'run':models.models.run, 'force':models.models.force, 'fake':models.models.fake, 'tidy': models.models.tidy}
command_list = ['run', 'force', 'fake', 'tidy']
for command in command_list:
    help_string += '\n%15s   %s'%(command, commands[command].__doc__)
    
class Command(BaseCommand):
    args = '[run, force, fake, tidy]'
    help = help_string

    def handle(self, *args, **options):
        results = []
        if not args:
            args = ['run']
        for command in args:
            try:    
                results = commands[command]()
                self.stdout.write('Successfully ran cuckoo (%s)\n' % command)
                if results:
                    self.stdout.write(str(results) + '\n')
            except KeyError:
                raise CommandError('Unknown command %s' % command)
