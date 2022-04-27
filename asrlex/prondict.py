"""Pronunciation dictionary."""
from collections import defaultdict
from pathlib import Path
import sys

from . import utils

__all__ = ['PronDict']


class PronDict:
    """Pronunciation dictionary handling mappings from words to phone
    sequences.

    Words are mapped to sets of pronunciations:

        >>> pdict = PronDict.load_dict('cmu.dict')
        >>> pdict['the']

    Parameters
    ----------
    other : PronDict or Mapping
        Pronunciation dictionary or compatible ``Mapping`` instance to
        initialize from.

    oov_pron : iterable of str
        Pronunciation to assign to out-of-vocabulary words.
        (Default: ('OOV',))

    Attributes
    ----------
    _word_to_prons : dict
        Mapping from words to sets of pronunciations, each pronunciation a
        list of phones.
    """
    def __init__(self, other=None, oov_pron=('OOV',)):
        self.oov_pron = tuple(oov_pron)
        self._word_to_prons = defaultdict(set)
        if other:
            self.update(other)

    def add_pron(self, word, *prons):
        """Add pronunciation."""
        if not word in self:
            self[word] = {}
        self[word].update(tuple(pron) for pron in prons)

    def update(self, other):
        """Add all pronunciations from another dictionary.

        Parameters
        ----------
        other : PronDict or Mapping
            Pronunciation dictionary or compatible ``Mapping`` instance to
            update from.
        """
        for word in other:
            self.add_pron(word, *other[word])

    def prune(self, keep=None, remove=None):
        """Prune dictionary.

        If ``keep`` is specified, dictionary will be pruned by removing
        all words not in ``keep``. Else, if ``remove`` is specified,
        dictionary will be pruned by removing all words in ``remove``.
        """
        if not utils.xor(keep is not None, remove is not None):
            raise ValueError(
                'Exactly one of "keep" and "remove" should be set.')
        if keep is not None:
            remove = set(self.words) - set(keep)
        for word in remove:
            try:
                del self[word]
            except KeyError:
                pass

    def union(self, *others):
        """Return union of pronunciation dictionaries."""
        oov_prons = {self.oov_pron}
        oov_prons.update([other.oov_pron for other in others])
        if len(oov_prons) > 1:
            raise ValueError('OOV pronunciations must match.')
        new_pdict = PronDict(self)
        for other in others:
            new_pdict.update(other)
        return new_pdict

    def intersection(self, *others):
        """Return intersection of pronunciation dictionaries."""
        pdicts = [self]
        pdicts.extend(others)
        oov_prons = {pdict.oov_pron for pdict in pdicts}
        if len(oov_prons) > 1:
            raise ValueError('OOV pronunciations must match.')
        new_pdict = PronDict(oov_pron=self.oov_pron)
        common_words = set.intersection(
            *[set(pdict.words) for pdict in pdicts])
        for word in common_words:
            prons = set.intersection(*[pdict[word] for pdict in pdicts])
            new_pdict[word] = prons
        return new_pdict

    def difference(self, *others):
        """Return difference of two or more pronunciation dictionaries.

        That is, all pronunciations that are in this dictionary but not the
        others.
        """
        oov_prons = {self.oov_pron}
        oov_prons.update([other.oov_pron for other in others])
        if len(oov_prons) > 1:
            raise ValueError('OOV pronunciations must match.')
        new_pdict = PronDict(self)
        others_union = PronDict.union(*others)
        for word in others_union:
            if word not in new_pdict:
                continue
            new_pdict[word] = new_pdict[word] - others_union[word]
            if not new_pdict[word]:
                del new_pdict[word]
        return new_pdict

    def copy(self):
        """Return deep copy of dictionary."""
        return PronDict(self, self.oov_pron)

    def apply(self, func, inplace=False):
        """Apply a function to every pronunciation in dictionary.

        Parameters
        ----------
        func : callable
           Function to apply to each pronunciation. Should return a new
           pronunciation.

        inplace : bool, optional
            If True, modify dictionary in place.
            (Default: False)

        Returns
        -------
        new_pdict : PronDict
            Dictionary with transformed pronunciations.
        """
        if not inplace:
            self = self.copy()
        for word in self:
            prons = [func(pron) for pron in self[word]]
            prons = [tuple(pron) for pron in prons]
            self[word] = prons
        return self

    @staticmethod
    def load_dict(dict_path, oov_pron=('OOV',), align_lexicon=False):
        """Load pronunciation dictionary from text file.

        Expected format of the text file is one pronunciation per line, each
        line of the form:

            <WORD> <PHONE>( <PHONE>)*

        where:

        - WORD  --  the head word of the entry
        - PHONE  --  a phone in the pronunciation

        If ``align_lexicon=True``, the expected format is:

            <WORD> <WORD> <PHONE>( <PHONE>)*

        Parameters
        ----------
        dict_path : Path
            Path to pronunciation dictionary.

        oov_pron : iterable of str
            Pronunciation to assign to out-of-vocabulary words.
            (Default: ('OOV',))

        align_lexicon : bool, optional
            If True, treat dictionary as being in Kaldi alignment lexicon
            format; that is, the head word is repeated.
            (Default: False)
        """
        dict_path = Path(dict_path)
        pdict = PronDict(oov_pron=oov_pron)
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith(';;;'):
                    # Used to indicate comments in cmudict.
                    continue
                fields = line.strip().split()
                if align_lexicon:
                    # For some reason, Kaldi alignment lexicons repeat the
                    # head word.
                    fields = fields[1:]
                if len(fields) < 2:
                    continue
                word = fields[0]
                pron = tuple(fields[1:])
                pdict.add_pron(word, pron)
        return pdict

    def print_dict(self, align_lexicon=False, sep='\t', file=sys.stdout):
        """Print mapping to STDOUT

        See ``load_dict`` for output file format.

        Parameters
        ----------
        align_lexicon : bool, optional
            If True, output dictionary as being in Kaldi alignment lexicon
            format.
            (Default: False)

        sep : str, optional
            Field separator.
            (Default: '\t')

        file : filelike, optional
            Object with ``write`` method.
            (Default: sys.stdout)
        """
        for word in self:
            for pron in sorted(self[word]):
                pron = [str(phn) for phn in pron]
                line = f'{word}{sep}{" ".join(pron)}'
                if align_lexicon:
                    line = f'{word}{sep}{line}'
                print(line, end='\n', file=file)

    def write_dict(self, dict_path, align_lexicon=False, sep='\t'):
        """Write mapping to file.

        See ``load_dict`` for output file format.

        Parameters
        ----------
        dict_path : Path
            Path to output pronunciation dictionary.

        align_lexicon : bool, optional
            If True, output dictionary as being in Kaldi alignment lexicon
            format.
            (Default: False)

        sep : str, optional
            Field separator.
            (Default: '\t')
        """
        dict_path = Path(dict_path)
        with open(dict_path, 'w', encoding='utf-8') as f:
            self.print_dict(align_lexicon=align_lexicon, sep=sep, file=f)

    @property
    def words(self):
        """Words comprising vocabulary.

        Words are sorted in lexicographic order.
        """
        return sorted(self._word_to_prons.keys())

    @property
    def phones(self):
        """Phones used in pronunciations."""
        phones = set()
        for word in self:
            for pron in self[word]:
                phones.update(pron)
        return sorted(phones)

    @property
    def n(self):
        """Number of words in vocabulary."""
        return len(self._word_to_prons)

    def __len__(self):
        return self.n

    def __getitem__(self, word):
        return self._word_to_prons.get(word, {self.oov_pron})

    def __setitem__(self, word, prons):
        prons = set(tuple(pron) for pron in prons)
        self._word_to_prons[word] = prons

    def __delitem__(self, word):
        del self._word_to_prons[word]

    def __contains__(self, word):
        return word in self._word_to_prons

    def __iter__(self):
        for word in self.words:
            yield word

    def __eq__(self, other_pdict):
        if self.oov_pron != other_pdict.oov_pron:
            return False
        if self._word_to_prons.items() != other_pdict._word_to_prons.items():
            return False
        return True

    def __or__(self, other):
        return self.union(other)

    def __and__(self, other):
        return self.intersection(other)

    def __sub__(self, other):
        return self.difference(other)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        pdict = dict(self._word_to_prons)
        return f'PronDict({pdict}, oov_pron={self.oov_pron})'
