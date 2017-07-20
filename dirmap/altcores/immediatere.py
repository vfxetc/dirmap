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
                self.auto_add(spec, _setup=False)
            else:
                self.add(*spec, _setup=False)

        self._setup()

    def add(self, src, dst, _setup=True):

        for name, path in ("Source", src), ("Destination", dst):
            assert_clean(name, path)

        pattern = re.compile(r'^(?:{})({}.*)?$'.format(re.escape(src), re.escape(os.path.sep)))
        self._entries.append(DirMapEntry(src, dst, pattern))

        if _setup:
            self._setup()

    def auto_add(self, paths, *args, **kwargs):
        
        _setup = kwargs.pop('_setup', True)
        if kwargs:
            raise ValueError("Too many kwargs.", kwargs)

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
            self.add(src, dst, _setup=False)
        
        if _setup:
            self._setup()

    def _setup(self):
        self._entries.sort(key=lambda e: (-len(e.src), e.src, e.dst))

    def __getitem__(self, i):
        return self._entries[i]

    def __len__(self):
        return len(self._entries)

    def __call__(self, path):
        #assert_clean('Path', path)
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
        return res

