import collections


__version__ = "0.1.0"


class StataVarVals():
    """A class for intermediate values when calculating with data
    variables within a Dta object or in Stata. Variables themselves 
    are referenced through an instance of StataVariable. 
    
    This class is meant for internal use.
    
    Example
    -------    
    A user can create or replace a data variable called "target" with
    
        src.target_ = src.input1_ - 2 * src.input2_
    
    Where `src` is either an instance of Dta or, in Stata, obtained from
    `st_mirror`. When `input1_` and `input2_` attributes are looked up,
    instances of StataVariable are returned (assuming variables "input1"
    and "input2" exist). The calculation on the right hand side results
    in an instance of StataVarVals holding the calculated values. The 
    assignment statement replaces values if the variable exists, or
    adds a new variable to the dataset.
    
    """
    def __init__(self, values):
        self.values = values
    
    def __setitem__(self, index, value):
        self.values[index] = value
        
    def __getitem__(self, index):
        return self.values[index]
            
    def __abs__(self):
        return StataVarVals([abs(v) for v in self.values])
        
    def __add__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v + o for (v,o) in zip(self.values, other)])
        return StataVarVals([v + other for v in self.values])
        
    def __bool__(self):
        return StataVarVals([bool(v) for v in self.values])
        
    def __eq__(self, other):
        if isinstance(other, collections.Iterable):
            values = self.values
            return StataVarVals(
                [values[i] == other[i] for i in range(len(self))]
            )
        return StataVarVals([v == other for v in self.values])
        
    def __float__(self):
        return StataVarVals([float(v) for v in self.values])
        
    def __floordiv__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v // o for (v,o) in zip(self.values, other)])
        return StataVarVals([v // other for v in self.values])
        
    def __ge__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v >= o for (v,o) in zip(self.values, other)])
        return StataVarVals([v >= other for v in self.values])
        
    def __gt__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v > o for (v,o) in zip(self.values, other)])
        return StataVarVals([v > other for v in self.values])
        
    def __iadd__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v + o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v + other for v in self.values]
        return self
        
    def __ifloordiv__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v // o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v // other for v in self.values]
        return self
        
    def __imod__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v % o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v % other for v in self.values]
        return self
        
    def __imul__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v * o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v * other for v in self.values]
        return self
        
    def __int__(self):
        return StataVarVals([int(v) for v in self.values])
        
    def __ipow__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v ** o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v ** other for v in self.values]
        return self
        
    def __isub__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v - o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v - other for v in self.values]
        return self
        
    def __iter__(self):
        values = self.values
        for v in values:
            yield v
        
    def __itruediv__(self, other):
        if isinstance(other, collections.Iterable):
            self.values = [v / o for (v,o) in zip(self.values, other)]
        else:
            self.values = [v / other for v in self.values]
        return self
        
    def __le__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v <= o for (v,o) in zip(self.values, other)])
        return StataVarVals([v <= other for v in self.values])
        
    def __len__(self):
        return len(self.values)
        
    def __lt__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v < o for (v,o) in zip(self.values, other)])
        return StataVarVals([v < other for v in self.values])
        
    def __mod__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v % o for (v,o) in zip(self.values, other)])
        return StataVarVals([v % other for v in self.values])
        
    def __mul__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v * o for (v,o) in zip(self.values, other)])
        return StataVarVals([v * other for v in self.values])
        
    def __ne__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v != o for (v,o) in zip(self.values, other)])
        return StataVarVals([v != other for v in self.values])
        
    def __neg__(self):
        return StataVarVals([-v for v in self.values])
        
    def __pos__(self):
        return self
        
    def __pow__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v ** o for (v,o) in zip(self.values, other)])
        return StataVarVals([v ** other for v in self.values])
        
    def __radd__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o + v for (v,o) in zip(self.values, other)])
        return StataVarVals([other + v for v in self.values])
        
    def __rfloordiv__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o // v for (v,o) in zip(self.values, other)])
        return StataVarVals([other // v for v in self.values])
        
    def __rmod__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o % v for (v,o) in zip(self.values, other)])
        return StataVarVals([other % v for v in self.values])
        
    def __rmul__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o * v for (v,o) in zip(self.values, other)])
        return StataVarVals([other * v for v in self.values])
        
    def __round__(self, n=None):
        return StataVarVals([round(v, n) for v in self.values])
        
    def __rpow__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o ** v for (v,o) in zip(self.values, other)])
        return StataVarVals([other ** v for v in self.values])
        
    def __rsub__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o - v for (v,o) in zip(self.values, other)])
        return StataVarVals([other - v for v in self.values])
        
    def __rtruediv__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([o / v for (v,o) in zip(self.values, other)])
        return StataVarVals([other / v for v in self.values])
        
    def __sub__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v - o for (v,o) in zip(self.values, other)])
        return StataVarVals([v - other for v in self.values])
        
    def __truediv__(self, other):
        if isinstance(other, collections.Iterable):
            return StataVarVals([v / o for (v,o) in zip(self.values, other)])
        return StataVarVals([v / other for v in self.values])
        
    
class StataVariable(StataVarVals):
    """A class for referencing a data variable within a Dta object or in
    Stata. Class instances are created when the user accesses a variable
    with "src.varname_", where "src" is either a Dta instance or, in 
    Stata, obtained from `st_mirror`, and "varname" is the full variable 
    name or an unambiguous abbreviation. Any property ending with a
    single underscore is assumed to be a reference to a variable.
    
    This class is meant for internal use.
    
    """

    def __init__(self, source, name):
        self.source = source
        self.name = name
        
    @property
    def values(self):
        src = self.source
        get = src.get
        c = src.index(self.name)
        return [get(r,c) for r in range(len(src))]
        
    def __iter__(self):
        src = self.source
        get = src.get
        c = src.index(self.name)
        for r in range(len(src)):
            yield get(r, c)
        
    def __setattr__(self, name, value):
        if name == "values":
            src = self.source
            c = src.index(self.name)
            src[:, c] = value
        else:
            self.__dict__[name] = value
    
    def __setitem__(self, index, value):
        src = self.source
        src[index, src.index(self.name)] = value
        
    def __getitem__(self, index):
        src = self.source
        get = src.get
        c = src.index(self.name)
    
        if isinstance(index, int):
            return get(index, c)
            
        if isinstance(index, slice):
            start, stop, step = index.indices(len(src))
            index = range(start, stop, step)
        elif not isinstance(index, collections.Iterable):
            raise TypeError("index must be slice, iterable, or int")
        
        return [get(i, c) for i in index]
        
    def __len__(self):
        return len(self.source)
        
    def __str__(self):
        return "variable {} of {}".format(self.name, self.source)
    
