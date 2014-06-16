import os,re
from copy import deepcopy
import sys
from subprocess import Popen, PIPE, STDOUT, call, check_call

from django.db import models, connection
from django.conf import settings
from django.core.management.base import CommandError

from .shells import get_db_shell_cmd


class CuckooError(CommandError):
    pass


class Patch(models.Model):
    """Class to hold information on patches that have been run"""
    patch = models.TextField(unique=True)
    sql = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)
    output = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def execute(self, quiet=False, dba=False, directory=None):
        """ Apply a patch """
        if directory is None:
            directory = getattr(settings, 'CUCKOO_DIRECTORY', 'sql-patches')
        cuckoo_db_name = getattr(settings, 'CUCKOO_DB', 'default')
        patch_file = os.path.join(directory, self.patch)
        try:
            self.output = _execute_file(cuckoo_db_name, patch_file, dba=dba)
            self.save()
            if not quiet:
                print '[CUCKOO] Ran patch %s' % self.patch
        except Exception as e:
            raise CuckooError("[CUCKOO] Error while executing patch %s\n %s" % (self.patch, e))


def _execute_file(db_name, patch_file, exists=True, dba=False):
    """Run a migration"""
    shell_cmd = get_db_shell_cmd(db_name, exists, dba)
    shell_cmd = shell_cmd + ' -f %s' % patch_file

    p = Popen(shell_cmd, shell=True, stdout=PIPE, stderr=PIPE)
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
    """ Run patches that have not yet been run """
    patches = get_patches(directory)

    for patch, sql in patches:
        try:
            Patch.objects.get(patch=patch)
        except Patch.DoesNotExist:
            p = Patch(patch=patch, sql=sql)
            if execute:
                p.execute(quiet, dba, directory)
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


def database_exists(database):
    cmd = 'psql -ltA -U dba'
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return database in [r.split('|')[0] for r in out.split('\n')]


def checked_call(cmd, errormsg):
    if call(cmd, shell=True) != 0:
        raise CuckooError(errormsg)


def refresh(stream=sys.stdout, dumpfile=None, create=False, quiet=False, yes=None, pgformat=False):
    """Apply a dump file, dropping and creating database."""
    if not dumpfile or not os.path.exists(dumpfile):
        raise CuckooError('You must provide a valid dump file: %s' % dumpfile)

    connection.close()
    cuckoo_db_name = getattr(settings, 'CUCKOO_DB', 'default')
    env = settings.DATABASES[cuckoo_db_name]
    dropcmd = get_db_shell_cmd(cuckoo_db_name, True, True, 'dropdb')
    if database_exists(env['NAME']):
        print '[CUCKOO] Dropping database.'
        checked_call(dropcmd, "could not drop database")
    if create:
        print '[CUCKOO] Creating database.'
        createcmd = get_db_shell_cmd(cuckoo_db_name, False, True, 'createdb')
        checked_call(createcmd, "Could not create database")
    print '[CUCKOO] Applying dump file: %s' % dumpfile
    try:
        if pgformat:
            restorecmd = get_db_shell_cmd(cuckoo_db_name, True, True, 'pg_restore -e -Fc -j 4')
            restorecmd += ' %s' % dumpfile
            checked_call(restorecmd, "could not restore database")
        else:
            output = _execute_file(cuckoo_db_name, dumpfile, exists=create, dba=True)
            if not quiet:
                print output
    except Exception as e:
        raise CuckooError("[CUCKOO] Error while executing dump file %s\n %s" % (dumpfile, e))


def create(stream=sys.stdout, drop=False, quiet=False, yes=True):

    cuckoo_db_name = getattr(settings, 'CUCKOO_DB', 'default')
    env = settings.DATABASES[cuckoo_db_name]
    exists = None
    try:
        exists = not bool(
            check_call(
                get_db_shell_cmd(cuckoo_db_name, exists, True)
                + " -lAt | grep -c '^%(NAME)s|' > /dev/null" % env, shell=True))
    except:
        exists = False
    if exists and drop:
        connection.close()
        dropcmd = get_db_shell_cmd(cuckoo_db_name, exists, True, 'dropdb')
        print '[CUCKOO] Dropped database %(NAME)s' % env
        checked_call(dropcmd, 'could not drop database')
        exists = False
    if not exists:
        createcmd = get_db_shell_cmd(cuckoo_db_name, False, True, 'createdb')
        checked_call(createcmd, 'could not create database')
        print '[CUCKOO] Created database %(NAME)s' % env
