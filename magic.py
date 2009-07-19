def thislist():
    """Return a reference to the list object being constructed by the
    list comprehension from which this function is called. Raises an
    exception if called from anywhere else.
    """
    import sys
    d = sys._getframe(1).f_locals
    nestlevel = 1
    while '_[%d]' % nestlevel in d:
        nestlevel += 1
    return d['_[%d]' % (nestlevel - 1)]

if __name__ == "__main__":
    l = [1,2,3,4]
