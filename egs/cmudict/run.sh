#!/bin/bash

set -e
stage=1


# Ensure required scripts are on path.
TOOLS_DIR=../../tools
MITLM_BIN=$TOOLS_DIR/mitlm/install/bin/
PHONETISAURUS_BIN=$TOOLS_DIR/Phonetisaurus/install/bin/
export PATH=$MITLM_BIN:$PHONETISAURUS_BIN:$PATH


##############################################
### Download most recent version of CMUdict.
##############################################
# Download and check out v0.7b from github.
CMUDICT=cmudict/cmudict.dict
CMUDICT_REPO=https://github.com/cmusphinx/cmudict
CMUDICT_HASH=4c6a365
if [ $stage -le 1 ]; then
    if [ ! -f $CMUDICT ]; then
	echo "Downloading CMUdict..."
	rm -fr cmudict/
	git clone $CMUDICT_REPO cmudict/
	cd cmudict/
	git checkout $CMUDICT_HASH
	cd ..
	echo "Download succeeded..."
    fi
fi


##############################################
### Train a G2P model using Phonetisaurus.
##############################################
# Uses asrlex train command, which wraps the Phonetisaursu training script.
# Equivalent to:
#
#     phonetisaurus-train \
#         --lexicon $CMUDICT --dir_prefix g2p_tmp/ --model_prefix model \
#         --ngram_order 7 --seq1_del --seq1_max 2 \
#         --seq2_del --seq2_max 2
G2PMODEL=cmudict.g2p
if [ $stage -le 2 ]; then
    echo "Training G2P..."
    asrlex train \
           --ngram-order 7 --grapheme-maxlen 2 --phoneme-maxlen 2 \
	   $G2PMODEL $CMUDICT
    echo "Training succeeded. Model is located at ${G2PMODEL}."
fi


##############################################
# Generate pronunciations using trained model.
##############################################
# Ese asrlex predict command. Generate top-2 pronunciations for each word
# in words.txt; these belong to 3 categories (see comments in words.txt):
# - words that appeared in training
# - words that are morphological variants of words that appeared in training
# - words that are completely out of vocabulary (OOV)
GENDICT=generated.dict
if [ $stage -le 3 ]; then
    echo "Generating pronunciations for words in \"words.txt\"..."
    asrlex predict \
      --n-best 2 --words-file words.txt $G2PMODEL > $GENDICT
    echo "Successful. Results in \"${GENDICT}\"."
fi
