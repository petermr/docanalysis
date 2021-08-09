# docanalysis
Semantic analysis of text documents including sentence and paragraph splitting

## Purpose
### Primary Purpose
Extracitng Ethics Committees and other entities related to Ethics Statement. 

History is available in `dictionary` repository. 
Warning: The previous repository is messy! 

### Subsidary Purpose
We've already seen that the module can be generalized to extract entities from sentences and paragraphs as long as they have a set of controlled vocabulary. 

For example, acknowledgements, data availabilty statmement, funding all have a fairly generic sentence structure. By defining a dictionary you can use `docanalysis` to extract entities. In case of acknowledgements or funding, you might be interested in the players involved. Or you might have a use-case which we might have never thought of!
## Installation 
- Git clone the repository
```
git clone https://github.com/petermr/docanalysis.git
```
- Run `python setup.py install` from inside the repository directory

## Architecture
- `pygetpapers` - scraper
- `ami` - section the papers
- nltk - sentence splitting
- spaCy - Named-Entity Recognition
## How to run?
The entry point to run the package is `demo.py`. 


Let's look at an example. This is a copy of `demo.py`. 
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

Dictionary, in `ami`'s terminology, a set of terms 
Some dictionaries come with this repository. To create a custom dictionary, you can take a look here. 

## Credits: 
- Daniel Meitchen and Peter Murray-Rust for ideas, help and guidance
- Ayush for doing most of the heavy-listing in writing code

## Research Idea
