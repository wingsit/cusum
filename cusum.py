import scikits.timeseries as ts
import numpy as np
import numpy.ma as ma
import csv
import scikits.timeseries.lib.reportlib as rl
import scipy.stats.mstats as stats



class cusum(object):
    """two method are implemented (pys, pds)"""

    def __init__(self,er, threshold, fcn ="pds", **argv):
        """para should be a tuple of parameters for the underlying function"""
        fcndict = {"pds":self._pds, "pys":self._pys}
        self.er = er
        self.threshold = threshold
        self._fcn = fcndict[fcn]
        self.para = argv.get("para")
        pass

    def _pys(sigma, mu1, mu2, gamma):
        pass

    def _pds(self, k, method = "twoside", nom = 36):
        __method__ = ("twoside","upper", "lower")
        if method not in __method__:
            raise
        cusum = []
        for n,i in enumerate(cumwindow(self.er,nom-1)):
            m = ma.mean(i)
            std = ma.std(i, ddof = 1)
            sar = (12.0 * self.er[n+nom-1] - m)/(std * (12.0**0.5))
            print m, std, sar
            cusum.append(sar)
        print cusum
        pass

    def train(self):
        self._fcn(*self.para)
        pass

def cumwindow(a, start = 0):
    for  i in xrange(len(a[start:])):
        yield a[0:i+start]
    
if __name__ == "__main__":
    pass
