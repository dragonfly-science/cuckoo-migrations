from cuckoo.models import get_patches, run, force, fake, tidy  
from django.core.management.base import BaseCommand, CommandError

help_string = """Run database patches using cuckoo
./python manage.py cuckoo will run any patches that haven't yet been applied
"""

commands = {'run':run, 'force':force, 'fake':fake, 'tidy': tidy, 'get_patches':get_patches}
command_list = ['run', 'force', 'fake', 'tidy', 'get_patches']
for command in command_list:
    help_string.append('\n%15s   %s'%(command, commands[command].__doc__))
    
class Command(BaseCommand):
    args = '[run, force, fake, tidy, get_patches]'
    help = help_string

    def handle(self, *args, **options):
        results = []
        if not args:
            args = ['run']
        for command in args:
            try:    
                results = commands[command]()
                self.stdout.write('Successfully ran cuckoo (%s)' % command)
                if results:
                    self.stdout.write(results)
            except KeyError:
                raise CommandError('Unknown command %s' % command)
