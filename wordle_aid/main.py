#!/usr/bin/env python3
"CLI program to filter word choices to aid solving Wordle game problems."

# Author: Mark Blakeney, Feb 2022.
from __future__ import annotations

import itertools
import shlex
import sys
from collections import Counter, deque
from pathlib import Path
from random import randint
from string import ascii_lowercase
from typing import TextIO

from argparse_from_file import ArgumentParser, Namespace
from spellchecker import SpellChecker

PROG = Path(__file__).parent.stem.replace('_', '-')

nonchar = '.'
valids = set(ascii_lowercase)
vowels = set('aeiou')
words = {}
words_language = None
words_files = tuple()
exclude_words = set()
exclude_words_files = tuple()
valid_words = set()

# See https://www.baeldung.com/linux/terminal-output-color
COLOR_green = '\033[;42m'
COLOR_yellow = '\033[;43m'
COLOR_reset = '\033[;49m'


def insert_colors(guess: str, result: str) -> str:
    "Insert wordle result colors to chars in guess string"
    nguess = []
    for g, r in zip(guess, result):
        if r != '.':
            g = COLOR_green + r + COLOR_reset
        elif g.isupper():
            g = COLOR_yellow + g + COLOR_reset

        nguess.append(g)

    return ''.join(nguess)


def dofilter(
    counts: dict[str, int], candidates: list[set[str]], args: Namespace
) -> dict[str, int]:
    # Iterate over words from dictionary and apply filters ..
    wordlen = len(candidates)
    ncandidates = {}
    for word in words:
        # Ensure word has required length
        if len(word) != wordlen:
            continue

        if valid_words and word not in valid_words:
            continue

        if word in exclude_words:
            continue

        # Create set() of chars for efficient subsequent checks
        wordset = set(word)

        # Ensure word has only valid chars
        if not wordset.issubset(valids):
            continue

        # If option specified, ensure has unique chars
        if args.unique and len(wordset) != wordlen:
            continue

        # If option specified, ensure has required number of vowels
        if args.vowels and len(wordset & vowels) < args.vowels:
            continue

        # If option specified, ensure is not plural
        if args.no_plural and word.endswith('s'):
            continue

        # Ensure required number of chars in word
        if any(word.count(c) < count for c, count in counts.items()):
            continue

        # Ensure each char in word is a candidate for that position
        if not all(c in cands for c, cands in zip(word, candidates)):
            continue

        # This word is a candidate. If it is in the list twice then
        # record higher frequency.
        freq = words[word]
        existing_freq = ncandidates.get(word, 0)
        if existing_freq < freq:
            ncandidates[word] = freq

    return ncandidates


def get_words(
    guesses: list[str], wordmask: str, args: Namespace
) -> list[tuple[str, int]]:
    "Get list of candidate words + frequencies for given guesses and mask"
    wordlen = len(wordmask)
    candidates = [({c} if c in valids else valids.copy()) for c in wordmask]
    allcounts = [Counter(c for c in wordmask if c in valids)]

    # Iterate over previous word guesses given on command line ..
    for word in guesses:
        if len(word) != wordlen:
            sys.exit(f'Word "{word}" must be length {wordlen}.')

        count = Counter()
        for pos, csrc in enumerate(word):
            if (c := csrc.lower()) not in valids:
                sys.exit(f'Invalid char "{c}" in word "{word}".')

            if c == wordmask[pos]:
                count[c] += 1
                continue

            if c != csrc:
                # Is upper case, so char is in word but not in this position
                candidates[pos].discard(c)
                count[c] += 1
            else:
                # Is lower case, so char is not in word
                for pos2 in range(wordlen):
                    if wordmask[pos2] != c:
                        candidates[pos2].discard(c)

        allcounts.append(count)

    # Sum max count for each char across all guesses
    chars = set(c for all in allcounts for c in all.keys())
    counts = {c: max(count.get(c, 0) for count in allcounts) for c in chars}
    if (n := sum(counts.values())) > wordlen:
        sys.exit(f'Too many required characters ({n} required > {wordlen} length).')

    # Filter word candidates based on counts and candidate sets
    ncandidates = dofilter(counts, candidates, args)

    # Output list of all (word, freq) candidates out in frequency order
    return [
        (word, ncandidates[word])
        for word in sorted(ncandidates, key=ncandidates.__getitem__)
    ]


def get_next_candidate(cands: list[tuple[str, int]], args: Namespace) -> str:
    "Return candidate word from top results"
    nlen = len(cands)
    num = args.random
    if num[-1] == '%':
        n = round(nlen * int(num[:-1]) / 100)
    else:
        n = int(num)

    n = randint(1, min(max(1, n), nlen))
    return cands[-n][0]


def score(word: str, target: str) -> str:
    "Score given word against target, returns:"
    ' upper case = letter in correct place'
    ' lower case = letter in incorrect place'
    ' nonchar = letter not in word'
    res = []
    remain = Counter(target)
    for c, t in zip(word, target):
        if c not in target:
            c = nonchar
        elif c == t:
            remain[c] -= 1
            c = c.upper()

        res.append(c)

    nres = []
    for c in res:
        if c.islower():
            remain[c] -= 1
            if remain[c] < 0:
                c = nonchar

        nres.append(c)

    return ''.join(nres)


