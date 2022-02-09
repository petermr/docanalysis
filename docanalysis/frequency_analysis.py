
import xml.etree.ElementTree as ET
import os
from collections import Counter

def get_terms_from_ami_xml(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()
    terms = []
    for para in root.iter('entry'):
        terms.append(para.attrib["term"])
    return terms

def frequency_counter(terms):
    frequency = {}

    # iterating over the list
    for item in terms:
    # checking the element in dictionary
        if item in frequency:
            # incrementing the counr
            frequency[item] += 1
        else:
            # initializing the count
            frequency[item] = 1

    # printing the frequency
    print(Counter(frequency).most_common())


xml_path = os.path.join(os.getcwd(), 'ami_dict.xml')
def main():
    terms = get_terms_from_ami_xml(xml_path)
    frequency_counter(terms)

main()