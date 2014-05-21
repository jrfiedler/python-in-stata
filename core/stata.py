import sys
import collections
import re
from math import ceil, log, floor

from stata_missing import MissingValue, MISSING
from stata_plugin import *
from stata_plugin import (
    _st_data, _st_store, _st_sdata, _st_sstore, _st_display, _st_error
)
from stata_variable import StataVariable


__version__ = "0.2.0"


__all__ = [
    'st_cols', '_st_data', 'st_data', 'st_format', 'st_global', 
    'st_ifobs', 'st_in1', 'st_in2', 'st_isfmt', 'st_islmname', 
    'st_ismissing', 'st_isname', 'st_isnumfmt', 'st_isnumvar', 
    'st_isstrfmt', 'st_isstrvar', 'st_isvarname', 'st_local', 
    'st_matrix', 'st_matrix_el', 'st_mirror', 'st_nobs', 
    'st_numscalar', 'st_nvar', 'st_rows', '_st_sdata', 
    'st_sdata', '_st_sstore', 'st_sstore', '_st_store', 
    'st_store', 'st_varindex', 'st_varname', 'st_view', 
    'st_viewobs', 'st_viewvars'
]


date_details = r'|'.join(
    d for d in (
        'CC', 'cc', 'YY', 'yy', 'JJJ', 'jjj', 'Month', 'Mon', 'month', 
        'mon', 'NN', 'nn', 'DD', 'dd', 'DAYNAME', 'Dayname', 'Day', 'Da',
        'day', 'da', 'q', 'WW', 'ww', 'HH', 'Hh', 'hH', 'hh', 'h', 'MM', 
        'mm', 'SS', 'ss', '.sss', '.ss', '.s', 'am', 'a.m.', 'AM', 'A.M.',
        '\.', ',', ':', '-', '\\\\', '_', '\+', '/', '!.'
    )
)
TIME_FMT_RE = re.compile(r'^%(-)?t(c|C|d|w|m|q|h|y|g)(' + date_details + ')*$')
TB_FMT_RE = re.compile(r'^%(-)?tb([^:]*)(:(' + date_details + ')*)?$')
NUM_FMT_RE = re.compile(r'^%(-)?(0)?([0-9]+)(\.|\,)([0-9]+)(f|g|e)(c)?$')
STR_FMT_RE = re.compile(r'^%(-|~)?(0)?([0-9]+)s$')
VALID_NAME_RE = re.compile(r'^[_a-zA-Z][_a-zA-Z0-9]{0,31}$')
VALID_LMNAME_RE = re.compile(r'^[_a-zA-Z0-9]{1,31}$')
RESERVED = frozenset(('_all', '_b', 'byte', '_coef', '_cons', 
            'double', 'float', 'if', 'in', 'int', 'long', '_n', '_N',
            '_pi', '_pred', '_rc', '_skip', 'using', 'with'))
STRING_TYPES_RE = re.compile(r'^str[0-9]+$')


class StataDisplay():
    def write(self, text):
        text_list = text.split("\n")
        for t in text_list[:-1]:
            _st_display(t)
            _st_display("\n")
        _st_display(text_list[-1])
    
    def flush(self):
        pass


class StataError():
    def write(self, text):
        _st_error(text)
    def flush(self):
        pass


sys.stdout = StataDisplay()
sys.stderr = StataError()


def st_isfmt(fmt):
    """Check that given string is a valid Stata format
        
    Parameters
    ----------
    fmt : str
    
    Returns
    -------
    bool
        
    """
    if not isinstance(fmt, str):
        raise TypeError("given fmt should be str")
    
    fmt = fmt.strip()
    
    if fmt[0] != '%':
        return False
    
    # handle business calendars first ;
    # this does not check the calendar name's validity.
    if fmt[1:3] == "tb" or fmt[1:4] == "-tb":
        return True if TB_FMT_RE.match(fmt) else False
        
    # handle date formats.
    if fmt[1] == 't' or fmt[1:3] == '-t':
        return True if TIME_FMT_RE.match(fmt) else False
    
    # categorize remaining formats using last character
    last_char = fmt[-1]
    if last_char == 's': # string
        return st_isstrfmt(fmt)
    elif last_char == 'H' or last_char == 'L': # binary
        # Valid binary formats are ^%(8|16)(H|L)$. 
        # Stata doesn't raise error with -8 or -16.
        return True if fmt[1:-1] in ('8', '16', '-8', '-16') else False
    elif last_char == 'x': # hexadecimal
        return True if fmt == '%21x' or fmt == '%-12x' else False
    elif last_char in {'f', 'g', 'e', 'c'}: # numeric
        m = NUM_FMT_RE.match(fmt)
        if not m: return False
        width = int(m.group(3))
        # In next line 244 is Stata 12 limit. Stata 13's is 2045.
        if width == 0 or width <= int(m.group(5)) or width > 244: return False
        return True
        
    return False


