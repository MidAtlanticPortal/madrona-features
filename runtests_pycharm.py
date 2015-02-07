"""Modified test runner to help run the test app with PyCharm's Unittest
run configuration.
"""

from django.test.utils import get_runner
import os
import django
from django.conf import settings

class EnvironmentSetterUpper:
    """Class that does django setup prior to running tests, and (hopefully)
    calls the test teardown.
    """
    def __init__(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
        django.setup()

        TestRunner = get_runner(settings)
        self.test_runner = TestRunner()

        self.test_runner.setup_test_environment()
        suite = self.test_runner.build_suite([], None)
        self.old_config = self.test_runner.setup_databases()

    def __del__(self):
        pass
        self.test_runner.teardown_databases(self.old_config)
        self.test_runner.teardown_test_environment()

setter_upper = EnvironmentSetterUpper()

from tests.tests import *

