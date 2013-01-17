from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os
import shutil
import subprocess
import multiprocessing

from qgis_mobility.generator.bzip2_builder import BZip2Builder
from qgis_mobility.generator.libiconv_builder import LibiconvBuilder
from qgis_mobility.generator.freexl_builder import FreeXLBuilder
from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder
from qgis_mobility.generator.spatialite_builder import SpatialiteBuilder
from qgis_mobility.generator.expat_builder import ExpatBuilder
from qgis_mobility.generator.gdal_builder import GDALBuilder
from qgis_mobility.generator.gsl_builder import GSLBuilder
from qgis_mobility.generator.qwt_builder import QWTBuilder
from qgis_mobility.generator.spatialindex_builder import SpatialindexBuilder


class QGisBuilder(Builder):
    """ Represents the build strategy for the QGis library """

    def library_name(self):
        """ Returns the library name of the QGis library """
        return 'qgis-1.8.0'
    
    def human_name(self):
        """ Returns the human readable name of the Spatialite Builder """
        return 'QGis Build Process'


    def get_default_flags(self):
        """ Returns the default flags salted with dependencies """
        flags = Builder.get_default_flags(self)
        gnu_libstdcxx = os.path.join(self.get_recon().get_ndk_path(),
                                     'sources', 'cxx-stl', 'gnu-libstdc++',
                                     '4.4.3', 'libs', 'armeabi')

        flags['CXXFLAGS'] = MY_STD_CXXFLAGS="-L" + gnu_libstdcxx + ' ' + flags['CXXFLAGS']
        flags['CXXFLAGS'] += ' -lsupc++ -llog -lz -lm -ldl -lc -lgcc -lgnustl_static -lz -lm -ldl -lm'
        return flags


    def do_download_cache(self):
        """
        Performs a check whether the library has been downloaded,
        otherwise, downloads it. When available, copy it to the
        qgis path
        """
        qgis_packed_library = self.library_name() + '.tar.bz2'
        excursion_path = os.path.join(self.get_source_path(), '..', 'qgis_download')
        download_path = os.path.join(excursion_path, qgis_packed_library)
        if not os.path.exists(download_path):
            if not os.path.exists(excursion_path): os.makedirs(excursion_path)
            self.push_current_source_path(os.path.join(excursion_path))
            self.wget('http://qgis.org/downloads/' + self.library_name() + '.tar.bz2')
            self.pop_current_source_path()
        
        qgis_packed_path = os.path.join(self.get_current_source_path(), 
                                        qgis_packed_library)
        shutil.copyfile(download_path, qgis_packed_path)
        return qgis_packed_path

    def add_definitions(self):
        source_path = self.get_current_source_path()
        f = open(os.path.join(source_path, 'initial.cmake'), 'w+')
        f.write('ADD_DEFINITIONS(-DQT_STL)\n')
        f.close()
        
        # Concatenate initial.cmake and CMakeLists.txt
        
        destination = open(os.path.join(source_path, 'new.txt'), 'w+')
        shutil.copyfileobj(open(os.path.join(source_path, 'initial.cmake')), destination)
        shutil.copyfileobj(open(os.path.join(source_path, 'CMakeLists.txt')), destination)
        destination.close()
        
        # Remove original CMakeLists.txt and replace with new.txt
        os.remove(os.path.join(source_path, 'CMakeLists.txt'))
        os.rename(os.path.join(source_path, 'new.txt'),
                  os.path.join(source_path, 'CMakeLists.txt'))

    def do_build(self):
        """ Runs the actual build process """
        # Downloading qgis is a big process. We escape to another directory and see if it is
        # downloaded already
        output = self.do_download_cache()
        
        # Resuming normal operations
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        
        recon = self.get_recon()

        # QGis uses (as only library in this whole project) cmake. We need to set up a number
        # of things for this.
        
        our_env = dict(os.environ).copy()
        our_env['QT_ROOT'] = recon.qt_path
        our_env['ANDROID_LEVEL'] = str(recon.android_level)
        our_env['ANDROID_NDK_PLATFORM'] = 'android-' + str(recon.android_level)
        our_env['ANDROID_NDK_TOOLCHAIN_ROOT'] = recon.get_toolchain_path()
        our_env['ANDROID_NDK_HOST'] = 'linux-x86'
        our_env['ANDROID_NDK_TOOLCHAIN_PREFIX'] = 'arm-linux-androideabi'
        our_env['ANDROID_NDK_TOOLCHAIN_VERSION'] = '4.4.3'
        our_env['QT_INCLUDE_DIR'] = os.path.join(our_env['QT_ROOT'], 'include')
        our_env['QT_LIBRARY_DIR'] = os.path.join(our_env['QT_ROOT'], 'lib')
        our_env['QMAKE'] = os.path.join(recon.qt_tools_path, 'qmake')
        our_env['PATH'] = self.get_path()
        our_env['INSTALL_DIR'] = self.get_build_path()
        
        # We need to add some definitions
        self.add_definitions()

        self.sed_i('s/SPATIALITE_INCLUDE_DIR/\\SPATIALITE_INCLUDE_DIR\\} \\$\\{SQLITE3_INCLUDE_DIR/',
                   'src/providers/spatialite/CMakeLists.txt')
        
        # Do the argument dance
        toolchain_src = os.path.join(self.get_core_patch_path(), 'cmake', 'android.toolchain.cmake')
        toolchain_file = os.path.join(self.get_current_source_path(), 'android.toolchain.cmake')
        shutil.copyfile(toolchain_src, toolchain_file)
        
        arguments = { 'ANDROID'              : 'true',
                      'ARM_TARGET'           : 'armeabi',
                      'CMAKE_INSTALL_PREFIX' : self.get_build_path(),
                      'CMAKE_TOOLCHAIN_FILE' : toolchain_file,
                      'QT_MKSPECS_DIR'       : os.path.join(recon.qt_path, 'mkspecs'),
                      'QT_QMAKE_EXECUTABLE'  : os.path.join(recon.qt_tools_path, 'qmake'),
                      'GDAL_CONFIG'          : os.path.join(GDALBuilder(recon).get_build_path(),
                                                            'bin', 'gdal-config'),
                      'GDAL_INCLUDE_DIR'     : GDALBuilder(recon).get_include_path(),
                      'GDAL_LIBRARY'         : os.path.join(GDALBuilder(recon).get_build_path(),
                                                            'lib', 'libgdal.so'),
                      'GEOS_CONFIG'          : os.path.join(GeosBuilder(recon).get_build_path(),
                                                            'bin', 'geos-config'),
                      'GEOS_INCLUDE_DIR'     : GeosBuilder(recon).get_include_path(),
                      'GEOS_LIBRARY'         : os.path.join(GeosBuilder(recon).get_build_path(),
                                                            'lib', 'libgeos_c.so'),
                      'EXPAT_INCLUDE_DIR'    : ExpatBuilder(recon).get_include_path(),
                      'EXPAT_LIBRARY'        : os.path.join(ExpatBuilder(recon).get_build_path(),
                                                            'lib', 'libexpat.so'),
                      'PROJ_INCLUDE_DIR'     : Proj4Builder(recon).get_include_path(),
                      'PROJ_LIBRARY'         : os.path.join(Proj4Builder(recon).get_build_path(),
                                                            'lib', 'libproj.so'),
                      'CHARSET_LIBRARY'      : os.path.join(LibiconvBuilder(recon).get_build_path(),
                                                            'lib', 'libcharset.so'),
                      'QWT_INCLUDE_DIR'      : QWTBuilder(recon).get_include_path(),
                      'QWT_LIBRARY'          : os.path.join(QWTBuilder(recon).get_build_path(),
                                                            'libs', 'armeabi', 'libqwt.a'),
                      'QT_MOBILITY_INCLUDE_DIR' : os.path.join(recon.qt_path, 'include',
                                                               'QtMobility'),
                      'SQLITE3_LIBRARY'      : os.path.join(SQLiteBuilder(recon).get_build_path(),
                                                            'lib', 'libsqlite3.so'),
                      'SQLITE3_INCLUDE_DIR'  : SQLiteBuilder(recon).get_include_path(),
                      'SPATIALITE_LIBRARY'   : os.path.join(SpatialiteBuilder(recon).get_build_path(),
                                                            'lib', 'libspatialite.so'),
                      'FLEX_EXECUTABLE'      : '/usr/bin/flex',
                      'BISON_EXECUTABLE'     : '/usr/bin/bison',
                      'SPATIALINDEX_INCLUDE_DIR' : SpatialindexBuilder(recon).get_include_path(),
                      'SPATIALINDEX_LIBRARY' :  os.path.join(SpatialindexBuilder(recon).get_build_path(),
                                                             'lib', 'libspatialindex.so'),
                      'NO_SWIG' : 'true', 
                      'PEDANTIC' : 'OFF',
                      'WITH_APIDOC' : 'OFF',
                      'WITH_DESKTOP' : 'OFF',
                      'WITH_BINDINGS' : 'OFF',
                      'WITH_GLOBE' : 'OFF',
                      'WITH_GRASS' : 'OFF',
                      'WITH_INTERNAL_QWTPOLAR' : 'ON',
                      'WITH_MAPSERVER' : 'OFF',
                      'WITH_POSTGRESQL' : 'OFF',
                      'WITH_SPATIALITE' : 'ON',
                      'WITH_TXT2TAGS_PDF' : 'OFF',
                      'WITH_QTMOBILITY' : 'ON',
                      'ENABLE_TESTS' : 'OFF' }
        args = ['cmake']        
        for arg in arguments:
            args.extend(['-D' + arg + '=' + arguments[arg]])
        args.extend(['.'])
        process = subprocess.Popen(args, cwd=self.get_current_source_path(), env=our_env)
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("Failed Process:", args[0])
        cpuflag = '-j' + str(multiprocessing.cpu_count())
        process = subprocess.Popen(['make', 'VERBOSE=1', cpuflag, 'install'],
                                   cwd=self.get_current_source_path(), env=our_env)
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("Failed Process:", args[0])
        print 'Done building QGis Base'
        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        
        self.mark_finished()
