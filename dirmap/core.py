import collections
import os

from .deep import deep_apply as _deep_apply


def assert_clean(path, name="Path"):
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
        """Add a single direct source to destination mapping."""
        for name, path in ("Source", src), ("Destination", dst):
            assert_clean(path, name)
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
        """Add (potentially many) mappings from a specially formatted string.

        The different chunks of the string are seperated with semi-colons.

        If the chunk contains commas, and the comma-delimeted parts of that
        chunk are passed to :method:`DirMap.add_existing`.

        Otherwise, the colon-delimited parts of that chunk are passed as
        the source and destination to :method:`DirMap.add_one`.

        e.g.::
            
            # Setup a single direct mapping.
            dirmap.add_str("/src:/dst")
            
            # Setup a few direct mappings.
            dirmap.add_str("/src1:/dst1;/src2:/dst2")

            # Pick one of a few paths via add_existing.
            dirmap_add_str("/path1,/path2,/path2")

        """

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

        srcs = set()
        dsts = set()
        for p in paths:
            assert_clean(p)
            (dsts if os.path.exists(p) else srcs).add(p)
        
        if len(dsts) != 1:
            raise ValueError("Not exactly one of given paths exists.", paths)
        if not srcs:
            raise ValueError("Only given one path.")
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

    def get(self, *args, **kwargs):
        """Stub to stop one from accidentally using this like a normal mapping.

        :raises NotImplementedError: on every call.

        """
        raise NotImplementedError("DirMap is not really a dict; use item access instead.")

    def apply(self, path):
        """Applies the dirmap to the given path.

        This is the same as calling the dirmap directly, and provided for when
        your code would be clearer to use a method.

        """

        return self(path)

    def deep_apply(self, obj, **kwargs):
        """Apply to everything in the given structure.

        .. seealso:: :func:`dirmap.deep.deep_apply` for caveats.

        """
        return _deep_apply((lambda x: self(x) if isinstance(x, basestring) else x), obj, **kwargs)



