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

import os
import tempfile
import pickle
import time
import stat

class TrackingProcess(object):
    """
    Wraps a call to a class of type TrackingBase in a subprocess, for
    parallelisation

    Messaging between the calling process and the child process is handled by
    pickle, so implicitly assumes that function calls are picklable. See the
    pickle module for more details.

    The API is intended to look similar to multiprocessing Process    
    
    So the general route for the job submission is to
    1. write the inputs to disk
    2. make a subprocess that reads in the inputs, does tracking, writes to disk
    3. read the outputs from disk, return to the user
    Inefficient in that it requires lots of disk mangling and process mangling;
    but it is generalisable.
    """
    def __init__(self, tracking, tmp_dir = "/tmp/tracking"):
        """
        Initialise the TrackingProcess
        - tracking: an object of type xboa.tracking.TrackingBase that will track
          hits. The tracking object must be picklable.
        - hit_list: a list of hits, used for tracking
        """
        self.pid = None
        self.exitcode = None
        self.return_value = None
        self.hit_list = None
        self.tracking = tracking
        self.tmp_dir = tmp_dir
        self.out_dir = self.new_out_dir()

    def new_out_dir(self):
        """
        Get a new output dir
        """
        try:
           os.makedirs(self.tmp_dir)
        except OSError:
           pass # maybe the directory already exists? Let's keep going
        self.out_dir = tempfile.mkdtemp(dir = self.tmp_dir)
        return self.out_dir

    def set_hit_list(self, hit_list):
        """
        Set the hit list over which the TrackingProcess should run
        """
        self.hit_list = hit_list
        process_out = open(os.path.join(self.out_dir, self.pickle_jar), "w")
        pickle.dump(self, process_out)

    def start(self):
        """
        Start the tracking process
        """
        raise NotImplementedError("A virtual method was called on "+\
                           "TrackingProcess base class that was not overloaded")

    def is_alive(self):
        """
        Returns True if the process is still running; returns False if the
        process has not started or has completed.
        """
        raise NotImplementedError("A virtual method was called on "+\
                           "TrackingProcess base class that was not overloaded")

    def terminate(self, timeout = None):
        """
        Terminate the process; wait until the process has died before returning
        - timeout: lock the process until timeout seconds expires or the process
                   terminates
        """
        raise NotImplementedError("A virtual method was called on "+\
                           "TrackingProcess base class that was not overloaded")

    def kill(self, timeout = None):
        """
        Kill the process; wait until the process has died before returning
        - timeout: lock the process until timeout seconds expires or the process
                   terminates
        """
        raise NotImplementedError("A virtual method was called on "+\
                           "TrackingProcess base class that was not overloaded")

    def run(self):
        """
        Run the tracking in the calling process
        """
        return self.tracking.track_many(self.hit_list)

    def join(self, timeout = None):
        """
        Block the calling process until the TrackingProcess finishes or timeout
        seconds pass
        - timeout: number of seconds to wait before returning to the calling
          process
        """
        start_time = time.time()
        delta_t = -1
        while self.is_alive() and (timeout == None or delta_t < timeout):
            delta_t = time.time()-start_time

    def get_return_value(self):
        """
        Fill the return value, if the current job has finished running

        raises a RuntimeError if the current job is still running
        """
        if self.is_alive():
            raise RuntimeError("Cannot get return value while the job is "+\
                               "running")
        if self.exitcode == None:
            raise RuntimeError("Call tracking_process.start() before trying "+\
                               "get the return value")
        return_path = os.path.join(self.out_dir, self.pickle_sandwich)
        if not os.path.exists(return_path):
            raise RuntimeError("The TrackingProcess finished without leaving "+\
                               "a return value")
        fin = open(return_path)
        self.return_value = pickle.load(fin)
        return self.return_value

    @classmethod
    def new_from_pickle(cls, pickle_dir):
        """
        Instantiate a TrackingProcess from pickle directory
        - pickle_dir: directory where pickled data is stored.
        """
        fin = open(os.path.join(pickle_dir, cls.pickle_jar), "r")
        process = pickle.load(fin)
        return process

    # I know these names are inscrutable - but I couldn't resist. I like
    # pickle :/
    pickle_jar = "tracking_process.pickle"
    pickle_sandwich = "hits_out.pickle"
    run_executable = "xboa_tracking_process.py"

