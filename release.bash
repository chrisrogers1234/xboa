#!/usr/bin/bash

# test_install.tcsh - tcsh script to build and install xboa
# run all tests and then run all examples. If full_build is
# set to 'yes' will push the packaged version to a target 
# directory. Otherwise just installs it locally.

run_unit_tests='yes'
full_build='yes'
here=$PWD
publish_dir=$here/../release
doxygen=$here/doxygen

if [ -e "${HOME}/run_test.py" ]; then
  echo 'Oops, you already have run_test.py - maybe you want to abort before it gets overwritten?'
  read yesno
fi

vers='0.16.2'
if [ $full_build == 'yes' ]; then
  echo 'Version '$vers'?'
  read yesno
  echo 'Updated version number in Common?'
  read yesno
  echo 'Updated version number in setup.py?'
  read yesno
  echo 'Updated release notes?'
  read yesno
  cd ~/
  echo import xboa.Common'\n'xboa.Common.make_doc'("'./'", "'$here'")' >& run_test.py
  python run_test.py
  rm run_test.py
  cd  $here
  rm -r dist
  python setup.py sdist
  cd dist
  tar -xzf xboa-$vers.tar.gz
  cd xboa-$vers
fi
python setup.py build
python setup.py install --force
rm -r build
cd $here

cd ~/
if [ $run_unit_tests == 'yes' ]; then
  python $here/xboa/test/XBOATest.py
fi
yesno=''
if [ $full_build == 'yes' ]; then
  cd $here
  $doxygen doc/Doxyfile

  echo 'Now publishing to $publish_dir (type yes to continue)'
  read yesno
fi
if [ -e $publish_dir ]; then
  echo "Found $publish_dir"
else
  mkdir $publish_dir
  echo "Did not find $publish_dir - making one now"
fi

if [ $yesno == 'yes' ]; then
  sleep 1
  mv doc/html $publish_dir/manual-xboa-$vers
  cd dist
  mv xboa-$vers.tar.gz $publish_dir
fi

cd $here


