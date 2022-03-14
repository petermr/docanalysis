from distutils.log import error
import os
import logging
from glob import glob
import spacy
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
from lxml import etree
from pygetpapers.download_tools import DownloadTools
from urllib.request import urlopen
def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install', package])



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
        'DRUG': 'https://raw.githubusercontent.com/petermr/dictionary/main/openVirus20210120/drug/drug.xml',}

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
        logging.info("Saving html")
        download_tools=DownloadTools()
        df = pd.DataFrame.from_dict(self.sentence_dictionary)
        download_tools.make_html_from_dataframe(df,html_path)

    def extract_entities_from_papers(self, corpus_path, terms_xml_path, sections,entities,query=None, hits=30,
                                     run_pygetpapers=False, run_sectioning=False, removefalse=True, create_csv=True,
                                     csv_name='entities.csv', make_ami_dict=False,spacy_model='spacy',html_path=False):
        self.spacy_model=spacy_model                             
        corpus_path=os.path.abspath(corpus_path)
        if run_pygetpapers:
            if not query:
                logging.warning('Please provide query as parameter')
                return
            logging.info(f"making project/searching {query} for {hits} hits into {corpus_path}")
            self.run_pygetpapers(query, hits, corpus_path)
        if os.path.isdir(corpus_path):
            if run_sectioning:
                self.run_ami_section(corpus_path)
        else:
            logging.error("Corpus doesn't exist")
            return
        self.all_paragraphs = self.get_glob_for_section(corpus_path,sections)
        self.make_dict_with_parsed_xml()
        logging.info(f"getting terms from/to {terms_xml_path}")
        self.run_spacy_over_sections(self.sentence_dictionary,entities)
        self.remove_statements_not_having_xmldict_entities(
                    dict_with_parsed_xml=self.sentence_dictionary)
        if terms_xml_path:
            terms = self.get_terms_from_ami_xml(terms_xml_path)
            print(terms)
            self.add_if_file_contains_terms(
                terms=terms, dict_with_parsed_xml=self.sentence_dictionary)
            if removefalse:
                self.remove_statements_not_having_xmldict_terms(
                    dict_with_parsed_xml=self.sentence_dictionary)
        if create_csv:
            self.convert_dict_to_csv(
                path=os.path.join(corpus_path, f'{csv_name}'), dict_with_parsed_xml=self.sentence_dictionary)
        if make_ami_dict:
            ami_dict_path = os.path.join(corpus_path,make_ami_dict)
            self.handle_ami_dict_creation(self.sentence_dictionary,ami_dict_path)
        if html_path:
            self.dictionary_to_html(os.path.join(corpus_path,html_path))
        return self.sentence_dictionary
    
    def run_pygetpapers(self,QUERY, HITS, OUTPUT):
        pygetpapers_call=Pygetpapers()
        pygetpapers_call.run_command(query=QUERY,limit=HITS,output=OUTPUT,xml=True)

    def run_ami_section(self, path):
        file_list= glob(os.path.join(
            path, '**','fulltext.xml'), recursive=True)
        for paper in file_list:
            outdir = Path(Path(paper).parent, "sections")
            AMIAbsSection.make_xml_sections(paper, outdir, True)

    
    def get_glob_for_section(self,path,section_names):

        for section_name in section_names:
            if section_name in self.sections.keys():
                self.all_paragraphs[section_name]=[]
                for section in self.sections[section_name]:
                    self.all_paragraphs[section_name]+= glob(os.path.join(
                    path, '**', 'sections', '**', section), recursive=True)
            else:
                logging.error("Section not supported.")
            
        return self.all_paragraphs


    def make_dict_with_parsed_xml(self):

        self.sentence_dictionary = {}
        
        counter = 1
        logging.info(f"starting  tokenization on {len(self.all_paragraphs)} paragraphs")
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
        logging.info(f"Found {len(self.sentence_dictionary)} sentences")
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
            doc = self.nlp(dict_with_parsed_xml[paragraph]['sentence'])
            entities, labels, position_end, position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end = self.make_required_lists()
            if self.spacy_model=="scispacy":
                self._get_abbreviations(doc, abbreviations, abbreviations_longform, abbreviation_start, abbreviation_end)
            self._get_entities(entities_names, doc, entities, labels, position_end, position_start)
            self.add_lists_to_dict(dict_with_parsed_xml[paragraph], entities, labels, position_end,
                                   position_start,abbreviations,abbreviations_longform,abbreviation_start,abbreviation_end)

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
        if xml_path in self.dict_of_ami_dict.keys():
            tree = ET.parse(urlopen(self.dict_of_ami_dict[xml_path]))
        else:
            tree = ET.parse(xml_path)
        root = tree.getroot()
        terms = []
        for para in root.iter('entry'):
            terms.append(para.attrib["term"])
        return terms

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

    def remove_statements_not_having_xmldict_terms(self, dict_with_parsed_xml):
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            sentect_dict = dict_with_parsed_xml[statement]
            if len(sentect_dict['has_terms']) == 0 :
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
        logging.info("Wrote ami dict")