import os
import sys
import logging
from glob import glob
import spacy
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET
from nltk import tokenize
import subprocess
import scispacy
import json
import re
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')


class DocAnalysis:
    """ """

    def __init__(self):
        self.labels_to_get = []
        logging.basicConfig(level=logging.INFO)

    def extract_entities_from_papers(self, corpus_path, terms_xml_path, query=None, hits=30,
                                     make_project=False, install_ami=False, removefalse=True, create_csv=True,
                                     csv_name='entities.csv', labels_to_get=['GPE', 'ORG']):
        """[summary]

        :param query: [description]
        :type query: [type]
        :param hits: [description]
        :type hits: [type]
        :param corpus_path: [description]
        :type corpus_path: [type]
        :param terms_xml_path: [description]
        :type terms_xml_path: [type]
        :param make_project: [description], defaults to False
        :type make_project: bool, optional
        :param install_ami: [description], defaults to False
        :type install_ami: bool, optional
        :param removefalse: [description], defaults to True
        :type removefalse: bool, optional
        :param create_csv: [description], defaults to True
        :type create_csv: bool, optional
        :param csv_name: [description], defaults to 'entities.csv'
        :type csv_name: str, optional
        :return: [description]
        :rtype: [type]
        """
        self.labels_to_get = labels_to_get
        if make_project:
            if not query:
                logging.warning('Please provide query as parameter')
                return
            logging.info(f"making project/searching {query} for {hits} hits into {corpus_path}")
            self.create_project_files(query, hits, corpus_path)
        if install_ami:
            logging.info(f"installing ami3 (check whether this is a good idea)")
            self.install_ami()

        logging.info(f"dict with parsed xml in {corpus_path}")
        dict_with_parsed_xml = self.make_dict_with_parsed_xml(corpus_path)
        # print(f"dict_with_parsed_xml {dict_with_parsed_xml.keys()}")
        # print(f"dict_with_parsed_xml {dict_with_parsed_xml[1]}")

        logging.info(f"getting terms from/to {terms_xml_path}")
        # terms = self.get_terms_from_ami_xml(terms_xml_path)  # (1) fails - move later?

        logging.info(f"add parsed_sections to dict: {len(dict_with_parsed_xml)}")
        self.add_parsed_sections_to_dict(dict_with_parsed_xml)
        logging.info(f"added parsed_sections to dict: {len(dict_with_parsed_xml)}")

        terms = self.get_terms_from_ami_xml(terms_xml_path)  # moved from (1)
        self.add_if_file_contains_terms(
            terms=terms, dict_with_parsed_xml=dict_with_parsed_xml)

        if removefalse:
            self.remove_statements_not_having_xmldict_terms_or_entities(
                dict_with_parsed_xml=dict_with_parsed_xml)
        if create_csv:
            self.convert_dict_to_csv(
                path=os.path.join(corpus_path, csv_name), dict_with_parsed_xml=dict_with_parsed_xml)
        return dict_with_parsed_xml

    def create_project_files(self, QUERY, HITS, OUTPUT):
        os.system(f'pygetpapers -q "{QUERY}" -k {HITS} -o {OUTPUT} -x')
        os.system(f"ami -p {OUTPUT} section")

    def install_ami(self):
        os.system("git clone https://github.com/petermr/ami3.git")
        os.system("cd ami3")
        os.system("mvn install -Dmaven.test.skip=true")

    def make_dict_with_parsed_xml(self, output):

        dict_with_parsed_xml = {}
        all_paragraphs = glob(os.path.join(
            output, '*', 'sections', '**', '[1_9]_p.xml'), recursive=True)
        counter = 1
        logging.info(f"starting  tokenization on {len(all_paragraphs)} paragraphs")
        for section_path in tqdm(all_paragraphs):
            paragraph_path = section_path
            paragraph_text = self.read_text_from_path(paragraph_path)
            sentences = tokenize.sent_tokenize(paragraph_text)
            for sentence in sentences:
                dict_with_parsed_xml[counter] = {}
                dict_for_sentences = dict_with_parsed_xml[counter]
                dict_for_sentences["file_path"] = section_path
                dict_for_sentences["paragraph"] = paragraph_text
                dict_for_sentences["sentence"] = sentence
                counter += 1
        logging.info(f"Found {len(dict_with_parsed_xml)} sentences")
        return dict_with_parsed_xml

    def read_text_from_path(self, paragraph_path):
        tree = ET.parse(paragraph_path)
        root = tree.getroot()
        try:
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            soup = BeautifulSoup(xmlstr, features='lxml')
            text = soup.get_text(separator="")
            paragraph_text = text.replace(
                '\n', '')
        except:
            paragraph_text = "empty"
        return paragraph_text

    def add_parsed_sections_to_dict(self, dict_with_parsed_xml):

        for paragraph in dict_with_parsed_xml:
            doc = nlp(dict_with_parsed_xml[paragraph]['sentence'])
            entities, labels, position_end, position_start = self.make_required_lists()
            for ent in doc.ents:
                self.add_parsed_entities_to_lists(
                    entities, labels, position_end, position_start, ent)
            self.add_lists_to_dict(dict_with_parsed_xml[paragraph], entities, labels, position_end,
                                   position_start)

    def add_if_file_contains_terms(self, terms, dict_with_parsed_xml):

        for statement in dict_with_parsed_xml:
            dict_for_sentence = dict_with_parsed_xml[statement]
            dict_for_sentence['has_terms'] = []
            for term in terms:
                if term.lower().strip() in dict_for_sentence['sentence'].lower():
                    dict_for_sentence['has_terms'].append(term)
            dict_for_sentence['weight'] = len(
                dict_for_sentence['has_terms'])

    def get_terms_from_ami_xml(self, xml_path):

        tree = ET.parse(xml_path)
        root = tree.getroot()
        terms = []
        for para in root.iter('entry'):
            terms.append(para.attrib["term"])
        return terms

    def make_required_lists(self):

        entities = []
        labels = []
        position_start = []
        position_end = []
        return entities, labels, position_end, position_start

    def add_lists_to_dict(self, dict_for_sentence, entities, labels, position_end, position_start):

        dict_for_sentence['entities'] = entities
        dict_for_sentence['labels'] = labels
        dict_for_sentence['position_start'] = position_start
        dict_for_sentence['position_end'] = position_end

    def add_parsed_entities_to_lists(self, entities, labels, position_end, position_start, ent=None):
        if ent.label_ in self.labels_to_get:
            entities.append(ent)
            labels.append(ent.label_)
            position_start.append(ent.start_char)
            position_end.append(ent.end_char)

    def convert_dict_to_csv(self, path, dict_with_parsed_xml):

        df = pd.DataFrame(dict_with_parsed_xml)
        df = df.T
        for col in df:
            try:
                df[col] = df[col].astype(str).str.replace(
                    "[", "").str.replace("]", "")
                df[col] = df[col].astype(str).str.replace(
                    "'", "").str.replace("'", "")
            except:
                pass
        df.to_csv(path, encoding='utf-8', line_terminator='\r\n')
        logging.info(f"wrote output to {path}")

    def remove_statements_not_having_xmldict_terms_or_entities(self, dict_with_parsed_xml):
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[statement]
            if len(sentect_dict['has_terms']) == 0 or len(sentect_dict['entities']) == 0:
                statement_to_pop.append(statement)

        for term in statement_to_pop:
            dict_with_parsed_xml.pop(term)

    @staticmethod
    def extract_particular_fields(dict_with_parsed_xml, field):
        """[summary]

        :param dict_with_parsed_xml: dictionary to extract entities from
        :type dict_with_parsed_xml: dict
        :param field: field name to extract from entities
        :type field: string
        :return: list containing entities
        :rtype: list
        """
        field_list = []
        for sentence in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[sentence]
            for entity, label in zip(sentect_dict['entities'], sentect_dict['labels']):
                if label == field:
                    if entity not in field_list:
                        field_list.append(entity)
        return field_list



