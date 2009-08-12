import scikits.timeseries as ts
import numpy as np
import numpy.ma as ma
import csv, itertools
import scikits.timeseries.lib.reportlib as rl
import scipy.stats.mstats as stats
import datetime
from magic import thislist
from math import sqrt

now = datetime.datetime.now

class Cusum(object):
    """two method are implemented (pys, pds),
        Attribute:
            er: Excess Return Series
            threshold: threshold
            cusum: Cusum Time Series
            crossRecord: A list of nested tuples for the threshold crossing record
            """
    verbose = False
    def __init__(self, er, threshold, fcn ="pds", **argv):
        """para should be a tuple of parameters for the underlying function"""
        fcndict = {"pds":self._pds, "pys":self._pys}
        self.er = er
        self.threshold = threshold
        self._fcn = fcndict[fcn]
        self.para = argv.get("para")

    def _pys(self, sigma = 7.5, mugood = 0.5, mubad = 0., gamma=0.9, std = 1.0):
        sigmas = [sigma, sigma]
        mgamma = 0.5*(1.0 - gamma)
        for er in windows(self.er[2:], 2, 1):
            if len(er)==2: sigmas.append(gamma*sigmas[-1] + mgamma * (er[1]-er[0])**2.0)
        sigmas = map(sqrt, sigmas)
        irs = [12.0 * i[1] / i[0] for i in itertools.izip(sigmas, self.er[1:])]
        L = [0.0]
        std = 1.0/(std**2.0)
        self.crossRecord = []
        for i in irs:
            l = max(0.0, L[-1] + std*(mubad-mugood) * ( i - 0.5*(mugood+mubad)))
            if l >= self.threshold:
                self.crossRecord.append(((self.er.dates[len(L)-1], L[-1]), (self.er.dates[len(L)], l)))
                L.append(0.0)
            else: L.append(l)
        self.cusum = ts.time_series(L, start_date = self.er.dates[0], dtype=float)
        
    def _pds(self, k, method = "twoside", nom = 36):
        self.crossRecord = []
        __method__ = ("twoside","upper", "lower")
        if method not in __method__: raise
        else: self.method = method
        sarl = []
        for n,i in enumerate(cumwindow(self.er,nom-1)):
            sar = (12.0 * self.er[n+nom-1] - ma.mean(i))/(ma.std(i, ddof = 1) * 3.4641016151377544)
            sarl.append(sar)
        cusums = [sarl[0]]
        if method == "twoside":
            for i in sarl[1:]:
                cu = cusums[-1] + i
                if abs(cu) > self.threshold:
                    cusums.append(0.0)
                    self.crossRecord.append(((self.er.dates[len(cusums)-1]+35, cusums[-2]), (self.er.dates[len(cusums)-1]+36, cu)))
                else: cusums.append(cu)
            self.cusum = ts.time_series(cusums, start_date = self.er.dates[0]+nom, dtype=float)
        elif method == "upper":
            cusums = [max(0, sarl[0]-k)]
            for i in sarl[1:]:
                cu = max(0, i-k+cusums[-1])
                if abs(cu) > self.threshold:
                    cusums.append(0.0)
                    self.crossRecord.append(((self.er.dates[len(cusums)-1]+35, cusums[-2]), (self.er.dates[len(cusums)-1]+36, cu)))
                else: cusums.append(cu)
            self.cusum = ts.time_series(cusums, start_date = self.er.dates[0]+nom, dtype=float)                
        elif method == "lower":
            cusums = [max((0, -sarl[0]-k))]
            for i in sarl[1:]:
                cu = max(0, -i-k+cusums[-1])
                if abs(cu) > self.threshold:
                    cusums.append(0.0)
                    self.crossRecord.append(((self.er.dates[len(cusums)-1]+35, cusums[-2]), (self.er.dates[len(cusums)-1]+36, cu)))
                else: cusums.append(cu)
            self.cusum = ts.time_series(cusums, start_date = self.er.dates[0]+nom, dtype=float)                
        else: raise Exception("Uncaught Case")

    def train(self):
        if self.verbose: time1 = now()
        self._fcn(*self.para)
        if self.verbose:
            time2 = now()
            print time2 - time1
        return self

    def getCrossOverDate(self): return self.cusum[[d3 for ((d1,d2),(d3,d4)) in self.crossRecord]]

    def countCrossOver(self, nom = None):
        if nom == None:
            return len(self.crossRecord)
        else:
            temp = self.getCrossOverDate()
            return len([i for i in (temp.dates > (ts.now('m') - nom)) if i])
        
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
    if results: yield results

def filterMngsByDate(mngs, date = 1):
    date = ts.now('m') - date
    def _filtermng(mng, date):
        return len(mng.dates[mng.dates>date])
    return [i for i in mngs if _filtermng(i[1], date)]


def dataFormat(data):
    """Parses out dates and managers from a csv, filters
       out unknown values, and eliminates lists with under
       60 known values."""
    
    date = data[0,1:]
    desc = data[1:,0]
    data = np.array(data[1:,1:])
    first_date=ts.Date('M', '1999-01')
    desc = list(map( lambda x: x[0,0], desc))
#    format = [float] * len(desc)
#    format = zip(desc, format)
    serieses = [ ts.time_series(i, start_date = first_date, dtype = float) for i in data]
    serieses = [i[i>-999] for i in [ma.masked_values(series, -999) for series in serieses] if len(i[i>-999]) > 60]
        
    return serieses

def main():
    ##    data = np.matrix(list(csv.reader(open("large_growth.csv", "r"))))
    import csv #moved up to before this line
    data = np.matrix(list(csv.reader(open("spmstar.csv", "r"))))
    date = data[0,1:]
    desc = data[1:,0]
    data = np.array(data[1:,1:])
    first_date=ts.Date('M', '1999-01')
    desc = list(map( lambda x: x[0,0], desc))
#    format = [float] * len(desc)
#    format = zip(desc, format)
    serieses = [ ts.time_series(i, start_date = first_date, dtype = float) for i in data]
    serieses = [i[i>-999] for i in [ma.masked_values(series, -999) for series in serieses] if len(i[i>-999]) > 60]
        
    mngs = []
    peer_size = len(serieses)
##    import csv
    writer = csv.writer(open("table.csv", "wb"))
    for n, (name, i) in enumerate(zip(desc, serieses)):
        c = Cusum(i, 4, fcn = "pds", para = (1,"lower", 36)).train()
        s = c.getCrossOverDate()
        writer.writerow((name , c.countCrossOver(1), c.countCrossOver(3), c.countCrossOver(6), c.countCrossOver(12), c.countCrossOver(24), c.countCrossOver(36)))

#        s = Cusum(i, 18, fcn = "pys", para = ()).train().getCrossOverDate() 
        mngs.append( (name, s))

    del writer


    tmngs = filterMngsByDate(mngs, 1)
    print len(tmngs)        
    tmngs = filterMngsByDate(mngs, 3)
    print len(tmngs)        
    tmngs = filterMngsByDate(mngs, 6)
    print len(tmngs)        
    tmngs = filterMngsByDate(mngs, 12)
    print len(tmngs)    
    
if __name__ == "__main__":
    main()
    
