from dataclasses import dataclass
from unittest import mock, TestCase

from django.db.models import F

from . import handlers
from .adjuncts import MappedValue as Mut, FixedValue as Val, Skip, PostProcess, Ref
from .records import RecordIterable, RecordQuerySetMixin


@dataclass
class TestDataClass:
    id: int
    name: str
    age: int
    street: str
    parent: 'TestDataClass' = None


class TestRecords(TestCase):
    def test_records_basic(self):
        lam = lambda entry: entry.get('name')
        ref = lambda pk: f'referenced: {pk}'
        cb = lambda entry: {**entry, **{'new': 'field'}}

        MockedValues = mock.MagicMock()
        values_return = mock.MagicMock(return_value=[{'id': 1, 'name': 'Name', 'age': 18, 'street_id': 2, 'two': 'Two', 'one': 'One'}])
        MockedValues.return_value = values_return
        qs = RecordQuerySetMixin()
        qs.values = MockedValues

        result = qs.records(
            TestDataClass,
            'one',
            two=F('field'),
            full_name=Mut(lam),
            street=Ref('street_id', ref),
            ignored=None,
            fixed=Val(1),
            parent=Skip(),
            post_process=PostProcess(cb),
        )

        # what we expect in the values call is:
        expected_in_values = [
            'one',
            'two',
            'id',
            'name',
            'age',
            'street_id',
        ]
        not_expected_in_values = ['full_name', 'street', 'ignored', 'fixed', 'parent', 'post_process']
        args_list = list(MockedValues.call_args[0]) + list(MockedValues.call_args[1].keys())
        for exp in expected_in_values:
            self.assertIn(exp, args_list)
        for nex in not_expected_in_values:
            self.assertNotIn(nex, args_list)

        # check result having correct variables.
        self.assertIs(result._iterable_class, RecordIterable)
        self.assertIsInstance(result._record, handlers.RecordDataclass)
        self.assertIn('full_name', result._record_kwargs)
        self.assertIn('street', result._record_kwargs)
        self.assertIn('fixed', result._record_kwargs)
        self.assertIn('post_process', result._record_kwargs)
        self.assertNotIn('ignored', result._record_kwargs)
        # not expected: values() keywords in _record_kwargs.
        for nex in expected_in_values:
            self.assertNotIn(nex, result._record_kwargs)

    def test_records_iterator(self):
        root = TestDataClass(id=0, name="Root", age=0, street='', parent=None)

        def full_callback(data):
            data['parent'] = root
            return data

        class FakeQuerySet:
            class FakeQuery:
                extra_select = []
                values_select = ['id', 'name', 'street_id', 'one']
                annotation_select = []

                def get_compiler(self, db):
                    compiler = mock.MagicMock()
                    compiler.results_iter.return_value = [
                        [1, 'arthus', 12, 'One'],
                    ]
                    return compiler

            db = mock.MagicMock()
            model = mock.MagicMock()
            query = FakeQuery()
            _record = handlers.RecordDataclass.wrap(TestDataClass)
            _record_kwargs = {
                'street': Ref('street_id', lambda pk: f'Street {pk}'),
                'age': Val(18),
                'name': Mut(lambda entry: entry.get('name').capitalize()),
                'parent': PostProcess(full_callback),
            }

        iterable = RecordIterable(FakeQuerySet())
        entry = next(iter(iterable))
        self.assertEqual(entry.id, 1)
        self.assertEqual(entry.name, 'Arthus')
        self.assertEqual(entry.street, 'Street 12')
        self.assertEqual(entry.parent, root)

class AdjunctTests(TestCase):
    def test_ref_none(self):
        r = Ref('key', None)
        result = r.resolve(model=None, dbdata = {'key': 'Value'} )
        self.assertEqual(r.adjunct, None)
        self.assertEqual(result, "Value")