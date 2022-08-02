import os
from chardet import detect

# get file encoding type


def get_encoding_type(file):
    """

    :param file: 

    """
    with open(file, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)['encoding']


from_codec = get_encoding_type('entity_extraction.py')

# add try: except block for reliability
try:
    with open('entity_extraction.py', 'r', encoding=from_codec) as f, open('entity_extraction2.py', 'w', encoding='utf-8') as e:
        text = f.read()  # for small files, for big use chunks
        e.write(text)


except UnicodeDecodeError:
    print('Decode Error')
except UnicodeEncodeError:
    print('Encode Error')
