from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os

class Proj4Builder(Builder):
    """ Represents the build strategy for the Proj4 library """

    def library_name(self):
        """ Returns the library name of the Proj4 library """
        return 'proj-4.7.0'
    
    def human_name(self):
        """ Returns the human readable name of the Proj4Builder """
        return 'Proj4 Build Process'

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://download.osgeo.org/proj/' + 
                           self.library_name() + '.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), 'proj-4.7.0'))
        self.patch('proj4.patch')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
