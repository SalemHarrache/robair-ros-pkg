# -*- coding: utf-8 -*-
"""
    robair_common.logger
    --------------------

    Logging setup.
"""
from __future__ import unicode_literals
import logging
import roslib
import rospy
from .compat import NullHandler

roslib.load_manifest('robair_common')


def get_logger():
    '''Initialize a speaking logger with stream handler (stderr).'''
    logger = logging.getLogger("robair")
    level_name = rospy.get_param('logger_level', 'DEBUG')
    if level_name not in ["CRITICAL", "ERROR", "WARN", "INFO", "DEBUG"]:
        logger.addHandler(NullHandler())
        return logger
    else:
        level = logging._levelNames[level_name]
    # Default to logging to stderr.
    format = '%(asctime)s %(levelname)s: %(message)s'
    logging.basicConfig(level=level, format=format)

    formatter = logging.Formatter(format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger = logging.getLogger("robair")
    logger.setLevel(level)
    logger.addHandler(stream_handler)
    return logger
