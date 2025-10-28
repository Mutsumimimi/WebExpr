#!/usr/bin/bash
./main-1.py
./generate_filelist.py
./tokenize.sh
./filter_words.py
python ./normalize.py
python ./remove_stopwd.py