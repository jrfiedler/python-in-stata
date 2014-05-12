import math

from stata_missing import MissingValue, MISSING as mv, get_missing
from stata_variable import StataVarVals


__version__ = "0.1.0"


def _is_missing(x):
    if isinstance(x, MissingValue) or x is None:
        return True
    if not isinstance(x, int) and not isinstance(x, float):
        raise TypeError("int, float, or MissingValue instance required")
    # the following is the range allowed by math functions, which is
    # slightly more restrictive that what is allowed in dta files
    if x < -8.988465674311579e+307 or x > 8.988465674311579e+307:
        return True
    return False

def st_abs(x):
    """Absolute value function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Absolute value of x when x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals(
            [mv if _is_missing(v) else abs(v) for v in x.values]
        )
    if _is_missing(x):
        return mv
    return abs(x)

def st_acos(x):
    """Inverse cosine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse cosine (measured in radians) when -1 <= x <= 1,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1 <= v <= 1
            else math.acos(v) for v in x.values
        ])
    if _is_missing(x) or not -1 <= x <= 1:
        return mv
    return math.acos(x)

def st_acosh(x):
    """Inverse hyperbolic cosine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse hyperbolic cosine when x is non-missing and x >= 1,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or v < 1
            else math.acosh(v) for v in x.values
        ])
    if _is_missing(x) or x < 1:
        return mv
    return math.acosh(x)

def st_asin(x):
    """Inverse sine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse sine (measured in radians) when -1 <= x <= 1,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1 <= v <= 1
            else math.asin(v) for v in x.values
        ])
    if _is_missing(x) or not -1 <= x <= 1:
        return mv
    return math.asin(x)

def st_asinh(x):
    """Inverse hyperbolic sine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse hyperbolic sine when x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) else math.asinh(v) for v in x.values
        ])
    if _is_missing(x):
        return mv
    return math.asinh(x)

def st_atan(x):
    """Inverse tangent function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse tangent (measured in radians) when x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) else math.atan(v) for v in x.values
        ])
    if _is_missing(x):
        return mv
    return math.atan(x)
    
def _atan2(x, y):
    if _is_missing(x) or _is_missing(y):
        return mv
    return math.atan2(x, y)

def st_atan2(x, y):
    """Two-parameter inverse tangent function.
    
    This function considers the signs of both x and y when 
    calculating angle.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    y : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse tangent of x/y (measured in radians) when 
    x and y are both non-missing, MISSING (".") otherwise.
    
    """
    if isinstance(x, StataVarVals):
        if isinstance(y, StataVarVals):
            return StataVarVals([
                _atan2(vx, vy) for vx, vy in zip(x.values, y.values)
            ])
        elif _is_missing(y):
            return StataVarVals([mv for v in x.values])
        else:
            return StataVarVals([_atan2(v, y) for v in x.values])
    if isinstance(y, StataVarVals):
        if _is_missing(x):
            return StataVarVals([mv for v in y.values])
        else:
            return StataVarVals([_atan2(x, v) for v in y.values])
    return _atan2(x, y)
    
def st_atanh(x):
    """Inverse hyperbolic tangent function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Inverse hyperbolic tangent when x is non-missing, 
    MISSING (".") otherwise.
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1 < v < 1
            else math.atanh(v) for v in x.values
        ])
    if _is_missing(x) or not -1 < x < 1:
        return mv
    return math.atanh(x)

def _ceil(x):
    if isinstance(x, MissingValue):
        return x
    if x is None:
        return mv
    if not isinstance(x, int) and not isinstance(x, float):
        raise TypeError("int, float, or MissingValue instance required")
    if not -8.988465674311579e+307 <= x <= 8.988465674311579e+307:
        return get_missing(x)
    return math.ceil(x)
    
def st_ceil(x):
    """Ceiling function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    If x is non-missing, returns the smallest int value >= x.
    If x is a float or int in Stata's missing value range, 
        returns the corresponding MissingValue instance.
    If x is a MissingValue instance, returns x.
    If x is None, returns MISSING (".").
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_ceil(v) for v in x.values])
    return _ceil(x)

def _cloglog(x):
    if _is_missing(x) or not 0 < x < 1:
        return mv
    log = math.log
    return log(-log(1 - x))
    
