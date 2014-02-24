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

import inspect
import os
import shutil
import fnmatch
import sys
import py_compile
import time
import shutil
from zipfile import ZipFile
from zipfile import ZIP_DEFLATED
from subprocess import Popen
from qgis_mobility.generator.sqlite_builder import SQLiteBuilder
from qgis_mobility.generator.geos_builder import GeosBuilder
from qgis_mobility.generator.proj4_builder import Proj4Builder
from qgis_mobility.generator.spatialite_builder import SpatialiteBuilder
from qgis_mobility.generator.expat_builder import ExpatBuilder
from qgis_mobility.generator.gdal_builder import GDALBuilder
from qgis_mobility.generator.qwt_builder import QWTBuilder
from qgis_mobility.generator.spatialindex_builder import SpatialindexBuilder
from qgis_mobility.generator.python_builder import PythonBuilder
from qgis_mobility.generator.qgis_builder import QGisBuilder
from qgis_mobility.generator.sip_builder import SipBuilder
from qgis_mobility.generator.pyqt_builder import PyQtBuilder
from qgis_mobility.generator.pyqtmobility_builder import PyQtMobilityBuilder
from qgis_mobility.generator.runtime_builder import RuntimeBuilder
        
import xml.etree.ElementTree as ET

class CreatorError(Exception):
    """
    This error is raised whenever something went wrong with the creator
    """
    def __init__(self, value):
        """
        Initializes the error with the given value which should describe
        what went wrong
        """
        self.value = value
    
    def __str__(self):
        """
        Returns a string with the description of what went wrong
        """
        return repr(self.value)

class CreatorFolderExistsError(CreatorError):
    """
    This error is raised whenever the creator finds a path which already exists
    and should not exist
    """
    def __init__(self, path):
        self.value = "Could not create folder: {path}".format(path=path)


class HostConfig(object):
    """
    Instances of this class are responsible for the implementation of
    loading customized configuration from the config.host module.
    """
    def __init__(self, path):
        """
        Initializes host configuration (where available)
        """
        if os.path.exists(os.path.join(path, 'config', 'host', '__init__.py')):
            if not path in sys.path: sys.path.append(path)
            import config.host as host_config
            self.host_config = host_config
        else:
            raise ImportError('Host configuration is not available')
    
    def transform_file(self, dirname, filename):
        """
        Requests the host config to emit a transformed name
        """
        if getattr(self.host_config, 'transform_file'):
            return self.host_config.transform_file(dirname, filename)
        else:
            return filename
           
    def package_name(self):
        """
        Returns the package name to be used for the given application.
        It should be in the form <x>.<y>.<z>, similar to Java packages.
        """
        return self.host_config.package_name

    def name(self):
        """
        Returns the normal name to be used for the given application.
        It should be in a normal form.
        """
        return self.host_config.name

    def version(self):
        """
        Returns the version of the given application (if any is found)
        """
        try:
            return str(self.host_config.version)
        except Exception:
            return "1.0"

