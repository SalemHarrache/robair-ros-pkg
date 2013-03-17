#!/usr/bin/env python
import roslib

roslib.load_manifest('robair_app')

import unittest


## A sample python unit test
class TestBareBones(unittest.TestCase):
    def test_one_equals_one(self):
        self.assertEquals(1, 1, "1!=1")


if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('robair_app', 'test_bare_bones', TestBareBones)
