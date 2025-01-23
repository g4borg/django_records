from . import models
import factory
import factory.fuzzy


class CelestialFactory(factory.django.DjangoModelFactory):
    orbits = factory.LazyAttribute(lambda c: CelestialFactory(celestial_type=c.celestial_type - 1) if c.celestial_type and c.celestial_type > 1 else None)
    name = factory.Faker('city')
    # 1 sun, 7 planets, 3 moons, 4 asteroids, 5 stations
    celestial_type = factory.Iterator([1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5])
    weight = factory.fuzzy.FuzzyFloat(100.0, 100000.0)
    size = factory.fuzzy.FuzzyFloat(1.0, 8.0)
    
    class Meta:
        model = models.Celestial

class PersonFactory(factory.DjangoModelFactory):
    origin = factory.SubFactory(CelestialFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    age = factory.fuzzy.FuzzyInteger(9, 79)
    
    class Meta:
        model = models.Person

class SpaceportFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda sp: f'Port {sp.celestial.name}')
    celestial = factory.SubFactory(CelestialFactory, celestial_type=factory.Iterator([2,2,3,4,5]))
    
    class Meta:
        model = models.Spaceport

class VisitorFactory(factory.DjangoModelFactory):
    person = factory.SubFactory(PersonFactory)
    spaceport = factory.SubFactory(SpaceportFactory)
    luggage_weight = factory.fuzzy.FuzzyFloat(1.0, 100.0)
    
    class Meta:
        model = models.Visitor

class CitizenFactory(factory.DjangoModelFactory):
    planet = factory.SubFactory(CelestialFactory, celestial_type=2)
    person = factory.SubFactory(PersonFactory, origin=factory.SelfAttribute('planet'))
    clearance_level = factory.fuzzy.FuzzyInteger(0, 4)
    class Meta:
        model = models.Citizen

