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

from qgis_mobility.generator.builder import Builder

import os
import subprocess
import shutil

from qgis_mobility.generator.python_builder import PythonBuilder

class PythonianBuilder(Builder):
    """ Superclass to builders which need host python support """
    
    def __init__(self, recon):
        Builder.__init__(self, recon)
        self._python_builder = PythonBuilder(recon)
        self._host_python_vars = self._python_builder.get_host_python_vars()
    
    def purge(self, arch):
        if os.path.exists(self.get_source_path(arch)):
            shutil.rmtree(self.get_source_path(arch))


    def get_build_finished_file(self):
        """
        The build finished file is altered, so the python builder can purge the
        files if necessary
        """
        return os.path.join(
            self.cache_path, '.py_fini' + self._library_name)

    def get_include_path(self, arch=None):
        """ Overrides the default include path """
        return self._python_builder.get_include_path(arch)

    def get_build_path(self, arch=None):
        """ Overrides the default build path """
        return self._python_builder.get_build_path(arch)

    def get_output_binaries_path(self):
        """ Overrides the default output binaries path """
        return self._python_builder.get_output_binaries_path()

    def get_output_library_path(self):
        """ Overrides the default output library path """
        return self._python_builder.get_output_library_path()
        
    def get_site_packages_path(self):
        """ Adds the method to get the path with site packages """
        library_path = self._python_builder.get_output_library_path()
        return os.path.join(library_path, 'python2.7', 'site-packages')

    def get_sip_path(self):
        """ Adds the method get the path for sip """
        return os.path.join(self._python_builder.get_build_path(),
                            'share', 'sip')

    def run_py_configure(self, options=[], host=False, binaries=True):
        """ Adds the python configure.py runner, akin autoconf """

        
        our_env = dict(os.environ).copy()
        if not host: 
            mappings = self.get_default_toolchain_mappings()
            our_env['PATH'] = os.pathsep.join([self.get_recon().qt_tools_path, 
                                               self.get_path()])
            our_env['QMAKESPEC'] = 'android-g++'
            for mapping in mappings: our_env[mapping] = mappings[mapping]
        
        args = [self._host_python_vars.python,
                'configure.py']

        if not host: 
            args.extend([
                '-d' + self.get_site_packages_path(),
                '-v' + self.get_sip_path()])
            if binaries:
                args.extend(['-b' + self.get_output_binaries_path()])


        args.extend(options)

        print "PATH:", our_env['PATH']
        
        print "Process arguments:", args
        
        process = subprocess.Popen(args, 
                                   cwd=self.get_current_source_path(),
                                   env=our_env)
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("Python Configure failed")
            
        print "Python Configure Done"
        
    def run_py_setup(self, option="build"):
        """ Adds the setup.py runner, akin configure/make """
        arch = self.get_current_arch()
        host = (arch == 'host')
        
        our_env = dict(os.environ).copy()
        mappings = self.get_default_toolchain_mappings()
        if not host: 
            our_env['PATH'] = os.pathsep.join([self.get_recon().qt_tools_path, 
                                               self.get_path()])
            our_env['QMAKESPEC'] = 'android-g++'
        for mapping in mappings: our_env[mapping] = mappings[mapping]
        
        args = [self._host_python_vars.python,
                'setup.py', option]

        print "PATH:", our_env['PATH']
        
        print "Process arguments:", args
        
        process = subprocess.Popen(args, 
                                   cwd=self.get_current_source_path(),
                                   env=our_env)
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("Setup.py failed")
            
        print "Setup.py Done"
    
    def run_py_setup_build_and_install(self):
        self.run_py_setup("build")
        self.run_py_setup("install")

    def run_make(self, install=False, host=False, command=None, makeopts=[]):
        args = ['make']
        
        if install: args.extend(['install'])

        if command != None and (not install):
            args.extend([command])

        args.extend(makeopts)

        our_env = dict(os.environ).copy()

        if not host: our_env['PATH'] = self.get_path()

        print args

        process = subprocess.Popen(args,
                                   cwd=self.get_current_source_path(), 
                                   env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Make failed: ")


    def run_py_configure_and_make(self, options=[], host=False, makeopts=[]):
        """ Runs the python configure.py runner and the make process """
        if os.path.exists(
                os.path.join(self.get_current_source_path(),
                             'Makefile')):
            self.run_make(command='clean')
        
        self.run_py_configure(options=options, host=host)
        self.run_make(host=host, makeopts=makeopts)
        self.run_make(install=True, host=host, makeopts=makeopts)
