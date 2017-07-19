import collections
import os
import re


DirMapEntry = collections.namedtuple('DirMapEntry', 'src dst pattern')


class DirMap(collections.Sequence):

    def __init__(self, input_=None):

        self._entries = []

        if isinstance(input_, basestring):
            input_ = [x.split(':', 1) for x in input_.split(';') if x]
        elif isinstance(input_, dict):
            input_ = input_.iteritems()
        elif input_ is None:
            return

        for src, dst in input_:
            self.add(src, dst, _sort=False)
        self._sort()

    def add(self, src, dst, _sort=True):

        for name, path in ("Source", src), ("Destination", dst):
            if not os.path.isabs(dst):
                raise ValueError("{} must be absolute.".format(name), dst)
            if not os.path.normpath(dst) == dst:
                raise ValueError("{} must be normalized.".format(name), dst)

        pattern = re.compile(r'^(?:{})({}.*)?$'.format(re.escape(src), re.escape(os.path.sep)))
        self._entries.append(DirMapEntry(src, dst, pattern))

        if _sort:
            self._sort()

    def auto_add(self, paths, *args):
        
        if isinstance(paths, basestring):
            paths = [paths]
            paths.extend(args)
        elif args:
            raise ValueError("Please provide an iterable or positional args, not both.")

        paths = list(paths)
        dsts = set(p for p in paths if os.path.exists(p))
        srcs = set(p for p in paths if p not in dsts)
        
        if len(dsts) != 1:
            raise ValueError("Not exactly one of given paths exists.", paths)
        dst = dsts.pop()
        
        for src in srcs:
            self.add(src, dst, _sort=False)
        self._sort()

    def _sort(self):
        self._entries.sort(key=lambda e: (-len(e.src), e.src, e.dst))

    def __getitem__(self, i):
        return self._entries[i]

    def __len__(self):
        return len(self._entries)

    def __call__(self, path):
        for entry in self._entries:
            m = entry.pattern.match(path)
            if m:
                rel_path = m.group(1)
                if rel_path:
                    return entry.dst + rel_path
                else:
                    return entry.dst

    def get(self, path):
        res = self(path) or path
        #print path, res
        return res

