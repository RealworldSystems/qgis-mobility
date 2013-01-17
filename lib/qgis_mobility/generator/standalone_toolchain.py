import subprocess
import os
import shutil

class StandaloneToolchain(object):

    def __init__(self, recon):
        self._recon = recon
    
    def make(self):
        if not os.path.exists(self._recon.get_toolchain_path()):
            standalone_chain = os.path.join(
                self._recon.ndk_path,
                'build', 'tools', 'make-standalone-toolchain.sh')
            os.makedirs(self._recon.get_toolchain_path())
            args = ['bash',
                    standalone_chain, 
                    '--platform=android-' + str(self._recon.android_level), 
                    '--install-dir=' + self._recon.get_toolchain_path()]
            print args
            process = subprocess.Popen(args)
            process.communicate(None)
            if not process.returncode == 0:
                shutil.rmtree(self._recon.get_toolchain_path())
                raise ValueError("Toolchain didn't compile successfully")
