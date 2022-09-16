import requests
from pprint import pprint
params = {
    "action": "wbsearchentities",
    "search": "Global warming",
    "language": "en",
    "format": "json"
}
data = requests.get(
    "https://www.wikidata.org/w/api.php", params=params)
result = data.json()
hit_list = []
for hit in result['search']:
    try:
        if "scientific article" not in hit["description"]:
            hit_list.append(hit["id"])
    except:
        hit_list.append(hit["id"])
print(hit_list)