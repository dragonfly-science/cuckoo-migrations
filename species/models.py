from django.db import models

class Species(models.Model):
    common_name = models.CharField(max_length=50)
    genus = models.CharField(max_length=50)
    species = models.CharField(max_length=50)

    def __str__(self):
        return 'Species: %s %s' % (self.genus, self.species)
