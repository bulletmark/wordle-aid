## WORDLE-AID
[![PyPi](https://img.shields.io/pypi/v/wordle-aid)](https://pypi.org/project/wordle-aid/)
[![AUR](https://img.shields.io/aur/version/wordle-aid)](https://aur.archlinux.org/packages/wordle-aid/)

[wordle-aid](http://github.com/bulletmark/wordle-aid) is a Linux command
line program to filter word choices to aid solving
[Wordle](https://www.powerlanguage.co.uk/wordle/) problems. You run this
program specifying your previous guesses and results, and then the
program outputs a list of candidate words in English frequency usage
order to your terminal.

The following example Wordle (#21) solution illustrates how to use it.

![wordle solution](https://github.com/bulletmark/wordle-aid/raw/main/wordle-example.png)

1. Choose any starting word as normal. You can even use `wordle-aid` to
   help with this, e.g.

    ```
    # print all 5 letter words, in reverse frequency order to screen:
    $ wordle-aid .....

    # Or, print all 5 letter words with at least 3 vowels:
    $ wordle-aid -v3 .....

    # Or, print all 5 letter words with at least 3 vowels and all unique letters:
    $ wordle-aid -v3 -u .....
    ```

2. We choose our favorite starting word **TRACE** as the first guess,
   which gives the result shown on the first line of the image above.
   Based on this result, run:

    ```
    $ wordle-aid TracE ..a..
    ...
    feast 4166016
    yeast 6083904
    heath 6139151
    dealt 6174968
    beats 6367861
    beast 14787561
    seats 17070818
    meant 17832930
    death 83216831
    least 111229798
    ```

   The output above is the list of possible candidate words, given the
   command line word arguments you have specified.

   Note: Specify the 1st guess word you used and set each yellow (i.e.
   correct but incorrect position) letter to upper-case, and other
   letters to lower-case. Specify all green (i.e. correct and in
   position) letters you have found so far in the right (wildcard) field
   in their correct position.

3. Choose a word from the suggestion list output from above command. We
   choose to enter the highest frequency candidate **LEAST** from the
   list, which gives the result shown on the second line in the the
   image above. Then run:

    ```
    $ wordle-aid TracE leasT .ea..
    ...
    beata 134085
    beatz 158324
    keath 158670
    neato 182680
    beaty 209357
    meaty 395095
    neath 571177
    meath 773366
    heath 6139151
    death 83216831
    ```

4. Choose a word from the suggestion list output from the above command.
   We choose to enter the highest frequency result **DEATH**, which
   gives us the final correct answer.

In summary, specify `.....` (all wildcards) as your starting result and
insert characters to it as your find them, i.e. all green letters from
each guess. Note that the number of wildcard characters determines the
Wordle game word size (e.g. `wordle-aid bundle ......` for a 6 letter
game). Specify your previous word guesses earlier on the command line.
They don't actually have to be in the order that you guessed them
although likely you will be re-editing from your command history so they
will be. Yellow letter guesses (i.e. letter valid but in incorrect
place) are entered as upper case, and dark/grey letter guesses (i.e.
letter not present anywhere) are entered as lower case. Green letters
(i.e. letter valid and in correct place) can be lower or upper case in
the earlier word arguments, but **must** be specified in the final
wildcard word (as either lower or upper case) .

### Word Dictionary

Wordle-aid embeds a copy of the [Kaggle English Word
Frequency](https://www.kaggle.com/rtatman/english-word-frequency) CSV
file which contains about 333 thousand of the most common english words
on the web. You can use an alternative file using the `-d/--dictfile`
option.

Or, you can choose to install the Python Spell Checker package
[pyspellchecker](https://pyspellchecker.readthedocs.io/) and use it as
the source of words by specifying `-d/--dictfile=pyspellchecker`.

You can make the alternative file (or `pyspellchecker`) your default by
specifing `--dictfile` as a [default starting
option](#default-command-arguments).

## Installation or Upgrade

Arch users can install [wordle-aid from the
AUR](https://aur.archlinux.org/packages/wordle-aid/).

Python 3.7 or later is required. Note [wordle-aid is on
PyPI](https://pypi.org/project/wordle-aid/) so just ensure that
`python3-pip` and `python3-wheel` are installed then type the following
to install (or upgrade):

```
$ sudo pip3 install -U wordle-aid
```

Or, to install from this source repository:

```
$ git clone http://github.com/bulletmark/wordle-aid
$ cd wordle-aid
$ sudo pip3 install -U .
```

To upgrade from the source repository:

```
$ cd wordle-aid # i.e. to git source dir above
$ git pull
$ sudo pip3 install -U .
```

Wordle-aid runs on pure Python. No 3rd party packages are required.

## Command Line Options

Type `wordle-aid -h` to view the following usage summary:

```
usage: wordle-aid [-h] [-d DICTFILE] [-v VOWELS] [-u] words [words ...]

CLI program to filter word choices to aid solving Wordle game problems.

positional arguments:
  words                 list of attempted words. Upper case letter is right
                        letter but wrong place. Lower case letter is wrong
                        letter anywhere. Last word is wildcards for current
                        matches.

options:
  -h, --help            show this help message and exit
  -d DICTFILE, --dictfile DICTFILE
                        alternative dictionary+frequency text file, default =
                        /usr/share/wordle-aid/words.txt. Or can specify
                        "pyspellchecker" if you also install that package.
  -v VOWELS, --vowels VOWELS
                        exclude words with less than this number of unique
                        vowels
  -u, --unique          exclude words with non-unique letters

Note you can set default starting arguments in your ~/.config/wordle-aid-
flags.conf.
```

## Default Command Arguments

You can add default arguments to a personal configuration file
`~/.config/wordle-aid-flags.conf`. If that file exists then each line of
arguments will be concatenated and automatically prepended to your
`wordle-aid` command line arguments. You may want to use this to specify
`--dictfile` to use a different default word dictionary file.

## License

Copyright (C) 2022 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.

<!-- vim: se ai syn=markdown: -->
