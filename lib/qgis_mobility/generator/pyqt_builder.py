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

from qgis_mobility.generator.pythonian_builder import PythonianBuilder

import os
import shutil
import subprocess

class PyQtBuilder(PythonianBuilder):
    """ Represents the build strategy for the Python Builder """

    def version(self): return '4.9.6'
    def small_name(self): return 'PyQt'
    def small_version(self): return self.small_name() + '-' + self.version()

    def library_name(self):
        """ Returns the library name of the sip version to build to build """
        return  self.small_name() + '-x11-gpl-' + self.version()
    
    def human_name(self):
        """ Returns the human readable name of the PyQt Builder """
        return 'PyQt Build Process'

    def qt_responder(self):
        f = open(os.path.join(self.get_current_source_path(), 'qt_responder.i'), 'w+')
        f.write('#include <Qt/qglobal.h>\n')
        f.write('QT_VERSION\n')
        f.write('QT_EDITION\n')
        f.close()

    def qtdirs_responder(self, qt_version, qt_edition):
        fname = os.path.join(self.get_current_source_path(), 'qtdirs.out')
        f = open(fname, 'w+')
        f.write(self.get_recon().necessitas_path)
        f.write('\n')
        for post in ['include', 'lib', 'bin', '', 'plugins']:
            f.write(self.make_qt_path(post))
            f.write('\n')
        
        f.write(qt_version)
        f.write('\n')
        f.write(qt_edition)
        f.write('\n')
        f.write("Open Source\n")
        f.write("shared\n")
        f.write("PyQt_NoPrintRangeBug\n")
        f.close()
        return fname

    def make_qt_path(self, post):
        return os.path.join(self.get_recon().qt_path, post)

    def use_preprocessor_determination(self):
        """ Runs the GCC preprocessor and returns a file """
        qt_include_path = self.make_qt_path('include')
        self.qt_responder()
        proc_args = ['cpp', '-x', 'c++', 'qt_responder.i', '-I', qt_include_path, '-o', 'qt_responder.out']
        process = subprocess.Popen(proc_args, cwd=self.get_current_source_path())
        process.communicate(None)
        if process.returncode != 0:
            raise ValueError("Could not run the precompiler for the responder file")
        
        # Read the responder files last two entries
        f = open(os.path.join(self.get_current_source_path(), 'qt_responder.out'))
        lines = f.readlines()
        f.close()
        
        length = len(lines)
        qt_version = str(int(lines[length - 2], 16))
        qt_edition = str(eval(lines[length - 1]))

        print "QT VERSION:", qt_version, "QT_EDITION:", qt_edition
        return qt_version, qt_edition


    def patch_all_files(self):
        self.patch('configure_py.patch', strip=1)
        self.patch('disable_X11.patch', strip=1)
        self.patch('hardcode_Q_PID.patch', strip=1)
        self.patch('hardcode_HANDLE.patch', strip=1)
        self.patch('hardcode_WId.patch', strip=1)
        self.patch('hardcode_qreal.patch', strip=1)
        self.patch('disable_QSound.patch', strip=1)
        self.patch('disable_QSound_qapplication.patch', strip=1)
        self.patch('disable_KeyboardModifiers_qguiapplication.patch', strip=1)
        self.patch('disable_KeyboardModifiers_qapplication.patch', strip=1)

    def do_build(self):
        """ Starts the build process of Android PyQt """


        output = self.wget('http://sourceforge.net/projects/pyqt/files/PyQt4/' + 
                           self.small_version() + '/' + self.library_name() + '.tar.gz/download')

        self.unpack(output)

        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.run_py_configure_and_make(options=['--confirm-license'], host=True)

        self.pop_current_source_path()
        shutil.rmtree(os.path.join(self.get_source_path(), self.library_name()))

        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))

        qt_version, qt_edition = self.use_preprocessor_determination()
        fname = self.qtdirs_responder(qt_version, qt_edition)

        self.patch_all_files()

        options=['--confirm-license',
                 '-eQtGui',
                 '-eQtCore', '-eQtDeclarative', '-eQtScript', '-eQtNetwork', 
                 '-eQtMultimedia', '-eQtScriptTools', '-eQtSql', '-eQtSvg', '-eQtTest',
                 '-eQtXml', '-eQtXmlPatterns',
                 'INCDIR+=' + self.make_qt_path(os.path.join('mkspecs', 'android-g++'))]

        mappings = self.get_default_toolchain_mappings()
        flags = self.get_default_flags()
        sysroot = os.path.join(self.get_recon().get_toolchain_path(), 'sysroot')
        options.extend(['CC=' + mappings['CC'],
                        'CFLAGS+=--sysroot=' + sysroot + ' -mthumb',
                        'CXXFLAGS+= -fpermissive --sysroot=' + sysroot + ' -mthumb',
                        'CXX=' + mappings['CXX'],
                        'LINK=' + mappings['CC'],
                        'LFLAGS+=' + flags['LDFLAGS']  + ' --sysroot=' + sysroot +
                        ' -L' + self.get_output_library_path() + ' -lpython2.7'])

        self.run_py_configure(options)
        
        for main_path in ['qpy', '.']:
            qpy_path = os.path.join(self.get_current_source_path(), main_path)
            directory = os.listdir(qpy_path)
            for path in directory:
                makefile = os.path.join(qpy_path, path, 'Makefile')
                if os.path.exists(makefile):
                    sedstring = 's|INCPATH[^=]*=|& -I' + self.get_include_path() + ' |'
                    self.sed_i(sedstring, makefile)
                    sedstring = 's|CPPFLAGS[^=]*=|& -I' + self.get_include_path() + ' |'
                    self.sed_i(sedstring, makefile)
                    sedstring = 's|LIBS[^=]*=|& -L' + self.get_output_library_path() + ' -lpython2.7 -llog -lz -lm -ldl -lc |'
                    self.sed_i(sedstring, makefile)
                    sedstring = 's|copy /y|cp -f|'
                    self.sed_i(sedstring, makefile)
                    sedstring = 's/\@if not exist[^|]*[|][|] mkdir/mkdir -p/'
                    self.sed_ie(sedstring, makefile)

        main_makefile = os.path.join(self.get_current_source_path(), 'Makefile')
        sedstring = 's/@(cd pyrcc.*$//'
        self.sed_i(sedstring, main_makefile)
        sedstring = 's|copy /y|cp -f|'
        self.sed_i(sedstring, main_makefile)
        sedstring = 's/\@if not exist[^|]*[|][|] mkdir/mkdir -p/'                    
        self.sed_ie(sedstring, main_makefile)
        
        self.run_make()
        self.run_make(install=True, makeopts=['INSTALL_ROOT=' + self.get_build_path()])

        self.mark_finished()
