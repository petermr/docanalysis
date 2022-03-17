from pathlib import Path

DOCANALYSIS_TOP = Path(__file__).parent.parent
print(DOCANALYSIS_TOP)
#EXISTING_CPROJECT = Path(DOCANALYSIS_TOP, 'stem_cell_research_300')
PMC_TEXT_FILE = Path(DOCANALYSIS_TOP, 'resources', 'test_pmc.text')
print(PMC_TEXT_FILE)