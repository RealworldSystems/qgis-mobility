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

import os       # Used for checking existance of the cache path
import urllib2  # Used for downloading the zip file pointed to by the url
import tempfile # Used to generate a temporary file for the contents of the zip
                # file aforementioned.
import tarfile  # For extracting the archive downloaded from the HTTP channel

from sys import stdout      # The stdout is used to directly write progress 
                            # dots on the terminal
class Download(object):
    """
    The download is responsible for downloading existing prebuilt caches from
    a given network resource. This severely limits the time needed to start
    using the framework.
    """
    
    def __init__(self, recon):
        """
        Initializes self with the recon object
        """
        self._recon = recon
        
    def url(self, url, cache_path):
        """
        Downloads the contents pointed to by the url from the server in zipped
        format, and puts them into the cache directory mentioned by path.
        
        If the cache directory is already available, this operation will halt
        """        
        # If the cache path already exists, the process halts, otherwise,
        # the download starts into a temporary file and extraction commences.
        if os.path.exists(cache_path):
            raise ValueError("Cache path [" + cache_path + "] already exists")
        else:
            # Create a temporary file to be able to store the data downloaded
            # from the URL
            tmp_file = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
            print "Opening URL: ", url
            print "Output to: ", tmp_file.name
            response = urllib2.urlopen(url)
            with tmp_file as tgz:
                print "Transferring chunks of 1 MiB"
                counter = 0
                while True:
                    read = response.read(1024 * 1024)
                    tgz.write(read)
                    stdout.write('.')
                    stdout.flush()
                    counter += 1
                    if counter % 64 == 0: print " ", counter, " MiB"
                    if len(read) == 0: 
                        print " ", counter, " MiB"
                        tgz.flush()
                        break
            
                # Reset the file read position of the temporary file containing
                # the tgz data earlier stored
                tgz.seek(0)

                # Open the tmp_file object as a TgzFile
                print "Extracting to ", cache_path
                zf = tarfile.open(name=None, mode="r", fileobj=tgz)
                counter = 0
                zf.extractall(cache_path)
