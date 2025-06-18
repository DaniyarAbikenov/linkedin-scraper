import json

from to_excel import save_dict_to_excel

with open("output/Cannabis Manufacturing and Processing.json", 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
save_dict_to_excel("Cannabis Manufacturing and Processing.json", data)