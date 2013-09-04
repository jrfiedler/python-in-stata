#include "Python.h"
#include "stplugin.h"


#define SF_input(a,l)           ((_stata_)->get_input((a),(l)))
#define SF_isstr(i)             ((_stata_)->isstr(i))
#define SF_safereforms(s1,s2,d) ((_stata_)->safereforms(s2,s2,d))

PyObject *Py_MISSING = NULL ; /* Python version of Stata's "." missing value */
PyObject *Py_MissingValueCls = NULL ; /* the missing value class */
PyObject *Py_GetMissing = NULL ; /* returns MissingValue instance for float */

char varnames[32767][33] ; /* all Stata variable names at each invocation */
long num_stata_vars = 0 ;

/* adapted from http://en.wikipedia.org/wiki/Trie#A_C_version */
typedef struct trie
{
	int varnum ;
	int prefixes ;
	struct trie *edges[63] ;
} trie ;

trie *varnames_trie ;
 
static trie * 
trie_initialize(trie *node)
{
	int i ;
	if (node == NULL)
		node = (trie *) malloc(sizeof(trie)) ;
	node->varnum = -1 ;
	node->prefixes = 0 ;
	
	/* 63 allowed characters: underscore, numbers, a-z, and A-Z */
	for (i = 0; i < 63; i++) 
		node->edges[i] = NULL ;
	return node ;
}

static int 
trie_char_index(char s)
{
	if (s == '_') {
		return 0 ;
	}
	else if (s >= '0' && s <= '9') {
		return s - '0' + 1 ;
	}
	else if (s >= 'a' && s <= 'z') {
		return s - 'a' + 11 ;
	}
	else if (s >= 'A' && s <= 'Z') {
		return s - 'A' + 37 ;
	}
	else {
		return -1 ;
	}
}
 
static trie * 
trie_add_word(trie *ver, char *str, int varnum)
{
	char s ;
	int k ;
	
	s = str[0] ;
	if(s == '\0') {
		ver->varnum = varnum ;
	}
	else {
		ver->prefixes = (ver->prefixes) + 1 ;
		k = trie_char_index(s) ;
		if (k == -1) {
			/* This is really weak protection against illegal characters.
			User should make sure that _pyallvars`i' is a varname. */
			return ver ;
		}
		str++ ;
		if(ver->edges[k] == NULL) {
			ver->edges[k] = trie_initialize(ver->edges[k]) ;
		}
		ver->edges[k] = trie_add_word(ver->edges[k], str, varnum) ;
	}
	return ver ;
}

static int 
trie_free(trie *node)
{
	int k ;
	for (k = 0; k < 63; k++) {
		if(node->edges[k] != NULL)
			trie_free(node->edges[k]) ;
	}
	free(node) ;
	return 0 ;
}

static int 
findvar(char *name, char abbr_ok)
{
	int i, k, foundNext ;
	trie *node = varnames_trie ;

	if (name[0] == '\0') {
		PyErr_SetString(PyExc_ValueError, 
			"empty string not allowed") ;
		return -1 ;
	}

	for (i = 0; name[i] != '\0'; i++) {
		k = trie_char_index(name[i]) ;
		if (k == -1) {
			PyErr_SetString(PyExc_ValueError, 
				"argument cannot be Stata variable name") ;
			return -1 ;
		}
		node = node->edges[k] ;
		if(node == NULL) {
			PyErr_SetString(PyExc_ValueError, 
				"no Stata variable found") ;
			return -1 ;
		}
	}

	/* if node->varnum != -1, then we have an exact match */
	if (node->varnum != -1)
		return node->varnum ;

	/* no exact match, keep looking */
	if (!abbr_ok) {
		PyErr_SetString(PyExc_ValueError,
			"no Stata variable found (abbrev. not allowed)") ;
		return -1 ;
	}

	if (node->prefixes > 1) {
		PyErr_SetString(PyExc_ValueError,
			"ambiguous abbreviation") ;
		return -1 ;
	}

	while (node->varnum == -1 && node != NULL) {
		foundNext = 0 ;
		for (i = 0; i < 63; i++) {
			if (node->edges[i] != NULL) {
				node = node->edges[i] ;
				foundNext = 1 ;
				break ;
			}
		}
		if (!foundNext) {
			PyErr_SetString(PyExc_ValueError,
				"internal error; can't find variable") ;
			return -1 ;
		}
	}
	return node->varnum ;
}

static PyObject *
_st_display(PyObject *self, PyObject *args)
{
	char *toDisplay ;
	
	if (!PyArg_ParseTuple(args, "s", &toDisplay))
		return NULL ;
	
	SF_display(toDisplay) ;
	
	Py_INCREF(Py_None) ;
	return Py_None ;
}

static PyObject *
_st_error(PyObject *self, PyObject *args)
{
	char *toDisplay ;
	
	if (!PyArg_ParseTuple(args, "s", &toDisplay))
		return NULL ;
	
	SF_error(toDisplay) ;
	
	Py_INCREF(Py_None) ;
	return Py_None ;
}