# -------this section comes from metadata_analysis.py 
# (https://github.com/petermr/crops/blob/main/metadata_analysis/metadata_analysis.py)

metadata_dictionary = {}


def querying_pygetpapers_sectioning(query, hits, output_directory, using_terms=False, terms_txt=None):
    """queries pygetpapers for specified query. Downloads XML, and sections papers using ami section
    Args:
        query (str): query to pygetpapers
        hits (int): no. of papers to download
        output_directory (str): CProject Directory (where papers get downloaded)
        using_terms (bool, optional): pygetpapers --terms flag. Defaults to False.
        terms_txt (str, optional): path to text file with terms. Defaults to None.
    """
    logging.info('querying pygetpapers')
    if using_terms:
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x --terms {terms_txt} --logfile pygetpapers_log.txt',
                       shell=True)
    else:
        subprocess.run(f'pygetpapers -q "{query}" -k {hits} -o {output_directory} -x  --logfile pygetpapers_log.txt',
                       shell=True)
    logging.info('running ami section')
    subprocess.run(f'ami -p {output_directory} section', shell=True)


def get_metadata_json(output_directory):
    WORKING_DIRECTORY = os.getcwd()
    glob_results = glob.glob(os.path.join(WORKING_DIRECTORY,
                                          output_directory, "*", 'eupmc_result.json'))
    metadata_dictionary["metadata_json"] = glob_results
    logging.info(f'metadata found for {len(metadata_dictionary["metadata_json"])} papers')


