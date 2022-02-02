# test whether...
# Cproject exists (I)
# dictionary exists (I)
# sections exist (I)
# non-empty CSV exists (O)
# dictionary is created (not sure if we create two dictionaries (entities and keyphrases) can be created at the same time)
import pytest
from pathlib import Path
import os
import subprocess

DOCANALYSIS_TOP = Path(__file__).parent.parent
EXISTING_CPROJECT = Path(DOCANALYSIS_TOP, 'stem_cell_research_300')
DICT_DIRECTORY = Path(DOCANALYSIS_TOP, 'ethics_dictionary')
TEST_DICT = Path(DICT_DIRECTORY, 'ethics_demo', 'ethics_demo.xml')
TEMP_CPROJECT = Path(DOCANALYSIS_TOP, 'test_ethics_20')
HITS = 20

class TestDocanalysis:

    def test_cproject_exists(self):
        """asserts whether CProject directory exists
        """
        assert DOCANALYSIS_TOP.exists(), f"checking whether {DOCANALYSIS_TOP} exists"

    def test_pygetpapers_runs(self):
        """- checks whether 
            - the corpus directory exists or not
            - the number of PMC * folders is equal to the hits specified
            - fulltext xml exists in each PMC folder or not
        """
        os.system(f'docanalysis --run_pygetpapers --query ethics statement --hits {HITS} --project_name {TEMP_CPROJECT}')
        assert TEMP_CPROJECT.exists(), f"repository {TEMP_CPROJECT} must exist"
        assert len(list(TEMP_CPROJECT.glob('PMC*/'))) == HITS
        assert len(list(TEMP_CPROJECT.glob('PMC*/fulltext.xml'))) == HITS

    def test_section_exists(self):
        """checkers whether
            - the number of PMC folder with sections is equal to number of hits
            - section exists in each PMC folder
        # not sure if this is the right way of testing whether papers are sectioned    
        """

        f'docanalysis --project_name {TEMP_CPROJECT} --section'
        assert len(list(TEMP_CPROJECT.glob('PMC*/sections/'))) == HITS
        for PMC in TEMP_CPROJECT.glob('**/'):
            for section in PMC.glob('sections/'):
                assert section.name.exists()

    def test_search_dict_exists(self):
        """checks whether the dictionary directory exists or not
        """
        assert TEST_DICT.exists(), f"dictionary {TEST_DICT} must exist"

    def test_csv_output_creation(self):
        """checks whether the csv output is created or not
        """
        os.system(f'docanalysis --project_name {TEMP_CPROJECT} --dictionary {TEST_DICT} --entity_extraction --key_phrase_extraction')
        assert Path(TEMP_CPROJECT, 'entities_keyphrases.csv').exists, 'checking if the output is created'

    def test_subprocess(self):
        subprocess.run(f'pygetpapers --help', capture_output=True, text=True).stdout

    def test_dict_creation_entites(self):
        os.system(f'docanalysis --project_name {TEMP_CPROJECT} --dictionary {TEST_DICT} --entity_extraction --key_phrase_extraction --make_dictionary entities')
        assert Path(TEMP_CPROJECT, 'entities.xml').exists, 'checking if the entitty dictionary is created'

    def test_dict_creation_entites(self):
        os.system(f'docanalysis --project_name {TEMP_CPROJECT} --dictionary {TEST_DICT} --entity_extraction --key_phrase_extraction --make_dictionary keyphrases')
        assert Path(TEMP_CPROJECT, 'keyphrase.xml').exists, 'checking if the keyphrase dictionary is created'

    def test_remove_dir():
        import shutil
        shutil.rmtree(TEMP_CPROJECT)
        assert "Ran all the tests" == "Ran all the tests"