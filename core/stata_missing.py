
__version__ = "0.1.0"

class MissingValue():
    def __init__(self, missType):
        self.value = float.fromhex('0x1.0' + 
                                   hex(missType)[2:].zfill(2) + 'p+1023')
        self.name = "." if missType == 0 else "." + chr(missType + 96)
        self.missType = missType
            
    def __abs__(self):
        return self
        
    def __add__(self, other):
        return MISSING
        
    def __bool__(self):
        return True
        
    def __divmod__(self, other):
        return MISSING, MISSING
        
    def __eq__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value == otherVal
        
    def __floordiv__(self, other):
        return MISSING
        
    def __ge__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value >= otherVal
        
    def __gt__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value > otherVal
        
    def __hash__(self):
        return self.value.__hash__()
        
    def __le__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value <= otherVal
        
    def __lt__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value < otherVal
        
    def __mod__(self, other):
        return MISSING
        
    def __mul__(self, other):
        return MISSING
        
    def __ne__(self, other):
        otherVal = other.value if isinstance(other, MissingValue) else other
        return self.value != otherVal
        
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
        
    def __round__(self, nDigits=None):
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
    """get a MissingValue instance that corresponds to given float value
    input: float
    returns: MissingValue instance
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
        