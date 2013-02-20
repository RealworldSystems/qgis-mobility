#
#  This file is part of QGis Mobility
#
#  QGis Mobility is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  QGis Mobility is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with QGis Mobility. If not, see 
#  <http://www.gnu.org/licenses/>.
#

from qgis_mobility.generator.standalone_toolchain import StandaloneToolchain
from qgis_mobility.generator.bzip2_builder import BZip2Builder
from qgis_mobility.generator.libiconv_builder import LibiconvBuilder
from qgis_mobility.generator.freexl_builder import FreeXLBuilder
from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder
from qgis_mobility.generator.spatialite_builder import SpatialiteBuilder
from qgis_mobility.generator.expat_builder import ExpatBuilder
from qgis_mobility.generator.gdal_builder import GDALBuilder
from qgis_mobility.generator.gsl_builder import GSLBuilder
from qgis_mobility.generator.qwt_builder import QWTBuilder
from qgis_mobility.generator.spatialindex_builder import SpatialindexBuilder
from qgis_mobility.generator.python_builder import PythonBuilder
from qgis_mobility.generator.qgis_builder import QGisBuilder
from qgis_mobility.generator.sip_builder import SipBuilder
from qgis_mobility.generator.pyqt_builder import PyQtBuilder
from qgis_mobility.generator.runtime_builder import RuntimeBuilder
from qgis_mobility.generator.creator import Creator

import sys
import os

from collections import namedtuple

__dependency_class_chain = [
        StandaloneToolchain,
        BZip2Builder,
        LibiconvBuilder,
        FreeXLBuilder,
        SQLiteBuilder,
        GeosBuilder,
        Proj4Builder,
        SpatialiteBuilder,
        ExpatBuilder,
        GDALBuilder,
        GSLBuilder,
        QWTBuilder,
        SpatialindexBuilder,
        PythonBuilder,
        SipBuilder,
        PyQtBuilder,
        QGisBuilder,
        RuntimeBuilder,
] 


__resolved_names = None


def __resolve_names():
    """
    This function resolves the names from the dependency class chain
    defined here
    """
    global __resolved_names
    
    if __resolved_names == None:
        name_dict = {}
        for dependency_class in __dependency_class_chain:
            mod = sys.modules[dependency_class.__module__]
            for obj_name in mod.__dict__.keys():
                if mod.__dict__[obj_name] == dependency_class:
                    lowered = obj_name.lower()
                    if len(lowered) > 6 and lowered[-7:] == "builder":
                        lowered = lowered[:-7]
                    name_dict[lowered] = dependency_class
        __resolved_names = name_dict

# Call the name resolution
__resolve_names()

def all_values():
    return __resolved_names.values()

def all_names():
    return __resolved_names.keys()

def get_dependency_class_chain(builder):
    """
    Resolves the dependency class chain upto now
    """
    global __dependency_class_chain
    
    elems = []
    for dependency in __dependency_class_chain:
        elems.extend([dependency])
        if builder.__class__ == dependency:
            return elems

    return elems

class Recipe(object):
    class _Target(object):
        def __init__(self, recipe, target, recon):
            """
            Initializes the target with a builder instance
            """
            self._recipe = recipe
            self._recon = recon
            self._builder = target(recon)

        def build(self):
            """
            Builds the target
            """
            
            for dependency_class in get_dependency_class_chain(self._builder):
                dependency_class(self._recon).make()
            
        
        def rebuild(self):
            """
            Rebuilds the target
            """
            self.clean()
            self.build()

        def clean(self):
            """
            Cleans up the mess
            """
            if self._builder.get_build_finished():
                print '='*80
                print "Cleaning", self._builder.human_name() 
                print '='*80
                self._builder.remove()
            else:
                print '='*80
                print "Already cleaned", self._builder.human_name() 
                print '='*80
    
    class _All(object):
        def __init__(self, targets):
            self._targets = targets
        
        def clean(self):
            for target in self._targets:
                target.clean()
            
        
        def build(self):
            self._targets.runtime.build()

    def __init__(self, recon):
        names = all_names()
        targets = namedtuple('_Targets', names)
        self.recipe = targets(*map (lambda v: Recipe._Target(self, v, recon), 
                                    all_values()))
        self.all = Recipe._All(self.recipe)
        self.creator = Creator(recon)
        self.__recon = recon
    
    def distclean(self):
        """ Removes everything """
        
        # This removes the whole tree of build fragments. To do this,
        # it needs to destroy hostpython (which is where this file
        # is running). Therefore, a shell file is executed replacing
        # this process
        script_path = self.__recon.get_script_path()
        distclean = os.path.join(script_path, "distclean.sh")
        os.execlp(distclean, distclean)

        def __purge_cache_path(self):
            """ Purges the source path but keeps build targets """
            rmtree(os.path.join(__recon.get_cache_path(), 'source'))
