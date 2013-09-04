{smcl}
{* *! version 0.1.0 22aug2013}{...}
{cmd:help python}
{hline}

{title:Title}

{phang}
{bf : python} {hline 2} use the Python language within Stata{p_end}

{title:Syntax}
{p 8 17 2}
{cmdab:python}
[{varlist}]
{ifin}
[{cmd:,}
{it:options}]

{synoptset 20 tabbed}{...}
{synopthdr}
{synoptline}
{synopt:{opth f:ile(filename)}}run Python file{p_end}
{synopt :{opth a:rgs(string)}}arguments for the Python file or interactive
	session{p_end}
{synoptline}
{p2colreset}{...}

{title:Options}

{phang}
{opt file(filename)} specifies a Python file to execute. Without this option,
	the command will start an interactive Python session.

{phang}
{opt args(string)} specifies arguments for the file or 
	interactive session. The number of arguments is stored in a local macro
	{bf:_pynargs}, and the arguments are stored in local macros {bf:_pyarg0},
	{bf:_pyarg1}, etc.


{title:Description}

{phang}
{cmd:python} is a convenience wrapper for the {cmd:python_plugin} plugin, which 
	makes the Python language available within Stata. The user can execute 
	Python files or use Python in an interactive interpreter. 

{p 8 8 2}	
	The plugin provides functions for interacting with Stata data, 
	matrices, macros, and numeric scalars. These functions all have the prefix 
	{bf:st_}, in analogy with Mata's {bf:st_} functions. There are about half as 
	many such functions as there are in Mata. 
	
{p 4 8 2}
	See {bf:python_plugin.pdf} for more information.


{title:Examples}

{com}. python
{txt}{txt}{hline 49} python (type {cmd:exit()} to exit) {hline}
{com}. for i in range(5): print(i)
0
1
2
3
4

. bool("only single-line inputs allowed")
True

. st_local("_pynargs")
'0'

. st_local("_pynvars")
'0'

. exit()
{txt}{hline}

{com}. clear

. sysuse auto
{txt}(1978 Automobile Data)

{com}. python make price trunk if mod(_n,2), args(arg1 "a r g 2" arg3)
{txt}{txt}{hline 49} python (type {cmd:exit()} to exit) {hline}
{com}. n_args = int(st_local("_pynargs"))

. n_opt_vars = int(st_local("_pynvars"))

. n_args, n_opt_vars
(3, 3)

. for i in range(n_args): print(st_local("_pyarg" + str(i)))
arg1
a r g 2
arg3

. for i in range(n_opt_vars): print(st_local("_pyvar" + str(i)))
make
price
trunk

. st_ifobs(0)
True

. "keep in mind Stata indexing is 1-based, Python indexing is 0-based"
'keep in mind Stata indexing is 1-based, Python indexing is 0-based'

. st_ifobs(1)
False

. funcs = sorted([x for x in globals() if x.startswith("st_")])

. template = "{c -(}:>15{c )-}{c -(}:>15{c )-}{c -(}:>15{c )-}{c -(}:>15{c )-}"

. for i in range(0, len(funcs)-4, 4): print(template.format(*funcs[i:i+4]))
      st_Matrix        st_View        st_cols        st_data
      st_format      st_global       st_ifobs         st_in1
         st_in2       st_isfmt    st_islmname   st_ismissing
      st_isname    st_isnumfmt    st_isnumvar    st_isstrfmt
    st_isstrvar   st_isvarname       st_local   st_matrix_el
        st_nobs   st_numscalar        st_nvar        st_rows
       st_sdata      st_sstore       st_store    st_varindex
	   
. "see python_plugin.pdf for more info"
'see python_plugin.pdf for more info'

. exit()
{txt}{hline}


{title:Authors}

{pstd}
James Fiedler, Universities Space Research Association{break}
Email: {browse "mailto:jrfiedler@gmail.com":jrfiedler@gmail.com}

