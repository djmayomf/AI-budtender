import threading
from queue import Queue
from typing import Callable, Any, List
import logging

logger = logging.getLogger(__name__)

class Future:
    def __init__(self):
        self._event = threading.Event()
        self._result = None
        self._exception = None
        
    def set_result(self, result):
        self._result = result
        self._event.set()
        
    def set_exception(self, exception):
        self._exception = exception
        self._event.set()
        
    def result(self, timeout=None):
        self._event.wait(timeout)
        if self._exception:
            raise self._exception
        return self._result

class CustomThreadPool:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.tasks = Queue()
        self.workers: List[threading.Thread] = []
        self.running = True
        self._start_workers()
        
    def _start_workers(self):
        for _ in range(self.max_workers):
            worker = threading.Thread(target=self._worker_thread)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
            
    def _worker_thread(self):
        while self.running:
            try:
                future, func, args, kwargs = self.tasks.get(timeout=1)
                try:
                    result = func(*args, **kwargs)
                    future.set_result(result)
                except Exception as e:
                    logger.error(f"Error in worker thread: {str(e)}")
                    future.set_exception(e)
                finally:
                    self.tasks.task_done()
            except Queue.Empty:
                continue
                
    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        future = Future()
        self.tasks.put((future, fn, args, kwargs))
        return future
        
    def shutdown(self, wait: bool = True):
        self.running = False
        if wait:
            for worker in self.workers:
                worker.join()
                
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

# Usage example:
def example_usage():
    def worker_function(x):
        return x * x
        
    with CustomThreadPool(max_workers=4) as pool:
        futures = [pool.submit(worker_function, i) for i in range(10)]
        results = [f.result() for f in futures]
        
    print(results)
