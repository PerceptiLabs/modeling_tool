
# Observe work in percentages
def observe_work(step_result_sequence, update_status_fn):
    total_percent = 0
    for step_ix, parts in enumerate(step_result_sequence):
        total_steps, message, total_increments, increments = parts
        for increment, _ in enumerate(increments):
            prev_step_count = step_ix
            prev_step_percent = int(step_ix / total_steps * 100)
            cur_percent = int(increment / total_increments * 100)
            cur_percent_scaled = int(cur_percent / total_steps)
            new_total_percent = prev_step_percent + cur_percent_scaled

            # only update on a change to avoid blasting update_status_fn
            if new_total_percent != total_percent:
                update_status_fn(100, total_percent, message)
                total_percent = new_total_percent

    update_status_fn(100, 100, f"complete")


