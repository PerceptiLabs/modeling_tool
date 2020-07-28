import pytest
import time


from perceptilabs.tasks.executor import TaskExecutor, TaskError, TaskTimeout


@pytest.fixture(scope='function')
def executor():
    e = TaskExecutor()
    yield e
    e.shutdown(kill=True)    

    
def test_runs_func(executor):
    def func(x, y):
        return x*y
    result = executor.run(func, (3,), kwargs={'y': 4})
    assert result == 12


def test_runs_func_in_order(executor):
    x = [executor.run(lambda x: x**2, (x,)) for x in range(10)]
    assert x == [x**2 for x in range(10)]


def test_raises_task_error(executor):
    class MyException(Exception):
        pass
    def func():
        raise MyException
    
    with pytest.raises(TaskError) as exc_:
        executor.run(func)

def test_raises_task_error_with_cause(executor):
    class MyException(Exception):
        pass    
    def func():
        raise MyException
    
    try:
        executor.run(func)
    except Exception as e:
        assert isinstance(e.__cause__, MyException)
    else:
        assert False
    

def test_cannot_run_stopped_executor(executor):
    executor.shutdown(kill=False)
    with pytest.raises(RuntimeError):
        executor.run(lambda x: x**2, (123,))


def test_cannot_run_killed_executor(executor):
    executor.shutdown(kill=True)
    with pytest.raises(RuntimeError):    
        executor.run(lambda x: x**2, (123,))
    
    
def test_raises_timeout(executor):
    def func():
        time.sleep(100)
        
    t0 = time.perf_counter()
    with pytest.raises(TaskTimeout):
        executor.run(func, timeout=0.1)
    t1 = time.perf_counter()
    
    assert t1 - t0 <= 1
