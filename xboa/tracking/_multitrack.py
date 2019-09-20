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
\namespace xboa::tracking::_multitrack

Should be imported directly from the xboa::tracking::multitrack namespace
"""

import copy
from xboa.tracking.tracking_process import TrackingProcess
from xboa.tracking import TrackingBase

# manages a worker pool
class MultiTrack(TrackingBase):
    """
    Defines methods to distribute a tracking job across several cores
    
    Idea is to define a tracking job as normal; but then wrap it in this
    MultiTrack class which handles the distribution across nodes
    """
    def __init__(self, n_processes, tracking_process):
        """
        Initialise the MultiTrack object
        - tracking: the wrapped Tracking object
        - n_processes: number of processes to run
        - tracking_process_type: type of TrackingProcess to use - should be a
          type object, not instantiated; MultiTrack will instantiate a
          TrackingProcess for each of n_processes
        """
        TrackingBase.__init__(self)
        self.tracking_job = tracking_process
        self.n_processes = n_processes
        self.job_list = []
        self.last = []

    def track_many_async(self, hit_list):
        """
        Track the hits in hit_list
        - hit_list: list of hits to be tracked
        Returns a list of (maybe still processing) jobs to the caller

        track_many_async splits the hit_list up into chunks, and starts one
        process for each chunk.

        Following the method call, track_many_async returns ownership of the
        process to the caller, even though the tracking processes may not have
        finished. Use TrackingProcess.is_alive() to check for the status of
        each process and MultiTrack.get_return_value() to get the resultant
        hits.
        """
        self.job_list = []
        self.last = []
        n_hits = len(hit_list)
        n_hits_per_process = n_hits/int(self.n_processes)
        remainder = n_hits % int(self.n_processes)
        
        for i in range(self.n_processes):
            if remainder > 0:
                this_hit_list = hit_list[0:n_hits_per_process+1]
                hit_list = hit_list[n_hits_per_process+1:]
                remainder -= 1
            else:
                this_hit_list = hit_list[0:n_hits_per_process]
                hit_list = hit_list[n_hits_per_process:]
            next_job = copy.deepcopy(self.tracking_job)
            next_job.new_out_dir()
            next_job.set_hit_list(this_hit_list)
            self.job_list.append(next_job)
            next_job.start()
        return self.job_list

    def track_one(self, a_hit):
        """
        Just call track_one on the hit
        """
        self.tracking.track_one(a_hit)

    def track_many(self, hit_list):
        """
        Track the hits in hit_list
        - hit_list: list of hits to be tracked

        Calls track_many_async and then polls returning jobs until they have all
        finished.

        Returns the result of tracking.track_many, i.e. a list of list of hits,
        one list of hits for each process.
        """
        self.track_many_async(hit_list)
        tmp_job_list = [job for job in self.job_list]
        while len(tmp_job_list) > 0:
            very_tmp_job_list = []
            for job in tmp_job_list:
                if job.is_alive():
                    very_tmp_job_list.append(job)
                else:
                    print "Process", job.pid, "finished with exitcode", 
                    print job.exitcode
            tmp_job_list = very_tmp_job_list
        return self.get_return_value()

    def get_return_value(self):
        """
        Return a list of list of hits. If all TrackingProcesses have finished,
        one list for each initial hit is returned. If some TrackingProcesses are
        still running, those results will not be included in the return value. 
        """
        self.last = []
        for job in self.job_list:
            try:
                self.last += job.get_return_value() 
            except RuntimeError: # the job wasn't finished?
                pass
        return self.last