def st_cloglog(x):
    """Complementary log log function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    log(-log(1 - x)) if x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_cloglog(v) for v in x.values])
    return _cloglog(x)

def _comb(n, k):
    if (_is_missing(n) or not 1 <= n <= 1e+305 or not n == math.floor(n) or 
            _is_missing(k) or not 0 <= k <= n or not k == math.floor(k)):
        return mv
    
    try:
        numer = 1.0
        denom = 1.0
        for t in range(1, int(min(k, n - k)) + 1):
            numer *= n
            denom *= t
            n -= 1
    except OverflowError:
        return mv

    inf = float('inf')
    value = numer / denom
    if numer == inf or denom == inf or value > 8.988465674311579e+307:
        return mv
    
    if -2147483647 <= value <= 2147483620:  # if it fits within Stata long
        return int(value)
    return value
    
def st_comb(n, k):
    """Combinatorial function.
    
    Parameters
    ----------
    n : float, int, MissingValue instance, or None
    k : float, int, MissingValue instance, or None
    
    Returns
    -------
    n! / (k! (n-k)!) if n and k are non-missing and n < 1e+305,
    MISSING (".") otherwise
    
    """
    if isinstance(n, StataVarVals):
        if isinstance(k, StataVarVals):
            return StataVarVals([
                _comb(vn, vk) for vn, vk in zip(n.values, k.values)
            ])
        elif _is_missing(k):
            return StataVarVals([mv for v in n.values])
        else:
            return StataVarVals([_comb(v, k) for v in n.values])
    if isinstance(k, StataVarVals):
        if _is_missing(n):
            return StataVarVals([mv for v in k.values])
        else:
            return StataVarVals([_comb(n, v) for v in k.values])
    return _comb(n, k)

def st_cos(x):
    """Cosine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None;
        angle in radians
    
    Returns
    -------
    Cosine of x if -1e+18 <= x <= 1e+18,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1e+18 <= v <= 1e+18
            else math.cos(v) for v in x.values
        ])
    if _is_missing(x) or not -1e+18 <= x <= 1e+18:
        return mv
    return math.cos(x)
    
def _cosh(x):
    # the domain stated in Stata is approximate
    if _is_missing(x) or not -709.8 <= x <= 709.8:
        return mv
    v = math.cosh(x)
    return v if -8.988465674311579e+307 <= v <= 8.988465674311579e+307 else mv

def st_cosh(x):
    """Hyperbolic cosine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Hyperbolic cosine of x if x is non-missing (see note below),
    MISSING (".") otherwise
    
    Note
    ----
    The hyperbolic cosine of x can fall in Stata's missing range
    for non-missing x. For x outside of -709 < x < 709 (approximate)
    this function will return MISSING (".").    
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_cosh(v) for v in x.values])
    return _cosh(x)
    
def _digamma(x):    
    # Algorithm
    # ---------
    # Bernardo, José M. (1976). "Algorithm AS 103 Psi (Digamma) Function".
    # Applied Statistics 25 (3): 315–317
    #  -> This paper's function returns zero for negative inputs.
    #     Wikipedia article below contains information for extending
    #     to negative inputs.
    #     
    # Wikipedia article on digamma function:
    #     http://en.wikipedia.org/wiki/Digamma_function
    
    if _is_missing(x):
        return mv
    
    value = 0
    
    # if x < 0, use reflection formula
    if x <= 0:
        flrx = math.floor(x)
        if x == flrx:
            return mv
        if x - flrx != 0.5:
            value -= math.pi / math.tan(math.pi * x)
        x = 1 - x
        
    while x < 8:
        value -= 1. / x
        x += 1
        
    value += math.log(x) - 0.5 / x
        
    if x < 1e10:
        y = 1. / (x * x)
        value -= y * (1./12 - y * (1./120 - y * (1./252 - y * (1./240 - 
            y * (5./660 - y * (691./32760 - y * 1./12))))))
        
    return value

def st_digamma(x):
    """Digamma (psi) function, the derivative of `st_lngamma`.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Digamma of x if x is non-missing, not zero, and not a negative integer,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_digamma(v) for v in x.values])
    return _digamma(x)

