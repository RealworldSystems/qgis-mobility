from qgis_mobility.generator.builder import Builder
import os
import shutil

class BZip2Builder(Builder):
    """ Represents the build strategy for the BZip2 library """
    
    def library_name(self):
        """ Returns the library name of the BZip2 library """
        return "bzip2-1.0.6"
    
    def human_name(self):
        """ Returns the human readable name of the BZip2Builder """
        return "BZip2 Build Process"

    def get_default_flags(self):
        return { 'LDFLAGS' : Builder.get_default_flags(self)['LDFLAGS'],
                 'CC'      : self.get_default_toolchain_mappings()['CC'] + ' ' + 
                             Builder.get_default_flags(self)['CFLAGS'] }        

    def do_build(self):
        output = self.wget("http://www.bzip.org/1.0.6/bzip2-1.0.6.tar.gz")
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), "bzip2-1.0.6"))
        self.patch("bzip2.patch")
        self.run_make(path=self.get_current_source_path(),
                      makefile="Makefile-libbz2_so")
        shutil.copyfile(os.path.join(self.get_current_source_path(), 'libbz2.so'),
                        os.path.join(self.get_build_path(), "libbz2.so"))
        shutil.copyfile(os.path.join(self.get_current_source_path(), 'bzlib.h'),
                        os.path.join(self.get_include_path(), "bzlib.h"))
        self.mark_finished()