def get_PMCIDS(metadata_dictionary=metadata_dictionary):
    metadata_dictionary["PMCIDS"] = []
    for metadata in metadata_dictionary["metadata_json"]:
        with open(metadata, encoding='utf-8') as f:
            metadata_in_json = json.load(f)
            try:
                metadata_dictionary["PMCIDS"].append(
                    metadata_in_json["full"]["pmcid"])
            except KeyError:
                metadata_dictionary["PMCIDS"].append('NaN')
    logging.info('getting PMCIDs')


def parse_xml(output_directory, section, metadata_dictionary=metadata_dictionary):
    metadata_dictionary[f"{section}"] = []
    for pmc in metadata_dictionary["PMCIDS"]:
        paragraphs = []
        test_glob = glob.glob(os.path.join(os.getcwd(), output_directory,
                                           pmc, 'sections', '**', f'*{section}*', '**', '*.xml'),
                              recursive=True)
        for result in test_glob:
            tree = ET.parse(result)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf-8', method='xml')
            soup = BeautifulSoup(xmlstr, features='lxml')
            text = soup.get_text(separator="")
            text = text.replace('\n', '')
            paragraphs.append(text)
        concated_paragraph = ' '.join(paragraphs)
        metadata_dictionary[f"{section}"].append(concated_paragraph)
    logging.info(f"parsing {section} section")


def get_abstract(metadata_dictionary=metadata_dictionary):
    TAG_RE = re.compile(r"<[^>]+>")
    metadata_dictionary["abstract"] = []
    for metadata in metadata_dictionary["metadata_json"]:
        with open(metadata, encoding='utf-8') as f:
            metadata_in_json = json.load(f)
            try:
                raw_abstract = metadata_in_json["full"]["abstractText"]
                abstract = TAG_RE.sub(' ', raw_abstract)
                metadata_dictionary["abstract"].append(abstract)
            except KeyError:
                metadata_dictionary["abstract"].append('NaN')
    logging.info("getting the abstracts")


def get_keywords(metadata_dictionary=metadata_dictionary):
    metadata_dictionary["keywords"] = []
    for metadata in metadata_dictionary["metadata_json"]:
        with open(metadata, encoding='utf-8') as f:
            metadata_in_json = json.load(f)
            try:
                metadata_dictionary["keywords"].append(
                    metadata_in_json["full"]["keywordList"]["keyword"])
            except KeyError:
                metadata_dictionary["keywords"].append([])
    logging.info("getting the keywords from metadata")


