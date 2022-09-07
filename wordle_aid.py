#!/usr/bin/env python3
'CLI program to filter word choices to aid solving Wordle game problems.'
# Author: Mark Blakeney, Feb 2022.

import sys
import argparse
from string import ascii_lowercase

# 3rd party package
from spellchecker import SpellChecker

def main():
    'Main code'
    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip())
    opt.add_argument('-v', '--vowels', type=int,
            help='exclude words with less than this number of unique vowels')
    opt.add_argument('-u', '--unique', action='store_true',
            help='exclude words with non-unique letters')
    opt.add_argument('words', nargs='+',
            help='list of attempted words. Upper case letter is right '
            'letter but wrong place. '
            'Lower case letter is wrong letter anywhere. Last word is '
            'wildcards for current matches.')

    args = opt.parse_args()
    valids = set(ascii_lowercase)
    vowels = set('aeiou')

    # Last command line argument is word mask
    wordmask = args.words[-1].lower()
    wordlen = len(wordmask)
    includes = set(wordmask) & valids
    includes_must = [(p, c) for p, c in enumerate(wordmask) if c in valids]

    excludes = set()
    includes_not = []

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

    # Load list of words from spellchecker
    words = SpellChecker()

    # Iterate over words from dictionary and apply filters ..
    for word in words:
        if len(word) != wordlen:
            continue

        # Create set() of chars for efficient subsequent checks
        wordset = set(word)

        # Ensure word has only valid chars
        if not wordset.issubset(valids):
            continue

        # If option specified, check if unique chars
        if args.unique and len(wordset) != wordlen:
            continue

        # If option specified, check has required number of vowels
        if args.vowels and len(wordset & vowels) < args.vowels:
            continue

        # Check has no excluded chars, and has all required includes
        if not wordset.isdisjoint(excludes) or not includes <= wordset:
            continue

        # Check does not have chars in positions where they must be excluded
        if any(word[pos] == c for pos, c in includes_not):
            continue

        # Check does have chars in positions where they must be included
        if any(word[pos] != c for pos, c in includes_must):
            continue

        # This word is a candidate. If it is in the list twice then
        # record higher frequency.
        freq = words[word]
        existing_freq = candidates.get(word, 0)
        if existing_freq < freq:
            candidates[word] = freq

    # Print all word candidates out in frequency order
    for word in sorted(candidates, key=candidates.get):
        print(word, candidates[word])

if __name__ == '__main__':
    sys.exit(main())
