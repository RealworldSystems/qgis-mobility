from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os
import shutil

class SpatialindexBuilder(Builder):
    """ Represents the build strategy for the SpatialIndex library """

    def library_name(self):
        """ Returns the library name of the SpatialIndex library """
        return 'spatialindex-1.7.1'
    
    def human_name(self):
        """ Returns the human readable name of the Spatialite Builder """
        return 'SpatialIndex Build Process'


    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags = Builder.get_default_flags(self)
        gnu_libstdcxx = os.path.join(self.get_recon().get_ndk_path(),
                                     'sources', 'cxx-stl', 'gnu-libstdc++',
                                     '4.4.3', 'libs', 'armeabi')

        flags['CXXFLAGS'] = MY_STD_CXXFLAGS="-L" + gnu_libstdcxx + ' ' + flags['CXXFLAGS']
        flags['CXXFLAGS'] += ' -lsupc++ -llog -lz -lm -ldl -lc -lgcc -lgnustl_static -lz -lm -ldl -lm'
        return flags


    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://download.osgeo.org/libspatialindex/spatialindex-src-1.7.1.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), 'spatialindex-src-1.7.1'))
        self.fix_config_sub_and_guess()
        self.patch('spatialindex.patch', strip=1)
        self.sed_ir('s/(hardcode_into_libs)=.*$/\\1=no/', 'configure')
        self.run_autotools_and_make(harness=False)        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        # Fix header weirdness
        src = os.path.join(self.get_include_path(), 'spatialindex')
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, self.get_include_path())
        shutil.copytree(os.path.join(src, 'tools'), os.path.join(self.get_include_path(), 'tools'))
        self.mark_finished()


