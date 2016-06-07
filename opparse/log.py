import logging


def logger(name):
    l = logging.getLogger(name)
    l.setLevel(logging.ERROR)
    l.addHandler(logging.StreamHandler())
    return l