static PyObject *
_st_data(PyObject *self, PyObject *args)
{
	ST_int i, j, nobs ;
	ST_double z ;
	ST_retcode rc ;
	PyObject *mv ;

	if (!PyArg_ParseTuple(args, "ii", &i, &j))
		return NULL ;

	/* check that variable and observation numbers make sense */
	nobs = SF_nobs() ;
	if (i < -nobs || i >= nobs) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata observation number out of range") ;
		return NULL ;
	}
	if (j < -num_stata_vars || j >= num_stata_vars) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata variable number out of range") ;
		return NULL ;
	}

	/* convert negative indices to positive */
	if (i < 0)
		i = nobs + i ;
	if (j < 0)
		j = num_stata_vars + j ;

	/* check to make sure variable is numerical */
	if (SF_isstr(j + 1)) {
		PyErr_SetString(PyExc_TypeError, 
			"Stata variable is string") ;
		return NULL ;
	}

	/* Using i + 1 and j + 1 since python index starts from 0.
	Also switch order of i and j because plugin uses opposite order */
	rc = SF_vdata(j + 1, i + 1, &z) ;
	if (rc) {
		PyErr_SetString(PyExc_Exception, 
			"error in retrieving Stata numerical value") ;
		return NULL ;
	}

	if (SF_is_missing(z)) {
		/* must be large float */
		mv = PyObject_CallObject(Py_GetMissing, Py_BuildValue("(d)", z)) ;
		Py_INCREF(mv) ; 
		return mv ;
	}
	
	return PyFloat_FromDouble(z) ;
}

static PyObject *
_st_store(PyObject *self, PyObject *args)
{
	ST_int i, j, nobs ;
	ST_double val ;
	ST_retcode rc ;
	Py_ssize_t nargs ;
	PyObject *pyob ;
	
	nargs = PyTuple_Size(args) ;
	if (nargs != 3) {
		PyErr_SetString(PyExc_TypeError,
			"function takes exactly 3 arguments") ;
		return NULL ;
	}
	
	/* check if value is float, None, or instance of MissingValueCls */
	if (!PyArg_ParseTuple(args, "iid", &i, &j, &val)) { /* test for float */
		PyErr_Clear() ;
		if (!PyArg_ParseTuple(args, "iiO", &i, &j, &pyob)) {
			/* probably only get here if 1st or 2nd arg not int  */
			return NULL ;
		}
		/* check whether pyob is MissingValue or None or something else */
		if (PyObject_IsInstance(pyob, Py_MissingValueCls)) {
			val = PyFloat_AsDouble(PyObject_GetAttrString(pyob, "value")) ;
		}
		else if (pyob == Py_None) {
			val = SV_missval ;
		}
		else {
			PyErr_SetString(PyExc_TypeError, 
				"set value should be float, None, or a missing value") ;
			return NULL ;
		}
	}

	/* check that variable and observation numbers make sense */
	nobs = SF_nobs() ;
	if (i < -nobs || i >= nobs) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata observation number out of range") ;
		return NULL ;
	}
	if (j < -num_stata_vars || j >= num_stata_vars) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata variable number out of range") ;
		return NULL ;
	}

	/* convert negative indices to positive */
	if (i < 0)
		i = nobs + i ;
	if (j < 0)
		j = num_stata_vars + j ;

	/* check to make sure variable is numerical */
	if (SF_isstr(j + 1)) {
		PyErr_SetString(PyExc_TypeError, 
			"Stata variable is string") ;
		return NULL ;
	}

	/* Using i + 1 and j + 1 since python index starts from 0.
	Also switch order of i and j because plugin uses opposite order. */
	rc = SF_vstore(j + 1, i + 1, val) ; 
	if (rc) {
		PyErr_SetString(PyExc_Exception, 
			"error in setting Stata numerical value") ;
		return NULL ;
	}
	
	Py_INCREF(Py_None) ;
	return Py_None ;
}

static PyObject *
_st_sdata(PyObject *self, PyObject *args)
{
	ST_int i, j, nobs ;
	char s[245] ;
	ST_retcode rc ;

	if (!PyArg_ParseTuple(args, "ii", &i, &j))
		return NULL ;

	/* check that variable and observation numbers make sense */
	nobs = SF_nobs() ;
	if (i < -nobs || i >= nobs) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata observation number out of range") ;
		return NULL ;
	}
	if (j < -num_stata_vars || j >= num_stata_vars) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata variable number out of range") ;
		return NULL ;
	}

	/* convert negative indices to positive */
	if (i < 0)
		i = nobs + i ;
	if (j < 0)
		j = num_stata_vars + j ;

	/* check to make sure variable is string */
	if (!SF_isstr(j + 1)) {
		PyErr_SetString(PyExc_TypeError, 
			"Stata variable is not string") ;
		return NULL ;
	}

	/* Using i + 1 and j + 1 since python index starts from 0.
	Also switch order of i and j because plugin uses opposite order. */
	rc = SF_sdata(j + 1, i + 1, s) ;
	if (rc) {
		PyErr_SetString(PyExc_Exception,
			"error in retrieving Stata string value") ;
		return NULL ;
	}
	
	return PyUnicode_FromString(s) ;
}