def st_exp(x):
    """Exponential function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Exponential of x (exp(x)) if x is non-missing and x <= 709,
    MISSING (".") otherwise.
    
    Note
    ----
    The exponential of x can fall in Stata's missing range for
    non-missing x. For x greater than approximately 709 this
    function will return MISSING (".").  
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or v > 709.09
            else min(mv, math.exp(v)) for v in x.values
        ])
    if _is_missing(x) or x > 709.09:
        return mv
    return min(mv, math.exp(x))
    
def _floor(x):
    if isinstance(x, MissingValue):
        return x
    if x is None:
        return mv
    if not isinstance(x, int) and not isinstance(x, float):
        raise TypeError("int, float, or MissingValue instance required")
    if not -8.988465674311579e+307 <= x <= 8.988465674311579e+307:
        return get_missing(x)
    return math.floor(x)

def st_floor(x):
    """Floor function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    If x is non-missing, returns the largest int value <= x.
    If x is a float or int in Stata's missing value range, 
        returns the corresponding MissingValue instance.
    If x is a MissingValue instance, returns x.
    If x is None, returns MISSING (".").
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_floor(v) for v in x.values])
    return _floor(x)
    
def _int(x):
    if isinstance(x, MissingValue):
        return x
    if x is None:
        return mv
    if not isinstance(x, int) and not isinstance(x, float):
        raise TypeError("int, float, or MissingValue instance required")
    if not -8.988465674311579e+307 <= x <= 8.988465674311579e+307:
        return get_missing(x)
    return int(x)

def st_int(x):
    """Integer truncation function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    If x is non-missing, returns the int value between x and zero
        closest to x (equal to x if x is integer-valued).
    If x is a float or int in Stata's missing value range, 
        returns the corresponding MissingValue instance.
    If x is a MissingValue instance, returns x.
    If x is None, returns MISSING (".").
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_int(v) for v in x.values])
    return _int(x)

def st_invcloglog(x):
    """Inverse of the complementary log log function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    1 - exp(-exp(x)) if x is non-missing,
    MISSING (".") otherwise
    
    """
    # This differs from Stata's invcloglog for x > 709 (Stata 13.1 on Win7),
    # where invcloglog(x) = . for x > 709.
    exp = math.exp
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v)
            else 1.0 if v > 5
            else 0.0 if v < -40
            else 1.0 - exp(-exp(v)) for v in x.values
        ])
    if _is_missing(x):
        return mv
    if x > 5:
        return 1.0
    if x < -40:
        return 0.0
    return 1.0 - exp(-exp(x))
    
def _invlogit(x):
    if _is_missing(x):
        return mv
    if x >= 40:
        return 1.0
    if x <= -750:
        return 0.0
    return math.exp(x)/(1 + math.exp(x))

def st_invlogit(x):
    """Inverse logit function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    exp(x) / (1 + exp(x)) if x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_invlogit(v) for v in x.values])
    return _invlogit(x)

def st_ln(x):
    """Natural log function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Natural log of x if x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or v <= 0 else math.log(v) for v in x.values
        ])
    if _is_missing(x) or x <= 0:
        return mv
    return math.log(x)
    
def _lnfactorial(n):
    # This differs from Stata for results in the missing range.
    # For example, in Stata 13.1 on Windows 7, lnfactorial(1.285e305) = .k_
    if _is_missing(n) or not n == math.floor(n) or n < 0 or n >= 1.282e+305:
        return mv
    #value = math.lgamma(n + 1)
    #return value if value <= 8.988465674311579e+307 else mv
    return min(mv, math.lgamma(n + 1))

def st_lnfactorial(n):
    """Log of factorial function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    log(x!) if x is integer-valued and x >= 0,
    MISSING (".") otherwise
    
    Note
    ----
    The log factorial of x can fall in Stata's missing range for
    non-missing x. This occurs for inputs > 1.28e+305 (approximate).
    In these cases, MISSING (".") will be returned.
    
    """
    if isinstance(n, StataVarVals):
        return StataVarVals([_lnfactorial(v) for v in n.values])
    return _lnfactorial(n)
    
def _lngamma(x):
    # This differs from Stata for x < -2,147,483,648 (Stata 13.1 on Win7).
    # There lngamma(x) = . for x < -2,147,483,648.
    if _is_missing(x) or (x <= 0 and x == math.floor(x)) or x >= 1.282e+305:
        return mv
    #v = math.lgamma(x)
    #return v if v <= 8.988465674311579e+307 else mv
    return min(mv, math.lgamma(x))

def st_lngamma(x):
    """Log gamma function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    The log of the gamma function of x if x is non-missing, 
    x > -2,147,483,648, and x is not a negative integer.
    Otherwise, MISSING (".") is returned.
    
    Note
    ----
    The log of gamma of x can fall in Stata's missing range for
    non-missing x. This occurs for inputs > 1.28e+305 (approximate).
    In these cases, MISSING (".") will be returned.
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_lngamma(v) for v in x.values])
    return _lngamma(x)

