#!/usr/src/env python
# -*- coding: utf-8 -*-
import logging
import coloredlogs


def get_logger(log_level: str, log_format: str, name: str = None) -> logging.Logger:
    res = logging.getLogger(__name__) if name is None else logging.getLogger(name)
    coloredlogs.install(level=log_level.upper(), fmt=log_format)
    return res
