import pandas as pd
import logging

class Util:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

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
