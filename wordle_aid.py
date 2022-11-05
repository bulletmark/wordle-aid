#!/usr/bin/env python3
'CLI program to filter word choices to aid solving Wordle game problems.'
# Author: Mark Blakeney, Feb 2022.

import sys
import itertools
from argparse import ArgumentParser, Namespace
from string import ascii_lowercase
from collections import Counter, deque
from random import randint

# 3rd party package
from spellchecker import SpellChecker

NON = '.'
VALIDS = set(ascii_lowercase)
VOWELS = set('aeiou')

# Load list of words from spellchecker
WORDS = SpellChecker()

def get_words(guesses: list, wordmask: str, args: Namespace) -> list:
    'Get list of candidate words + frequencies for given guesses and mask'
    wordlen = len(wordmask)
    includes = set(wordmask) & VALIDS
    includes_must = [(p, c) for p, c in enumerate(wordmask) if c in VALIDS]

    excludes = set()
    includes_not = []
    counts = []

    # Iterate over previous word guesses given on command line ..
    for word in guesses:
        word_count = Counter()
        if len(word) != wordlen:
            sys.exit(f'Word "{word}" must be length {wordlen}')

        for pos, csrc in enumerate(word):
            c = csrc.lower()
            if c not in VALIDS:
                sys.exit(f'Word "{word}" has invalid character "{csrc}"')

            if c != wordmask[pos]:
                includes_not.append((pos, c))

            if c == csrc:
                excludes.add(c)
                if c == wordmask[pos]:
                    word_count[c] += 1
            else:
                includes.add(c)
                word_count[c] += 1

        if word_count:
            counts.append(word_count)

    chars = set(itertools.chain.from_iterable(counts))
    includes_count = {c: max(wc[c] for wc in counts) for c in chars}

    # Only bother with chars having multiple (>1) counts
    includes_count = {k: v for k, v in includes_count.items() if v > 1}

    excludes -= includes
    candidates = {}

    # Iterate over words from dictionary and apply filters ..
    for word in WORDS:
        # Ensure word has required length
        if len(word) != wordlen:
            continue

        # Create set() of chars for efficient subsequent checks
        wordset = set(word)

        # Ensure word has only valid chars
        if not wordset.issubset(VALIDS):
            continue

        # If option specified, ensure has unique chars
        if args.unique and len(wordset) != wordlen:
            continue

        # If option specified, ensure has required number of vowels
        if args.vowels and len(wordset & VOWELS) < args.vowels:
            continue

        # Ensure has no excluded chars, and has all required includes
        if not wordset.isdisjoint(excludes) or not includes <= wordset:
            continue

        # Ensure does not have chars in positions where they must be excluded
        if any(word[pos] == c for pos, c in includes_not):
            continue

        # Ensure does have chars in positions where they must be included
        if any(word[pos] != c for pos, c in includes_must):
            continue

        # Ensure has required multiples of relevant chars
        for c, v in includes_count.items():
            if word.count(c) < v:
                break
        else:
            # This word is a candidate. If it is in the list twice then
            # record higher frequency.
            freq = WORDS[word]
            existing_freq = candidates.get(word, 0)
            if existing_freq < freq:
                candidates[word] = freq

    # Output list of all (word, freq) candidates out in frequency order
    return [(word, candidates[word])
            for word in sorted(candidates, key=candidates.get)]

def get_next_candidate(cands: str, args: Namespace) -> str:
    'Return candidate word from top results'
    nlen = len(cands)
    num = args.random
    if num[-1] == '%':
        n = round(nlen * int(num[:-1]) / 100)
    else:
        n = int(num)

    n = randint(1, min(max(1, n), nlen))
    return cands[-n][0]

def score(word: str, target: str) -> str:
    'Score given word against target, returns:'
    ' upper case = letter in correct place'
    ' lower case = letter in incorrect place'
    ' NON = letter not in word'
    res = []
    remain = Counter(target)
    for c, t in zip(word, target):
        if c not in target:
            c = NON
        elif c == t:
            remain[c] -= 1
            c = c.upper()

        res.append(c)

    nres = []
    for c in res:
        if c.islower():
            remain[c] -= 1
            if remain[c] < 0:
                c = NON

        nres.append(c)

    return ''.join(nres)

# This is defined as a standalone function so it could be called as an
# API for simulation runs etc by providing args_list and stream.
# E.g. stream can be io.StringIO.
def run(args_list: list, fp=sys.stdout) -> None:
    'Run with given args to specified output stream'
    # Process command line options
    opt = ArgumentParser(description=__doc__.strip())
    opt.add_argument('-v', '--vowels', type=int,
            help='exclude words with less than this number of unique vowels')
    opt.add_argument('-u', '--unique', action='store_true',
            help='exclude words with non-unique letters')
    opt.add_argument('-s', '--solve', action='store_true',
            help='solve to final given word, starting with earlier '
                     'given words (if any)')
    opt.add_argument('-r', '--random', default='1',
            help='choose word for solver at each step randomly from given '
                     'number (or %%) of top candidates, default=%(default)s')
    opt.add_argument('words', nargs='+',
            help='list of attempted words. Upper case letter is right '
            'letter but wrong place. '
            'Lower case letter is wrong letter anywhere. Last word is '
            'wildcards for current matches.')

    args = opt.parse_args(args_list)

    guesses = args.words[:-1]
    wordmask = args.words[-1]
    wordmask_l = wordmask.lower()

    if not args.solve:
        # Just run normal aid tool
        for word, freq in get_words(guesses, wordmask_l, args):
            print(word, freq, file=fp)
        return

    # Else run solver ..
    if not set(wordmask_l).issubset(VALIDS):
        sys.exit(f'Invalid word {wordmask} to solve')

    res = '.' * len(wordmask_l)
    guesses = deque(guesses)
    nguesses = []

    for count in itertools.count(1):
        if len(guesses) > 0:
            guess = guesses.popleft().lower()
        else:
            cands = get_words(nguesses, res, args)
            if not cands:
                print('No solution', file=fp)
                break
            guess = get_next_candidate(cands, args)

        gscore = score(guess, wordmask_l)
        nguess = ''.join(c.upper() if p.islower() else c for c, p in
                            zip(guess, gscore))
        res = ''.join(c.lower() if c.isupper() else
                p for c, p in zip(gscore, res))

        print(f'{count} {guess} [{nguess} {res}]', file=fp)

        if guess == wordmask_l:
            break

        nguesses.append(nguess)

def main() -> None:
    'Main code'
    return run(sys.argv[1:])

if __name__ == '__main__':
    sys.exit(main())