def key_phrase_extraction(section, metadata_dictionary=metadata_dictionary):
    metadata_dictionary["yake_keywords"] = []
    for text in metadata_dictionary[f"{section}"]:
        custom_kw_extractor = yake.KeywordExtractor(
            lan='en', n=2, top=10, features=None)
        keywords = custom_kw_extractor.extract_keywords(text)
        keywords_list = []
        for kw in keywords:
            keywords_list.append(kw[0])
        metadata_dictionary["yake_keywords"].append(keywords_list)
    logging.info(f'extracted key phrases from {section}')


def get_organism(section,label_interested= 'TAXON', metadata_dictionary=metadata_dictionary):
    #nlp = spacy.load("en_ner_bionlp13cg_md")
    nlp = spacy.load("en_core_sci_sm")
    metadata_dictionary["entities"] = []
    for sci_text in metadata_dictionary[f"{section}"]:
        entity = []
        doc = nlp(sci_text)
        for ent in doc.ents:
            if ent.label_ == label_interested:
                entity.append(ent.text)
        metadata_dictionary["entities"].append(entity)
    logging.info(F"NER using SciSpacy - looking for {label_interested}")


def convert_to_csv(path='keywords_results_yake_organism_pmcid_tps_cam_ter_c.csv', metadata_dictionary=metadata_dictionary):
    df = pd.DataFrame(metadata_dictionary)
    df.to_csv(path, encoding='utf-8', line_terminator='\r\n')
    logging.info(f'writing the keywords to {path}')


def convert_to_json(path='ethics_statement_2000.json', metadata_dictionary = metadata_dictionary):
    json_file = json.dumps(metadata_dictionary)
    f = open(path,"w", encoding='ascii')
    f.write(json_file)
    f.close()
    logging.info(f'writing the dictionary to {path}')


def look_for_a_word(section, search_for="TPS", metadata_dictionary=metadata_dictionary):
    metadata_dictionary[f"{search_for}_match"] = []
    for text in metadata_dictionary[f"{section}"]:
        words = text.split(" ")
        match_list = ([s for s in words if f"{search_for}" in s])
        metadata_dictionary[f"{search_for}_match"] .append(match_list)
    logging.info(f"looking for {search_for} in {section}")


def look_for_next_word(section, search_for=["number:", "no.", "No.", "number" ], metadata_dictionary=metadata_dictionary):
    metadata_dictionary[f"{search_for}_match"] = []
    for text in metadata_dictionary[f"{section}"]:
        words = text.split(" ")
        words = iter(words)
        try:
            match_list = ([next(words) for s in words if any(xs in s for xs in search_for)])
            metadata_dictionary[f"{search_for}_match"].append(match_list)
        except StopIteration:
            metadata_dictionary[f"{search_for}_match"].append([])

    logging.info(f"looking for {search_for} in {section}")


def add_if_file_contains_terms(section, metadata_dictionary=metadata_dictionary, terms=['iNaturalist']):
    metadata_dictionary["terms"] = []
    for term in terms:
        for text in metadata_dictionary[f"{section}"]:
            if term.lower() in text.lower():
                metadata_dictionary["terms"].append(term)
            else:
                metadata_dictionary["terms"].append('NaN')
    logging.info(f'looking for term matches in {section}')



CPROJECT = os.path.join(os.path.expanduser('~'), 'ethics_statement_2000_generic')
SECTION= 'ethic'
#querying_pygetpapers_sectioning("inaturalist",'500',CPROJECT)
get_metadata_json(CPROJECT)
get_PMCIDS()
parse_xml(CPROJECT, SECTION)
get_abstract()
get_keywords()
key_phrase_extraction(SECTION)
#get_organism(SECTION)
look_for_next_word(SECTION)
#look_for_next_word(SECTION, search_for="C.")
#look_for_next_word(SECTION, search_for='Citrus')
add_if_file_contains_terms(SECTION)
convert_to_csv(f'ethics_{SECTION}2000.csv')
convert_to_json()