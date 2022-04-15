#!/bin/bash
# Installation script for OpenFST with Python extensions.
set -e


#######################
# Config
#######################
NJOBS=20  # Number of parallel jobs for make.


#######################
# Clone repo.
#######################
OPENFST_URL=http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.7.2.tar.gz
OPENFST_DIR=openfst
if [ ! -d $OPENFST_DIR ]; then
    echo "$0: Downloading OpenFst..."
    wget $OPENFST_URL
    tar -xvf openfst-1.7.2.tar.gz
    ln -s openfst-1.7.2 openfst
fi


#######################
# Build
#######################
cd $OPENFST_DIR
if [ ! -f install.succeeded ]; then
    echo "$0: Compiling OpenFst..."
    ./configure \
	--enable-static --enable-shared --enable-far --enable-ngram-fsts \
	--prefix=$PWD
    make clean
    make -j $NJOBS
    make install
    touch install.succeeded
fi


#######################
# Success!
#######################
echo "Successfully installed OpenFst."
