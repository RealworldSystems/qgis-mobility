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


