#!/usr/bin/env python
"""TODO"""
from argparse import ArgumentParser
from pathlib import Path

from asrlex.g2p import G2P
from asrlex.prondict import PronDict



def train_g2p(args):
    """Train G2P model.

    Wrapper around ``G2P.train``, which itself wraps ``phonetisaurus-train``.
    """
    # TODO: Eliminate boilerplate via jsonargparse or similar.
    pdicts = [PronDict.load_dict(pth) for pth in args.pdict]
    pdict = PronDict.union(*pdicts)
    G2P.train_g2p(args.model, pdict, ngram_order=args.ngram_order,
                  seq1_del=args.grapheme_del, seq1_max=args.grapheme_maxlen,
                  seq2_del=args.phoneme_del, seq2_max=args.phoneme_maxlen,
                  grow=args.grow)


def predict_g2p(args):
    """Generate pronunciations using G2P model.

    Pronunciations will be written to STDOUT.
    """
    # Determine words to generate pronunciations for.
    words = []
    if args.words is not None:
        words = args.words.split(':')
    elif args.words_file is not None:
        with open(args.words_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    # Skip comments.
                    continue
                words.append(line.strip())

    # Generate pronunciations sequentially using supplied G2P model.
    model = G2P(args.model)
    pdict = PronDict()
    for word in sorted(words):
        prons = model.get_prons(
            word, n_best=args.n_best, cum_prob=args.cum_prob,
            thresh=args.thresh, beam=args.beam, accumulate=args.accumulate)
        pdict.add_pron(word, *prons)
    pdict.print_dict(sep=args.sep)


def main():
    parser = ArgumentParser()
    subcommands = parser.add_subparsers()

    # Training.
    train_parser = subcommands.add_parser(
        'train', description='train a G2P model')
    train_parser.add_argument(
        'model', type=Path, help='output path for trained G2P')
    train_parser.add_argument(
        'pdict', type=Path, nargs='+',
        help='path to pronunciation dictionary to train on')
    train_parser.add_argument(
        '--ngram-order', metavar='ORDER', type=int, default=7,
        help='maximum ngram order for joint ngram model '
             '(Default: %(default)s)')
    train_parser.add_argument(
        '--grapheme-maxlen', metavar='NUM-GRAPHEMES', type=int, default=2,
        help='maximum grapheme subsequence length in alignment '
             '(Default: %(default)s)')
    train_parser.add_argument(
        '--grapheme-del', default=False, action='store_true',
        help='allow deletions of graphemes in alignment')
    train_parser.add_argument(
        '--phoneme-maxlen', metavar='NUM-PHONHEMES', type=int, default=2,
        help='maximum phoneme subsequence length in alignment '
             '(Default: %(default)s)')
    train_parser.add_argument(
        '--phoneme-del', default=False, action='store_true',
        help='allow deletions of phonemes in alignment')
    train_parser.add_argument(
        '--grow', default=False, action='store_true',
        help='allow growing of lattice restrictions for words that cannot '
             'be aligned')
    train_parser.set_defaults(func=train_g2p)

    # Predict.
    predict_parser = subcommands.add_parser(
        'predict', description='generate pronunciations using a G2P model')
    predict_parser.add_argument(
        'model', type=Path, help='path to trained Phonetisaurus G2P model')
    predict_parser.add_argument(
        '--words', metavar='WORDS', default=None,
        help='colon delimited list of words to generate pronunciations for')
    predict_parser.add_argument(
        '--words-file', metavar='FILE', default=None,
        help='path to file containing words to generate prounciations for; '
              'one word per line')
    predict_parser.add_argument(
        '--n-best', '-k', metavar='NBEST', default=3, type=int,
        help='return the NBEST top scoring pronunciations per word; ignored '
             'if --cum-prob is set (Default: %(default)s)')
    predict_parser.add_argument(
        '--cum-prob', metavar='PROB', default=None, type=float,
        help='for each word, return smallest set of pronunciations whose '
             'cumulative probabiliy <= PROB; overrides --n-best '
             '(Default: %(default)s)')
    predict_parser.add_argument(
        '--thresh', metavar='THRESH', default=5, type=float,
        help='when creating n-best lists, prune words with log-prob '
             '<= -THRESH (Default %(default)s)')
    predict_parser.add_argument(
        '--beam', metavar='BEAMWIDTH', default=10000, type=int,
        help='decoding beam width (Default %(default)s)')
    predict_parser.add_argument(
        '--accumulate', default=False, action='store_true',
        help='accumulate probabilities across unique pronunciations')
    predict_parser.add_argument(
        '--sep', metavar='SEP', default='\t',
        help='separatator between head word and pronunciation in output')
    predict_parser.set_defaults(func=predict_g2p)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
