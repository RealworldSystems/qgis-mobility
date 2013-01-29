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
import os
import shutil
import distutils.dir_util

class LibiconvBuilder(Builder):
    def library_name(self):
        """ Returns the library name of the Libiconv library """
        return 'libiconv-1.13.1'
    
    def human_name(self):
        """ Returns the human readable name of the Libiconv Builder """
        return 'Libiconv (Iconv) Build Process'

    def get_default_flags(self):
        """
        Changes the default flags to include:
        gl_cv_header_working_stdint_h=yes
        """
        flags = Builder.get_default_flags(self).copy()
        flags['gl_cv_header_working_stdint_h'] = 'yes'
        flags['CFLAGS'] += ' -UHAVE_LANGINFO_CODESET'
        return flags
    
    
    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.13.1.tar.gz')
        self.unpack(output)
        my_source_path = os.path.join(self.get_source_path(), 'libiconv-1.13.1')
        self.push_current_source_path(my_source_path)
        self.fix_config_sub_and_guess()
        self.push_current_source_path(os.path.join(self.get_current_source_path(), 'build-aux'))
        self.fix_config_sub_and_guess()
        self.pop_current_source_path()
        self.push_current_source_path(os.path.join(self.get_current_source_path(), 'libcharset', 'build-aux'))
        self.fix_config_sub_and_guess()
        self.pop_current_source_path()
        self.patch('libiconv.patch', strip=1)
        self.run_autotools_and_make()
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
