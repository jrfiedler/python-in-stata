import unittest
import sys
import random
from types import GeneratorType

from stata_missing import MISSING_VALS as mvs


def makeCapture(parent):
    class CaptureDisplay():
        def write(self, text):
            parent.output += text
        def flush(self):
            pass
    return CaptureDisplay()


class TestSmallFuncs(unittest.TestCase):
    def setUp(self):
        self.output = ""
        self.stdout = sys.stdout
        self.testOut = makeCapture(self)
        self.data = st_View().toList()
        
    def test_st_cols(self): # not in mata
        self.assertRaises(TypeError, st_cols, 0) # argument needs to be str
        self.assertRaises(TypeError, st_cols, "matA", 0) # exactly one argument allowed
        self.assertRaises(TypeError, st_cols) # exactly one argument allowed
    
        self.assertEqual(st_cols("matA"), 4)
        self.assertEqual(st_cols("noSuchMatrix"), 0)
        
    def test__st_data(self):
        self.assertRaises(TypeError, _st_data, 0, 1, 0) # too many arguments
        self.assertRaises(TypeError, _st_data, 0) # too few arguments
        self.assertRaises(TypeError, _st_data, "0", 1) # 1st 2 args must be int
        self.assertRaises(TypeError, _st_data, 0, "1") # 1st 2 args must be int
        self.assertRaises(TypeError, _st_data, 0, 0) # Stata variable is not numeric
        self.assertRaises(IndexError, _st_data, 0, 12) # var num out of range
        self.assertRaises(IndexError, _st_data, 0, -13) # var num out of range
        self.assertRaises(IndexError, _st_data, 74, 1) # obs num out of range
        self.assertRaises(IndexError, _st_data, -75, 1) # obs num out of range
        
        self.assertEqual(_st_data(0, 1), 4099)
        self.assertEqual(_st_data(-1, 1), 11995)
        self.assertEqual(_st_data(0, -1), 0)
        self.assertEqual(_st_data(-1, -1), 1)
        
    def test_st_data(self):
        self.assertRaises(TypeError, st_data, "4", "pr") # 1st arg should be int or iterable of int
        self.assertRaises(TypeError, st_data, 4, None) # 2nd arg should be int, str or iterable of int or str
        self.assertRaises(TypeError, st_data, 4) # too few args
        self.assertRaises(TypeError, st_data, 4, "pr", 1000000) # too many args
        self.assertRaises(TypeError, st_data, 4, "ma") # "make" is not numeric
        self.assertRaises(TypeError, st_data, 4, "ma pr mpg") # "make" is not numeric
        self.assertRaises(TypeError, st_data, 4, 0) # "make" is not numeric
        self.assertRaises(TypeError, st_data, 4, (0,1,2)) # "make" is not numeric
        self.assertRaises(IndexError, st_data, 0, 12) # var num out of range
        self.assertRaises(IndexError, st_data, 0, -13) # var num out of range
        self.assertRaises(IndexError, st_data, 74, 1) # obs num out of range
        self.assertRaises(IndexError, st_data, -75, 1) # obs num out of range
        
        subset1 = st_data(range(0,74,6), range(1,12,4))
        self.assertEqual(subset1,
            [[4099.0, 11.0, 121.0],
             [4453.0, 10.0, 304.0],
             [15906.0, 13.0, 350.0],
             [3955.0, 13.0, 250.0],
             [4187.0, 10.0, 140.0],
             [6165.0, 23.0, 302.0],
             [4733.0, 16.0, 231.0],
             [4425.0, 11.0, 86.0],
             [5222.0, 16.0, 231.0],
             [9735.0, 12.0, 121.0],
             [5799.0, 10.0, 107.0],
             [5899.0, 14.0, 134.0],
             [6850.0, 16.0, 97.0]])
             
        subset2 = st_data(range(0,73,6), (1,5,9))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), (1,5,9))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), "pr tr di")
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), ("pr", "tr di"))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), ("pr", "tr", "di"))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), (-11, -7, -3))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,6,12,18,24,30,36,42,48,54,60,66,72), (-11, "tr", -3))
        self.assertEqual(subset1, subset2)
             
        subset2 = st_data((0,-68,12,-56,24,-44,36,-32,48,54,60,66,72), (-11, "tr", -3))
        self.assertEqual(subset1, subset2)
             
        subset3 = st_data((8, 12, -5, 2, 1), ("di", "pr", "tr"))
        self.assertEqual(subset3,
            [[231.0, 10372.0, 17.0],
             [350.0, 15906.0, 13.0],
             [97.0, 7140.0, 12.0],
             [121.0, 3799.0, 12.0],
             [258.0, 4749.0, 11.0]])
        
    def test_st_format(self): # not in mata
        self.assertRaises(TypeError, st_format, 1, 1) # 1st arg should be str
        self.assertRaises(TypeError, st_format, "%12.0g", "1") # 2nd arg should be numeric
        self.assertRaises(TypeError, st_format, "%12.0g") # too few args
        self.assertRaises(TypeError, st_format, "%12.0g", 1, 1) # too many args
        
        # not much checking to do here; formatting comes directly from Stata, 
        # and Stata's formatting function returns something useful even with bad fmt strings
        
    def test_st_global(self):
        self.assertRaises(TypeError, st_global, "a", "b", "c") # too many arguments
        self.assertRaises(TypeError, st_global) # too few arguments
        self.assertRaises(TypeError, st_global, 0) # arguments must be str
        self.assertRaises(TypeError, st_global, 'globalA', 0) # arguments must be str
        self.assertRaises(ValueError, st_global, ".&*") # malformed name
        self.assertRaises(ValueError, st_global, ".&*", "set value") # malformed name
        
        self.assertEqual(st_global("noSuchGlobal"), "")
        self.assertEqual(st_global("globalA"), "some global")
        
        # other tests through tearDown and .ado
        
    def test_st_isfmt(self):
        goodFmts = [
            '%12.0g', '%12.2f', '%12.4e',
            '%12.0gc', '%12.2fc', '%12.4ec',
            '%12,0g', '%12,2f', '%12,4e',
            '%12,0gc', '%12,2fc', '%12,4ec',
            '%12s', '%21x', '%16H', '%16L',
            '%8H', '%8L', '%tc', '%tC', '%td',
            '%tw', '%tm', '%tq', '%th', '%ty',
            '%tg', '%-tc', '%-tC', '%-td',
            '%-tw', '%-tm', '%-tq', '%-th', 
            '%-ty', '%-tg', '%-12.0g', '%-12.2f', 
            '%-12.4e', '%-12.0gc', '%-12.2fc', 
            '%-12.4ec', '%-12,0g', '%-12,2f', 
            '%-12,4e', '%-12,0gc', '%-12,2fc', 
            '%-12,4ec', '%-12s',
            '%tCDDmonCCYY_HH:MM:SS',
            '%tcDDmonCCYY_HH:MM:SS',
            '%tdDDmonCCYY',
            '%twCCYY!www',
            '%tmCCYY!mnn',
            '%tqCCYY!qq',
            '%thCCYY!hh',
            '%tyCCYY',
            '%tC+DDmon+CC+YY_HH:MM:SS',
            '%tc+DDmon+CC+YY_HH:MM:SS',
            '%td++DD+monCCYY',
            '%tw+CC+YY!www',
            '%tm+CC+YY!mnn',
            '%tq+CC+YY!qq',
            '%th+CC+YY!hh',
            '%ty+CC+YY',
            '%tbcalname:DDmonCCYY_HH:MM:SS',
            '%tbcalname:DDmonCCYY_HH:MM:SS',
            '%tbcalname:DDmonCCYY',
            '%tbcalname:CCYY!www',
            '%tbcalname:CCYY!mnn',
            '%tbcalname:CCYY!qq',
            '%tbcalname:CCYY!hh',
            '%tbcalname:CCYY',
            '%tbcalname:+DDmon+CC+YY_HH:MM:SS',
            '%tbcalname:+DDmon+CC+YY_HH:MM:SS',
            '%tbcalname:++DD+monCCYY',
            '%tbcalname:+CC+YY!www',
            '%tbcalname:+CC+YY!mnn',
            '%tbcalname:+CC+YY!qq',
            '%tbcalname:+CC+YY!hh',
            '%tbcalname:+CC+YY'
        ]
        
        badFmts = [
            'fmt', '%f', '%q', '%10.10g',
            '%12sa', '%20x', '%10H', '%18L', '%7H', 
            '%9L', '%12;4e', '%12|4ec',
            '%tCDDmonBBYY_HH:MM:SS',
            '%tcDDmonBBYY_HH:MM:SS',
            '%tdDDmonBBYY',
            '%twCCZZ!www',
            '%tmCCXX!mnn',
            '%tqCCRR!qq',
            '%thCCZZ!hh',
            '%tyCCXX',
            '%th*CC+YY!hh',
            '%ty*CC+YY',
            '%trDDmonCCYY_HH:MM:SS',
            '%tpDDmonCCYY_HH:MM:SS',
            '%toDDmonCCYY',
            '%tnCCYY!www',
            '%tlCCYY!mnn',
            '%tkCCYY!qq',
            '%tjCCYY!hh',
            '%tiCCYY',
        ]
        
        self.assertRaises(TypeError, st_isfmt, 1) # should be str
        
        self.assertTrue(all(st_isfmt(fmt) for fmt in goodFmts))
        self.assertTrue(all(not st_isfmt(fmt) for fmt in badFmts))
        
    def test_st_islmname(self):
        letters = list('_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        numbers = list('0123456789')
        
        goodChars = letters + numbers
        
        self.assertRaises(TypeError, st_islmname, 1) # arg needs to be str
        
        self.assertFalse(st_islmname('/name')) # cannot contain punctuation
        self.assertFalse(st_islmname('name'*8)) # must must be <= 31 characters long
        self.assertFalse(st_islmname('')) # must must be > 0 characters long
        
        for i in range(50):
            nameLen = random.randint(1,31)
            nameList = [random.choice(goodChars) for i in range(nameLen)]
            name = "".join(nameList)
            self.assertTrue(st_islmname(name))
    
    def test_st_ismissing(self): # not in mata
        self.assertRaises(TypeError, st_ismissing, 0, 0) # too many arguments
        self.assertRaises(TypeError, st_ismissing) # too few arguments
        
        self.assertTrue(st_ismissing(None))
        self.assertTrue(st_ismissing(float('inf')))
        self.assertTrue(st_ismissing(float('-inf')))
        self.assertTrue(st_ismissing(mvs[0]))
        
        self.assertFalse(st_ismissing(0))
        self.assertFalse(st_ismissing('blah')) # non-numerical are not missing
        self.assertFalse(st_ismissing({})) # non-numerical are not missing
        
    def test_st_isname(self):
        letters = list('_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        numbers = list('0123456789')
        
        begChars = letters
        endChars = letters + numbers
        
        self.assertRaises(TypeError, st_isname, 1) # arg needs to be str
        
        self.assertFalse(st_isname('6name')) # must start with underscore or letter
        self.assertFalse(st_isname('/name')) # cannot contain punctuation
        self.assertFalse(st_isname('name'*8 + 'z')) # must must be <= 32 characters long
        self.assertFalse(st_isname('')) # must must be > 0 characters long
        
        for i in range(50):
            nameLen = random.randint(0,31)
            nameList = [random.choice(begChars)] + [random.choice(endChars) for i in range(nameLen)]
            name = "".join(nameList)
            self.assertTrue(st_isname(name))
        
    def test_st_isnumfmt(self):
        # num_fmt_re = re.compile(r'^%(-)?(0)?([0-9]+)(\.|\,)([0-9]+)(f|g|e)(c)?$')
        # any testing here is inferior to simply checking the regular expression 
        # against the specification ; it is good to have tests, though, so ...
        
        self.assertRaises(TypeError, st_isnumfmt, 0) # arg must be str
        
        self.assertFalse(st_isnumfmt("%8.8f")) # precision must be < width
        self.assertFalse(st_isnumfmt("%+8.6f")) # + char not allowed
        self.assertFalse(st_isnumfmt("%8f")) # precision required
        self.assertFalse(st_isnumfmt("!8f")) # first character must be %
        self.assertFalse(st_isnumfmt("%10x")) # x format accepts +/- 21 only
        self.assertFalse(st_isnumfmt("%10H")) # H format accepts +/- 8 and 16 only
        self.assertFalse(st_isnumfmt("%10L")) # L format accepts +/- 8 and 16 only
        
        for i in range(50):
            align = random.choice(('-', ''))
            width = random.randint(1,100)
            septr = random.choice(('.',','))
            preci = random.randint(0,width-1)
            fmtTp = random.choice(('f','g','e'))
            mybeC = random.choice(('c',''))
            fmt = '%' + align + str(width) + septr + str(preci) + fmtTp + mybeC
            self.assertTrue(st_isnumfmt(fmt))
            
        self.assertTrue("%8L")
        self.assertTrue("%-8L")
        self.assertTrue("%8H")
        self.assertTrue("%-8H")
        self.assertTrue("%16L")
        self.assertTrue("%-16L")
        self.assertTrue("%16H")
        self.assertTrue("%-16H")
        self.assertTrue("%21x")
        self.assertTrue("%-21x")
        
    def test_st_isnumvar(self):
        self.assertRaises(TypeError, st_isnumvar, 1.1) # should be int
        self.assertRaises(TypeError, st_isnumvar, 0, 1) # too many arguments
        self.assertRaises(TypeError, st_isnumvar) # too few arguments
        self.assertRaises(ValueError, st_isnumvar, "xx") # no such variable
        
        self.assertTrue(st_isnumvar(9))
        self.assertTrue(st_isnumvar("disp"))
                
        self.assertFalse(st_isnumvar(0))
        self.assertFalse(st_isnumvar("ma"))
        
    def test_st_isstrfmt(self):
        # str_fmt_re = re.compile(r'^%(-|~)?(0)?([0-9]+)s$')
        # any testing here is inferior to simply checking the regular expression 
        # against the specification ; it is good to have tests, though, so ...
        
        self.assertRaises(TypeError, st_isstrfmt, 0) # arg must be str
        
        self.assertFalse(st_isnumfmt("%+8s")) # + char not allowed
        self.assertFalse(st_isnumfmt("!8s")) # first character must be %
        self.assertFalse(st_isnumfmt("%8.8s")) # precision not allowed
        self.assertFalse(st_isnumfmt("%0s")) # width must be > 0
        
        for i in range(50):
            align = random.choice(('-', '~', ''))
            width = random.randint(1,100)
            fmt = '%' + align + str(width) + 's'
            self.assertTrue(st_isstrfmt(fmt))
        
    def test_st_isstrvar(self):
        self.assertRaises(TypeError, st_isstrvar, 1.1) # should be int
        self.assertRaises(TypeError, st_isstrvar, 0, 1) # too many arguments
        self.assertRaises(TypeError, st_isstrvar) # too few arguments
        self.assertRaises(ValueError, st_isstrvar, "xx") # no such variable
        
        self.assertTrue(st_isstrvar(0))
        self.assertTrue(st_isstrvar("ma"))
        
        self.assertFalse(st_isstrvar(9))
        self.assertFalse(st_isstrvar("disp"))
        
    def test_st_isvarname(self): # not in mata
        reserved = frozenset(('_all', '_b', 'byte', '_coef', '_cons', 
            'double', 'float', 'if', 'in', 'int', 'long', '_n', '_N',
            '_pi', '_pred', '_rc', '_skip', 'using', 'with'))
            
        letters = list('_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        numbers = list('0123456789')
        
        begChars = letters
        endChars = letters + numbers
        
        self.assertRaises(TypeError, st_isvarname, 1) # arg needs to be str
        
        self.assertTrue(all(not st_isvarname(r) for r in reserved))
        self.assertFalse(st_isvarname('str10')) # also reserved
        self.assertFalse(st_isvarname('6name')) # must start with underscore or letter
        self.assertFalse(st_isvarname('/name')) # cannot contain punctuation
        self.assertFalse(st_isvarname('name'*8 + 'z')) # must must be <= 32 characters long
        self.assertFalse(st_isvarname('')) # must must be > 0 characters long
        
        for i in range(50):
            nameLen = random.randint(0,31)
            nameList = [random.choice(begChars)] + [random.choice(endChars) for i in range(nameLen)]
            name = "".join(nameList)
            self.assertTrue(st_isvarname(name))
        
    def test_st_local(self):
        self.assertRaises(TypeError, st_local, "a", "b", "c") # too many arguments
        self.assertRaises(TypeError, st_local) # too few arguments
        self.assertRaises(TypeError, st_local, 0) # arguments must be str
        self.assertRaises(TypeError, st_local, 'localA', 0) # arguments must be str
        self.assertRaises(ValueError, st_local, ".&*") # malformed name
        self.assertRaises(ValueError, st_local, ".&*", "set value") # malformed name
        
        self.assertEqual(st_local("noSuchLocal"), "")
        self.assertEqual(st_local("localA"), "some local")
        
        # other tests through tearDown and .ado
        
    def test_st_matrix_el(self): # not in mata
        self.assertRaises(TypeError, st_matrix_el, "matA", 0, 0, 0, 0) # too many arguments
        self.assertRaises(TypeError, st_matrix_el, "matA", 0) # too few arguments
        self.assertRaises(TypeError, st_matrix_el, "matA", 0, '1') # 2nd & 3rd args must be int
        self.assertRaises(TypeError, st_matrix_el, "matA", 0, 0, '1') # last args must be numeric
        self.assertRaises(TypeError, st_matrix_el, 0, 0, '1') # 1st arg must be str
        self.assertRaises(ValueError, st_matrix_el, "not_a_matrix", 0, 0) # not a matrix name; retrieving
        self.assertRaises(ValueError, st_matrix_el, "not_a_matrix", 0, 0, 0) # not a matrix name; setting
        self.assertRaises(IndexError, st_matrix_el, "matA", 0, 4) # col index out of range; retrieving
        self.assertRaises(IndexError, st_matrix_el, "matA", 0, -5) # col index out of range; retrieving
        self.assertRaises(IndexError, st_matrix_el, "matA", 7, 0) # row index out of range; retrieving
        self.assertRaises(IndexError, st_matrix_el, "matA", -8, 0) # row index out of range; retrieving
        self.assertRaises(IndexError, st_matrix_el, "matA", 0, 4, 0) # col index out of range; setting
        self.assertRaises(IndexError, st_matrix_el, "matA", 0, -5, 0) # col index out of range; setting
        self.assertRaises(IndexError, st_matrix_el, "matA", 7, 0, 0) # row index out of range; setting
        self.assertRaises(IndexError, st_matrix_el, "matA", -8, 0, 0) # row index out of range; setting
        
        # getting
        self.assertEqual(st_matrix_el('matA', 0, 0), 4749)
        self.assertEqual(st_matrix_el('matA', -1, -1), 2)
        self.assertEqual(st_matrix_el('matA', 1, 2), mvs[0])
        
        # setting
        st_matrix_el('matB', 0, 0, 10000)
        st_matrix_el('matB', 0, 1, mvs[0])
        st_matrix_el('matB', 0, 2, mvs[11])
        st_matrix_el('matB', 0, 3, None)
        
        self.assertEqual(st_matrix_el('matB', 0, 0), 10000)
        self.assertEqual(st_matrix_el('matB', 0, 1), mvs[0])
        self.assertEqual(st_matrix_el('matB', 0, 2), mvs[11])
        self.assertEqual(st_matrix_el('matB', 0, 3), mvs[0])
        
        # replace values
        for i in range(4):
            st_matrix_el('matB', 0, i, st_matrix_el('matA', 0, i))
            self.assertEqual(st_matrix_el('matB', 0, i), st_matrix_el('matA', 0, i))
        
    def test_st_nobs(self):
        self.assertEqual(st_nobs(), 74)
        
    def test_st_numscalar(self):
        self.assertRaises(TypeError, st_numscalar, "a", 0, 0) # too many arguments
        self.assertRaises(TypeError, st_numscalar) # too few arguments
        self.assertRaises(TypeError, st_numscalar, 0) # 1st arg must be str
        self.assertRaises(TypeError, st_numscalar, 'scalarA', "0") # 2nd argument must be int
        self.assertRaises(ValueError, st_numscalar, ".&*") # malformed name
        self.assertRaises(ValueError, st_numscalar, ".&*", 0) # malformed name
        self.assertRaises(ValueError, st_numscalar, "noSuchScalar") # non-existant scalar
        
        self.assertEqual(st_numscalar("scalarA"), 123456)
        self.assertEqual(st_numscalar("scalarB"), mvs[0])
        self.assertEqual(st_numscalar("scalarC"), mvs[7])
        
        # other testing through tearDown and .ado
        
    def test_st_nvar(self):
        self.assertEqual(st_nvar(), 12)
        
    def test_st_rows(self): # not in mata
        self.assertRaises(TypeError, st_rows, 0) # argument needs to be str
        self.assertRaises(TypeError, st_rows, "matA", 0) # only one argument allowed
    
        self.assertEqual(st_rows("matA"), 7)
        self.assertEqual(st_rows("noSuchMatrix"), 0)
        
    def test__st_sdata(self):
        self.assertRaises(TypeError, _st_sdata, 0, 0, 0) # too many arguments
        self.assertRaises(TypeError, _st_sdata, 0) # too few arguments
        self.assertRaises(TypeError, _st_sdata, "0", 0) # 1st 2 args must be int
        self.assertRaises(TypeError, _st_sdata, 0, "0") # 1st 2 args must be int
        self.assertRaises(TypeError, _st_sdata, 0, 1) # Stata variable is not numeric
        self.assertRaises(IndexError, _st_sdata, 0, 12) # var num out of range
        self.assertRaises(IndexError, _st_sdata, 0, -13) # var num out of range
        self.assertRaises(IndexError, _st_sdata, 74, 0) # obs num out of range
        self.assertRaises(IndexError, _st_sdata, -75, 0) # obs num out of range
        
        self.assertEqual(_st_sdata(0, 0), "AMC Concord")
        self.assertEqual(_st_sdata(-1, 0), "Volvo 260")
        self.assertEqual(_st_sdata(0, -12), "AMC Concord")
        
    def test_st_sdata(self):
        self.assertRaises(TypeError, st_sdata, "4", "ma") # 1st arg should be int or iterable of int
        self.assertRaises(TypeError, st_sdata, 4, None) # 2nd arg should be int, str or iterable of int or str
        self.assertRaises(TypeError, st_sdata, 4) # too few args
        self.assertRaises(TypeError, st_sdata, 4, "ma", 1000000) # too many args
        self.assertRaises(TypeError, st_sdata, 4, "pr") # "price" is not string
        self.assertRaises(TypeError, st_sdata, 4, "ma pr ma") # "price" is not string
        self.assertRaises(TypeError, st_sdata, 4, 1) # "price" is not string
        self.assertRaises(TypeError, st_sdata, 4, (0,1,2)) # "price" is not string
        self.assertRaises(IndexError, st_sdata, 0, 12) # var num out of range
        self.assertRaises(IndexError, st_sdata, 0, -13) # var num out of range
        self.assertRaises(IndexError, st_sdata, 74, 0) # obs num out of range
        self.assertRaises(IndexError, st_sdata, -75, 0) # obs num out of range
        
        self.assertEqual(st_sdata(0, 0), [["AMC Concord"]])
        self.assertEqual(st_sdata(-1, 0), [["Volvo 260"]])
        self.assertEqual(st_sdata(0, -12), [["AMC Concord"]])
        
        output = [['AMC Concord'], ['AMC Pacer'], ['AMC Spirit'], 
             ['Buick Century'], ['Buick Electra'], ['Buick LeSabre'], 
             ['Buick Opel'], ['Buick Regal'], ['Buick Riviera'], 
             ['Buick Skylark'], ['Cad. Deville'], ['Cad. Eldorado']]
        self.assertEqual(st_sdata(range(12), 0), output)
        
        tripleOutput = [o*3 for o in output]
        self.assertEqual(st_sdata(range(12), (0, -12, 0)), tripleOutput)
        self.assertEqual(st_sdata(range(12), (-12, "ma ma")), tripleOutput)
        self.assertEqual(st_sdata(range(12), (-12, "ma", "ma")), tripleOutput)
        
    def test__st_sstore(self):
        self.assertRaises(TypeError, _st_sstore, 0, 0) # too few arguemtns
        self.assertRaises(TypeError, _st_sstore, 0, 0, 0, 0) # too many arguemtns
        self.assertRaises(TypeError, _st_sstore, 'blah', 0, 'a car') # row must be int
        self.assertRaises(TypeError, _st_sstore, 0, 'blah', 'a car') # col must be int
        self.assertRaises(TypeError, _st_sstore, 0, 0, 1) # set value must be str
        self.assertRaises(TypeError, _st_sstore, 0, 1, 'a car') # targeted Stata variable is not string
        self.assertRaises(IndexError, _st_sstore, 0, 12, 'blah') # var num out of range
        self.assertRaises(IndexError, _st_sstore, 0, -13, 'blah') # var num out of range
        self.assertRaises(IndexError, _st_sstore, 74, 0, 'blah') # obs num out of range
        self.assertRaises(IndexError, _st_sstore, -75, 0, 'blah') # obs num out of range
        
        # set values
        _st_sstore(0, 0, "Jalopy")
        _st_sstore(-1, -12, "Car X")
        
        # test
        self.assertEqual(_st_sdata(0, 0), "Jalopy")
        self.assertEqual(_st_sdata(73, 0), "Car X")
        
        # replace
        _st_sstore(0, 0, self.data[0][0])
        _st_sstore(73, 0, self.data[73][0])
        
        # test the replacement
        self.assertEqual(_st_sdata(0, 0), 'AMC Concord')
        self.assertEqual(_st_sdata(73, 0), 'Volvo 260')
        
    def test_st_sstore(self):
        self.assertRaises(TypeError, st_sstore, "4", "ma", "blah") # 1st arg should be int or iterable of int
        self.assertRaises(TypeError, st_sstore, 4, None, "blah") # 2nd arg should be int, str or iterable of int or str
        self.assertRaises(TypeError, st_sstore, 4, 0) # too few args
        self.assertRaises(TypeError, st_sstore, 4, "ma", "blah", "blah") # too many args
        self.assertRaises(TypeError, st_sstore, 4, "pr", "blah") # "price" is not string
        self.assertRaises(TypeError, st_sstore, 4, "ma pr ma", [["blah", 1, "blah"]]) # "price" is not string
        self.assertRaises(TypeError, st_sstore, 4, 1, "blah") # "price" is not string
        self.assertRaises(TypeError, st_sstore, 4, (0,1,2), [["blah", 1, 2]]) # "price" is not string
        self.assertRaises(IndexError, st_sstore, 0, 12, 'blah') # var num out of range
        self.assertRaises(IndexError, st_sstore, 0, -13, 'blah') # var num out of range
        self.assertRaises(IndexError, st_sstore, 74, 0, 'blah') # obs num out of range
        self.assertRaises(IndexError, st_sstore, -75, 0, 'blah') # obs num out of range
        
        # set values
        st_sstore(range(12), 0, [str(i) for i in range(12)])
        st_sstore(range(-12,0,1), (0, "ma", "ma"), 
            [["{}_{}".format(i,j) for j in range(3)] for i in range(12)]) # three assignments on same var for each ob; last will stick
        
        # test
        self.assertEqual(st_sdata(range(12), 0), [[str(i)] for i in range(12)])
        self.assertEqual(st_sdata(range(62,74), 0), [[str(i) + "_2"] for i in range(12)])
        
        # replace
        st_sstore(range(12), 0, [row[0] for row in self.data[:12]])
        st_sstore(range(-12,0,1), "ma", [row[0] for row in self.data[62:]])
        
        # test the replacement
        self.assertEqual(st_sdata(range(74), 0), [[row[0]] for row in self.data])
        
    def test__st_store(self):
        self.assertRaises(TypeError, _st_store, 0, 1, 0, 0) # too many arguments
        self.assertRaises(TypeError, _st_store, 0, 1) # too few arguments
        self.assertRaises(TypeError, _st_store, "0", 1, 1) # 1st 2 args must be int
        self.assertRaises(TypeError, _st_store, 0, "1", 1) # 1st 2 args must be int
        self.assertRaises(TypeError, _st_store, 0, 1, 'a car') # set value must be numeric
        self.assertRaises(TypeError, _st_store, 0, 0, 0) # targeted Stata variable is not numeric
        self.assertRaises(IndexError, _st_store, 0, 12, 0) # var num out of range
        self.assertRaises(IndexError, _st_store, 0, -13, 0) # var num out of range
        self.assertRaises(IndexError, _st_store, 74, 0, 0) # obs num out of range
        self.assertRaises(IndexError, _st_store, -75, 0, 0) # obs num out of range
        
        # be sure that current values are different from values that will be set
        self.assertNotEqual(_st_data(0, 1), 100)
        self.assertNotEqual(_st_data(1, 2), mvs[0])
        self.assertNotEqual(_st_data(2, 3), mvs[5])
        
        # set values
        _st_store(0, 1, 100)
        _st_store(1, 2, None)
        _st_store(2, 3, mvs[5])
        
        # test
        self.assertEqual(_st_data(0, 1), 100)
        self.assertEqual(_st_data(1, 2), mvs[0])
        self.assertEqual(_st_data(2, 3), mvs[5])
        
        # replace
        _st_store(0, 1, self.data[0][1])
        _st_store(1, 2, self.data[1][2])
        _st_store(2, 3, self.data[2][3])
        
        # test the replacement
        self.assertEqual(_st_data(0, 1), self.data[0][1])
        self.assertEqual(_st_data(1, 2), self.data[1][2])
        self.assertEqual(_st_data(2, 3), self.data[2][3])
        
    def test_st_store(self):
        self.assertRaises(TypeError, st_store, "4", "pr", 12345) # 1st arg should be int or iterable of int
        self.assertRaises(TypeError, st_store, 4, None) # 2nd arg should be int, str or iterable of int or str
        self.assertRaises(TypeError, st_store, 4, 0) # too few args
        self.assertRaises(TypeError, st_store, 4, "pr", 12345, 12345) # too many args
        self.assertRaises(TypeError, st_store, 4, "ma", "blah") # "make" is not nuemric
        self.assertRaises(TypeError, st_store, 4, "ma pr ma", [["blah", 1, "blah"]]) # "make" is not nuemric
        self.assertRaises(TypeError, st_store, 4, 0, 1) # "make" is not nuemric
        self.assertRaises(TypeError, st_store, 4, (0,1,2), [["blah", 1, 2]]) # "make" is not nuemric
        self.assertRaises(IndexError, st_store, 0, 12, 0) # var num out of range
        self.assertRaises(IndexError, st_store, 0, -13, 0) # var num out of range
        self.assertRaises(IndexError, st_store, 74, 1, 0) # obs num out of range
        self.assertRaises(IndexError, st_store, -75, 1, 0) # obs num out of range
        
        # set values
        st_store(range(0,30,2), (1, "mpg rep", 4, "tr"),
            [[i*10 + j for j in range(1,6)] for i in range(0,30,2)])
        st_store(range(27), -1, mvs)
        
        # test
        self.assertEqual(st_data(range(0,30,2), (1, "mpg rep", 4, "tr")),
            [[i*10 + j for j in range(1,6)] for i in range(0,30,2)])
        self.assertEqual(st_data(range(27), 11), [[mv] for mv in mvs])
        
        # replace
        st_store(range(0,30,2), (1, "mpg rep", 4, "tr"),
            [self.data[i][1:6] for i in range(0,30,2)])
        st_store(range(27), -1, [row[11] for row in self.data[:27]])
        
        # test the replacement
        self.assertEqual(st_data(range(74), (1, "mpg rep", 4, "tr")),
            [row[1:6] for row in self.data])
        self.assertEqual(st_data(range(74), 11), [[row[11]] for row in self.data])
        
    def test_st_varindex(self):
        self.assertRaises(TypeError, st_varindex, 0) # should be str
        self.assertRaises(ValueError, st_varindex, 'm', 1) # ambiguous
        self.assertRaises(ValueError, st_varindex, 'xx') # no such variable
        self.assertRaises(ValueError, st_varindex, 'mpgmpg', 1) # no such variable
        self.assertRaises(ValueError, st_varindex, 'mpz') # no such variable
        self.assertRaises(ValueError, st_varindex, '') # empty string not allowed
        self.assertRaises(ValueError, st_varindex, 'mp&g') # cannot be Stata var name
        self.assertRaises(ValueError, st_varindex, 'mp') # need to have 2nd arg truthy for abbrevs
        self.assertRaises(ValueError, st_varindex, 'mp', False) # need to have 2nd arg truthy for abbrevs
        self.assertRaises(ValueError, st_varindex, 'mp', 0) # need to have 2nd arg truthy for abbrevs
    
        abbrevs = ['ma', 'pr', 'mp', 're', 'he', 'tr', 'we', 'le', 'tu', 'di', 'ge', 'fo']
        self.assertTrue(all(st_varindex(x, 1) == i for x,i in zip(abbrevs, range(12))))
        self.assertTrue(all(st_varindex(x, True) == i for x,i in zip(abbrevs, range(12))))
        
    def test_st_varname(self):
        self.assertRaises(TypeError, st_varname, "m") # should be int
        self.assertRaises(TypeError, st_varname, 1.2) # should be int
        self.assertRaises(TypeError, st_varname) # too few args
        self.assertRaises(TypeError, st_varname, 0, 1) # too many args
    
        names = ['make', 'price', 'mpg', 'rep78', 'headroom', 'trunk', 
                   'weight', 'length', 'turn', 'displacement', 'gear_ratio', 
                   'foreign']
        self.assertEqual(names, [st_varname(i) for i in range(st_nvar())])
        
    def tearDown(self):        
        st_local("localB", "the local B")
        st_local("localC", "the local C")
        
        st_global("globalB", "the global B")
        st_global("globalC", "the global C")
        
        st_numscalar("scalarD", 789)
        st_numscalar("scalarE", mvs[13])
        st_numscalar("scalarF", None)
        st_numscalar("scalarG", mvs[13].value)


class TestMatrix(unittest.TestCase):
    def setUp(self):
        self.output = ""
        self.stdout = sys.stdout
        self.testOut = makeCapture(self)
        self.m = st_Matrix("matA")
        self.maxDiff = None
    
    def test___init__(self):
        self.assertRaises(ValueError, st_Matrix, 'noSuchMatrix')
    
        m = st_Matrix('matA')
        self.assertEqual(m._nRows, 7)
        self.assertEqual(m._nCols, 4)
        self.assertEqual(m._matname, 'matA')
        self.assertEqual(m._fmt, "%10.0g")
        self.assertEqual(m._rowNums, tuple(range(7)))
        self.assertEqual(m._colNums, tuple(range(4)))
    
        m2 = m[::2, ::2]
        self.assertEqual(m2._nRows, 4)
        self.assertEqual(m2._nCols, 2)
        self.assertEqual(m2._matname, 'matA')
        self.assertEqual(m2._fmt, "%10.0g")
        self.assertEqual(m2._rowNums, (0,2,4,6))
        self.assertEqual(m2._colNums, (0,2))
    
        m3 = m[(0,1,2,0,1,2), (1,3,1,3)]
        self.assertEqual(m3._nRows, 6)
        self.assertEqual(m3._nCols, 4)
        self.assertEqual(m3._matname, 'matA')
        self.assertEqual(m3._fmt, "%10.0g")
        self.assertEqual(m3._rowNums, (0,1,2,0,1,2))
        self.assertEqual(m3._colNums, (1,3,1,3))
        
    def test___iter__(self):
        m = self.m
        it = iter(m)
        self.assertTrue(isinstance(it, GeneratorType))
        self.assertEqual(list(it), 
            [tuple(m.get(i,j) for j in range(m._nCols)) 
             for i in range(m._nRows)])
        
        m2 = self.m[::2, ::2]
        it = iter(m2)
        self.assertTrue(isinstance(it, GeneratorType))
        self.assertEqual(list(it), 
            [tuple(m2.get(i,j) for j in range(m2._nCols)) 
             for i in range(m2._nRows)])
        
    def test_format(self):
        self.assertEqual(self.m._fmt, "%10.0g")
        
        self.assertRaises(TypeError, self.m.format, 10.0) # arg must be str
        self.assertRaises(ValueError, self.m.format, "%10s") # arg must be valid numerical fmt
        self.assertRaises(ValueError, self.m.format, "%10g") # arg must be valid numerical fmt
        
        self.m.format("%12.0g")
        self.assertEqual(self.m._fmt, "%12.0g")
        mRepr = ('\n{txt}matA[7,4]\n' + 
                '{txt}             c0           c1           c2           c3\n' + 
                '{txt}r0{res}         4749           17            3            3\n' + 
                '{txt}r1{res}         3799           22            .            3\n' + 
                '{txt}r2{res}         4816           20            3          4.5\n' + 
                '{txt}r3{res}         7827           15            4            4\n' + 
                '{txt}r4{res}         5788           18            3            4\n' + 
                '{txt}r5{res}         4453           26            .            3\n' + 
                '{txt}r6{res}         5189           20            3            2\n')
        
        sys.stdout = self.testOut
        self.m.list()
        sys.stdout = self.stdout
        self.assertEqual(self.output, mRepr)
        self.output = ""
        
        
        self.m.format("%tq")
        self.assertEqual(self.m._fmt, "%tq")
        mRepr = ('\n{txt}matA[7,4]\n' + 
                '{txt}       c0     c1     c2     c3\n' + 
                '{txt}r0{res} 3147q2 1964q2 1960q4 1960q4\n' + 
                '{txt}r1{res} 2909q4 1965q3      . 1960q4\n' + 
                '{txt}r2{res} 3164q1 1965q1 1960q4 1961q1\n' + 
                '{txt}r3{res} 3916q4 1963q4 1961q1 1961q1\n' + 
                '{txt}r4{res} 3407q1 1964q3 1960q4 1961q1\n' + 
                '{txt}r5{res} 3073q2 1966q3      . 1960q4\n' + 
                '{txt}r6{res} 3257q2 1965q1 1960q4 1960q3\n')        
        
        sys.stdout = self.testOut
        self.m.list()
        sys.stdout = self.stdout
        self.assertEqual(self.output, mRepr)
        self.output = ""
        
        
        self.m.format("%10.0g")
        self.assertEqual(self.m._fmt, "%10.0g")
        
    def test_list(self):
        mRepr = ('\n' + 
                 '{txt}matA[7,4]\n'
                 '{txt}           c0         c1         c2         c3\n' + 
                 '{txt}r0{res}       4749         17          3          3\n' + 
                 '{txt}r1{res}       3799         22          .          3\n' + 
                 '{txt}r2{res}       4816         20          3        4.5\n' + 
                 '{txt}r3{res}       7827         15          4          4\n' + 
                 '{txt}r4{res}       5788         18          3          4\n' + 
                 '{txt}r5{res}       4453         26          .          3\n' + 
                 '{txt}r6{res}       5189         20          3          2\n')
        
        sys.stdout = self.testOut
        self.m.list()
        sys.stdout = self.stdout
        self.assertEqual(self.output, mRepr)
        self.output = ""
        
    def test_toList(self):
        mList = [[4749.0, 17.0, 3.0, 3.0], 
                 [3799.0, 22.0, mvs[0], 3.0], 
                 [4816.0, 20.0, 3.0, 4.5], 
                 [7827.0, 15.0, 4.0, 4.0], 
                 [5788.0, 18.0, 3.0, 4.0], 
                 [4453.0, 26.0, mvs[0], 3.0], 
                 [5189.0, 20.0, 3.0, 2.0]]
             
        self.assertEqual(self.m.toList(), mList)
        
    def test___repr__(self):
        mRepr = ('\n' + 
                 '{txt}matA[7,4]\n' + 
                 '{txt}           c0         c1         c2         c3\n' + 
                 '{txt}r0{res}       4749         17          3          3\n' + 
                 '{txt}r1{res}       3799         22          .          3\n' + 
                 '{txt}r2{res}       4816         20          3        4.5\n' + 
                 '{txt}r3{res}       7827         15          4          4\n' + 
                 '{txt}r4{res}       5788         18          3          4\n' + 
                 '{txt}r5{res}       4453         26          .          3\n' + 
                 '{txt}r6{res}       5189         20          3          2')
              
        self.assertEqual(self.m.__repr__(), mRepr)
        
    def test_get(self):
        self.assertRaises(TypeError, self.m.get, 1, "1") # both args must be int
        self.assertRaises(TypeError, self.m.get, "1", 1) # both args must be int
        self.assertRaises(TypeError, self.m.get, 1, 1.1) # both args must be int
        self.assertRaises(TypeError, self.m.get, 1, 1.1, 1.1) # too many args
        self.assertRaises(TypeError, self.m.get, 1) # too few args
    
        mList = [[4749.0, 17.0, 3.0, 3.0], 
                 [3799.0, 22.0, mvs[0], 3.0], 
                 [4816.0, 20.0, 3.0, 4.5], 
                 [7827.0, 15.0, 4.0, 4.0], 
                 [5788.0, 18.0, 3.0, 4.0], 
                 [4453.0, 26.0, mvs[0], 3.0], 
                 [5189.0, 20.0, 3.0, 2.0]]
                 
        for r in range(7):
            for c in range(4):
                self.assertEqual(self.m.get(r,c), mList[r][c])
                
    def test_rows(self):
        self.assertRaises(AttributeError, setattr, self.m, "rows", (0,2,4))
        
        self.assertEqual(self.m.rows, (0,1,2,3,4,5,6))
        self.assertEqual(self.m[::2, ].rows, (0,2,4,6))
        
    def test_cols(self):
        self.assertRaises(AttributeError, setattr, self.m, "cols", (0,2))
        
        self.assertEqual(self.m.cols, (0,1,2,3))
        self.assertEqual(self.m[:, ::2].cols, (0,2))
        
    def test_nRows(self):
        self.assertRaises(AttributeError, setattr, self.m, "nRows", 10)
        
        self.assertEqual(self.m.nRows, 7)
        self.assertEqual(self.m[::2, ].nRows, 4)
    
    def test_nCols(self):
        self.assertRaises(AttributeError, setattr, self.m, "nCols", 10)
        
        self.assertEqual(self.m.nCols, 4)
        self.assertEqual(self.m[:, ::2 ].nCols, 2)
    

    def test___eq__(self):
        self.assertFalse(self.m == self.m.toList())
        
        self.assertEqual(self.m, st_Matrix("matB"))
        
        m2 = st_Matrix("matB")
        
        m2[1,1] = mvs[-1]
        self.assertFalse(self.m == m2)
        
        m2[:, :] = [[mvs[0], mvs[0], mvs[0], mvs[0]], 
                    [mvs[1], mvs[2], mvs[3], mvs[4]], 
                    [mvs[1], mvs[2], mvs[3], mvs[4]], 
                    [mvs[1], mvs[2], mvs[3], mvs[4]], 
                    [mvs[1], mvs[2], mvs[3], mvs[4]], 
                    [mvs[1], mvs[2], mvs[3], mvs[4]], 
                    [mvs[0], mvs[0], mvs[0], mvs[0]]]
        
        self.assertEqual(m2.toList(), 
            [[mvs[0], mvs[0], mvs[0], mvs[0]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[0], mvs[0], mvs[0], mvs[0]]])

        m3 = m2[1:, 1:]
        self.assertFalse(m2 == m3)
        self.assertEqual(m2, m2[(6,1,2,3,4,5,0), ])
        self.assertFalse(m2 == m2[(0,6,1,2,3,4,5), ])
        

        m2[:, :] = self.m
        
        self.assertEqual(m2, self.m)
    
    def test__checkIndex(self):
        checkIndex = self.m._checkIndex
        self.assertRaises(TypeError, checkIndex, range(4), "a") # last arg should be slice, int, or iterable of int
        self.assertRaises(TypeError, checkIndex, range(4), 1.1) # last arg should be slice, int, or iterable of int
        self.assertRaises(TypeError, checkIndex, range(4), (1, 2.1, 3.0)) # last arg should be slice, int, or iterable of int
        self.assertRaises(IndexError, checkIndex, range(4), 4) # last arg too large by 1
        self.assertRaises(IndexError, checkIndex, range(4), -5) # last arg too small by 1
        self.assertRaises(TypeError, checkIndex, range(10), slice("blah", 8, 2)) # str in slice raises error
        
        self.assertEqual(checkIndex(range(44), None), range(44))
        self.assertEqual(checkIndex(range(44), (i for i in range(0,40,2))), tuple(i for i in range(0,40,2)))
        self.assertEqual(checkIndex(range(44), (1,2,10,20)), (1,2,10,20))
        self.assertEqual(checkIndex(range(44), 14), (14,))
        self.assertEqual(checkIndex(range(44), -3), (41,))
        self.assertEqual(checkIndex(range(44), slice(2,None,2)), range(2,44,2))
    
    def test___getitem__(self):
        getItem = self.m.__getitem__
        self.assertRaises(TypeError, getItem, (1,1), (2,2)) # too many args
        self.assertRaises(TypeError, getItem) # too few args
        self.assertRaises(TypeError, getItem, 1) # arg should be tuple
        self.assertRaises(TypeError, getItem, (1,1,1) ) # arg should be two- or two-item tuple
        self.assertRaises(TypeError, getItem, (1, 2.5) ) # tuple entries should be int, slice, or iterable of int
        self.assertRaises(TypeError, getItem, (1.5, 2) ) # tuple entries should be int, slice, or iterable of int
        self.assertRaises(TypeError, getItem, (1, "str iterable") ) # tuple entries should be int, slice, or iterable of int
        
        self.assertEqual(getItem((1,1)).toList(), [[st_matrix_el("matA", 1, 1)]])
        self.assertEqual(self.m[1,1].toList(), [[st_matrix_el("matA", 1, 1)]])
        
        self.assertEqual(getItem((slice(None), slice(None))).toList(), [[st_matrix_el("matA", i, j) for j in range(4)] for i in range(7)])
        self.assertEqual(self.m[:,:].toList(), [[st_matrix_el("matA", i, j) for j in range(4)] for i in range(7)])
        
        self.assertEqual(
            getItem(((1,3,5,0,2,4), (1,3,0,2))).toList(), 
            [[st_matrix_el("matA", i, j) for j in (1,3,0,2)] for i in (1,3,5,0,2,4)])
        self.assertEqual(
            self.m[(1,3,5,0,2,4), (1,3,0,2)].toList(), 
            [[st_matrix_el("matA", i, j) for j in (1,3,0,2)] for i in (1,3,5,0,2,4)])
        
        self.assertEqual(
            getItem(((0,2,4,0,2,4), (0,2,0,2))).toList(), 
            [[st_matrix_el("matA", i, j) for j in (0,2,0,2)] for i in (0,2,4,0,2,4)])
        self.assertEqual(
            self.m[(0,2,4,0,2,4), (0,2,0,2)].toList(), 
            [[st_matrix_el("matA", i, j) for j in (0,2,0,2)] for i in (0,2,4,0,2,4)])
        
        self.assertEqual(
            getItem((slice(0,40,2), slice(0,40,2))).toList(), 
            [[st_matrix_el("matA", i, j) for j in (0,2)] for i in (0,2,4,6)])
        self.assertEqual(
            self.m[:40:2, :40:2].toList(), 
            [[st_matrix_el("matA", i, j) for j in (0,2)] for i in (0,2,4,6)])
        
        m2 = self.m[(0,2,4,1,3,5,1,3,5,0,2,4,6), (0,2,2,0,1,3,3,1)]
        self.assertTrue(isinstance(m2, st_Matrix))
        self.assertEqual(m2[::2,::2][(0,3,5,2,1,4,6), (0,2,1,3)], self.m)
        
    def test___setitem__(self):
        setItem = self.m.__setitem__
    
        self.assertRaises(ValueError, setItem, 1, 1) # 1st arg needs to be tuple
        self.assertRaises(ValueError, setItem, (1, 1, 1), 1) # 1st arg needs to be one- or two-item tuple
        self.assertRaises(TypeError, setItem, (1,1)) # too few args
        self.assertRaises(TypeError, setItem, (1,1), 2, 2 ) # too many args
        self.assertRaises(TypeError, setItem, (1, "nope"), 1) # elements of tuple should be int, slice, or iterable of int
        self.assertRaises(TypeError, setItem, (1.5, 1), 1) # elements of tuple should be int, slice, or iterable of int
    
        self.assertRaises(ValueError, setItem, (1,1), (2,2) ) # 2nd arg not right shape
        self.assertRaises(ValueError, setItem, (1,1), [[2, 2]] ) # 2nd arg not right shape
        self.assertRaises(ValueError, setItem, ((1,2,3),(1,2)), [[2, 2, 2]*2] ) # 2nd arg not right shape
        self.assertRaises(ValueError, setItem, ((1,2,3),(1,2)), [2] ) # 2nd arg not right shape
        self.assertRaises(ValueError, setItem, ((1,2,3),(1,2)), [[2,2,2,2,2,2]] ) # 2nd arg not right shape
    
        m2 = st_Matrix("matB")
        
        m2[::2, ::2] = [[None]*2]*4
        
        self.assertEqual(m2.toList(), 
            [[mvs[0], 17.0, mvs[0], 3.0], 
             [3799.0, 22.0, mvs[0], 3.0], 
             [mvs[0], 20.0, mvs[0], 4.5], 
             [7827.0, 15.0, 4.0, 4.0], 
             [mvs[0], 18.0, mvs[0], 4.0], 
             [4453.0, 26.0, mvs[0], 3.0], 
             [mvs[0], 20.0, mvs[0], 2.0]])
             
        m2[1:6, 1] = [mvs[1]]*5
        
        self.assertEqual(m2.toList(), 
            [[mvs[0], 17.0, mvs[0], 3.0], 
             [3799.0, mvs[1], mvs[0], 3.0], 
             [mvs[0], mvs[1], mvs[0], 4.5], 
             [7827.0, mvs[1], 4.0, 4.0], 
             [mvs[0], mvs[1], mvs[0], 4.0], 
             [4453.0, mvs[1], mvs[0], 3.0], 
             [mvs[0], 20.0, mvs[0], 2.0]])
             
        m2[1:6, 0] = [[mvs[1]]]*5
        
        self.assertEqual(m2.toList(), 
            [[mvs[0], 17.0, mvs[0], 3.0], 
             [mvs[1], mvs[1], mvs[0], 3.0], 
             [mvs[1], mvs[1], mvs[0], 4.5], 
             [mvs[1], mvs[1], 4.0, 4.0], 
             [mvs[1], mvs[1], mvs[0], 4.0], 
             [mvs[1], mvs[1], mvs[0], 3.0], 
             [mvs[0], 20.0, mvs[0], 2.0]])
             
        m2[(1,2,3,4,5), (1,2,3)] = [[mvs[2], mvs[3], mvs[4]]]*5
        
        self.assertEqual(m2.toList(), 
            [[mvs[0], 17.0, mvs[0], 3.0], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[1], mvs[2], mvs[3], mvs[4]], 
             [mvs[0], 20.0, mvs[0], 2.0]])

        m2[:, :] = self.m
        
        self.assertEqual(m2, self.m)


class TestView(unittest.TestCase):
    def setUp(self):
        self.output = ""
        self.stdout = sys.stdout
        self.testOut = makeCapture(self)
        self.v = st_View()
        self.maxDiff = None
        
    def test___init__(self):
        self.assertEqual(self.v._nRows, 74)
        self.assertEqual(self.v._nObs, 74)
        self.assertEqual(self.v._nCols, 12)
        self.assertEqual(self.v._nVar, 12)
        self.assertEqual(self.v._getters, [_st_sdata] + [_st_data]*11)
        self.assertEqual(self.v._setters, [_st_sstore] + [_st_store]*11)
        self.assertEqual(self.v._formats, ["%11s"] + ["%9.0g"]*11)
        self.assertEqual(self.v._rowNums, tuple(range(74)))
        self.assertEqual(self.v._colNums, tuple(range(12)))
        
        newView = self.v[::2, ::2]
        self.assertEqual(newView._nRows, 37)
        self.assertEqual(newView._nObs, 37)
        self.assertEqual(newView._nCols, 6)
        self.assertEqual(newView._nVar, 6)
        self.assertEqual(newView._getters, [_st_sdata] + [_st_data]*5)
        self.assertEqual(newView._setters, [_st_sstore] + [_st_store]*5)
        self.assertEqual(newView._formats, ["%11s"] + ["%9.0g"]*5)
        self.assertEqual(newView._rowNums, tuple(range(0,74,2)))
        self.assertEqual(newView._colNums, tuple(range(0,12,2)))
        
        newView = self.v[::4, (0,1,2,0,1,2)]
        self.assertEqual(newView._nRows, 19)
        self.assertEqual(newView._nObs, 19)
        self.assertEqual(newView._nCols, 6)
        self.assertEqual(newView._nVar, 3)
        self.assertEqual(newView._getters, ([_st_sdata] + [_st_data]*2)*2)
        self.assertEqual(newView._setters, ([_st_sstore] + [_st_store]*2)*2)
        self.assertEqual(newView._formats, (["%11s"] + ["%9.0g"]*2)*2)
        self.assertEqual(newView._rowNums, tuple(range(0,74,4)))
        self.assertEqual(newView._colNums, (0,1,2,0,1,2))
        
    def test___iter__(self):
        v = self.v
        it = iter(v)
        self.assertTrue(isinstance(it, GeneratorType))
        self.assertEqual(list(it), 
                         [tuple(v[i,:].toList()[0]) for i in range(v._nRows)])
        
        it = iter(self.v[::2, ::2])
        self.assertTrue(isinstance(it, GeneratorType))
        self.assertEqual(list(it), 
            [tuple(v[i,::2].toList()[0]) 
             for i in range(0, v._nRows, 2)])
        
    def test_format(self):
        self.assertRaises(TypeError, self.v.format, 1) # too few args
        self.assertRaises(TypeError, self.v.format, 1, "%8.2f", 0) # too many args
        self.assertRaises(TypeError, self.v.format, 1, 8.2) # fmt should be str
        self.assertRaises(TypeError, self.v.format, (1,2), "8.2f") # column arg should be int or str
        self.assertRaises(ValueError, self.v.format, 1, "%8.8f") # not a valid format
        self.assertRaises(ValueError, self.v.format, 1, "%8s") # string fmt for non-string column
        self.assertRaises(ValueError, self.v.format, 0, "%8.2f") # non-string fmt for string column
        
    def test_list(self):
        pass
        
    def test_toList(self):
        self.assertEqual(self.v[::6,::4].toList(), 
            [['AMC Concord', 2.5, 40.0], 
             ['Buick Opel', 3.0, 34.0], 
             ['Cad. Seville', 3.0, 45.0], 
             ['Chev. Nova', 3.5, 43.0], 
             ['Ford Mustang', 2.0, 43.0], 
             ['Merc. Marquis', 3.5, 44.0], 
             ['Olds Cutlass', 4.5, 42.0], 
             ['Plym. Champ', 2.5, 37.0], 
             ['Pont. Grand Prix', 2.0, 45.0], 
             ['BMW 320i', 2.5, 34.0], 
             ['Honda Accord', 3.0, 36.0], 
             ['Toyota Celica', 2.5, 36.0], 
             ['VW Scirocco', 2.0, 36.0]])
             
        self.assertEqual(self.v[1,].toList(),
            [['AMC Pacer', 4749.0, 17.0, 3.0, 3.0, 11.0, 3350.0, 
              173.0, 40.0, 258.0, 2.5299999713897705, 0.0]])
        
    def test_get(self):
        self.assertRaises(TypeError, self.v.get, 0) # too few args
        self.assertRaises(TypeError, self.v.get, 0, 0, 0) # too many args
        self.assertRaises(TypeError, self.v.get, 0, "0") # args must be int
        self.assertRaises(TypeError, self.v.get, "0", 0) # args must be int
        self.assertRaises(TypeError, self.v.get, 0, 0.5) # args must be int
        self.assertRaises(IndexError, self.v.get, 0, 12) # 2nd arg out of range
        self.assertRaises(IndexError, self.v.get, 0, -13) # 2nd arg out of range
        self.assertRaises(IndexError, self.v.get, 74, 0) # 1st arg out of range
        self.assertRaises(IndexError, self.v.get, -75, 0) # 1st arg out of range
        
        self.assertEqual(self.v.get(0,0), "AMC Concord")
        self.assertEqual(self.v.get(1,1), 4749.0)
        self.assertTrue(abs(self.v.get(-1,-2) - 2.98) < 1e-6)
        
    def test___repr__(self):
        self.assertEqual(self.v[::6, ::4].__repr__(),
            '\n' + 
            '  {txt}obs: 13\n' + 
            ' vars:  3\n\n' +
            '{txt}             c0        c4        c8\n' + 
            '{txt} r0{res} AMC Concord       2.5        40\n' + 
            '{txt} r6{res}  Buick Opel         3        34\n' + 
            '{txt}r12{res} Cad. Sevill         3        45\n' + 
            '{txt}r18{res}  Chev. Nova       3.5        43\n' + 
            '{txt}r24{res} Ford Mustan         2        43\n' + 
            '{txt}r30{res} Merc. Marqu       3.5        44\n' + 
            '{txt}r36{res} Olds Cutlas       4.5        42\n' + 
            '{txt}r42{res} Plym. Champ       2.5        37\n' + 
            '{txt}r48{res} Pont. Grand         2        45\n' + 
            '{txt}r54{res}    BMW 320i       2.5        34\n' + 
            '{txt}r60{res} Honda Accor         3        36\n' + 
            '{txt}r66{res} Toyota Celi       2.5        36\n' + 
            '{txt}r72{res} VW Scirocco         2        36')
            
        self.assertEqual(self.v[(0,1,2,0,1,2), (0,1,2,0,1,2)].__repr__(),
            '\n' + 
            '  {txt}obs: 3 (6 rows)\n' + 
            ' vars: 3 (6 columns)\n\n' + 
            '{txt}            c0        c1        c2          c0        c1        c2\n' + 
            '{txt}r0{res} AMC Concord      4099        22 AMC Concord      4099        22\n' + 
            '{txt}r1{res}   AMC Pacer      4749        17   AMC Pacer      4749        17\n' + 
            '{txt}r2{res}  AMC Spirit      3799        22  AMC Spirit      3799        22\n' + 
            '{txt}r0{res} AMC Concord      4099        22 AMC Concord      4099        22\n' + 
            '{txt}r1{res}   AMC Pacer      4749        17   AMC Pacer      4749        17\n' + 
            '{txt}r2{res}  AMC Spirit      3799        22  AMC Spirit      3799        22')
       
    def test__checkIndex(self):
        checkIndex = self.v._checkIndex
        self.assertRaises(TypeError, checkIndex, range(4), "a") # last arg should be slice, int, or iterable of int
        self.assertRaises(TypeError, checkIndex, range(4), 1.1) # last arg should be slice, int, or iterable of int
        self.assertRaises(TypeError, checkIndex, range(4), (1, 2.1, 3.0)) # last arg should be slice, int, or iterable of int
        self.assertRaises(IndexError, checkIndex, range(4), 4) # last arg too large by 1
        self.assertRaises(IndexError, checkIndex, range(4), -5) # last arg too small by 1
        self.assertRaises(TypeError, checkIndex, range(10), slice("blah", 8, 2)) # str in slice raises error
        
        self.assertEqual(checkIndex(range(44), None), range(44))
        self.assertEqual(checkIndex(range(44), (i for i in range(0,40,2))), tuple(i for i in range(0,40,2)))
        self.assertEqual(checkIndex(range(44), (1,2,10,20)), (1,2,10,20))
        self.assertEqual(checkIndex(range(44), 14), (14,))
        self.assertEqual(checkIndex(range(44), -3), (41,))
        self.assertEqual(checkIndex(range(44), slice(2,None,2)), range(2,44,2))
    
    def test___getitem__(self):
        getItem = self.v.__getitem__
    
        self.assertRaises(TypeError, getItem) # too few arguments
        self.assertRaises(TypeError, getItem, (1,1), (1,1)) # too many arguments
        self.assertRaises(TypeError, getItem, 1) # arg should be one- or two-item tuple
        self.assertRaises(TypeError, getItem, (1,"pr")) # tuple contents should be int
        self.assertRaises(IndexError, getItem, (74,0)) # index out of range
        self.assertRaises(IndexError, getItem, (0,12)) # index out of range
        
        # repeated in test_toList
        self.assertEqual(self.v[::6,::4].toList(), 
            [['AMC Concord', 2.5, 40.0], 
             ['Buick Opel', 3.0, 34.0], 
             ['Cad. Seville', 3.0, 45.0], 
             ['Chev. Nova', 3.5, 43.0], 
             ['Ford Mustang', 2.0, 43.0], 
             ['Merc. Marquis', 3.5, 44.0], 
             ['Olds Cutlass', 4.5, 42.0], 
             ['Plym. Champ', 2.5, 37.0], 
             ['Pont. Grand Prix', 2.0, 45.0], 
             ['BMW 320i', 2.5, 34.0], 
             ['Honda Accord', 3.0, 36.0], 
             ['Toyota Celica', 2.5, 36.0], 
             ['VW Scirocco', 2.0, 36.0]])
        
        # repeated in test_toList
        self.assertEqual(self.v[1,].toList(),
            [['AMC Pacer', 4749.0, 17.0, 3.0, 3.0, 11.0, 3350.0, 
              173.0, 40.0, 258.0, 2.5299999713897705, 0.0]])
              
        self.assertEqual(self.v[(0,6,12,18,24,30,36,42,48,54,60,66,72),(0,4,8)].toList(), 
            [['AMC Concord', 2.5, 40.0], 
             ['Buick Opel', 3.0, 34.0], 
             ['Cad. Seville', 3.0, 45.0], 
             ['Chev. Nova', 3.5, 43.0], 
             ['Ford Mustang', 2.0, 43.0], 
             ['Merc. Marquis', 3.5, 44.0], 
             ['Olds Cutlass', 4.5, 42.0], 
             ['Plym. Champ', 2.5, 37.0], 
             ['Pont. Grand Prix', 2.0, 45.0], 
             ['BMW 320i', 2.5, 34.0], 
             ['Honda Accord', 3.0, 36.0], 
             ['Toyota Celica', 2.5, 36.0], 
             ['VW Scirocco', 2.0, 36.0]])
              
        self.assertEqual(self.v[(0,6,12,18,24,30,36,-32,-26,-20,-14,-8,-2),(0,-8,-4)].toList(), 
            [['AMC Concord', 2.5, 40.0], 
             ['Buick Opel', 3.0, 34.0], 
             ['Cad. Seville', 3.0, 45.0], 
             ['Chev. Nova', 3.5, 43.0], 
             ['Ford Mustang', 2.0, 43.0], 
             ['Merc. Marquis', 3.5, 44.0], 
             ['Olds Cutlass', 4.5, 42.0], 
             ['Plym. Champ', 2.5, 37.0], 
             ['Pont. Grand Prix', 2.0, 45.0], 
             ['BMW 320i', 2.5, 34.0], 
             ['Honda Accord', 3.0, 36.0], 
             ['Toyota Celica', 2.5, 36.0], 
             ['VW Scirocco', 2.0, 36.0]])
              
        self.assertEqual(self.v[(0,0,0,0,0),(0,0)].toList(), 
            [['AMC Concord', 'AMC Concord'], 
             ['AMC Concord', 'AMC Concord'], 
             ['AMC Concord', 'AMC Concord'], 
             ['AMC Concord', 'AMC Concord'], 
             ['AMC Concord', 'AMC Concord']])
    
    def test___setitem__(self):
        setitem = self.v.__setitem__
        
        varCopy = self.v.toList()
        newVals = [['a str'] + [1000*i + j for j in range(11)] for i in range(74)]
            
        self.assertRaises(ValueError, setitem, 4, [[None]*12]) # first arg needs to be row,col tuple
        self.assertRaises(ValueError, setitem, (1,2,4), [[None]*12]) # first arg needs to be row,col tuple
        
        self.assertRaises(ValueError, setitem, (slice(None,None,6),slice(None,None,4)), [row[::6] for row in varCopy[::6]]) # too few columns on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),slice(None,None,4)), [row[::3] for row in varCopy[::6]]) # too many columns on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),slice(None,None,4)), [row[::4] for row in varCopy[::9]]) # too few rows on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),slice(None,None,4)), [row[::4] for row in varCopy[::2]]) # too many rows on right
        
        self.assertRaises(ValueError, setitem, (slice(None,None,6),3), [row[3:3] for row in varCopy[::6]]) # too few columns on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),3), [row[3:5] for row in varCopy[::6]]) # too many columns on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),3), [row[3:4] for row in varCopy[::9]]) # too few rows on right
        self.assertRaises(ValueError, setitem, (slice(None,None,6),3), [row[3:4] for row in varCopy[::2]]) # too many rows on right
        
        self.assertRaises(ValueError, setitem, (6,slice(3,8,None)), [row[3:6] for row in varCopy[6:7]]) # too few columns on right
        self.assertRaises(ValueError, setitem, (6,slice(3,8,None)), [row[0:9] for row in varCopy[6:7]]) # too many columns on right
        self.assertRaises(ValueError, setitem, (6,slice(3,8,None)), [row[3:8] for row in varCopy[6:6]]) # too few rows on right
        self.assertRaises(ValueError, setitem, (6,slice(3,8,None)), [row[3:8] for row in varCopy[4:10]]) # too many rows on right
        
        self.assertRaises(TypeError, setitem, (slice(None,None), (2,3)), [row[0:2] for row in varCopy]) # type mismatch
        self.assertRaises(TypeError, setitem, (slice(None,None), (0,1)), [row[2:4] for row in varCopy]) # type mismatch
        
            # check to make sure strings are treated as indivisible objects
        self.assertRaises(ValueError, setitem, (slice(0,6), 0), "string") # make sure "string" not assigned to rows as "s" "t" "r" ...
        self.assertRaises(ValueError, setitem, (slice(0,6), 0), ("string",)) # make sure "string" not assigned to rows as "s" "t" "r" ...
        
        # edge case, not rows or cols selected; should return immediately
        self.v[1:1, :] = []
        self.assertEqual(varCopy, self.v.toList())
        self.v[:, 4:4] = []
        self.assertEqual(varCopy, self.v.toList())
        
        # single item
            # first with row and column indices
        self.v[4,5] = varCopy[4][5] + 1
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4,5] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        
        self.v[4,5] = [varCopy[4][5] + 1]
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4,5] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        
        self.v[4,5] = [[varCopy[4][5] + 1]]
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4,5] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        
            # now with row and column slices
        self.v[4:5,5:6] = [[varCopy[4][5] + 1]]
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4:5,5:6] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
           
            # assignment from generator
        self.v[4,5] = (x for x in [varCopy[4][5] + 1])
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4,5] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        
        self.v[4,5] = ((x for x in [varCopy[4][5] + 1]) for _ in range(1))
        self.assertNotEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5] + 1)
        self.v[4,5] = varCopy[4][5]
        self.assertEqual(self.v[4,5].toList()[0][0], varCopy[4][5])
        
        # single row
            # column iterable of indices
        self.v[4,(1,4,7,10)] = newVals[4][1:11:3]
        self.assertNotEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [newVals[4][1:11:3]])
        self.v[4,(1,4,7,10)] = varCopy[4][1:11:3]
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        
                # alternate form: [[1, 2, 3, ...]]
        self.v[4,(1,4,7,10)] = [newVals[4][1:11:3]]
        self.assertNotEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [newVals[4][1:11:3]])
        self.v[4,(1,4,7,10)] = [varCopy[4][1:11:3]]
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
           
            # column index slice
        self.v[4,1:11:3] = newVals[4][1:11:3]
        self.assertNotEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [newVals[4][1:11:3]])
        self.v[4,1:11:3] = varCopy[4][1:11:3]
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
            
            # assignment from generator
        self.v[4,1:11:3] = (x for x in newVals[4][1:11:3])
        self.assertNotEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [newVals[4][1:11:3]])
        self.v[4,1:11:3] = (x for x in varCopy[4][1:11:3])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        
                # alternate form: ((x for x in ...) for _ in range(1))
        self.v[4,1:11:3] = ((x for x in newVals[4][1:11:3]) for _ in range(1))
        self.assertNotEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [newVals[4][1:11:3]])
        self.v[4,1:11:3] = ((x for x in varCopy[4][1:11:3]) for _ in range(1))
        self.assertEqual(self.v[4,(1,4,7,10)].toList(), [varCopy[4][1:11:3]])
        
        # single column
            # column index, row iterable
        self.v[(1,5,9,13,17), 2] = [x[2] for x in newVals[1:18:4]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[(1,5,9,13,17), 2].toList(), [[x[2]] for x in newVals[1:18:4]])
        self.v[(1,5,9,13,17), 2] = [x[2] for x in varCopy[1:18:4]] # this also is an assingment using alternate form [[1], [2], [3], ...]
        self.assertEqual(self.v.toList(), varCopy)
        
                # alternate form: [[1], [2], [3], ...]
        self.v[(1,5,9,13,17), 2] = [[x[2]] for x in newVals[1:18:4]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[(1,5,9,13,17), 2].toList(), [[x[2]] for x in newVals[1:18:4]])
        self.v[(1,5,9,13,17), 2] =[[x[2]] for x in varCopy[1:18:4]]
        self.assertEqual(self.v.toList(), varCopy)
            
            # column index slice, row slice
        self.v[1:18:4, 2:3] = [x[2] for x in newVals[1:18:4]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[(1,5,9,13,17), 2].toList(), [[x[2]] for x in newVals[1:18:4]])
        self.v[1:18:4, 2:3] = [x[2] for x in varCopy[1:18:4]]
        self.assertEqual(self.v.toList(), varCopy)
           
            # assignment from generator
        self.v[(1,5,9,13,17), 2] = (x[2] for x in newVals[1:18:4])
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[(1,5,9,13,17), 2].toList(), [[x[2]] for x in newVals[1:18:4]])
        self.v[(1,5,9,13,17), 2] = (x[2] for x in varCopy[1:18:4])
        self.assertEqual(self.v.toList(), varCopy)
        
                # alternate form: ((x for _ in range(1)) for x in ...)
        self.v[(1,5,9,13,17), 2] = ((x[2] for _ in range(1)) for x in newVals[1:18:4])
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[(1,5,9,13,17), 2].toList(), [[x[2]] for x in newVals[1:18:4]])
        self.v[(1,5,9,13,17), 2] = ((x[2] for x in varCopy[1:18:4]))
        self.assertEqual(self.v.toList(), varCopy)
        
        # multi-row, multi-column
            # row slice, column index slice
            # stType of displacement (col 9) is int and gear_ratio (col 10) contains float,
            # so values are truncated on assignment
        self.v[::2, 1::4] = [row[2::4] for row in varCopy[1::2]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[::2, 1::4].toList(), [row[2:10:4] + [int(row[10])] for row in varCopy[1::2]])
        self.v[::2, 1::4] = [row[1::4] for row in varCopy[::2]] # restore values
        self.assertEqual(self.v.toList(), varCopy) # check that values restored
            
            # row iterable, column slice
        self.v[::2, 1:13:6] = [row[1::6] for row in varCopy[1::2]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[::2, 1::6].toList(), [row[1::6] for row in varCopy[1::2]])
        self.v[::2, 1:13:6] = [row[1::6] for row in varCopy[::2]]
        self.assertEqual(self.v.toList(), varCopy)
        
                # stType of rep78 (col 3) is int and headroom (col 4) is float,
                # so values are truncated on assignment
        self.v[::2, 3:8] = [row[4:9] for row in varCopy[1::2]]
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[::2, 3:8].toList(), [[int(row[4])] + row[5:9] for row in varCopy[1::2]])
        self.v[::2, 3:8] = [row[3:8] for row in varCopy[::2]] # restore values
        self.assertEqual(self.v.toList(), varCopy) # check that values restored
            
            # assignment from generator
        self.v[::2, 3:8] = (row[4:9] for row in varCopy[1::2])
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[::2, 3:8].toList(), [[int(row[4])] + row[5:9] for row in varCopy[1::2]])
        self.v[::2, 3:8] = (row[3:8] for row in varCopy[::2]) # restore values
        self.assertEqual(self.v.toList(), varCopy) # check that values restored
        
        self.v[::2, 3:8] = ((x for x in row[4:9]) for row in varCopy[1::2])
        self.assertNotEqual(self.v.toList(), varCopy)
        self.assertEqual(self.v[::2, 3:8].toList(), [[int(row[4])] + row[5:9] for row in varCopy[1::2]])
        self.v[::2, 3:8] = ((x for x in row[3:8]) for row in varCopy[::2]) # restore values
        self.assertEqual(self.v.toList(), varCopy) # check that values restored
        
    def test_st_viewobs(self):
        self.assertRaises(TypeError, st_viewobs, st_Matrix("matA")) # arg needs to be st_View instance
        self.assertRaises(TypeError, st_viewobs, self.v, 0) # too many args
        self.assertRaises(TypeError, st_viewobs) # too few args
    
        self.assertEqual(st_viewobs(self.v), tuple(range(74)))
        self.assertEqual(st_viewobs(self.v[::6,]), tuple(range(0,74,6)))
        
    def test_st_viewvars(self):
        self.assertRaises(TypeError, st_viewvars, st_Matrix("matA")) # arg needs to be st_View instance
        self.assertRaises(TypeError, st_viewvars, self.v, 0) # too many args
        self.assertRaises(TypeError, st_viewvars) # too few args
    
        self.assertEqual(st_viewvars(self.v), tuple(range(12)))
        self.assertEqual(st_viewvars(self.v[::4,::4]), (0,4,8))


#import pdb ; pdb.set_trace()   
suite = unittest.TestLoader().loadTestsFromTestCase(TestSmallFuncs)
unittest.TextTestRunner(verbosity=2).run(suite)

print("\n")


suite = unittest.TestLoader().loadTestsFromTestCase(TestView)
unittest.TextTestRunner(verbosity=2).run(suite)

print("\n")


suite = unittest.TestLoader().loadTestsFromTestCase(TestMatrix)
unittest.TextTestRunner(verbosity=2).run(suite)

print("\n")
