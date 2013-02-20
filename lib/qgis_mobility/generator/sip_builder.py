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

import os
import shutil

class SipBuilder(PythonianBuilder):
    """ Represents the build strategy for the Python Builder """

    def library_name(self):
        """ Returns the library name of the sip version to build to build """
        return 'sip-4.14.2'
    
    def human_name(self):
        """ Returns the human readable name of the Python Builder """
        return 'SIP (Binding Processor for Python) Build Process'

    def do_build(self):
        """ Starts the build process of Android SIP """

        output = self.wget('http://sourceforge.net/projects/pyqt/files/sip/' + 
                           self.library_name() + '/' + self.library_name() + '.tar.gz/download')

        self.unpack(output)

        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        shutil.copyfile(os.path.join(self.get_patch_path(), 'android-g++'),
                        os.path.join(self.get_current_source_path(), 'specs', 'android-g++'))
        
        options=['-e' + self.get_include_path(), 
                 '-pandroid-g++', 'INCDIR=' + self.get_include_path(),
                 'CXXFLAGS=-mthumb --std=gnu++0x',
                 'CFLAGS=-mthumb',
                 'LFLAGS=-L' + self.get_output_library_path() + ' -lpython2.7 -Wl,--fix-cortex-a8',
                 'STRIP=']

        self.run_py_configure_and_make(options=options)
        self.run_py_configure_and_make(host=True)
        # Need to install SIP to host python
        

        self.mark_finished()

