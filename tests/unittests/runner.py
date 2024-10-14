import os
import unittest
import sys

os.environ['birchrest_log_level'] = 'test'

loader = unittest.TestLoader()
tests = loader.discover('.')
testRunner = unittest.TextTestRunner()
result = testRunner.run(tests)

if not result.wasSuccessful():
    sys.exit(1)
