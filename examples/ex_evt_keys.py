
""" Example shows how to print evt.keys()
    Usage: python Detector/examples/ex_evt_keys.py exp=amoj5415:run=50
"""
##-----------------------------

import psana
import sys

dsname = 'exp=amoj5415:run=49' if len(sys.argv)==1 else sys.argv[1]
ds = psana.DataSource(dsname)

for i, evt in enumerate(ds.events()) :
    if i>5 : break
    print '%s\nEvent# %3d' % (100*'_', i)
    for key in evt.keys() : print key

##-----------------------------