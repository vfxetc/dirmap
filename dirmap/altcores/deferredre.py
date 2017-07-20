import collections
import os
import re


DirMapEntry = collections.namedtuple('DirMapEntry', 'src dst pattern')


def assert_clean(name, path):
    if not os.path.isabs(path):
        raise ValueError("{} must be absolute.".format(name), path)
    if not os.path.normpath(path) == path:
        raise ValueError("{} must be normalized.".format(name), path)


class DirMap(collections.Sequence):

    """Remaps directories from one layout to another.

    Useful for systematically translating paths from one environment to another
    in which volumes are mounted differenly, or directories otherwise moved.

    e.g.::

        >>> dirmap = DirMap({'/src': '/dst'})
        >>> dirmap('/src/something')
        '/dst/something'

    """

    def __init__(self, input_=None):
        self._entries = []
        self._to_setup = []
        if input_ is not None:
            self.add_many(input_)

    def _setup(self):
        if not self._to_setup:
            return
        for src, dst in self._to_setup:
            pattern = re.compile(r'^(?:{})({}.*)?$'.format(re.escape(src), re.escape(os.path.sep)))
            self._entries.append(DirMapEntry(src, dst, pattern))
        self._to_setup = []
        self._entries.sort(key=lambda e: (-len(e.src), e.src, e.dst))

    def add_many(self, input_):

        if isinstance(input_, basestring):
            to_add = []
            for chunk in input_.split(';'):

                if not chunk:
                    continue

                parts = chunk.split(',')
                if len(parts) > 1:
                    to_add.append(set(parts))
                    continue

                parts = chunk.split(':')
                if len(parts) != 2:
                    raise ValueError("More than one colon in chunk.", chunk)
                to_add.append(parts)

        elif isinstance(input_, dict):
            to_add = input_.items()

        else:
            to_add = input_

        for spec in to_add:
            if isinstance(spec, set):
                self.auto_add(spec)
            else:
                self.add(*spec)

    def add(self, src, dst):

        for name, path in ("Source", src), ("Destination", dst):
            if not os.path.isabs(dst):
                raise ValueError("{} must be absolute.".format(name), dst)
            if not os.path.normpath(dst) == dst:
                raise ValueError("{} must be normalized.".format(name), dst)

        self._to_setup.append((src, dst))

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
            self.add(src, dst)
    
    def __getitem__(self, i):
        self._setup()
        return self._entries[i]

    def __len__(self):
        self._setup()
        return len(self._entries)

    def __call__(self, path):
        #assert_clean('Path', path)
        self._setup()
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

