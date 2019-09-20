#!/usr/bin/env python

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
Utility for hanling xboa tracking distributed processing
"""

import sys
import argparse
import os
import pickle

from xboa.tracking.tracking_process import TrackingProcess

def parse_args():
    """Parse the input arguments"""
    parser = argparse.ArgumentParser(description="Utility for handling xboa "+\
                                            "tracking distributed processing.")
    parser.add_argument('--out-dir', dest='out_dir', type=str,
                 help='Directory where the pickled tracking process is stored')
    args = parser.parse_args()
    return args

def main():
    """Run the TrackingProcess"""
    args = parse_args()
    out_dir = args.out_dir 
    fin = open(os.path.join(out_dir, TrackingProcess.pickle_jar))
    tracking_process = pickle.load(fin)
    # clear any old data; always want to get new data
    if os.path.exists(TrackingProcess.pickle_sandwich):
        os.remove(TrackingProcess.pickle_sandwich)
    # run the data and dump the output
    hits = tracking_process.run()
    fout = open(os.path.join(out_dir, TrackingProcess.pickle_sandwich), "w")
    pickle.dump(hits, fout)

if __name__ == "__main__":
    main()
