from fileinput import filename
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
import yake
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

    def make_ami_dict_from_list(self,list_of_terms,title):
        xml_string=f'''<?xml version="1.0" encoding="UTF-8"?>
                            <dictionary title="{title}">
                    '''
        for term in list_of_terms:
            xml_string+=f'''
                        <entry term="{term}"/>
            '''
        xml_string+="</dictionary>"
        return xml_string
    
    def write_string_to_file(self,string_to_put,title):
        with open(f'{title}.xml',mode='w') as f:
            f.write(string_to_put)

if __name__=="__main__":
    Docanalysis= DocAnalysis()
    Docanalysis.extract_entities_from_papers("D:\\main_projects\\repositories\\docanalysis\\corpus\\e_cancer_clinical_trial_50", "D:\\main_projects\\repositories\\docanalysis\\ethics_dictionary\\ethics_key_phrases\\ethics_key_phrases.xml", query=None, hits=30,
                                     make_project=False, install_ami=False, removefalse=True, create_csv=True,
                                     csv_name='entities.csv', labels_to_get=['GPE', 'ORG'])