import sys
import collections
import re
from math import ceil, log, floor

from stata_missing import MissingValue, MISSING
from stata_plugin import *
from stata_plugin import (_st_data, _st_store, _st_sdata, _st_sstore,
                          _st_display, _st_error)


__version__ = "0.1.0"

__all__ = [
    'st_cols', '_st_data', 'st_data', 'st_format', 'st_global', 
    'st_ifobs', 'st_in1', 'st_in2', 'st_isfmt', 'st_islmname', 
    'st_ismissing', 'st_isname', 'st_isnumfmt', 'st_isnumvar', 
    'st_isstrfmt', 'st_isstrvar', 'st_isvarname', 'st_local', 
    'st_Matrix', 'st_matrix_el', 'st_nobs', 'st_numscalar', 'st_nvar', 
    'st_rows', '_st_sdata', 'st_sdata', '_st_sstore', 'st_sstore', 
    '_st_store', 'st_store', 'st_varindex', 'st_varname', 'st_View', 
    'st_viewobs', 'st_viewvars'
    ]


dateDetails = r'|'.join(
    d for d in 
        ('CC', 'cc', 'YY', 'yy', 'JJJ', 'jjj', 'Month', 'Mon', 'month', 
        'mon', 'NN', 'nn', 'DD', 'dd', 'DAYNAME', 'Dayname', 'Day', 'Da',
        'day', 'da', 'q', 'WW', 'ww', 'HH', 'Hh', 'hH', 'hh', 'h', 'MM', 
        'mm', 'SS', 'ss', '.sss', '.ss', '.s', 'am', 'a.m.', 'AM', 'A.M.',
        '\.', ',', ':', '-', '\\\\', '_', '\+', '/', '!.')
    )
TIME_FMT_RE = re.compile(r'^%(-)?t(c|C|d|w|m|q|h|y|g)(' + dateDetails + ')*$')
TB_FMT_RE = re.compile(r'^%(-)?tb([^:]*)(:(' + dateDetails + ')*)?$')
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
        textList = text.split("\n")
        for t in textList[:-1]:
            _st_display(t)
            _st_display("\n")
        _st_display(textList[-1])
    
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
    """check that given str fmt is a valid Stata format"""
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
    lastChar = fmt[-1]
    if lastChar == 's': # string
        return st_isstrfmt(fmt)
    elif lastChar == 'H' or lastChar == 'L': # binary
        # Valid binary formats are ^%(8|16)(H|L)$. 
        # Stata doesn't raise error with -8 or -16.
        return True if fmt[1:-1] in ('8', '16', '-8', '-16') else False
    elif lastChar == 'x': # hexadecimal
        return True if fmt == '%21x' or fmt == '%-12x' else False
    elif lastChar in {'f', 'g', 'e', 'c'}: # numeric
        m = NUM_FMT_RE.match(fmt)
        if not m: return False
        width = int(m.group(3))
        # In next line 244 is Stata 12 limit. Stata 13's is 2045.
        if width == 0 or width <= int(m.group(5)) or width > 244: return False
        return True
        
    return False


def st_isnumfmt(fmt):
    """determine if given str is a valid Stata numerical format"""
    if not isinstance(fmt, str):
        raise TypeError("function argument should be str")
    return st_isfmt(fmt) and not st_isstrfmt(fmt)


def st_isstrfmt(fmt):
    """determine if given str is a valid Stata string format"""
    if not isinstance(fmt, str):
        raise TypeError("function argument should be str")
    m = STR_FMT_RE.match(fmt)
    if not m: return False
    width = int(m.group(3))
    if width == 0 or width > 244: return False # Stata 12; Stata 13 is different
    return True


def st_isname(name):
    """determine if given str is a valid Stata name"""
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    return True if VALID_NAME_RE.match(name) else False


def st_isvarname(name):
    """determine if given str is a valid Stata variable name"""
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    if name in RESERVED or STRING_TYPES_RE.match(name): return False
    return True if VALID_NAME_RE.match(name) else False


def st_islmname(name):
    """determine if given str is a valid local macro name"""
    if not isinstance(name, str):
        raise TypeError("function argument should be str")
    return True if VALID_LMNAME_RE.match(name) else False


