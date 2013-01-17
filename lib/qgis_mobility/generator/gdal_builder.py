from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os

class GDALBuilder(Builder):
    """ Represents the build strategy for the GDAL library """

    def library_name(self):
        """ Returns the library name of the GDAL library """
        return 'gdal-1.8.0'
    
    def human_name(self):
        """ Returns the human readable name of the GDAL Builder """
        return 'GDAL Build Process'    

    def get_default_flags(self):
        flags = Builder.get_default_flags(self)
        flags['LIBS'] = '-lsupc++ -lstdc++'
        return flags
    
    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--without-grib'])
        return flags
    

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://download.osgeo.org/gdal/' + self.library_name() + '.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.fix_config_sub_and_guess()
        self.patch('android.diff', strip=0)
        self.patch('gdal.patch', strip=1)
        self.run_autotools_and_make(harness=False)        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        
        self.mark_finished()


