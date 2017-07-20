from __future__ import print_function

import time

from dirmap.core import DirMap as Main
from dirmap.altcores.deferredre import DirMap as DeferredRe
from dirmap.altcores.dicttrie import DirMap as DictTrie
from dirmap.altcores.dictlookup import DirMap as DictLookup
from dirmap.altcores.immediatere import DirMap as ImmediateRe


specs = [
    ('/src', '/dst'),
    ('/Volumes/CGroot/Projects/SitG', '/Volumes/heap/sitg/work/film'),
    ('/Volumes/CGartifacts/Projects/SitG', '/Volumes/heap/sitg/work/film-artifacts'),
    ('/src/inner', '/dstouter'),
    ('/src with spaces', '/dst with spaces'),
]

tests = [

    ('/Volumes/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
     '/Volumes/heap/sitg/work/film/sequences/DR/shots/DR00/layout/maya/scenes/something.mb'),

    ('/src',
     '/dst'),

    ('/src/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
     '/dst/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb'),

    ('/notathing/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
     '/notathing/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb'),

    ('/Volumes/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/publishes/maya_scene/something/v0001/something.mb',
     '/Volumes/heap/sitg/work/film/sequences/DR/shots/DR00/layout/publishes/maya_scene/something/v0001/something.mb'),

]


def go(cls, name=None):


    num = 1000

    start_time = time.time()
    
    for i in xrange(num):
        map_ = cls(specs)
        for src, dst in tests:
            x = map_(src)
            if x != dst:
                print('{}: {} -> {} != {}'.format(name, src, x, dst))
                exit()

    setup_dur = time.time() - start_time

    start_time = time.time()
    for i in xrange(num):
        for src, _ in tests:
            x = map_(src)
            x == dst
    apply_dur = time.time() - start_time

    setup_dur -= apply_dur

    print('{:11}: setup={:7d}ns apply={:5d}ns'.format(
        name or cls.__name__,
        int(1e9 * setup_dur / num),
        int(1e9 * apply_dur / num / len(tests)),
    ))


for i in xrange(3):
    go(Main, 'Main')
    go(ImmediateRe, 'ImmediateRe')
    go(DeferredRe, 'DeferredRe')
    go(DictTrie, 'DictTrie')
    go(DictLookup, 'DictLookup')
    print()


