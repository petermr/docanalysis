import os
from docanalysis import DocAnalysis
from pathlib import Path

doc_analysis = DocAnalysis()
ETHICS_DICTIONARY_DIR = Path(os.getcwd(), "ethics_dictionary")
CORPUS_DIR =  Path(os.getcwd(), "corpus")


def create_phrases_file(phrases_dir, phrases_file, dictionary_dir=ETHICS_DICTIONARY_DIR):
    global terms_xml_path
    terms_xml_dir = Path(dictionary_dir, phrases_dir)
    if not terms_xml_dir.exists():
        terms_xml_dir.mkdir()
    terms_xml_path = Path(terms_xml_dir, phrases_file)


def get_or_create_corpus_dir(subdir_name, corpus_dir=CORPUS_DIR):
    """get specific corpus directory, creating if necessary

    :param corpus_dir: directory containing corpora
    :param subdir_name: specific corpus to get or create
    :return: directoyr of specific corpus"""
    assert corpus_dir.exists(), "directory of corpora must exist"
    subdir = Path(corpus_dir, subdir_name)
    if not subdir.exists():
        subdir.mkdir()
    return subdir


corpus_path = get_or_create_corpus_dir("e_cancer_clinical_trial_50")
phrases_file = create_phrases_file("ethics_key_phrases", "ethics_key_phrases.xml")


def run_analysis(corpus_path, phrases_file):
    dict_for_entities = doc_analysis.extract_entities_from_papers(
        corpus_path=corpus_path,
        terms_xml_path=terms_xml_path,
    )
    print(f"dict {dict_for_entities}")
    create_and_write_list_for_fields(dict_for_entities, "ORG", "org.text")
    create_and_write_list_for_fields(dict_for_entities, "GPE", "GPE.text")


def create_and_write_list_for_fields(dict_for_entities, field, out_filename):
    list_with_orgs = doc_analysis.extract_particular_fields(
        dict_for_entities, field)
    with open(out_filename, 'w') as f:
        f.write(str(list_with_orgs))


run_analysis(corpus_path, phrases_file)
