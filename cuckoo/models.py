import os
import sys

from django.db import models, connection, transaction, DatabaseError
try:
    from django.conf import settings
except ImportError:
    pass


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
        cursor = connection.cursor()
        with transaction.commit_on_success():
            try:
                cursor.execute(self.sql)
                self.output = cursor.fetchall()
                self.save()
                if not quiet:
                    print '[CUCKOO] Ran patch %s' % self.patch
            except:
                print "[CUCKOO] Error while executing patch %s" % self.patch
                raise


def get_patches(directory):
    """Return a list of all patches on disk"""
    if directory is None:
        try:
            directory = settings.CUCKOO_DIRECTORY
        except:
            directory = 'sql-patches'
    patches = []
    for f in os.listdir(directory): 
        if f.endswith('.sql'):
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

def clean(stream=sys.stdout):
    """Remove all patches from the database"""
    for p in Patch.objects.all():
        p.delete()
    print '[CUCKOO] Removed all patches from the database'
    
