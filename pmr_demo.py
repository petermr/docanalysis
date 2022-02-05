import os
from docanalysis import DocAnalysis
from pathlib import Path

ethic_statement_creator = DocAnalysis()
term_dir = Path(os.getcwd(), "terpenes_dictionary", "terpenes_key_phrases", )
if not term_dir.exists():
    term_dir.mkdir()
dict_for_entities = ethic_statement_creator.extract_entities_from_papers(
    corpus_path=Path(os.getcwd(), "corpus", "terpenes", ),
    terms_xml_path=Path(term_dir, "terpenes_key_phrases.xml"),
    query="terpenes",
    hits=10,
    make_project=True
)
print(f"dict {dict_for_entities}")
list_with_orgs = ethic_statement_creator.extract_particular_fields(
    dict_for_entities, 'ORG')
with open('org.text', 'w') as f:
    f.write(str(list_with_orgs))
list_with_gpe = ethic_statement_creator.extract_particular_fields(
    dict_for_entities, 'GPE')
with open('GPE.text', 'w') as f:
    f.write(str(list_with_gpe))

