import os, sys, inspect

# Get the current path
current_path = os.path.realpath(os.path.dirname(
    inspect.getfile(inspect.currentframe())))

# Create the library path from this
lib_path = os.path.abspath(os.path.join(current_path, '..', 'lib'))
cache_path = os.path.abspath(os.environ['CACHE_PATH'])

sys.path.append(lib_path)

from qgis_mobility.generator.main import run

run(cache_path)
