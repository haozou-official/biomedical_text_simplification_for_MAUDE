# Controllable Sentence Simplification

This repository is the original implementation of the ACCESS model (**A**udien**C**e-**CE**ntric **S**entence **S**implification)  presented in [Controllable Sentence Simplification](https://arxiv.org/abs/1910.02677).

### Dependencies

* Python 3.6

### Installing

```
git clone git@github.com:facebookresearch/access.git
cd access
pip install -e .
pip install --force-reinstall easse@git+git://github.com/feralvam/easse.git@580ec953e4742c3ae806cc85d867c16e9f584505
pip install --force-reinstall fairseq@git+https://github.com/louismartin/fairseq.git@controllable-sentence-simplification

pip install torch==1.2
pip install sacrebleu==1.3.7
```

### How to use

Download the dataset that has been pre-processed, you can use any other "complex" dataset to simplify.

[Dataset we used](https://drive.google.com/file/d/1qbHh6DWp91e2h59tovg945a9EA4jvhFm/view?usp=sharing)

Simplify text with the pretrained model
```
python scripts/generate.py < my_file.complex
```

Evaluate the model performence:
```
bash scripts/evaluate.sh
```

Train a model ***(you don't necessary have to run this script for our project)***
```
python scripts/train.py
```

## Pretrained model

The fairseq checkpoint of our model with the best scores can be found [here](http://dl.fbaipublicfiles.com/access/best_model.tar.gz).

## References

If you use this code, please cite:  
L. Martin, B. Sagot, E. De la Clergerie, A. Bordes, [*Controllable Sentence Simplification*](https://arxiv.org/abs/1910.02677)

## Author

If you have any question, please contact the author:
**Louis Martin** ([louismartincs@gmail.com](mailto:louismartincs@gmail.com))

## License

See the [LICENSE](LICENSE) file for more details.
