import unittest


class TestSmallFuncs(unittest.TestCase):
    def test_data_funcs(self):
        self.assertEqual(_st_data(0, -4), 1)
        self.assertEqual(_st_data(0, -2), 2)
        self.assertEqual(_st_sdata(0, -3),"1st")
        self.assertEqual(_st_sdata(0, -1), "2nd")

    def test_st_isnumvar(self):
        isNum = [False] + [True]*12 + [False, True, False]
        self.assertEqual(isNum, [st_isnumvar(i) for i in range(st_nvar())])
        
    def test_st_isstrvar(self):
        isStr = [True] + [False]*12 + [True, False, True]
        self.assertEqual(isStr, [st_isstrvar(i) for i in range(st_nvar())])
        
    def test_st_nvar(self):
        self.assertEqual(st_nvar(), 16)
        
    def test_st_varindex(self):
        names = ['make', 'price', 'mpg', 'rep78', 'headroom', 'trunk', 
                   'weight', 'length', 'turn', 'displacement', 'gear_ratio', 
                   'foreign', 'numvar', 'strvar', 'numvar_2', 'strvar_2']
        # because of numvar & numvar_2, and strvar & strvar_2, this also
        # checks that st_varindex can find matches when a valid name is also
        # a prefix of another name
        self.assertEqual(list(range(st_nvar())), 
                         [st_varindex(name) for name in names])

    def test_st_varname(self):
        names = ['make', 'price', 'mpg', 'rep78', 'headroom', 'trunk', 
                   'weight', 'length', 'turn', 'displacement', 'gear_ratio', 
                   'foreign', 'numvar', 'strvar', 'numvar_2', 'strvar_2']
        self.assertEqual(names, [st_varname(i) for i in range(st_nvar())])
        
        
suite = unittest.TestLoader().loadTestsFromTestCase(TestSmallFuncs)
unittest.TextTestRunner(verbosity=2).run(suite)
