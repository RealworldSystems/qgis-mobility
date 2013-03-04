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

from qgis_mobility.generator.pyqt_builder import PyQtBuilder

import os
import shutil
import subprocess

class PyQtMobilityBuilder(PyQtBuilder):
    """ Represents the build strategy for the Python Builder """

    def version(self): return '1.0.1'
    def small_name(self): return 'PyQtMobility'
    def small_version(self): return self.small_name() + '-' + self.version()

    def library_name(self):
        """ Returns the library name of the sip version to build to build """
        return  self.small_name() + '-gpl-' + self.version()
    
    def human_name(self):
        """ Returns the human readable name of the PyQt Builder """
        return 'PyQt-Mobility Build Process'


    def do_build(self):
        """ Starts the build process of Android PyQt """

        output = self.wget('http://www.riverbankcomputing.co.uk/static/Downloads/PyQtMobility/' +
                           self.library_name() + '.tar.gz')

        self.unpack(output)

        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.pop_current_source_path()
        shutil.rmtree(os.path.join(self.get_source_path(), self.library_name()))
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))

        qt_version, qt_edition = self.use_preprocessor_determination()
        fname = self.qtdirs_responder(qt_version, qt_edition)

        mappings = self.get_default_toolchain_mappings()
        flags = self.get_default_flags()
        sysroot = os.path.join(self.get_recon().get_toolchain_path(), 'sysroot')
        options =[
            '-eQtLocation', '-eQtSensors',
            '-n' + os.path.join(self.get_recon().get_qt_path(), 'include'),
            '-o' + os.path.join(self.get_recon().get_qt_path(), 'lib')]

        sip_path = os.path.join(self.get_build_path(), 'share', 'sip')

        self.sed_ie('s|flags.append.pyqt.pyqt_sip_dir.|flags.append(\'' + sip_path + '\')|', 'configure.py')


        self.run_py_configure(options, binaries=False)
        
        makeopts = ['CC=' + mappings['CC'],
                    'CFLAGS+=--sysroot=' + sysroot + ' -mthumb' + ' -I' + self.get_include_path() + ' -I' + os.path.join(self.get_recon().get_qt_path(), 'include'),
                    'CXXFLAGS+= -fpermissive --sysroot=' + sysroot + ' -mthumb' + ' -I' + self.get_include_path() + ' -I' + os.path.join(self.get_recon().get_qt_path(), 'include'),
                    'CXX=' + mappings['CXX'],
                    'LINK=' + mappings['CC'],
                    'LIBS=-L' + os.path.join(self.get_recon().get_qt_path(), 'lib') + ' -L' + self.get_output_library_path() + ' -lQtSensors -lQtLocation -lQtCore -lQtGui -lpython2.7',
                    'INSTALL_ROOT=' + self.get_build_path()]

        self.run_make(makeopts=makeopts)


        self.sed_ie('s|strip|' + self.get_tool('strip') + '|', 'QtLocation/Makefile')
        self.sed_ie('s|strip|' + self.get_tool('strip') + '|', 'QtSensors/Makefile')

        self.run_make(makeopts=makeopts, install=True)

        self.mark_finished()
