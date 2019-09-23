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
class BSubProcess(TrackingProcess):
    """
    TrackingProcess that can do multiprocessing on this node (i.e. not 
    distributed across a cluster)

    Submits jobs using subprocess module
    """
    def __init__(self, tracking, queue, job_time):
        """
        Initialise the Process
        - tracking: a picklable object of type xboa.tracking.TrackingBase
        - hit_list: a list of objects of type xboa.hit.Hit
        """
        if not self.has_bsub():
            raise ImportError("bsub not available on this machine")
        TrackingProcess.__init__(self, tracking, self.scratch_dir)
        self.queue = queue
        self.job_time = job_time
        out_path = os.path.join(self.out_dir, self.pickle_jar)
        process_out = open(out_path, "w")
        pickle.dump(self, process_out)
        process_out.close()

    def start(self):
        """
        Start the tracking by opening a subprocess and calling run()
        """
        if self.is_alive():
            raise RuntimeError("Attempt to start a process that is already "+\
                               "started")
        log = os.path.join(self.out_dir, self.std_out)
        err = os.path.join(self.out_dir, self.std_err)
        proc_output = subprocess.check_output(
                                     ['bsub',
                                      '-q', self.queue,
                                      '-W', self.job_time,
                                      '-o', log,
                                      '-e', err,
                                      self.run_executable,
                                      "--out-dir", self.out_dir])
        start_index = proc_output.find("<")+1
        end_index = proc_output.find(">")
        self.pid = int(proc_output[start_index:end_index])

    def is_alive(self):
        """
        Returns true if the process is currently running
        """
        if self.pid == None:
            return False
        proc_output = subprocess.check_output(['bjobs', '-l', str(self.pid)])
        status = self._get_substr(proc_output, 'Status <', '>')
        if status in ["PEND", "RUN", "WAIT"]:
            return True
        self.exitcode = 0
        try:
            self.exitcode = self._get_substr(proc_output, 'exit code ', '.')
        except ValueError:
            pass # no report if exit code was 0
        return False
  
    def terminate(self, timeout = None):
        """
        Terminate the process (always a hard exit with bsub)
        """
        self.kill(timeout)

    def kill(self, timeout = None):
        """
        Kill the process (hard exit)
        """
        if self.pid == None:
            raise(RuntimeError("Attempt to kill process before it has started"))
        subprocess.call(['bkill', str(self.pid)])

    @classmethod
    def _get_substr(cls, a_string, start_key, end_key):
        """Get a substring bounded, but not including, start_key and end_key"""
        start_index = a_string.find(start_key)
        if start_index < 0:
            raise ValueError("start_key "+start_key+" could not be found in "+\
                             "string "+a_string)
        a_string = a_string[start_index+len(start_key):]
        end_index = a_string.find(end_key)
        if end_index < 0:
            raise ValueError("end_key "+end_key+" could not be found in "+\
                             "string "+a_string)
        return a_string[:end_index]

    @classmethod
    def has_bsub(cls):
        try:
            subprocess.call(['bsub', '-h'],
                            stdout = cls.dump_handle,
                            stderr = subprocess.STDOUT)
            return True
        except OSError:
            return False

    dump_handle = open("/dev/null", "w")
    scratch_dir = "/work/scratch/tracking"
    std_out = "job.out"
    std_err = "job.err"
