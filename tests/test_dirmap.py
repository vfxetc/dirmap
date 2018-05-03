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

        self.assertRaises(ValueError, map_.add_existing, [src1]) # Just one.
        self.assertRaises(ValueError, map_.add_existing, [src1], dst) # Wrong API use.
        self.assertRaises(ValueError, map_.add_existing, [src1, src2]) # Nothing exists.
        self.assertRaises(ValueError, map_.add_existing, [src1, dst + '/..']) # Unclean.

    def test_deep_apply(self):

        map_ = DirMap({'/src': '/dst'})

        # Basics
        x = map_.deep_apply({
            '/src/key': ['/src/listitem'],
            'tuple': ('/src/tupleitem', ),
            'set': set(['/src/setitem']),
        })
        self.assertEqual(x, {
            '/src/key': ['/dst/listitem'],
            'tuple': ('/dst/tupleitem', ),
            'set': set(['/dst/setitem']),
        })

        # Include dict keys.
        x = map_.deep_apply({'/src': '/src'}, dict_keys=True)
        self.assertEqual(x, {'/dst': '/dst'})

        # Dict recursion
        a = {}
        a['/src'] = a
        b = map_.deep_apply(a, dict_keys=True)
        self.assertEqual(b.keys(), ['/dst'])
        self.assertIs(b['/dst'], b)

        # List recursion
        a = ['/src']
        a.append(a)
        b = map_.deep_apply(a)
        self.assertEqual(b[0], '/dst')
        self.assertIs(b[1], b)

