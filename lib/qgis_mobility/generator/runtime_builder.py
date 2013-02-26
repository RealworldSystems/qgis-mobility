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
import glob
import shutil
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


    def pyqt4_override_flags(self):
        return "-x QSETINT_CONVERSION -x QSETTYPE_CONVERSION -x VendorID -t WS_UNKOWN -x PyQt_NoPrintRangeBug -t Qt_4_8_0 -x Py_v3 -g"

    def sip_dir(self):
        return os.path.join(self.cache_path, 
                            'build', 'Python-2.7.2', 'share', 'sip')

    def host_python_binary_path(self):
        return os.path.join(self.cache_path, 'hostpython', 'bin')

    def get_default_toolchain_mappings(self):
        flags = Builder.get_default_toolchain_mappings(self)
        flags['LD_RUN_PATH'] = os.path.join(self.get_recon().get_qt_path(), 'lib')
        return flags

    def get_default_flags(self):
        cflags = '-Wno-psabi -fsigned-char -mthumb'
        ldflags = '-Wl,--fix-cortex-a8'
        return { 'CFLAGS'   : cflags,
                 'LDFLAGS'  : ldflags,
                 'CXXFLAGS' : cflags }


    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--with-qgis-base-path=' + QGisBuilder(self.get_recon()).get_build_path(),
                      '--with-python-base-path=' + PythonBuilder(self.get_recon()).get_build_path(),
                      '--with-qt-base-path=' + self.get_recon().get_qt_path(),
                      '--with-qt-library-path=' + os.path.join(self.get_source_path(), 'lib'),
                      '--with-qt-include-path=' + os.path.join(self.get_recon().get_qt_path(), 'include'),
                      '--with-sip=' + self.sip_dir(),
                      '--with-pyqt4-flags=' + self.pyqt4_override_flags(),
                      '--with-pyqt4-dir=' + self.sip_dir(),
                      '--with-sip-binary-path=' + self.host_python_binary_path(),
                      '--with-preconfig-path=/data/data/org.kde.necessitas.example.QGisMobility/files',
                      '--with-project-code-path=/data/data/org.kde.necessitas.example.QGisMobility/files/application',
                      '--disable-silent-rules'])
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
        os.mkdir(os.path.join(self.get_source_path(), 'lib'))
        for libname in glob.glob(os.path.join(self.get_recon().get_qt_path(), 'lib', '*.so')):
            outlibname = os.path.join(self.get_source_path(), 'lib', os.path.split(libname)[-1])
            print "Copying for libtool's sake %s to %s" % (libname, outlibname)
            shutil.copyfile(libname, outlibname)
        self.run_autoreconf()
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()
        source_include_path = os.path.join(self.get_build_path(), 'include')
        if os.path.exists(source_include_path):
            distutils.dir_util.copy_tree(
                source_include_path, self.get_include_path())
        self.mark_finished()