def st_isnumfmt(fmt):
    """Determine if given string is a valid Stata numeric format.
        
    Parameters
    ----------
    fmt : str
    
    Returns
    -------
    bool
        
    """
    if not isinstance(fmt, str):
        raise TypeError("function argument should be str")
    return st_isfmt(fmt) and not st_isstrfmt(fmt)


def st_isstrfmt(fmt):
    """Determine if given string is a valid Stata string format
        
    Parameters
    ----------
    fmt : str
    
    Returns
    -------
    bool
        
    """
    if not isinstance(fmt, str):
        raise TypeError("function argument should be str")
    m = STR_FMT_RE.match(fmt)
    if not m: return False
    width = int(m.group(3))
    if width == 0 or width > 244: return False # Stata 12; Stata 13 is different
    return True


def st_isname(name):
    """Determine if given string is a valid Stata name
    
    Parameters
    ----------
    name : str
    
    Returns
    -------
    bool
    
    Note
    ----
    To check for a valid local macro name, use `st_islmname`.
    To check for a valid Stata variable name, use `st_isvarname`.
    
    """
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    return True if VALID_NAME_RE.match(name) else False


def st_isvarname(name):
    """Determine if given string is a valid Stata variable name
    
    Parameters
    ----------
    name : str
    
    Returns
    -------
    bool
    
    """
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    if name in RESERVED or STRING_TYPES_RE.match(name): return False
    return True if VALID_NAME_RE.match(name) else False


def st_islmname(name):
    """Determine if given string is a valid local macro name.
    
    Parameters
    ----------
    name : str
    
    Returns
    -------
    bool
    
    """
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    return True if VALID_LMNAME_RE.match(name) else False


