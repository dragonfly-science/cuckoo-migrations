import os,re
from copy import deepcopy
import sys
from subprocess import Popen, PIPE, STDOUT, call

from django.db import models, connection
from django.conf import settings

class CuckooError(Exception): pass

class Patch(models.Model):
    """Class to hold information on patches that have been run"""
    patch = models.TextField(unique=True)
    sql = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)
    output = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']

    def execute(self, quiet=False, dba=False):
        """Apply a patch"""
        directory = getattr(settings, 'CUCKOO_DIRECTORY', 'sql-patches')
        patch_file = os.path.join(directory, self.patch)
        try:
            self.output = _execute_file(patch_file, dba=dba)
            self.save()
            if not quiet:
                print '[CUCKOO] Ran patch %s' % self.patch
        except Exception as e:
            print CuckooError("[CUCKOO] Error while executing patch %s\n %s" % (self.patch, e))

def _execute_file(patch_file, exists=True, dba=False):

    # If defined directly
    db_string = getattr(settings, 'CUCKOO_DATABASE_STRING', None)
    # Else use the settings default databse settings 
    if not db_string:
        env = deepcopy(settings.DATABASES['default'])
        if not exists:
            env['NAME'] = 'postgres'
        if dba or not exists:
            env['USER'] = 'dba'
        db_string = 'psql --set ON_ERROR_STOP=1 %(NAME)s -U %(USER)s -h %(HOST)s' % env
        if env.get('PORT', None):
            db_string += ' -p %(PORT)s' % env
        db_string = db_string + ' -f %s'

    cmd = db_string  % patch_file
    print cmd
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    if p.returncode != 0 or re.search('ERROR', err):
        raise CuckooError(err)
    return out



def get_patches(directory):
    """Return a list of all patches on disk"""
    if directory is None:
        try:
            directory = settings.CUCKOO_DIRECTORY
        except:
            directory = 'sql-patches'
    patches = []
    if not os.path.exists(directory):
        print "There is no patches directory: looking for a directory called '%s'.\n  note: see 'CUCKOO_DIRECTORY'" % directory
        sys.exit(1)
    for f in sorted(filter(lambda p: p.endswith('.sql'), os.listdir(directory))):
        sql = open(os.path.join(directory, f)).read()
        patches.append((f, sql))
    return patches

def run(stream=sys.stdout, directory=None, quiet=False, execute=True, dba=False):
    """Run patches that have not yet been run"""
    patches = get_patches(directory)

    for patch, sql in patches:
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            if execute:
                p.execute(quiet, dba)
            elif not quiet:
                print '[CUCKOO] Would have run patch %s' % p.patch
                
def dryrun(stream=sys.stdout, directory=None):
    """Call run, without executing the patches"""
    run(directory, execute=False)

def force(stream=sys.stdout, directory=None, quiet=False, dba=False):
    """Run all patches, even if they are already in the database"""
    patches = get_patches(directory)
    for patch, sql in patches:
        try:
            p = Patch.objects.get(patch=patch)
            p.sql = sql
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql, output='')
        p.execute(quiet, dba)


def fake(stream=sys.stdout, directory=None, quiet=False):
    """Add all patches to the database so that they are not run subsequently"""
    patches = get_patches(directory)
    for patch, sql in patches:
        try:
            p = Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql, output='')
            p.save()
            print '[CUCKOO] Fake-run patch %s' % p.patch

def status(stream=sys.stdout, directory=None):
    """Display the current state."""
    print "[CUCKOO] The following patches have been run on the system"
    patches = get_patches(directory)
    for patch, sql in patches:
        try:
            p = Patch.objects.get(patch=patch)
            print "%25s     %s" % (p.last_modified.strftime('%H:%M, %d %h, %Y'), p.patch)
        except Patch.DoesNotExist:
            print "%25s     %s" % ('Not yet run', patch)

    
def clean(stream=sys.stdout):
    """Remove all patches from the database"""
    for p in Patch.objects.all():
        p.delete()
    print '[CUCKOO] Removed all patches from the database'
    

def refresh(stream=sys.stdout, dumpfile=None, create=False, quiet=False, yes=None):
    """Apply a dump file, dropping and creating database."""
    if not dumpfile or not os.path.exists(dumpfile):
        raise CuckooError('You must provide a valid dump file: %s' % dumpfile)

    connection.close()
    env = settings.DATABASES['default']
    dropcmd = ('dropdb   %(NAME)s -U %(USER)s -h %(HOST)s -e' + ('' if yes else 'i')) % env
    if env.get('PORT', None):
        dropcmd += ' -p %(PORT)s ' % env
    call(dropcmd, shell=True)
    if create:
        print '[CUCKOO] Creating database.'
        createcmd = 'createdb -U dba %(NAME)s -O %(USER)s -h %(HOST)s -e'  % env
        if env.get('PORT', None):
            createcmd += ' -p %(PORT)s ' % env
        call(createcmd, shell=True)
    print '[CUCKOO] Applying dump file: %s' % dumpfile
    try:
        output = _execute_file(dumpfile, exists=create, dba=True)
        if not quiet:
            print output
    except Exception as e:
        print CuckooError("[CUCKOO] Error while executing dump file %s\n %s" % (dumpfile, e))
