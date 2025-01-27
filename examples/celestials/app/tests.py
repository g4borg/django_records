from dataclasses import dataclass
from unittest.case import skipIf
from unittest import mock

from django.db.models import F
from django.test.testcases import TestCase
from django.test.utils import tag

from django_records.adjuncts import MappedValue, FixedValue, PostProcess
from django_records.handlers import RecordDictHandler


try:
    from .models import Celestial
    from .galaxy import Stars
    celestials_installed = True
except RuntimeError:
    celestials_installed = False


@dataclass
class Entity:
    id: int


@dataclass
class SpaceRock:
    id: int
    name: str
    orbits_name: str
    is_moon: bool


@tag('library')
@skipIf(not celestials_installed, "Celestials Testpackage not installed into INSTALLED_APPS.")
class TestQueryBuilder(TestCase):

    def setUp(self):
        super().setUp()
        Stars.create_sol(context=self)

    def test_records(self):
        entities = Celestial.objects.filter(orbits__name='Sol', celestial_type__lte=4).records(Entity)
        self.assertEqual(len(entities), len(self.planets))

        # test whether we really return dataclass as result, even with first.
        self.assertIsInstance(entities.first(), Entity)

        # find moons. test whether i can use entities to do an SQL query. works because i have only one key.
        self.assertEqual(len(self.moons), Celestial.objects.filter(orbits__in=entities).count())

        # this is pretty much the same as
        self.assertEqual(len(self.moons), len(Celestial.objects.filter(
            orbits__in=Celestial.objects.filter(orbits__name='Sol', celestial_type__lte=4)).values_list('id', flat=True)))

    def test_handler_dict(self):
        entities = Celestial.objects.filter(orbits__name='Sol', celestial_type__lte=4).records(RecordDictHandler())
        self.assertEqual(len(entities), len(self.planets))
        self.assertIsInstance(entities.first(), dict)

    def test_MappedValue(self):

        # this tests whether our own celestial type or the celestial type of what we orbit is correct for being a moon. parameter is a dictionary.
        is_moon = lambda entry: True if 5 > (entry.get('celestial_type') or 0) > 1 and 5 > (entry.get('orbits_type') or 0) > 1 else False

        entities = Celestial.objects.records(SpaceRock,  # we want our output to be a SpaceRock dataclass.
                                    'celestial_type',  #  we include the key celestial_type into our query.
                                    id=FixedValue(None),  # we blank out id to test FixedValue working.
                                    orbits_name=F('orbits__name'),  # we set our custom orbits_name to a related field value
                                    orbits_type=F('orbits__celestial_type'),  # our MappedValue needs this data.
                                    is_moon=MappedValue(is_moon))  # MappedValue over result

        self.assertEqual(len(entities), len(self.celestials))

        for idx, entity in enumerate(entities):
            dbdata = self.celestials[idx]
            model = Celestial.objects.filter(id=dbdata.id).first()
            self.assertEqual(entity.name, dbdata.name)
            self.assertIsNone(entity.id)
            self.assertEqual(entity.is_moon, model.is_moon)

    def test_post_process(self):
        side_effect = lambda x:x
        post_process_one = mock.Mock(side_effect=side_effect)
        post_process_two = mock.Mock(side_effect=side_effect)

        entities = Celestial.objects.all().records(Entity, 
                                                   post_process_one=PostProcess(post_process_one), 
                                                   post_process_two=PostProcess(post_process_two))

        self.assertEqual(len(entities), len(self.celestials))
        self.assertEqual(post_process_one.call_count, len(self.celestials))
        self.assertEqual(post_process_two.call_count, len(self.celestials))
