from django.db import models, connection, transaction, DatabaseError
from settings import PATCH_DIRECTORY
import os

class Patch(models.Model):
    patch = models.TextField(unique=True)
    sql = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)
    output = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['id']

    def execute(self):
        cursor = connection.cursor()
        try:
            cursor.execute(self.sql)
            self.output = str(cursor.fetchall())
            self.save()
            transaction.commit()
        except:
            transaction.rollback()
            msg = "Error while executing the patch %s" % self.patch
            raise DatabaseError, msg

def get_patches():
    patches = []
    for f in os.listdir(PATCH_DIRECTORY): 
        if f.endswith('.sql'):
            sql = open(os.path.join(PATCH_DIRECTORY, f)).read()
            patches.append((f, sql))
    return patches

def run():
    patches = get_patches()
    for patch, sql in patches():
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            p.execute()
        
def run_all():
    patches = get_patches() # Read the patches off disk
    Patch.objects.all().delete() # Clear the database
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.execute()

def mark_all():
    patches = get_patches() # Read the patches off disk
    Patch.objects.all().delete() # Clear the database
    for patch, sql in patches:
        p = Patch(patch=patch, sql=sql, output='')
        p.save()
    
