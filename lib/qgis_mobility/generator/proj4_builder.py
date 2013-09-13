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

class Proj4Builder(Builder):
    """ Represents the build strategy for the Proj4 library """

    def library_name(self):
        """ Returns the library name of the Proj4 library """
        return 'proj-4.7.0'
    
    def human_name(self):
        """ Returns the human readable name of the Proj4Builder """
        return 'Proj4 Build Process'

    def do_build_for(self, arch, output):
        """
        Builds the Proj4 library for the given architecture using the tarball
        specified as output
        """
        self.set_current_arch(arch)
        self.unpack(output)
        base_source_path = os.path.join(self.get_source_path(), 'proj-4.7.0')
        self.push_current_source_path(base_source_path)
        self.patch('proj4.patch')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.pop_current_source_path()
        shutil.rmtree(base_source_path)


    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://download.osgeo.org/proj/' + 
                           self.library_name() + '.tar.gz')
        self.do_build_for('host', output)
        self.do_build_for('android', output)
        self.mark_finished()
