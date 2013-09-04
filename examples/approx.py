try:
    from sympy import *
    # this kind of import puts a lot of stuff in global namespace;
    # usually better to import what you need or import sympy
except ImportError:
    st_local("importerror", "True")
    raise

x = Symbol('x')
f = Function('f')
g = Function('g')

f = eval(st_local("anything").replace('^','**'))
n = int(st_local("nterms"))
c = st_local("center")
c = float(c) if (c != "pi" and c != "_pi") else pi

terms_gen = f.series(x, x0=c, n=None)

st_local("f", repr(f).replace("**", "^"))

g = 0
for i, term in zip(range(n), terms_gen):
    g += term
    grepr = repr(g).replace("**", "^").replace("E", "exp(1)")
    grepr = grepr.replace("pi", "_pi")
    st_local("f" + str(i+1), grepr)
    