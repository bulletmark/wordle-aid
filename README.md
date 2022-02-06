## WORDLE-AID

[wordle-aid](http://github.com/bulletmark/wordle-aid) is a Linux command
line program to filter word choices to aid solving
[Wordle](https://www.powerlanguage.co.uk/wordle/) problems. You run this
program specifying your previous guesses and results, and then the
program outputs a list of candidate words in English frequency usage
order to your terminal.

The following example Worldle solution best illustrates how to use it. 

![wordle solution](https://github.com/bulletmark/wordle-aid/raw/main/wordle-example.png)

1. Choose any starting word as normal. You can even use `wordle-aid` to
   help with this, e.g.

    ```
    # print all 5 letter words, in reverse frequency order to screen:
    wordle-aid .....

    # Or, print all 5 letter words with at least 3 vowels:
    wordle-aid -v3 .....

    # Or, print all 5 letter words with at least 3 vowels and all unique letters:
    wordle-aid -v2 -u .....
    ```

2. Enter **ARISE** as your first guess on Wordle, which gives result on first line above. Then run:

    ```
    wordle-aid aRise .....
    ```

   Note: Specify the guess word you used and set each candidate letter
   (yellow and green) to upper-case, and each non-candidate letter to lower-case.

3. Choose a word from the suggestion list output from above command.
   We choose to enter **WORLD** which gives result on second line above, then run:

    ```
    wordle-aid aRise wORld .O...
    ```

    Note: Here we have set the right-side wildcard word to include the correctly placed
    green `O` letter.

4. Choose a word from the suggestion list output from above command.
   We choose to enter **COURT** which gives result on second line above, then run:

    ```
    wordle-aid aRise wORld cOuRT .O...
    ```

5. Choose a word from the suggestion list output from above command.
   We choose to enter **MOTOR** which gives final correct answer.

In summary, specify `.....` (all wildcards) as your starting result and
insert characters to it as your find them, i.e. all green letters from
each guess. Note that the number of wildcard characters determines the
Wordle game word size (e.g. `wordle-aid arises ......` for a 6 letter
game). Specify your previous word guesses earlier on the command line.
They don't actually have to be in the order that you guessed them
although likely you will be re-editing from your command history so they
will be. Yellow letter guesses (i.e. letter valid but in incorrect
place) are entered as upper case, and dark/grey letter guesses (i.e.
letter not present anywhere) are entered as lower case. Green letters
(i.e. letter valid and in correct place) can actually be upper or lower
case in the earlier word arguments, but **must** be specified in the
final wildcard word.

Try `wordle-aid` out on the [Wordle Archive](https://www.devangthakkar.com/wordle_archive/).

### Word Dictionary

Wordle-aid embeds a copy of the [Kaggle English Word
Frequency](https://www.kaggle.com/rtatman/english-word-frequency) CSV
file which contains about 333 thousand of the most common english
words on the web. You can use an alternative file using the
`-d/--dictfile` option. You can make this alternative file your default by
specifing `--dictfile` as a [default starting
option](#default-command-arguments).

## Installation or Upgrade

Arch users can install [wordle-aid from the
AUR](https://aur.archlinux.org/packages/wordle-aid/).

Python 3.6 or later is required. Note [wordle-aid is on
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

```
usage: wordle-aid [-h] [-d DICTFILE] [-v VOWELS] [-u] words [words ...]

CLI program to filter word choices to aid solving Wordle.

positional arguments:
  words                 list of attempted words. Upper case letter is right
                        letter but wrong place. Lower case letter is wrong
                        letter anywhere. Last word is wildcards for current
                        matches.

options:
  -h, --help            show this help message and exit
  -d DICTFILE, --dictfile DICTFILE
                        alternative dictionary+frequency text file, default =
                        /usr/share/wordle-aid/words.txt.
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
