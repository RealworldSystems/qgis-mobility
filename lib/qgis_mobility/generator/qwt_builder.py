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

class QWTBuilder(Builder):
    """ Represents the build strategy for the QWT library """

    def library_name(self):
        """ Returns the library name of the QWT library """
        return 'qwt-5.2.0'
    
    def human_name(self):
        """ Returns the human readable name of the QWT Builder """
        return 'QWT Build Process'        

    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags  = Builder.get_default_flags(self)
        flags['ANDROID_NDK_ROOT'] = self.get_recon().get_ndk_path()
        return flags

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://downloads.sourceforge.net/project/qwt/qwt/5.2.0/' + 
                           self.library_name() + '.tar.bz2')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.sed_ie('s/^CONFIG\\s*+=\\s*QwtDesigner/#CONFIG += QwtDesigner/', 'qwtconfig.pri')
        self.sed_ie('s/^CONFIG\\s*+=\\s*QwtDll/#CONFIG += QwtDll plugin/', 'qwtconfig.pri')
        self.sed_ie('s/^INSTALLBASE.*/CONFIG += $INSTALL_DIR/', 'qwtconfig.pri')
        self.run_qmake_and_make()
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(),
                                                  'usr', 'local', self.library_name(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()


