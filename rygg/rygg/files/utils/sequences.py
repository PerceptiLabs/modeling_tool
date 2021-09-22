
def observe_progress(expected_count, sequence, callback_fn):
    so_far = 0
    interval = expected_count / 100
    callback_fn(expected_count, 0)

    for x in sequence:
        so_far += 1

        # don't firehose the status. Just call back on increments of 1%
        if so_far % (expected_count / 100) == 0:
            callback_fn(expected_count, so_far)

        yield x

    callback_fn(expected_count, expected_count)


def on_first(sequence, fn, *args, **kwargs):
    called = False

    for x in sequence:
        if not called:
            fn(*args, **kwargs)

        yield x

