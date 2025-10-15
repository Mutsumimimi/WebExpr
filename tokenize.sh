#!/usr/bin/bash
cd /home/ubuntu/Document/WebExpr/stanford-corenlp-4.5.10
# java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize -file ../test.copy -outputDirectory ../ -outputFormat "conll" -output.columns word

export FILELIST_PATH="/home/ubuntu/Document/WebExpr/filelist.txt"
export OUTPUT_PATH="/home/ubuntu/Document/WebExpr/output_data"
java -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -annotators tokenize -fileList "${FILELIST_PATH}" -outputDirectory "${OUTPUT_PATH}" -outputFormat "conll" -output.columns word
