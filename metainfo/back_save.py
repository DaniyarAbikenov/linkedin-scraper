import json

from scraper import save_dict_to_excel

with open("backups/Irvine, CA, Manufactoring 1-10.xlsx.json", 'r', encoding='utf8') as f:
    data = json.load(f)
save_dict_to_excel("output/Irvine, CA, Manufactoring 1-10.xlsx", data)