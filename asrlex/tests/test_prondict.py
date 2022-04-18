"""Tests for pronunciation dictionaries."""
from pathlib import Path
import shutil
import tempfile

import pytest

from asrlex.prondict import PronDict


TEST_DIR = Path(__file__).parent
SAMPLE_DICT_PATH = Path(TEST_DIR, 'sample.dict')


def test_init():
    # Test empty initialization.
    oov_pron = ('OOV',)
    assert PronDict(oov_pron=oov_pron).oov_pron == oov_pron

    # Test initialization from mapping.
    prons = {('p1', 'p2'), ('p2', 'p3')}
    pdict = PronDict({'w1' : prons})
    assert pdict['w1'] == prons

    # Test initialization from another pronunciation dictionary.
    pdict2 = PronDict(pdict)
    assert pdict2 == pdict


def add_pron():
    expected_pdict = PronDict({
        'w1' : {('p1', 'p2'), ('p2', 'p3')}})
    pdict = PronDict()
    pdict.add_pron('w1', ('p1', 'p2'), ('p2', 'p3'))
    assert pdict == expected_pdict


def test_update():
    prons = {('p1', 'p2'), ('p2', 'p3')}
    pdict1 = PronDict({'w1' : prons})
    pdict2 = PronDict()
    pdict2.update(pdict1)
    assert pdict1 == pdict2
    expected_pdict = PronDict()


def test_prune():
    pdict = PronDict({
        'w1' : {('p1', 'p2')},
        'w2' : {('p2', 'p3')},
        'w3' : {('p3', 'p4')},
        })

    # Test remove specified words.
    pdict.prune(remove=['w1', 'w2'])
    assert pdict == PronDict({'w3' : {('p3', 'p4')}})

    # Test retention of specified words only.
    pdict.prune(keep=[])
    assert pdict == PronDict()

    # Test no exception raised when asked to remove non-existent words.
    pdict.prune(remove=['w1', 'w2', 'w3']) # Shouldn't raise exception.


def test_union():
    pdict1 = PronDict({'w1' : {('p1', 'p2')}})
    pdict2 = PronDict({'w2' : {('p2', 'p3')}})
    pdict3 = PronDict({'w3' : {('p3', 'p4')}})
    expected_pdict = PronDict({
        'w1' : {('p1', 'p2')},
        'w2' : {('p2', 'p3')},
        'w3' : {('p3', 'p4')},
        })
    assert PronDict.union(pdict1, pdict2, pdict3) == expected_pdict
    assert pdict1.union(pdict2, pdict3) == expected_pdict


def test_intersection():
    pdict1 = PronDict({
        'w1' : {('p1', 'p2'), ('p99', 'p100')},
        'w2' : {('p2', 'p3')},
        })
    pdict2 = PronDict({
        'w1' : {('p1', 'p2')},
        'w3' : {('p3', 'p4')},
        })
    pdict3 = PronDict({
        'w1' : {('p1', 'p2'), ('p100', 'p101')},
        'w4' : {('p4', 'p5')}})
    expected_pdict = PronDict({'w1' : {('p1', 'p2')}})
    assert PronDict.intersection(pdict1, pdict2, pdict3) == expected_pdict
    assert pdict1.intersection(pdict2, pdict3) == expected_pdict


def test_difference():
    pdict1 = PronDict({
        'w1' : {('p1', 'p2'), ('p2', 'p3')},
        'w2' : {('p3', 'p4')},
        })
    pdict2 = PronDict({
        'w1' : {('p1', 'p2')},
        'w3' : {('p3', 'p4')},
        })
    pdict3 = PronDict({
        'w1' : {('p2', 'p3')},
        'w4' : {('p5', 'p6')}})
    expected_pdict = PronDict({'w2' : {('p3', 'p4')}})
    assert PronDict.difference(pdict1, pdict2, pdict3) == expected_pdict
    assert pdict1.difference(pdict2, pdict3) == expected_pdict


def test_copy():
    pdict = PronDict({'w1' : {('p1', 'p2')}})
    pdict2 = pdict.copy()
    pdict['w1'] = {}
    assert pdict != pdict2


def test_apply():
    # Test inplace=False.
    pdict = PronDict({'w1' : {('p1', 'p2'), ('p2', 'p3')}})
    expected_pdict = PronDict(
        {'w1' : {('P1', 'P2'), ('P2', 'P3')}})
    to_upper = lambda x: (p.upper() for p in x)
    assert pdict.apply(to_upper) == expected_pdict
    assert pdict != expected_pdict

    # Test inplace=True
    pdict.apply(to_upper, inplace=True)
    assert pdict == expected_pdict


def test_phones():
    pdict = PronDict({'w1' : {('p1', 'p2'), ('p2', 'p3')}})
    assert pdict.phones == ['p1', 'p2', 'p3']


def test_load_dict():
    pdict_expected = PronDict({
        'an' : {('ae', 'n'), ('ah', 'n')},
        'the' : {('dh', 'ah'), ('dh', 'iy')},
        'watch' : {('w', 'aa', 'ch'), ('w', 'ao', 'ch')},
        })
    print(pdict_expected)
    print(PronDict.load_dict(SAMPLE_DICT_PATH))
    assert PronDict.load_dict(SAMPLE_DICT_PATH) == pdict_expected


def test_write_dict(tmpdir):
    tmp_dict_path = Path(tmpdir, 'test_write.dict')
    pdict = PronDict({
        'an' : {('ae', 'n'), ('ah', 'n')},
        'the' : {('dh', 'ah'), ('dh', 'iy')},
        'watch' : {('w', 'aa', 'ch'), ('w', 'ao', 'ch')},
        })
    pdict.write_dict(tmp_dict_path)
    assert SAMPLE_DICT_PATH.read_text() == tmp_dict_path.read_text()


def test_or():
    expected_pdict = PronDict({
        'w1' : {('p1', 'p2')},
        'w2' : {('p2', 'p3')},
        })
    pdict1 = PronDict({'w1' : {('p1', 'p2')}})
    pdict2 = PronDict({'w2' : {('p2', 'p3')}})

    assert (pdict1 | pdict2) == expected_pdict
