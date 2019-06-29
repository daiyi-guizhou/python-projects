import threading
import inspect
import ctypes
import time
import logging
import traceback

# https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread


def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class ForceInturruptException(Exception):
    pass


class ForceTerminateException(Exception):
    pass


class ThreadWithExc(threading.Thread):
    '''A thread class that supports raising exception in the thread from
       another thread.
    '''

    def _get_my_tid(self):
        """determines this (self's) thread id

        CAREFUL : this function is executed in the context of the caller
        thread, to get the identity of the thread represented by this
        instance.
        """
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        # do we have it cached?
        if hasattr(self, "_thread_id"):
            return self._thread_id

        # no, look for it in the _active dict
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid

        # TODO: in python 2.6, there's a simpler way to do : self.ident
        raise AssertionError("could not determine the thread's id")

    def raiseExc(self, exctype):
        """Raises the given exception type in the context of this thread.

        If the thread is busy in a system call (time.sleep(),
        socket.accept(), ...), the exception is simply ignored.

        If you are sure that your exception should terminate the thread,
        one way to ensure that it works is:

            t = ThreadWithExc( ... )
            ...
            t.raiseExc( SomeException )
            while t.isAlive():
                time.sleep( 0.1 )
                t.raiseExc( SomeException )

        If the exception is to be caught by the thread, you need a way to
        check that your thread has caught it.

        CAREFUL : this function is executed in the context of the
        caller thread, to raise an excpetion in the context of the
        thread represented by this instance.
        """
        _async_raise(self._get_my_tid(), exctype)

    def interrupt_single_run(self):
        print('interrupt_single_run')
        self.raiseExc(ForceInturruptException)

    def terminate(self):
        self.raiseExc(ForceTerminateException)


class ForeverThread(ThreadWithExc):
    ''' This ForeverThread keeps thread alive with entry `single_run` '''

    def __init__(self, timeSleepInSeconds=0.1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeSleepInSeconds = timeSleepInSeconds
        self.logger = logging.getLogger('ForeverThread')

    def single_run(self):
        if self._target:
            self._target(*self._args, **self._kwargs)
        else:
            raise NotImplementedError('Implement me to run or set target')

    def run(self):
        while True:
            try:
                self._last_run_time = time.time()
                self.single_run()
            except ForceInturruptException:
                self.logger.warning('Interrupted by others, run again')
            except ForceTerminateException:
                self.logger.critical('Terminated by others, exit')
                break
            except:
                self.logger.error(traceback.format_exc()) 
            finally:
                time.sleep(self.timeSleepInSeconds)             


class TimeoutDaemon(ForeverThread):
    def __init__(self):
        super().__init__()
        self.threads_timeout = {}
        self.lock = threading.Lock()
        self.start()

    def set_thread_single_run_timeout(self, t, timeout):
        if not issubclass(type(t), ForeverThread):
            raise ValueError('t is not subclass of ForeverThread!')
        with self.lock:
            self.threads_timeout[t] = timeout

    def single_run(self):
        time.sleep(0.1)
        now = time.time()
        with self.lock:
            for t, timeout in self.threads_timeout.items():
                if now - t._last_run_time > timeout:
                    t.interrupt_single_run()


if __name__ == '__main__':
    # class MyThread(ForeverThread):
    #     def __init__(self):
    #         super().__init__()
    #         self.cnt = 0

    #     def single_run(self):
    #         self.cnt += 1
    #         print(self.cnt)
    #         time.sleep(1)
    #         if self.cnt > 3:
    #             raise Exception()

    # t = MyThread()
    # t.start()

    # def xx():
    #     print(time.time())
    #     time.sleep(0.5)
    #     raise Exception()
    # t = ForeverThread(target=xx)
    # t.start()
    # t.join()

    # time.sleep(2)
    # t.interrupt_single_run()

    # time.sleep(2)
    # t.terminate()

    # t.join()
    # print('over')

    def xx2():
        print('xx2:', time.time())
        for _ in range(30):
            time.sleep(0.1)
    t = ForeverThread(target=xx2)
    t.start()

    daemon = TimeoutDaemon()
    daemon.set_thread_single_run_timeout(t, 4)

    t.join()
