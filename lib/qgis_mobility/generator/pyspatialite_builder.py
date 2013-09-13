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

from qgis_mobility.generator.pythonian_builder import PythonianBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder

import os
import shutil
import subprocess

class PySpatialiteBuilder(PythonianBuilder):
    """ Represents the build strategy for the PySpatialite Builder """

    def version(self): return '2.6.2'
    def small_name(self): return 'PySpatialite'
    def small_version(self): return self.small_name() + '-' + self.version()

    def library_name(self):
        """ Returns the library name of the sip version to build to build """
        return "pyspatialite-2.6.2-spatialite.2.3.1"
    
    def human_name(self):
        """ Returns the human readable name of the PySpatialite Builder """
        return 'PySpatialite Build Process (HOST Only)'

    def get_default_toolchain_mappings(self):
        mappings = PythonianBuilder.get_default_toolchain_mappings(self)
        arch = self.get_current_arch()
        geos_lib_path = GeosBuilder(self.get_recon(), arch).get_library_path()
        proj_lib_path = Proj4Builder(self.get_recon(), arch).get_library_path()
        flags = "-L%s -L%s" % (geos_lib_path, proj_lib_path)
        mappings['LDFLAGS'] = flags
        return mappings

    def do_build(self):
        """ Starts the build process of the HOST Only PySpatialite """

        url = "https://pypi.python.org/packages/source/p/pyspatialite/%s.tar.gz" % self.library_name()
        output = self.wget(url)
        self.set_current_arch('host')
        self.unpack(output)

        base_source_path = os.path.join(self.get_source_path(), 
                                        self.library_name())
        self.push_current_source_path(base_source_path)
        self.patch("pyspatialite.patch", strip=1)
        self.run_py_setup_build_and_install()
        self.pop_current_source_path()
        shutil.rmtree(os.path.join(base_source_path))
        self.mark_finished()
