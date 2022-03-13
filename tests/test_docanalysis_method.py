import pytest
import glob
import os
from pathlib import Path
from ..docanalysis.extract_entities import DocAnalysis

DOCANALYSIS_TOP = Path(__file__).parent.parent
EXISTING_CPROJECT = Path(DOCANALYSIS_TOP, 'stem_cell_research_300')

class TestDocanalysisMeth():

    def test_cproject_exists(self):
        assert EXISTING_CPROJECT.exists(), f"checking whether {EXISTING_CPROJECT} exists"

    def test_glob_section(self):
        all_paragraphs = glob(os.path.join(
            EXISTING_CPROJECT, '*', 'sections', '**', '[1_9]_p.xml'), recursive=True)
        assert all_paragraphs is not None