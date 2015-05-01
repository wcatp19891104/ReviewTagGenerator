#!/bin/sh
echo "building start"
echo "-----generating training data-------"
python ./Preprocess/src/PreProcess.py
echo "-----Sync Dictionary------"
cp ./Preprocess/resource/test_data.txt ./Test/resource/test_data.txt
cp ./Preprocess/resource/train_data.txt ./Model/Train/resource/train_data.txt

cp ./Preprocess/src/PostProcess/resource/ValidProTag.txt ./Model/Train/resource/validProTag.txt
cp ./Preprocess/src/PostProcess/resource/ValidProTag.txt ./Model/dictionary/ValidProTag.txt
echo "-----training data-------"
python ./Model/Train/src/Train_P_jj_tag.py
python ./Model/Train/src/Train_P_Tag.py
python ./Model/Train/src/Train_P_Type_Tag.py


echo "-----evaluation----------"
python ./Test/src/Evaluation.py
