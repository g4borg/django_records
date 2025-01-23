from django.apps import AppConfig

# Only include tests in your INSTALLED_APPS if you want to test against django models.

class CommonTestsConfig(AppConfig):
    name = 'tests.celestials'
    label = 'celestials_tests'
