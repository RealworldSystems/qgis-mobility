#
# This is the initialization routine for the generator
#

import os, exceptions

# Autodiscovery of Necessitas for Android

_necessitas = None

def _necessitas_guess_paths():
    test_paths = []
    if 'NECESSITAS' in os.environ:
        test_paths.extend([os.environ['NECESSITAS']])
    if 'HOME' in os.environ:
        home_path = os.environ['HOME']
        test_paths.extend([os.path.join(home_path, 'necessitas')])
        test_paths.extend([os.path.join(home_path, 'NecessitasQtSDK')])
    test_paths.extend([os.path.join('/', 'opt', 'necessitas')])
    test_paths.extend([os.path.join('/', 'opt', 'NecessitasQtSDK')])
    return test_paths

def current_necessitas():
    global _necessitas
    if _necessitas == None:
        for path in _necessitas_guess_paths():
            if os.path.exists(path):
                _necessitas = path
                return _necessitas # early return
        err_str = "Automatic recognition of Necessitas failed "
        err_str += "please install it or set the "
        err_str += "'NECESSITAS' environment variable"
        raise exceptions.EnvironmentError(err_str)
    else:
        return _necessitas
