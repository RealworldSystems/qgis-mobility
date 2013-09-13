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

from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os
import shutil

from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder


class SpatialiteBuilder(Builder):
    """ Represents the build strategy for the SpatiaLite library """

    def library_name(self):
        """ Returns the library name of the SpatiaLite library """
        return 'spatialite-3.0.1'
    
    def human_name(self):
        """ Returns the human readable name of the Spatialite Builder """
        return 'SpatiaLite Build Process'


    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        default_flags = Builder.get_default_flags(self)
        arch = self.get_current_arch()
        flags = SQLiteBuilder(self.get_recon(), arch).salt_flags(default_flags)
        flags = GeosBuilder(self.get_recon(), arch).salt_flags(flags)
        flags = Proj4Builder(self.get_recon(), arch).salt_flags(flags)
        flags['LDFLAGS'] += ' -lm'
        print flags
        return flags

    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--disable-geosadvanced', '--disable-iconv', '--disable-freexl'])
        return flags
    
    def do_build_for(self, arch, output):
        """ 
        If arch is set to "host", the build is done for the host environment.
        If arch is set to "target", the build is done for the target environment.
        """
        host = (arch == "host")
        self.set_current_arch(arch)
        
        self.unpack(output)
        
        base_source_path = os.path.join(self.get_source_path(), 
                                        'lib' + self.library_name())
        
        if not os.path.exists(base_source_path + '/m4'): 
              os.makedirs(base_source_path + '/m4')

        self.push_current_source_path(base_source_path)
        self.fix_config_sub_and_guess()
        self.sed_ir('s/(\-version\-info 4\:0\:2)/\-avoid\-version/g', 'src/Makefile.am')
        self.sed_ir('s/#include <freexl.h>//', 'src/shapefiles/shapefiles.c')
        self.run_autoreconf()
        if not host:
            self.sed_i("s/@MINGW_FALSE@am__append_1 = -lpthread -ldl/@MINGW_FALSE@am_append_1 = -ldl/", 
                   'src/Makefile.in')
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.run_autotools_and_make()
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))

        self.pop_current_source_path()
        shutil.rmtree(base_source_path)
        
    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://www.gaia-gis.it/gaia-sins/libspatialite-sources/lib' + 
                           self.library_name() + '.tar.gz')

        self.do_build_for('host', output)
        self.do_build_for('android', output)
        self.mark_finished()


