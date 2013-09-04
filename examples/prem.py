import re

varNum = st_varindex(st_local("varlist"), True)
reComp = re.compile(st_local("regex"))

for i in range(st_in1(), st_in2()):
    if st_ifobs(i):
        obs = _st_sdata(i, varNum)
        m = reComp.search(obs)
        if m: 
            beg, end = m.start(), m.end()
            s1, s2, s3 = obs[:beg], obs[beg:end], obs[end:]
            print(s1 + "{ul on}" + s2 + "{ul off}" + s3)
