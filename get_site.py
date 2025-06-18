import json

from metainfo.scraper import get_company_metadata

file_name = input("file name:")
with open(f"input/{file_name}", 'r', encoding='utf-8-sig') as f:
    data = json.load(f)
for index in range(len(data)):
    if data[index]['url'] or not data[index]['linkedin']:
        continue
    try:
        meta = get_company_metadata(data[index]['linkedin'])
        data[index]['url'] = meta.get('Веб-сайт')
        print(f"[{index}/{len(data)}] {data[index]['url']} | {data[index]['title']}")
        if index % 10 == 0:
            with open(f"output/{file_name}", 'w', encoding='utf-8-sig') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e)
