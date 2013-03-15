# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from functools import wraps
import errno
import os
import signal
import time
import threading
from contextlib import contextmanager


class retry(object):
    '''Retries a function or method until it returns True value.
    delay sets the initial delay in seconds, and backoff sets the factor by
    which the delay should lengthen after each failure.
    Tries must be at least 0, and delay greater than 0.'''

    def __init__(self, tries=3, delay=1):
        self.tries = tries
        self.delay = delay

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            for i in range(self.tries):
                try:
                    ret = f(*args, **kwargs)
                    if ret:
                        return ret
                    elif i == self.tries - 1:
                        return ret
                except Exception as e:
                    if i == self.tries - 1:
                        # last chance
                        raise e
                if self.delay > 0:
                    time.sleep(self.delay)
        wrapped_f.__doc__ = f.__doc__
        wrapped_f.__name__ = f.__name__
        wrapped_f.__module__ = f.__module__
        return wrapped_f


class TimeoutError(Exception):
    pass


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


@contextmanager
def thread_context(**kwargs):
    """ Context manager that save any context bject in the thread local
        context.
    """
    threadlocal = threading.local()
    for key, value in kwargs.items():
        setattr(threadlocal, key, value)
    yield


def thread(*proxy_args, **proxy_kwargs):

    fire = proxy_kwargs.pop('fire', False) or proxy_args or proxy_kwargs

    def decorator(func):

        if fire:

            @wraps(func)
            def fun(*args, **kwargs):
                func(*args, **kwargs)

            fun.thread = threading.Thread(target=fun, args=proxy_args,
                                          kwargs=proxy_kwargs)
            fun.thread.start()

            return fun

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                thread = threading.Thread(target=func, args=args,
                                          kwargs=kwargs)
                thread.start()
                return thread

            return wrapper

    return decorator
