/**
\mainpage XBOA: A multiparticle tracking postprocessor library for accelerator physicsists
You've got your favourite tracking code running, what now? This package is a post-processor for taking beam data to calculate beam emittance, Twiss functions, etc. Also includes bindings to plotting packages ROOT and matplotlib, and a whole lot more!

\par Download and Installation
You can download the latest version from the code repository hosted on <a href="http://sourceforge.net/projects/xboa/">sourceforge</a>. This is mirrored on <a href="http://launchpad.net/xboa">launchpad</a>.

\par
Installation instructions are in the README file, but you probably have to do something like:

\par
\code
tar -xzf xboa-<version>.tar.gz
cd xboa-<version>
python setup.py build
sudo python setup.py install
\endcode

\par
At the moment only Linux is supported, but windows support would be pretty easy to implement if there was demand.

\par Running
When doing any physics analysis beyond the most basic, one really wants to be able to manipulate the analysis in various ways. For any detailed analysis, physicists will want to make cuts and calculate different variables in different ways. For this reason x-boa really provides just a library of physics analysis functions. Examples of how to use it are provided, but once physicists get going they can really push the analysis however they like.

\par Examples
There are several example scripts in the xboa/examples directory that are good to start with:
\li \link xboa::examples::Example_1 xboa/examples/Example_1.py \endlink Load and access particle data
\li \link xboa::examples::Example_2 xboa/examples/Example_2.py \endlink Load data and make some plots
\li \link xboa::examples::Example_3 xboa/examples/Example_3.py \endlink Make some cuts before plotting
\li \link xboa::examples::Example_4 xboa/examples/Example_4.py \endlink Apply a transformation before plotting
\li \link xboa::examples::closed_orbit xboa/examples/closed_orbit.py \endlink Find a closed orbit

\par
They take you through the steps required to load particle tracking data, access it, make plots and manipulate it in various ways.  There is also a script that _almost_ clones the functionality of the ecalc9f code developed by Greg Penn and Rick Fernow, XBOA9f.py

\par Modules
Three modules are available
\li \link xboa::common::_common common \endlink contains some useful general purpose routines including general plotting routines
\li \link xboa::hit hit \endlink module provides the \link xboa::hit::_hit::Hit Hit \endlink class and other interfaces to individual monte carlo Hits (e.g. particles traversing some output plane)
\li \link xboa::bunch bunch \endlink module provides the \link xboa::bunch::_bunch::Bunch Bunch \endlink class and other interfaces to operations on groups of particles (e.g. moment and Twiss parameter calculation)
\li \link xboa::tracking tracking \endlink provides an interface to tracking for use by the algorithms module
\li \link xboa::algorithms algorithms \endlink provides a library many for common accelerator physics functions such as finding closed orbits 

Additionally, there is some C code hiding "under the bonnet"

\authors Chris Rogers chris.rogers@stfc.ac.uk
*/
