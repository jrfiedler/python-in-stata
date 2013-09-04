program fdi
	// fdi asinh(x), range(-3 3) fint(lpattern(dash))
	
	version 12.1
	
	syntax anything [, Foptions(string asis) ///
						FPRIMEoptions(string asis) ///
						FINToptions(string asis) ///
						range(passthru) ///
						*]

	plugin call python_plugin , fdi.py
	if ("`importerror'" != "") {
		noi di as error _n "module Sympy must be installed"
		exit
	}

	noi di "  f : `anything'"
	noi di "D(f): `fprime'"
	noi di "I(f): `fint'"

	twoway function y = `anything', `range' lc(black) `foptions' || ///
		   function y = `fprime', `range' lp(shortdash_dot) lc(black) `fprimeoptions' || ///
		   function y = `fint', `range' lp(dash) lc(black) `fintoptions' ///
		   legend(order(1 "`anything'" 2 "`fprime'" 3 "`fint'") cols(1)) `options'

end

program python_plugin, plugin
