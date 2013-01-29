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

import os, inspect
import shutil
import subprocess
from subprocess import Popen
import re


class Builder(object):
    """ Represents an abstract object to aid in building the different sources """
    
    def __init__(self, recon):
        self.verify()
        self._current_path = self._get_current_path()
        self._library_name = self.library_name()
        self._recon = recon
        self._sourcepaths = [os.path.join(self.cache_path, "source", self._library_name)]
    
    def get_recon(self):
        """ Returns the recon object """
        return self._recon

    def library_name(self):
        raise ValueError("Should implement the library_name method")

    def do_build(self):
        raise ValueError("Should implement the do_build method")

    def human_name(self):
        raise ValueError("Should implement the human_name method")

    def salt_flags(self, flags):
        """ Provides a base flag salter """
        libs = os.path.join(self.get_build_path(), 'lib')
        includes = os.path.join(self.get_include_path())
        flags['LDFLAGS'] += ' -L' + libs
        flags['CFLAGS'] += ' -I' + includes
        flags['CXXFLAGS'] += ' -I' + includes
        if not 'LD_LIBRARY_PATH' in flags:
            flags['LD_LIBRARY_PATH'] = os.path.join(self.get_build_path(), 'lib')
        else:
            flags['LD_LIBRARY_PATH'] += os.pathsep + os.path.join(self.get_build_path(), 'lib')
        return flags

    def insert_config_path_flag(self, flags):
        pkg_config_path = os.path.join(self.get_build_path(), 'lib', 'pkg_config')
        if not 'PKG_CONFIG_PATH' in flags:
            flags['PKG_CONFIG_PATH'] = pkg_config_path
        else:
            flags['PKG_CONFIG_PATH'] += os.pathsep + pkg_config_path
        return flags

    def push_current_source_path(self, path):
        self._sourcepaths.extend([path])

    def pop_current_source_path(self):
        self._sourcepaths.pop()


    def make(self):
        print "=" * 80
        print self.human_name()
        print "=" * 80
        if not self.build_finished:
            self.purge()
            self._verify_cache()
            self._verify_build_path()
            self._verify_source_path()
            self._verify_include_path()
            self.do_build()
        else:
            print "Already Done"
    
    def purge(self):
        if os.path.exists(self.get_build_path()):
            shutil.rmtree(self.get_build_path())
        if os.path.exists(self.get_source_path()):
            shutil.rmtree(self.get_source_path())
        if os.path.exists(self.get_include_path()):
            shutil.rmtree(self.get_include_path())
        
    def _get_current_path(self):
        return os.path.realpath(os.path.dirname(
            inspect.getfile(inspect.currentframe())))

    def get_build_finished_file(self):
        return os.path.join(
            self.cache_path, '.fini' + self._library_name)
    
    def get_build_finished(self):
        return os.path.exists(self.get_build_finished_file())
    
    build_finished = property(get_build_finished, None, None, 
                              "True if the build is finished")
    
    def mark_finished(self):
        with open(self.get_build_finished_file(), 'w'):
            pass

    def get_home_path(self):
        """ Return the home path """
        return self._recon.get_home_path()
    
    home_path = property(get_home_path, None, None, "The HOME path")
    
    def get_cache_path(self):
        """ Returns the cache path """
        return self._recon.get_cache_path()
    
    cache_path = property(get_cache_path, None, None, "The QGIS Mobility cache")
    

    def get_runtime_path(self):
        """ Returns the path pointing to the runtime sources """
        return os.path.join(self._current_path, '..', '..', '..', 'runtime')

    def get_core_patch_path(self):
        return os.path.join(self._current_path, '..', '..', '..', 'patches')

    def get_patch_path(self):
        patches_path = self.get_core_patch_path()
        path = os.path.abspath(os.path.join(patches_path, self._library_name))
        if os.path.exists(path): return path
        else: return None
    
    patch_path = property(get_patch_path, None, None, "The path with the patches")
    
    def get_build_path(self):
        return os.path.join(self.cache_path, "build", self._library_name)
    
    build_path = property(get_build_path, None, None, "The path with the builds")


    def get_output_library_path(self):
        """ Returns the path where normally libraries should be found """
        return os.path.join(self.get_build_path(), 'lib')

    def get_output_binaries_path(self):
        """ Returns the path where normally the binaries should be found """
        return os.path.join(self.get_build_path(), 'bin')
    
    def get_include_path(self):
        return os.path.join(self.cache_path, "include", self._library_name)

    def get_source_path(self):
        return os.path.join(self.cache_path, "source", self._library_name)
    
    def get_current_source_path(self):
        return self._sourcepaths[-1]

    def get_toolchain_prefix(self):
        """ Returns the prefix of the GCC toolchain """
        return 'arm-linux-androideabi-'
    
    def get_tool(self, tool_name):
        """ Returns a GCC tool form the toolchain with the right prefix """
        return self.get_toolchain_prefix() + tool_name

    def get_default_toolchain_mappings(self):
        return { 'CC'     : self.get_tool('gcc'),
                 'CXX'    : self.get_tool('g++'),
                 'LD'     : self.get_tool('ld'),
                 'AR'     : self.get_tool('ar'),
                 'RANLIB' : self.get_tool('ranlib'),
                 'AS'     : self.get_tool('as') }


    def get_default_flags(self):
        cflags = '-DANDROID=ON -Wno-psabi -O2 -mthumb'
        ldflags = '-Wl,--fix-cortex-a8'
        return { 'CFLAGS'   : cflags,
                 'LDFLAGS'  : ldflags,
                 'CXXFLAGS' : cflags + ' --std=gnu++0x' }

    def get_default_configure_flags(self):
        return ['--host=arm-linux-androideabi', '--prefix=' + self.get_build_path()]
    
    def get_path(self):
        default_path = ''
        if 'PATH' in os.environ: default_path = os.environ['PATH']
        arm_toolchain_path = os.path.join(self._recon.get_toolchain_path(), 'bin')
        sdk_tools = os.path.join(self._recon.sdk_path, 'tools')
        platform_tools = os.path.join(self._recon.sdk_path, 'platform-tools')
        return os.pathsep.join([arm_toolchain_path, sdk_tools, 
                                platform_tools, default_path])
        
    def _verify_cache(self):
        if not os.path.exists(self.get_cache_path()):
            os.makedirs(self.get_cache_path())
    
    def _verify_build_path(self):
        if not os.path.exists(self.get_build_path()):
            os.makedirs(self.get_build_path())

    def _verify_source_path(self):
        if not os.path.exists(self.get_source_path()):
            os.makedirs(self.get_source_path())

    def _verify_include_path(self):
        if not os.path.exists(self.get_include_path()):
            os.makedirs(self.get_include_path())

    def verify(self):
        if not 'HOME' in os.environ: 
            raise EnvironmentError("HOME should be defined in the environment")
    
    def _call_process(self, args):
        output = subprocess.call(args)
        if output != 0:
            raise ValueError("Failed Process: " + args[0])

    def wget(self, url):
        args = ['wget', '-P', self.get_current_source_path(), url]
        self._call_process(args)
        storage = os.path.join(self.get_current_source_path(), url.split('/')[-1])
        print "File stored at:", storage
        return storage

    def patch(self, patch_name, strip=None):
        patch_file = os.path.join(self.patch_path, patch_name)
        args = ['patch']
        if not strip == None: args.extend(['-p' + str(strip)])
        args.extend(['-d', self.get_current_source_path(), '-i', patch_file])
        self._call_process(args)
        print "Patched path:", self.get_current_source_path()
        print "Patched ( with -i ) using:", patch_file

    def sed(self, sedstring, path, options=None):
        args = ['sed']
        if not options == None: args.extend(options)
        args.extend([sedstring, path])
        process = Popen(args, cwd=self.get_current_source_path())
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])
        print "Sed finished with:", path

    def sed_i(self, sedstring, path):
        self.sed(sedstring, path, options=['-i'])        

    def sed_ir(self, sedstring, path):
        self.sed(sedstring, path, options=['-i', '-r'])
        
    def sed_ie(self, sedstring, path):
        self.sed(sedstring, path, options=['-i', '-e'])

    def unpack(self, archive):
        extension_groups = re.search("[.]([^.]*)$", archive).groups()
        unpack_method = 'xzvf'
        if len(extension_groups) > 0:
            if extension_groups[0] == "bz2": unpack_method = "xjvf"
        args = ['tar', unpack_method, archive, '-C', self.get_current_source_path()]
        print args
        self._call_process(args)
        print "Unpacked using:", archive
    
    def fix_config_sub_and_guess(self):
        config_sub_path = os.path.join(self.get_current_source_path(), 'config.sub')
        config_guess_path = os.path.join(self.get_current_source_path(), 'config.guess')
        if os.path.exists(config_sub_path):
            os.remove(os.path.join(self.get_current_source_path(), 'config.sub'))
        if os.path.exists(config_guess_path):
            os.remove(os.path.join(self.get_current_source_path(), 'config.guess'))
        shutil.copyfile(os.path.join(self.get_core_patch_path(), 'config', 'config.sub'),
                        os.path.join(self.get_current_source_path(), "config.sub"))
        shutil.copyfile(os.path.join(self.get_core_patch_path(), 'config', 'config.guess'),
                        os.path.join(self.get_current_source_path(), "config.guess"))

    def run_svn_checkout(self, url, path=None):
        args = ['svn', 'checkout', url]
        if not path == None: args.extend([path])
        process = Popen(args, cwd=self.get_current_source_path())
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])
        print "SVN Checkout performed from:", url
        

    def run_autogen(self):
        process = Popen(['bash', 'autogen.sh'], cwd=self.get_current_source_path())
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])
        print "Autogeneration done"

    def run_autoreconf(self):
        process = Popen(['autoreconf'], cwd=self.get_current_source_path())
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])
        print "Auto(re)configuration done"
        

    def run_autotools_and_make(self, where=None, harness=True, runmakeinstall=True):
        harnessed_source_path = self.get_current_source_path()
        if harness:
            harnessed_source_path = os.path.join(self.get_current_source_path(), 'harness')
            if not os.path.exists(harnessed_source_path): os.makedirs(harnessed_source_path)

        our_env = dict(os.environ).copy()
        our_env['PATH'] = self.get_path()

        environmental = []
        
        flags = self.get_default_flags()
        for flag in flags: environmental.extend([flag + '=' + flags[flag]])
        
        mappings = self.get_default_toolchain_mappings()
        for flag in mappings: environmental.extend([flag + '=' + mappings[flag]])
        
        if where == None: where = self.get_current_source_path()

        args = [os.path.join(where, 'configure')]
        args.extend(environmental)
        args.extend(self.get_default_configure_flags())
        all_processes = [args]
        if runmakeinstall: all_processes.extend([['make'], ['make', 'install']])
        for arguments in all_processes:
            process = Popen(arguments, cwd=harnessed_source_path, env=our_env)
            process.communicate(None)
            if not process.returncode == 0:
                raise ValueError("Failed Process: " + arguments[0])
        
        print "Autotools and Make ended in:", where
        

    def run_qmake_and_make(self):
        harnessed_source_path = os.path.join(self.get_current_source_path(), 'harness')
        os.makedirs(harnessed_source_path)
        our_env = dict(os.environ).copy()
        our_env['PATH'] = self.get_path()
        
        flags = self.get_default_flags()
        for flag in flags: our_env[flag] = flags[flag]
        
        mappings = self.get_default_toolchain_mappings()
        for flag in mappings: our_env[flag] = mappings[flag]
        
        args = [os.path.join(self.get_recon().qt_tools_path, 'qmake'), 
                os.path.join(self.get_current_source_path(), 'qwt.pro')]
        
        process = Popen(args, cwd=harnessed_source_path, env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + arguments[0])
        
        process = Popen(['make'], cwd=harnessed_source_path, env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + arguments[0])

        our_env['INSTALL_ROOT'] = self.get_build_path()
        
        process = Popen(['make', 'install'], cwd=harnessed_source_path, env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + arguments[0])
            
    def run_make(self, path=None, makefile=None):
        args = ['make']
        if makefile != None:
            args.extend(['-f' + makefile])
        if path == None:
            path = self.build_path
        
        for flag in self.get_default_flags():
            value = self.get_default_flags()[flag]
            args.extend([flag + '=' + value])
        
        print args

        our_env = dict(os.environ).copy()
        our_env['PATH'] = self.get_path()

        process = Popen(args, cwd=path, env=our_env)
        process.communicate(None)
        if not process.returncode == 0:
            raise ValueError("Failed Process: " + args[0])

        print "Make ended in: ", path
