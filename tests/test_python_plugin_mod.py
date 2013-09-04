import unittest


class TestSmallFuncs(unittest.TestCase):
    def test_st_ifobs(self): # not in mata
        self.assertTrue(all(st_ifobs(i) for i in range(0,74,2)))
        self.assertTrue(all(not st_ifobs(i) for i in range(1,74,2)))
        
    def test_st_in1(self): # not in mata
        self.assertEqual(st_in1(), 4)
        
    def test_st_in2(self): # not in mata
        self.assertEqual(st_in2(), 70)

        
suite = unittest.TestLoader().loadTestsFromTestCase(TestSmallFuncs)
unittest.TextTestRunner(verbosity=2).run(suite)

print("\n")
