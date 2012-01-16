import os.path

from django.db import models
from django.test.utils import setup_test_environment
from django.utils import unittest

from cuckoo.models import Patch, get_patches, run, fake, force, tidy

class Species(models.Model):
    common_name = models.CharField(max_length=50)
    genus = models.CharField(max_length=50)
    species = models.CharField(max_length=50)

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
        self.assertEqual(s[1].genus, 'Eudynamis')

class Fake(unittest.TestCase):
    def setUp(self):
        """Reset the databases before each test"""
        Patch.objects.all().delete()
        Species.objects.all().delete()
    
    def test_fake(self):
        """Test that running 'fake' creates patches, but doesn't execute them"""
        self.assertEqual(len(Patch.objects.all()), 0)
        fake()
        self.assertEqual(len(Patch.objects.all()), 2) #Two patches created
        self.assertEqual(len(Species.objects.all()), 0) #No species created
        
    def test_fake_times(self):
        """Test that running 'fake' doesn't change the times"""
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
    
if __name__ == '__main__':
    setup_test_environment()
    unittest.main()


