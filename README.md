This repo illustrates the usage of [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus) to train models for grapheme-to-phoneme (G2P) transduction
for use in building speech-to-text or forced alignment systems.


# Installation

If using a recent Linux distribution (e.g., Ubuntu >= 18.04) or OS X,
installation should be straightforward. If using Windows, you will need to
first install and activate [Microsoft's Windows Subsystem for Linux](https://docs.microsoft.com/en-us/windows/wsl/); see [Windows specific instructions](windows-specific-instructions)
for more details.


#### Step 1: Install build dependencies

Run the commands below to install the system packages necessary for building
Phonetisaurus and dependencies from source:

    # Ubuntu/Debian
    sudo apt-get install autoconf cmake curl g++ git libtool make pkg-config subversion wget

    # OSX
    sudo port install autoconf autoconf-archive cmake git libtool pkgconfig wget


#### Step 2: Clone the repo and create a new build environment

First, clone the repo:

    git clone git@github.com:nryant/phonetisaurus_tutorial.git

Next, create a new isolated Python environment into which to install the
aligner and its dependencies. In these instructions, we use ``virtualenv``,
though other tools such as ``conda`` will also work. Make sure to activate the
new virtual environment before moving on to the next step:

    virtualenv my_venv
    source my_venv/bin/activate


#### Step 3: Install Python packages

To install the Python packages relied upon by the scripts, run:

    cd phonetisaurus_tutorial/
    pip install -r requirements.txt


#### Step 4: Install OpenFST

Phonetisaurus relies on the presence of an installation of [OpenFST](http://www.openfst.org)
for the build process. To build OpenFST locally under ``tools/``:

    cd tools
    ./install_openfst.sh

If the build process is successful, you will see ``Successfully installed OpenFst.``
printed at the very end.


#### Step 5: Install Phonetisaurus and MITLM

We rely on [Phonetisaurus](https://github.com/AdolfVonKleist/Phonetisaurus)
for generating pronunciations for out-of-vocabulary words. To build Phonetisaurus
and install its Python wrapper:

    cd tools
    ./install_phonetisaurus.sh

If the build is successful, you will see ``Successfully installed Phonetisaurus.``

You will also need to install the [MIT Language Modeling Toolkit](https://github.com/mitlm/mitlm),
which Phonetisaurus depends on:

    cd tools
    ./install_mitlm.sh

If successful, you should see ``Successfully installed MITLM.``


#### Windows specific instructions

To install on Windows, you first need to activate the Windows Subsystem for Linux
(WSL) by following the instructions at:

    https://docs.microsoft.com/en-us/windows/wsl/install-win10

During this install process, you will be asked to select a Linux distribution
(step 6). Make sure to select Ubuntu 20.04 LTS:

    https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71?rtc=1&activetab=pivot:overviewtab

After installation, create a user account:

    https://docs.microsoft.com/en-us/windows/wsl/user-support

and open a terminal Window. You should now be able to install by


# References

* Novak, J. R., Minematsu, N., & Hirose, K. (2016). [Phonetisaurus: Exploring grapheme-to-phoneme conversion with joint n-gram models in the WFST framework](https://www.cambridge.org/core/journals/natural-language-engineering/article/abs/phonetisaurus-exploring-graphemetophoneme-conversion-with-joint-ngram-models-in-the-wfst-framework/F1160C3866842F0B707924EB30B8E753). Natural Language Engineering, 22(6), 907-938.