static PyObject *
_st_sstore(PyObject *self, PyObject *args)
{
	ST_int i, j, nobs ;
	char *s ;
	ST_retcode rc ;

	if (!PyArg_ParseTuple(args, "iis", &i, &j, &s))
		return NULL ;

	/* check that variable and observation numbers make sense */
	nobs = SF_nobs() ;
	if (i < -nobs || i >= nobs) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata observation number out of range") ;
		return NULL ;
	}
	if (j < -num_stata_vars || j >= num_stata_vars) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata variable number out of range") ;
		return NULL ;
	}

	/* convert negative indices to positive */
	if (i < 0)
		i = nobs + i ;
	if (j < 0)
		j = num_stata_vars + j ;

	/* check to make sure variable is string */
	if (!SF_isstr(j + 1)) {
		PyErr_SetString(PyExc_TypeError, 
			"Stata variable is not string") ;
		return NULL ;
	}

	/* Using i + 1 and j + 1 since python index starts from 0.
	Also switch order of i and j because plugin uses opposite order. */
	rc = SF_sstore(j + 1, i + 1, s) ;
	if (rc) {
		PyErr_SetString(PyExc_Exception, 
			"error in setting Stata string value") ;
		return NULL ;
	}
	
	Py_INCREF(Py_None) ;
	return Py_None ;
}

static PyObject *
st_nobs(PyObject *self, PyObject *args)
{
	ST_int nobs ;

	if (!PyArg_ParseTuple(args, ""))
		return NULL ;
	
	nobs = SF_nobs() ;
	
	return PyLong_FromLong((long) nobs) ;
}

static PyObject *
st_nvar(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ""))
		return NULL ;
	
	return PyLong_FromLong((long) num_stata_vars) ;
}

static PyObject *
st_ifobs(PyObject *self, PyObject *args)
{
	ST_int j, nobs ;
	
	if (!PyArg_ParseTuple(args, "i", &j))
		return NULL ;
	
	/* check to make sure observation number makes sense */
	nobs = SF_nobs() ;
	if (j < -nobs || j >= nobs) {
		PyErr_SetString(PyExc_IndexError, 
			"Stata observation number out of range") ;
		return NULL ;
	}

	/* convert negative index to positive */
	if (j < 0)
		j = nobs + j ;

	/* j + 1 since python index starts from 0 */		
	if (SF_ifobs(j + 1)) {
		Py_INCREF(Py_True) ;
		return Py_True ;
	}
	else {
		Py_INCREF(Py_False) ;
		return Py_False ;
	}
}

static PyObject *
st_in1(PyObject *self, PyObject *args)
{
	ST_int n ;
	
	if (!PyArg_ParseTuple(args, ""))
		return NULL ;

	n = SF_in1() ;
	
	/* n - 1 since python indexing starts from 0 */
	return PyLong_FromLong((long) n - 1) ;
}

static PyObject *
st_in2(PyObject *self, PyObject *args)
{
	ST_int n ;
	
	if (!PyArg_ParseTuple(args, ""))
		return NULL ;

	n = SF_in2() ;
	
	/* Unlike stata_in1() function above, do not adjust by - 1.
	Python indexes will often be used like x[n1:n2] or
	range(n1, n2), which means n1 up to but not including n2. */
	return PyLong_FromLong((long) n) ;
}

