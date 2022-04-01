def slice(d, *keys):
    return {k: d[k] for k in keys if k in d}


# mashup of multi-level group_by and reduce
def aggregate_flat(seq, keys, func, initializer=None):
    if not keys:
        raise ValueError("keys can't be empty")

    # we can't hash by compound keys unless we do some extra work
    def hashseq(seq):
        ret = 0
        for x in seq:
            ret ^= hash(x)
        return ret

    def get_key_for_item(x):
        keys_dict = slice(x, *keys)
        k = hashseq(keys_dict.values())
        return k

    as_dict = {}
    for x in seq:
        key = get_key_for_item(x)
        previous = as_dict.get(key, initializer)
        as_dict[key] = {**x, **func(previous, x)}

    return list(as_dict.values())


def hash_adder(key):
    def inner(l, r):
        rval = r[key]
        if not l:
            return {key: rval}
        lval = l[key]
        return {key: lval + rval}

    return inner


# dive down into nested dicts w/o key errors.
# Example:
#  dig({'a': {'b': 1}}, 'a', 'b') == 1
#  dig({'a': {'b': 1}}, 'a', 'c') == None
def dig(d, *keys):
    ret = d
    for k in keys:
        if ret:
            ret = ret.get(k)
    return ret
