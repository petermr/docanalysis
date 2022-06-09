from distutils.log import error
import os
import logging
from glob import glob
import spacy
from spacy import displacy
from spacy.matcher import PhraseMatcher
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET
from nltk import tokenize
from docanalysis.ami_sections import AMIAbsSection
from pathlib import Path
from pygetpapers import Pygetpapers
from collections import Counter
import pip
import json
import re
from lxml import etree
import pyparsing as pp
from pygetpapers.download_tools import DownloadTools
from urllib.request import urlopen
def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])

#nlp_phrase = spacy.load("en_core_web_sm")

class EntityExtraction:
    """ """

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.sections= {"ABS":['*abstract.xml'],
        "ALL":['*.xml'],
        "ACK": ['*ack.xml'],
        "AFF": ['*aff.xml'],
        "AUT": ['*contrib-group.xml'],
        "CON": ['*conclusion*/*.xml'],
        "DIS": ['*discussion*/**/*_title.xml', '*discussion*/**/*_p.xml'], # might bring unwanted sections like tables, fig. captions etc. Maybe get only title and paragraphs?
        "ETH": ['*ethic*/*.xml'],
        "FIG": ['*fig*.xml'],
        "INT": ['*introduction*/*.xml', '*background*/*.xml'],
        "KEY": ['*kwd-group.xml'],
        "MET": ['*method*/*.xml', '*material*/*.xml'] ,# also gets us supplementary material. Not sure how to exclude them
        "RES": ['*result*/*/*_title.xml', '*result*/*/*_p.xml'], # not sure if we should use recursive globbing or not. 
        "TAB": ['*table*.xml'],
        "TIL": ['*article-meta/*title-group.xml'],}

        self.dict_of_ami_dict = {
        'EO_ACTIVITY': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/activity/eo_activity.xml',
        'EO_COMPOUND': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/compound/eo_compound.xml',
        'EO_ANALYSIS': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/analysis/eo_analysis_method.xml',
        'EO_EXTRACTION': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/extraction/eo_extraction.xml',
        'EO_PLANT': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/plant/eo_plant.xml',
        'PLANT_GENUS': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/plant_genus/plant_genus.xml',
        'EO_PLANT_PART': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/plant_part/plant_part.xml',
        'EO_TARGET': 'https://raw.githubusercontent.com/petermr/dictionary/main/cevopen/target/eo_target_organism.xml',
        'COUNTRY': 'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/country/country.xml',
        'DISEASE':'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/disease/disease.xml',
        'ORGANIZATION': 'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/organization/organization.xml',
        'DRUG': 'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/drug/drug.xml',
        'TEST_TRACE': 'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/test_trace/test_trace.xml' }

        self.all_paragraphs={}
        self.sentence_dictionary={}
        self.spacy_model='spacy'
        self.nlp = None

    def switch_spacy_versions(self,spacy_type):
        logging.info(f'Loading {spacy_type}')
        if spacy_type=="scispacy":
            from scispacy.abbreviation import AbbreviationDetector
            try:
                self.nlp = spacy.load('en_ner_bc5cdr_md')
            except OSError:
                install('https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_ner_bc5cdr_md-0.4.0.tar.gz')
                self.nlp = spacy.load('en_ner_bc5cdr_md')
            self.nlp.add_pipe("abbreviation_detector")
        elif spacy_type=="spacy":
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                from spacy.cli import download
                download('en_core_web_sm')
                self.nlp = spacy.load('en_core_web_sm')

    def dictionary_to_html(self,html_path):
        list_of_docs=[]
        for sentence in self.sentence_dictionary:
            list_of_docs.append(self.sentence_dictionary[sentence]['doc'])
        html= displacy.render(list_of_docs, style="ent", page=True,minify=True)
        logging.info(f"saving output: {html_path}")
        self.write_string_to_file(html,html_path)

    def extract_entities_from_papers(self, corpus_path, terms_xml_path, search_section,entities,query=None, hits=30,
                                     run_pygetpapers=False, make_section=False, removefalse=True, 
                                     csv_name=False, make_ami_dict=False,spacy_model=False,html_path=False, synonyms=False, make_json=False):
        self.spacy_model=spacy_model                             
        corpus_path=os.path.abspath(corpus_path)
        if run_pygetpapers:
            if not query:
                logging.warning("please provide query (like 'terpene', 'essential oils') as parameter")
                return
            self.run_pygetpapers(query, hits, corpus_path)
        if os.path.isdir(corpus_path):
            if make_section:
                self.run_ami_section(corpus_path)
        else:
            logging.error("CProject doesn't exist")
            return
        if len(glob(os.path.join(corpus_path, '**', 'sections')))>0:
            self.all_paragraphs = self.get_glob_for_section(corpus_path,search_section)
        else:
            logging.error('section papers using --run_sectioning before search')
        if spacy_model or csv_name or make_ami_dict:
            self.make_dict_with_parsed_xml()
        if spacy_model:
            self.run_spacy_over_sections(self.sentence_dictionary,entities)
            self.remove_statements_not_having_xmldict_entities(
                        dict_with_parsed_xml=self.sentence_dictionary)
        if terms_xml_path:
            terms = self.get_terms_from_ami_xml(terms_xml_path)
            self.add_if_file_contains_terms(
                terms=terms, dict_with_parsed_xml=self.sentence_dictionary)
            if removefalse:
                self.remove_statements_not_having_xmldict_terms(
                    dict_with_parsed_xml=self.sentence_dictionary)
            if synonyms:
                synonyms_list = self.get_synonyms_from_ami_xml(terms_xml_path)
                self.add_if_file_contains_terms(
                    terms=synonyms_list, dict_with_parsed_xml=self.sentence_dictionary, searching='synonyms')
                if removefalse:
                    self.remove_statements_not_having_xmldict_terms(
                        dict_with_parsed_xml=self.sentence_dictionary)
                if html_path:
                    self.dictionary_to_html(os.path.join(corpus_path,html_path))
        if csv_name:
            self.convert_dict_to_csv(
                path=os.path.join(corpus_path, f'{csv_name}'), dict_with_parsed_xml=self.sentence_dictionary)
        if make_json:
            self.convert_dict_to_json(path=os.path.join(corpus_path, f'{make_json}'), dict_with_parsed_xml=self.sentence_dictionary)
        if make_ami_dict:
            ami_dict_path = os.path.join(corpus_path,make_ami_dict)
            self.handle_ami_dict_creation(self.sentence_dictionary,ami_dict_path)
        
        return self.sentence_dictionary
    
    def run_pygetpapers(self,QUERY, HITS, OUTPUT):
        pygetpapers_call=Pygetpapers()
        pygetpapers_call.run_command(query=QUERY,limit=HITS,output=OUTPUT,xml=True)
        logging.info(f"making CProject {OUTPUT} with {HITS} papers on {QUERY}")

    def run_ami_section(self, path):
        file_list= glob(os.path.join(
            path, '**','fulltext.xml'), recursive=True)
        for paper in file_list:
            xml_file=open(paper,'r')
            xml_string=xml_file.read()
            xml_file.close()
            if len(xml_string)>0:
                outdir = Path(Path(paper).parent, "sections")
                AMIAbsSection.make_xml_sections(paper, outdir, True)
            else:
                logging.warning(f"{paper} is empty")

    
    def get_glob_for_section(self,path,section_names):
        for section_name in section_names:
            if section_name in self.sections.keys():
                self.all_paragraphs[section_name]=[]
                for section in self.sections[section_name]:
                    self.all_paragraphs[section_name]+= glob(os.path.join(
                    path, '**', 'sections', '**', section), recursive=True)
            else:
                logging.error("please make sure that you have selected only the supported sections: ACK, AFF, AUT, CON, DIS, ETH, FIG, INT, KEY, MET, RES, TAB, TIL")
        return self.all_paragraphs


    def make_dict_with_parsed_xml(self):

        self.sentence_dictionary = {}
        
        counter = 1
        for section in self.all_paragraphs:
            for section_path in tqdm(self.all_paragraphs[section]):
                paragraph_path = section_path
                paragraph_text = self.read_text_from_path(paragraph_path)
                sentences = tokenize.sent_tokenize(paragraph_text)
                for sentence in sentences:
                    self.sentence_dictionary[counter] = {}
                    dict_for_sentences = self.sentence_dictionary[counter]
                    dict_for_sentences["file_path"] = section_path
                    dict_for_sentences["paragraph"] = paragraph_text
                    dict_for_sentences["sentence"] = sentence
                    dict_for_sentences["section"] = section
                    counter += 1
        logging.info(f"Found {len(self.sentence_dictionary)} sentences in the section(s).")
        return self.sentence_dictionary

    def read_text_from_path(self, paragraph_path):
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

    def run_spacy_over_sections(self, dict_with_parsed_xml,entities_names):
        self.switch_spacy_versions(self.spacy_model)
        for paragraph in tqdm(dict_with_parsed_xml):
            if len(dict_with_parsed_xml[paragraph]['sentence'])>0:
                doc = self.nlp(dict_with_parsed_xml[paragraph]['sentence'])
                entities, labels, position_end, position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end = self.make_required_lists()
                if self.spacy_model=="scispacy":
                    self._get_abbreviations(doc, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end)
                self._get_entities(entities_names, doc, entities, labels, position_end, position_start)
                self.add_lists_to_dict(dict_with_parsed_xml[paragraph], entities, labels, position_end,
                                    position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end)
                dict_with_parsed_xml[paragraph]['doc'] = doc

    def _get_entities(self, entities_names, doc, entities, labels, position_end, position_start):
        for ent in doc.ents:
            if (ent.label_ in entities_names) or (entities_names==['ALL']):
                self.add_parsed_entities_to_lists(
                        entities, labels, position_end, position_start, ent)

    def _get_abbreviations(self, doc, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end):
        for abrv in doc._.abbreviations:
            abbreviations.append(abrv)
            abbreviations_longform.append(abrv._.long_form)
            abbreviation_start.append(abrv.start)
            abbreviation_end.append(abrv.end)

    def add_if_file_contains_terms(self, terms, dict_with_parsed_xml, searching='terms'):

        for statement in tqdm(dict_with_parsed_xml):
            dict_for_sentence = dict_with_parsed_xml[statement]
            dict_for_sentence[f'has_{searching}'] = []
            term_list, frequency = self.is_phrase_in_using_regex(terms, dict_for_sentence['sentence'])
            if term_list:
                print(term_list)
                dict_for_sentence[f'has_{searching}'].append(term_list)
                dict_for_sentence[f'weight_{searching}'] = frequency
        
    def is_phrase_in(self, phrases, text):
        token_list = []
        text = text.lower()
        for phrase in phrases: 
            phrase.lower().strip()
            rule = pp.ZeroOrMore(pp.Keyword(phrase))
            for token, start, end in rule.scanString(text):
                if token:
                    token_list.append(token[0])
            frequency = (len(token_list))
        return token_list, frequency
    
    def is_phrase_in_using_regex(self, phrases, text):
        match_list = []
        for phrase in phrases:
            if re.search(r"\b{}\b".format(phrase), text, re.IGNORECASE) is not None:
                match_list.append(phrase)
        frequency = len(match_list)
        return match_list, frequency


    def get_terms_from_ami_xml(self, xml_path):
        if xml_path in self.dict_of_ami_dict.keys():
            logging.info(f"getting terms from {xml_path}")
            tree = ET.parse(urlopen(self.dict_of_ami_dict[xml_path]))
        #elif xml_path not in self.dict_of_ami_dict.keys():
        #    logging.error(f'{xml_path} is not a supported dictionary. Choose from: EO_ACTIVITY, EO_COMPOUND, EO_EXTRACTION, EO_PLANT, EO_PLANT_PART, PLANT_GENUS,EO_TARGET, COUNTRY, DISEASE, DRUG, ORGANIZATION ')
        else:
            logging.info(f"getting terms from {xml_path}")
            tree = ET.parse(xml_path)
            root = tree.getroot()
            terms = []
            for para in root.iter('entry'):
                terms.append(para.attrib["term"])
            return terms

    def get_synonyms_from_ami_xml(self, xml_path):
        if xml_path in self.dict_of_ami_dict.keys():
            logging.info(f"getting synonyms from {xml_path}")
            tree = ET.parse(urlopen(self.dict_of_ami_dict[xml_path]))
        elif xml_path not in self.dict_of_ami_dict.keys():
            logging.error(f'{xml_path} is not a supported dictionary. Choose from: EO_ACTIVITY, EO_COMPOUND, EO_EXTRACTION, EO_PLANT, EO_PLANT_PART, PLANT_GENUS,EO_TARGET, COUNTRY, DISEASE, DRUG, ORGANIZATION ')
        else:
            logging.info(f"getting synonyms from {xml_path}")
            tree = ET.parse(xml_path)
        root = tree.getroot()
        root = tree.getroot()
        synonyms = []
        for synonym in (root.findall("./entry/synonym")):
            synonyms.append(synonym.text)
        return synonyms

    def make_required_lists(self):
        abbreviations=[]
        abbreviations_longform=[]
        abbreviation_start=[]
        abbreviation_end=[]
        entities = []
        labels = []
        position_start = []
        position_end = []
        return entities, labels, position_end, position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end

    def add_lists_to_dict(self, dict_for_sentence, entities, labels, position_end,
                                   position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end):

        dict_for_sentence['entities'] = entities
        dict_for_sentence['labels'] = labels
        dict_for_sentence['position_start'] = position_start
        dict_for_sentence['position_end'] = position_end
        dict_for_sentence['abbreviations']= abbreviations
        dict_for_sentence['abbreviations_longform']= abbreviations_longform
        dict_for_sentence['abbreviation_start']= abbreviation_start
        dict_for_sentence['abbreviation_end']= abbreviation_end

    def add_parsed_entities_to_lists(self, entities, labels, position_end, position_start, ent=None):
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

    def convert_dict_to_json(self, path, dict_with_parsed_xml):
        with open(path ,mode='w', encoding='utf-8') as f:
             json.dump(dict_with_parsed_xml, f, indent = 4)
        logging.info(f"wrote JSON output to {path}")
        


    def remove_statements_not_having_xmldict_terms(self, dict_with_parsed_xml, searching='terms'):
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[statement]
            if len(sentect_dict[f'has_{searching}']) == 0 :
                statement_to_pop.append(statement)

        for term in statement_to_pop:
            dict_with_parsed_xml.pop(term)
    
    def remove_statements_not_having_xmldict_entities(self, dict_with_parsed_xml):
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[statement]
            if len(sentect_dict['entities']) == 0:
                statement_to_pop.append(statement)

        for term in statement_to_pop:
            dict_with_parsed_xml.pop(term)

    @staticmethod
    def extract_particular_fields(dict_with_parsed_xml, field):
        field_list = []
        for sentence in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[sentence]
            for entity, label in zip(sentect_dict['entities'], sentect_dict['labels']):
                if label == field:
                    if entity not in field_list:
                        field_list.append(entity)
        return field_list

    def make_ami_dict_from_list(self,list_of_terms_with_count,title):
        dictionary_element=  etree.Element("dictionary")
        dictionary_element.attrib['title']=title
        for term in list_of_terms_with_count:
            try:
                entry_element=etree.SubElement(dictionary_element,"entry")
                entry_element.attrib['term']=term[0]
                entry_element.attrib['count']=str(term[1])
            except Exception as e:
                logging.error(f"Couldn't add {term} to amidict")
        return etree.tostring(dictionary_element, pretty_print=True).decode('utf-8')
    
    def write_string_to_file(self,string_to_put,title):
        with open(title,mode='w', encoding='utf-8') as f:
            f.write(string_to_put)
    
    def handle_ami_dict_creation(self,result_dictionary,title):
        list_of_entities=[]
        for entry in result_dictionary:
            if 'entities' in result_dictionary[entry]:
                entity = result_dictionary[entry]['entities']
                list_of_entity_strings  = [i.text for i in entity]
                list_of_entities.extend(list_of_entity_strings)
        dict_of_entities_with_count = Counter(list_of_entities)
        list_of_terms_with_count= dict_of_entities_with_count.most_common()
        xml_dict = self.make_ami_dict_from_list(list_of_terms_with_count,title)
        self.write_string_to_file(xml_dict,f'{title}.xml')
        logging.info("Wrote all the entities extracted to ami dict")