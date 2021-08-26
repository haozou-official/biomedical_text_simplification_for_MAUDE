# Text Simplification for Leadless Pacemaker Failure Reports in MAUDE

## Instructions

### Dependencies
* Python 3.6

### Pulling data from MAUDE
PLEASE NOTE: Data has already been pulled from MAUDE and preprocessed. See Download data below.
<ol type="1">
  <li>Run pull_data.py to retrieve data using the openFDA api (https://open.fda.gov/) from the MAUDE medical device adverse event database.</li>
    
    python3 pull_data.py [-h] [-l] [-n] product_code start_date end_date
    
  <li>Supply the following positional arguments</li>
    <ol type="i">
      <li>product_code (the FDA product code corresponding to device type)</li>
      <li>start_date (start date in YYYYMMDD format)</li>
      <li>end_date  (end date in YYYYMMDD format)</li>
    </ol>
</ol>



### Neural Text Simplification (OpenNMT)
(Based on instructions from [Neural Text Simplification](https://github.com/senisioi/NeuralTextSimplification))
<ol type="1">
  <li>OpenNMT dependencies</li>
  <ol type="i">
    <li>Install Torch</li>
    <li>Install additional packages:</li>
    
    luarocks install tds
        
  </ol>
  <li>Download data</li>
  <ol type="i">
    <li>[Google drive](https://drive.google.com/file/d/1ozGBwod4wnl7BsRDlFjPrXZxverhIN3f/view?usp=sharing)</li>
    <li>Unzip and insert data into NeuralTextSimplification directory</li>
    <li>Check to make sure it contains [dev.en, dev.sen, train.en, train.sen, test.en, test.sen]</li>
  </ol>
  
  <li>Download model</li>
  <ol type="i">
    <li>[Google drive](https://drive.google.com/file/d/1fd2aDMt-6oZAmqEM6yJHuSMQ5u6rrDJW/view?usp=sharing)</li>
  <li>Create models directory in NeuralTextSimplification/ and move model there</li>
  </ol>

  <li>Run mid_translate.sh from the scripts directory</li>
  <ol type="i">
    <li>Make sure MODEL_PATH matches the model path</li>
    <li>Run script</li>

    cd src/scripts
    ./mid_translate.sh
    
  </ol>
    
  <li>Check the predictions in the results directory:</li>
  
    cd ../../results_NTS  
  
  <li>Move results from results_NTS directory into predictions directory (needs to be unzipped)</li>
  
  <li>Move preferred model from OpenNMT directory to models directory</li>

  <li>Run automatic evaluation metrics</li>
  <ol type="i">
    <li>Install the python requirements (only nltk is needed) within the Neural Text Simplification directory</li>
  
    pip3 install -r src/requirements.txt
    
   <li>Run SARI/BLEU evaluation script within the Neural Text Simplification directory</li>
    
    python3 src/evaluate.py ./data/test.en ./data/references/references.tsv ./predictions/ 
    
   <li>Run Flesch-Kincaid script at the root level. test_fk.txt is the name of the output file, so it's okay if the file doesn't exist yet.</li>
    
    python3 apply_FK.py NeuralTextSimplification/data/references/test.en test_fk.txt -t NeuralTextSimplification/predictions/[prediction file]
  </ol>
</ol>

### Controllabel Sentence Simplification (Fairseq)
Based on instructions from [Controllable Sentence Simplification](https://github.com/facebookresearch/access).
#### Getting Started

#### Installing

```
git clone git@github.com:facebookresearch/access.git
cd access
pip install -e .
pip install --force-reinstall easse@git+git://github.com/feralvam/easse.git@580ec953e4742c3ae806cc85d867c16e9f584505
pip install --force-reinstall fairseq@git+https://github.com/louismartin/fairseq.git@controllable-sentence-simplification

pip install torch==1.2
pip install sacrebleu==1.3.7
```
#### How to use

Download the dataset that has been pre-processed, you can use any other "complex" dataset to simplify.

[Dataset we used](https://drive.google.com/file/d/1qbHh6DWp91e2h59tovg945a9EA4jvhFm/view?usp=sharing)

Simplify text with the pretrained model
```
python scripts/generate.py < my_file_complex.txt
```
Evaluate the model performence:
```
bash scripts/evaluate.sh
```

Train a model ***(you don't necessary have to run this script for our project)***
```
python scripts/train.py
```

