import collections
import os
import re
import pprint


DirMapEntry = collections.namedtuple('DirMapEntry', 'src dst pattern')


def create_trie(src_iter):
    trie = {}
    for src in src_iter:
        node = trie
        parts = src[1:].split(os.path.sep)
        for part in parts:
            node = node.setdefault(part, {})
        node[None] = True # Signal that it is the end.
    return trie

_sep_re = os.path.sep if os.path.sep == '/' else re.escape(os.path.sep)

def format_trie_pattern(root, indent=''):

    indent2 = indent + '    '

    end = False
    dsts = []
    for src, node in sorted(root.iteritems()):

        if src is None:
            end = True
            continue

        dst = format_trie_pattern(node, indent2)
        if dst:
            dsts.append(re.escape(src) + _sep_re + dst)
        else:
            dsts.append(re.escape(src))

    if dsts:
        dsts = '|'.join('\n{i2}{dst}'.format(i2=indent2, dst=dst) for dst in dsts)
    
    if end and dsts:
        pattern = '{i}(?:|/(?:{dsts}\n{i}))'.format(
            i=indent,
            dsts=dsts,
        )
    elif not end:
        pattern = '{i}(?:{dsts}\n{i})'.format(
            i=indent,
            dsts=dsts,
        )
    else:
        pattern = ''

    return pattern



def append_trie(trie, src, dst):
    node = trie
    parts = src[1:].split(os.path.sep)
    for part in parts:
        node = node.setdefault(part, {})
    node[None] = dst

def lookup_trie(trie, path):

    parts = path[1:].split(os.path.sep)
    node = trie
    results = []

    for i, part in enumerate(parts):
        
        node = node.get(part)
        if node is None: # We hit the end of the trie.
            break

        dst = node.get(None)
        if dst is not None:
            results.append((i, dst))

    if not results:
        return None, None

    i, dst = results[-1]
    return dst, os.path.sep.join(parts[i + 1:])


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
        self._maps = {}
        self._trie = {}
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

        #pattern = re.compile(r'^(?:{})({}.*)?$'.format(re.escape(src), re.escape(os.path.sep)))
        self._maps[src] = dst
        append_trie(self._trie, src, dst)

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

    def __iter__(self):
        return iter(self._maps)

    def __getitem__(self, i):
        return self._maps[i]

    def __len__(self):
        return len(self._maps)

    def __call__(self, path):

        #assert_clean('Path', path)

        dst, rel_path = lookup_trie(self._trie, path)

        if not dst:
            return

        if rel_path:
            return dst + os.path.sep + rel_path
        else:
            return dst


    def get(self, path):
        res = self(path) or path
        #print path, res
        return res

