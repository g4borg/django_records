from abc import ABC
from typing import Any, Callable

class Adjunct(ABC):
    """
    Baseclass that defines the Adjunct interface.

    Any Adjunct data which does not translate into SQL, but rather adds data programmatically.

    Adjuncts are filtered by records() and act as mutators of the retrieved database value
    before creating the target record. 
    They can also provide a key to be included into the .values() call.
    """
    __slots__ = ['value']

    skip = False  # if skip is true, this adjunct will not be actually processed.
    resolves_field = True  # if resolves_field is true, this adjunct will be called for a single field with resolve()
    post_processing = False  # if post_processing is true, this adjunct will in the end be called with dbdata, and be able to manipulate the whole dictionary.

    def resolve(self, model, dbdata) -> Any | None:
        """
        resolve returns the field value for one entry.
        """
        raise NotImplementedError

    def post_process(self, model, dbdata) -> dict | None:
        """if you have post_processing on True, this needs to be implemented.
        has to return either a new dictionary to use in initialization of an object, or None.
        """
        raise NotImplementedError

    def values_field(self) -> str | tuple[str, str] | None:
        """
        return a field for the values operator.

        if you return None, it will not be added. (default)
        if you return a string, it will be added to values as args.
        if you return a tuple, it will be added to values as kwargs (key, value).
        """
        return


class FixedValue(Adjunct):
    """always resolves to a fixed value."""

    def __init__(self, value=None):
        self.value = value

    def resolve(self, model, dbdata):
        return self.value


class MutValue(Adjunct):
    """adjunct value that returns a field value with a callback.
        currently supports only 1 parameter (dbdata).
    """

    def __init__(self, callback):
        self.callback = callback if callable(callback) else None

    def resolve(self, model, dbdata):
        # at this point i could check if callback needs 0-2 arguments and decide the call.
        if self.callback:
            return self.callback(dbdata)

class MutValueNotNone(MutValue):
    """MutValue that only calls the callback if the dbdata is not None
    (convenience function)
    """
    def resolve(self, model, dbdata):
        if dbdata is not None:
            return super().resolve(model, dbdata)


class Ref(Adjunct):
    """
    Adds this key to the .values() call, and processes it with an adjunct or callback.

    If no adjunct is defined, it simply redirects the value as-is.

    -> key can be a tuple of (keyname, expression) for annotations. # TODO: test this bold claim.
    """
    __slots__ = ['adjunct', 'key']

    def __init__(self, key, adjunct: Adjunct | Callable | None = None):
        match adjunct:
            case Adjunct(adj): self.adjunct = adjunct
            case callback if callable(callback): self.adjunct = MutValueNotNone(callback)
            case _: self.adjunct = None
        self.key = key

    def resolve(self, model, dbdata):
        value = dbdata.get(self.key)
        if self.adjunct:
            return self.adjunct.resolve(model, value)
        else:
            return value

    def values_field(self):
        return self.key


class Skip(Adjunct):
    """Skips this key from being retrieved from the database or used in the dataclass instantiation."""

    skip = True
    resolves_field = False


class PostProcess(Adjunct):
    """calls a callback which can modify the whole initialization dictionary."""
    __slots__ = ['callback']

    resolves_field = False
    post_processing = True

    def __init__(self, callback):
        self.callback = callback

    def post_process(self, model, dbdata):
        if self.callback:
            return self.callback(dbdata)
