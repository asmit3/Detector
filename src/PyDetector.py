#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  module PyDetector
#--------------------------------------------------------------------------
"""
Base methods for detector interface. Of special note is the detector_factory
method that automatically identifies the correct detector from a
source string.

@version $Id$

@author Lane, Thomas Joseph - "Sacramentum hoc revelatum est"
"""
#------------------------------
__version__ = "$Revision$"
##-----------------------------

import _psana
import re
import Detector.DetectorTypes as dt
from Detector.EpicsDetector import EpicsDetector
from Detector.ControlDataDetector import ControlDataDetector

class DetInfo(object):
    """
    A class that provides a consistent string repr for all
    detectors, e.g. BldInfo() types that have only a single
    name and DetInfo() types that adhere to ".:." syntax.

    If that didn't mean anything to you, then you don't
    need this class.
    """

    def __init__(self,source_string):
        """
        Interpret a string like 'DetInfo(CxiDs2.0:Cspad.0)' in terms of:
        
        detector_type --> 'CxiDs2'
        detector_id   --> 0
        device_type   --> 'Cspad'
        device_id     --> 0
        """

        m = re.search('(\w+).(\d)\:(\w+).(\d)', source_string)

        if m:
            mg = m.groups()
            self.det = mg[0]
            self.detid = int(mg[1])
            self.dev = mg[2]
            self.devid  = int(mg[3])
        else:
            self.dev = source_string

    def __repr__(self):
        if not hasattr(self,'det'):
            return self.dev
        else:
            return self.det+'.'+str(self.detid)+':'+self.dev+'.'+str(self.devid)


# the following function is renamed psana.Detector in the
# psana __init__.py file
def detector_factory(source_string, env):
    """
    Create a python Detector from a string identifier.

    Parameters
    ----------
    source_string : str
        A string identifying a piece of data to access, examples include:
          - 'cspad'                  # a DAQ detector alias
          - 'XppGon.0:Cspad.0'       # a DAQ detector full-name
          - 'DIAG:FEE1:202:241:Data' # an EPICS variable name (or alias)
          - 'EBeam'                  # a BldInfo identifier\n
        The idea is that you should be able to pass something that makes
        sense to you as a human here, and you automatically get the right
        detector object in return.

    env : psana.Env
        The psana environment object associated with the psana.DataSource
        you are interested in (from method DataSource.env()).

    Returns
    -------
    A psana-python detector object. Try detector(psana.Event) to
    access your data.

    HOW TO GET MORE HELP
    --------------------
    The Detector method returns an object that has methods that
    change depending on the detector type. To see help for a particular
    detector type execute commands similar to the following

    env = DataSource('exp=xpptut15:run=54').env()
    det = Detector('cspad',env)

    and then use the standard ipython "det?" command (and tab completion) to
    see the documentation for that particular detector type.
    """

    # > create an instance of the determined detector type & return it
    source_string = map_alias_to_source(source_string, env)
    dt = dettype(source_string, env)
    det_instance = dt(source_string, env)
    det_instance.name = DetInfo(source_string)

    return det_instance


def map_alias_to_source(source_string, env):
    """
    Check to see if `source_string` is in the `env` alias map, and if so
    use the alias map to look it up and return the psana Source string
    corresponding to that alias.

    Parameters
    ----------
    source_string : str
        A string identifying a piece of data to access, examples include:

    env : psana.Env
        The psana environment object associated with the psana.DataSource
        you are interested in (from method DataSource.env()).

    Returns
    -------
    source_string : str
        De-aliased source string -- a unique identifier.
    """

    # see if the source_string is an alias
    amap = env.aliasMap()
    alias_src = amap.src(source_string) # string --> DAQ-style psana.Src

    # if it is an alias, look up the full name
    if amap.alias(alias_src) != '':         # alias found
        source_string = str(alias_src)

    return source_string


