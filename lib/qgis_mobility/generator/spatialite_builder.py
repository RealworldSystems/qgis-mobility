from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os

from qgis_mobility.generator.libiconv_builder import LibiconvBuilder
from qgis_mobility.generator.freexl_builder import FreeXLBuilder
from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder


class SpatialiteBuilder(Builder):
    """ Represents the build strategy for the SpatiaLite library """

    def library_name(self):
        """ Returns the library name of the SpatiaLite library """
        return 'spatialite-3.0.1'
    
    def human_name(self):
        """ Returns the human readable name of the Spatialite Builder """
        return 'SpatiaLite Build Process'


    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags = LibiconvBuilder(self.get_recon()).salt_flags(Builder.get_default_flags(self))
        flags = SQLiteBuilder(self.get_recon()).salt_flags(flags)
        flags = GeosBuilder(self.get_recon()).salt_flags(flags)
        flags = Proj4Builder(self.get_recon()).salt_flags(flags)
        flags = FreeXLBuilder(self.get_recon()).salt_flags(flags)
        flags['LDFLAGS'] += ' -lm'
        return flags

    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--disable-geosadvanced', '--disable-iconv'])
        return flags
    

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://www.gaia-gis.it/gaia-sins/libspatialite-sources/lib' + 
                           self.library_name() + '.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), 'lib' + self.library_name()))
        self.fix_config_sub_and_guess()
        self.sed_i("s/@MINGW_FALSE@am__append_1 = -lpthread -ldl/@MINGW_FALSE@am_append_1 = -ldl/", 
                   'src/Makefile.in')
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        
        self.mark_finished()


