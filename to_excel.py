import json
import os
from pathlib import Path

from openpyxl.workbook import Workbook


def save_dict_to_excel(worksheet, data):
    wb = Workbook()
    ws = wb.active

    # Записываем заголовки (ключи из первого словаря)
    headers = list(data[0].keys())
    ws.append(headers)

    # Записываем данные
    for row in data:
        ws.append([row.setdefault(key, None) for key in headers])

    wb.save(str(worksheet).replace(".json", '') + '.xlsx')

def main():
    input_dir = Path("searches")
    output_dir = Path("results")

    os.makedirs(output_dir, exist_ok=True)

    with open(input_dir / "Huntignton Beach CA Manufacturing 1-10.json", "r", encoding='utf-8') as f:
        data = json.load(f)
    save_dict_to_excel(Path(output_dir) / data['name'], data['results'])

if __name__ == '__main__':
    main()