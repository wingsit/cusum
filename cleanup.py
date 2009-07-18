import csv
from datetime import date
reader = list(csv.reader(open("mstar.csv", "r")))
writer = csv.writer(open("pmstar.csv", "w"))
reader = zip(*reader)[2:]
reader = zip(*reader)

def cleanup(l):
    def mapper(i):
        try:
            return float(i)
        except:
            if i == "NA":return -999
            else: return i
    return map(mapper, l)

reader = map(cleanup, reader)

writer.writerows(reader)
del writer

print "Here yet"
