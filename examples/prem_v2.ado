program prem_v2
  version 12.1
  syntax varlist(string min=1 max=1) [if] [in] , regex(string)
  
  python `varlist' `if' `in', file(prem.py) locals(regex "`regex'")
end
