import scikits.timeseries as ts
import numpy as np
import numpy.ma as ma
import csv
import scikits.timeseries.lib.reportlib as rl
import scipy.stats.mstats as stats


data = np.matrix(list(csv.reader(open("pmstar.csv", "r"))))
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
for series in serieses:
    try:
        print rl.Report(series)()
    except:
        pass

#print stats.gmean(s)
print s
print ma.mean(s)
