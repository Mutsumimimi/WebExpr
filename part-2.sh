#!/usr/bin/bash
SRC_PATH="src/part-2"
python ${SRC_PATH}/main-1.py
python ${SRC_PATH}/generate_filelist.py
./tokenize.sh
# python ${SRC_PATH}/mytokenize.py
python ${SRC_PATH}/filter_words.py
python ${SRC_PATH}/normalize.py
python ${SRC_PATH}/remove_stopwd.py