st_log = st_ln

def st_log10(x):
    """Log-base-10 function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    The log-base-10 of x if x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or v <= 0
            else math.log(v, 10) for v in x.values
        ])
    if _is_missing(x) or x <= 0:
        return mv
    return math.log(x, 10)
    
def _logit(x):
    if _is_missing(x) or not 0 < x < 1:
        return mv
    v = math.log(x / (1 - x))
    return v if -8.988465674311579e+307 <= v <= 8.988465674311579e+307 else mv

def st_logit(x):
    """Logit function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    log(x / (1 - x)) if 0 < x < 1,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_logit(v) for v in x.values])
    return _logit(x)
    
def _max(*args, sub_max=None):
    input = [a for a in args if not _is_missing(a)]
    if sub_max is not None:
        input.append(sub_max)
    return max(input) if not len(input) == 0 else mv

def st_max(*args):
    """Max function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
        (2 or more such inputs allowed)
    
    Returns
    -------
    max(x1, x2, ...) if any x is non-missing (with missing values ignored).
    Otherwise, MISSING (".") returned.
    
    """
    if len(args) <= 1:
        raise TypeError("need at least 2 arguments")
    vectors = [a for a in args if isinstance(a, StataVarVals)]
    scalars = [
        a for a in args if not isinstance(a, StataVarVals) and not _is_missing(a)
    ]
    if len(vectors) != 0:
        sca_max = max(scalars) if not len(scalars) == 0 else None
        return StataVarVals([_max(*v, sub_max=sca_max) for v in zip(*vectors)])
    elif len(scalars) == 0:
        return mv
    return max(scalars)
    
def _min(*args, sub_min=None):
    input = [a for a in args if not _is_missing(a)]
    if sub_min is not None:
        input.append(sub_min)
    return min(input) if not len(input) == 0 else mv

def st_min(*args):
    """Min function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
        (2 or more such inputs allowed)
    
    Returns
    -------
    min(x1, x2, ...) if any x is non-missing (with missing values ignored).
    Otherwise, MISSING (".") returned.
    
    """
    if len(args) <= 1:
        raise TypeError("need at least 2 arguments")
    vectors = [a.values for a in args if isinstance(a, StataVarVals)]
    scalars = [
        a for a in args if not isinstance(a, StataVarVals) and not _is_missing(a)
    ]
    if len(vectors) != 0:
        sca_min = min(scalars) if not len(scalars) == 0 else None
        return StataVarVals([_min(*v, sub_min=sca_min) for v in zip(*vectors)])
    elif len(scalars) == 0:
        return mv
    return min(scalars)

