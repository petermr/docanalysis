import xml.etree.ElementTree as ET
import logging
import yake

class CreateReadDict:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def get_terms_from_ami_xml(self, xml_path):

        tree = ET.parse(xml_path)
        root = tree.getroot()
        terms = []
        for para in root.iter('entry'):
            terms.append(para.attrib["term"])
        logging.info(f"reading terms from dictionary {xml_path}")
        return terms

    def key_phrase_extraction(self, section, dict_with_parsed_xml):
        dict_with_parsed_xml["yake_keywords"] = []
        for text in dict_with_parsed_xml[f"{section}"]:
            custom_kw_extractor = yake.KeywordExtractor(
                lan='en', n=2, top=10, features=None)
            keywords = custom_kw_extractor.extract_keywords(text)
            keywords_list = []
            for kw in keywords:
                keywords_list.append(kw[0])
            dict_with_parsed_xml["yake_keywords"].append(keywords_list)
        logging.info(f'extracted key phrases from {section}')
        return dict_with_parsed_xml

