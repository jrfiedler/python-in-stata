program prem
  version 12.1
  syntax varlist(string min=1 max=1) [if] [in] , regex(string)
  
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
  
  plugin call python_plugin * `if' `in', prem.py
end

program python_plugin, plugin
