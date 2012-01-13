import os

from django.db import models, connection, transaction, DatabaseError
from django.conf import settings
import sqlparse

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

def get_patches():
    """Return a list of all patches on disk"""
    patches = []
    for f in os.listdir(settings.CUCKOO_DIRECTORY): 
        if f.endswith('.sql'):
            sql = open(os.path.join(settings.CUCKOO_DIRECTORY, f)).read()
            patches.append((f, sql))
    return patches

def run():
    """Run patches that have not yet been run"""
    patches = get_patches()
    for patch, sql in patches:
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            p.execute()
        
def force():
    """Run all patches, even if they are already in the database"""
    patches = get_patches()
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.execute()

def fake():
    """Add all patches to the database so that they are not run subsequently"""
    patches = get_patches()
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.save()

def tidy():
    """Remove any patches from the database that are not on disk"""
    patches = get_patches()
    saved = Patch.objects.all()
    for s in saved:
        if s.patch not in patches:
            s.delete()
    
