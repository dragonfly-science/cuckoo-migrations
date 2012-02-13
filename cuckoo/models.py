import os
import sys
from subprocess import Popen, PIPE, STDOUT

from django.db import models, connection, transaction, DatabaseError
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

    def execute(self, quiet=False):
        """Apply a patch"""

        # There are two modes, either using connection object
        # or, if defined, a shell command
        database_string = getattr(settings, 'CUCKOO_DATABASE_STRING', None)
        if database_string:
            # apply the string directly...
            directory = getattr(settings, 'CUCKOO_DIRECTORY', 'sql-patches')
            patch_file = os.path.join(directory, self.patch)
            cmd = database_string % patch_file
            try:
                out, err = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE).communicate()
                self.output = out
                self.save()
                if err:
                    raise CuckooError(err)
                if not quiet:
                    print '[CUCKOO] Ran patch %s' % self.patch
            except Exception as e:
                print CuckooError("[CUCKOO] Error while executing patch %s\n %s" % (self.patch, e))
            return

        # Else run it using the connection object
        cursor = connection.cursor()
        with transaction.commit_on_success():
            try:
                cursor.execute(self.sql)
                self.output = cursor.fetchall()
                self.save()
                if not quiet:
                    print '[CUCKOO] Ran patch %s' % self.patch
            except Exception as e:
                print CuckooError("[CUCKOO] Error while executing patch %s\n %s" % (self.patch, e))


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

def run(stream=sys.stdout, directory=None, quiet=False, execute=True):
    """Run patches that have not yet been run"""
    patches = get_patches(directory)
    
    for patch, sql in patches:
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            if execute:
                p.execute(quiet)
            elif not quiet:
                print '[CUCKOO] Would have run patch %s' % p.patch
                
def dryrun(stream=sys.stdout, directory=None):
    """Call run, without executing the patches"""
    run(directory, execute=False)

def force(stream=sys.stdout, directory=None, quiet=False):
    """Run all patches, even if they are already in the database"""
    patches = get_patches(directory)
    for patch, sql in patches:
        try:
            p = Patch.objects.get(patch=patch)
            p.sql = sql
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql, output='')
        p.execute(quiet)


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
    