# the following function is renamed psana.Detector in the
# psana __init__.py file
def dettype(source_string, env):
    """
    Create a python Detector-class "type" from a string identifier.

    Parameters
    ----------
    source_string : str
        A string identifying a piece of data to access, examples include:
          - 'cspad'                  # a DAQ detector alias
          - 'XppGon.0:Cspad.0'       # a DAQ detector full-name
          - 'DIAG:FEE1:202:241:Data' # an EPICS variable name (or alias)
          - 'EBeam'                  # a BldInfo identifier\n
        The idea is that you should be able to pass something that makes
        sense to you as a human here, and you automatically get the right
        detector object in return.

    env : psana.Env
        The psana environment object associated with the psana.DataSource
        you are interested in (from method DataSource.env()).

    Returns
    -------
    The type of the appropriate detector class
    """

    epics = env.epicsStore()
    if source_string in epics.names(): # both names & aliases
        detector_class = EpicsDetector

    elif source_string in ['ControlData', 'ScanData']:
        detector_class = ControlDataDetector

    elif source_string in dt.bld_info.keys(): # if source is a BldInfo...
        detector_class = dt.bld_info[source_string]

    else:                                     # assume source is a DetInfo...
        di = DetInfo(source_string)
        if di.dev in dt.detectors.keys():
            detector_class = dt.detectors[di.dev]
        else:
            raise KeyError('Unknown DetInfo device type: %s (source: %s)'
                           '' % (di.dev, source_string))

    return detector_class

##-----------------------------

def _test1(ntest):
    """Test of the detector_factory(src, env) for AreaDetector and WFDetector classes.
    """
    from time import time
    import psana

    dsname, src                  = 'exp=xpptut15:run=54',  'XppGon.0:Cspad.0'
    if   ntest==2  : dsname, src = 'exp=meca1113:run=376', 'MecTargetChamber.0:Cspad2x2.1'
    elif ntest==3  : dsname, src = 'exp=amob5114:run=403', 'Camp.0:pnCCD.0'
    elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  'NoDetector.0:Epix100a.0'
    elif ntest==5  : dsname, src = 'exp=sxri0414:run=88',  'SxrEndstation.0:Acqiris.2'
    elif ntest==6  : dsname, src = 'exp=cxii0215:run=49',  'CxiEndstation.0:Imp.1'
    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

    ds = psana.DataSource(dsname)
    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    for key in evt.keys() : print key

    det = detector_factory(src, env)

    try :
        nda = det.pedestals(rnum)
        print '\nnda:\n', nda
        print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)
    except :
        print 'WARNING: det.pedestals(rnum) is not available for dataset: %s and source : %s' % (dsname, src) 

    try :
        t0_sec = time()
        nda = det.raw(evt)
        print '\nConsumed time to get raw data (sec) =', time()-t0_sec
        print 'nda:\n', nda.flatten()[0:10]
    except :
        print 'WARNING: det.raw(evt) is not available for dataset: %s and source : %s' % (dsname, src) 

##-----------------------------

def _test2():
    """Test of the detector_factory(src, env) for EvrDetector, DdlDetectorand and EpicsDetector classes.
    """
    # test EVR names
    import psana

    #ds = psana.DataSource('exp=amoj5415:run=43')
    ds = psana.DataSource('exp=xpptut15:run=54')
    env = ds.env()

    names = ['cspad',
             'XppGon.0:Cspad.0',
             'evr0',
             'NoDetector.0:Evr.0',
             'FEEGasDetEnergy',
             'EBeam',
             'dev.0:det.0',
             'notadet',
             #'DIAG:FEE1:202:241:Data',
             #'XTCAV_yag_status',
             #'badname',
             ]

    for name in names:
        det = detector_factory(name, env)
        print name, '-->', type(det)

        for evt in ds.events():
            print det(evt)
            break

    return 


def _test3():

    import psana

    ds = psana.DataSource('exp=xppk3815:run=100:idx')
    #det = psana.Detector('ControlData', ds.env())
    det = psana.Detector('ControlData')

    run = ds.runs().next()
    nsteps = run.nsteps()
    for step in range(nsteps):
        times = run.times(step)
        for t in times[:2]:
            evt = run.event(t)
            print t, det().pvControls()[0].value()
    
    return


def test4():
    import psana
    ds = psana.DataSource('exp=xpptut15:run=54')
    env = ds.env()
    d = psana.Detector('evr0')
    d2 = psana.Detector('yag2')
    print d.source, d2.source
    print d( ds.events().next() )
    print d2.raw( ds.events().next() )

##-----------------------------

if __name__ == '__main__':

    #for i in range(5): _test1(i)
    #_test2()
    _test3()
    test4()

    import sys; sys.exit()

    try    : ntest = int(sys.argv[1]) if len(sys.argv)>1 else 0
    except : raise ValueError('First input parameter "%s" is expected to be empty or integer test number' % sys.argv[1])
    print 'Test# %d' % ntest

    if len(sys.argv)<2 : _test2()
    else               : _test1(ntest)

    sys.exit ('Self test is done')

##-----------------------------
