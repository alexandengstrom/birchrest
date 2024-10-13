import os
import unittest

os.environ['birchrest_log_level'] = 'test'

loader = unittest.TestLoader()
tests = loader.discover('.')
testRunner = unittest.TextTestRunner()
testRunner.run(tests)
