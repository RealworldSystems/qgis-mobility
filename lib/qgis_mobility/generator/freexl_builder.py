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
from qgis_mobility.generator.libiconv_builder import LibiconvBuilder


class FreeXLBuilder(Builder):
    """ Represents the build strategy for the FreeXL library """

    def library_name(self):
        """ Returns the library name of the FreeXL library """
        return 'freexl-1.0.0e'
    
    def human_name(self):
        """ Returns the human readable name of the FreeXLBuilder """
        return 'FreeXL Build Process'

    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags = LibiconvBuilder(self.get_recon()).salt_flags(Builder.get_default_flags(self))
        flags['LDFLAGS'] += ' -lm'
        return flags

    def salt_flags(self, flags):
        flags = Builder.salt_flags(self, flags)
        pkg_config_path = os.path.join(self.get_build_path(), 'lib', 'pkg_config')
        if 'PKG_CONFIG_PATH' in flags:
            flags['PKG_CONFIG_PATH'] = pkg_config_path
        else:
            flags['PKG_CONFIG_PATH'] += os.path.sep + pkg_config_path
        return flags

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://www.gaia-gis.it/gaia-sins/freexl-1.0.0e.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), 'freexl-1.0.0e'))
        self.patch('freexl.patch', strip=1)
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
