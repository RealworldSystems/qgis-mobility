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

class GSLBuilder(Builder):
    """ Represents the build strategy for the GSL library """

    def library_name(self):
        """ Returns the library name of the GSL library """
        return 'gsl-1.14'
    
    def human_name(self):
        """ Returns the human readable name of the GSL Builder """
        return 'GSL Build Process'        

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://ftp.gnu.org/gnu/gsl/' + self.library_name() + '.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()


