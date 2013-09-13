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

class SQLiteBuilder(Builder):
    """ Represents the build strategy for the SQLite library """

    def library_name(self):
        """ Returns the library name of the SQLite library """
        return 'sqlite-autoconf-3070400'
    
    def human_name(self):
        """ Returns the human readable name of the GeosBuilder """
        return 'SQLite Build Process'

    def salt_flags(self, flags):
        flags = Builder.salt_flags(self, flags)
        self.insert_config_path_flag(flags)
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
                                        self.library_name())
        
        self.push_current_source_path(base_source_path)
        self.fix_config_sub_and_guess()
        
        if not host:
            self.patch('sqlite.patch', strip=1)
        
        self.run_autotools_and_make()
        
        includes_from = os.path.join(self.get_build_path(), 'include')
        includes_to = self.get_include_path()
        
        distutils.dir_util.copy_tree(includes_from, includes_to)

        self.pop_current_source_path()
        shutil.rmtree(base_source_path)
        

    def do_build(self):
        """ Runs the actual build process """
        tarball_url = "http://www.sqlite.org/%s.tar.gz" % self.library_name()
        output = self.wget(tarball_url)
        self.do_build_for("host", output)
        self.do_build_for("android", output)
        self.mark_finished()
