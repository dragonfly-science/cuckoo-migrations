import os
import os.path
import sys
from StringIO import StringIO

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
from django.test.utils import setup_test_environment
setup_test_environment()

from django.conf import settings
from django.db import models
from django.utils import unittest

from cuckoo.models import Patch, get_patches, run, fake, force, clean, dryrun
from species.models import Species

#class Species(models.Model):
#    common_name = models.CharField(max_length=50)
#    genus = models.CharField(max_length=50)
#    species = models.CharField(max_length=50)

class Run(unittest.TestCase):
    def setUp(self):
        """Reset the databases before each test"""
        Patch.objects.all().delete()
        Species.objects.all().delete()

    def test_run(self):
        """Test that running cuckoo runs patches"""
        p = Patch.objects.all()
        run()
        self.assertEqual(len(Patch.objects.all()), 2)
    
    def test_patch_executed(self):
        """Test the correct data has been inserted"""
        run()
        s = Species.objects.get(common_name = 'Shining bronze cuckoo')
        self.assertEqual(s.genus, 'Chrysococcyx') 

    def test_run_twice(self):
        """Test that running cuckoo twice only executes the patches once"""
        run()
        run()
        p = Patch.objects.all()
        self.assertEqual(len(p), 2)
    
    def test_run_twice_times(self):
        """Test that running cuckoo twice doesn't change the times"""
        run()
        self.assertEqual(len(Patch.objects.all()), 2)
        t1 = [x.last_modified for x in Patch.objects.all()]
        run()
        t2 = [x.last_modified for x in Patch.objects.all()]
        for i in range(len(t1)):
            self.assertEqual(t1[i], t2[i]) #Running twice didn't change the last_modified times
    
    def test_patches_run_in_list_order(self):
        """Test the patches are run in list order"""
        run()
        s = Species.objects.all()
        self.assertEqual(s[0].genus, 'Chrysococcyx') 
        self.assertEqual(s[1].genus, 'Eudynamys')

class Fake(unittest.TestCase):
    def setUp(self):
        """Reset the databases before each test"""
        Patch.objects.all().delete()
        Species.objects.all().delete()
    
    def test_fake(self):
        """Test that running 'fake' creates new patches, but doesn't execute them"""
        self.assertEqual(len(Patch.objects.all()), 0)
        fake()
        self.assertEqual(len(Patch.objects.all()), 2) #Two patches created
        self.assertEqual(len(Species.objects.all()), 0) #No species created
        
    def test_fake_times(self):
        """Test that running 'fake' does nothing if teh patches have already been run"""
        run()
        self.assertEqual(len(Patch.objects.all()), 2)
        t1 = [x.last_modified for x in Patch.objects.all()]
        fake()
        t2 = [x.last_modified for x in Patch.objects.all()]
        for i in range(len(t1)):
            self.assertEqual(t1[i], t2[i]) #Running fake didn't change the last_modified times

class Force(unittest.TestCase):
    def setUp(self):
        """Reset the databases before each test"""
        Patch.objects.all().delete()
        Species.objects.all().delete()
    
    def test_force(self):
        """Running force executes the patches even though they are in the database"""
        # First run once
        run()
        self.assertEqual(len(Species.objects.all()), 2)
        t1 = [x.last_modified for x in Patch.objects.all()]
        # Now remove records from the species database
        Species.objects.all().delete()
        # Now forcibly run again
        force()
        self.assertEqual(len(Species.objects.all()), 2)
        t2 = [x.last_modified for x in Patch.objects.all()]
        for i in range(len(t1)):
            self.assertNotEqual(t1[i], t2[i]) #Running force changed the modification times


class Directory(unittest.TestCase):
    """Check that the directory mechanism works as expected"""
    def setUp(self):
        """Reset the databases before each test and set path to patches"""
        Patch.objects.all().delete()
        Species.objects.all().delete()
        settings.CUCKOO_DIRECTORY = 'test_patches'

    def test_settings_directory(self):
        run()
        p = Species.objects.get(genus = 'Eudynamys')
        self.assertEqual(p.species, 'orientalis')

    def test_argument_directory(self):
        run(directory = 'sql-patches')
        p = Species.objects.get(genus = 'Eudynamys')
        self.assertEqual(p.species, 'taitensis')

    def test_two_directories(self):
        """Patches with the same name should only be run once"""
        run() #Use value from settings
        run(directory = 'sql-patches')
        p = Species.objects.filter(genus = 'Eudynamys')
        self.assertEqual(len(p), 2)

class Clean(unittest.TestCase):
    def setUp(self):
        """Reset the databases before each test and set path to patches"""
        Patch.objects.all().delete()
        Species.objects.all().delete()

    def test_remove_all_patches(self):
        """'clean' removes all patch records from the database"""
        p = Patch.objects.all()
        run()
        self.assertEqual(len(Patch.objects.all()), 2)
        clean()
        self.assertEqual(len(Patch.objects.all()), 0)

