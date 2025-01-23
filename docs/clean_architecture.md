# Clean Architecture

If you look at the records() function, and ask yourself, why one would even define this abstraction, I want to explain in this document a bit the background to it.

In some architectural patterns, you work with so called "Entities", which are supposed to hold simple and plain objects (value objects), without any attached functionality, often represented as structs, or "DTO"s so data-transfer objects, which are also supposed to be pure.

The idea is, to reduce side effects, by always handling data in the layer independently, and also make the code portable, so that you could exchange the database engine behind it.

> As many well versed architectural experts note at this point in time, is, that in reality, this is a very abstract thought, as exchanging your ORM Framework for example is even more unlikely, than exchanging your database engine once you are in production, which is I think the main category of thought Django programmers usually follow - especially since changing Database with django becomes a configuration question. But let's put this aside.

Let's assume, achieving such layers is your goal, and you agree that the business layer of your application becomes "django independent", and you only want to see plain python objects there.

In such cases, you would most likely create repository facades, because in Django, the Repository is carried around on the model instance as the `objects` keyword by default, and is called a `Manager` (and managers cannot be used independently)

In these facades, you would do your querysets, but in the end produce custom objects through factories, but since the model instance itself should not leak, you would transform model data into some readonly structure.

But the overhead of creating a model instance in this case would become a hassle, so you would probably opt to retrieve instead dictionaries with `values()`, and feed those into dataclasses or pydantic objects instead.

This is where `records()` tries to chime in. It will take over the values() call, and produce your plain objects directly, and you can even modify it's data sources, so that it can even instantiate it as purely readonly object.

## But why?

Especially in refactoring, but also in creating new code, what you can do now, is simply using your models, as long as they are very similar to your dataclasses, and move your querysets into a facade, maybe even as a separate refactoring step, and for now, use standard querysets and return django models.

Once you are ready to isolate the code even further, all you will have to do, is add `records()` into your queryset calls in the facade.

## Where the semi-active record pattern of Django will influence this

Your new repository facade probably has to give you a save(), create(), update(), delete() and refresh_from_db() alternative for your entities (well refresh might be just getting the object again, and the mutators might even go DDD style into a separate facade...)

> I am not advocating, that you should use django like this, but if you do, django-records was designed to help out.

As with most of the non active record pattern libraries, you will quickly see, that using entities often changes save() calls to update() calls.

## Some benefits

For one, as long as data transfer objects have similar fields, transforming them becomes easy. you can also very simply reduce calls to only use the fields of your dataclass.

Additionally, as `records()` itself produces an Iterator, any function like `first()` or `last()` are supported.
