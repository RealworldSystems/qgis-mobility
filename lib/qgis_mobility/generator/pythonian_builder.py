from qgis_mobility.generator.builder import Builder

import os
import subprocess

from qgis_mobility.generator.python_builder import PythonBuilder

class PythonianBuilder(Builder):
    """ Superclass to builders which need host python support """
    
    def __init__(self, recon):
        Builder.__init__(self, recon)
        self._python_builder = PythonBuilder(recon)
        self._host_python_vars = self._python_builder.get_host_python_vars()
    
    def make(self):
        print "=" * 80
        print self.human_name()
        print "=" * 80
        if not self.build_finished:
            #self.purge()
            self._verify_cache()
            self._verify_build_path()
            self._verify_source_path()
            self._verify_include_path()
            self.do_build()
        else:
            print "Already Done"

    def get_include_path(self):
        """ Overrides the default include path """
        return self._python_builder.get_include_path()

    def get_build_path(self):
        """ Overrides the default build path """
        return self._python_builder.get_build_path()

    def get_output_binaries_path(self):
        """ Overrides the default output binaries path """
        return self._python_builder.get_output_binaries_path()

    def get_output_library_path(self):
        """ Overrides the default output library path """
        return self._python_builder.get_output_library_path()
        
    def get_site_packages_path(self):
        """ Adds the method to get the path with site packages """
        library_path = self._python_builder.get_output_library_path()
        return os.path.join(library_path, 'site-packages')

    def get_sip_path(self):
        """ Adds the method get the path for sip """
        return os.path.join(self._python_builder.get_build_path(),
                            'share', 'sip')

    def run_py_configure(self, options=[]):
        """ Adds the python configure.py runner, akin autoconf """
        
        our_env = dict(os.environ).copy()
        our_env['PATH'] = self.get_path()
        
        args = [self._host_python_vars.python,
                'configure.py',
                '-b' + self.get_output_binaries_path(),
                '-d' + self.get_site_packages_path(),
                '-e' + self.get_include_path(),
                '-v' + self.get_sip_path(),
                '-pandroid-g++']
        args.extend(options)
        
        print "Process arguments:", args
        
        process = subprocess.Popen(args, 
                                   cwd=self.get_current_source_path(),
                                   env=our_env)
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("SIP Configure failed")
            
        print "Python Configure Done"
        
    def run_make(self, install=False):
        args = ['make']
        
        if install: args.extend(['install'])

        our_env = dict(os.environ).copy()
        our_env['PATH'] = self.get_path()

        process = subprocess.Popen(args,
                                   cwd=self.get_current_source_path(), 
                                   env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Make failed: ")


    def run_py_configure_and_make(self, options=[]):
        """ Runs the python configure.py runner and the make process """
        
        self.run_py_configure(options)
        self.run_make()
        self.run_make(install=True)
