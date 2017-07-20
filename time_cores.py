from __future__ import print_function

import time

from dirmap.core import DirMap as Main
from dirmap.altcores.deferredre import DirMap as DeferredRe
from dirmap.altcores.dicttrie import DirMap as DictTrie
from dirmap.altcores.dictlookup import DirMap as DictLookup


specs = [
    ('/src', '/dst'),
    ('/Volumes/CGroot/Projects/SitG', '/Volumes/heap/sitg/work/film'),
    ('/Volumes/CGartifacts/Projects/SitG', '/Volumes/heap/sitg/work/film-artifacts'),
    ('/src/inner', '/dstouter'),
    ('/src with spaces', '/dst with spaces'),
]

srcs = [
    '/Volumes/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
    '/src',
    '/src/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
    '/notathing/CGroot/Projects/SitG/sequences/DR/shots/DR00/layout/maya/scenes/something.mb',
]


def go(cls, name=None):


    num = 4000

    start_time = time.time()
    
    for i in xrange(num):
        map_ = cls(specs)
        for src in srcs:
            x = map_(src)

    setup_dur = time.time() - start_time

    start_time = time.time()
    for i in xrange(num):
        for src in srcs:
            x = map_(src)
    apply_dur = time.time() - start_time

    setup_dur -= apply_dur

    print('{:11}: setup={:7d}ns apply={:5d}ns'.format(
        name or cls.__name__,
        int(1e9 * setup_dur / num),
        int(1e9 * apply_dur / num / len(srcs)),
    ))


for i in xrange(3):
    go(Main, 'Main')
    go(DeferredRe, 'DeferredRe')
    go(DictTrie, 'DictTrie')
    go(DictLookup, 'DictLookup')
    print()


