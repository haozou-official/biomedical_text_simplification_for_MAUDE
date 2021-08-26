#!/bin/bash

DATA=data
PRED=results/my_simplified.txt

python evaluate.py $DATA/my_complex.txt $DATA/my_references.txt $PRED
