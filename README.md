### docanalysis 
 Ingests [CProjects](https://github.com/petermr/tigr2ess/blob/master/getpapers/TUTORIAL.md#cproject-and-ctrees) and carries out text-analysis of documents, including sectioning, NLP/text-mining, vocabulary generation. Uses NLTK and other Python tools for many operations, and [spaCy](https://spacy.io/) or [scispaCy](https://allenai.github.io/scispacy/) for extraction and annotation of entities. Outputs summary data and word-dictionaries. 
 
### Set up `venv`
We recommend you set up a virtual environment before installing and running `docanalysis`

Windows
```
mkdir docanalysis_demo
cd docanalysis_demo
python -m venv venv
venv\Scripts\activate.bat
```

### Install `docanalysis`
Make sure `pip` is installed along with python. Download python from: [https://www.python.org/downloads/](https://www.python.org/downloads/) and select the option `Add Python to Path while installing`. Check out [https://pip.pypa.io/en/stable/installing/](https://pip.pypa.io/en/stable/installing/) if difficulties installing pip.

#### Method One (recommended)
- Run  `pip install docanalysis`
-   To make sure  `docanalysis`  has been installed by reopening the terminal and typing the command `docanalysis`. You should see a help message come up.
    
#### Method 2
-   Manually clone the repository and run `python setup.py install` from inside the repository directory
-   To make sure  `docanalysis`  has been installed by reopening the terminal and typing the command `docanalysis`. You should see a help message come up.

### How to run
Run `docanalysis --help` to get a list of flags and their usage

```
usage: docanalysis [-h] [--run_pygetpapers] [--run_sectioning] [-q QUERY] [-k HITS] [--project_name PROJECT_NAME]
                   [-d DICTIONARY] [-o OUTPUT] [--make_ami_dict MAKE_AMI_DICT] [-l LOGLEVEL] [-f LOGFILE]

Welcome to Docanalysis version 0.0.7. -h or --help for help

optional arguments:
  -h, --help            show this help message and exit
  --run_pygetpapers     queries EuropePMC via pygetpapers
  --run_sectioning      make sections
  -q QUERY, --query QUERY
                        query to pygetpapers
  -k HITS, --hits HITS  numbers of papers to download from pygetpapers
  --project_name PROJECT_NAME
                        name of CProject folder
  -d DICTIONARY, --dictionary DICTIONARY
                        Ami Dictionary to tag sentences and support supervised entity extraction
  -o OUTPUT, --output OUTPUT
                        Output CSV file [default=entities.csv]
  --make_ami_dict MAKE_AMI_DICT
                        if provided will make ami dict with given title
  -l LOGLEVEL, --loglevel LOGLEVEL
                        [All] Provide logging level. Example --log warning <<info,warning,debug,error,critical>>,
                        default='info'
  -f LOGFILE, --logfile LOGFILE
                        [All] save log to specified file in output directory as well as printing to terminal
```

#### Download open papers via `pygetpapers`
```
docanalysis --run_pygetpapers -q "terpene" -k 10 --project_name terpene_10
```
#### Section the papers
```
docanalysis --project_name terpene_10 --run_sectioning
```
#### Extract entities
```
docanalysis --project_name terpene_10 --output entities_202202019 --make_ami_dict entities_20220209
```
#### Create dictionary
```
docanalysis --project_name terpene_10 --output entities_202202019 --make_ami_dict entities_20220209
```
#### All at one go!
```
docanalysis --run_pygetpapers -q "terpene" -k 10 --project_name terpene_10 --run_sectioning --output entities_202202019 --make_ami_dict entities_20220209 
```
### Tools used
- [`pygetpapers`](https://github.com/petermr/pygetpapers) - scrape open repositories to download papers of interest
- [nltk](https://www.nltk.org/) - splits sentences
- [spaCy](https://spacy.io/) - recognize Named-Entities and label them
    - Here's the list of NER labels [SpaCy's English model](https://spacy.io/models/en) provides:  
     `CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART`
    - In most of our projects (Ethics Statements and Acknowledgements Mining), we are mainly interested in GPE (Geopolitical Entities), ORG (Organization)
 - [SciSpaCy](https://allenai.github.io/scispacy/)

#### TODO list
- 2022-03-07: https://github.com/petermr/petermr/discussions/12#discussioncomment-2307963

#### Issues

## What is a dictionary

Dictionary, in `ami`'s terminology, a set of terms/phrases in XML format. 
Dictionaries related to ethics and acknowledgments are available in [Ethics Dictionary](https://github.com/petermr/docanalysis/tree/main/ethics_dictionary) folder

If you'd like to create a custom dictionary, you can find the steps, [here](https://github.com/petermr/tigr2ess/blob/master/dictionaries/TUTORIAL.md)

## Credits: 
[Daniel Mietchen](https://github.com/Daniel-Mietchen), [Peter Murray-Rust](https://github.com/petermr), [Ayush Garg](https://github.com/ayush4921), [Shweata N. Hegde](https://github.com/ShweataNHegde/)

## Research Idea
