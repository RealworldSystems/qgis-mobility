from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os
from qgis_mobility.generator.python_builder import PythonBuilder
from qgis_mobility.generator.qgis_builder import QGisBuilder


class RuntimeBuilder(Builder):
    """ Represents the build strategy for the Runtime library """

    def library_name(self):
        """ Returns the library name of the runtime """
        return 'runtime'
    
    def human_name(self):
        """ Returns the human readable name of the Runtime """
        return 'Runtime Build Process'


    def get_default_configure_flags(self):
        flags = Builder.get_default_configure_flags(self)
        flags.extend(['--with-qgis-base-path=' + QGisBuilder(self.get_recon()).get_build_path(),
                      '--with-python-base-path=' + PythonBuilder(self.get_recon()).get_build_path(),
                      '--with-qt-base-path=' + self.get_recon().get_qt_path(),
                      '--with-qt-include-path=' + os.path.join(self.get_recon().get_qt_path(), 'include')])
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
        distutils.dir_util.copy_tree(self.get_runtime_path(), self.get_source_path())
        self.run_autoreconf()
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.fix_config_sub_and_guess()
        self.run_autotools_and_make()
        source_include_path = os.path.join(self.get_build_path(), 'include')
        if os.path.exists(source_include_path):
            distutils.dir_util.copy_tree(
                source_include_path, self.get_include_path())
        self.mark_finished()
