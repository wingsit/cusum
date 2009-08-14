import csv
from datetime import date
reader = list(csv.reader(open("fourfund.csv", "r")))
writer = csv.writer(open("pfourfund.csv", "w"), dialect = csv.excel)
reader = zip(*reader)[2:]
reader = zip(*reader)

def cleanup(l):
    def mapper(i):
        try:
            return float(i)
        except:
            if i == "NA":return -999
            elif "Excess" in i:
                print i[-8:]
                return i[-8:]
            else:
                return i
                
    return map(mapper, l)

reader = map(cleanup, reader)

writer.writerows(reader)
del writer

print "Here yet"
