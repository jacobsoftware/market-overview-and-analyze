import os
import json

def save_or_update_json(path:str, dict_to_json:dict) -> None:

    if os.path.isfile(path):
        loaded_json = load_json(path)
        loaded_json.update(dict_to_json)
        with open(path, 'w') as save_hrefs:
            json.dump(loaded_json,save_hrefs,sort_keys=True,indent=4,separators=(',', ': '))
    else:
        with open(path, 'w') as save_hrefs:
            json.dump(dict_to_json,save_hrefs,sort_keys=True,indent=4,separators=(',', ': '))

def load_json(file:str) -> list:
    with open(file, 'r') as json_file:
        key = json.load(json_file)
        return key