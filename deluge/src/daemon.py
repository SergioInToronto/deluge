#
# daemon.py
#
# Copyright (C) Andrew Resch  2007 <andrewresch@gmail.com> 
# 
# Deluge is free software.
# 
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 2 of the License, or (at your option)
# any later version.
# 
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with deluge.  If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#  In addition, as a special exception, the copyright holders give
#  permission to link the code of portions of this program with the OpenSSL
#  library.
#  You must obey the GNU General Public License in all respects for all of
#  the code used other than OpenSSL. If you modify file(s) with this
#  exception, you may extend this exception to your version of the file(s),
#  but you are not obligated to do so. If you do not wish to do so, delete
#  this exception statement from your version. If you delete this exception
#  statement from all source files in the program, then also delete it here.

# Instantiate the logger
import logging
log = logging.getLogger("deluge")

import Pyro.core
from deluge.core import Core

class Daemon:
  def __init__(self):
    # Instantiate the Manager class
    self.core = Core()
    # Initialize the Pyro core and daemon
    Pyro.core.initServer(banner=0)
    log.info("Pyro server initiliazed..")
    self.daemon = Pyro.core.Daemon()
    # Connect the Manager to the Pyro server
    obj = Pyro.core.ObjBase()
    obj.delegateTo(self.core)
    self.uri = self.daemon.connect(obj, "core")
    log.debug("uri: %s", self.uri)
    
  def start(self):
    # Start the main loop for the pyro daemon
    self.daemon.requestLoop()
    
  def getURI(self):
    # Return the URI for the Pyro server
    return self.uri
