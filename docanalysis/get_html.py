from bs4 import BeautifulSoup
from glob import glob
import os
from abbreviations import schwartz_hearst
from lxml import etree
import yake

def read_text_from_html(paragraph_path):
    """

    :param paragraph_path: 

    """
  with open(paragraph_path, 'r') as f:
      html = f.read()
      soup = BeautifulSoup(html, features="html.parser")

      # kill all script and style elements
      for script in soup(["script", "style"]):
          script.extract()    # rip it out

      # get text
      text = soup.get_text()

      # break into lines and remove leading and trailing space on each
      #lines = (line.strip() for line in text.splitlines())
      # break multi-headlines into a line each
      #chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
      # drop blank lines
      #text_write = '\n'.join(chunk for chunk in chunks if chunk)
      #text = '\n'.join(chunk for chunk in chunks if chunk)
      return text

def get_glob(corpus_path):
    """

    :param corpus_path: 

    """
    paragraph_path = glob(os.path.join(corpus_path, '**', 'sections', '**', "*html"), recursive=True)
    return paragraph_path

def abbreviation_search_using_sw(paragraph_text):
    """

    :param paragraph_text: 

    """
    pairs = schwartz_hearst.extract_abbreviation_definition_pairs(doc_text=paragraph_text)
    keys = pairs.keys()
    values = pairs.values()
    return keys, values

def make_ami_dict_from_list(title, keys, values):
    """

    :param title: 
    :param keys: 
    :param values: 

    """
    dictionary_element=  etree.Element("dictionary")
    dictionary_element.attrib['title']= title
    for term, expansion in zip(keys, values):
        entry_element=etree.SubElement(dictionary_element,"entry")
        entry_element.attrib['term']=term
        entry_element.attrib['exapansion']=expansion
    return etree.tostring(dictionary_element, pretty_print=True).decode('utf-8')

def write_string_to_file(string_to_put,title):
    """

    :param string_to_put: 
    :param title: 

    """
    with open(title,mode='w', encoding='utf-8') as f:
        f.write(string_to_put)
    print(f"wrote dict to {title}")

def extract_keyphrase(paragraph_text):
    """

    :param paragraph_text: 

    """
    custom_kw_extractor = yake.KeywordExtractor(lan='en', n=5, top=10, features=None)
    keywords = custom_kw_extractor.extract_keywords(paragraph_text)
    keywords_list = []
    for kw in keywords:
        keywords_list.append(kw[0])
    print(keywords_list)

def does_everything(corpus_path):
    """

    :param corpus_path: 

    """
    all_text = []
    all_keys = []
    all_values = []
    all_paragraph_paths = get_glob(corpus_path)
    for paragraph_path in all_paragraph_paths:
        paragraph_text = read_text_from_html(paragraph_path)
        #print(paragraph_text)
        all_text.append(paragraph_text)
        keys, values = abbreviation_search_using_sw(paragraph_text)
        all_keys.extend(keys)
        all_values.extend(values)
    print(len(all_keys), all_values)
    #all_text_string = joinStrings(all_text)
    #print(all_text_string)
    #extract_keyphrase(all_text_string)
    #dict_string = make_ami_dict_from_list("abb", all_keys, all_values)
    #return dict_string


def joinStrings(stringList):
    """

    :param stringList: 

    """
    return ''.join(string for string in stringList)

path = os.path.join(os.path.expanduser('~'), "ipcc_sectioned")
does_everything(path)
#write_string_to_file( dict_string, "abb.xml")

import json
from urllib.request import urlopen

#PATH = urlopen()
#json_dict = json.load(PATH)
#print(json_dict)

