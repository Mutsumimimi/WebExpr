#!/usr/bin/bash
./main-1.py
./generate_filelist.py
./tokenize.sh
./filter_words.py
./normalize.py
./remove_stopwd.py