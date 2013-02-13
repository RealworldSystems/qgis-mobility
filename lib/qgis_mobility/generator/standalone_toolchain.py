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

import subprocess
import os
import shutil

class StandaloneToolchain(object):

    def __init__(self, recon):
        self._recon = recon

    def clean(self): pass   
 
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
