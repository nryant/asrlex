#!/bin/bash
# Installs MIT Language Modeling (MITLM) toolkit. This is needed by
# Phonetisaurus for ngram estimation.
set -e


#######################
# Config
#######################
NJOBS=20  # Number of parallel jobs for make.


######################
# Clone repo.
#######################
MITLM_REPO=https://github.com/mitlm/mitlm.git
MITLM_DIR=$PWD/mitlm
GIT_REVISION=553edca
if [ ! -d $MITLM_DIR ]; then
    echo "$0: Downloading MITLM..."
    git clone $MITLM_REPO $MITLM_DIR
    cd $MITLM_DIR
    git checkout $GIT_REVISION
    cd ..
fi


#######################
# Build
#######################
cd $MITLM_DIR
if [ ! -f install.succeeded ]; then
    echo "$0: Compiling MITLM..."
    autoreconf -i
    ./configure --prefix=$PWD/install
    make clean
    make -j $NJOBS
    make install
    touch install.succeeded
fi


#######################
# Success!
#######################
echo "$0: Successfully installed MITLM."
