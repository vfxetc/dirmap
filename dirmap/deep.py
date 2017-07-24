

def deep_apply(func, obj, dict_keys=False):
    """Apply func to everything in the given structure.

    This works predictably with dicts, lists, sets and tuples. Any classes
    which extend them are assumed to be able to be called with empty
    constructors (except the tuple which will be passed a generator).

    """

    # We abuse this dict as both settings and the memo cache.
    memo = {'dict_keys': bool(dict_keys)}

    return _deep_apply(func, obj, memo)


def _deep_apply(func, obj, memo):

    # In general, the memo cache exists for recursive objects.
    # We construct an empty version, add it to the memo cache (keyed by the id
    # of the original object), and then go about adding sub-objects to it.
    try:
        return memo[id(obj)]
    except KeyError:
        pass

    if isinstance(obj, list):
        new = type(obj)()
        memo[id(obj)] = new
        for x in obj:
            new.append(_deep_apply(func, x, memo))
        return new

    elif isinstance(obj, set):
        new = type(obj)()
        memo[id(obj)] = new
        for x in obj:
            new.add(_deep_apply(func, x, memo))
        return new

    elif isinstance(obj, dict):
        new = type(obj)()
        memo[id(obj)] = new
        dict_keys = memo['dict_keys']
        for k, v in obj.iteritems():
            new[_deep_apply(func, k, memo) if dict_keys else k] = _deep_apply(func, v, memo)
        return new

    elif isinstance(obj, tuple):
        return type(obj)(_deep_apply(func, x, memo) for x in obj)

    else:
        return func(obj)
