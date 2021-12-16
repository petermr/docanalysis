from docanalysis.parse_sections import ParseSections
import logging
import spacy
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    from spacy.cli import download
    download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class GetEntities:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
    
    def add_parsed_sections_to_dict(self, dict_with_parsed_xml):
        logging.basicConfig(level=logging.INFO)

        for paragraph in dict_with_parsed_xml:
            doc = nlp(dict_with_parsed_xml[paragraph]['sentence'])
            entities, labels, position_end, position_start = ParseSections.make_required_lists()
            for ent in doc.ents:
                self.add_parsed_entities_to_lists(
                    entities, labels, position_end, position_start, ent)
            self.add_lists_to_dict(dict_with_parsed_xml[paragraph], entities, labels, position_end,
                                   position_start)