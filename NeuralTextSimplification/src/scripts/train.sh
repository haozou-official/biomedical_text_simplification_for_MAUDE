#!/bin/bash
source ./base_conf.sh

cd $OPENNMT_PATH

th train.lua -data ${DIRECTORY}/NTS-train.t7 -save_model risako -log_file ${DIRECTORY}/log.txt 
#-save_data ${DIRECTORY}/${TRAIN_OUT} -src_seq_length 80 -tgt_seq_length 80  -shuffle 1 -log_file ${DIRECTORY}/${TRAIN_OUT}.log -src_vocab_size 50000 -tgt_vocab_size 50000 -log_level DEBUG


cd $CWD

