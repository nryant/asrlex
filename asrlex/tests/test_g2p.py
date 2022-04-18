"""Tests for G2P training/application."""
# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from asrlex.g2p import remap_reserved_symbols, restore_reserved_symbols, G2P
from asrlex.prondict import PronDict


PARENT_DIR = Path(__file__).parent
REF_DICT_PATH = Path(PARENT_DIR, 'sample.dict')
REF_MODEL_PATH = Path(PARENT_DIR, 'g2p.fst')

SYMS_TXT = ('right-brace} R...\n'
	    'i_p_o ay...\n'
            'pipe| p...\n')
NO_SYMS_TXT = ('right-brace\u2622 R...\n'
               'i\u2695p\u2695o ay...\n'
               'pipe\u262f p...\n')

def test_remap_reserved_symbols():
    assert NO_SYMS_TXT == remap_reserved_symbols(SYMS_TXT)


def test_restore_reserved_symbols():
    assert SYMS_TXT == restore_reserved_symbols(NO_SYMS_TXT)


def test_g2p_init():
    G2P(REF_MODEL_PATH)


def test_train_g2p(tmpdir):
    # Test argument checking.
    with pytest.raises(TypeError):
        G2P.train_g2p('/dev/null', PronDict(), ngram_order=1.5)
    with pytest.raises(ValueError):
        G2P.train_g2p('/dev/null', PronDict(), ngram_order=0)
    with pytest.raises(ValueError):
        G2P.train_g2p('/dev/null', PronDict(), seq1_max=0)
    with pytest.raises(ValueError):
        G2P.train_g2p('/dev/null', PronDict(), seq2_max=0)

    # Train model.
    pdict = PronDict.load_dict(REF_DICT_PATH)
    model_path = Path(tmpdir, 'g2p.fst')
    model = G2P.train_g2p(
        model_path, pdict, ngram_order=3, seq1_del=True, seq1_max=2,
        seq2_del=True, seq2_max=2, grow=False)
    assert model is not None
    assert model_path.exists()

    # Check that it generates the expected pronunciations
    expected_prons = {('dh', 'ah'), ('dh', 'iy')}
    actual_prons = model.get_prons('the')
    assert actual_prons == expected_prons


def test_g2p_get_prons():
    model = G2P(REF_MODEL_PATH)
    expected_prons = {('dh', 'ah'), ('dh', 'iy')}
    actual_prons = model.get_prons('the')
    assert actual_prons == expected_prons
