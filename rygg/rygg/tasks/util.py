def to_status_percent(publish_fn, total_steps, step_ix, step_name, total_increments, increment_ix):
    if not hasattr(to_status_percent, "total_percent"):
        to_status_percent.total_percent = 0
        # make sure we set the status on the first call
        publish_fn(100, 0, step_name)

    total_percent = to_status_percent.total_percent
    prev_step_count = step_ix
    prev_step_percent = int(step_ix / total_steps * 100)
    cur_percent = int(increment_ix / total_increments * 100)
    cur_percent_scaled = int(cur_percent / total_steps)
    new_total_percent = prev_step_percent + cur_percent_scaled

    # only update on a change to avoid blasting publish_fn
    if new_total_percent != to_status_percent.total_percent:
        to_status_percent.total_percent = new_total_percent
        publish_fn(100, new_total_percent, step_name)

