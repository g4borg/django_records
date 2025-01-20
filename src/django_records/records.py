import logging

from django.db.models import QuerySet, Model
from django.db.models.expressions import BaseExpression, Combinable
from django.db.models.manager import Manager
from django.db.models.query import ValuesIterable

from .adjuncts import Adjunct
from .handlers import RecordDataclass, RecordHandler
from .errors import RecordClassDefinitionError, RecordInstanceError

logger = logging.getLogger(f"django_records.{__name__}")

class RecordIterable(ValuesIterable):
    """
    Iterable returned by records() that yields a record class for each row.
    Replaces the standard iterable of the queryset.
    """

    def __iter__(self):
        queryset: QuerySet = self.queryset
        model: Model = self.queryset.model
        query = queryset.query
        compiler = query.get_compiler(queryset.db)
        record_data = getattr(queryset, '_record_kwargs', {})
        record_handler = queryset._record

        # extra(select=...) cols are always at the start of the row.
        names = [
            *query.extra_select,
            *query.values_select,
            *query.annotation_select,
        ]
        indexes = range(len(names))

        for row in compiler.results_iter(chunked_fetch=self.chunked_fetch, chunk_size=self.chunk_size):
            dbdata = {names[i]: row[i] for i in indexes}

            # post-processors will be able to rewrite the whole dictionary.
            post_processors = []
            # we overwrite db data bluntly for now. actually we would provide callbacks the current dict.
            for k, v in record_data.items():
                if v.resolves_field:
                    dbdata[k] = v.resolve(model, dbdata)
                if v.post_processing:
                    post_processors.append(v)
            if post_processors:
                for processor in post_processors:
                    processed = processor.post_process(model, dbdata)
                    if processed is not None:
                        dbdata = processed
            try:
                record = record_handler.create(**dbdata)
            except Exception as e:
                raise RecordInstanceError("Error creating Record instance") from e
            
            yield record


class RecordQuerySetMixin:
    _record_handler = RecordDataclass

    def record_into(self, handler):
        self._record = handler
        return self

    def records(self, *args, **kwargs):
        """
        generates record objects

        Acts like values(), however:
            - if record type is not defined with record_into(), you have to define it on the queryset, or the model, with _default_record,
              otherwise it will raise a RuntimeError.
            - keyword arguments of type "Adjunct" are used as deferred values, and resolved independently.
            - values() is called with every required_argument on the dataclass not handled by an Adjunct
        """
        if len(args) and not isinstance(args[0], str):
            # we assume this is our dataclass
            handler = args[0]
            args = args[1:]
            # @deprecate: we might remove this
            logger.warning("Defining the target class in args might be soon deprecated: %s", handler)
        else:
            handler = getattr(self, '_record', getattr(self, '_default_record', getattr(self.model, '_default_record', None)))
        if not handler:
            raise RecordClassDefinitionError("Trying records() on a Queryset without destination class.")

        if not isinstance(handler, RecordHandler):
            handler = self._record_handler.wrap(handler)

        all_keys = [*args, *kwargs.keys()]
        unhandled_keys = list(set(handler.required_arguments) - set(all_keys))
        args = [*args, *unhandled_keys]

        # rebuild keyword arguments for values, by filtering out our adjuncts
        new_kw = {}
        adjuncts = {}
        for k, v in kwargs.items():
            if isinstance(v, Adjunct):
                # skip allows an adjunct to completely ignore a key.
                if not v.skip:
                    adjuncts[k] = v
                # check if we have to add to values. adjuncts can define a field to add here.
                add_to_values = v.values_field()
                if isinstance(add_to_values, str) and add_to_values not in args:
                    args.append(add_to_values)
                elif isinstance(add_to_values, tuple):
                    new_kw[add_to_values[0]] = add_to_values[1]
            elif isinstance(v, BaseExpression) or isinstance(v, Combinable) or hasattr(v, 'resolve_expression'):
                new_kw[k] = v
            elif v is None:
                # ignore None
                pass
            else:
                # this will fail in values() for now, but i do not want to hijack future django functionality here.
                # however it would be just funky if we actually replace this with new_kw[k] = Val(v).
                new_kw[k] = v

        # copy ourself with values() and save the results on the cloned queryset values produces.
        try:
            values = self.values(*args, **new_kw)
        except Exception as e:
            raise RecordInstanceError("Error with calculated values") from e
        values._iterable_class = RecordIterable
        values._record_kwargs = adjuncts
        values._record = handler
        return values


class RecordQuerySet(RecordQuerySetMixin, QuerySet):
    # overwrite cloning. I would love to have a way to inject this into django directly (or use model.Meta)
    def _clone(self):
        c = super()._clone()
        for key in ['_record', # saves the actual final handler until the iterator is consumed
                    '_record_kwargs', # saves the actual kwargs to records until the iterator is consumed
                    '_record_handler', # if the default handler to transform target classes, by default dataclasses
                    '_default_record', # the default target class for this particular model
                    ]:
            if hasattr(self, key):
                setattr(c, key, getattr(self, key))
        return c


# Alternative:
# class RecordManager(BaseManager.from_queryset(RecordQuerySet)):
#    pass


class RecordManager(RecordQuerySetMixin, Manager):
    def get_queryset(self):
        return RecordQuerySet(self.model, using=self._db)
