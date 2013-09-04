*! version 0.1.0
* Use Python within Stata, either interactively or by executing a file. 

program define python
	version 12.1
	
	syntax [varlist(default=none)] [if] [in] [, File(string) ///
												Args(string asis) ]

	// For the plugin, if file is empty set file local to empty quotes.
	// This is mostly to satisfy constraints in an older version of this
	// program, but is retained in case future changes require it.
	if ("`file'" == "") {
		local file = `""""'
	}

	// Set locals for variables in program varlist.
	local _pynvars = 0
	if ("`varlist'" != "") {
		unab varlist : `varlist'
		foreach var of varlist `varlist' {
			local _pyvar`_pynvars' = word("`varlist'", `_pynvars' + 1)
			local _pynvars = `_pynvars' + 1
		}
	}

	// Set locals for arguments.
	tokenize `args'
	local _pynargs = 0
	while (`"``=`_pynargs'+1''"' != `""') {
		local _pyarg`_pynargs' = `"``=`_pynargs'+1''"'
		local _pynargs = `_pynargs' + 1
	}

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

	// Get number of variables in dataset, and 
	// create local to designate all variables.
	local var_abbr = cond(c(k) > 0, "*", "")

	// If "`file'"" != "", plugin will (try to) run file.
	// Otherwise, plugin will start interactive interpreter.
	plugin call python_plugin `var_abbr' `if' `in', `file'

end


program python_plugin, plugin
