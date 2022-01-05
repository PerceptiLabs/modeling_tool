from concurrent.futures import ThreadPoolExecutor, Future
from threading import Event
from queue import Queue, Empty
from typing import TypeVar, Iterable, Callable, Any

InputType = TypeVar('T')
OutputType = TypeVar('U')
FnType = Callable[[InputType], OutputType]

# Wrap ThreadPoolExecutor.map's eager execution with a queue to make it truly asynchronous
def async_map(input: Iterable[InputType], fn: FnType, cancel_token=Event()) -> Iterable[OutputType]:

    # Wraps f to have a side-effect of putting its result (or exception) into queue q.
    # The return value is None so the synchronous map we're relying on doesn't store too much in memory.
    def wrap_fn(f: FnType, q: Queue) -> Callable[[InputType], None]:
        def inner(val):
            try:
                result = f(val)
                q.put(result)
            except Exception as e:
                q.put(e)
            return None

        return inner

    # Run through the input and submit a work item to the executor for each
    # return how many results we're going to at the end.
    def submit(executor: ThreadPoolExecutor, wrapped_fn: Callable[[InputType], None], items: InputType) -> int:
        ret = 0
        for item in input:
            executor.submit(wrapped_fn, item)
            ret += 1
        return ret

    # Pull results from the output and yield each one until:
    #   * we're cancelled,
    #   * we've yielded as many results as there were inputs (submit_future's value())
    #   * we find an exception in the responses.
    # We know when we're at the end when submit_future is done and we've completed as many items as it submitted.
    def extract_output(output_queue: Queue, submit_future: Future) -> None:
        num_yielded = 0
        num_submitted = None
        while True:
            # if cancelling, then break out
            if cancel_token.is_set():
                break

            # check whether the submit is done, and if so count the inputs
            if num_submitted == None and submit_future.done():
                num_submitted = submit_future.result()

            # if the submit is done and we've yielded all of the results, then bail
            if num_submitted != None and  num_submitted == num_yielded:
                break

            # otherwise, just wait for something and yield it.
            # Time out occasionally to check the cancel_token or whether we're done
            try:
                cur = output_queue.get(timeout=0.5)
            except Empty:
                continue
            try:
                if isinstance(cur, Exception):
                    raise cur

                yield cur
                num_yielded += 1
            finally:
                output_queue.task_done()


    output = Queue()
    f = wrap_fn(fn, output)

    with ThreadPoolExecutor() as executor:
        # Do the submissions from inside the executor to make it async,
        # and then pull from the output queue on the main thread.
        map_future = executor.submit(submit, executor, f, input)

        for x in extract_output(output, map_future):
            yield x
