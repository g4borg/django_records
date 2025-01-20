"""
RecordHandlers describe how a Record class should be built.

Each Record Type should define one.

Usually you just want to use one of the pre-built Handlers for dataclass, dict, or pydantic.

"""
from .errors import RecordClassDefinitionError

class RecordHandler:
    """
    Handler for a record type

    defines how a record can be created, and how to retrieve all field names, and the required ones.
    """
    __slots__ = ['klass']

    @classmethod
    def wrap(cls, klass):
        """internal factory function used to wrap a non-record handler into a record handler"""
        return cls(klass)

    def __init__(self, klass):
        self.klass = klass

    def create(self, **kwargs):
        """the actual creation of the underlying record type instance"""
        return self.klass(**kwargs)

    def get_field_names(self):
        """should return all field names of the wrapped record type."""
        return self.klass.__dict__.keys()

    @property
    def record(self):
        """property used to retrieve the wrapped class."""
        return self.klass

    @property
    def required_arguments(self):
        """property used that can filter for required field names"""
        return self.get_field_names()


class RecordDict(RecordHandler):
    """RecordHandler that outputs a dictionary"""

    def __init__(self, klass=None):
        # it is not required to define dict, but you could do OrderedDict e.g.
        self.klass = klass or dict

    def get_field_names(self) -> list[str]:
        # dictionary has no required fields. any field is possible.
        return []


class RecordDataclass(RecordHandler):
    """handles dataclasses.dataclass derivatives"""

    def create(self, **kwargs):
        # clean field names to be only valid if they are on the dataclass.
        record_fields = self.get_field_names()
        kwargs = {k: v for k, v in kwargs.items() if k in record_fields}
        return self.klass(**kwargs)

    def get_field_names(self) -> list[str]:
        # returns all field names, even those which are not required.

        # for dataclasses:
        if hasattr(self.klass, '__dataclass_fields__'):
            return list(self.klass.__dataclass_fields__.keys())

        # for pydantic BaseModel:
        if hasattr(self.klass, '__fields__'):
            return list(self.klass.__fields__.keys())

        raise RecordClassDefinitionError("Field Names not found.")
