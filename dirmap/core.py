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
        self._sorted = False
        if input_ is not None:
            self.add_many(input_)

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
            assert_clean(name, path)
        self._entries.append((src, dst))
        self._sorted = False

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
        return self._entries[i]

    def __len__(self):
        return len(self._entries)

    def __call__(self, path):

        if not self._sorted:
            self._entries.sort(key=lambda (src, dst): (-len(src), src, dst))
            self._sorted = True

        for src, dst in self._entries:

            if not path.startswith(src):
                continue

            if len(src) == len(path):
                return dst

            if path[len(src)] == os.path.sep:
                rel_path = path[len(src):]
                return dst + rel_path


    def get(self, path):
        res = self(path) or path
        return res

