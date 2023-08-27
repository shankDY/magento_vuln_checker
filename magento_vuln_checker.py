import requests
import re
import concurrent.futures

# Метод для поиска версии Magento в тексте ответа
def find_magento_version(response_text, url):
    version_pattern = re.compile(r'Magento\s+([0-9]+\.[0-9]+\.[0-9]+)')
    match = version_pattern.search(response_text)
    
    if match:
        return match.group(1)
    else:
        return fetch_version_from_endpoint(url)


# Метод для получения версии Magento из эндпоинта
def fetch_version_from_endpoint(url):
    endpoint_url = f"{url}/magento_version"
    try:
        response = requests.get(endpoint_url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        return "Не удалось получить точную версию."


# Чекаем статический файл, если он есть, значит версия magento => 2.4.4.
def check_static_file(url):
    static_file_url = f"{url}/static/adminhtml/Magento/backend/en_US/tiny_mce_5/tinymce.min.js"
    response = requests.head(static_file_url)

    return False if response.status_code == 404 else True

# Метод для обработки одного URL
def process_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        magento_version = find_magento_version(response.text, url)
        static_check_result = check_static_file(url)
        
        display_results(url, magento_version, static_check_result)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == 403:
            next
        else:
            next


def display_results(url, magento_version, static_check_result):
    if static_check_result == False:
        print(f"Анализ URL: {url}")
        print("======================================\n")
        print(f"Версия Magento: {magento_version}\n")
        print("Версия Magento меньше 2.4.4, и c высокой вероятностью является уязвимой к CVE-2022-24086\n")
        print("======================================\n")


'''
Метод для обработки url из списка
Используются ThreadPoolExecutor для параллельной обработки URL. Максимальное количество рабочих потоков ограничено max_workers=10
'''
def process_urls_from_file(file_path):
    with open(file_path, "r") as file:
        urls = [line.rstrip() for line in file]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_url, urls)

if __name__ == "__main__":
    option = input("Выберите опцию (1 - проверка одного URL, 2 - проверка из файла): ")
    
    if option == "1":
        target_url = input("Введите URL сайта для поиска версии Magento: ")
        process_url(target_url)
    elif option == "2":
        file_path = input("Введите путь к файлу с URL: ")
        process_urls_from_file(file_path)
    else:
        print("Неверная опция. Выход.")
