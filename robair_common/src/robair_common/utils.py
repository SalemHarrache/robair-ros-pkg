# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time


def parse_args(args):
    """ Parse a list of arguments and create *args and **kwargs
    >>> parse_args(("a", "b"))
    (['a', 'b'], {})
    >>> parse_args(("a", "b=a"))
    (['a'], {'b': 'a'})
    """
    new_args = []
    kwargs = {}
    for arg in args:
        if "=" in arg:
            key, value = arg.split('=', 1)
            kwargs[key] = value
        else:
            new_args.append(arg)
    return new_args, kwargs


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
