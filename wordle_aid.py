#!/usr/bin/env python3
'CLI program to filter word choices to aid solving Wordle game problems.'
# Author: Mark Blakeney, Feb 2022.

import sys
import argparse
import shlex
from string import ascii_lowercase
from pathlib import Path

NAME = Path(sys.argv[0]).stem.replace('_', '-')
CNFFILE = f'~/.config/{NAME}-flags.conf'

# This file from https://www.kaggle.com/rtatman/english-word-frequency
DICTFILE = Path(sys.prefix) / 'share' / NAME / 'words.txt'

def main():
    'Main code'
    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip(),
            epilog='Note you can set default starting arguments in '
            f'your {CNFFILE}.')
    opt.add_argument('-d', '--dictfile', default=DICTFILE,
            help='alternative dictionary+frequency text file, '
            'default = %(default)s.')
    opt.add_argument('-v', '--vowels', type=int,
            help='exclude words with less than this number of unique vowels')
    opt.add_argument('-u', '--unique', action='store_true',
            help='exclude words with non-unique letters')
    opt.add_argument('words', nargs='+',
            help='list of attempted words. Upper case letter is right '
            'letter but wrong place. '
            'Lower case letter is wrong letter anywhere. Last word is '
            'wildcards for current matches.')

    # Merge in default args from user config file. Then parse the
    # command line.
    cnffile = Path(CNFFILE).expanduser()
    cnfargs = shlex.split(cnffile.read_text().strip()) \
            if cnffile.exists() else []
    args = opt.parse_args(cnfargs + sys.argv[1:])

    dictfile = Path(args.dictfile).expanduser()
    if not dictfile.exists():
        sys.exit(f'Dictionary file {dictfile} does not exist.')

    valids = set(ascii_lowercase)
    vowels = set('aeiou')

    # Last command line argument is word mask
    wordmask = args.words[-1].lower()
    wordlen = len(wordmask)
    wordset = set(c for c in wordmask if c in valids)
    includes_must = [(p, c) for p, c in enumerate(wordmask) if c in valids]

    excludes = set()
    includes = wordset.copy()
    includes_not = []

    # Iterate over previous word guesses given on command line ..
    for word in args.words[:-1]:
        if len(word) != wordlen:
            sys.exit(f'Word {word} must be length {wordlen}')

        for pos, csrc in enumerate(word):
            c = csrc.lower()
            if c not in valids:
                sys.exit(f'Word {word} has invalid character "{csrc}"')

            if c == csrc:
                excludes.add(c)
            else:
                includes.add(c)
                if c != wordmask[pos]:
                    includes_not.append((pos, c))

    excludes -= includes
    candidates = {}

    # Iterate over words from dictionary and apply filters ..
    with dictfile.open() as fp:
        for ln in fp:
            ln = ln.strip()
            if not ln or ln[0].lower() not in valids:
                continue

            word, freq_str = ln.replace(',', ' ').split()
            if len(word) != wordlen or not freq_str.isdigit():
                continue

            word = word.lower()
            wordset = set(word)

            if args.unique and len(wordset) != wordlen:
                continue

            if args.vowels and len(wordset & vowels) < args.vowels:
                continue

            if not wordset.isdisjoint(excludes) or not includes <= wordset:
                continue

            if any(word[pos] == c for pos, c in includes_not):
                continue

            if any(word[pos] != c for pos, c in includes_must):
                continue

            # This word is a candidate. If it is in the list twice then
            # record higher frequency.
            freq = int(freq_str)
            if word not in candidates or freq > candidates[word]:
                candidates[word] = freq

    # Print all word candidates out in frequency order
    for word in sorted(candidates, key=candidates.get):
        print(word, candidates[word])

if __name__ == '__main__':
    sys.exit(main())