def load_words(fnames: tuple[str]) -> set[str]:
    "Load words from given list of files into given set"
    words = set()
    for fname in fnames:
        with Path(fname).expanduser().open() as fp:
            for line in fp:
                words.update(line.lower().split())

    return words


def init(
    argsl: list[str] | str, read_start_options: bool
) -> tuple[ArgumentParser, Namespace]:
    # Process command line options
    opt = ArgumentParser(
        description=__doc__, from_file=None if read_start_options else ''
    )
    opt.add_argument(
        '-l',
        '--language',
        default='en',
        help='pyspellchecker language dictionary to use, default="%(default)s"',
    )
    opt.add_argument(
        '-v',
        '--vowels',
        type=int,
        help='exclude words with less than this number of unique vowels',
    )
    opt.add_argument(
        '-u',
        '--unique',
        action='store_true',
        help='exclude words with non-unique letters',
    )
    opt.add_argument(
        '-S',
        '--no-plural',
        action='store_true',
        help='exclude words ending in "s" (simple plural filter)',
    )
    opt.add_argument(
        '-w',
        '--words-file',
        action='append',
        default=[],
        help='filter dictionary to words in given text file. '
        'Use multiple times to specify multiple files.',
    )
    opt.add_argument(
        '-e',
        '--exclude-words-file',
        action='append',
        default=[],
        help='exclude words in given text file. Use multiple '
        'times to specify multiple files.',
    )
    opt.add_argument(
        '-s',
        '--solve',
        action='store_true',
        help='solve to final given word, starting with earlier given words (if any)',
    )
    opt.add_argument(
        '-r',
        '--random',
        default='1',
        help='choose word for solver at each step randomly from given '
        'number (or %%) of top candidates, default=%(default)s',
    )
    opt.add_argument(
        '-c',
        '--no-colors',
        action='store_true',
        help="don't show colors in solver output",
    )
    opt.add_argument(
        '-V', '--version', action='store_true', help=f'show {opt.prog} version'
    )
    opt.add_argument(
        'words',
        nargs='*',
        help='list of attempted words. Upper case letter is right '
        'letter but wrong place. '
        'Lower case letter is wrong letter anywhere. Last word is '
        'wildcards for current matches.',
    )

    if isinstance(argsl, str):
        argsl = shlex.split(argsl)

    sys.argv = [opt.prog] + argsl
    return opt, opt.parse_args()


# This is defined as a standalone function so it could be called as an
# API for simulation runs etc by providing args_list and stream.
# E.g. fileout stream can be io.StringIO.
def run(
    argsl: list[str] | str,
    fileout: TextIO = sys.stdout,
    *,
    read_start_options: bool = False,
) -> None:
    "Run with given argsl to specified output stream"
    global words
    global words_language
    global words_files, exclude_words_files

    opt, args = init(argsl, read_start_options)

    if hasattr(fileout, 'isatty') and not fileout.isatty():
        args.no_colors = True

    if args.version:
        try:
            from importlib.metadata import version

            ver = version(opt.prog)
        except Exception:
            ver = 'unknown'

        print(ver, file=fileout)
        return

    if not args.words:
        opt.error('Must enter words')

    # Load list of words from spellchecker (use cached if possible)
    if words_language != args.language:
        words_language = args.language
        words = SpellChecker(language=words_language)

    files = tuple(args.words_file)
    if words_files != files:
        words_files = files
        valid_words.update(load_words(files))

    files = tuple(args.exclude_words_file)
    if exclude_words_files != files:
        exclude_words_files = files
        exclude_words.update(load_words(files))

    guesses = args.words[:-1]
    wordmask = args.words[-1]
    wordmask_l = wordmask.lower()
    wordlen = len(wordmask)

    if not args.solve:
        # Just run normal aid tool
        for word, freq in get_words(guesses, wordmask_l, args):
            print(word, freq, file=fileout)
        return

    # Else run solver ..
    if not set(wordmask_l).issubset(valids):
        sys.exit(f'Invalid word {wordmask} to solve.')

    res = '.' * len(wordmask_l)
    guesses = deque(guesses)
    nguesses = []

    for count in itertools.count(1):
        if len(guesses) > 0:
            guess = guesses.popleft().lower()
            if len(guess) != wordlen:
                sys.exit(f'Word "{guess}" must be length {wordlen}.')
        else:
            cands = get_words(nguesses, res, args)
            if not cands:
                print(f'{count:2} {wordmask_l} NO SOLUTION', file=fileout)
                break
            guess = get_next_candidate(cands, args)

        gscore = score(guess, wordmask_l)
        nguess = ''.join(c.upper() if p.islower() else c for c, p in zip(guess, gscore))
        res = ''.join(c.lower() if c.isupper() else p for c, p in zip(gscore, res))

        solved = guess == wordmask_l
        add = ' SOLVED' if solved else ''

        nguess_d = nguess if args.no_colors else insert_colors(nguess, res)
        print(f'{count:2} {guess} [{nguess_d} {res}]{add}', file=fileout)

        if solved:
            break

        nguesses.append(nguess)


def main() -> None:
    "Main code"
    run(sys.argv[1:], read_start_options=True)


if __name__ == '__main__':
    main()
