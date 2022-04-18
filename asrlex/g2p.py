"""G2P using PHonetisaurus."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from wurlitzer import pipes

from Phonetisaurus import PhonetisaurusScript as Phonetisaurus

from . import utils

__all__ = ['G2P']



def _check_dependencies():
    """Check that Phonetisaurus and mitlm are installed."""
    for program in ['phonetisaurus-align', 'phonetisaurus-apply',
                    'phonetisaurus-arpa2wfst', 'phonetisaurus-train']:
        if not utils.which(program):
            # TODO: Add URL to INSTALL instructions once repo is public.
            raise ImportError(
                'Phonetisaurus required for G2P models. Please run '
                '"tools/install_phonetisaurus.sh".')
    if not utils.which('estimate-ngram'):
        # TODO: Add URL to INSTALL instructions once repo is public.
        raise ImportError(
            'MITLM required for training G2P models. Please run '
            '"tools/install_mitlm.sh".')

_check_dependencies()


RESERVED_MAP = {
    '}' : '\u2622',
    '|' : '\u262f',
    '_' : '\u2695',
    }
RESERVED_IMAP = {v : k for k, v in RESERVED_MAP.items()}

def remap_reserved_symbols(s):
    """Remap all occurrences of the Phonetisaurus reserved symbols in a string
    ``s``.

    This mapping is invertible and may be undone by calling
    ``restored_reserved_symbols``.
    """
    # Following is only marginally slower that a translate call.
    for isym, osym in RESERVED_MAP.items():
        s = s.replace(isym, osym)
    return s


def restore_reserved_symbols(s):
    """Restore all occurrences of the Phonetisaurus reserved symbols to a
    string ``s``.

    Undoes effect of ``remap_reserved_symbols.
    """
    for isym, osym in RESERVED_IMAP.items():
        s = s.replace(isym, osym)
    return s


class G2P:
    """Generates pronunciations for words from Phonetisaurus G2P model.

    Parameters
    ----------
    model_path : Path
        Path to Phonetisaurus FST model.

    Attributes
    ----------
    _model : PhonetisaurusScript.Phonetisaurus
            Phonetisaurus G2P model.
    """
    def __init__(self, model_path):
        model_path = Path(model_path)
        self.model_path = model_path
        self._model = Phonetisaurus(str(model_path))

    def get_prons(self, word, n_best=3, cum_prob=None, thresh=5,
                  beam=10000, accumulate=False):
        """Generate pronunciations for word.

        Parameters
        ----------
        word : str
            Word to generate pronunciations for.

        n_best : int, optional
            Maximum number of hypotheses to produce for each word. Has no
            effect if ``prob_mass`` is set.
            (Default: 3)

        cum_prob : float, optional
            If not ``None``, sort the hypotheses for each word in descending
            order of probability and select the maximum number of hypotheses
            whose cumulative probability is <= ``cum_prob``. Overrides
            ``n_best``.
            (Default: None)

        thresh : float, optional
            Pruning threshold for creation of n-best list, expressed as a
            negative log probability. Larger thresholds result in smaller lists
            and smaller thresholds in shorter list. Equivalent to
            ``weight_threshold`` in file ``shortest-path.h`` of OpenFST.
            (Default: 5)

        beam : int, optional
            Decoding beam width.
            (Default: 10000)

        accumulate : bool, optional
            If True, accumulate probabilities across unique pronunciations.
            (Default: False)
        """
        if cum_prob is not None:
            utils.validate_ranged_arg(cum_prob, 'cum_prob', 0.0, 1.0)
        cum_prob = cum_prob if cum_prob else 0.0
        utils.validate_integer_arg(beam, 'beam', min_val=1)
        word = remap_reserved_symbols(word)
        prons = set()
        with pipes() as (stdout, stderr):
            # Phonetisaurus writes annoying warnigns to STDERR whenever it
            # encounters an unknown symbol, so need this hack to prevent
            # console from being polluted.
            for result in self._model.Phoneticize(
                    word, n_best, beam, thresh, False, accumulate, cum_prob):
                phones = tuple(self._model.FindOsym(p) for p in result.Uniques)
                if not phones:
                    continue
                prons.add(phones)
        return prons

    @staticmethod
    def train_g2p(model_path, pron_dict, ngram_order=7, seq1_del=True,
                  seq1_max=2, seq2_del=True, seq2_max=2, grow=False):
        """Train G2P model using Phonetisaurus.

        Parameters
        ----------
        model_path : Path
            Output path for Phonetisaurus FST model.

        pron_dict : PronDict
            Pronunciation dictionary for training.

        ngram_order : int, optional
            Maximum ngram order for joint ngram model.
            (Default: 7)

        seq1_del : bool, optional
            Allow deletions of graphemes in alignment.
            (Default: True)

        seq1_max : int, optional
            Maximum grapheme subsequence length in alignment.
            (Default: 2)

        seq2_del : bool, optional
            Allow deletions of phonemes in alignment.
            (Default: True)

        seq2_max : int, optional
            Maximum phoneme subsequence length in alignment.
            (Default: 2)

        grow : bool, optional
            If True, allow growing of lattice restrictions for words that
            cannot be aligned.
            (Default: False)

        Returns
        -------
        model : PhonetisaurusScript.Phonetisaurus
            Phonetisaurus G2P model.
        """
        utils.validate_integer_arg(ngram_order, 'ngram_order', min_val=1)
        utils.validate_integer_arg(seq1_max, 'seq1_max', min_val=1)
        utils.validate_integer_arg(seq2_max, 'seq2_max', min_val=1)
        train_dir = Path(tempfile.mkdtemp())
        try:
            # Prepare dictionary for training by remapping the reserved symbols
            # "{", "|", and "_".
            dict_path = Path(train_dir, 'train.dict')
            pron_dict.write_dict(dict_path)
            txt = dict_path.read_text()
            txt = remap_reserved_symbols(txt)
            dict_path.write_text(txt)

            # Train G2P model.
            train_path = utils.which('phonetisaurus-train')
            cmd = ['python3', train_path,
                   '--lexicon', dict_path,
                   '--dir_prefix', train_dir, # Working directory for training.
                   '--model_prefix', 'model',
                   '--ngram_order', str(ngram_order),
                   '--seq1_max', str(seq1_max),
                   '--seq2_max', str(seq2_max),
                   ]
            if seq1_del:
                cmd.append('--seq1_del')
            if seq2_del:
                cmd.append('--seq2_del')
            if grow:
                cmd.append('--grow')
            subprocess.run(
                cmd, capture_output=True, check=True)

            # Migrate G2P FST from Phonetisaurus working directory.
            src_model_path = Path(train_dir, 'model.fst')
            shutil.copy(src_model_path, model_path)

            return G2P(model_path)
        except subprocess.CalledProcessError as e:
            # TODO:
            # - add appropriate logging
            # - ensure this catches all possible failure modes from
            #   Phonetisaurus
            raise e
        finally:
            shutil.rmtree(train_dir)

        return None
