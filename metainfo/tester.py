import pandas as pd
import requests
from fake_headers import Headers


# Путь к Excel-файлу
excel_file_path = "output/" + input("file_name:")

# Имя столбца, в котором хранится URL
url_column_name = "Веб-сайт"

# Имя столбца, куда будет записываться результат
availability_column_name = "Availability"
headers = Headers(os="mac", headers=True).generate()


def check_website_availability(url: str) -> bool:
    """
    Проверяет доступность сайта по HTTP или HTTPS.
    Возвращает True, если сайт доступен хотя бы по одному протоколу,
    иначе False.
    """
    # Удаляем возможные лишние пробелы в URL
    url = url.strip()

    # Если в URL уже указан http:// или https://, убираем их,
    # чтобы избежать дублирования протокола при подстановке ниже
    url = url.replace("http://", "").replace("https://", "").strip()

    # Формируем URL-адреса для проверки
    http_url = f"http://{url}"
    https_url = f"https://{url}"

    for test_url in [http_url, https_url]:
        try:
            # Пытаемся выполнить GET-запрос
            response = requests.get(test_url, timeout=10, headers=headers)
            print(test_url, "|", response.status_code)
            # Если ответ 200 (OK), считаем, что ресурс доступен
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            # Игнорируем любые ошибки соединения и переходим к следующему протоколу
            pass

    return False


def main():
    # Считываем Excel-файл в DataFrame
    df = pd.read_excel(excel_file_path)

    # Проверяем, что столбец с URL существует
    if url_column_name not in df.columns:
        print(f"Столбец '{url_column_name}' не найден в файле Excel."
)
        return
    # Создаём или перезаписываем столбец с результатами
    df[availability_column_name] = df[url_column_name].apply(lambda x: "Available"
    if check_website_availability(str(x))
    else "Not Available")

    # Сохраняем результат в новый Excel-файл
    output_file_path = excel_file_path.replace("output/", 'output/checked/')
    df.to_excel(output_file_path, index=False)
    print(f"Проверка завершена. Результаты сохранены в '{output_file_path}'.")


if __name__ == "__main__":
    main()
