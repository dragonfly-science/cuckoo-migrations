import os.path

from django.test.utils import setup_test_environment
from django.utils import unittest

from cuckoo.models import Patch, get_patches, run, fake, force, tidy

class PatchTestCase(unittest.TestCase):
    def test_run(self):
        run()
        p = Patch.objects.all()
        self.assertEqual(len(p), 2)

if __name__ == '__main__':
    setup_test_environment()
    unittest.main()


