from bs4 import BeautifulSoup
from glob import glob
import os
from abbreviations import schwartz_hearst

def read_text_from_html(paragraph_path):
    with open(paragraph_path, encoding="utf-8") as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        for div_ipcc in soup.find_all("div"):
            paragraph_text = div_ipcc.text
            return paragraph_text

def get_glob(corpus_path):
    paragraph_path = glob(os.path.join(corpus_path, '**', 'sections', '**', "*html"), recursive=True)
    return paragraph_path

def does_everything(corpus_path):
    all_paragraph_paths = get_glob(corpus_path)
    for paragraph_path in all_paragraph_paths:
        print(paragraph_path)
        paragraph_text = read_text_from_html(paragraph_path)
        abbs = abbreviation_search_using_sw(paragraph_text)
        print(abbs)


def abbreviation_search_using_sw(paragraph_text):
    pairs = schwartz_hearst.extract_abbreviation_definition_pairs(doc_text=paragraph_text)
    return pairs

path = os.path.join(os.path.expanduser('~'), "ipcc_sectioned")
does_everything(path)