from unittest import TestCase
import os

from dirmap import DirMap


class TestDirMap(TestCase):

    def test_basics(self):

        map_ = DirMap([
            ('/src', '/dst'),
            ('/src/inner', '/dst2/inner'),
            ('/src3', '/dst3'),
        ])

        self.assertEqual(map_('/path/to/thing'), '/path/to/thing')

        self.assertEqual(map_('/src'), '/dst')
        self.assertEqual(map_('/src/inner'), '/dst2/inner')
        self.assertEqual(map_('/src3'), '/dst3')
        self.assertEqual(map_('/src/another'), '/dst/another')

    def test_empty(self):
        map_ = DirMap()
        self.assertEqual(len(map_), 0)
        self.assertEqual(map_('/path/to/thing'), '/path/to/thing')

    def test_add_existing(self):

        here = os.path.abspath(os.path.join(__file__, '..', '..'))

        src1 = os.path.join(here, 'doesnotexist1')
        src2 = os.path.join(here, 'doesnotexist2')
        dst = os.path.join(here, 'dirmap')

        map_ = DirMap()
        map_.add_existing((src1, dst, src2))

        self.assertEqual(map_(src1), dst)
        self.assertEqual(map_(src2), dst)

        self.assertRaises(ValueError, map_.add_existing, ['just one'])
        self.assertRaises(ValueError, map_.add_existing, ['list'], 'and args')
        self.assertRaises(ValueError, map_.add_existing, ['none', 'exist'])
