#!/usr/bin/env python3
'CLI program to filter word choices to aid solving Wordle game problems.'
# Author: Mark Blakeney, Feb 2022.

import os
import sys
import argparse
import shlex
import re
from string import ascii_lowercase
from pathlib import Path

PROG = Path(sys.argv[0])
NAME = PROG.stem.replace('_', '-')
CNFFILE = Path(os.getenv('XDG_CONFIG_HOME', '~/.config'), f'{NAME}-flags.conf')

class Spell:
    'Wrapper for Python Spell Checker'
    def __init__(self):
        try:
            from spellchecker import SpellChecker
        except Exception:
            sys.exit('Must install pyspellchecker to use it.')

        self.spell = SpellChecker()

    def open(self):
        return self

    def __enter__(self):
        return self

    def __iter__(self):
        for word in self.spell:
            yield f'{word} {self.spell[word]}'

    def __exit__(self, *exc):
        del self.spell

def main():
    'Main code'
    # Data file from https://www.kaggle.com/rtatman/english-word-frequency
    # Work out where data file is on this system:
    for ddir in (PROG.resolve().parent.parent, Path(sys.prefix)):
        dictfile = ddir / 'share' / NAME / 'words.txt'
        if dictfile.exists():
            break

    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip(),
            epilog='Note you can set default starting arguments in '
            f'your {CNFFILE}.')
    opt.add_argument('-d', '--dictfile', default=dictfile,
            help='alternative dictionary+frequency text file, '
            'default = %(default)s. Or can specify "pyspellchecker" if '
            'you also install that package.')
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
    cnflines = ''
    cnffile = CNFFILE.expanduser()
    if cnffile.exists():
        with cnffile.open() as fp:
            cnflines = [re.sub(r'#.*$', '', line).strip() for line in fp]
        cnflines = ' '.join(cnflines).strip()

    args = opt.parse_args(shlex.split(cnflines) + sys.argv[1:])

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

    if args.dictfile == 'pyspellchecker':
        dictfile = Spell()
    else:
        dictfile = Path(args.dictfile).expanduser()
        if not dictfile.exists():
            return f'Dictionary file "{dictfile}" does not exist.'

    # Iterate over previous word guesses given on command line ..
    for word in args.words[:-1]:
        if len(word) != wordlen:
            return f'Word "{word}" must be length {wordlen}'

        for pos, csrc in enumerate(word):
            c = csrc.lower()
            if c not in valids:
                return f'Word "{word}" has invalid character "{csrc}"'

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

            if not wordset.issubset(valids):
                continue

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
            existing_freq = candidates.get(word)
            if not existing_freq or existing_freq < freq:
                candidates[word] = freq

    # Print all word candidates out in frequency order
    for word in sorted(candidates, key=candidates.get):
        print(word, candidates[word])

if __name__ == '__main__':
    sys.exit(main())
