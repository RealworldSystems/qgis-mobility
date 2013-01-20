from qgis_mobility.generator.builder import Builder
import os
import subprocess
import multiprocessing
import shutil
import collections

from qgis_mobility.generator.sqlite_builder import SQLiteBuilder

class PythonBuilder(Builder):
    """ Represents the build strategy for the Python Builder """

    def __init__(self, recon):
        Builder.__init__(self, recon)
        self._build_shared = ' '.join([self.get_tool('gcc'), 
                                       '--shared', self.get_cflags()])
    
    def library_name(self):
        """ Returns the librrary name of the python version to build """
        return 'Python-2.7.2'
    
    def human_name(self):
        """ Returns the human readable name of the Python Builder """
        return 'Python Build Process'
    
    def get_path(self):
        """ Also return the path of the ndk itself """
        return os.pathsep.join([self.get_recon().get_ndk_path(),
                                Builder.get_path(self)])
    def do_download_cache(self):
        """
        Performs a check whether the library has been downloaded,
        otherwise, downloads it. When available, copy it to the
        qgis path
        """
        python_packed_library = self.library_name() + '.tgz'
        excursion_path = os.path.join(self.get_source_path(), '..', 'python_download')
        download_path = os.path.join(excursion_path, python_packed_library)
        if not os.path.exists(download_path):
            if not os.path.exists(excursion_path): os.makedirs(excursion_path)
            self.push_current_source_path(os.path.join(excursion_path))
            self.wget('http://www.python.org/ftp/python/2.7.2/' + 
                      self.library_name() + '.tgz')
            self.pop_current_source_path()
        python_packed_path = os.path.join(self.get_current_source_path(), 
                                        python_packed_library)
        shutil.copyfile(download_path, python_packed_path)
        return python_packed_path

    def get_default_configure_flags(self):
        """ Overrides the default configure flags for the specifics of Python """
        return ['--host=arm-eabi', '--build=x86_64-linux-gnu','--enable-shared']

    def get_host_python_prefix(self):
        return os.path.join(self.get_recon().get_cache_path(), 'hostpython')

    def get_host_python_vars(self):
        host_python_prefix = self.get_host_python_prefix()
        PythonVars = collections.namedtuple('PythonVars', ['bin', 'python', 'pgen'])
        return PythonVars(bin=os.path.join(host_python_prefix, 'bin'),
                          python=os.path.join(host_python_prefix, 'bin', 'python'),
                          pgen=os.path.join(self.get_source_path(), 'host', 'Parser', 'pgen'))

    def get_cflags(self):
        return ' '.join(['-mandroid -O2 -fomit-frame-pointer --sysroot',
                         self.get_recon().ndk_platform,
                         '-DNO_MALLINFO=1',
                         '-I' + SQLiteBuilder(self.get_recon()).get_include_path()])

    def current_build_shared(self):
        return self._build_shared

    def get_default_toolchain_mappings(self):
        """ Overrides the toolchain mappings for a number of things"""
        return { 
            'CC'        : ' '.join([self.get_tool('gcc'), self.get_cflags()]),
            'CXX'       : ' '.join([self.get_tool('g++'), self.get_cflags()]),
            'AR'        : self.get_tool('ar'),
            'RANLIB'    : self.get_tool('ranlib'),
            'STRIP'     : ' '.join([self.get_tool('strip'), '--strip-unneeded']),
            'BLDSHARED' : self.current_build_shared() }

    
    def get_default_flags(self):
        return { 'CFLAGS' : self.get_cflags(),
                 'CXXFLAGS' : self.get_cflags() }

    def autotools_cleanse(self):
        if os.path.exists(os.path.join(self.get_current_source_path(), 'Makefile')):
            process = subprocess.Popen(['make', 'distclean'],
                                       cwd=self.get_current_source_path())
            process.communicate(None)
            if process.returncode != 0:
                raise ValueError("could not perform distclean")
        self.run_autotools_and_make(harness=False, runmakeinstall=False)
        
        pyconfig_path = 'pyconfig.h'
        self.sed_ie('/HAVE_FDATASYNC/ c#undef HAVE_FDATASYNC', pyconfig_path)
        self.sed_ie('/HAVE_KILLPG/ c#undef HAVE_KILLPG', pyconfig_path)
        self.sed_ie('/HAVE_GETHOSTBYNAME_R/ c#undef HAVE_GETHOSTBYNAME_R', pyconfig_path)
        self.sed_ie('/HAVE_DECL_ISFINITE/ c#undef HAVE_DECL_ISFINITE', pyconfig_path)

    def do_build(self):
        """ Starts the build process of Android Python """
        output = self.do_download_cache()
        host_source_path = os.path.join(self.get_current_source_path(), 'host')
        android_source_path = os.path.join(self.get_current_source_path(), 'android')


        self.unpack(output)
        os.rename(os.path.join(self.get_current_source_path(), self.library_name()),
                  host_source_path)

        self.unpack(output)
        os.rename(os.path.join(self.get_current_source_path(), self.library_name()),
                  android_source_path)

        self.push_current_source_path(os.path.join(self.get_current_source_path(), 'host'))
        # Do the host dance
        host_python_prefix = self.get_host_python_prefix()
        host_python_vars = self.get_host_python_vars()

        if os.path.exists(host_python_prefix):
            shutil.rmtree(host_python_prefix)
        
        
        host_build = [['bash', 'configure', '--prefix=' + host_python_prefix],
                      ['make', '-j' + str(multiprocessing.cpu_count())],
                      ['make', 'install']]
        for args in host_build:
            process = subprocess.Popen(args, cwd=self.get_current_source_path())
            process.communicate(None)
            if process.returncode != 0:
                raise ValueError("Could not build host python")

        os.symlink(os.path.join(host_python_prefix, 'bin', 'python'),
                   os.path.join(self.get_current_source_path(), '..', 'pythonhost'))

        self.pop_current_source_path()
        self.push_current_source_path(os.path.join(self.get_current_source_path(), 'android'))
        path = self.get_path()
        our_env = dict(os.environ).copy()
        our_env['PATH'] = os.pathsep.join([self.get_source_path(), path])
        our_env['ARCH'] = 'armeabi'
        our_env['NDKPLATFORM'] = self.get_recon().ndk_platform

        for name in ['Python-2.7.2-xcompile.patch', 
                     'Python-2.7.2-android.patch',
                     'Python-2.7.2-site-relax-include-config.patch',
                     'Python-2.7.2-enable_ipv6.patch',
                     'Python-2.7.2-filesystemdefaultencoding.patch']:
            self.patch(name, strip=1)
        
        
        self.autotools_cleanse()
        
        module = 'libpython2.7.so'
        #our_env['BLDSHARED'] = module_flags['BLDSHARED']
        #our_env['RUNSHARED'] = ' '.join(['LD_LIBRARY_PATH=' + self.get_current_source_path(),
        #                                 'PATH=' + os.pathsep.join([host_python_vars.bin, path])])

        module_make_args = ['make', '-j' + str(multiprocessing.cpu_count()),
                            'HOSTPYTHON=' + host_python_vars.python,
                            'HOSTPGEN=' + host_python_vars.pgen,
                            'CROSS_COMPILE=' + 'arm-eabi-',
                            'CROSS_COMPILE_TARGET=yes',
                            'HOSTARCH=armlinux',
                            'BUILDARCH=x86_64-linux-gnu',
                            'INSTSONAME=libpython2.7.so',
                            module]


        # The sqlite module detection is odd, it replaces the known -I directives, need to have it
        # Create symlink to ../jni/sqlite3
        
        #sqlite3_jni_path = os.path.join(self.get_source_path(), 'jni', 'sqlite3')

        #os.makedirs(os.path.join(self.get_source_path(), 'jni'))

        #os.symlink(SQLiteBuilder(self.get_recon()).get_include_path(),
        #           sqlite3_jni_path)

        process = subprocess.Popen(module_make_args, env=our_env, 
                                   cwd=self.get_current_source_path())
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError(' '.join(["Could not make the module with "] + run))
        
        shutil.copyfile(os.path.join(self.get_current_source_path(), 'libpython2.7.so'),
                        os.path.join(self.get_current_source_path(), '..', 'libpython2.7.so'))
        

        
        self._build_shared = ' '.join([self.get_tool('gcc'), '-shared', 
                                       self.get_cflags(),
                                       '-L' + os.path.join(
                                           self.get_current_source_path(), 
                                           '..'),
                                       '-L' + os.path.join(
                                           SQLiteBuilder(self.get_recon()).get_build_path(),
                                           'lib'),
                                       '-lpython2.7', '-Wl,--no-undefined'])

        self.autotools_cleanse()

        # Get the current architecture
        process = subprocess.Popen(['uname', '-m'], stdout=subprocess.PIPE)
        out, err = process.communicate(None)
        machine = out.strip()
        
        make_args = ['make', '-n', '-j' + str(multiprocessing.cpu_count()), 
                     'HOSTPYTHON=' + host_python_vars.python,
                     'HOSTPGEN=' + host_python_vars.pgen,
                     'CROSS_COMPILE=' + 'arm-eabi-',
                     'CROSS_COMPILE_TARGET=yes',
                     'HOSTARCH=armlinux',
                     'BUILDARCH=' + machine + '-linux-gnu',
                     'INSTSONAME=libpython2.7.so']

        make_install_args = ['make', 'install',
                             'HOSTPYTHON=' + host_python_vars.python,
                             'HOSTPGEN=' + host_python_vars.pgen,
                             'CROSS_COMPILE=' + 'arm-eabi-',
                             'CROSS_COMPILE_TARGET=yes',
                             'HOSTARCH=armlinux',
                             'prefix=' + self.get_build_path(),
                             'BUILDPYTHON=python',
                             'BUILDEXE=host',
                             'INSTSONAME=libpython2.7.so']

        
        for run in [make_args, make_install_args]:
            process = subprocess.Popen(run, env=our_env, 
                                       cwd=self.get_current_source_path())
            process.communicate(None)
            if process.returncode != 0:
                raise ValueError("Could not make the finish")
        
        dest_path = os.path.join(self.get_build_path(), 'lib', 'libpython2.7.so')
        if os.path.exists(dest_path):
            os.remove(dest_path)

        shutil.copyfile(os.path.join(self.get_current_source_path(), 'libpython2.7.so'),
                        dest_path)
        
        print "Python Build Job finished"
        
        self.mark_finished()
