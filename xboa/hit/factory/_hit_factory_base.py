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

import xboa.hit

class HitFactoryBase(object):
    """
    Base factory class for making hits
    """
    def __init__(self):
        """
        Initialise the base class
        """
        pass

    def make_hit(self):
        """
        Generate a new hit
        """
        raise NotImplementedError("make_hit not implemented")

    def hit_generator(self):
        try:
            print("gen in")
            yield self.make_hit()
            print("gen out")
        except (EOFError, xboa.hit.BadEventError):
            self.new_spill()
            try:
                yield self.make_hit()
            except (EOFError, xboa.hit.BadEventError):
                raise StopIteration("Finished")
        except StopIteration:
            raise

    def new_spill(self):
        """
        Load the next spill from the file handle

        For files that have data bundled into spills (i.e. MAUS format), this
        enables user to load the next spill. Otherwise it is a no-op.
        """
        pass

    @classmethod
    def bad_pid(cls, pid):
        if pid not in cls.bad_pids:
            print("Failed to parse pid", pid)
            cls.bad_pids.append(pid)

    bad_pids = []