def st_mod(x,y):
    """Modulo (modulus) function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    y : float, int, MissingValue instance, or None
    
    Returns
    -------
    x - y * int(x / y) if x and y are both non-missing and y > 0,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        if isinstance(y, StataVarVals):
            return StataVarVals([
                mv if _is_missing(vx) or _is_missing(vy) or vy <= 0
                else vx % vy for vx, vy in zip(x.values, y.values)
            ])
        elif _is_missing(y) or y <= 0:
            return StataVarVals([mv for v in x.values])
        else:
            return StataVarVals([
                mv if _is_missing(v) else v % y for v in x.values
            ])
    if isinstance(y, StataVarVals):
        if _is_missing(x):
            return StataVarVals([mv for v in y.values])
        else:
            return StataVarVals([
                mv if _is_missing(v) or v <= 0 else x % v for v in y.values
            ])
    if _is_missing(x) or _is_missing(y) or y <= 0:
        return mv
    return x % y
    
def _reldif(x, y):
    missing = False
    if x is None or (not isinstance(x, MissingValue) and 
            (x < -8.988465674311579e+307 or x > 8.988465674311579e+307)):
        x = get_missing(x)
        missing = True
    if y is None or (not isinstance(y, MissingValue) and 
            (y < -8.988465674311579e+307 or y > 8.988465674311579e+307)):
        y = get_missing(y)
        missing = True
    if x == y:
        return 0
    if missing:
        return mv
    return abs(x - y) / (abs(y) + 1)
    
def st_reldif(x, y):
    """Relative difference function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    y : float, int, MissingValue instance, or None
    
    Returns
    -------
    If x and y are both non-missing, returns |x - y| / (|y| + 1).
    If x and y are both missing and correspond to the same 
        MissingValue instance, returns 0.
    Otherwise, returns MISSING (".").
    
    """
    if isinstance(x, StataVarVals):
        if isinstance(y, StataVarVals):
            return StataVarVals([
                _reldif(vx, vy) for vx, vy in zip(x.values, y.values)
            ])
        else:
            return StataVarVals([
                _reldif(v, y) for v in x.values
            ])
    if isinstance(y, StataVarVals):
        return StataVarVals([
            _reldif(x, v) for v in y.values
        ])
    return _reldif(x, y)
    
def _round(x, y):
    # Python 3 uses "banker's rounding": when a value is equidistant between
    # two rounded numbers, it rounds to the even digit. For example
    # >>> round(2.5)
    # 2
    # >>> round(3.5)
    # 4
    # >>> round(2.25, 2)
    # 2.2
    #
    # However, imprecision effects also come into play. With banker's rounding,
    # one might expect round(2.675, 2) to be 2.68, but 2.675 is stored as
    # something slightly smaller than 2.675, so it rounds down to 2.67.
    #
    # Stata has this latter issue as well, depending on use. If you use 
    # round(2.675, 0.01) interactively, you'll get 2.68. If you use
    # round(x, 0.01) where x is a variable containing 2.675 (approx), then
    # you get 2.67. If you use round(x, y) where x is a variable containing
    # 2.675 (approx) and y is a variable containing 0.01 (approx), then you
    # get 2.68 (approx).
    #
    # . di round(2.675, 0.01)
    # 2.68
    # 
    # . clear
    # 
    # . set obs 1
    # obs was 0, now 1
    # 
    # . gen x = 2.675
    # 
    # . di round(x, 0.01)
    # 2.67
    #
    # . clear
    # 
    # . set obs 1
    # obs was 0, now 1
    # 
    # . gen x = 2.675
    # 
    # . gen y = 0.01
    # 
    # . di round(x, y)
    # 2.6799999
    #

    if _is_missing(y):
        return mv
    if y == 0:
        if _is_missing(x) and not isinstance(x, MissingValue):
            return get_missing(x)
        return x
    if _is_missing(x):
        return x if isinstance(x, MissingValue) else get_missing(x)
    return round(x / y) * y

def st_round(x, y=1):
    """Rounding function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    y : float, int, MissingValue instance, or None;
        y is optional, default value is 1
    
    Returns
    -------
    If both x and y are non-missing, returns x / y rounded to
        the nearest integer times y (but see notes below).
    If y is 1 or y is not specified, returns x rounded to the 
        nearest integer (but see notes below).
    If y is zero, returns x.
    If y is missing, MISSING (".") is returned.
    If x is missing and y is non-missing, returns MissingValue
        corresponding to x.
    If both x and y are missing, returns MISSING (".").
    
    Notes
    -----
    Python 3 uses "banker's rounding": When equidistant between two rounded
    values, Python 3 rounds to the even digit. For example, round(3.5) and
    round(4.5) are both 4. Keep in mind that floating point imprecision of
    inputs may affect the output.
    
    """
    if isinstance(x, StataVarVals):
        if isinstance(y, StataVarVals):
            return StataVarVals([
                _round(vx, vy) for vx, vy in zip(x.values, y.values)
            ])
        if y == 0:
            return StataVarVals([
                get_missing(v)
                if _is_missing(v) and not isinstance(v, MissingValue)
                else v for v in x.values
            ])
        else:
            return StataVarVals([
                _round(v, y) for v in x.values
            ])
    if isinstance(y, StataVarVals):
        return StataVarVals([
            _round(x, v) for v in y.values
        ])
    return _round(x, y)

def st_sign(x):
    """Sign function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    the sign of x (-1 if < 0; 0 if == 0; 1 if > 0) if x is non-missing,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v)
            else 0 if v == 0 else -1 if v < 0 else 1 for v in x.values
        ])
    if _is_missing(x):
        return mv
    return 0 if x == 0 else -1 if x < 0 else 1
                     
