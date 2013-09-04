program define test_python_plugin
	version 12.1

	tempfile auto_copy

	preserve
	clear
	qui sysuse auto
	qui save `auto_copy' // safety against changes to dataset

	// set up local, global, scalar, and matrices
	local localA = "some local"
	local localB = "some local"
	global globalA = "some global"
	global globalB = "some global"
	scalar scalarA = 123456
	scalar scalarB = .
	scalar scalarC = .g
	scalar scalarD = .g
	mkmat price-headroom in 2/8, matrix(matA)
	matrix matB = matA

	// drop values, just in case
	macro drop noSuchGlobal globalC _localC
	cap scalar drop scalarE noSuchScalar
	cap matrix drop noSuchMatrix
	
	// Put all varnames of varlist in locals.
	// Used to create lookups name <-> index.
	local _pynallvars = 0
	if (c(k) > 0) {
		foreach var of varlist * {
			local _pyallvars`_pynallvars' = "`var'"
			local _pynallvars = `_pynallvars' + 1
		}
	}

	// call test_plugin.py to interact with above values
	noi plugin call python_plugin *, test_python_plugin.py

	// assert correct changes made in test_plugin
	assert scalar(scalarD) == 789
	assert scalar(scalarE) == .m
	assert scalar(scalarF) == .
	assert scalar(scalarG) == .m
	assert "`localB'" == "the local B"
	assert "`localC'" == "the local C"
	assert "$globalB" == "the global B"
	assert "$globalC" == "the global C"

	// now call test_python_plugin_mod.py with if, in, and varlist
	noi plugin call python_plugin * in 5/70 if mod(_n,2), ///
		test_python_plugin_mod.py

	// now call test_python_plugin_reg.py after doing a regression and gen;
	// the regression will put a hidden variable into the dataset;
	// check that all functions work as they should, and that plugin doesn't
	// see hidden variable
	qui reg price weight length rep78
	qui gen numvar = 2*_n - 1
	qui gen strvar = "1st"
	qui gen numvar_2 = 2*_n
	qui gen strvar_2 = "2nd"
	
	// Put all varnames of varlist in locals.
	// Used to create lookups name <-> index.
	ereturn clear // to clear hidden variables
	local _pynallvars = 0
	if (c(k) > 0) {
		foreach var of varlist * {
			local _pyallvars`_pynallvars' = "`var'"
			local _pynallvars = `_pynallvars' + 1
		}
	}
	
	noi plugin call python_plugin *, test_python_plugin_reg.py
	
	restore
end

program python_plugin, plugin
