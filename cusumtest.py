import unittest as ut
import cusum as cs
import csv
import numpy as np
import scikits.timeseries as ts

class cusumtest(ut.TestCase):
    def setUp(self):
        self.pdssuite = []
        self.pyssuite = []

        data = np.matrix(list(csv.reader(open("test.csv", "r"))))
        data = cs.dataFormat(data)
        self.pdssuite.append(cs.Cusum(data[0], 1000, fcn = "pds", para = (1,"twoside", 36)))
        self.pdssuite.append(cs.Cusum(data[1], 1000, fcn = "pds", para = (1,"upper", 36)))
        self.pdssuite.append(cs.Cusum(data[2], 1000, fcn = "pds", para = (1,"lower", 36)))
        self.pyssuite.append(cs.Cusum(data[3], 1000, fcn = "pys", para = (7.5, 0.5, 0., 0.9, 1.0)))
        
    def testPds(self):
        print "testPds"
        cusum = list(csv.reader(open("cusumpds.csv", "r")))
        outof = len(self.pdssuite)
        for n, case in enumerate(self.pdssuite):
            print n+1, '/', outof
            case.train()
            progsum = case.cusum.data.tolist()
            truesum = cusum[n]
            if len(progsum) != len(truesum):
                raise AssertionError
            for n, i in enumerate(progsum):
                self.assertAlmostEqual(i, float(truesum[n]))

    def testPys(self):
        print "testPys"
        cusum = list(csv.reader(open("cusumpys.csv", "r")))
        outof = len(self.pyssuite)
        for n, case in enumerate(self.pyssuite):
            print n+1, '/', outof
            case.train()
            progsum = case.cusum.data.tolist()
            truesum = cusum[n]
            if len(progsum) != len(truesum):
                raise AssertionError
            for n, i in enumerate(progsum):
                self.assertAlmostEqual(i, float(truesum[n]))

    def testPdsDate(self):
        print "testPdsDate"
        cusum = list(csv.reader(open("cusumpds.csv", "r")))
        outof = len(self.pdssuite)
        for n, case in enumerate(self.pdssuite):
            print n+1, '/', outof
            case.train()
            progdate = case.cusum.dates.tolist()
            if progdate[0] != ts.Date('M', '2001-8'):
                raise AssertionError

    def testPysDate(self):
        print "testPysDate"
        cusum = list(csv.reader(open("cusumpys.csv", "r")))
        outof = len(self.pyssuite)
        for n, case in enumerate(self.pyssuite):
            print n+1, '/', outof
            case.train()
            progdate = case.cusum.dates.tolist()
            print progdate[0]
            print ts.Date('M', '1999-1')
            if progdate[0] != ts.Date('M', '1999-1'):
                raise AssertionError

class thresholdtest(ut.TestCase):
    def setUp(self):
        self.pdssuite = []
        self.pyssuite = []

        self.pdscross = {0:ts.Date('M', '2002-11'), 1:ts.Date('M', '2002-2'), 2:ts.Date('M', '2001-12')}
        self.pyscross = {0:ts.Date('M', '1999-10')}
        
        data = np.matrix(list(csv.reader(open("test.csv", "r"))))
        data = cs.dataFormat(data)
        self.pdssuite.append(cs.Cusum(data[0], 4, fcn = "pds", para = (1,"twoside", 36)))
        self.pdssuite.append(cs.Cusum(data[1], 4, fcn = "pds", para = (1,"upper", 36)))
        self.pdssuite.append(cs.Cusum(data[2], 4, fcn = "pds", para = (1,"lower", 36)))
        self.pyssuite.append(cs.Cusum(data[3], 4, fcn = "pys", para = (7.5, 0.5, 0., 0.9, 1.0)))

    def testPds(self):
        print "testPdsThresh"
        cusum = list(csv.reader(open("threshpds.csv", "r")))
        outof = len(self.pdssuite)
        for n, case in enumerate(self.pdssuite):
            print n+1, '/', outof
            case.train()
            progsum = case.cusum.data.tolist()
            truesum = cusum[n]
            if len(progsum) != len(truesum):
                raise AssertionError
            for n, i in enumerate(progsum):
                self.assertAlmostEqual(i, float(truesum[n]))

    def testPys(self):
        print "testPysThresh"
        cusum = list(csv.reader(open("threshpys.csv", "r")))
        outof = len(self.pyssuite)
        for n, case in enumerate(self.pyssuite):
            print n+1, '/', outof
            case.train()
            progsum = case.cusum.data.tolist()
            truesum = cusum[n]
            if len(progsum) != len(truesum):
                raise AssertionError
            for n, i in enumerate(progsum):
                self.assertAlmostEqual(i, float(truesum[n]))

    def testPysCrossRecord(self):
        print "testPysCrossRecord"
        cusum = list(csv.reader(open("cusumpys.csv", "r")))
        outof = len(self.pyssuite)
        for n, case in enumerate(self.pyssuite):
            print n+1, '/', outof
            case.train()
            truesum = cusum[n]
            ind = 0
            while abs(float(truesum[ind])) <= case.threshold and ind < len(truesum):
                ind += 1
            self.assertAlmostEqual(float(truesum[ind]), case.crossRecord[0][1][1])
            progdate = case.cusum.dates.tolist()
            if progdate[ind] != self.pyscross[n]:
                raise AssertionError

    def testPdsCrossRecord(self):
        print "testPdsCrossRecord"
        cusum = list(csv.reader(open("cusumpds.csv", "r")))
        outof = len(self.pdssuite)
        for n, case in enumerate(self.pdssuite):
            print n+1, '/', outof
            case.train()
            truesum = cusum[n]
            ind = 0
            while abs(float(truesum[ind])) < case.threshold and ind < len(truesum):
                ind += 1
            self.assertAlmostEqual(float(truesum[ind]), case.crossRecord[0][1][1])
            if progdate[ind] != self.pdscross[n]:
                raise AssertionError

class handletest(ut.TestCase):
    def setUp(self):
        data = np.matrix(list(csv.reader(open("handletest.csv", "r"))))
        self.data = cs.dataFormat(data)
        self.na = cs.Cusum(self.data[0], 4, fcn = "pds", para = (1, "twoside", 36))

    def testNA(self):
        print "testNA"
        proger = self.na.er
        trueer = [n + 1 for n in range(100)]
        if len(proger) != len(trueer):
                raise AssertionError
        for n, i in enumerate(proger):
            self.assertAlmostEqual(i, float(trueer[n]))

    def testLimit(self):
        print "testLimit"
        try:
            self.limit = cs.Cusum(self.data[1], 4, fcn = "pds", para = (1, "twoside", 36))
            self.assertEqual(self.limit.er, [])
        except IndexError:
            pass

if __name__ == '__main__':
    ut.main()
