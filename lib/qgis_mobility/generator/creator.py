import os

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
        # native/         - Contains subfolders which can be compiled 
        #                   using specific autoconf routines into additional
        #                   shared objects. Linking is done in alphabetical
        #                   order (important for dependencies)
        
        host_config = os.path.join(working_folder, 'config', 'host')
        target_config = os.path.join(working_folder, 'config', 'target')
        app = os.path.join(working_folder, 'app')
        native = os.path.join(working_folder, 'native')

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
