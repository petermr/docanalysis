import os
import logging
from glob import glob
import spacy
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET
from nltk import tokenize

class ParseSections():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

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

    def add_if_file_contains_terms(self, terms, dict_with_parsed_xml):

        for statement in dict_with_parsed_xml:
            dict_for_sentence = dict_with_parsed_xml[statement]
            dict_for_sentence['has_terms'] = []
            for term in terms:
                if term.lower().strip() in dict_for_sentence['sentence'].lower():
                    dict_for_sentence['has_terms'].append(term)
            dict_for_sentence['weight'] = len(
                dict_for_sentence['has_terms'])

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