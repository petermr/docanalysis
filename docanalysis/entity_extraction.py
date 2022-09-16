from distutils.log import error
import os
import logging
import requests
from glob import glob
import spacy
from spacy import displacy
from nltk import tokenize
from spacy.matcher import PhraseMatcher
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET
from docanalysis.ami_sections import AMIAbsSection
from pathlib import Path
from pygetpapers import Pygetpapers
from collections import Counter
import pip
import json
import re
from lxml import etree
from pygetpapers.download_tools import DownloadTools
from urllib.request import urlopen
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    from nltk import tokenize


def install(package):
    """

    :param package: 

    """
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])


try:
    from abbreviations import schwartz_hearst
except ModuleNotFoundError:
    install('abbreviations')
    from abbreviations import schwartz_hearst


#nlp_phrase = spacy.load("en_core_web_sm")

CONFIG_SECTIONS = 'https://raw.githubusercontent.com/petermr/docanalysis/main/docanalysis/config/default_sections.json'
CONFIG_AMI_DICT = 'https://raw.githubusercontent.com/petermr/docanalysis/main/docanalysis/config/default_dicts.json'


class EntityExtraction:
    """EntityExtraction Class"""

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.sections = self.json_to_dict(CONFIG_SECTIONS)
        self.dict_of_ami_dict = self.json_to_dict(CONFIG_AMI_DICT)
        self.all_paragraphs = {}
        self.sentence_dictionary = {}
        self.spacy_model = 'spacy'
        self.nlp = None

    def switch_spacy_versions(self, spacy_type):
        """Method to toggle between spacy and scispacy

        :param spacy_type: "spacy" or "scispacy"
        :type spacy_type: string

        """
        logging.info(f'Loading {spacy_type}')
        if spacy_type == "scispacy":
            from scispacy.abbreviation import AbbreviationDetector
            try:
                self.nlp = spacy.load('en_ner_bc5cdr_md')
            except OSError:
                install(
                    'https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bc5cdr_md-0.4.0.tar.gz')
                self.nlp = spacy.load('en_ner_bc5cdr_md')
            self.nlp.add_pipe("abbreviation_detector")
        elif spacy_type == "spacy":
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                from spacy.cli import download
                download('en_core_web_sm')
                self.nlp = spacy.load('en_core_web_sm')

    def dictionary_to_html(self, html_path):
        """Converts dictionary to html

        :param html_path: path to save html
        :type html_path: string

        """
        list_of_docs = []
        for sentence in self.sentence_dictionary:
            list_of_docs.append(self.sentence_dictionary[sentence]['doc'])
        html = displacy.render(list_of_docs, style="ent",
                               page=True, minify=True)
        logging.info(f"saving output: {html_path}")
        self._write_string_to_file(html, html_path)

    def extract_entities_from_papers(self, corpus_path, terms_xml_path, search_sections, entities, query=None, hits=30,
                                     run_pygetpapers=False, make_section=False, removefalse=True,
                                     csv_name=False, make_ami_dict=False, spacy_model=False, html_path=False, synonyms=False, make_json=False, search_html=False, extract_abb=False):
        """logic implementation (Q: how detailed should the description here be?)

        :param corpus_path: 
        :param terms_xml_path: 
        :param search_sections: 
        :param entities: 
        :param query:  (Default value = None)
        :param hits:  (Default value = 30)
        :param run_pygetpapers:  (Default value = False)
        :param make_section:  (Default value = False)
        :param removefalse:  (Default value = True)
        :param csv_name:  (Default value = False)
        :param make_ami_dict:  (Default value = False)
        :param spacy_model:  (Default value = False)
        :param html_path:  (Default value = False)
        :param synonyms:  (Default value = False)
        :param make_json:  (Default value = False)
        :param search_html:  (Default value = False)
        :param extract_abb:  (Default value = False)

        """

        self.spacy_model = spacy_model
        corpus_path = os.path.abspath(corpus_path)
        if run_pygetpapers:
            if not query:
                logging.warning(
                    "please provide query (like 'terpene', 'essential oils') as parameter")
                return
            self.run_pygetpapers(query, hits, corpus_path)
        if os.path.isdir(corpus_path):
            if make_section:
                self.run_ami_section(corpus_path)
        else:
            logging.error("CProject doesn't exist")
            return
        if search_html:
            search_sections = ['HTML', ]
        if search_sections == ['ALL', ]:
            search_sections = self.sections.keys()
        if len(glob(os.path.join(corpus_path, '**', 'sections'))) > 0:
            self.all_paragraphs = self.get_glob_for_section(
                corpus_path, search_sections)
        else:
            logging.error('section papers using --make_sections before search')
        if spacy_model or csv_name or extract_abb or make_ami_dict:
            if search_html:
                self.make_dict_with_parsed_document(document_type='html')
            else:
                self.make_dict_with_parsed_document()
        if spacy_model:
            self.run_spacy_over_sections(self.sentence_dictionary, entities)
            self.remove_statements_not_having_xmldict_terms(
                dict_with_parsed_xml=self.sentence_dictionary, searching='entities')
        if terms_xml_path:
            for i in range(len(terms_xml_path)):
                compiled_terms = self.get_terms_from_ami_xml(terms_xml_path[i])
                self.add_if_file_contains_terms(
                    compiled_terms=compiled_terms, dict_with_parsed_xml=self.sentence_dictionary, searching=f'{i}')
                if removefalse:
                    self.remove_statements_not_having_xmldict_terms(
                        dict_with_parsed_xml=self.sentence_dictionary, searching=f'{i}')
            if synonyms:
                synonyms_list = self.get_synonyms_from_ami_xml(terms_xml_path)
                self.add_if_file_contains_terms(
                    compiled_terms=synonyms_list, dict_with_parsed_xml=self.sentence_dictionary, searching='has_synonyms')
                if removefalse:
                    self.remove_statements_not_having_xmldict_terms(
                        dict_with_parsed_xml=self.sentence_dictionary)
                if html_path:
                    self.dictionary_to_html(
                        os.path.join(corpus_path, html_path))
        if extract_abb:
            self.abbreviation_search_using_sw(self.sentence_dictionary)
            abb_ami_dict_path = os.path.join(corpus_path, extract_abb)
            self.make_ami_dict_from_abbreviation(
                extract_abb, self.sentence_dictionary, abb_ami_dict_path)
            if removefalse:
                self.remove_statements_not_having_xmldict_terms(
                    dict_with_parsed_xml=self.sentence_dictionary, searching='abb')

        if csv_name:
            dict_with_parsed_xml_no_paragrph = self.remove_paragraph_form_parsed_xml_dict(
                self.sentence_dictionary, "paragraph")
            self.convert_dict_to_csv(
                path=os.path.join(corpus_path, f'{csv_name}'), dict_with_parsed_xml=dict_with_parsed_xml_no_paragrph)
        if make_json:
            dict_with_parsed_xml_no_paragrph = self.remove_paragraph_form_parsed_xml_dict(
                self.sentence_dictionary, "paragraph")
            self.convert_dict_to_json(path=os.path.join(
                corpus_path, f'{make_json}'), dict_with_parsed_xml=dict_with_parsed_xml_no_paragrph)
        if make_ami_dict:
            ami_dict_path = os.path.join(corpus_path, make_ami_dict)
            self.handle_ami_dict_creation(
                self.sentence_dictionary, make_ami_dict, ami_dict_path)

        return self.sentence_dictionary

    def run_pygetpapers(self, query, hits, output):
        """calls pygetpapers to query EPMC for papers; downloads specified number of papers

        :param query: query to pygetpapers/EPMC
        :type query: str
        :param hits: number of papers to download
        :type hits: int
        :param output: name of the folder
        :type output: str

        """
        pygetpapers_call = Pygetpapers()
        pygetpapers_call.run_command(
            query=query, limit=hits, output=output, xml=True)
        logging.info(f"making CProject {output} with {hits} papers on {query}")

    def run_ami_section(self, path):
        """Creates sections folder for each paper (CTree); sections papers into front, body, back and floats based on JATS

        :param path: CProject path
        :type path: string

        """
        file_list = glob(os.path.join(
            path, '**', 'fulltext.xml'), recursive=True)
        for paper in file_list:
            with open(paper, 'r') as xml_file:
                xml_string = xml_file.read()
            if len(xml_string) > 0:
                outdir = Path(Path(paper).parent, "sections")
                AMIAbsSection.make_xml_sections(paper, outdir, True)
            else:
                logging.warning(f"{paper} is empty")

    def get_glob_for_section(self, path, section_names):
        """globs for xml files in section folder of each CTree

        :param path: CProject path
        :type path: string
        :param section_names: one or more keys (section names) from CONFIG_SECTIONS
        :type section_names: string
        :returns: list of globs
        :rtype: list

        """
        for section_name in section_names:
            if section_name in self.sections.keys():
                self.all_paragraphs[section_name] = []
                for section in self.sections[section_name]:
                    self.all_paragraphs[section_name] += glob(os.path.join(
                        path, '**', 'sections', '**', section), recursive=True)
            else:
                logging.error(
                    "please make sure that you have selected only the supported sections: ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY, MET, RES, TAB, TIL")
        return self.all_paragraphs

    def make_dict_with_parsed_document(self, document_type="xml"):
        """creates dictionary with parsed xml or html

        :param document_type: type of file fed: xml or html. Defaults to "xml".
        :type document_type: str
        :returns: python dict containing parsed text from xml or html
        :rtype: dict

        """

        self.sentence_dictionary = {}

        counter = 1
        for section in self.all_paragraphs:
            for section_path in tqdm(self.all_paragraphs[section]):
                paragraph_path = section_path
                if document_type == 'html':
                    paragraph_text = self.read_text_from_html(paragraph_path)
                elif document_type == 'xml':
                    paragraph_text = self.read_text_from_path(paragraph_path)
                sentences = tokenize.sent_tokenize(paragraph_text)
                for sentence in sentences:
                    self.sentence_dictionary[counter] = {}
                    self._make_dict_attributes(
                        counter, section, section_path, paragraph_text, sentence)
                    counter += 1
        logging.info(
            f"Found {len(self.sentence_dictionary)} sentences in the section(s).")
        return self.sentence_dictionary

    def _make_dict_attributes(self, counter, section, section_path, paragraph_text, sentence):
        """

        :param counter: 
        :param section: 
        :param section_path: 
        :param paragraph_text: 
        :param sentence: 

        """
        dict_for_sentences = self.sentence_dictionary[counter]
        dict_for_sentences["file_path"] = section_path
        dict_for_sentences["paragraph"] = paragraph_text
        dict_for_sentences["sentence"] = sentence
        dict_for_sentences["section"] = section

    def read_text_from_path(self, paragraph_path):
        """uses ElementTree to read text from xml files

        :param paragraph_path: path to xml file
        :type paragraph_path: string
        :returns: raw text from xml
        :rtype: string

        """
        try:
            tree = ET.parse(paragraph_path)
            root = tree.getroot()
            xmlstr = ET.tostring(root, encoding='utf8', method='xml')
            soup = BeautifulSoup(xmlstr, features='lxml')
            text = soup.get_text(separator=" ")
            paragraph_text = text.replace(
                '\n', ' ')
        except:
            paragraph_text = "empty"
            logging.error(f"cannot parse {paragraph_path}")
        return paragraph_text

    def read_text_from_html(self, paragraph_path):
        """uses beautifulsoup to read text from html files

        :param paragraph_path: path to html file
        :type paragraph_path: string
        :returns: raw text from html
        :rtype: string

        """
        with open(paragraph_path, encoding="utf-8") as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            return soup.text.replace('\n', ' ')

    def run_spacy_over_sections(self, dict_with_parsed_xml, entities_names):
        """uses spacy to extract specific Named-Entities from sentences in python dict

        :param dict_with_parsed_xml: main dict with sentences
        :type dict_with_parsed_xml: dict
        :param entities_names: list of kinds of Named-Entities that needs to be extacted
        :type entities_names: list

        """
        self.switch_spacy_versions(self.spacy_model)
        for paragraph in tqdm(dict_with_parsed_xml):
            if len(dict_with_parsed_xml[paragraph]['sentence']) > 0:
                doc = self.nlp(dict_with_parsed_xml[paragraph]['sentence'])
                entities, labels, position_end, position_start, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end = self._make_required_lists()
                if self.spacy_model == "scispacy":
                    self._get_abbreviations(
                        doc, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end)
                self._get_entities(entities_names, doc, entities,
                                   labels, position_end, position_start)
                self._add_lists_to_dict(dict_with_parsed_xml[paragraph], entities, labels, position_end,
                                        position_start, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end)

    def _get_entities(self, entities_names, doc, entities, labels, position_end, position_start):
        """

        :param entities_names: 
        :param doc: 
        :param entities: 
        :param labels: 
        :param position_end: 
        :param position_start: 

        """
        for ent in doc.ents:
            if (ent.label_ in entities_names) or (entities_names == ['ALL']):
                self._add_parsed_entities_to_lists(
                    entities, labels, position_end, position_start, ent)

    def abbreviation_search_using_sw(self, dict_with_parsed_xml):
        """Extracts abbreviations from sentences using schwartz_hearst. Credit: Ananya Singha

        :param dict_with_parsed_xml: main python dictionary with sentences
        :type dict_with_parsed_xml: dict

        """
        for text in dict_with_parsed_xml:
            dict_for_sentence = dict_with_parsed_xml[text]
            dict_for_sentence["abb"] = []
            pairs = schwartz_hearst.extract_abbreviation_definition_pairs(
                doc_text=dict_for_sentence['sentence'])
            dict_for_sentence["abb"] = pairs
            self._make_list_from_dict(pairs)

    def make_abb_exp_list(self, result_dictionary):
        """make lists of abbreviations and expansions to input into xml dictionary creating method

        :param result_dictionary: main dictionary that contains sentences and abbreviation dict (abb and expansion)
        :type result_dictionary: dict
        :returns: all abbreviations
        :rtype: list

        """
        list_of_name_lists = []
        list_of_term_lists = []
        for entry in result_dictionary:
            sentence_dictionary = result_dictionary[entry]
            if 'abb' in sentence_dictionary:
                pairs_dicts = (result_dictionary[entry]['abb'])
                name_list_for_every_dict, term_list_for_every_dict = self._make_list_from_dict(
                    pairs_dicts)
                list_of_name_lists.append(name_list_for_every_dict)
                list_of_term_lists.append(term_list_for_every_dict)
        return self._list_of_lists_to_single_list(list_of_name_lists), self._list_of_lists_to_single_list(list_of_term_lists)

    def _make_list_from_dict(self, pairs):
        """

        :param pairs: 

        """
        keys_list = []
        values_list = []
        keys_list.extend(pairs.keys())
        values_list.extend(pairs.values())
        return keys_list, values_list

    def _list_of_lists_to_single_list(self, list_of_lists):
        """

        :param list_of_lists: 

        """
        return [item for sublist in list_of_lists for item in sublist]

    def make_ami_dict_from_abbreviation(self, title, result_dictionary, path):
        """create xml ami-dict containing abbreviations extracted from sentences

        :param title: title of xml ami-dict
        :type title: str
        :param result_dictionary: main dictionary with sentences and corresponding abbeviations
        :type result_dictionary: dict
        :param path: path where the xml ami-dict file would lie
        :type path: str

        """
        name_list, term_list = self.make_abb_exp_list(result_dictionary)
        dictionary_element = etree.Element("dictionary")
        dictionary_element.attrib['title'] = title
        for name, term in tqdm(zip(name_list, term_list)):

            wiki_lookup_list = self.wiki_lookup(term)
            try:
                entry_element = etree.SubElement(dictionary_element, "entry")
                entry_element.attrib['name'] = name
                entry_element.attrib['term'] = term
                if len(wiki_lookup_list) == 0:
                    entry_element.attrib['wikidataID'] = ""
                elif len(wiki_lookup_list) == 1:
                    entry_element.attrib['wikidataID'] = ", ".join(wiki_lookup_list)
                else:
                    raw_element = etree.SubElement(entry_element, 'raw')
                    raw_element.attrib['wikidataID'] = ", ".join(wiki_lookup_list)
            except Exception as e:
                logging.error(f"Couldn't add {term} to amidict")
        xml_dict = self._etree_to_string(dictionary_element)
        self._write_string_to_file(xml_dict, f'{path}.xml')
        logging.info(f'wrote all abbreviations to ami dict {path}.xml')

    def _etree_to_string(self, dictionary_element):
        """

        :param dictionary_element: 

        """
        xml_dict = etree.tostring(
            dictionary_element, pretty_print=True).decode('utf-8')
        return xml_dict

    def _get_abbreviations(self, doc, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end):
        """

        :param doc: 
        :param abbreviations: 
        :param abbreviations_longform: 
        :param abbreviation_start: 
        :param abbreviation_end: 

        """
        for abrv in doc._.abbreviations:
            abbreviations.append(abrv)
            abbreviations_longform.append(abrv._.long_form)
            abbreviation_start.append(abrv.start)
            abbreviation_end.append(abrv.end)

    def add_if_file_contains_terms(self, compiled_terms, dict_with_parsed_xml, searching='has_terms'):
        """populate the main dictionary with term matches, its frequency and span

        :param compiled_terms: list of compiled ami-dict terms
        :type compiled_terms: list
        :param dict_with_parsed_xml: dictionary containing sentences
        :type dict_with_parsed_xml: dict
        :param searching: dict key name. Defaults to 'has_terms'.
        :type searching: str

        """
        for statement in tqdm(dict_with_parsed_xml):
            dict_for_sentence = dict_with_parsed_xml[statement]
            dict_for_sentence[f'{searching}'] = []
            dict_for_sentence[f'{searching}_span'] = []
            term_list, span_list, frequency = self.search_sentence_with_compiled_terms(
                compiled_terms, dict_for_sentence['sentence'])
            if term_list:
                dict_for_sentence[f'{searching}'].append(term_list)
                dict_for_sentence[f'weight_{searching}'] = frequency
                dict_for_sentence[f'{searching}_span'].append(span_list)

    def search_sentence_with_compiled_terms(self, compiled_terms, sentence):
        """search sentences using the compiled ami-dict entry

        :param compiled_terms: list of compiled ami-dict terms
        :type compiled_terms: list
        :param sentence: sentence to search using compiled terms
        :type sentence: string
        :returns: list of terms that was found after searching sentence
        :rtype: list

        """
        # https://stackoverflow.com/questions/47681756/match-exact-phrase-within-a-string-in-python
        match_list = []
        span_list = []
        frequency = 0
        for compiled_term in compiled_terms:
            term_match = compiled_term.search(sentence, re.IGNORECASE)
            if term_match is not None:
                match_list.append(term_match.group())
                span_list.append(term_match.span())
            frequency = len(match_list)
        return match_list, span_list, frequency

    def get_terms_from_ami_xml(self, xml_path):
        """parses ami-dict (xml) and reads the entry terms; ami-dict can either be the default ones (user specifies python dict key) or customized ones (user specifies full path to it)

        :param xml_path: either keys from dict_of_ami_dict or full path to ami-dict
        :type xml_path: string
        :returns: list of regex compiled entry terms from ami-dict
        :rtype: list

        """
        if xml_path in self.dict_of_ami_dict.keys():
            logging.info(f"getting terms from {xml_path}")
            tree = ET.parse(urlopen(self.dict_of_ami_dict[xml_path]))
            root = tree.getroot()
        elif xml_path not in self.dict_of_ami_dict.keys():
            tree = ET.parse(xml_path)
            root = tree.getroot()
            logging.info(f"getting terms from {xml_path}")
        else:
            logging.error(f'{xml_path} is not a supported dictionary. Choose from: EO_ACTIVITY, EO_COMPOUND, EO_EXTRACTION, EO_PLANT, EO_PLANT_PART, PLANT_GENUS,EO_TARGET, COUNTRY, DISEASE, DRUG, ORGANIZATION ')

        compiled_terms = self._compiled_regex(root.iter('entry'))
        return (set(compiled_terms))

    def _compiled_regex(self, iterate_over):
        """

        :param iterate_over: 

        """
        compiled_terms = []
        for para in iterate_over:
            try:
                term = (para.attrib["term"])
            except KeyError:
                term = para.text
            try:
                compiled_term = self._regex_compile(term)
            except re.error:
                logging.warning(f'cannot use term {term}')
            compiled_terms.append(compiled_term)
        return compiled_terms

    def _regex_compile(self, term):
        """

        :param term: 

        """
        return re.compile(r'\b{}\b'.format(term))

    def get_synonyms_from_ami_xml(self, xml_path):
        """parses ami-dict (xml) and reads the entry's synonyms; ami-dict can either be the default ones (user specifies python dict key) or customized ones (user specifies full path to it)

        :param xml_path: either keys from dict_of_ami_dict or full path to ami-dict
        :type xml_path: string
        :returns: list of regex compiled entry's synonyms from ami-dict
        :rtype: list

        """
        if xml_path in self.dict_of_ami_dict.keys():
            logging.info(f"getting synonyms from {xml_path}")
            tree = ET.parse(urlopen(self.dict_of_ami_dict[xml_path]))
            root = tree.getroot()
        elif xml_path not in self.dict_of_ami_dict.keys():
            logging.info(f"getting synonyms from {xml_path}")
            tree = ET.parse(xml_path)
            root = tree.getroot()
        else:
            logging.error(f'{xml_path} is not a supported dictionary. Choose from: EO_ACTIVITY, EO_COMPOUND, EO_EXTRACTION, EO_PLANT, EO_PLANT_PART, PLANT_GENUS,EO_TARGET, COUNTRY, DISEASE, DRUG, ORGANIZATION ')
        synonyms = self._compiled_regex(root.findall("./entry/synonym"))
        return synonyms

    def _make_required_lists(self):
        """ """
        abbreviations = []
        abbreviations_longform = []
        abbreviation_start = []
        abbreviation_end = []
        entities = []
        labels = []
        position_start = []
        position_end = []
        return entities, labels, position_end, position_start, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end

    def _add_lists_to_dict(self, dict_for_sentence, entities, labels, position_end,
                           position_start, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end):
        """

        :param dict_for_sentence: 
        :param entities: 
        :param labels: 
        :param position_end: 
        :param position_start: 
        :param abbreviations: 
        :param abbreviations_longform: 
        :param abbreviation_start: 
        :param abbreviation_end: 

        """

        dict_for_sentence['entities'] = entities
        dict_for_sentence['labels'] = labels
        dict_for_sentence['position_start'] = position_start
        dict_for_sentence['position_end'] = position_end
        dict_for_sentence['abbreviations'] = abbreviations
        dict_for_sentence['abbreviations_longform'] = abbreviations_longform
        dict_for_sentence['abbreviation_start'] = abbreviation_start
        dict_for_sentence['abbreviation_end'] = abbreviation_end

    def _add_parsed_entities_to_lists(self, entities, labels, position_end, position_start, ent=None):
        """

        :param entities: 
        :param labels: 
        :param position_end: 
        :param position_start: 
        :param ent:  (Default value = None)

        """
        entities.append(ent.text)
        labels.append(ent.label_)
        position_start.append(ent.start_char)
        position_end.append(ent.end_char)

    def convert_dict_to_csv(self, path, dict_with_parsed_xml):
        """Turns python dictionary into CSV using pandas

        :param path: CSV file to write output
        :type path: string
        :param dict_with_parsed_xml: python dictionary that needs to be converted to csv
        :type dict_with_parsed_xml: dict

        """
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

    def remove_paragraph_form_parsed_xml_dict(self, dict_with_parsed_xml, key_to_remove):
        """pops out the specified key value pairs from python dictionaries

        :param dict_with_parsed_xml: python dict from which a key-value pair needs to be removed
        :type dict_with_parsed_xml: dict
        :param key_to_remove: key of the pair that needs to be removed
        :type key_to_remove: string
        :returns: python dict with the specified key-value pair removed
        :rtype: dict

        """
        for entry in dict_with_parsed_xml:
            dict_with_parsed_xml[entry].pop(key_to_remove, None)
        return dict_with_parsed_xml

    def convert_dict_to_json(self, path, dict_with_parsed_xml):
        """writes python dictionary to json file

        :param path: json file path to write to
        :type path: str
        :param dict_with_parsed_xml: main dictionary with sentences, search hits, entities, etc.
        :type dict_with_parsed_xml: dict

        """
        with open(path, mode='w', encoding='utf-8') as f:
            json.dump(dict_with_parsed_xml, f, indent=4)
        logging.info(f"wrote JSON output to {path}")

    def remove_statements_not_having_xmldict_terms(self, dict_with_parsed_xml, searching='has_terms'):
        """removes key-value pairs from the main python dict that do not have any match hits

        :param dict_with_parsed_xml: python dictionary from which the specific key-value pairs needs to be removed
        :type dict_with_parsed_xml: dict
        :param searching: the key to the pair in the nested-dict that needs to be removed (Default value = 'has_terms')
        :type searching: str

        """
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[statement]
            if len(sentect_dict[searching]) == 0:
                statement_to_pop.append(statement)

        for term in statement_to_pop:
            dict_with_parsed_xml.pop(term)

    def make_ami_dict_from_list(self, list_of_terms_with_count, title):
        """makes ami-dict from a python dictionary containing terms and frequencies.

        :param list_of_terms_with_count: python dictionary containing terms and their frequency of occurence
        :type list_of_terms_with_count: dict
        :param title: title of the xml ami-dict as well as the name of the XML file
        :type title: string
        :returns: xml ami-dict
        :rtype: file

        """
        dictionary_element = etree.Element("dictionary")
        dictionary_element.attrib['title'] = title
        for term in list_of_terms_with_count:
            try:
                entry_element = etree.SubElement(dictionary_element, "entry")
                entry_element.attrib['term'] = term[0]
                entry_element.attrib['count'] = str(term[1])
            except Exception as e:
                logging.error(f"Couldn't add {term} to amidict")
        return self._etree_to_string(dictionary_element)

    def _write_string_to_file(self, string_to_put, title):
        """

        :param string_to_put: 
        :param title: 

        """
        with open(title, mode='w', encoding='utf-8') as f:
            f.write(string_to_put)

    def handle_ami_dict_creation(self, result_dictionary, title, path):
        """creates and writes ami dictionary with entities extracted and their frequency.

        :param result_dictionary: main python dictionary with sentences, entities, etc.
        :type result_dictionary: dict
        :param title: title of ami-dictionary (xml file)
        :type title: str
        :param path: file path
        :type path: str

        """
        list_of_entities = []
        for entry in result_dictionary:
            if 'entities' in result_dictionary[entry]:
                entity = result_dictionary[entry]['entities']
                list_of_entities.extend(entity)
        dict_of_entities_with_count = Counter(list_of_entities)
        list_of_terms_with_count = dict_of_entities_with_count.most_common()
        xml_dict = self.make_ami_dict_from_list(
            list_of_terms_with_count, title)
        self._write_string_to_file(xml_dict, f'{path}.xml')
        logging.info(f"Wrote all the entities extracted to {path}.xml")

    def json_to_dict(self, json_file_link):
        """loads json file as python dictionary

        :param json_file_link: link to json file on the web
        :type json_file_link: str
        :returns: python dictionary from json
        :rtype: dictionary

        """
        path = urlopen(json_file_link)
        json_dict = json.load(path)
        return (json_dict)

    def wiki_lookup(self, query):
        """Queries Wikidata API for Wikidata Item IDs for terms in ami-dict

        :param query: term to query wikdiata for ID
        :type query: string
        :returns: potential Wikidata Item URLs
        :rtype: list

        """
        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "format": "json"
        }
        data = requests.get(
            "https://www.wikidata.org/w/api.php", params=params)
        result = data.json()
        hit_list = []
        for hit in result['search']:
            try:
                if "scientific article" not in hit["description"]:
                    hit_list.append(hit["id"])
            except:
                hit_list.append(hit["id"])
        return hit_list


# take out the constants
# look through download_tools (pygetpapers) and see if we have overlapping functionality.
# functionality_from_(where you are getting a data)


# Future goals
# make tests automated
# readthedocs
# tutorials
# repository management