def _parseObsColsVals(obs, cols, value=None):
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
        nObs = len(obs)
        nCols = len(cols)
        
        def tupleIzer(x):
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
            value = tuple(tupleIzer(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (nObs == 1 and len(value) == nCols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
            
        # check lengths
        if not len(value) == nObs:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == nCols for v in value):
            raise ValueError("inner dimensions do not match number of columns")
    
    return obs, cols, value


def st_data(obs, cols):
    """return numeric data in given observation numbers as a list of lists, 
    one sub-list for each row; obs should be int or iterable of int;
    cols should be a single str or int or iterable of str or int
    
    """
    obs, cols, _ = _parseObsColsVals(obs, cols)
    
    if not all(st_isnumvar(c) for c in cols):
        raise TypeError("only numeric Stata variables allowed")
    
    return [[_st_data(i,j) for j in cols] for i in obs]


def st_sdata(obs, cols):
    """return string data in given observation numbers as a list of lists, 
    one sub-list for each row; obs should be int or iterable of int;
    cols should be a single str or int or iterable of str or int
    
    """
    obs, cols, _ = _parseObsColsVals(obs, cols)
    
    if not all(st_isstrvar(c) for c in cols):
        raise TypeError("only string Stata variables allowed")
    
    return [[_st_sdata(i,j) for j in cols] for i in obs]


def st_store(obs, cols, vals):
    """replace numeric data in given observation numbers and columns;
    obs should be int or iterable of int;
    cols should be a str or int, or iterable of str or int;
    new values should be iterable of iterables, one sub-iterable per row
    
    """
    obs, cols, vals = _parseObsColsVals(obs, cols, vals)

    if not all(st_isnumvar(c) for c in cols):
        raise TypeError("only numeric Stata variables allowed")
    
    for obsNum, row in zip(obs, vals):
        for colNum, value in zip(cols, row):
            _st_store(obsNum, colNum, value)


def st_sstore(obs, cols, vals):
    """replace string data in given observation numbers and columns;
    obs should be int or iterable of int;
    cols should be a str or int, or iterable of str or int;
    new values should be iterable of iterables, one sub-iterable per row
    
    """
    obs, cols, vals = _parseObsColsVals(obs, cols, vals)

    if not all(st_isstrvar(c) for c in cols):
        raise TypeError("only string Stata variables allowed")
    
    for obsNum, row in zip(obs, vals):
        for colNum, value in zip(cols, row):
            _st_sstore(obsNum, colNum, value)


class st_Variable():
    """Python class of views onto a single variable 
    in the Stata dataset in memory
    
    """
    def __init__(self, variable):
        if isinstance(variable, str):
            colNum = st_varindex(variable, True)
        elif isisntance(variable, int):
            numVars = st_nvar()
            if not -numVars <= variable < numVars:
                raise IndexError("variable number out of range")
            if variable < 0:
                variable = numVars + variable
            colNum = variable
        else:
            raise TypeError("argument should be str name or int index")
            
        if st_isstrvar(colNum):
            self._getter = _st_sdata
            self._setter = _st_sstore
        else:
            self._getter = _st_data
            self._setter = _st_store
            
        self._nobs = st_nobs()
        self._colNum = colNum
                         
    def __iter__(self):
        """return iterable of obs"""
        getter, colNum = self._getter, self._colNum
        return (getter(i, colNum) for i in range(self._nobs))
    
    def __len__(self):
        return self._nobs
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self._nobs)
            getter, colNum = self._getter, self._colNum
            return [getter(i, colNum) for i in range(start, stop, step)]
        if not isinstance(index, int):
            raise TypeError("index should be int or slice")
        return self._getter(self._colNum, index)
            
    def __setitem__(self, index, value):
        if isinstance(index, slice):
            index = range(self._nobs)[index]
        elif isinstance(index, int):
            index = (index,)
        else:
            raise TypeError("index should be int or slice")
        
        if not isinstance(value, collections.Iterable):
            if len(index) > 1:
                raise TypeError("this assignment requires iterable")
            value = (value,)
        else:
            if not hasattr(value, "__len__"):
                value = tuple(value)
            if len(value) != len(index):
                raise ValueError("iterable length does not match slice length")
        
        setter, colNum = self._setter, self._colNum
        for i,v in zip(index, value):
            setter(i, colNum, v)


class st_View():
    """Python class of views onto the Stata dataset in memory"""
    def __init__(self, rowNums=None, colNums=None, selectVar=None):
        if not rowNums:
            self._nObs = self._nRows = st_nobs()
            rowNums = tuple(range(self._nObs))
        else:
            # using set because there could be duplicates
            self._nObs = len(set(rowNums))
            self._nRows = len(rowNums)
        
        if not colNums:
            self._nVar = self._nCols = st_nvar()
            colNums = tuple(range(self._nVar))
        else:
            self._nVar = len(set(colNums))
            self._nCols = len(colNums)
            
        if not (selectVar is None or selectVar == ""):
            if isinstance(selectVar, str):
                selectVar = st_varindex(selectVar, True)
            elif not isinstance(selectVar, int):
                raise TypeError("selectVar should be str, int, or None")
            
            if selectVar == -1:
                rowNums = tuple(r for r in rowNums
                    if not any(st_ismissing(_st_data(r, c)) for c in colNums))
            else:
                rowNums = tuple(r for r in rowNums 
                                if _st_data(r, selectVar) != 0)
            
        self._rowNums = rowNums
        self._colNums = colNums
        
        self._formats = ["%11s" if st_isstrvar(c) else "%9.0g" 
                         for c in colNums]
        self._getters = [_st_sdata if st_isstrvar(c) else _st_data 
                         for c in colNums]
        self._setters = [_st_sstore if st_isstrvar(c) else _st_store 
                         for c in colNums]
                         
    def __iter__(self):
        """return iterable of obs"""
        getters, cols, rows = self._getters, self._colNums, self._rowNums
        return (tuple(g(r, c) for g,c in zip(getters, cols)) for r in rows)
    
    def __repr__(self):
        getters, colNums, rowNums = self._getters, self._colNums, self._rowNums
        nRows, nObs = self._nRows, self._nObs
        nCols, nVar = self._nCols, self._nVar
        
        fmts = self._formats
        
        nObsStr = str(nObs)
        nRowStr = "" if nRows == nObs else (" (" + str(nRows) + " rows)")
        nVarStr = str(nVar)
        nColStr = "" if nCols == nVar else (" (" + str(nCols) + " columns)")
        
        header = ("  {{txt}}" +
                  "obs: {{:>{m}}}{{}}\n vars: {{:>{m}}}{{}}".format(
                        m=max((len(nObsStr), len(nVarStr))))
                  )
        header = header.format(nObsStr, nRowStr, nVarStr, nColStr)
        
        if nRows == 0 or nCols == 0:
            return "\n" + header + "\n\n"
                            
        strList = []
        append = strList.append
        for c,i in zip(colNums, range(nCols)):
            if st_isstrvar(c):
                m = STR_FMT_RE.match(fmts[i])
                width = int(m.group(3)) if m else 11
                align = "<" if m and m.group(1) == "-" else ">"
                fmt = "{:" + align + str(width) + "}"
                append([fmt.format(_st_sdata(r,c)[:width]) for r in rowNums])
            else:
                fmt = fmts[i] if not STR_FMT_RE.match(fmts[i]) else "%9.0g"
                append([st_format(fmt, _st_data(r,c)) for r in rowNums])
        strList = [[inner[i] for inner in strList] for i in range(nRows)]
        
        maxRow = max(rowNums)
        nDigits = 1 if maxRow == 0 else floor(log(maxRow, 10)) + 1
        
        rowFmt = "{{txt}}{:>" + str(nDigits+1) + "}"
        colFmt = ["{:>" + str(len(s)) + "}" for s in strList[0]]
        
        for row, i in zip(strList, rowNums):
            row.insert(0, rowFmt.format("r" + str(i)) + "{res}")
        
        strList.insert(0, 
                       [rowFmt.format("")] + 
                       [colFmt[i].format("c" + str(v))
                                   for v,i in zip(colNums, range(nCols))])
        
        return ("\n" + header + "\n\n" + 
                "\n".join(" ".join(r for r in row) for row in strList))
        
    def toList(self):
        """return Stata data values as list of lists, 
        one sub-list per observation
        
        """
        getters, colNums, rowNums = self._getters, self._colNums, self._rowNums
        return [[g(r, c) for g,c in zip(getters, colNums)] for r in rowNums]
        
    def get(self, row, col):
        """get single value from view"""
        # use self.rowNums[row] rather than row because self's rows
        # are not necessarily the same as Stata's observation numbers
        return self._getters[col](self._rowNums[row], self._colNums[col])
        
    def list(self):
        """display values in current view object, 
        like Stata's -list- command
        
        """
        print(self.__repr__())
        
    def format(self, col, fmt):
        """set the display format for given column in view"""
        if not isinstance(fmt, str):
            raise TypeError("fmt argument should be str")
            
        if not isinstance(col, int):
            raise TypeError('col argument should be int')
        
        if not st_isfmt(fmt):
            raise ValueError(fmt + " is not a valid Stata format")
            
        if st_isstrfmt(fmt) != st_isstrvar(self._colNums[col]):
            raise ValueError("format does not match Stata variable type")
        
        self._formats[col] = fmt
        
    @property
    def rows(self):
        return self._rowNums
        
    @property
    def cols(self):
        return self._colNums
        
    @property
    def nRows(self):
        return self._nRows
        
    @property
    def nCols(self):
        return self._nCols
                
    def __eq__(self, other):
        """determine if self is equal to other"""
        if not isinstance(other, st_View): return False
        
        if (not len(self._rowNums) == len(other._rowNums) or 
            not len(self._colNums) == len(other._colNums)):
                return False
        
        rows1, cols1 = self._rowNums, self._colNums
        rows2, cols2 = other._rowNums, other._colNums
        getters, nCols = self._getters, self._nCols
        return all(st_isstrvar(c1) == st_isstrvar(c2) and
                   all(getters[i](r1, c1) == getters[i](r2, c2)
                        for r1, r2 in zip(rows1, rows2)
                       )
                   for c1, c2, i in zip(cols1, cols2, range(nCols))
                  )
        
    def _checkIndex(self, priorIndex, nextIndex):
        """To be used with __init__, __getitem__, and __setitem__ .
        Checks that index is well-formed and converts it to a 
        consistent form.
        
        """
        if nextIndex is None: return priorIndex
        if isinstance(nextIndex, slice):
            start, stop, step = nextIndex.indices(len(priorIndex))
            finalIndex = priorIndex[start:stop:step]
        elif isinstance(nextIndex, collections.Iterable):
            if not hasattr(nextIndex, "__len__"):
                nextIndex = tuple(nextIndex)
            if not all(isinstance(i, int) for i in nextIndex):
                raise TypeError("individual indices must be int")
            finalIndex = tuple(priorIndex[i] for i in nextIndex)
        else:
            if not isinstance(nextIndex, int):
                raise TypeError("index must be slice, iterable of int, or int")
            finalIndex = (priorIndex[nextIndex],)
        return finalIndex
    
    def __getitem__(self, index):
        """return 'sub-view' of view with given indices"""
        if not isinstance(index, tuple) or not 1 <= len(index) <= 2:
            raise TypeError("data index must be [rows,cols] or [rows,]")
        newRows = self._checkIndex(self._rowNums, index[0])
        newCols = self._checkIndex(self._colNums, 
                                   index[1] if len(index) == 2 else None)
        return st_View(rowNums=newRows, colNums=newCols)
        
    def __setitem__(self, index, value):
        """change values if in 'sub-view' of view with given indices"""
        if not isinstance(index, tuple) or len(index) > 2:
            raise ValueError("data index must be [rows,cols] or [rows,]")
        newRows = self._checkIndex(self._rowNums, index[0])
        newCols = self._checkIndex(self._colNums, 
                                   index[1] if len(index) == 2 else None)
        
        nNewRows = len(newRows)
        nNewCols = len(newCols)
        
        if nNewRows == 0 or nNewCols == 0:
            return
        
        def tupleIzer(x):
            if isinstance(x, str) or not isinstance(x, collections.Iterable):
                return (x,)
            return tuple(x)
            
        if isinstance(value, st_Matrix) or isinstance(value, st_View):
            value = value.toList()
            # no need to go through tupleIzer here, so maybe rewrite
        
        # force input into 2d structure
        if (isinstance(value, str) or
                not isinstance(value, collections.Iterable)):
            value = ((value,),)
        else:
            value = tuple(tupleIzer(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (nNewRows == 1 and len(value) == nNewCols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
        
        # check lengths
        if not len(value) == nNewRows:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == nNewCols for v in value):
            raise ValueError("inner dimensions do not match number of columns")    
        
        setters = self._setters
        for row, i in zip(newRows, range(nNewRows)):
            for col, j in zip(newCols, range(nNewCols)):
                setters[col](row, col, value[i][j])


def st_viewvars(viewObj):
    """return column numbers from st_View object"""
    if not isinstance(viewObj, st_View):
        raise TypeError("argument should be a View")
    return viewObj._colNums


def st_viewobs(viewObj):
    """return row numbers from st_View object"""
    if not isinstance(viewObj, st_View):
        raise TypeError("argument should be a View")
    return viewObj._rowNums

    
class st_Matrix():
    """Python class of views onto Stata matrices"""
    def __init__(self, matname, rowNums=None, colNums=None, fmt=None):
        nRows, nCols = st_rows(matname), st_cols(matname)
        if nRows == 0 or nCols == 0:
            # in Mata, st_matrix returns J(0,0) if matrix doesn't exist, 
            # but typical Python thing would be to raise an error
            raise ValueError("cannot find a Stata matrix with that name")
        self._matname = matname
        self._fmt = fmt or "%10.0g"
        self._rowNums = rowNums if rowNums is not None else tuple(range(nRows))
        self._colNums = colNums if colNums is not None else tuple(range(nCols))
        # in next line, don't want st_rows() because rowNums does not 
        # have to equal range(st_rows())
        self._nRows = len(self._rowNums)
        self._nCols = len(self._colNums)
        
    def __iter__(self):
        """return iterable of rows"""
        matname, cols, rows = self._matname, self._colNums, self._rowNums
        return (tuple(st_matrix_el(matname, r, c) for c in cols) for r in rows)
        
    def format(self, fmt):
        """Change the display format of the matrix.
        Argument -fmt- should be a valid Stata numerical format.
        
        """
        if not isinstance(fmt, str):
            raise TypeError('fmt argument should be str')
        if st_isstrfmt(fmt) or not st_isfmt(fmt):
            raise ValueError("given format is not a valid numeric format")
        self._fmt = fmt
        
    def list(self, fmt=None):
        """like Stata's -matrix list- command"""
        if fmt is None:
            fmt = self._fmt
        elif not st_isnumfmt(fmt):
            raise ValueError("given format is not a valid numeric format")
        
        matname, rowNums, colNums = self._matname, self._rowNums, self._colNums
        maxRow = max(rowNums)
        
        nDigits = (1 if self._nRows == 0 or maxRow == 0
                     else floor(log(maxRow, 10)) + 1)
        
        fmtWidth = len(st_format(fmt, 0))
        
        rowFmt = "{{txt}}{:>" + str(nDigits+1) + "}"
        colFmt = "{:>" + str(fmtWidth) + "}"
        
        # print matrix info and column headers
        print("\n{{txt}}{}[{},{}]".format(matname, self._nRows, self._nCols))
        print(rowFmt.format("") + " " + 
              " ".join(colFmt.format("c" + str(i)) for i in colNums))
        
        # print rows
        for r in rowNums:
            print(rowFmt.format("r" + str(r)) + "{res} " + 
                  " ".join(st_format(fmt, st_matrix_el(matname, r, c)) 
                           for c in colNums))
        
    def toList(self):
        """return matrix values in list of lists, 
        one sub-list per row
        
        """
        matname, colNums, rowNums = self._matname, self._colNums, self._rowNums
        return [[st_matrix_el(matname, r, c) for c in colNums] for r in rowNums]
        
    def get(self, row, col):
        """get single item from matrix"""
        # use self._rowNums[row] rather than row directly because 
        # self's rows might not be the same as the Stata matrix's
        return st_matrix_el(self._matname, 
                            self._rowNums[row], self._colNums[col])
        
    def __repr__(self):
        """string representation of st_Matrix object"""
        matname, rowNums, colNums = self._matname, self._rowNums, self._colNums
        maxRow = max(rowNums)
        fmt = self._fmt
        
        nDigits = (1 if self._nRows == 0 or maxRow == 0
                     else floor(log(maxRow, 10)) + 1)
        
        fmtWidth = len(st_format(fmt, 0))
        
        rowFmt = "{{txt}}{:>" + str(nDigits+1) + "}"
        colFmt = "{:>" + str(fmtWidth) + "}"
        
        # matrix info, column headers, and generator of row strs
        header = "\n{{txt}}{}[{},{}]".format(matname, self._nRows, self._nCols)
        colTop = (rowFmt.format("") + " " +
                  " ".join(colFmt.format("c" + str(i)) for i in colNums))
        rowGen = (rowFmt.format("r" + str(r)) + 
                  "{res} " +
                  " ".join(st_format(fmt, st_matrix_el(matname, r, c)) 
                           for c in colNums)
                  for r in rowNums)
        
        return header + "\n" + colTop + "\n" + "\n".join(rowGen)
        
    @property
    def rows(self):
        return self._rowNums
        
    @property
    def cols(self):
        return self._colNums
        
    @property
    def nRows(self):
        return self._nRows
        
    @property
    def nCols(self):
        return self._nCols
                
    def __eq__(self, other):
        """determine if self is equal to other"""
        if not isinstance(other, st_Matrix): return False
        
        if (not len(self._rowNums) == len(other._rowNums) or 
            not len(self._colNums) == len(other._colNums)):
                return False
        
        mat1, rows1, cols1 = self._matname, self._rowNums, self._colNums
        mat2, rows2, cols2 = other._matname, other._rowNums, other._colNums
        return all(st_matrix_el(mat1, r1, c1) == st_matrix_el(mat2, r2, c2)
                   for r1, r2 in zip(rows1, rows2) 
                   for c1, c2 in zip(cols1, cols2))
        
    def _checkIndex(self, priorIndex, nextIndex):
        """To be used with __getitem__ and __setitem__ .
        Checks that index is well-formed and converts it 
        to consistent form.
        
        """
        if nextIndex is None: return priorIndex
        if isinstance(nextIndex, slice):
            start, stop, step = nextIndex.indices(len(priorIndex))
            finalIndex = priorIndex[start:stop:step]
        elif isinstance(nextIndex, collections.Iterable):
            if not hasattr(nextIndex, "__len__"):
                nextIndex = tuple(nextIndex)
            if not all(isinstance(i, int) for i in nextIndex):
                raise TypeError("individual indices must be int")
            finalIndex = tuple(priorIndex[i] for i in nextIndex)
        else:
            if not isinstance(nextIndex, int):
                raise TypeError("index must be slice, iterable of int, or int")
            finalIndex = (priorIndex[nextIndex],)
        return finalIndex
    
    def __getitem__(self, index):
        """return st_Matrix object containing rows and cols 
        specified by index tuple
        
        """
        if not isinstance(index, tuple) or not 1 <= len(index) <= 2:
            raise TypeError("matrix index must be [rows,cols] or [rows,]")
        newRows = self._checkIndex(self._rowNums, index[0])
        newCols = self._checkIndex(self._colNums, 
                                   index[1] if len(index) == 2 else None)
        return st_Matrix(self._matname, 
                         rowNums=newRows, colNums=newCols, fmt=self._fmt)
        
    def __setitem__(self, index, value):
        """Replace values in specified rows and cols of -index- tuple.
        The shape of -value- should match the shape implied by -index-.
        
        """
        if not isinstance(index, tuple) or len(index) > 2:
            raise ValueError("matrix index must be [rows,cols] or [rows,]")
        newRows = self._checkIndex(self._rowNums, index[0])
        newCols = self._checkIndex(self._colNums, 
                                   index[1] if len(index) == 2 else None)
        
        nNewRows = len(newRows)
        nNewCols = len(newCols)
        
        if nNewRows == 0 or nNewCols == 0:
            return
        
        def tupleIzer(x):
            if isinstance(x, str):
                raise TypeError("matrix values may not be str")
            if not isinstance(x, collections.Iterable):
                return (x,)
            return tuple(x)
            
        if isinstance(value, st_Matrix) or isinstance(value, st_View):
            value = value.toList()
            # No need to go through tupleIzer here, so maybe rewrite.
            # If rewriting around tupleIzer, st_View variables should be
            # checked to be sure they are numeric.
        
        # force input into 2d structure
        if isinstance(value, str):
            raise TypeError("matrix values must be numeric; str not allowed")
        if not isinstance(value, collections.Iterable):
            value = ((value,),)
        else:
            value = tuple(tupleIzer(v) for v in value)
            
        # Reformation above is wrong for a single-row assignment, where
        # values [val1, val2, ...] should be interpreted as  
        # single row: [[val1, val2, ...]]. Procedure above makes it   
        # into [[val1], [val2], ...] (the correct assumption otherwise).
        if (nNewRows == 1 and len(value) == nNewCols and 
                all(len(v) == 1 for v in value)):
            value = [[v[0] for v in value]]
        
        # check lengths
        if not len(value) == nNewRows:
            raise ValueError("length of value does not match number of rows")
        if not all(len(v) == nNewCols for v in value):
            raise ValueError("inner dimensions do not match number of columns")    
        
        matname = self._matname
        for row, i in zip(newRows, range(nNewRows)):
            for col, j in zip(newCols, range(nNewCols)):
                st_matrix_el(matname, row, col, value[i][j])
