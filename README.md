## docanalysis 
 Ingests [CProjects](https://github.com/petermr/tigr2ess/blob/master/getpapers/TUTORIAL.md#cproject-and-ctrees) and carries out text-analysis of documents, including sectioning, NLP/text-mining, vocabulary generation. Uses [NLTK](https://www.nltk.org/) and other Python tools for many operations, and [spaCy](https://spacy.io/) or [scispaCy](https://allenai.github.io/scispacy/) for extraction and annotation of entities. Outputs summary data and word-dictionaries. 

### Install `docanalysis`
You can download `docanalysis` from PYPI via `pip`. 
```
  pip install docanalysis
```
If you are on a Mac
```
pip3 install docanalysis
```

Download python from: [https://www.python.org/downloads/](https://www.python.org/downloads/) and select the option `Add Python to Path while installing`. Make sure `pip` is installed along with python. Check out [https://pip.pypa.io/en/stable/installing/](https://pip.pypa.io/en/stable/installing/) if you have difficulties installing pip.

### Run `docanalysis`
`docanalysis --help` should list the flags we support and their use.

```
usage: docanalysis.py [-h] [--run_pygetpapers] [--make_section] [-q QUERY] [-k HITS] [--project_name PROJECT_NAME]
                      [-d DICTIONARY] [-o OUTPUT] [--make_ami_dict MAKE_AMI_DICT]
                      [--search_section [SECTION [SECTION ...]]] [--entities [ENTITIES [ENTITIES ...]]]
                      [--spacy_model SPACY_MODEL] [--html HTML] [--synonyms SYNONYMS] [-l LOGLEVEL] [-f LOGFILE]

Welcome to docanalysis version 0.0.7. -h or --help for help

optional arguments:
  -h, --help            show this help message and exit
  --run_pygetpapers     downloads papers from EuropePMC via pygetpapers
  --make_section        makes sections
  -q QUERY, --query QUERY
                        provide query to pygetpapers
  -k HITS, --hits HITS  specify number of papers to download from pygetpapers
  --project_name PROJECT_NAME
                        provide CProject directory name
  -d DICTIONARY, --dictionary DICTIONARY
                        provide ami dictionary to annotate sentences or support supervised entity extraction
  -o OUTPUT, --output OUTPUT
                        outputs csv file [default=entities.csv]
  --make_ami_dict MAKE_AMI_DICT
                        provide title for ami-dict. Makes ami-dict of all extracted entities
  --search_section [SECTION [SECTION ...]]
                        provide section(s) to annotate. Choose from: ALL, ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY,
                        MET, RES, TAB, TIL. Defaults to ALL
  --entities [ENTITIES [ENTITIES ...]]
                        provide entities to extract. Default(ALL). Choose from SpaCy: CARDINAL, DATE, EVENT, FAC, GPE,
                        LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME,
                        WORK_OF_ART; SciSpaCy: CHEMICAL, DISEASE
  --spacy_model SPACY_MODEL
                        optional. Choose between spacy or scispacy models. Defaults to spacy
  --html HTML           saves output in html format to given path
  --synonyms SYNONYMS   searches the corpus/sections with synonymns from ami-dict
  -l LOGLEVEL, --loglevel LOGLEVEL
                        provide logging level. Example --log warning <<info,warning,debug,error,critical>>,
                        default='info'
  -f LOGFILE, --logfile LOGFILE
                        saves log to specified file in output directory as well as printing to terminal
```

#### Download papers from [EPMC](https://europepmc.org/) via `pygetpapers`
INPUT
```
docanalysis --run_pygetpapers -q "terpene" -k 10 --project_name terpene_10
```
OUTPUT
```
INFO: making project/searching terpene for 10 hits into C:\Users\shweata\docanalysis\terpene_10
INFO: Total Hits are 13935
1it [00:00, 936.44it/s]
INFO: Saving XML files to C:\Users\shweata\docanalysis\terpene_10\*\fulltext.xml
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10/10 [00:30<00:00,  3.10s/it]
```

CPROJ
```
C:\USERS\SHWEATA\DOCANALYSIS\TERPENE_10
│   eupmc_results.json
│
├───PMC8625850
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8727598
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8747377
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8771452
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8775117
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8801761
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8831285
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8839294
│       eupmc_result.json
│       fulltext.xml
│
├───PMC8840323
│       eupmc_result.json
│       fulltext.xml
│
└───PMC8879232
        eupmc_result.json
        fulltext.xml
```

#### Section the papers
INPUT
```
docanalysis --project_name terpene_10 --make_section
```
OUTPUT
```
WARNING: Making sections in C:\Users\shweata\docanalysis\terpene_10\PMC8625850\fulltext.xml
INFO: dict_keys: dict_keys(['abstract', 'acknowledge', 'affiliation', 'author', 'conclusion', 'discussion', 'ethics', 'fig_caption', 'front', 'introduction', 'jrnl_title', 'keyword', 'method', 'octree', 'pdfimage', 'pub_date', 'publisher', 'reference', 'results_discuss', 'search_results', 'sections', 'svg', 'table', 'title'])
WARNING: loading templates.json
INFO: wrote XML sections for C:\Users\shweata\docanalysis\terpene_10\PMC8625850\fulltext.xml C:\Users\shweata\docanalysis\terpene_10\PMC8625850\sections
WARNING: Making sections in C:\Users\shweata\docanalysis\terpene_10\PMC8727598\fulltext.xml
INFO: wrote XML sections for C:\Users\shweata\docanalysis\terpene_10\PMC8727598\fulltext.xml C:\Users\shweata\docanalysis\terpene_10\PMC8727598\sections
WARNING: Making sections in C:\Users\shweata\docanalysis\terpene_10\PMC8747377\fulltext.xml
INFO: wrote XML sections for C:\Users\shweata\docanalysis\terpene_10\PMC8747377\fulltext.xml C:\Users\shweata\docanalysis\terpene_10\PMC8747377\sections
...
```

CTREE
```
├───PMC8625850
│   └───sections
│       ├───0_processing-meta
│       ├───1_front
│       │   ├───0_journal-meta
│       │   └───1_article-meta
│       ├───2_body
│       │   ├───0_1._introduction
│       │   ├───1_2._materials_and_methods
│       │   │   ├───1_2.1._materials
│       │   │   ├───2_2.2._bacterial_strains
│       │   │   ├───3_2.3._preparation_and_character
│       │   │   ├───4_2.4._evaluation_of_the_effect_
│       │   │   ├───5_2.5._time-kill_studies
│       │   │   ├───6_2.6._propidium_iodide_uptake-e
│       │   │   └───7_2.7._hemolysis_test_from_human
│       │   ├───2_3._results
│       │   │   ├───1_3.1._encapsulation_of_terpene_
│       │   │   ├───2_3.2._both_terpene_alcohol-load
│       │   │   ├───3_3.3._farnesol_and_geraniol-loa
│       │   │   └───4_3.4._farnesol_and_geraniol-loa
│       │   ├───3_4._discussion
│       │   ├───4_5._conclusions
│       │   └───5_6._patents
│       ├───3_back
│       │   ├───0_ack
│       │   ├───1_fn-group
│       │   │   └───0_fn
│       │   ├───2_app-group
│       │   │   └───0_app
│       │   │       └───2_supplementary-material
│       │   │           └───0_media
│       │   └───9_ref-list
│       └───4_floats-group
│           ├───4_table-wrap
│           ├───5_table-wrap
│           ├───6_table-wrap
│           │   └───4_table-wrap-foot
│           │       └───0_fn
│           ├───7_table-wrap
│           └───8_table-wrap
...
```

#### Extract entities 
##### From specific section(s)
##### From all sections
##### From sentences with boilerplate phrase(s)
```
docanalysis --project_name terpene_10 --output entities.csv --make_ami_dict entities.xml
```
#### Create dictionary
```
docanalysis --project_name terpene_10 --output entities_202202019 --make_ami_dict entities_20220209
```
#### What is a dictionary
Dictionary, in `ami`'s terminology, a set of terms/phrases in XML format. 
Dictionaries related to ethics and acknowledgments are available in [Ethics Dictionary](https://github.com/petermr/docanalysis/tree/main/ethics_dictionary) folder

If you'd like to create a custom dictionary, you can find the steps, [here](https://github.com/petermr/tigr2ess/blob/master/dictionaries/TUTORIAL.md)
#### All at one go!
```
docanalysis --run_pygetpapers -q "terpene" -k 10 --project_name terpene_10 --run_sectioning --output entities_202202019 --make_ami_dict entities_20220209 
```
### Python tools used
- [`pygetpapers`](https://github.com/petermr/pygetpapers) - scrape open repositories to download papers of interest
- [nltk](https://www.nltk.org/) - splits sentences
- [spaCy](https://spacy.io/) and  [SciSpaCy](https://allenai.github.io/scispacy/)
 - recognize Named-Entities and label them
     - Here's the list of NER labels [SpaCy's English model](https://spacy.io/models/en) provides:  
     `CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART`
 
### Credits: 
-  [Ayush Garg](https://github.com/ayush4921)
-  [Shweata N. Hegde](https://github.com/ShweataNHegde/)
-  [Daniel Mietchen](https://github.com/Daniel-Mietchen)
-  [Peter Murray-Rust](https://github.com/petermr)

### Set up `venv`
We recommend you create a virtual environment (`venv`) before installing `docanalysis` and activate the `venv` every time you run `docanalysis`.

#### Windows
Creating a `venv`
```
>> mkdir docanalysis_demo
>> cd docanalysis_demo
>> python -m venv venv
```

Activating `venv`
```
>> venv\Scripts\activate.bat
```

#### MacOS
Creating a `venv`
```
>> mkdir docanalysis_demo
>> cd docanalysis_demo
>> python3 -m venv venv
```

Activating `venv`
```
>> venv\Scripts\activate.bat
```

Refer the [official documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for more help. 