static PyObject *
st_matrix_el(PyObject *self, PyObject *args)
{
	char *mat ;
	ST_int i, j, nRows, nCols ;
	ST_double val ;
	ST_retcode rc ;
	PyObject *pyob ;
	Py_ssize_t nargs ;
	
	nargs = PyTuple_Size(args) ;

	if (nargs == 3) {
		if (!PyArg_ParseTuple(args, "sii", &mat, &i, &j))
			return NULL ;

		/* check to make sure row and col numbers make sense */
		nRows = SF_row(mat) ;
		nCols = SF_col(mat) ;
		if (nRows == 0 || nCols == 0) {
			PyErr_SetString(PyExc_ValueError, 
				"cannot find a Stata matrix with that name") ;
			return NULL ;
		}
		if (i < -nRows || i >= nRows) {
			PyErr_SetString(PyExc_IndexError, 
				"matrix row number out of range") ;
			return NULL ;
		}
		if (j < -nCols || j >= nCols) {
			PyErr_SetString(PyExc_IndexError, 
				"matrix col number out of range") ;
			return NULL ;
		}

		/* convert negative indices to positive */
		if (i < 0)
			i = nRows + i ;
		if (j < 0)
			j = nCols + j ;

		/* i + 1 and j + 1 since python indexing starts from 0 */
		rc = SF_mat_el(mat, i + 1, j + 1, &val) ;
		if (rc) {
			PyErr_SetString(PyExc_Exception, 
				"error in retrieving Stata matrix element") ;
			return NULL ;
		}

		if (SF_is_missing(val)) {
			pyob = PyObject_CallObject(
				Py_GetMissing, Py_BuildValue("(d)", val)) ;
			Py_INCREF(pyob) ;
			return pyob ;
		}
	
		return PyFloat_FromDouble(val) ;
	}
	else if (nargs == 4) {
		/* check if value is float, None, or instance of MissingValueCls */
		if (!PyArg_ParseTuple(args, "siid", &mat, &i, &j, &val)) {
			PyErr_Clear() ;
			if (!PyArg_ParseTuple(args, "siiO", &mat, &i, &j, &pyob)) {
				/* probably only get here if fisrt 3 args not str, int, int  */
				return NULL ;
			}
			/* check whether pyob is MissingValue or None or something else */
			if (PyObject_IsInstance(pyob, Py_MissingValueCls)) {
				val = PyFloat_AsDouble(PyObject_GetAttrString(pyob, "value")) ;
			}
			else if (pyob == Py_None) {
				val = SV_missval ;
			}
			else {
				PyErr_SetString(PyExc_TypeError, 
					"set value should be float, None, or a missing value") ;
				return NULL ;
			}
		}

		/* check to make sure row and col numbers make sense */
		nRows = SF_row(mat) ;
		nCols = SF_col(mat) ;
		if (nRows == 0 || nCols == 0) {
			PyErr_SetString(PyExc_ValueError, 
				"cannot find a Stata matrix with that name") ;
			return NULL ;
		}
		if (i < -nRows || i >= nRows) {
			PyErr_SetString(PyExc_IndexError, 
				"matrix row number out of range") ;
			return NULL ;
		}
		if (j < -nCols || j >= nCols) {
			PyErr_SetString(PyExc_IndexError, 
				"matrix col number out of range") ;
			return NULL ;
		}

		/* convert negative indices to positive */
		if (i < 0)
			i = nRows + i ;
		if (j < 0)
			j = nCols + j ;

		/* i + 1 and j + 1 since python indexing starts from 0 */
		rc = SF_mat_store(mat, i + 1, j + 1, val) ; 
		if (rc) {
			PyErr_SetString(PyExc_Exception, 
				"error in setting Stata matrix element") ;
			return NULL ;
		}
	
		Py_INCREF(Py_None) ;
		return Py_None ;
	}
	else {
		PyErr_SetString(PyExc_TypeError, 
			"st_matrix_el() takes 3 arguments for getting or 4 for setting") ;
		return NULL ;
	}
}

static PyObject *
st_cols(PyObject *self, PyObject *args)
{
	char *mat ;
	ST_int nCols ;

	if (!PyArg_ParseTuple(args, "s", &mat))
		return NULL ;

	nCols = SF_col(mat) ;
	
	return PyLong_FromLong((long) nCols) ;
}

static PyObject *
st_rows(PyObject *self, PyObject *args)
{
	char *mat ;
	ST_int nRows ;

	if (!PyArg_ParseTuple(args, "s", &mat))
		return NULL ;

	nRows = SF_row(mat) ;
	
	return PyLong_FromLong((long) nRows) ;
}

static PyObject *
st_global(PyObject *self, PyObject *args)
{
	char *name, get_value[245], *set_value ;
	ST_retcode rc ;
	Py_ssize_t nargs ;
	
	nargs = PyTuple_Size(args) ;
	
	if (nargs == 1) {
		if (!PyArg_ParseTuple(args, "s", &name))
			return NULL ;
			
		rc = SF_macro_use(name, get_value, 245) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError, 
				"error in retrieving Stata global") ;
			return NULL ;
		}
		
		return PyUnicode_FromString(get_value) ;
	}
	else if (nargs == 2) {
		if (!PyArg_ParseTuple(args, "ss", &name, &set_value))
			return NULL ;

		rc = SF_macro_save(name, set_value) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError,
				"error in setting Stata global") ;
			return NULL ;
		}
		
		Py_INCREF(Py_None) ;
		return Py_None ;
	}
	else {
		PyErr_SetString(PyExc_TypeError, 
			"st_global() takes 1 argument for retrieving or 2 for setting") ;
		return NULL ;
	}
}

static PyObject *
st_local(PyObject *self, PyObject *args)
{
	char *lclname, macname[33], get_value[245], *set_value ;
	int i ;
	ST_retcode rc ;
	Py_ssize_t nargs ;
	
	nargs = PyTuple_Size(args) ;
	
	macname[0] = '_' ;
	macname[32] = '\0' ;
	
	if (nargs == 1) {
		if (!PyArg_ParseTuple(args, "s", &lclname))
			return NULL ;
		
		for(i = 0; i < 31 && ((macname[i+1] = lclname[i]) != '\0'); i++)
			;
			
		rc = SF_macro_use(macname, get_value, 245) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError, 
				"error in retrieving Stata local") ;
			return NULL ;
		}
		
		return PyUnicode_FromString(get_value) ;
	}
	else if (nargs == 2) {
		if (!PyArg_ParseTuple(args, "ss", &lclname, &set_value))
			return NULL ;
		
		for(i = 0; i < 31 && ((macname[i+1] = lclname[i]) != '\0'); i++)
			;

		rc = SF_macro_save(macname, set_value) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError, 
				"error in setting Stata local") ;
			return NULL ;
		}
		
		Py_INCREF(Py_None) ;
		return Py_None ;
	}
	else {
		PyErr_SetString(PyExc_TypeError, 
			"st_local() takes 1 argument for retrieving or 2 for setting") ;
		return NULL ;
	}
}

