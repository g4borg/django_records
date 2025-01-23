# Django Records

Django Records aims to provide a queryset extension facility, that allows to directly create structured data from querysets, other than Model Instances.

An example is to create dataclass instances as entities for a clean architecture setup, where model instances should not persist in the business layer and are just readonly representations of the fetched data, especially if you plan e.g. to use django-agnostic repository facades.

Main target is support of dataclass and pydantic, and allow building readonly representations of the data.

A more in-depth explanation, why you would use this module is described [in the documentation](./docs/clean_architecture.md)

Project Home:

- https://git.g4b.org/g4borg/django_records
- https://github.com/g4borg/django_records (copy)

## How to install

- First you have to add django_records to your projects' requirements (TODO: update this once packaged)
- For any model you want to be able to use records() on, you have to override the default Manager by creating it from the RecordQuerySet
- Mixins are available
- I suggest to study the code in records.py, as it is not much
- TODO: More in depth and less painful installation instructions.

## The .records() queryset function

> Changed since 0.3: records is not supposed take an optional first parameter as record target, instead use record_into(), however support for it is kept.

`records()` fetches data from the database with a values() call, and uses that to directly create a dataclass, or any other such structure ("a record").
It completely skips instantiation of a django model instance, and comes with tools to make it easy to handle initialization data, so that you can automate even production of immutable or nested data structures (called `Adjunct`), that work similar to tools like `Q()` or `F()`.

Out of the box, records assumes, you want to use `dataclasses.dataclass` or a `pydantic.BaseModel`.

Usage:

```python
    SomeModel.objects.filter(...).records('field1', 'field2', annotation=F(...), adjunct=Adjunct(...))
```

## Defining target default structure or a custom one with .record_into()

> Unstable: record_into() might be renamed.

- You can define the target class you want to create directly on the Queryset Manager (or Queryset)

  ```python
  @dataclass
  class Entity:
      id: int

  MyManager = BaseManager.from_queryset(RecordQuerySet)
  MyManager._default_record = Entity

  ...
  ```

- You can add it to your model (I have not found a standard way to expand Meta yet)

```python
class MyModel(models.Model):
    _default_record = Entity
```

- You could also add the `Handler` directly as `_default_record`, otherwise if you want to use another Handler than the default dataclasses handler, you can define `_record_handler` on the Queryset

- Finally you can override this behaviour by explicitly chaining the target class into the queryset with `record_into()`, which takes either a `RecordHandler` object, or any type of class that can be wrapped by one.

```python
    SomeModel.objects.filter(...).record_into(TargetDataClass).records('field1', 'field2')
```

## Adjuncts

Just like Django Expressions can be used to annotate keys in the model that are retrieved, so can Adjuncts be used to circumvent this mechanic, and insert local data into your target class. You might want to use this, if e.g. the dataclass you create is _immutable_, or the dataclass you use has _required fields_, that need data when you create the class, but the data is not part of your database query.

> Adjuncts do not influence the underlying SQL, except being able to add keys to the values() call.

> The keys used in the kwargs to records() primarily represent the keys passed to the dataclass.

- `FixedValue` simply carries some data and inserts it into every model. e.g. `.records(data=FixedValue(1))` will set the field `data` always to 1.
- `MutValue` allows to use a callable as argument, which gets called when setting the field on the model. e.g. `.records(data=MutValue(lambda entry: 'x' in entry))`
- `MutValueNotNone` same as `MutValue` but only applies the callable if the database value is not None (shortcut).
- `Ref` uses a different key to retrieve the data from values, and may apply an Adjunct to it. This probably is the most used Adjunct in real life examples.
- `Skip` allows you to skip a field. This is needed, as records() would include all fields on a dataclass, without knowing if it is optional, and helpful if you rewrite the fields with a PostProcess.
- `PostProcess` allows you to call a function as a callback at creation - if the callback returns anything else than None, it is used as initializer for the production of the object.

## Testing & Developing

### Install prerequisites

If you have `just` installed, you can use

`just install`

to install uv, python, and build a virtual env.

> Note: Windows users should install uv manually first.

### Built-In Tests

`just test` should run the unit tests.

### Integration Test: Examples Project

The [celestial project](examples/celestials/README.md) in examples serves to demonstrate basic usage of records, as well as providing integration testing.
