For updated tutorial, please check the [Wiki](https://github.com/petermr/docanalysis/wiki/docanalysis-Tutorial) page.
## docanalysis 
`docanalysis` is a Command Line Tool that ingests corpora [(CProjects)](https://github.com/petermr/tigr2ess/blob/master/getpapers/TUTORIAL.md#cproject-and-ctrees) and carries out text-analysis of documents, including
- sectioning
- NLP/text-mining
- dictionary generation 

Besides the bespoke code, it uses [NLTK](https://www.nltk.org/) and other Python tools for many operations, and [spaCy](https://spacy.io/) or [scispaCy](https://allenai.github.io/scispacy/) for extraction and annotation of entities. Outputs summary data and word-dictionaries. 

### Set up `venv`
We recommend you create a virtual environment (`venv`) before installing `docanalysis` and that you activate the `venv` before each time you run `docanalysis`.

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
>> source venv/bin/activate
```

Refer the [official documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) for more help. 

### Install `docanalysis`
You can download `docanalysis` from PYPI. 
```
  pip install docanalysis
```
If you are on a Mac
```
pip3 install docanalysis
```

Download python from: [https://www.python.org/downloads/](https://www.python.org/downloads/) and select the option `Add Python to Path while installing`. Make sure `pip` is installed along with python. Check out [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/) if you have difficulties installing pip.

### Run `docanalysis`
`docanalysis --help` should list the flags we support and their use.

```
usage: docanalysis.py [-h] [--run_pygetpapers] [--make_section] [-q QUERY] [-k HITS] [--project_name PROJECT_NAME] [-d DICTIONARY] [-o OUTPUT]
                      [--make_ami_dict MAKE_AMI_DICT] [--search_section [SEARCH_SECTION [SEARCH_SECTION ...]]] [--entities [ENTITIES [ENTITIES ...]]]
                      [--spacy_model SPACY_MODEL] [--html HTML] [--synonyms SYNONYMS] [--make_json MAKE_JSON] [--search_html] [--extract_abb EXTRACT_ABB]
                      [-l LOGLEVEL] [-f LOGFILE]

Welcome to docanalysis version 0.1.3. -h or --help for help

optional arguments:
  -h, --help            show this help message and exit
  --run_pygetpapers     [Command] downloads papers from EuropePMC via pygetpapers
  --make_section        [Command] makes sections; requires a fulltext.xml in CTree directories
  -q QUERY, --query QUERY
                        [pygetpapers] query string
  -k HITS, --hits HITS  [pygetpapers] number of papers to download
  --project_name PROJECT_NAME
                        CProject directory name
  -d DICTIONARY, --dictionary DICTIONARY
                        [file name/url] existing ami dictionary to annotate sentences or support supervised entity extraction
  -o OUTPUT, --output OUTPUT
                        outputs csv with sentences/terms
  --make_ami_dict MAKE_AMI_DICT
                        [Command] title for ami-dict. Makes ami-dict of all extracted entities; works only with spacy
  --search_section [SEARCH_SECTION [SEARCH_SECTION ...]]
                        [NER/dictionary search] section(s) to annotate. Choose from: ALL, ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY, MET, RES, TAB, TIL. Defaults to
                        ALL
  --entities [ENTITIES [ENTITIES ...]]
                        [NER] entities to extract. Default (ALL). Common entities SpaCy: GPE, LANGUAGE, ORG, PERSON (for additional ones check: ); SciSpaCy: CHEMICAL,
                        DISEASE
  --spacy_model SPACY_MODEL
                        [NER] optional. Choose between spacy or scispacy models. Defaults to spacy
  --html HTML           outputs html with sentences/terms
  --synonyms SYNONYMS   annotate the corpus/sections with synonyms from ami-dict
  --make_json MAKE_JSON
                        outputs json with sentences/terms
  --search_html         searches html documents (mainly IPCC)
  --extract_abb EXTRACT_ABB
                        [Command] title for abb-ami-dict. Extracts abbreviations and expansions; makes ami-dict of all extracted entities
  -l LOGLEVEL, --loglevel LOGLEVEL
                        provide logging level. Example --log warning <<info,warning,debug,error,critical>>, default='info'
  -f LOGFILE, --logfile LOGFILE
                        saves log to specified file in output directory as well as printing to terminal
```

#### Download papers from [EPMC](https://europepmc.org/) via `pygetpapers`
COMMAND
```
docanalysis --run_pygetpapers -q "terpene" -k 10 --project_name terpene_10
```
LOGS
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
COMMAND
```
docanalysis --project_name terpene_10 --make_section
```
LOGS
```
WARNING: Making sections in /content/terpene_10/PMC9095633/fulltext.xml
INFO: dict_keys: dict_keys(['abstract', 'acknowledge', 'affiliation', 'author', 'conclusion', 'discussion', 'ethics', 'fig_caption', 'front', 'introduction', 'jrnl_title', 'keyword', 'method', 'octree', 'pdfimage', 'pub_date', 'publisher', 'reference', 'results_discuss', 'search_results', 'sections', 'svg', 'table', 'title'])
WARNING: loading templates.json
INFO: wrote XML sections for /content/terpene_10/PMC9095633/fulltext.xml /content/terpene_10/PMC9095633/sections
WARNING: Making sections in /content/terpene_10/PMC9120863/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9120863/fulltext.xml /content/terpene_10/PMC9120863/sections
WARNING: Making sections in /content/terpene_10/PMC8982386/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC8982386/fulltext.xml /content/terpene_10/PMC8982386/sections
WARNING: Making sections in /content/terpene_10/PMC9069239/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9069239/fulltext.xml /content/terpene_10/PMC9069239/sections
WARNING: Making sections in /content/terpene_10/PMC9165828/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9165828/fulltext.xml /content/terpene_10/PMC9165828/sections
WARNING: Making sections in /content/terpene_10/PMC9119530/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9119530/fulltext.xml /content/terpene_10/PMC9119530/sections
WARNING: Making sections in /content/terpene_10/PMC8982077/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC8982077/fulltext.xml /content/terpene_10/PMC8982077/sections
WARNING: Making sections in /content/terpene_10/PMC9067962/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9067962/fulltext.xml /content/terpene_10/PMC9067962/sections
WARNING: Making sections in /content/terpene_10/PMC9154778/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9154778/fulltext.xml /content/terpene_10/PMC9154778/sections
WARNING: Making sections in /content/terpene_10/PMC9164016/fulltext.xml
INFO: wrote XML sections for /content/terpene_10/PMC9164016/fulltext.xml /content/terpene_10/PMC9164016/sections
 47% 1056/2258 [00:01<00:01, 1003.31it/s]ERROR: cannot parse /content/terpene_10/PMC9165828/sections/1_front/1_article-meta/26_custom-meta-group/0_custom-meta/1_meta-value/0_xref.xml
 67% 1516/2258 [00:01<00:00, 1047.68it/s]ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/7_xref.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/14_email.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/3_xref.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/6_xref.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/9_email.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/10_email.xml
ERROR: cannot parse /content/terpene_10/PMC9119530/sections/1_front/1_article-meta/24_custom-meta-group/0_custom-meta/1_meta-value/4_xref.xml
...
100% 2258/2258 [00:02<00:00, 949.43it/s] 
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
##### Search sections using dictionary
COMMAND
```
docanalysis --project_name terpene_10 --output entities.csv --make_ami_dict entities.xml
```
LOGS
```
INFO: Found 7134 sentences in the section(s).
INFO: getting terms from /content/activity.xml
100% 7134/7134 [00:02<00:00, 3172.14it/s]
/usr/local/lib/python3.7/dist-packages/docanalysis/entity_extraction.py:352: FutureWarning: The default value of regex will change from True to False in a future version. In addition, single character regular expressions will *not* be treated as literal strings when regex=True.
  "[", "").str.replace("]", "")
INFO: wrote output to /content/terpene_10/activity.csv
```

#### Extract entities
We use `spacy` to extract Named Entites. Here's the list of Entities it supports:CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW,LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART 
INPUT
```
docanalysis --project_name terpene_10 --make_section --spacy_model spacy --entities ORG --output org.csv
```
LOGS
```
INFO: Found 7134 sentences in the section(s).
INFO: Loading spacy
100% 7134/7134 [01:08<00:00, 104.16it/s]
/usr/local/lib/python3.7/dist-packages/docanalysis/entity_extraction.py:352: FutureWarning: The default value of regex will change from True to False in a future version. In addition, single character regular expressions will *not* be treated as literal strings when regex=True.
  "[", "").str.replace("]", "")
INFO: wrote output to /content/terpene_10/org.csv
```
##### Extract information from specific section(s)
You can choose to extract entities from specific sections

COMMAND
```
docanalysis --project_name terpene_10 --make_section --spacy_model spacy --search_section AUT, AFF --entities ORG --output org_aut_aff.csv
```
LOG
```
INFO: Found 28 sentences in the section(s).
INFO: Loading spacy
100% 28/28 [00:00<00:00, 106.66it/s]
/usr/local/lib/python3.7/dist-packages/docanalysis/entity_extraction.py:352: FutureWarning: The default value of regex will change from True to False in a future version. In addition, single character regular expressions will *not* be treated as literal strings when regex=True.
  "[", "").str.replace("]", "")
INFO: wrote output to /content/terpene_10/org_aut_aff.csv
```
#### Create dictionary of extracted entities
COMMAND
```
docanalysis --project_name terpene_10 --make_section --spacy_model spacy --search_section AUT, AFF --entities ORG --output org_aut_aff.csvv --make_ami_dict org
```
LOG
```
INFO: Found 28 sentences in the section(s).
INFO: Loading spacy
100% 28/28 [00:00<00:00, 96.56it/s] 
/usr/local/lib/python3.7/dist-packages/docanalysis/entity_extraction.py:352: FutureWarning: The default value of regex will change from True to False in a future version. In addition, single character regular expressions will *not* be treated as literal strings when regex=True.
  "[", "").str.replace("]", "")
INFO: wrote output to /content/terpene_10/org_aut_aff.csvv
INFO: Wrote all the entities extracted to ami dict
```

Snippet of the dictionary
```
<?xml version="1.0"?>
- dictionary title="/content/terpene_10/org.xml">
<entry count="2" term="Department of Biochemistry"/>
<entry count="2" term="Chinese Academy of Agricultural Sciences"/>
<entry count="2" term="Tianjin University"/>
<entry count="2" term="Desert Research Center"/>
<entry count="2" term="Chinese Academy of Sciences"/>
<entry count="2" term="University of Colorado Boulder"/>
<entry count="2" term="Department of Neurology"/>
<entry count="1" term="Max Planck Institute for Chemical Ecology"/>
<entry count="1" term="College of Forest Resources and Environmental Science"/>
<entry count="1" term="Michigan Technological University"/>
```

### Extract Abbreviations

```
docanalysis --project_name corpus\ethics_10 --output dict_search_5.csv  --make_json dict_search_5.json --make_ami_dict entities --extract_abb ethics_abb
```

`--extract_abb` extracts all abbreviations and make an ami-dictionary of abbreviations and its expansion. 

EXAMPLE DICTIONARY: 
```
<dictionary title="ethics_abb">
  <entry name="ASD" term="Atrial septal defect"/>
  <entry name="SPSS" term="Statistical Package for Social Sciences"/>
  <entry name="ACGME" term="Accreditation Council of Graduate Medical Education"/>
  <entry name="ABP" term="American Board of Paediatrics"/>
  <entry name="TBL" term="Team Based Learning"/>
  <entry name="TBL" term="Team-Based Learning"/>
  <entry name="UNTH" term="University of Nigeria Teaching Hospital"/>
  <entry name="PAH" term="pulmonary hypertension"/>
  <entry name="HREC" term="Human Sciences Research Council, Research Ethics Committee"/>
  <entry name="HREC" term="Human Sciences Research Council, Research Ethics Committee"/>
  <entry name="CDC" term="Center for Disease Control and Prevention"/>
  <entry name="ASD" term="Atrial septal defect"/>
  <entry name="PAH" term="pulmonary arterial hypertension"/>
  <entry name="CVDs" term="cardiovascular diseases"/>
  <entry name="BNs" term="Bayesian networks"/>
  <entry name="GI" term="gastrointestinal cancer"/>
  <entry name="ART" term="antiretroviral therapy"/>
  <entry name="HIV" term="human immunodeficiency virus"/>
  <entry name="GATE" term="Global Cooperation on Assistive Technology"/>
</dictionary>
```

### Search HTML
If you working with HTML files (IPCC Reports, for example) and not XMLs in CProjects, you can use `--search_html` flag.

```
docanalysis --project_name corpus\ipcc_sectioned  --extract_abb ethics_abb --search_html
```

 Make sure that your `html` sections is in `sections` folder. Here's an example structure: 

```
C:.
|   dict_search_2.csv
|   dict_search_2.json
|
\---chap4
    |   chapter_4
    |
    \---sections
            4.1.html
            4.2.1.html
            4.2.2.html
            4.2.3.html
            4.2.4.html
            4.2.5.html
            4.2.7.html
            4.2.html
            4.3.1.html
            4.3.2.html
            4.3.html
            4.4.1.html
            4.4.2.html
            4.4.html
            4.5.html
            executive_summary.html
            frequently_asked_questions.html
            table_of_contents.html
```
If you haven't sectioned your `html`, please use `py4ami` to section it.  
#### What is a dictionary
Dictionary, in `ami`'s terminology, a set of terms/phrases in XML format. 
Dictionaries related to ethics and acknowledgments are available in [Ethics Dictionary](https://github.com/petermr/docanalysis/tree/main/ethics_dictionary) folder

If you'd like to create a custom dictionary, you can find the steps, [here](https://github.com/petermr/tigr2ess/blob/master/dictionaries/TUTORIAL.md)

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