static PyObject *
st_numscalar(PyObject *self, PyObject *args)
{
	char *name ;
	double value ;
	ST_retcode rc ;
	Py_ssize_t nargs ;
	PyObject *pyob ;
	
	nargs = PyTuple_Size(args) ;
	
	if (nargs == 1) {
		if (!PyArg_ParseTuple(args, "s", &name))
			return NULL ;
			
		rc = SF_scal_use(name, &value) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError, 
				"error in setting Stata scalar") ;
			return NULL ;
		}
		
		if (SF_is_missing(value)) {
			pyob = PyObject_CallObject(
				Py_GetMissing, Py_BuildValue("(d)", value)) ;
			Py_INCREF(pyob) ;
			return pyob ;
		}
		
		return PyFloat_FromDouble(value) ;
	}
	else if (nargs == 2) {
		/* check if value is float, None, or instance of MissingValueCls */
		if (!PyArg_ParseTuple(args, "sd", &name, &value)) {
			PyErr_Clear() ;
			if (!PyArg_ParseTuple(args, "sO", &name, &pyob)) {
				/* probably only get here if 1st arg not str */
				return NULL ;
			}
			/* check whether pyob is MissingValue or None or something else */
			if (PyObject_IsInstance(pyob, Py_MissingValueCls)) {
				value = PyFloat_AsDouble(
					PyObject_GetAttrString(pyob, "value")) ;
			}
			else if (pyob == Py_None) {
				value = SV_missval ;
			}
			else {
				PyErr_SetString(PyExc_TypeError, 
					"set value should be float, None, or a missing value") ;
				return NULL ;
			}
		}

		rc = SF_scal_save(name, value) ;
		if (rc) {
			PyErr_SetString(PyExc_ValueError, 
				"error in setting Stata scalar") ;
			return NULL ;
		}
		
		Py_INCREF(Py_None) ;
		return Py_None ;
	}
	else {
		PyErr_SetString(PyExc_TypeError, 
			"st_numscalar() takes 1 argument for getting or 2 for setting") ;
		return NULL ;
	}
}

static ST_int
get_st_varnum(PyObject *arg)
{
	ST_int varnum ;
	char *varname ;
	
	if (!PyArg_ParseTuple(arg, "i", &varnum)) {
		PyErr_Clear() ;
		if (!PyArg_ParseTuple(arg, "s", &varname)) {
			PyErr_SetString(PyExc_TypeError,
				"Stata variable should be specified with single int or str") ;
			return -1 ;
		}
		else {
			varnum = findvar(varname, 1) ;
			/* findvar will set Python error string if warranted */
		}
	}
	else {
		/* checking to be sure varnum makes sense */
		if (varnum < -num_stata_vars || varnum >= num_stata_vars) {
			PyErr_SetString(PyExc_IndexError, 
				"Stata variable number out of range") ;
			return -1 ;
		}

		/* convert negative index to positive */
		if (varnum < 0)
			varnum = num_stata_vars + varnum ;
			
		/* varnum + 1 since python indexing starts from 0 */
		varnum = varnum + 1 ;
	}
	
	return varnum ;
}

static PyObject *
st_isstrvar(PyObject *self, PyObject *args)
{
	ST_int varnum ;

	varnum = get_st_varnum(args) ;

	if (varnum < 0) 
		return NULL ;
		
	if (SF_isstr((ST_int) varnum)) {
		Py_INCREF(Py_True) ;
		return Py_True ;
	}
	else {
		Py_INCREF(Py_False) ;
		return Py_False ;
	}
}

static PyObject *
st_isnumvar(PyObject *self, PyObject *args)
{
	ST_int varnum ;

	varnum = get_st_varnum(args) ;

	if (varnum < 0)
		return NULL ;
		
	if (!SF_isstr((ST_int) varnum)) {
		Py_INCREF(Py_True) ;
		return Py_True ;
	}
	else {
		Py_INCREF(Py_False) ;
		return Py_False ;
	}
}

static PyObject * 
st_varindex(PyObject *self, PyObject *args)
{
	int varnum, abbr_ok ;
	char *abbr ;
	Py_ssize_t nargs ;
	PyObject *pyob ;
	
	nargs = PyTuple_Size(args) ;

	if (nargs == 1) {
		if (!PyArg_ParseTuple(args, "s", &abbr))
			return NULL ;
		varnum = findvar(abbr, 0) ;
	}
	else if (nargs == 2) {
		if (!PyArg_ParseTuple(args, "sO", &abbr, &pyob))
			return NULL ;
		abbr_ok = PyObject_IsTrue(pyob) ;
		if (abbr_ok == -1) {
			PyErr_SetString(PyExc_TypeError, 
				"could not coerce second argument to boolean") ;
			return NULL ;
		}
		varnum = findvar(abbr, (char) abbr_ok) ;
	}
	else {
		PyErr_SetString(PyExc_TypeError, 
			"st_numscalar() takes 1 argument for getting or 2 for setting") ;
		return NULL ;
	}
	
	if (varnum < 0)
		return NULL ;

	return PyLong_FromLong((long) varnum ) ;
}

