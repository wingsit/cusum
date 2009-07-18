import scikits.timeseries as ts
import numpy as np
import numpy.ma as ma
import csv
import scikits.timeseries.lib.reportlib as rl
import scipy.stats.mstats as stats


data = np.matrix(list(csv.reader(open("spmstar.csv", "r"))))
date = data[0,1:]
desc = data[1:,0]
data = np.array(data[1:,1:])

first_date=ts.Date('M', '1999-01')
desc = list(map( lambda x: x[0,0], desc))
format = [float] * len(desc)
format = zip(desc, format)
#print format
serieses = [ ts.time_series(i, start_date = first_date, dtype = float, fill_value = -99) for i in data]
serieses = [i[i>-999] for i in [ma.masked_values(series, -999) for series in serieses] if len(i) > 48]
print len(serieses)

s = serieses[1]
# for series in serieses:
#     try:
#         print rl.Report(series)()
#     except:
#         pass



#print stats.gmean(s)
#print s
#print ma.mean(s[:36])

def cumwindow(a, start = 0):
    for  i in xrange(len(a[start:])):
        yield a[0:i+start]

print s
cusum = []

for n, i in enumerate(cumwindow(s, 35)):
    er = ma.mean(i)
    std = ma.std(i, ddof = 1)
    sar = (12.0 * s[n+35] - er) / (std * (12.0 ** 0.5))
    cusum.append(sar)
    print  s[n+35],er, std, sar, sum(cusum)


# def rmean(timeseries, training_period = 36):
#     print ma.mean(s[:training_period])
#     for i in enumerate(s[36:]):
#         print i
    
# print rmean(s)
