# docanalysis
Unsupervised entity extraction from sections of papers that have defined boilerplates. Examples of such sections include - Ethics Statements, Funders, Acknowledgments, and so on. 
\
## Purpose
### Primary Purpose
- Extracting Ethics Committees and other entities related to Ethics Statements from papers
- Curating the extracted entities to public databases like Wikidata
- Building a feedback loop where we go from unsupervised entity extraction to curating the extracted information in public repositories to then, supervised entity extraction.  

### Subsidary Purpose(s)
The use case can go beyond Ethics Statements. `docanalysis` is a general package that can extract relevant entities from the section of your interest.

Sections like Acknowledgements, Data Availability Statements, etc., all have a fairly generic sentence structure. All you have to do is create an `ami` dictionary that contains boilerplates of the section of your interest. You can, then, use `docanalysis` to extract entities. Check this section [dictionaries](https://github.com/petermr/docanalysis#What is-a-dictionary) which outlines steps for creating custom dictionaries. In case of acknowledgements or funding, you might be interested in the players involved. Or you might have a use-case which we might have never thought of!
## Installation 

`pip install docanalysis`


## Tools Used and their purpose
- [`pygetpapers`](https://github.com/petermr/pygetpapers) - scrape repositories to download papers of interest
- [`ami`](https://github.com/petermr/ami3) - section the papers
- [nltk](https://www.nltk.org/) - split sentence
- [spaCy](https://spacy.io/) - recognize Named-Entities and label them
    - Here's the list of NER labels [SpaCy's English model](https://spacy.io/models/en) provides:  
     `CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART`
    - In most of our projects (Ethics Statements and Acknowledgements Mining), we are mainly interested in GPE (Geopolitical Entities), ORG (Organization)
## Documentation

```
extract_entities_from_papers(CORPUS_PATH, TERMS_XML_PATH, QUERY=None, HITS=None, make_project=False, install_ami=False, removefalse=True, create_csv=True, csv_name='entities.csv', labels_to_get=['GPE', 'ORG'])
```

```
Parameters: CORPUS_PATH: path to an existing corpus (CProject)
            TERMS_XML_PATH: path to ami dictionary (some are in ethics dictionary folder)
            QUERY: Query set to EPMC 
            HITS: No. of papers you wish to download 
            make_project: Defaults to False. To create a new CProject using pygetpapers set it to True                          
            install_ami: installs Java ami if given True
            removefalse: removes sentences with zero matches with dictionary phrases and sentences with no Named-Entities recognized
            create_csv: creates .csv output in CORPUS_PATH. 
            csv_name:Default csv file name is `entities.csv`
            labels_to_get: SpaCy recognizes Named-Entites and labels them. You can choose for lables you are interested by providing it as a list. For all available labels, check out the Tools Used section. 
```
## How to run?
We have created `demo.py` where you can run the package. 

```
import os
from docanalysis import DocAnalysis
ethic_statement_creator = DocAnalysis()
dict_for_entities = ethic_statement_creator.extract_entities_from_papers(
    "essential oil AND chemical composition",
    100,
    os.path.join(
        os.getcwd(), "stem_cell_research_300",
    ),
    os.path.join(
        os.getcwd(), "ethics_dictionary", "ethics_key_phrases", "ethics_key_phrases.xml"
    ),
)
list_with_orgs = ethic_statement_creator.extract_particular_fields(
    dict_for_entities, 'ORG')
with open('org.text', 'w') as f:
    f.write(str(list_with_orgs))
list_with_gpe = ethic_statement_creator.extract_particular_fields(
    dict_for_entities, 'GPE')
with open('GPE.text', 'w') as f:
    f.write(str(list_with_gpe))
```
To break this down, 
|Variable snippet      |What is it?     |
|----------------------|----------------|
|`essential oil AND chemical composition` |Query to `pygetpapers` (EPMC default)|
|`100`                 |number of hits  |
|stem_cell_research_300|Output directory|
|"ethics_dictionary", "ethics_key_phrases", "ethics_key_phrases.xml"     |dictionary path |

## What is a dictionary

Dictionary, in `ami`'s terminology, a set of terms/phrases in XML format. 
Dictionaries related to ethics and acknowledgments are available in [Ethics Dictionary](https://github.com/petermr/docanalysis/tree/main/ethics_dictionary) folder

If you'd like to create a custom dictionary, you can find the steps, [here](https://github.com/petermr/tigr2ess/blob/master/dictionaries/TUTORIAL.md)

## History

History is available in [`dictionary` repository](https://github.com/petermr/dictionary/blob/main/ethics_statement_project/ethics_statement_project.md)   

Warning: The dictionary repository is messy! 

## Credits: 
[Daniel Mietchen](https://github.com/Daniel-Mietchen), [Peter Murray-Rust](https://github.com/petermr), [Ayush Garg](https://github.com/ayush4921), [Shweata N. Hegde](https://github.com/ShweataNHegde/)

## Research Idea
