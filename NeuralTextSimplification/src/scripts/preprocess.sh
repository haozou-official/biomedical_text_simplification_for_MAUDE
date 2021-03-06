#!/bin/bash
source ./base_conf.sh

cd $OPENNMT_PATH

#th preprocess.lua -train_src ${DIRECTORY}/train.en -train_tgt ${DIRECTORY}/train.sen -valid_src ${DIRECTORY}/dev.en -valid_tgt ${DIRECTORY}/dev.sen -save_data ${DIRECTORY}/${DATA_OUT} -src_seq_length 80 -tgt_seq_length 80  -shuffle 1 -log_file ${DIRECTORY}/${DATA_OUT}.log -src_vocab_size 50000 -tgt_vocab_size 50000 -log_level DEBUG
th preprocess.lua -train_src ${DIRECTORY}/only_med_data/train.en -train_tgt ${DIRECTORY}/only_med_data/train.sen -valid_src ${DIRECTORY}/only_med_data/dev.en -valid_tgt ${DIRECTORY}/only_med_data/dev.sen -save_data ${DIRECTORY}/only_med_data/${DATA_OUT} -src_seq_length 80 -tgt_seq_length 80  -shuffle 1 -log_file ${DIRECTORY}/only_med_data/${DATA_OUT}.log -src_vocab_size 50000 -tgt_vocab_size 50000 -log_level DEBUG

cd $CWD

