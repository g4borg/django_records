from django.db import models
from django_records.records import RecordManager

class Celestial(models.Model):
    CELESTIAL_TYPES = ((0, 'Unknown'),
                       (1, 'Star'),
                       (2, 'Planet'),
                       (3, 'Planetoid'),
                       (4, 'Asteroid'),
                       (5, 'Station'))
    orbits = models.ForeignKey('self', blank=True, null=True, related_name='orbitals', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    celestial_type = models.IntegerField(choices=CELESTIAL_TYPES, default=int)
    weight = models.FloatField(default=float)
    size = models.FloatField(default=float)
    
    objects = RecordManager()
    
    @property
    def is_moon(self):
        return 5 > self.celestial_type > 1 and self.orbits and 5 > self.orbits.celestial_type > 1

class Spaceport(models.Model):
    name = models.CharField(max_length=100)
    celestial = models.ForeignKey(Celestial, related_name='spaceports', on_delete=models.CASCADE)
    
    objects = RecordManager()

class Person(models.Model):
    origin = models.ForeignKey(Celestial, related_name='children', blank=True, null=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    
    objects = RecordManager()

class Visitor(models.Model):
    person = models.ForeignKey(Person, related_name='as_visitor', on_delete=models.CASCADE)
    spaceport = models.ForeignKey(Spaceport, related_name='visitors', on_delete=models.CASCADE)
    luggage_weight = models.FloatField(blank=True, null=True, default=float)
    
    objects = RecordManager()

class Citizen(models.Model):
    planet = models.ForeignKey(Celestial, related_name='citizens', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, related_name='citizenships', on_delete=models.CASCADE)
    clearance_level = models.IntegerField(blank=True, null=True)

    objects = RecordManager()