class Creator(object):
    """
    The creator is responsible for aiding in the process of application
    development
    """
    def __init__(self, recon):
        self._recon = recon
    
    def gen(self, path):
        """
        Creates a directory structure with the necessary boilerplate for
        further application development
        """
        
        working_folder = os.path.abspath(path)
        
        if os.path.exists(working_folder):
            raise CreatorFolderExistsError(working_folder)
        
        # Further, we need a number of additional folders and items,
        # which are displayed in the following tree
        #
        # config/         - Contains configuration
        # + host/         - Contains configuration for the host, which
        #                   is used by the creator (and sandboxed)
        #   + __init__.py - Initialization for the host configuration       
        # + target/       - Contains configuration for the device, which
        #                   is used by the target
        #   + __init__.py - Initialization for the target configuration
        # app/            - Contains the actual application code
        #   + main.py     - The entry point of the application

        
        host_config = os.path.join(working_folder, 'config', 'host')
        target_config = os.path.join(working_folder, 'config', 'target')
        app = os.path.join(working_folder, 'app')

        for path in [working_folder, host_config, target_config, app, native]:
            print "Creating directory: {path}".format(path=path)
            os.makedirs(path)
        
        host_init_file = os.path.join(host_config, '__init__.py')
        target_init_file = os.path.join(target_config, '__init__.py')
        main_file = os.path.join(app, 'main.py')

        for filename in [host_init_file, target_init_file, main_file]:
            with file(filename, 'a'):
                print "Creating file: {file}".format(file=filename)
                os.utime(filename, None)        

    def __check_out_dir(self, path):
        """
        Checks if the out folder in the application structure exists. If
        it does not exist, it will be created.
        """
        outdir = os.path.join(path, '.out')
        if not os.path.exists(outdir): os.mkdir(outdir)
        return outdir

    def __transform_file(self, dirname, filename):
        
        if dirname == os.path.join('config', 'host'): return None
        if dirname == os.path.join('.out'): return None
        if fnmatch.fnmatch(filename, '*.apk'): return None
        if fnmatch.fnmatch(filename, '*~'): return None
        if fnmatch.fnmatch(filename, '*.pyc'): return None
        if fnmatch.fnmatch(filename, '*.pyo'): return None
        if fnmatch.fnmatch(filename, '*.py'):
            joined = os.path.join(self.working_folder, dirname, filename)
            print("Compiling {0}\n      --> {0}c".format(joined))
            py_compile.compile(joined, joined + 'c', joined, True)
            return self.host_config.transform_file(dirname, filename + 'c')
        return self.host_config.transform_file(dirname, filename)

    def __gather_files_to_pack(self, path):
        basepath_len = len(path) + 1
        for root, dirnames, filenames in os.walk(path, followlinks=True):
            for e in [x for x in dirnames if x[0] == '.']: dirnames.remove(e)
            splitted_root = root[basepath_len :]
            for filename in filenames:
                transformed = self.__transform_file(splitted_root, filename)
                if not transformed == None:
                    yield os.path.join(root, transformed)


    def __setup(self, path):
        working_folder = os.path.abspath(path)
        hc = HostConfig(working_folder)
        self.host_config = hc
        self.working_folder = working_folder

    def pack(self, path):
        """
        Packs the application into a zip file for further deployment
        """
        self.__setup(path)
        outdir = self.__check_out_dir(self.working_folder)
        app_zip = os.path.join(outdir, 'application.zip')
        if os.path.exists(app_zip): os.remove(app_zip)
        zf = ZipFile(app_zip, "w")
        for filename in self.__gather_files_to_pack(self.working_folder):
            name = filename[len(self.working_folder):]
            print("Storing {0}\n    --> [{2}] {1}".format(filename, name, app_zip))
            zf.write(filename, name)
        zf.writestr('timestamp', str(time.time()))
        zf.close()

    def __transform_python_file(self, lib_path, dirname, filename):
        totalfile = os.path.join(lib_path, dirname, filename)
        splitted_dir_name = dirname.split(os.path.sep)
        if len(splitted_dir_name) > 0 and not splitted_dir_name[0] in ['bin', 'lib']: return None
        
        for name in ['uic', 'test', 'tests', 'lib2to3', 'idlelib', 'distutils']:
            if name in splitted_dir_name: return None
   
        
        if fnmatch.fnmatch(filename, "*codecs*.so"): return None
        if fnmatch.fnmatch(filename, "libpython*"): return None
        
        for e in ['grp', 'termios', '_sha256', '_sha512',  'mmap', 
                  '_csv', 'cPickle', '_heapq', '_bisect']:
            if fnmatch.fnmatch(filename, '{0}.so'.format(e)): return None

        if fnmatch.fnmatch(filename, "*.exe"): return None
        if fnmatch.fnmatch(filename, "*.pc"): return None
        if os.path.exists(totalfile + 'c'): return None
        if os.path.exists(totalfile + 'o'): return None
        if fnmatch.fnmatch(filename, "*.pyo") and os.path.exists(totalfile[:-1] + 'c'): return None

        if len(splitted_dir_name) == 1 and splitted_dir_name[0] == 'bin' and not filename == 'python2.7': return None

        return filename

    def __transform_qgsmsystem_file(self, lib_path, dirname, filename):
        if fnmatch.fnmatch(filename, '*~'): return None
        if fnmatch.fnmatch(filename, '*.pyc'): return None
        if fnmatch.fnmatch(filename, '*.pyo'): return None
        if fnmatch.fnmatch(filename, '*.py'):
            joined = os.path.join(lib_path, dirname, filename)
            print("Compiling {0}\n      --> {0}c".format(joined))
            py_compile.compile(joined, joined + 'c', joined, True)
            return filename + 'c'
        return filename

    def __gather_python_files_to_pack(self, path):
        basepath_len = len(path) + 1
        for root, dirnames, filenames in os.walk(path, followlinks=True):
            splitted_root = root[basepath_len :]
            for filename in filenames:
                transformed = self.__transform_python_file(path, splitted_root, filename)
                if not transformed == None:
                    yield os.path.join(root, transformed)
    

    def __gather_qgis_python_files_to_pack(self, path):
        basepath_len = len(path) + 1
        for root, dirnames, filenames in os.walk(path):
            splitted_root = root[basepath_len :]
            for filename in filenames:
                joined = os.path.join(splitted_root, filename)
                if splitted_root.split(os.path.sep)[0] == 'plugins': pass
                elif fnmatch.fnmatch(joined, 'qgis/__init__.py'):
                    yield os.path.join(root, filename)
                elif fnmatch.fnmatch(joined, 'qgis/*.py*'): pass
                else: yield os.path.join(root, filename)

    def __gather_qgsmsystem_files_to_pack(self, path):
        basepath_len = len(path) + 1
        for root, dirnames, filenames in os.walk(path, followlinks=True):
            splitted_root = root[basepath_len :]
            for filename in filenames:
                transformed = self.__transform_qgsmsystem_file(path, splitted_root, filename)
                if not transformed == None:
                    yield os.path.join(root, transformed)

    def __gather_resources_files_to_pack(self, path):
        for root, dirnames, filenames in os.walk(path, followlinks=True):
            for filename in filenames:
                yield os.path.join(root, filename)


    def pack_python(self, path):
        """
        Packs the python assets into a zip file for further deployment
        """
        self.__setup(path)
        
        lib_path = PythonBuilder(self._recon).get_build_path()
        qgis_path = QGisBuilder(self._recon).get_build_path()
        runtime_path = RuntimeBuilder(self._recon).get_build_path()
        qgis_lib_path = os.path.join(qgis_path, 'files', 'share', 'python')
        qgsmsystem_path = os.path.join(runtime_path, 'lib', 'qgis-mobility', 'qgsmsystem')
        resources_path = os.path.join(qgis_path, 'files', 'share', 'resources')

        outdir = self.__check_out_dir(self.working_folder)
        python_zip = os.path.join(outdir, 'python_27.zip')
        qgsmsystem_zip = os.path.join(outdir, 'qgsmsystem.zip')
        resources_zip = os.path.join(outdir, 'resources.zip')

        if os.path.exists(python_zip): os.remove(python_zip)
        zf = ZipFile(python_zip, "w", ZIP_DEFLATED)
        for filename in self.__gather_python_files_to_pack(lib_path):
            name = filename[len(lib_path):]
            if 'QtMobility' in name.split(os.path.sep):
                splitted = name.split(os.path.sep)
                name = os.path.sep + os.path.join('lib', 'python2.7', 'site-packages', 'PyQt4', 
                                                  os.path.join(*splitted[4:])) 
            print("Storing {0}\n    --> [{2}] {1}".format(filename, name, python_zip))
            zf.write(filename, name)
        for filename in self.__gather_qgis_python_files_to_pack(qgis_lib_path):
            name = os.path.sep + os.path.join('lib', 'python2.7', 'site-packages', 
                                              filename[len(qgis_lib_path) + 1:])
            print("Storing {0}\n    --> [{2}] {1}".format(filename, name, python_zip))
            zf.write(filename, name)
        name = os.path.sep + os.path.join('lib', 'libpython2.7.so')
        filename = os.path.join(PythonBuilder(self._recon).get_source_path(), 'libpython2.7.so')
        zf.write(filename, name)
        zf.writestr('timestamp', str(time.time()))
        zf.close()

        zf = ZipFile(qgsmsystem_zip, "w", ZIP_DEFLATED)
        for filename in self.__gather_qgsmsystem_files_to_pack(qgsmsystem_path):
            name = filename[len(qgsmsystem_path):]
            print("Storing {0}\n    --> [{2}] {1}".format(filename, name, qgsmsystem_zip))
            zf.write(filename, name)
        zf.writestr('timestamp', str(time.time()))
        zf.close()

        zf = ZipFile(resources_zip, "w", ZIP_DEFLATED)
        for filename in self.__gather_resources_files_to_pack(resources_path):
            name = filename[len(resources_path):]
            print("Storing {0}\n    --> [{2}] {1}".format(filename, name, resources_zip))
            zf.write(filename, name)
        zf.writestr('timestamp', str(time.time()))
        zf.close()
        
    def android(self, path):
        """
        Sets up the APK skeleton
        """
        self.__setup(path)

        current_path = os.path.realpath(os.path.dirname(
            inspect.getfile(inspect.currentframe())))

        share_path = os.path.join(current_path, '..', '..', '..', 'share')
        android_path = os.path.join(share_path, 'android')
        outdir = self.__check_out_dir(self.working_folder)
        android_out = os.path.join(outdir, 'android')
        
        if os.path.exists(android_out):
            shutil.rmtree(android_out)
        
        shutil.copytree(android_path, android_out)

        # Write local.properties
        line = "sdk.dir: {0}\n".format(self._recon.get_sdk_path())
        f = file(os.path.join(android_out, 'local.properties'), 'w')
        f.write(line)
        f.close()

        # set package name in XML
        et = ET.ElementTree()
        et.parse(os.path.join(android_out, 'AndroidManifest.xml'))
        et.getroot().attrib['package'] = self.host_config.package_name()
        version_name = '{http://schemas.android.com/apk/res/android}versionName'
        v = self.host_config.version()
        print "Setting version: {0}".format(v)
        et.getroot().attrib[version_name] = v
        et.write(os.path.join(android_out, 'AndroidManifest.xml'),  'utf-8', True)

        # set derived normal name in ant file
        et = ET.ElementTree()
        et.parse(os.path.join(android_out, 'build.xml'))
        et.getroot().attrib['name'] = self.host_config.name()
        et.write(os.path.join(android_out, 'build.xml'),  'utf-8', True)

        # set derived normal name in strings.xml
        et = ET.ElementTree()
        et.parse(os.path.join(android_out, 'res', 'values', 'strings.xml'))
        for child in et.getroot().getchildren():
            if child.attrib['name'] == 'app_name':
                child.text = self.host_config.name()
        et.write(os.path.join(android_out, 'res', 'values', 'strings.xml'),  'utf-8', True)

        # @R@ needs to be replaced with self.host_config.package_name.QGisMobility.R
        qt_activity_file_name = os.path.join(android_out, 'src', 'org', 'kde',
                                             'necessitas', 'origo', 'QtActivity.java')
        
        args = ['sed']
        args.extend(['-i', 
                     "s/@R@/%s.R/" % self.host_config.package_name(),
                     qt_activity_file_name])
        process = Popen(args)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])
        print "Sed finished with:", path

        
    def __run_ant(self, command):
        outdir = self.__check_out_dir(self.working_folder)
        android_out = os.path.join(outdir, 'android')
        process = Popen(['ant', command], cwd=android_out)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])


    def make_apk_debug(self, path):
        self.__setup(path)

        self.pack(path)
        self.pack_python(path)
        self.android(path)
        outdir = self.__check_out_dir(self.working_folder)
        rawdir = os.path.join(outdir, 'android', 'res', 'raw')
        
        for zipfile in ['application.zip', 'resources.zip', 'python_27.zip', 'qgsmsystem.zip']:
            if not os.path.exists(rawdir): os.makedirs(rawdir)
            shutil.copyfile(os.path.join(outdir, zipfile),
                            os.path.join(rawdir, zipfile))
            
        build_path = lambda builder: builder(self._recon).build_path

        shared_objects = [
            os.path.join(build_path(GeosBuilder), 'lib', 'libgeos.so'),
            os.path.join(build_path(GeosBuilder), 'lib', 'libgeos_c.so'),
            os.path.join(build_path(ExpatBuilder), 'lib', 'libexpat.so'),
            os.path.join(build_path(GDALBuilder), 'lib', 'libgdal.so'),
            os.path.join(build_path(Proj4Builder), 'lib', 'libproj.so'),
            os.path.join(build_path(QGisBuilder), 'lib', 'libqgis_core.so'),
            os.path.join(build_path(QGisBuilder), 'lib', 'libqgispython.so'),
            os.path.join(build_path(QGisBuilder), 'lib', 'libspatialiteprovider.so'),
            os.path.join(build_path(RuntimeBuilder), 'lib', 'libqgismobility.so'),
            os.path.join(build_path(SpatialindexBuilder), 'lib', 'libspatialindex.so'),
            os.path.join(build_path(SpatialindexBuilder), 'lib', 'libspatialindex_c.so'),
            os.path.join(build_path(SpatialiteBuilder), 'lib', 'libspatialite.so'),
            os.path.join(build_path(SQLiteBuilder), 'lib', 'libsqlite3.so'),
        ]

        for so in shared_objects:
            to = os.path.join(outdir, 'android', 'libs', 'armeabi', 
                              so.split(os.path.sep)[-1])
            print("Copying {0}\n    --> {1}".format(so, to))
            shutil.copyfile(so, to)

        icon = os.path.join(self.working_folder, 'config', 'host', 'icon.png')
        if os.path.exists(icon):
            shutil.copyfile(icon, os.path.join(outdir, 'android', 'res', 'drawable', 'icon.png'))
        
        self.__run_ant('debug')
        apkname = self.host_config.name() + '-debug.apk'
        shutil.copyfile(os.path.join(outdir, 'android', 'bin', apkname),
                        os.path.join(self.working_folder, apkname))
        
