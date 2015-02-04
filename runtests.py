# Set up for testing apps independently.
#
# See: docs.djangoprojects.com/en/1.7/topics/testing/advanced

import os
import sys
import django

from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()

def run_tests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    tests_to_run = []
    for test_name in sys.argv[1:]:
        tests_to_run.append('tests.tests.' + test_name)

    failures = test_runner.run_tests(tests_to_run)
    sys.exit(bool(failures))


if __name__ == '__main__':
    setup_django()
    run_tests()
