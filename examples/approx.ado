program approx, rclass
	// approx sin(x), range(-3.5 3.5) nterms(5)
	
	version 12.1

	syntax anything [, range(passthru) center(string) nterms(integer 3) *]

	if (`nterms' < 3) local nterms 3
	if ("`center'" == "") local center 0
	
	mata: st_local("filepath", findfile("approx.py"))
	if (`"`filepath'"' == `""') {
		noi di as error "cannot find Python file approx.py"
		exit 601
	}

	plugin call python_plugin , `"`filepath'"'
	if ("`importerror'" != "") {
		noi di as error _n "module Sympy must be installed"
		exit
	}

	forv i=1(1)`nterms' {
		if ("`f`i''" == "") {
			local nterms = `i' - 1
			continue, break
		}
	}

	local graphstr ""
	local legendstr ""
	forv i=1(1)`nterms' {
		local rg = 150 - round((`i' * 40) / `nterms')
		local bl = 250 - round((`i' * 80) / `nterms')
		local graphstr `"`graphstr' function y = `f`i'', `range' lcolor("`rg' `rg' `bl'") || "'
		local legendstr `"`legendstr' `i' "`f`i''""'
	}

	twoway `graphstr' function y = `f', `range' lcolor(black) lwidth(medthick) ///
		   legend(order(`legendstr')) title("Taylor approximations to `f'") `options'
		   
	return clear
	forv i=`nterms'(-1)1 {
		return local f`i' "`f`i''"
	}

end

program python_plugin, plugin
