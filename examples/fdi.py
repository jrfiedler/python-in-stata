try:
    from sympy import *
    # this kind of import puts a lot of stuff in global namespace;
    # usually better to import what you need or import sympy
except ImportError:
    st_local("importerror", "True")
    raise

x = Symbol('x')
f = Function('f')

f = eval(st_local("anything").replace('^','**'))

st_local("anything", st_local("anything").replace("**", "^"))
st_local("fprime", repr(f.diff(x)).replace("**", "^"))
st_local("fint", repr(f.integrate(x)).replace("**", "^"))
