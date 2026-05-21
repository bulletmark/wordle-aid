#!/usr/bin/env python3
"""
Takes a word pattern of letters in character positions: '?' for don't care,
'.' for any character to group in a common pattern, any specific letter to
match literally, or 1 or more chars wrapped in '[]' to not match literally at
that position. Prints all words that match.
"""

import argparse
import io
import sys
from collections import defaultdict
from pathlib import Path

import wordle_aid


def load_words(fnames: tuple[str]) -> set[str]:
    "Load words from given list of files into given set"
    words = set()
    for fname in fnames:
        with Path(fname).expanduser().open() as fp:
            for line in fp:
                words.update(line.lower().split())

    return words


def main() -> str | None:
    opt = argparse.ArgumentParser(description=__doc__)
    opt.add_argument(
        '-e',
        '--exclude-words-file',
        action='append',
        default=[],
        help='exclude words in given text file. Use multiple '
        'times to specify multiple files.',
    )
    opt.add_argument(
        '-S',
        '--no-plural',
        action='store_true',
        help='exclude words ending in "s" (simple plural filter)',
    )
    opt.add_argument('pattern', help='input character pattern of "?", ".", and letters')
    args = opt.parse_args()

    skips = []
    patternl = []
    index = 0
    exclude = None
    for c in args.pattern.lower():
        if c == '[':
            exclude = set()
            continue

        if c == ']':
            if not exclude:
                return 'Error: mismatched or empty "[]"'
            c = '.'
        elif exclude is not None:
            exclude.add(c)
            continue

        index += 1
        skips.append(exclude or set())
        exclude = None
        patternl.append(c)

    if exclude is not None:
        return 'Error: mismatched "[]"'

    exclude_words = load_words(args.exclude_words_file)
    buf = io.StringIO()
    pattern = ''.join(patternl)
    wordle_aid.run(pattern, buf)
    words = defaultdict(list)
    for line in buf.getvalue().splitlines():
        word = line.split()[0].lower()

        # Filter out excluded words
        if word in exclude_words:
            continue

        # Filter out words with excluded characters
        if any(w in s for w, s in zip(word, skips)):
            continue

        # If option specified, ensure is not plural
        if args.no_plural and word.endswith('s'):
            continue

        key = ''.join((c if x == '.' else '-') for c, x in zip(word, pattern))
        words[key].append(word)

    for key in sorted(words, key=lambda k: len(words[k])):
        print(' '.join(words[key]))


if __name__ == '__main__':
    sys.exit(main())