static PyObject *
st_varname(PyObject *self, PyObject *args)
{
	int varnum ;

	if (!PyArg_ParseTuple(args, "i", &varnum))
		return NULL ;

	if (varnum < -num_stata_vars || varnum >= num_stata_vars) {
		PyErr_SetString(PyExc_IndexError,
			"Stata variable index out of range") ;
		return NULL ;
	}
	
	/* varnum - 1 since python indexing starts from 0 */
	return PyUnicode_FromString(varnames[varnum]) ;
}

static PyObject *
st_ismissing(PyObject *self, PyObject *args)
{
	double d ;
	Py_ssize_t nargs ;
	PyObject *arg0 = NULL ;
	
	nargs = PyTuple_Size(args) ;
	
	if (nargs != 1) {
		PyErr_SetString(PyExc_TypeError,
			"function takes exactly 1 argument") ;
		return NULL ;
	}
	
	/* borrowed reference, no need for Py_DECREF */
	arg0 = PyTuple_GetItem(args, (Py_ssize_t) 0) ; 
	
	if (PyObject_IsInstance(arg0, Py_MissingValueCls) || arg0 == Py_None) {
		Py_INCREF(Py_True) ;
		return Py_True ;
	}
	
	if (!PyArg_ParseTuple(args, "d", &d)) {
		/* function argument is not correct type to be missing,
		so return False */
		PyErr_Clear() ;
		Py_INCREF(Py_False) ;
		return Py_False ;
	}
	
	if (d > 8.988465674311579e+307 || d < -1.7976931348623157e+308) {
		Py_INCREF(Py_True) ;
		return Py_True ;
	}
	else {
		Py_INCREF(Py_False) ;
		return Py_False ;
	}
}

static PyObject *
st_format(PyObject *self, PyObject *args)
{
	char *input1, *output, *fmt , fmtcopy[245] ;
	double value ;
	Py_ssize_t i ;
	Py_ssize_t nargs ;
	PyObject *pyob ;

	input1 = NULL ;
	
	nargs = PyTuple_Size(args) ;
	if (nargs != 2) {
		PyErr_SetString(PyExc_TypeError, 
			"st_format() takes exactly 2 arguments") ;
		return NULL ;
	}

	/* check if value is float, None, or instance of MissingValueCls */
	if (!PyArg_ParseTuple(args, "sd", &fmt, &value)) { /* test for float */
		PyErr_Clear() ;
		if (!PyArg_ParseTuple(args, "sO", &fmt, &pyob)) {
			/* probably only get here if 1st arg not str */
			return NULL ;
		}
		/* check whether pyob is MissingValue or None or something else */
		if (PyObject_IsInstance(pyob, Py_MissingValueCls)) {
			value = PyFloat_AsDouble(PyObject_GetAttrString(pyob, "value")) ;
		}
		else if (pyob == Py_None) {
			value = SV_missval ;
		}
		else {
			PyErr_SetString(PyExc_TypeError, 
				"2nd arg should be float, None, or a missing value") ;
			return NULL ;
		}
	}
	
	/* SF_safereforms changes the first and second arguments. 
	Not a problem with changing the first, but for the second, 
	the chenge causes a Python error when using a string 
	constant in a loop. Python expects the old string to 
	still be there and tries to reuse it. So instead, pass
	a copy of z2 to SF_safereforms. */
	for (i = 0; i < 245 && fmt[i] != '\0'; i++)
		;
		
	if (i > 244) {
		PyErr_SetString(PyExc_ValueError, 
			"format string is too long; max length is 245") ;
		return NULL ;
	}

	for (i = 0; (fmtcopy[i] = fmt[i]) != '\0'; i++)
		;
	
	output = SF_safereforms(input1, fmtcopy, value) ;
	
	return PyUnicode_FromString(output) ;
}

