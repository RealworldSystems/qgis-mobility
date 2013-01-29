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
