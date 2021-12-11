from pathlib import Path
import xml.etree.ElementTree as ET
from docanalysis.create_read_dictionary import Dictionary
DOCANALYSIS_TOP = Path(__file__).parent.parent
ETHICS_300 = Path(DOCANALYSIS_TOP, 'stem_cell_research_300')
print(ETHICS_300)
PAPERS_NUMBER = 300
DICT_DIRECTORY = Path(DOCANALYSIS_TOP, 'ethics_dictionary')
TEST_DICT = Path(DICT_DIRECTORY, 'ethics_demo', 'ethics_demo.xml')

class TestEthics:
    def setUp(self):
        """common resources
        """
        pass

    def test_ethics_dict(self):
        """checks whether the dictionary directory exists or not
        """
        assert TEST_DICT.exists(), f"dictionary {TEST_DICT} must exist"
    
    def test_ethics_dictionary_validity(self):
        pass
    
    def test_for_terms(self):
        dict_root = ET.parse(TEST_DICT)
        assert dict_root is not None
        terms = Dictionary.get_terms_from_entries(dict_root)
        assert terms is not None
        assert len(terms) == 7

    def test_ethics_corpus(self):
        """- checks whether 
             - the corpus directory exists or not
             - the number of PMC * folders is equal to the hits specified
             - fulltext xml exists in each PMC folder or not
        """
        assert ETHICS_300.exists(), f"repository {ETHICS_300} must exist"
        assert len(list(ETHICS_300.glob('PMC*/'))) == PAPERS_NUMBER
        assert len(list(ETHICS_300.glob('PMC*/fulltext.xml'))) == PAPERS_NUMBER

    def test_ethics_section(self):
        """checkers whether
            - the number of PMC folder with sections is equal to number of hits
            - section exists in each PMC folder
        # not sure if this is the right way of testing whether papers are sectioned    
        """
        assert len(list(ETHICS_300.glob('PMC*/sections/'))) == PAPERS_NUMBER
        for PMC in ETHICS_300.glob('**/'):
            for section in PMC.glob('sections/'):
                assert section.name.exists()

# ---------------------
    def utility(self):
        pass