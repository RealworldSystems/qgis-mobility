from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os

class ExpatBuilder(Builder):
    """ Represents the build strategy for the Expat library """

    def library_name(self):
        """ Returns the library name of the Expat library """
        return 'expat-2.0.1'
    
    def human_name(self):
        """ Returns the human readable name of the Expat Builder """
        return 'Expat Build Process'    

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://freefr.dl.sourceforge.net/project/expat/expat/2.0.1/expat-2.0.1.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.push_current_source_path(os.path.join(self.get_current_source_path(), 'conftools'))
        self.fix_config_sub_and_guess()
        self.pop_current_source_path()
        self.patch('expat.patch', strip=1)
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        
        self.mark_finished()


