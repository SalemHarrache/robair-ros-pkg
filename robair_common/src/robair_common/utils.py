# -*- coding: utf-8 -*-
from __future__ import unicode_literals


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
