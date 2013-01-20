import qgis_mobility.generator
from qgis_mobility.generator.recipe import Recipe
import os
import argparse

def _current_necessitas(): 
    return qgis_mobility.generator.current_necessitas()

class Recon(object):
    """ Sets the paths for the different components of necessitas we need """
    def __init__(self, necessitas_path):
        """ Initializes the Recon object and attempts to set the necessary tooling """
        self._home_path = os.environ['HOME']
        self._necessitas_path = necessitas_path
        self._ndk_path = os.path.join(self._necessitas_path, "android-ndk")
        self._sdk_path = os.path.join(self._necessitas_path, "android-sdk")
        self._qt_path = os.path.join(self._necessitas_path, "Android", 
                                     "Qt", "482", "armeabi")
        self._qt_tools_path = os.path.join(self._qt_path, "bin")
        self._android_level = 14
        self._ndk_platform = os.path.join(self._ndk_path, 'platforms', 'android-' + 
                                          str(self._android_level), 'arch-arm')
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
        return os.path.join(self.get_home_path(), ".qgis_mobility_generator_cache")

    def get_toolchain_path(self):
        return os.path.join(self.get_cache_path(), 'toolchain')
    
    def get_ndk_platform(self):
        return self._ndk_platform

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

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', action='store', nargs=1,
                        help='Initiates a make routine')
    args = parser.parse_args()
    
    if 'make' in args.action:
        recon = Recon(_current_necessitas())
        Recipe(recon).make()
    else:
        raise ValueError('action provided is not used')
