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
\namespace xboa::hit::factory

The hit factory module defines a number of factory classes used for generating 
hit objects

Implemented within this module:
\li \link xboa::hit::factory::_maus_root_hit_factory::MausRootHitFactory
  MausRootHitFactory \endlink: factory that reads data from a MAUS ROOT file.
\li \link xboa::hit::factory::_maus_json_hit_factory::MausJsonHitFactory
  MausJsonHitFactory \endlink: factory that reads data from a MAUS JSON file.
\li \link xboa::hit::factory::_builtin_hit_factory::BuiltinHitFactory
  BuiltinHitFactory \endlink: factory that reads data from various "built-in"
  types, e.g. ICOOL, G4BL, etc.
\li \link xboa::hit::factory::_user_hit_factory::UserHitFactory
  UserHitFactory \endlink: Class for reading in line-by-line data based on a
  user-specified format.
\li \link xboa::hit::factory::_opal_hit_factory::OpalHitFactory
  OpalHitFactory \endlink: Class for reading in data from OPAL tracking code.
\li \link xboa::hit::factory::_line_factory_base::LineFactoryBase
  LineFactoryBase \endlink: Base class for factories that read in line-by-line.
\li \link xboa::hit::factory::_hit_factory_base::HitFactoryBase
  HitFactoryBase \endlink: Base class for all other hit factory classes.
"""

from xboa.hit.factory._hit_factory_base import HitFactoryBase
from xboa.hit.factory._line_factory_base import LineFactoryBase
from xboa.hit.factory._maus_root_hit_factory import MausRootHitFactory
from xboa.hit.factory._maus_root_recon_hit_factory import MausRootReconHitFactory
from xboa.hit.factory._maus_json_hit_factory import MausJsonHitFactory
from xboa.hit.factory._builtin_hit_factory import BuiltinHitFactory
from xboa.hit.factory._user_hit_factory import UserHitFactory
from xboa.hit.factory._opal_hit_factory import OpalHitFactory

all = ["HitFactoryBase", "LineFactoryBase", "UserHitFactory",
       "BuiltinHitFactory", "OpalHitFactory", "MausJsonHitFactory"]
