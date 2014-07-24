
__version__ = "0.1.2"

class MissingValue():
    """A class to mimic some of the properties of Stata's missing values.
    
    The class is intended for mimicking only the 27 regular missing
    values ., .a, .b, .c, etc.
    
    Users wanting MissingValue instances should access members of
    MISSING_VALS rather than create new instances.
    
    """
    def __init__(self, index):
        """Users wanting MissingValue instances should access members of
        MISSING_VALS rather than create new instances.
        
        """
        self.value = float.fromhex(
            "".join(('0x1.0', hex(index)[2:].zfill(2), 'p+1023'))
        )
        self.name = "." if index == 0 else "." + chr(index + 96)
        self.index = index
            
    def __abs__(self):
        return self
        
    def __add__(self, other):
        return MISSING
        
    def __bool__(self):
        return True
        
    def __divmod__(self, other):
        return MISSING, MISSING
        
    def __eq__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value == other_val
        
    def __floordiv__(self, other):
        return MISSING
        
    def __ge__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value >= other_val
        
    def __gt__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value > other_val
        
    def __hash__(self):
        return self.value.__hash__()
        
    def __le__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value <= other_val
        
    def __lt__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value < other_val
        
    def __mod__(self, other):
        return MISSING
        
    def __mul__(self, other):
        return MISSING
        
    def __ne__(self, other):
        other_val = other.value if isinstance(other, MissingValue) else other
        return self.value != other_val
        
    def __neg__(self):
        return MISSING
        
    def __pos__(self):
        return MISSING
        
    def __pow__(self, other):
        return MISSING
        
    def __radd__(self, other):
        return MISSING
        
    def __rdivmod__(self, other):
        return MISSING, MISSING
        
    def __repr__(self):
        return self.name
        
    def __rfloordiv__(self, other):
        return MISSING
        
    def __rmod__(self, other):
        return MISSING
        
    def __rmul__(self, other):
        return MISSING
        
    def __round__(self, ndigits=None):
        return self
        
    def __rpow__(self, other):
        return MISSING
        
    def __rsub__(self, other):
        return MISSING
        
    def __rtruediv__(self, other):
        return MISSING
        
    def __sub__(self, other):
        return MISSING
        
    def __str__(self):
        return self.name
        
    def __truediv__(self, other):
        return MISSING


MISSING_VALS = tuple(MissingValue(i) for i in range(27))
MISSING = MISSING_VALS[0]


def get_missing(value):
    """Get a MissingValue instance corresponding to a given float.
    
    The MissingValue instances returned by this function are analogues
    of the 27 regular missing values in Stata: ., .a, .b, .c, etc.
    If the given float is not the exact value associated with a Stata 
    missing value, the returned instance might be surprising.
    For interactive use, it may be easier to access members of
    MISSING_VALS, which is a tuple of the 27 regular missing values.
    
    Parameters
    ----------
    value : float (or coercible to float)
    
    Returns
    -------
    MissingValue instance
    
    """
    if value is None: return MISSING
    # apply float() partly to test that value is numeric, 
    # partly to ensure that it has the hex method
    value = float(value)
    # return default MissingValue if requesting based on value
    # 1. in non-missing range 
    # 2. above highest recognized missing value
    # 3. in negative missing range
    if value <= 8.988465674311579e+307 or value > 9.045521364627034e+307:
        id = 0
    else:
        id = int(value.hex()[5:7], 16)
        if not 0 <= id <= 26: id = 0
    return MISSING_VALS[id]
        