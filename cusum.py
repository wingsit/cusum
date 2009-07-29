import scikits.timeseries as ts
import numpy as np
import numpy.ma as ma
import csv, itertools
import scikits.timeseries.lib.reportlib as rl
import scipy.stats.mstats as stats
from magic import thislist
import datetime
now = datetime.datetime.now

class Cusum(object):
    """two method are implemented (pys, pds)"""
    verbose = True
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
        else:
            self.method = method
        sarl = []
        if method == "twoside":
            for n,i in enumerate(cumwindow(self.er,nom-1)):
                sar = (12.0 * self.er[n+nom-1] - ma.mean(i))/(ma.std(i, ddof = 1) * 3.4641016151377544)
                sarl.append(sar)
            self.cusum = ts.time_series([sum(i) for i in cumwindow(sarl,1)], start_date = self.er.dates[0]+nom, dtype = float)
#        rl.Report(self.cusum)()
        elif method == "upper":
            for n,i in enumerate(cumwindow(self.er,nom-1)):
                sar = (12.0 * self.er[n+nom-1] - ma.mean(i))/(ma.std(i, ddof = 1) * 3.4641016151377544)
                sarl.append(sar)
            self.cusum = [max((0, sarl[0]-k))]
            for i in sarl[1:]:
                self.cusum.append(max(0, i-k+self.cusum[-1]))
            self.cusum = ts.time_series(self.cusum, start_date = self.er.dates[0]+nom, dtype=float)
        elif method == "lower":
            for n,i in enumerate(cumwindow(self.er,nom-1)):
                sar = (12.0 * self.er[n+nom-1] - ma.mean(i))/(ma.std(i, ddof = 1) * 3.4641016151377544)
                sarl.append(sar)
            self.cusum = [max((0, -sarl[0]-k))]
            for i in sarl[1:]:
                self.cusum.append(max(0, -i-k+self.cusum[-1]))
            self.cusum = ts.time_series(self.cusum, start_date = self.er.dates[0]+nom, dtype=float)
        else:
            raise Exception("Uncaught Case")
        pass

    def train(self):
        if self.verbose: time1 = now()
        self._fcn(*self.para)
        if self.verbose:
            time2 = now()
            print time2 - time1
        return self

    def getCrossOverDate(self):
        date = []
        for n, i in enumerate(windows(self.cusum,2,1)):
            if len(i)==2:
                if (i[0] < self.threshold and i[1] >= self.threshold)\
                        or (i[0] > -self.threshold and i[1] < -self.threshold):
                    if self.verbose: print self.cusum.dates[n+1],i            
                    date.append(self.cusum.dates[n+1])
        return self.cusum[date]

def cumwindow(a, start = 0):
    for  i in xrange(len(a[start:])):
        yield a[0:i+start]

def windows(iterable, length=2, overlap = 0):
    it = iter(iterable)
    results = list(itertools.islice(it,length))
    while len(results) == length:
        yield results
        results = results[length - overlap:]
        results.extend(itertools.islice(it, length-overlap))
    if results:
        yield results

def filterMngsByDate(mngs, date = 1):
    date = ts.now('m') - date
    def _filtermng(mng, date):
        return len(mng.dates[mng.dates>date])
    return [i for i in mngs if _filtermng(i[1], date)]
    
if __name__ == "__main__":
    data = np.matrix(list(csv.reader(open("large_growth.csv", "r"))))
#    data = np.matrix(list(csv.reader(open("spmstar.csv", "r"))))
    date = data[0,1:]
    desc = data[1:,0]
    data = np.array(data[1:,1:])
    first_date=ts.Date('M', '1999-01')
    desc = list(map( lambda x: x[0,0], desc))
    format = [float] * len(desc)
    format = zip(desc, format)
#print format
    serieses = [ ts.time_series(i, start_date = first_date, dtype = float) for i in data]
    serieses = [i[i>-999] for i in [ma.masked_values(series, -999) for series in serieses] if len(i[i>-999]) > 60]
    
    
#    s = serieses[1]
#    t = Cusum(s, 4, fcn = "pds", para = (1,"twoside", 36)).train().getCrossOverDate()
    mngs = []
    peer_size = len(serieses)
    for n, (name, i) in enumerate(zip(desc, serieses)):
##        print float(n*100)/peer_size
        print name
        s = Cusum(i, 4, fcn = "pds", para = (1,"lower", 36)).train().getCrossOverDate()
        mngs.append( (name, s))

    tmngs = filterMngsByDate(mngs, 1)
    for i in tmngs:
        print i
    print len(tmngs)        
##    tmngs = filterMngsByDate(mngs, 3)
##    print len(tmngs)        
##    tmngs = filterMngsByDate(mngs, 6)
##    print len(tmngs)        
##    tmngs = filterMngsByDate(mngs, 12)
##    print len(tmngs)        
    
