from bs4 import BeautifulSoup
from glob import glob
import os
from abbreviations import schwartz_hearst
from lxml import etree

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

def abbreviation_search_using_sw(paragraph_text):
    pairs = schwartz_hearst.extract_abbreviation_definition_pairs(doc_text=paragraph_text)
    keys = pairs.keys()
    values = pairs.values()
    return keys, values

def make_ami_dict_from_list(title, keys, values):
    dictionary_element=  etree.Element("dictionary")
    dictionary_element.attrib['title']= title
    for term, expansion in zip(keys, values):
        entry_element=etree.SubElement(dictionary_element,"entry")
        entry_element.attrib['term']=term
        entry_element.attrib['exapansion']=expansion
    return etree.tostring(dictionary_element, pretty_print=True).decode('utf-8')

def write_string_to_file(string_to_put,title):
    with open(title,mode='w', encoding='utf-8') as f:
        f.write(string_to_put)
    print(f"wrote dict to {title}")

def does_everything(corpus_path):
    all_keys = []
    all_values = []
    all_paragraph_paths = get_glob(corpus_path)
    for paragraph_path in all_paragraph_paths:
        paragraph_text = read_text_from_html(paragraph_path)
        keys, values = abbreviation_search_using_sw(paragraph_text)
        all_keys.extend(keys)
        all_values.extend(values)
    dict_string = make_ami_dict_from_list("abb", all_keys, all_values)
    return dict_string

path = os.path.join(os.path.expanduser('~'), "ipcc_sectioned")
dict_string = does_everything(path)
write_string_to_file( dict_string, "abb.xml")