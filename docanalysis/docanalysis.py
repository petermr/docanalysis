import logging
import os
from docanalysis.create_read_dictionary import CreateReadDict
from docanalysis.download_pre_process import DownloadPapers
from docanalysis.parse_sections import ParseSections
from docanalysis.util import Util
from docanalysis.get_entities import GetEntities

class DocAnalysis:
    """ """

    def __init__(self):
        self.labels_to_get = []
        logging.basicConfig(level=logging.INFO)

    def extract_entities_from_papers(self, corpus_path, terms_xml_path, query=None, hits=30,
                                     make_project=False, removefalse=True, create_csv=True,
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
            DownloadPapers.create_project_files(query, hits, corpus_path)

        logging.info(f"dict with parsed xml in {corpus_path}")
        dict_with_parsed_xml = ParseSections.make_dict_with_parsed_xml(corpus_path)

        logging.info(f"getting terms from/to {terms_xml_path}")
        logging.info(f"add parsed_sections to dict: {len(dict_with_parsed_xml)}")
        GetEntities.add_parsed_sections_to_dict(dict_with_parsed_xml)
        logging.info(f"added parsed_sections to dict: {len(dict_with_parsed_xml)}")

        terms = CreateReadDict.get_terms_from_ami_xml(terms_xml_path)  # moved from (1)
        ParseSections.add_if_file_contains_terms(
            terms=terms, dict_with_parsed_xml=dict_with_parsed_xml)

        if removefalse:
            Util.remove_statements_not_having_xmldict_terms_or_entities(
                dict_with_parsed_xml=dict_with_parsed_xml)
        if create_csv:
            Util.convert_dict_to_csv(
                path=os.path.join(corpus_path, csv_name), dict_with_parsed_xml=dict_with_parsed_xml)
        return dict_with_parsed_xml