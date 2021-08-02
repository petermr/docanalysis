import os
import sys
import logging
from glob import glob
import spacy
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import xml.etree.ElementTree as ET
from spacy.matcher import PhraseMatcher
# os.system('pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_sm-0.4.0.tar.gz')
nlp = spacy.load("en_core_web_sm")


class EthicStatements:
    """ """

    def __init__(self):
        """[summary]
        """
        logging.basicConfig(level=logging.INFO)

    def extract_entities_from_papers(
        self, working_directory, QUERY, HITS, OUTPUT, TERMS_XML_PATH
    ):
        """[summary]
        :param working_directory: [description]
        :type working_directory: [type]
        :param QUERY: [description]
        :type QUERY: [type]
        :param HITS: [description]
        :type HITS: [type]
        :param OUTPUT: [description]
        :type OUTPUT: [type]
        :param TERMS_XML_PATH: [description]
        :type TERMS_XML_PATH: [type]
        """
        # self.install_ami()
        self.create_project_files(QUERY, HITS, OUTPUT)
        dict_with_parsed_xml = self.make_dict_with_pmcids(
            working_directory, OUTPUT)
        terms = self.get_terms_from_ami_xml(TERMS_XML_PATH)
        self.add_ethic_statements_to_dict(dict_with_parsed_xml)
        self.add_if_file_contains_terms(
            terms=terms, dict_with_parsed_xml=dict_with_parsed_xml
        )
        self.remove_tems_which_have_false_terms(
            dict_with_parsed_xml=dict_with_parsed_xml
        )
        self.sentence_based_phrase_matching(
            terms=terms, dict_with_parsed_xml=dict_with_parsed_xml
        )
        self.remove_sentences_not_having_terms(
            dict_with_parsed_xml=dict_with_parsed_xml
        )
        self.iterate_over_xml_and_populate_sentence_dict(
            dict_with_parsed_xml=dict_with_parsed_xml
        )
        self.make_rows_from_sentence_dict(
            dict_with_parsed_xml=dict_with_parsed_xml)
        self.convert_dict_to_csv(
            path=os.path.join(os.getcwd(), '../', 'temp', f"{OUTPUT}.csv"), dict_with_parsed_xml=dict_with_parsed_xml
        )

    def create_project_files(self, QUERY, HITS, OUTPUT):
        """[summary]
        :param QUERY: [description]
        :type QUERY: [type]
        :param HITS: [description]
        :type HITS: [type]
        :param OUTPUT: [description]
        :type OUTPUT: [type]
        """

        logging.info("querying EPMC using pygetpapers")
        os.system(f'pygetpapers -q "{QUERY}" -k {HITS} -o {OUTPUT} -x')
        logging.info("sectioning papers using java ami section")
        os.system(f"ami -p {OUTPUT} section")

    def install_ami(self):
        """ """

        os.system("git clone https://github.com/petermr/ami3.git")
        os.system("cd ami3")
        os.system("mvn install -Dmaven.test.skip=true")

    def make_dict_with_pmcids(self, working_directory, output):
        """[summary]
        :param working_directory: [description]
        :type working_directory: [type]
        :param output: [description]
        :type output: [type]
        :return: [description]
        :rtype: [type]
        """

        dict_with_parsed_xml = {}
        all_paragraphs = glob(
            os.path.join(
                working_directory, output, "*", "sections", "**", "*.xml"
            ),
            recursive=True,
        )
        for statement in tqdm(all_paragraphs):
            self.find_pmcid_from_file_name_and_make_dict_key(
                dict_with_parsed_xml, statement
            )
        logging.info(f"Found {len(dict_with_parsed_xml)} XML files")
        return dict_with_parsed_xml

    def find_pmcid_from_file_name_and_make_dict_key(
        self, dict_with_parsed_xml, paragraph_file
    ):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        :param paragraph_file: [description]
        :type paragraph_file: [type]
        """

        dict_with_parsed_xml[paragraph_file] = {}

    def add_ethic_statements_to_dict(self, dict_with_parsed_xml):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """

        logging.info(
            "populating the python dictionary with (ethics) paragraphs")

        for ethics_statement in tqdm(dict_with_parsed_xml):
            tree = ET.parse(ethics_statement)
            root = tree.getroot()
            self.add_parsed_xml(dict_with_parsed_xml, ethics_statement, root)

    def make_rows_from_sentence_dict(self, dict_with_parsed_xml):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        for statement in dict_with_parsed_xml:
            entities, labels, position_end, position_start, sentence_has_terms, sentences = self.initiate_lists()
            dict_for_statement = dict_with_parsed_xml[statement]
            dict_with_sentences = dict_for_statement["sentence_dict"]
            for sentence in dict_with_sentences:
                self.append_values_to_lists(dict_with_sentences, entities, labels, position_end,
                                            position_start, sentence, sentence_has_terms, sentences)
            self.add_lists_for_sentences_to_dict(dict_for_statement, entities, labels, position_end,
                                                 position_start, sentence_has_terms, sentences)
            dict_for_statement.pop("sentence_dict")

    def initiate_lists(self):
        """[summary]
        :return: [description]
        :rtype: [type]
        """
        sentences = []
        entities = []
        labels = []
        position_start = []
        position_end = []
        sentence_has_terms = []
        return entities, labels, position_end, position_start, sentence_has_terms, sentences

    def append_values_to_lists(self, dict_with_sentences, entities, labels, position_end,
                               position_start, sentence, sentence_has_terms, sentences):
        """[summary]
        :param dict_with_sentences: [description]
        :type dict_with_sentences: [type]
        :param entities: [description]
        :type entities: [type]
        :param labels: [description]
        :type labels: [type]
        :param position_end: [description]
        :type position_end: [type]
        :param position_start: [description]
        :type position_start: [type]
        :param sentence: [description]
        :type sentence: [type]
        :param sentence_has_terms: [description]
        :type sentence_has_terms: [type]
        :param sentences: [description]
        :type sentences: [type]
        """
        sentence_dict = dict_with_sentences[sentence]
        sentences.append(sentence)
        entities.append(sentence_dict["entities"])
        labels.append(sentence_dict["labels"])
        position_start.append(sentence_dict["position_start"])
        position_end.append(sentence_dict["position_end"])
        sentence_has_terms.append(sentence_dict["matched_phrases"])

    def add_lists_for_sentences_to_dict(self, dict_for_statement, entities=None, labels=None,
                                        position_end=None,
                                        position_start=None, sentence_has_terms=None, sentences=None):
        """[summary]
        :param dict_for_statement: [description]
        :type dict_for_statement: [type]
        :param entities: [description], defaults to False
        :type entities: bool, optional
        :param labels: [description], defaults to False
        :type labels: bool, optional
        :param position_end: [description], defaults to False
        :type position_end: bool, optional
        :param position_start: [description], defaults to False
        :type position_start: bool, optional
        :param sentence_has_terms: [description], defaults to False
        :type sentence_has_terms: bool, optional
        :param sentences: [description], defaults to False
        :type sentences: bool, optional
        """
        if sentences is not None:
            dict_for_statement["sentences"] = sentences
        if entities is not None:
            dict_for_statement["entities"] = entities
        if labels is not None:
            dict_for_statement["labels"] = labels
        if position_start is not None:
            dict_for_statement["position_start"] = position_start
        if position_end is not None:
            dict_for_statement["position_end"] = position_end
        if sentence_has_terms is not None:
            dict_for_statement["sentence_has_terms"] = sentence_has_terms

    def add_if_file_contains_terms(self, terms, dict_with_parsed_xml):
        """[summary]
        :param terms: [description]
        :type terms: [type]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        matcher = self.initiate_phrase_matcher(terms)

        logging.info("phrase matching at top level")

        for statement in tqdm(dict_with_parsed_xml):
            matched_phrases = []
            statement_dict = dict_with_parsed_xml[statement]
            statement_dict["has_terms"] = False
            statement_dict["weight"] = 0
            doc = nlp(statement_dict["parsed"])
            matches = matcher(doc)
            for match_id, start, end in matches:
                matched_span = doc[start:end]
                matched_phrases.append(matched_span.text)
                statement_dict["has_terms"] = matched_phrases
            statement_dict["weight"] = len(matched_phrases)

    def initiate_phrase_matcher(self, terms):
        """[summary]
        :param terms: [description]
        :type terms: [type]
        :return: [description]
        :rtype: [type]
        """
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp(text) for text in terms]
        matcher.add("TerminologyList", patterns)
        return matcher

    def sentence_based_phrase_matching(self, terms, dict_with_parsed_xml):
        """[summary]
        :param terms: [description]
        :type terms: [type]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        nlp = spacy.load("en_core_web_sm")
        logging.info(
            "splitting ethics statement containing paragraphs into sentences")
        logging.info("phrase matching at sentence level")
        for statement in tqdm(dict_with_parsed_xml):
            if len(dict_with_parsed_xml) == 0:
                logging.warning("No terms matching")
                sys.exit(1)
            sentence_dict = dict_with_parsed_xml[statement]
            sentences = self.split_in_sentences(
                sentence_dict["parsed"]
            )
            matcher = self.initiate_phrase_matcher(terms)
            sentence_dict["sentence_dict"] = {}
            for sentence in tqdm(sentences):
                self.add_matched_phrases_for_sentence(
                    matcher, nlp, sentence, sentence_dict)

    def add_matched_phrases_for_sentence(self, matcher, nlp, sentence, sentence_dict):
        """[summary]
        :param matcher: [description]
        :type matcher: [type]
        :param nlp: [description]
        :type nlp: [type]
        :param sentence: [description]
        :type sentence: [type]
        :param sentence_dict: [description]
        :type sentence_dict: [type]
        """
        sentence_dict["sentence_dict"][sentence] = {}
        matched_phrases = []
        doc = nlp(sentence)
        matches = matcher(doc)
        for match_id, start, end in matches:
            matched_span = doc[start:end]
            matched_phrases.append(matched_span.text)
        sentence_dict["sentence_dict"][sentence][
            "matched_phrases"
        ] = matched_phrases

    @staticmethod
    def split_in_sentences(text):
        """[summary]
        :param text: [description]
        :type text: [type]
        :return: [description]
        :rtype: [type]
        """
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        return [str(sent).strip() for sent in doc.sents]

    @staticmethod
    def get_terms_from_ami_xml(xml_path):
        """[summary]
        :param xml_path: [description]
        :type xml_path: [type]
        :return: [description]
        :rtype: [type]
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()
        terms = []
        for para in root.iter("entry"):
            terms.append(para.attrib["term"])
        logging.info("getting terms from ami dictionary")
        return terms

    def iterate_over_xml_and_populate_sentence_dict(self, dict_with_parsed_xml):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        logging.info("named-entity recognition at sentence level")

        for ethics_statement in tqdm(dict_with_parsed_xml):
            sentence_dict = dict_with_parsed_xml[ethics_statement]["sentence_dict"]
            for sentence in tqdm(
                sentence_dict
            ):
                self.iterate_over_xml_and_populate_dict(
                    sentence, sentence_dict[sentence])

    def iterate_over_xml_and_populate_dict(
        self, dict_with_parsed_xml, dict_to_add_list_to,
    ):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        :param dict_to_add_list_to: [description]
        :type dict_to_add_list_to: [type]
        """
        doc = nlp(dict_with_parsed_xml)
        entities, labels, position_end, position_start = self.make_required_lists()
        for ent in doc.ents:
            self.add_parsed_entities_to_lists(
                entities, labels, position_end, position_start, ent
            )
        self.add_lists_for_sentences_to_dict(
            dict_to_add_list_to,
            entities=entities,
            labels=labels,
            position_end=position_end,
            position_start=position_start,
        )

    def add_parsed_xml(self, dict_with_parsed_xml, ethics_statement, root):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        :param ethics_statement: [description]
        :type ethics_statement: [type]
        :param root: [description]
        :type root: [type]
        """
        try:
            xmlstr = ET.tostring(root, encoding="utf8", method="xml")
            soup = BeautifulSoup(xmlstr, features="lxml")
            text = soup.get_text(separator=" ")
            dict_with_parsed_xml[ethics_statement]["parsed"] = text.replace(
                "\n", "")
        except:
            dict_with_parsed_xml[ethics_statement]["parsed"] = "empty"

    def make_required_lists(self):
        """[summary]
        :return: [description]
        :rtype: [type]
        """
        entities = []
        labels = []
        position_start = []
        position_end = []
        return entities, labels, position_end, position_start

    def add_parsed_entities_to_lists(
        self, entities, labels, position_end, position_start, ent=None
    ):
        """[summary]
        :param entities: [description]
        :type entities: [type]
        :param labels: [description]
        :type labels: [type]
        :param position_end: [description]
        :type position_end: [type]
        :param position_start: [description]
        :type position_start: [type]
        :param ent: [description], defaults to None
        :type ent: [type], optional
        """
        if ent.label_ == "ORG" or ent.label_ == "GPE":
            entities.append(ent)
            labels.append(ent.label_)
            position_start.append(ent.start_char)
            position_end.append(ent.end_char)

    def convert_dict_to_csv(self, path, dict_with_parsed_xml):
        """[summary]
        :param path: [description]
        :type path: [type]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """

        df = pd.DataFrame(dict_with_parsed_xml)
        df = df.T
        df.to_csv(path, encoding="utf-8", line_terminator="\r\n")
        logging.info(f"wrote output to {path}")

    def remove_tems_which_have_false_terms(self, dict_with_parsed_xml):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        statement_to_pop = []
        for statement in dict_with_parsed_xml:
            if dict_with_parsed_xml[statement]["has_terms"] == False:
                statement_to_pop.append(statement)

        for term in statement_to_pop:
            dict_with_parsed_xml.pop(term)

    def remove_sentences_not_having_terms(self, dict_with_parsed_xml):
        """[summary]
        :param dict_with_parsed_xml: [description]
        :type dict_with_parsed_xml: [type]
        """
        for statement in dict_with_parsed_xml:
            sentences_to_pop = []
            for sentence in dict_with_parsed_xml[statement]["sentence_dict"]:
                if (
                    len(
                        dict_with_parsed_xml[statement]["sentence_dict"][sentence][
                            "matched_phrases"
                        ]
                    )
                    == 0
                ):
                    sentences_to_pop.append(sentence)

            for sentence in sentences_to_pop:
                dict_with_parsed_xml[statement]["sentence_dict"].pop(sentence)


ethic_statement_creator = EthicStatements()
ethic_statement_creator.extract_entities_from_papers(
    os.getcwd(),
    "lantana",
    20,
    os.path.join(
        os.path.expanduser('~'), "ethics_statement_corpus_1000"
    ),
    os.path.join(
        os.getcwd(), "../", "ethics_dictionary", "ethics_key_phrases", "ethics_key_phrases.xml"
    ),
)


"""
Credits to Ayush Garg.
Shweata N. Hegde
"""
