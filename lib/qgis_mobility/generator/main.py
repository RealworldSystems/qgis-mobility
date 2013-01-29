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

import qgis_mobility.generator
from qgis_mobility.generator.recipe import Recipe
from shutil import rmtree
import os
import argparse
import textwrap
import inspect
import re

def _current_necessitas(): 
    return qgis_mobility.generator.current_necessitas()

class Recon(object):
    """ Sets the paths for the different components of necessitas we need """
    def __init__(self, necessitas_path, cache_path):
        """ Initializes the Recon object and attempts to set the necessary tooling """
        self._home_path = os.environ['HOME']
        self._necessitas_path = necessitas_path
        self._ndk_path = os.path.join(self._necessitas_path, "android-ndk")
        self._sdk_path = os.path.join(self._necessitas_path, "android-sdk")
        self._qt_path = os.path.join(self._necessitas_path, "Android", 
                                     "Qt", "482", "armeabi")
        self._qt_tools_path = os.path.join(self._qt_path, "bin")
        self._qt_version_triplet = [4,8,2]
        self._android_level = 14
        self._ndk_platform = os.path.join(self._ndk_path, 'platforms', 'android-' + 
                                          str(self._android_level), 'arch-arm')
        self._cache_path = cache_path
        self.verify()
    
    def get_necessitas_path(self): 
        """ Return the Necessitas path """
        return self._necessitas_path
    
    def get_ndk_path(self):
        """ Return the NDK path """
        return self._ndk_path
    
    def get_sdk_path(self):
        """ Return the SDK path """
        return self._sdk_path
    
    def get_qt_tools_path(self):
        """ Return the QT Tools path """
        return self._qt_tools_path

    def get_qt_path(self):
        """ Return the QT path """
        return self._qt_path
    
    def get_home_path(self):
        """ Return the home path """
        return self._home_path
    
    def get_android_level(self):
        """ Returns the level of the android target to use """
        return self._android_level
    
    def get_cache_path(self):
        return self._cache_path

    def get_toolchain_path(self):
        return os.path.join(self.get_cache_path(), 'toolchain')
    
    def get_ndk_platform(self):
        return self._ndk_platform

    def get_qt_version_triplet(self):
        return self._qt_version_triplet

    def get_script_path(self):
        current_path = os.path.realpath(os.path.dirname(
            inspect.getfile(inspect.currentframe())))
        
        return os.path.join(current_path, '..', '..', '..', 'script')


    necessitas_path = property(get_necessitas_path, None, None, "The necessitas path")
    ndk_path        = property(get_ndk_path,        None, None, "The Android NDK path")
    sdk_path        = property(get_sdk_path,        None, None, "The Android SDK path")
    qt_tools_path   = property(get_qt_tools_path,   None, None, "The Android QT Tools path")
    qt_path         = property(get_qt_path,         None, None, "The Android QT path")
    android_level   = property(get_android_level,   None, None, "The Android Level to use")
    ndk_platform    = property(get_ndk_platform,    None, None, "The NDK platform to use")

    def paths(self):
        """ Returns a map of the defined paths """
        return {'necessitas_path' : self.necessitas_path,
                'ndk_path'        : self.ndk_path,
                'sdk_path'        : self.sdk_path,
                'qt_tools_path'   : self.qt_tools_path}
    
    def __str__(self):
        return object.__str__(self) + " " + self.paths().__str__()
    
    def verify(self):
        for path in self.paths().values():
            if not os.path.exists(path):
                raise EnvironmentError("Could not determine path: " + path)


def __purge_cache_path(recon):
    """ Purges the source path but keeps build targets """
    rmtree(os.path.join(recon.get_cache_path(), 'source'))

def __distclean(recon):
    """ Removes everything """
    
    # This removes the whole tree of build fragments. To do this,
    # it needs to destroy hostpython (which is where this file
    # is running). Therefore, a shell file is executed replacing
    # this process
    script_path = recon.get_script_path()
    distclean = os.path.join(script_path, "distclean.sh")
    os.execlp(distclean, distclean)
    

def __workout_targets(receiver, prefix="", start={}):
    for item in dir(receiver):
        if len(item) < 1 or item[0:1] != '_':
            attr = getattr(receiver, item)
            if type(attr).__name__ == 'instancemethod':
                start[prefix + item] = [receiver, attr]
            elif isinstance(attr, object):
                __workout_targets(attr, prefix + item  + ':', start)
    
    return start

def __parsecommand(expression, recipe):
    """
    Parses the command range as given in expression
    """
    
    targets = __workout_targets(recipe)
    if 'purgecache' == expression:
        __purge_cache_path(recon)
    elif 'distclean' == expression:
        __distclean(recon)
    else:
        receiver, attr = targets[expression]
        attr()
        

def run(cache_path):

    recon = Recon(_current_necessitas(), cache_path)
    recipe = Recipe(recon)

    epilog=textwrap.dedent('''\
    The action should be any of the following
    ''')
    epilog += "  - purgecache\n  - distclean\n  - "
    epilog += "\n  - ".join(sorted(__workout_targets(recipe).keys()))
    
    describe = textwrap.dedent('''\
    script arguments:
      -c <PATH>   Instructs the bash script to initiate
                  into the given cache path
    ''')
    usage = "qgsmg [-c <PATH>] [-h] action"
    parser = argparse.ArgumentParser(
        usage=usage,
        epilog=epilog,
        description=describe, prog='qgsmg',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('action', action='store', nargs=1,
                        help='Initiates a make routine')
    args = parser.parse_args()
    
    __parsecommand(args.action[0], recipe)
    
