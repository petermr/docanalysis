import xml.etree.ElementTree as ET
import logging
import yake

class Dictionary:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def get_terms_from_ami_xml(self, dict_path):
        tree = ET.parse(dict_path)
        dict_root = tree.getroot()
        logging.info(f"reading terms from dictionary {dict_path}")
        terms = self.get_terms_from_entries(dict_root)
        return terms

    def get_terms_from_entries(self, root):
        """extract terms from entries in dictionary
        Args:
            root (): [description]

        Returns:
            [list]: list of terms
        """
        terms = []
        for para in root.iter('entry'):
            terms.append(para.attrib["term"])
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

