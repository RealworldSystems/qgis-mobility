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

class GeosBuilder(Builder):
    """ Represents the build strategy for the Geos library """

    def library_name(self):
        """ Returns the library name of the Geos library """
        return 'geos-3.2.3'
    
    def human_name(self):
        """ Returns the human readable name of the FreeXLBuilder """
        return 'Geos Build Process'

    def sixty_four(self):
        f = open(os.path.join(self.get_current_source_path(), 'sixty_four.h'), 'w+')
        f.write('#define uint64_t unsigned long long\n')
        f.write('#define HAVE_ISNAN\n')
        f.close()

    def get_default_flags(self):
        """ Modify the flags to add the sixty_four business """
        flags = Builder.get_default_flags(self)
        flags['CFLAGS'] += ' -imacros ' + os.path.join(
            self.get_current_source_path(), 'sixty_four.h')
        flags['CXXFLAGS'] += ' -imacros ' + os.path.join(
            self.get_current_source_path(), 'sixty_four.h')
        flags['LIBS'] = '-lsupc++ -lstdc++'
        return flags
    
    def salt_flags(self, flags):
        flags = Builder.salt_flags(self, flags)
        self.insert_config_path_flag(flags)
        return flags
            
    def get_default_configure_flags(self):
        """ Override the configure flags to use """
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--disable-inline'])
        return flags

    def do_build(self):
        """ Runs the actual build process """
        self.run_svn_checkout('http://svn.osgeo.org/geos/tags/3.2.3', 'geos-3.2.3')
        self.push_current_source_path(os.path.join(self.get_source_path(), 'geos-3.2.3'))
        self.patch('int64_crosscomp.patch', strip=1)
        self.run_autogen()
        self.patch('geos.patch', strip=1)
        self.patch('CoordinateSequenceFactory.h.patch', strip=1)
        self.patch('Bintree.cpp.patch', strip=1)
        self.patch('Node.cpp.patch', strip=1)
        self.patch('Root.cpp.patch', strip=1)
        self.patch('AbstractNode.cpp.patch', strip=1)
        self.patch('DirectedEdgeStar.h.patch', strip=1)
        self.patch('DouglasPeuckerLineSimplifier.h.patch', strip=1)
        self.patch('MonotoneChainBuilder.h.patch', strip=1)
        self.patch('SimpleNestedRingTester.h.patch', strip=1)
        self.patch('TaggedLineString.cpp.patch', strip=1)
        self.patch('TaggedLineString.h.patch', strip=1)
        self.patch('TaggedLineStringSimplifier.h.patch', strip=1)
        self.patch('swig.patch', strip=1)
        self.sixty_four()
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