static PyMethodDef StataMethods[] = {
	{"_st_display", _st_display, METH_VARARGS,
	 "display in results window; smcl is interpreted\n"
	 "input: single str\n"
	 "returns: None"},
	{"_st_error", _st_error, METH_VARARGS,
	 "display error message in results window; smcl is interpreted\n"
	 "input: single str\n"
	 "returns: None"},
	{"_st_data", _st_data, METH_VARARGS,
	 "retrieve value in obs index i, var index j\n"
	 "input: int i, int j\n"
	 "returns: float"},
	{"_st_store", _st_store, METH_VARARGS,
	 "in obs index i, var index j, put float v\n"
	 "input: int i, int j, and float (or int) v\n"
	 "returns: None"},
	{"_st_sdata", _st_sdata, METH_VARARGS,
	 "retrieve value in obs index i, var index j\n"
	 "input: int i, int j\n"
	 "returns: str"},
	{"_st_sstore", _st_sstore, METH_VARARGS,
	 "in obs index i, var index j, put str s\n"
	 "input: int i, int j, and str s\n"
	 "returns None"},
	{"st_nvar", st_nvar, METH_VARARGS,
	 "get number of variables in the dataset loaded in Stata"},
	{"st_nobs", st_nobs, METH_VARARGS,
	 "get number of observations in the dataset loaded in Stata"},
	{"st_ifobs", st_ifobs, METH_VARARGS,
	 "determine whether 'if' condition is true in given observation\n"
	 "if no 'if' condition specified, returns True for all observations\n"
	 "input: int\n"
	 "returns: boolean"},
	{"st_in1", st_in1, METH_VARARGS,
	 "get gebbing of 'in' range when plugin was called;\n"
	 "if no 'in' range specified, returns zero"},
	{"st_in2", st_in2, METH_VARARGS,
	 "get end of 'in' range plus one when plugin was called;\n"
	 "if no 'in' range specified, returns number of observations in dataset"},
	{"st_matrix_el", st_matrix_el, METH_VARARGS,
	 "with 3 arguments:\n"
		"\tretrieve value in given matrix row and column\n"
		"\tinput: str matrix name, int row, int column\n"
		"\treturns: float\n"
	 "with 4 arguments:\n"
		"\tset value in given matrix row and column\n"
		"\tinput: str matrix name, int row, int column, and numeric value\n"
		"\treturns: None"},
	{"st_cols", st_cols, METH_VARARGS,
	 "get number of columns in given matrix\n"
	 "input: str matrix name\n"
	 "returns: int"},
	{"st_rows", st_rows, METH_VARARGS,
	 "get number of rows in given matrix\n"
	 "input: str matrix name\n"
	 "returns: int"},
	{"st_local", st_local, METH_VARARGS,
	 "with 1 argument:\n"
		"\tretrieve str in given local\n"
		"\tinput: str name\n"
		"\treturns: str\n"
	 "with 2 arguments:\n"
		"\tset local to given value\n"
		"\tinput: str name and str value\n"
		"\treturns: None"},
	{"st_global", st_global, METH_VARARGS,
	 "with 1 argument:\n"
		"\tretrieve str in given global\n"
		"\tinput: str name\n"
		"\treturns: str\n"
	 "with 2 arguments:\n"
		"\tset global to given value\n"
		"\tinput: str name and str value\n"
		"\treturns: None"},
	{"st_numscalar", st_numscalar, METH_VARARGS,
	 "with 1 argument:\n"
		"\tretrieve float in given scalar\n"
		"\tinput: str name\n"
		"\treturns: float\n"
	 "with 2 arguments:\n"
		"\tset scalar to given value\n"
		"\tinput: str name and float value\n"
		"\treturns: None"},
	{"st_isnumvar", st_isnumvar, METH_VARARGS,
	 "check if variable is numerical\n"
	 "input: int index -or- str name/abbrev\n"
	 "returns: boolean"},
	{"st_isstrvar", st_isstrvar, METH_VARARGS,
	 "check if variable is string\n"
	 "input: int index -or- str name/abbrev\n"
	 "returns: boolean"},
	{"st_varindex", st_varindex, METH_VARARGS,
	 "find index of variable with given name or abbreviation\n"
	 "input: str name/abbrev\n"
	 "returns: int (>= 0)\n"
	 "raises: ValueError if abbreviation is invalid or ambiguous"},
	{"st_varname", st_varname, METH_VARARGS,
	 "find name of variable at given index\n"
	 "input: int index (zero-based)\n"
	 "returns: str name"},
	{"st_ismissing", st_ismissing, METH_VARARGS,
	 "determine if Stata considers value missing\n"
	 "input: any Python object\n"
	 "returns: boolean"},
	{"st_format", st_format, METH_VARARGS,
	 "use given fmt, return string representation of value\n"
	 "input: str fmt and float (or int) value\n"
	 "returns: str"},
	{NULL, NULL, 0, NULL} /* Sentinel */
} ;

static struct PyModuleDef statamodule = {
	PyModuleDef_HEAD_INIT,
	"stata_plugin", /* name of module */
	NULL, 			/* module documentation, may be NULL */
	-1, 			/* size of per-interpreter state of the module,
						or -1 if the module keeps state in global variables. */
	StataMethods
} ;

PyMODINIT_FUNC
PyInit_stata_plugin(void)
{
	return PyModule_Create(&statamodule) ;
}

static int 
file_exists(const char *filename)
{
	FILE *f = fopen(filename, "r") ;

	if (!f) return 0 ;

	fclose(f) ;
	
	return 1 ;
}