def st_sin(x):
    """Sine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None;
        angle in radians
    
    Returns
    -------
    sine of x if x is non-missing and -1e+18 <= x <= 1e+18,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1e+18 <= v <= 1e+18
            else math.sin(v) for v in x.values
        ])
    if _is_missing(x) or not -1e+18 <= x <= 1e+18:
        return mv
    return math.sin(x)

def _sinh(x):
    if _is_missing(x) or not -709.8 <= x <= 709.8:
        return mv
    v = math.sinh(x)
    return v if -8.988465674311579e+307 <= v <= 8.988465674311579e+307 else mv
    
def st_sinh(x):
    """Hyperbolic sine function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    hyperbolic sine of x if x is non-missing and -1e+18 <= x <= 1e+18,
    MISSING (".") otherwise
    
    Note
    ----
    The hyperbolic sine of x can fall in Stata's missing range
    for non-missing x. For x outside of -709 < x < 709 (approximate)
    this function will return MISSING (".").
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_sinh(v) for v in x.values])
    return _sinh(x)

def st_sqrt(x):
    """Square root function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    square root of x if x is non-missing and >= 0,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or v < 0 else math.sqrt(v) for v in x.values
        ])
    if _is_missing(x) or x < 0:
        return mv
    return math.sqrt(x)
    
def _sum(*args):
    nonmiss = [a for a in args if not _is_missing(a)]
    if len(nonmiss) == 0:
        return 0
    v = sum(nonmiss)
    return v if -8.988465674311579e+307 <= v <= 8.988465674311579e+307 else mv

def st_sum(x):
    """Summation function.
    
    Parameters
    ----------
    x : a reference to a Stata variable, or 
        a single float, int, MissingValue instance, or None
    
    Returns
    -------
    sum of x1, x2, ... if any x is non-missing (with missing values ignored).
    If all inputs are missing values, returns zero.
    
    """
    if isinstance(x, StataVarVals):
        values = [v for v in x.values if not _is_missing(v)]
        if len(values) == 0:
            return 0
        v = sum(values)
        if -8.988465674311579e+307 <= v <= 8.988465674311579e+307:
            return v
        return mv
    if _is_missing(x):
        return 0
    return x

def st_tan(x):
    """Tangent function.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None;
        angle in radians
    
    Returns
    -------
    tangent of x if x is non-missing and -1e+18 <= x <= 1e+18,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) or not -1e+18 <= v <= 1e+18
            else math.tan(v) for v in x.values
        ])
    if _is_missing(x) or not -1e+18 <= x <= 1e+18:
        return mv
    return math.tan(x)  # assuming tan does not get above ~ 1e17

def st_tanh(x):
    if isinstance(x, StataVarVals):
        return StataVarVals([
            mv if _is_missing(v) else math.tanh(v) for v in x.values
        ])
    if _is_missing(x):
        return mv
    return math.tanh(x)
    
def _trigamma(x):    
    # Algorithm
    # ---------
    # Schneider, B E (1978). "Algorithm AS 121: Trigamma Function". 
    # Applied Statistics 27 (1): 97-99
    #  -> This paper's function returns zero for negative inputs.
    #     Wikipedia article below contains information for extending
    #     to negative inputs.
    # 
    # Wikipedia article on trigamma function:
    #     http://en.wikipedia.org/wiki/Trigamma_function
        
    if _is_missing(x):
        return mv
    
    value = 0
    
    # if x < 0, use reflection formula
    flip = False
    if x <= 0:
        if x == math.floor(x):
            return mv
        pi = math.pi
        value -= pi * pi / (math.sin(pi * x)) ** 2
        x = 1 - x
        flip = True
        
    while x < 15:
        value += 1. / (x * x)
        x += 1
        
    y = 1. / (x * x)
    value += 0.5*y + (1. + y*(1./6 + y*(-1./30 + y*(1./42 + y*(-1./30 + y*(5./66)))))) / x
        
    return value if not flip else -value

def st_trigamma(x):
    """Trigamma function, derivative of `st_digamma`, second
    derivative of `st_lngamma`.
    
    Parameters
    ----------
    x : float, int, MissingValue instance, or None
    
    Returns
    -------
    Trigamma of x if x is non-missing, not zero, and not a negative integer,
    MISSING (".") otherwise
    
    """
    if isinstance(x, StataVarVals):
        return StataVarVals([_trigamma(v) for v in x.values])
    return _trigamma(x)

st_trunc = st_int

