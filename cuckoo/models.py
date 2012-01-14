import os

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

    def execute(self):
        """Apply a patch"""
        cursor = connection.cursor()
        try:
            cursor.execute(self.sql)
            self.output = cursor.fetchall()
            self.save()
            transaction.commit()
        except:
            transaction.rollback()
            raise
            #msg = "Error while executing the patch %s" % self.patch
            #raise DatabaseError, msg

def get_patches(directory):
    """Return a list of all patches on disk"""
    if directory is None:
        directory = settings.CUCKOO_DIRECTORY
    patches = []
    for f in os.listdir(directory): 
        if f.endswith('.sql'):
            sql = open(os.path.join(directory, f)).read()
            patches.append((f, sql))
    return patches

def run(directory=None):
    """Run patches that have not yet been run"""
    patches = get_patches(directory)
    for patch, sql in patches:
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            p.execute()
        
def force(directory=None):
    """Run all patches, even if they are already in the database"""
    patches = get_patches(directory)
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.execute()

def fake(directory=None):
    """Add all patches to the database so that they are not run subsequently"""
    patches = get_patches(directory)
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.save()

def tidy(directory=None):
    """Remove any patches from the database that are not on disk"""
    patches = get_patches(directory)
    saved = Patch.objects.all()
    for s in saved:
        if s.patch not in patches:
            s.delete()
    
