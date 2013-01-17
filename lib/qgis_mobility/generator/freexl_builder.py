from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os
from qgis_mobility.generator.libiconv_builder import LibiconvBuilder


class FreeXLBuilder(Builder):
    """ Represents the build strategy for the FreeXL library """

    def library_name(self):
        """ Returns the library name of the FreeXL library """
        return 'freexl-1.0.0e'
    
    def human_name(self):
        """ Returns the human readable name of the FreeXLBuilder """
        return 'FreeXL Build Process'

    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags = LibiconvBuilder(self.get_recon()).salt_flags(Builder.get_default_flags(self))
        flags['LDFLAGS'] += ' -lm'
        return flags

    def salt_flags(self, flags):
        flags = Builder.salt_flags(self, flags)
        pkg_config_path = os.path.join(self.get_build_path(), 'lib', 'pkg_config')
        if 'PKG_CONFIG_PATH' in flags:
            flags['PKG_CONFIG_PATH'] = pkg_config_path
        else:
            flags['PKG_CONFIG_PATH'] += os.path.sep + pkg_config_path
        return flags

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://www.gaia-gis.it/gaia-sins/freexl-1.0.0e.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), 'freexl-1.0.0e'))
        self.patch('freexl.patch', strip=1)
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
