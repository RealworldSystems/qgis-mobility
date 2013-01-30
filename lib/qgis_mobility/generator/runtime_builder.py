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
from qgis_mobility.generator.python_builder import PythonBuilder
from qgis_mobility.generator.qgis_builder import QGisBuilder


class RuntimeBuilder(Builder):
    """ Represents the build strategy for the Runtime library """

    def library_name(self):
        """ Returns the library name of the runtime """
        return 'runtime'
    
    def human_name(self):
        """ Returns the human readable name of the Runtime """
        return 'Runtime Build Process'


    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--with-qgis-base-path=' + QGisBuilder(self.get_recon()).get_build_path(),
                      '--with-python-base-path=' + PythonBuilder(self.get_recon()).get_build_path(),
                      '--with-qt-base-path=' + self.get_recon().get_qt_path(),
                      '--with-qt-include-path=' + os.path.join(self.get_recon().get_qt_path(), 'include')])
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
        distutils.dir_util.copy_tree(self.get_runtime_path(), self.get_source_path())
        self.run_libtoolize()
        self.run_automake_add_missing()
        self.run_autoreconf()
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()
        source_include_path = os.path.join(self.get_build_path(), 'include')
        if os.path.exists(source_include_path):
            distutils.dir_util.copy_tree(
                source_include_path, self.get_include_path())
        self.mark_finished()
