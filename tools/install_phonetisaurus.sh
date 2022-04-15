#!/bin/bash
# Installation Phonetisaurus Python wrapper.
set -e


#######################
# Config
#######################
NJOBS=20  # Number of parallel jobs for make.


#######################
# Check dependencies
#######################
# Phonetisaurus requires an install of OpenFST to compile.
#
# TODO: Add check for presence of pybindgen. Python bindings won't be
#       built if not present.
if [ ! -f openfst/install.succeeded ]; then
    echo "$0: OpenFST must be installed before building Phonetisaurus."
    echo "$0: Run the following script to install OpenFST:"
    echo "$0:"
    echo "$0:     install_openfst.sh"
    exit 1
fi


######################
# Clone repo.
#######################
PHONETISAURUS_REPO=https://github.com/AdolfVonKleist/Phonetisaurus.git
PHONETISAURUS_DIR=$PWD/Phonetisaurus
GIT_REVISION=f08d3df
if [ ! -d $PHONETISAURUS_DIR ]; then
    echo "$0: Downloading Phonetisaurus..."
    git clone $PHONETISAURUS_REPO $PHONETISAURUS_DIR
    cd $PHONETISAURUS_DIR
    git checkout $GIT_REVISION
    cd ..
fi


#######################
# Build
#######################
cd $PHONETISAURUS_DIR
if [ ! -f install.succeeded ]; then
    echo "$0: Compiling Phonetisaurus..."
    ./configure \
	--with-openfst-libs=../openfst/lib \
	--with-openfst-includes=../openfst/include \
	--enable-python --prefix=$PWD/install
    make clean
    make -j $NJOBS
    make install
    
    echo "$0: Installing Python extension..."
    cd python
    cp ../.libs/Phonetisaurus.so .
    python setup.py install
    
    touch install.succeeded
fi


#######################
# Success!
#######################
echo "$0: Successfully installed Phonetisaurus."