def _parse_obs_cols_vals(obs, cols, value=None):
    """helper for st_data, st_sdata, st_store, and st_sstore"""
    if isinstance(obs, int):
        obs = (obs,)
    if (not isinstance(obs, collections.Iterable) or 
            not all(isinstance(o, int) for o in obs)):
        raise TypeError("observations should be int or iterable of ints")
    if isinstance(cols, int) or isinstance(cols, str):
        cols = (cols,)
    if (not isinstance(cols, collections.Iterable) or 
            not all(isinstance(c, int) or isinstance(c, str) for c in cols)):
        raise TypeError("columns should be int, str, or iterable of int or str")
    
    # If entry in cols is str, break apart and apply st_findindex.
    # Either way, unpack into flat list.
    cols = [item 
        for c in cols 
            for item in 
                ((st_varindex(name, True) for name in c.split())
                 if isinstance(c, str) else (c,))]
    
    # checking vals
    if value is not None:
        nobs = len(obs)
        ncols = len(cols)
        
        def tuple_maker(x):
            if isinstance(x, str) or not isinstance(x, collections.Iterable):
                return (x,)
            if hasattr(x, "__len__"):
                return x
            return tuple(x)
        
        # force input into 2d structure
        if (isinstance(value, str) or 
                not isinstance(value, collections.Iterable)):
            value = ((value,),)
        else:
            value = tuple(tuple_maker(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (nobs == 1 and len(value) == ncols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
            
        # check lengths
        if not len(value) == nobs:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == ncols for v in value):
            raise ValueError("inner dimensions do not match number of columns")
    
    return obs, cols, value


def st_data(obsnums, vars):
    """Return numeric data in given observations and Stata variables.
    
    Parameters
    ----------
    obsnums : int or iterable of int
    vars : int, str, or iterable of int or str
        integers denote column numbers
        strings should be Stata variable names or 
          unambiguous abbreviations
    
    Returns
    -------
    List of lists of float or MissingValue,
    one sub-list for each observation
    
    """
    obsnums, vars, _ = _parse_obs_cols_vals(obsnums, vars)
    
    if not all(st_isnumvar(v) for v in vars):
        raise TypeError("only numeric Stata variables allowed")
    
    return [[_st_data(i,j) for j in vars] for i in obsnums]


def st_sdata(obsnums, vars):
    """Return string data in given observations and Stata variables.
    
    Parameters
    ----------
    obsnums : int or iterable of int
    vars : int, str, or iterable of int or str
        integers denote column numbers
        strings should be Stata variable names or 
          unambiguous abbreviations
    
    Returns
    -------
    List of lists, one sub-list for each observation
    
    """
    obsnums, vars, _ = _parse_obs_cols_vals(obsnums, vars)
    
    if not all(st_isstrvar(v) for v in vars):
        raise TypeError("only string Stata variables allowed")
    
    return [[_st_sdata(i,j) for j in vars] for i in obsnums]


def st_store(obs, cols, vals):
    """Replace data in given observations and Stata numeric variables
    
    Parameters
    ----------
    obsnums : int or iterable of int
    vars : int, str, or iterable of int or str
        integers denote column numbers
        strings should be Stata variable names or 
          unambiguous abbreviations
    values : iterable of iterables of numeric
        one sub-iterable per row
        dimensions should match implied dimensions 
          of `obsnums` and `vars`
        
    Returns
    -------
    None
    
    """
    obs, cols, vals = _parse_obs_cols_vals(obs, cols, vals)

    if not all(st_isnumvar(c) for c in cols):
        raise TypeError("only numeric Stata variables allowed")
    
    for obs_num, value_row in zip(obs, vals):
        for col_num, value in zip(cols, value_row):
            _st_store(obs_num, col_num, value)


def st_sstore(obsnums, vars, values):
    """Replace data in given observations and Stata string variables
    
    Parameters
    ----------
    obsnums : int or iterable of int
    vars : int, str, or iterable of int or str
        integers denote column numbers
        strings should be Stata variable names or 
          unambiguous abbreviations
    values : iterable of iterables of strings
        one sub-iterable per row
        dimensions should match implied dimensions 
          of `obsnums` and `vars`
        
    Returns
    -------
    None
    
    """
    obsnums, vars, values = _parse_obs_cols_vals(obsnums, vars, values)

    if not all(st_isstrvar(v) for v in vars):
        raise TypeError("only string Stata variables allowed")
    
    for obs, val_row in zip(obsnums, values):
        for col, val in zip(vars, val_row):
            _st_sstore(obs, col, val)

        
def st_view(rownums=None, varnums=None, selectvar=""):
    """Return a view onto current Stata data
    
    Parameters
    ----------
    rownums : int, iterable of int, None, or MissingValue instance
        optional
        default value is None
        if not specified, or is None or MissingValue instance,
            a view on all observations will be returned
    varnums : int, iterable of int, None, or MissingValue instance
        optional
        default value is None
        if not specified, or is None or MissingValue instance,
            a view on all Stata variables will be returned
    selectvar : string, int, None, or MissingValue instance
        optional
        default value is the empty string
        if not specified, or if the empty string, all rows in
            `rownums` will be included
        if specified as an integer or non-empty string, the
            corresponding Stata variable must be numeric;
            all rows in `rownums` will be included where the
            Stata variable has non-zero values
        if specified as None or a MissingValue instance, all
            rows in `rownums` will be included where _none_ 
            of the `varnums` variables have missing values
    
    Returns
    -------
    instance of StataView class    
    
    """
    nobs = st_nobs()
    nvar = st_nvar()
    
    if not st_ismissing(rownums):
        if isinstance(rownums, int):
            rownums = (rownums,)
        elif not isinstance(rownums, collections.Iterable):
            raise TypeError("rownums should be int or iterable of int")
        else:
            if not hasattr(rownums, "__len__"):  # a test for persistence
                rownums = tuple(rownums)
            if not all(isinstance(r, int) for r in rownums):
                raise TypeError("rownums must be integers")
            if not all(-nobs <= r < nobs for r in rownums):
                raise IndexError("rownums out of range")
            rownums = tuple(r if r >= 0 else nobs + r for r in rownums)
    else:
        rownums = None
    
    if not st_ismissing(varnums):
        if isinstance(varnums, int):
            varnums = (varnums,)
        elif not isinstance(varnums, collections.Iterable):
            raise TypeError("varnums should be int or iterable of int")
        else:
            if not hasattr(varnums, "__len__"):
                varnums = tuple(rownums)
            if not all(isinstance(c, int) for c in varnums):
                raise TypeError("varnums must be integers")
            if not all(-nvar <= c < nvar for c in varnums):
                raise IndexError("varnums out of range")
            varnums = tuple(c if c >= 0 else nvar + c for c in varnums)
    else:
        varnums = None
            
    if not selectvar == "":        
        if rownums is None:
            rownums = tuple(range(nobs))
        
        if st_ismissing(selectvar):
            numeric = tuple(
                c for c in (range(nvar) if varnums is None else varnums)
                if st_isnumvar(c)
            )
            rownums = tuple(
                r for r in rownums
                if not any(st_ismissing(_st_data(r,c)) for c in numeric)
            )
        else:
            if isinstance(selectvar, str):
                selectvar = st_varindex(selectvar, True)
            elif not isinstance(selectvar, int):
                raise TypeError("selectvar misspecified; invalid type")
            elif not -nvar <= selectvar < nvar:
                raise IndexError("selectvar index out of range")
            rownums = tuple(
                r for r in rownums if _st_data(r, selectvar) != 0
            )
            
    return StataView(rownums, varnums)

            
class StataView():
    """Python class of views onto the Stata dataset in memory"""
    def __init__(self, rownums=None, colnums=None):
        if rownums is None :
            self._nobs = self._nrows = st_nobs()
            rownums = tuple(range(self._nobs))
        else:
            # using set because there could be duplicates
            self._nobs = len(set(rownums))
            self._nrows = len(rownums)
        
        if colnums is None:
            self._nvar = self._ncols = st_nvar()
            colnums = tuple(range(self._nvar))
        else:
            self._nvar = len(set(colnums))
            self._ncols = len(colnums)
            
        self._rownums = rownums
        self._colnums = colnums
        
        self._formats = [
            "%11s" if st_isstrvar(c) else "%9.0g" for c in colnums
        ]
        self._getters = [
            _st_sdata if st_isstrvar(c) else _st_data for c in colnums
        ]
        self._setters = [
            _st_sstore if st_isstrvar(c) else _st_store for c in colnums
        ]
                         
    def __iter__(self):
        """return iterable of obs"""
        getters, cols, rows = self._getters, self._colnums, self._rownums
        return (tuple(g(r, c) for g,c in zip(getters, cols)) for r in rows)
    
    def __str__(self):
        getters, colnums, rownums = self._getters, self._colnums, self._rownums
        nrows, nobs = self._nrows, self._nobs
        ncols, nvar = self._ncols, self._nvar
        
        fmts = self._formats
        
        nobs_str = str(nobs)
        nrow_str = "" if nrows == nobs else (" (" + str(nrows) + " rows)")
        nvar_str = str(nvar)
        ncol_str = "" if ncols == nvar else (" (" + str(ncols) + " columns)")
        
        header = (
            "  {{txt}}" +
            "obs: {{:>{m}}}{{}}\n vars: {{:>{m}}}{{}}".format(
                m=max((len(nobs_str), len(nvar_str)))
            )
        )
        header = header.format(nobs_str, nrow_str, nvar_str, ncol_str)
        
        if nrows == 0 or ncols == 0:
            return "\n" + header + "\n\n"
                            
        rows = []
        append = rows.append
        for i, c in enumerate(colnums):
            if st_isstrvar(c):
                m = STR_FMT_RE.match(fmts[i])
                width = int(m.group(3)) if m else 11
                align = "<" if m and m.group(1) == "-" else ">"
                fmt = "{:" + align + str(width) + "}"
                append([fmt.format(_st_sdata(r,c)[:width]) for r in rownums])
            else:
                fmt = fmts[i] if not STR_FMT_RE.match(fmts[i]) else "%9.0g"
                append([st_format(fmt, _st_data(r,c)) for r in rownums])
        rows = [[inner[i] for inner in rows] for i in range(nrows)]
        
        maxrow = max(rownums)
        ndigits = 1 if maxrow == 0 else floor(log(maxrow, 10)) + 1
        
        row_fmt = "{{txt}}{:>" + str(ndigits+1) + "}"
        col_fmt = ["{:>" + str(len(s)) + "}" for s in rows[0]]
        
        for row, i in zip(rows, rownums):
            row.insert(0, row_fmt.format("r" + str(i)) + "{res}")
        
        rows.insert(
            0, 
            [row_fmt.format("")] + 
            [
                col_fmt[i].format("c" + str(v))
                for v,i in zip(colnums, range(ncols))
            ]
        )
        
        return ("\n" + header + "\n\n" + 
                "\n".join(" ".join(r for r in row) for row in rows))
        
    def to_list(self):
        """Return Stata data values as list of lists
                
        Returns
        -------
        List of lists, one sub-list per observation
        
        """
        getters, colnums, rownums = self._getters, self._colnums, self._rownums
        return [[g(r, c) for g,c in zip(getters, colnums)] for r in rownums]
        
    def get(self, rownum, colnum):
        """Get single data value from view
        
        Parameters
        ----------
        rownum : int
            index of row _within view_, i.e., not Stata observation number
        colnum : int
            index of column _within view_, i.e., not Stata variable number
            
        Returns
        -------
        string, float, or MissingValue instance, depending
        on data type of Stata variable
        
        """
        # use self._rownums[row] rather than row because self's rows
        # are not necessarily the same as Stata's observation numbers
        return self._getters[colnum](
            self._rownums[rownum], self._colnums[colnum]
        )
        
    def list(self):
        """Display values in current view object
        
        Side effects
        ------------
        Displays data, much like Stata's `list` command
        
        """
        print(self.__str__())
        
    def format(self, colnum, fmt):
        """Set the display format used by the `list` method
        
        Parameters
        ----------
        colnum : int
            index of column _within view_, i.e., not Stata variable number
        fmt : str
            Stata display format        
        
        """
        if not isinstance(fmt, str):
            raise TypeError("fmt argument should be str")
            
        if not isinstance(colnum, int):
            raise TypeError('colnum argument should be int')
        
        if not st_isfmt(fmt):
            raise ValueError(fmt + " is not a valid Stata format")
            
        if st_isstrfmt(fmt) != st_isstrvar(self._colnums[colnum]):
            raise ValueError("format does not match Stata variable type")
        
        self._formats[colnum] = fmt
        
    @property
    def rows(self):
        return self._rownums
        
    @property
    def cols(self):
        return self._colnums
        
    @property
    def nrows(self):
        return self._nrows
        
    @property
    def ncols(self):
        return self._ncols
                
    def __eq__(self, other):
        """determine if self is equal to other"""
        if not isinstance(other, StataView): return False
        
        if (not len(self._rownums) == len(other._rownums) or 
            not len(self._colnums) == len(other._colnums)):
                return False
        
        # This tests whether *contents* are the same.
        # It would be a little less permissive but 
        # easier and faster to test that rownums and 
        # colnums are the same. Which is better?
        rows1, cols1 = self._rownums, self._colnums
        rows2, cols2 = other._rownums, other._colnums
        getters, ncols = self._getters, self._ncols
        return all(
            st_isstrvar(c1) == st_isstrvar(c2) and
            all(
                getters[i](r1, c1) == getters[i](r2, c2)
                for r1, r2 in zip(rows1, rows2)
            )
            for c1, c2, i in zip(cols1, cols2, range(ncols))
        )
        
    def _check_index(self, prior_index, next_index):
        """To be used with __init__, __getitem__, and __setitem__ .
        Checks that index is well-formed and converts it to a 
        consistent form.
        
        """
        if next_index is None: return prior_index
        if isinstance(next_index, slice):
            start, stop, step = next_index.indices(len(prior_index))
            final_index = prior_index[start:stop:step]
        elif isinstance(next_index, collections.Iterable):
            if not hasattr(next_index, "__len__"):
                next_index = tuple(next_index)
            if not all(isinstance(i, int) for i in next_index):
                raise TypeError("individual indices must be int")
            final_index = tuple(prior_index[i] for i in next_index)
        else:
            if not isinstance(next_index, int):
                raise TypeError("index must be slice, iterable of int, or int")
            final_index = (prior_index[next_index],)
        return final_index
    
    def __getitem__(self, index):
        """return 'sub-view' of view with given indices"""
        if not isinstance(index, tuple) or not 1 <= len(index) <= 2:
            raise TypeError("data index must be [rows,cols] or [rows,]")
        sel_rows = self._check_index(self._rownums, index[0])
        sel_cols = self._check_index(self._colnums, 
                                     index[1] if len(index) == 2 else None)
        return StataView(rownums=sel_rows, colnums=sel_cols)
        
    def __setitem__(self, index, value):
        """change values if in 'sub-view' of view with given indices"""
        if not isinstance(index, tuple) or len(index) > 2:
            raise ValueError("data index must be [rows,cols] or [rows,]")
        sel_rows = self._check_index(self._rownums, index[0])
        sel_cols = self._check_index(self._colnums, 
                                     index[1] if len(index) == 2 else None)
        
        n_sel_rows = len(sel_rows)
        n_sel_cols = len(sel_cols)
        
        if n_sel_rows == 0 or n_sel_cols == 0:
            return
        
        def tuple_maker(x):
            if isinstance(x, str) or not isinstance(x, collections.Iterable):
                return (x,)
            return tuple(x)
            
        if isinstance(value, StataMatrix) or isinstance(value, StataView):
            value = value.to_list()
            # no need to go through tuple_maker here, so maybe rewrite
        
        # force input into 2d structure
        if (isinstance(value, str) or
                not isinstance(value, collections.Iterable)):
            value = ((value,),)
        else:
            value = tuple(tuple_maker(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (n_sel_rows == 1 and len(value) == n_sel_cols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
        
        # check lengths
        if not len(value) == n_sel_rows:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == n_sel_cols for v in value):
            raise ValueError("inner dimensions do not match number of columns")    
        
        setters = self._setters
        for row, i in zip(sel_rows, range(n_sel_rows)):
            for col, j in zip(sel_cols, range(n_sel_cols)):
                setters[col](row, col, value[i][j])


def st_viewvars(view_obj):
    """Return Stata variable indices from StataView object
    
    Parameters
    ----------
    view_obj : instance of StataView class
    
    Returns
    -------
    tuple of int
    
    """
    if not isinstance(view_obj, StataView):
        raise TypeError("argument should be a View")
    return view_obj._colnums


def st_viewobs(view_obj):
    """Return row numbers from StataView object
    
    Parameters
    ----------
    view_obj : instance of StataView class
    
    Returns
    -------
    tuple of int
    
    """
    if not isinstance(view_obj, StataView):
        raise TypeError("argument should be a View")
    return view_obj._rownums


def st_mirror():
    """Return a 'mirror' of the current Stata data set
        
    Returns
    -------
    instance of StataMirror class
    
    """
    return StataMirror()

    
class StataMirror(StataView):
    def __init__(self):
        pass
        
    @property
    def _rownums(self):
        return tuple(i for i in range(st_nobs()))
        
    @property
    def _colnums(self):
        return tuple(i for i in range(st_nvar()))
        
    @property
    def _nrows(self):
        return st_nobs()
        
    @property
    def _ncols(self):
        return st_nvar()
        
    @property
    def _getters(self):
        return [
            _st_sdata if st_isstrvar(i) else _st_data 
            for i in range(st_nvar())
        ]
        
    @property
    def _setters(self):
        return [
            _st_sstore if st_isstrvar(i) else _st_store 
            for i in range(st_nvar())
        ]
        
    def __len__(self):
        return st_nobs()

    def __getattr__(self, name):
        """Provides shortcut to Stata variables by appending "_".
        Raises AttributeError if name does not end with "_".
        Tries to find variable and return StataVariable otherwise.
        """
        if not name.endswith("_"):
            msg = "'{}' object has no attribute '{}'"
            raise AttributeError(msg.format(self.__class__.__name__, name))
            
        varname = st_varname(st_varindex(name[:-1], True))
        
        return StataVariable(self, varname)
        
    def __setattr__(self, name, value):
        """Provides shortcut to Stata variables by appending "_".
        Creates or replaces variable if name ends with "_".
        Creates or replaces regular attribute otherwise.
        """
        if not name.endswith("_"):
            self.__dict__[name] = value
        else:
            if not isinstance(value, collections.Iterable):
                if st_nobs() > 1:
                    raise TypeError("iterable required")
                value = (value,)
            elif len(value) != st_nobs():
                msg = "need iterable of length {}, got length {}"
                raise ValueError(msg.format(st_nobs(), len(value)))
            col = st_varindex(name[:-1], True)
            setter = _st_sstore if st_isstrvar(col) else _st_store
            for i,v in enumerate(value):
                setter(i, col, v)
        
    def __delattr__(self, name):
        """Provides shortcut to Stata variables by appending "_".
        Raises AttributeError if name does not end with "_".
        Otherwise, tries to find variable and drop it.
        """
        if name.endswith("_"):
            raise ValueError("cannot drop Stata variables from Python")
        else:
            if name not in self.__dict__:
                msg = "'{}' object has no attribute '{}'"
                raise AttributeError(msg.format(self.__class__.__name__, name))
            del self.__dict__[name]

    def index(self, varname):
        """Returns index of Stata variable within data set
        
        Parameter
        ---------
        varname : str
            Stata variable name or unambiguous abbreviation
        
        Returns
        -------
        int
        
        """
        return st_varindex(varname, True)
        
    def get(self, rownum, colnum):
        """Get single data value from view
        
        Parameters
        ----------
        rownum : int
            Stata observation number
        colnum : int
            Stata variable index
            
        Returns
        -------
        string, float, or MissingValue instance, depending
        on data type of Stata variable
        
        """
        if st_isstrvar(colnum): 
            return _st_sdata(rownum, colnum)
        else:
            return _st_data(rownum, colnum)


def st_matrix(matname):
    """Return a view onto given Stata matrix
    
    Parameters
    ----------
    matname : str
        name of Stata matrix
        
    Returns
    -------
    instance of StataMatrix class
    
    """
    if not isinstance(matname, str):
        raise TypeError("matrix name should be a string")
        
    nrows, ncols = st_rows(matname), st_cols(matname)
    if nrows == 0 or ncols == 0:
        # in Mata, st_matrix returns J(0,0) if matrix doesn't exist, 
        # but typical Python thing would be to raise an error
        raise ValueError("cannot find a Stata matrix named " + matname)
    
    return StataMatrix(matname)


class StataMatrix():
    """Python class of views onto Stata matrices"""
    def __init__(self, matname, rownums=None, colnums=None, fmt=None):
        nrows, ncols = st_rows(matname), st_cols(matname)
        if nrows == 0 or ncols == 0:
            # in Mata, st_matrix returns J(0,0) if matrix doesn't exist, 
            # but typical Python thing would be to raise an error
            raise ValueError("cannot find a Stata matrix named " + matname)
        self._matname = matname
        self._fmt = fmt or "%10.0g"
        self._rownums = tuple(rownums if rownums is not None else range(nrows))
        self._colnums = tuple(colnums if colnums is not None else range(ncols))
        # in next line, don't want st_rows() because rownums does not 
        # have to equal range(st_rows())
        self._nrows = len(self._rownums)
        self._ncols = len(self._colnums)
        
    def __iter__(self):
        """return iterable of rows"""
        matname, cols, rows = self._matname, self._colnums, self._rownums
        return (tuple(st_matrix_el(matname, r, c) for c in cols) for r in rows)
        
    def format(self, fmt):
        """Set the display format used by the `list` method
        
        Parameters
        ----------
        fmt : str
            Stata numeric display format        
        
        """
        if not isinstance(fmt, str):
            raise TypeError('fmt argument should be str')
        if st_isstrfmt(fmt) or not st_isfmt(fmt):
            raise ValueError("given format is not a valid numeric format")
        self._fmt = fmt
        
    def list(self, fmt=None):
        """Display values in current view object
        
        Side effects
        ------------
        Displays data, much like Stata's `matrix list` command
        
        """
        if fmt is None:
            fmt = self._fmt
        elif not st_isnumfmt(fmt):
            raise ValueError("given format is not a valid numeric format")
        
        matname, rownums, colnums = self._matname, self._rownums, self._colnums
        maxrow = max(rownums)
        
        ndigits = (1 if self._nrows == 0 or maxrow == 0
                     else floor(log(maxrow, 10)) + 1)
        
        fmt_width = len(st_format(fmt, 0))
        
        row_fmt = "{{txt}}{:>" + str(ndigits+1) + "}"
        col_fmt = "{:>" + str(fmt_width) + "}"
        
        # print matrix info and column headers
        print("\n{{txt}}{}[{},{}]".format(matname, self._nrows, self._ncols))
        print(row_fmt.format("") + " " + 
              " ".join(col_fmt.format("c" + str(i)) for i in colnums))
        
        # print rows
        for r in rownums:
            print(row_fmt.format("r" + str(r)) + "{res} " + 
                  " ".join(st_format(fmt, st_matrix_el(matname, r, c)) 
                           for c in colnums))
        
    def to_list(self):
        """Return matrix values as list of lists
                
        Returns
        -------
        List of lists of float or MissingValue instances,
        one sub-list per row
        
        """
        matname, cols, rows = self._matname, self._colnums, self._rownums
        return [[st_matrix_el(matname, r, c) for c in cols] for r in rows]
        
    def get(self, rownum, colnum):
        """get single item from matrix"""
        """Get single value from matrix view
        
        Parameters
        ----------
        rownum : int
            index of row _within view_, i.e., 
                not necessarily row of Stata matrix
        colnum : int
            index of column _within view_, i.e., 
                not necessarily column of Stata matrix
                
        Returns
        -------
        float or MissingValue instance
        
        """
        # use self._rownums[rownum] rather than row directly because 
        # self's rows might not be the same as the Stata matrix's
        return st_matrix_el(
            self._matname, self._rownums[rownum], self._colnums[colnum]
        )
        
    def __str__(self):
        """string representation of StataMatrix object"""
        matname, rownums, colnums = self._matname, self._rownums, self._colnums
        maxrow = max(rownums)
        fmt = self._fmt
        
        ndigits = (1 if self._nrows == 0 or maxrow == 0
                     else floor(log(maxrow, 10)) + 1)
        
        fmt_width = len(st_format(fmt, 0))
        
        row_fmt = "{{txt}}{:>" + str(ndigits+1) + "}"
        col_fmt = "{:>" + str(fmt_width) + "}"
        
        # matrix info, column headers, and generator of row strs
        header = "\n{{txt}}{}[{},{}]".format(matname, self._nrows, self._ncols)
        col_top = (row_fmt.format("") + " " +
                   " ".join(col_fmt.format("c" + str(i)) for i in colnums))
        row_gen = (row_fmt.format("r" + str(r)) + 
                   "{res} " +
                   " ".join(st_format(fmt, st_matrix_el(matname, r, c)) 
                            for c in colnums)
                   for r in rownums)
        
        return header + "\n" + col_top + "\n" + "\n".join(row_gen)
        
    @property
    def rows(self):
        return self._rownums
        
    @property
    def cols(self):
        return self._colnums
        
    @property
    def nrows(self):
        return self._nrows
        
    @property
    def ncols(self):
        return self._ncols
                
    def __eq__(self, other):
        """determine if self is equal to other"""
        if not isinstance(other, StataMatrix): return False
        
        if (not len(self._rownums) == len(other._rownums) or 
            not len(self._colnums) == len(other._colnums)):
                return False
        
        mat1, rows1, cols1 = self._matname, self._rownums, self._colnums
        mat2, rows2, cols2 = other._matname, other._rownums, other._colnums
        return all(st_matrix_el(mat1, r1, c1) == st_matrix_el(mat2, r2, c2)
                   for r1, r2 in zip(rows1, rows2) 
                   for c1, c2 in zip(cols1, cols2))
        
    def _check_index(self, prior_index, next_index):
        """To be used with __getitem__ and __setitem__ .
        Checks that index is well-formed and converts it 
        to consistent form.
        
        """
        if next_index is None: return prior_index
        if isinstance(next_index, slice):
            start, stop, step = next_index.indices(len(prior_index))
            final_index = prior_index[start:stop:step]
        elif isinstance(next_index, collections.Iterable):
            if not hasattr(next_index, "__len__"):
                next_index = tuple(next_index)
            if not all(isinstance(i, int) for i in next_index):
                raise TypeError("individual indices must be int")
            final_index = tuple(prior_index[i] for i in next_index)
        else:
            if not isinstance(next_index, int):
                raise TypeError("index must be slice, iterable of int, or int")
            final_index = (prior_index[next_index],)
        return final_index
    
    def __getitem__(self, index):
        """return StataMatrix object containing rows and cols 
        specified by index tuple
        
        """
        if not isinstance(index, tuple) or not 1 <= len(index) <= 2:
            raise TypeError("matrix index must be [rows,cols] or [rows,]")
        sel_rows = self._check_index(self._rownums, index[0])
        sel_cols = self._check_index(self._colnums, 
                                   index[1] if len(index) == 2 else None)
        return StataMatrix(self._matname, 
                         rownums=sel_rows, colnums=sel_cols, fmt=self._fmt)
        
    def __setitem__(self, index, value):
        """Replace values in specified rows and cols of -index- tuple.
        The shape of -value- should match the shape implied by -index-.
        
        """
        if not isinstance(index, tuple) or len(index) > 2:
            raise ValueError("matrix index must be [rows,cols] or [rows,]")
        sel_rows = self._check_index(self._rownums, index[0])
        sel_cols = self._check_index(self._colnums, 
                                   index[1] if len(index) == 2 else None)
        
        n_sel_rows = len(sel_rows)
        n_sel_cols = len(sel_cols)
        
        if n_sel_rows == 0 or n_sel_cols == 0:
            return
        
        def tuple_maker(x):
            if isinstance(x, str):
                raise TypeError("matrix values may not be str")
            if not isinstance(x, collections.Iterable):
                return (x,)
            return tuple(x)
            
        if isinstance(value, StataMatrix) or isinstance(value, StataView):
            value = value.to_list()
            # No need to go through tuple_maker here, so maybe rewrite.
            # If rewriting around tuple_maker, StataView variables should be
            # checked to be sure they are numeric.
        
        # force input into 2d structure
        if isinstance(value, str):
            raise TypeError("matrix values must be numeric; str not allowed")
        if not isinstance(value, collections.Iterable):
            value = ((value,),)
        else:
            value = tuple(tuple_maker(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (n_sel_rows == 1 and len(value) == n_sel_cols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
        
        # check lengths
        if not len(value) == n_sel_rows:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == n_sel_cols for v in value):
            raise ValueError("inner dimensions do not match number of columns")    
        
        matname = self._matname
        for row, i in zip(sel_rows, range(n_sel_rows)):
            for col, j in zip(sel_cols, range(n_sel_cols)):
                st_matrix_el(matname, row, col, value[i][j])
