import collections
import os


def assert_clean(name, path):
    if not os.path.isabs(path):
        raise ValueError("{} must be absolute.".format(name), path)
    if not os.path.normpath(path) == path:
        raise ValueError("{} must be normalized.".format(name), path)


class DirMap(collections.Mapping):

    """Remaps directories from one layout to another.

    Useful for systematically translating paths from one environment to another
    in which volumes are mounted differenly, or directories otherwise moved.

    e.g.::

        >>> dirmap = DirMap({'/src': '/dst'})
        >>> dirmap('/src/something')
        '/dst/something'

    """

    def __init__(self, input_=None):
        self._map = {}
        self._sorted = None
        if input_ is not None:
            self.add(input_)

    def add_one(self, src, dst):
        for name, path in ("Source", src), ("Destination", dst):
            assert_clean(name, path)
        self._map[src] = dst
        self._sorted = None

    def add(self, input_, dst=None):

        if dst is not None:
            self.add_one(input_, dst)
            return

        if isinstance(input_, (set, basestring)):
            input_ = [input_]

        elif isinstance(input_, dict):
            input_ = input_.iteritems()

        for spec in input_:
            if isinstance(spec, set):
                self.add_existing(spec)
            if isinstance(spec, str):
                self.add_str(spec)
            else:
                self.add_one(*spec)

    def add_str(self, input_):

        for chunk in input_.split(';'):

            if not chunk:
                continue

            parts = chunk.split(',')
            if len(parts) > 1:
                self.add_existing(parts)
                continue

            parts = chunk.split(':')
            if len(parts) != 2:
                raise ValueError("More than one colon in chunk.", chunk)
            
            self.add_one(*parts)


    def add_existing(self, paths, *args):

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
            self.add_one(src, dst)

    def __iter__(self):
        return iter(self._map)

    def __getitem__(self, i):
        return self._map[i]

    def __len__(self):
        return len(self._map)

    def __call__(self, path):

        if self._sorted is None:
            self._sorted = sorted(self._map.iteritems(), key=lambda (src, dst): (-len(src), src, dst))

        for src, dst in self._sorted:

            if not path.startswith(src):
                continue

            if len(src) == len(path):
                return dst

            if path[len(src)] == os.path.sep:
                rel_path = path[len(src):]
                return dst + rel_path

        return path

    def apply(self, path):
        return self(path)

