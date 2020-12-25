# Text transformation with Hypernymization with Spacy

## 1. Prerequire

```bash
# create conda env
conda create -n myenv python=3.6
conda activate myenv

# set tuna source
(myenv) pip install pip -U
(myenv) pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# modules & models install
(myenv) pip install nltk
(myenv) pip install spacy
(myenv) python -m spacy download en_core_web_lg

# Optional
(myenv) pip install jupyter
```

## 2. Usage

**Quick Start**

```python
from hypernymizer import Hypernmizer

alt_text = "Harrison Ford and Calista Flockhart attend the premiere of 'Hollywood Homicide' at the 29th American Film Festival September 5, 2003 in Deauville, France."

hyper = Hypernmizer()
res = hyper.transform(hyper)
```

## 3. Results

**Test Examples**

```bash
(myenv) python hypernymizer.py
```

Check the results in `results.txt`.