static int
run_file(char *filename)
{
	FILE *fp ;
	PyObject *obj ;

	if (!file_exists(filename)) {
		SF_error("file not found\n\n") ;
		return 601 ;
	}
	
	/* workaround found in comment at stackoverflow.com/3654652 */
	obj = Py_BuildValue("s", filename) ;
	fp = _Py_fopen(obj, "r+") ;
	if (fp != NULL) {
		PyRun_SimpleFileEx(fp, filename, 1) ;
	}
	else {
		PyErr_Clear() ;
		SF_error("file could not be opened\n\n") ;
		return 603 ;
	}
	
	return 0 ;
}

static void 
run_interactive(int already_init)
{
	PyObject *main_module, *main_dict ;
	PyObject *pyrun ;
	char input[1000] ;
	int rc ;

	/* with help from stackoverflow.com/questions/9541353 */
	SF_display("{txt}{hline 49} " 
		"python (type {cmd:exit()} to exit) {hline}\n") ;
	
	main_module = PyImport_AddModule("__main__") ;
	main_dict = PyModule_GetDict(main_module) ;
	
	rc = SF_input(input, 999) ;
	while (strcmp(input, "exit()") != 0) {
		if (strcmp(input, "") != 0) {
			strcat(input, "\n") ;
			pyrun = PyRun_String(input, Py_single_input, 
			                     main_dict, main_dict) ;
			if (pyrun == NULL) { /* exception occurred */
				if (PyErr_ExceptionMatches(PyExc_SystemExit)) {
					/* exit invoked */
					PyErr_Clear() ;
					break ;
				}
				PyErr_Print() ; /* print error if not exit */
			}
			/* extra blank line before next input */
			SF_display("\n") ; 
		}
		rc = SF_input(input, 1000) ;
	}
	SF_display("{txt}{hline}\n") ;
}

static void 
initialize_plugin(void)
{
	PyObject *sys, *path ;

	PyImport_AppendInittab("stata_plugin", PyInit_stata_plugin) ;
	
	Py_Initialize() ;
	
	/* add current directory, aka ".", to Python path */
	sys = PyImport_ImportModule("sys") ;
	path = PyObject_GetAttrString(sys, "path") ;
	PyList_Append(path, PyUnicode_FromString(".")) ;
	
	PyRun_SimpleString("exit.__class__.__repr__ = "
		"lambda self: 'Use exit() plus Return to exit'") ;
	PyRun_SimpleString("from stata import *\n") ;
}

static int
initialize_missing(void)
{
	PyObject *miModule ;
			
	/* define missing value objects (i.e., make these known to C code) */
	miModule = PyImport_ImportModule("stata_missing") ;
	if (miModule == NULL) {
		PyErr_Clear() ;
		SF_error("could not import stata_missing module") ;
		SF_error("\n") ;
		return 601 ;
	}
	Py_MISSING = PyObject_GetAttrString(miModule, "MISSING") ;
	Py_MissingValueCls = PyObject_GetAttrString(miModule, "MissingValue") ;
	Py_GetMissing = PyObject_GetAttrString(miModule, "get_missing") ;
	return 0 ;
}

static void
setup_varnames(void)
{
	int rc, i, j ;
	char lname[17], varnamei[33], nvar[6], num[65], *end = NULL ;
	/* nvar[6] covers max no. of Stata vars, 32767 */
	
	/* this block sets num_stata_vars */
	nvar[5] = '\0' ; /* null-terminate nvar, just to be safe */
	rc = SF_macro_use("__pynallvars", nvar, 5) ;
	num_stata_vars = strtol(nvar, &end, 10) ;
	/* if nvar string not exhausted, set num_stata_vars to 0 */
	if (*end)
		num_stata_vars = 0 ;

	/* put all Stata variable names in **varnames 
	   and make trie tree of names */
	lname[0] = '\0' ;
	strcat(lname, "__pyallvars") ;
	lname[16] = '\0' ;

	varnames_trie = trie_initialize(NULL) ;
	for (i = 0; i < num_stata_vars; i++) {
		sprintf(num, "%d", i) ; /* safe because nvar limited to 6 chars */
		strcat(lname, num) ;
		for (j = 0; j < 6 && (lname[11+j] = num[j]) != '\0'; j++)
			;
		rc = SF_macro_use(lname, varnamei, 33) ;
		if (rc) {
			varnames[i][0] = '\0' ;
			continue ;
		}
		strcpy(varnames[i], varnamei) ;
		varnames_trie = trie_add_word(varnames_trie, varnamei, i) ;
	}
}

STDLL
stata_call(int argc, char *argv[])
{
	int already_init = Py_IsInitialized() ;
	int rc ;
	
	if (!already_init) {
		initialize_plugin() ;
	}

	/* make sure missing values are set */
	if (Py_MISSING == NULL) {
		rc = initialize_missing() ;
		if (rc)
			return 0 ;
	}

	setup_varnames() ;
	
	/* decide if run file or run interaction session */
	if (argc >= 1 && *argv[0] != '\0') {
		rc = run_file(argv[0]) ;
	}
	else {
		run_interactive(already_init) ;
	}

	/* free memory in varnames_trie, since memory 
	will be reallocated on next plugin call */
	if (num_stata_vars > 0) {
		trie_free(varnames_trie) ;
	}
	
	return 0 ;
}
