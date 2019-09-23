# This file is a part of xboa
# 
# xboa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xboa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xboa in the doc folder.  If not, see 
# <http://www.gnu.org/licenses/>.

"""
Import ThisNodeProcess directly from the multitrack module
"""

import os
import pickle
import subprocess

from ._tracking_process import TrackingProcess

# Could potentially use multiprocessing with pickle used to do in memory
# messaging (rather than relying on disk writes to handle messaging, which can
# be slow and can lead to funny errors).
class ThisNodeProcess(TrackingProcess):
    """
    TrackingProcess that can do multiprocessing on this node (i.e. not 
    distributed across a cluster)

    Submits jobs using subprocess module
    """
    def __init__(self, tracking):
        """
        Initialise the Process
        - tracking: a picklable object of type xboa.tracking.TrackingBase
        - hit_list: a list of objects of type xboa.hit.Hit
        """
        TrackingProcess.__init__(self, tracking)
        self.proc = None

    def start(self):
        """
        Start the tracking by opening a subprocess and calling run()
        """
        if self.is_alive():
            raise RuntimeError("Attempt to start a process that is already "+\
                               "started")
        self.proc = subprocess.Popen([self.run_executable,
                                      "--out-dir", self.out_dir])
        self.pid = self.proc.pid

    def is_alive(self):
        """
        Returns true if the process is currently running
        """
        if self.proc == None:
            return False
        self.exitcode = self.proc.poll()
        return self.exitcode == None
  
    def terminate(self, timeout = None):
        """
        Terminate the process (soft exit)
        """
        if self.proc == None:
            raise RuntimeError("Attempt to terminate a process before it has "+\
                               "been started")
        self.proc.terminate()
        self.join(timeout)
        self.exitcode = self.proc.poll()

    def kill(self, timeout = None):
        """
        Kill the process (hard exit)
        """
        if self.proc == None:
            raise RuntimeError("Attempt to terminate a process before it has "+\
                               "been started")
        self.proc.kill()
        self.join(timeout)
        self.exitcode = self.proc.poll()

