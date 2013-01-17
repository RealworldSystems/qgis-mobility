from qgis_mobility.generator.builder import Builder
import distutils.dir_util
import os

class SQLiteBuilder(Builder):
    """ Represents the build strategy for the SQLite library """

    def library_name(self):
        """ Returns the library name of the SQLite library """
        return 'sqlite-autoconf-3070400'
    
    def human_name(self):
        """ Returns the human readable name of the FreeXLBuilder """
        return 'SQLite Build Process'

    def salt_flags(self, flags):
        flags = Builder.salt_flags(self, flags)
        self.insert_config_path_flag(flags)
        return flags

    def do_build(self):
        """ Runs the actual build process """
        output = self.wget('http://www.sqlite.org/' + self.library_name() + '.tar.gz')
        self.unpack(output)
        self.push_current_source_path(os.path.join(self.get_source_path(), self.library_name()))
        self.fix_config_sub_and_guess()
        self.patch('sqlite.patch', strip=1)
        self.run_autotools_and_make()        
        distutils.dir_util.copy_tree(os.path.join(self.get_build_path(), 'include'),
                                     os.path.join(self.get_include_path()))
        self.mark_finished()
