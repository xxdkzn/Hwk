import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            function_name = old_function.__name__
            arguments = ", ".join(map(str, args)) + ", ".join(f"{k}={v}" for k, v in kwargs.items())
            result = old_function(*args, **kwargs)
            with open(path, 'a') as log_file:
                log_file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {function_name}({arguments}) -> {result}\n")
            return result
        return new_function
    return __logger

@logger('suitable_vacancies.log')
def get_suitable_vacancies(url):
    # URL для получения свежих вакансий по запросу "Python" в Москве и Санкт-Петербурге
    url = 'https://hh.ru/search/vacancy?area=1&area=2&text=python&order_by=publication_time'

    # Выполняем GET-запрос к странице
    response = requests.get(url)

    # Парсим HTML-код страницы
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все вакансии на странице
    vacancies = soup.find_all('div', class_='vacancy-serp-item')

    # Создаем список для хранения подходящих вакансий
    suitable_vacancies = []

    # Проходим по всем вакансиям
    for vacancy in vacancies:
        # Получаем ссылку на вакансию
        vacancy_link = vacancy.find('a', class_='serp-item__title')['href']

        # Получаем вилку заработной платы
        salary_info = vacancy.find('span', class_='bloko-header-2 bloko-header-2_lite')
        if salary_info:
            salary_range = salary_info.text
            # Проверяем, содержит ли вилка зарплаты доллары (USD)
            if 'USD' in salary_range:
                # Извлекаем числовые значения вилки зарплаты
                salary_numbers = re.findall(r'\d+', salary_range)
                if len(salary_numbers) == 2:
                    min_salary = int(salary_numbers[0])
                    max_salary = int(salary_numbers[1])
                else:
                    min_salary = int(salary_numbers[0])
                    max_salary = min_salary

                # Получаем название компании
                company_name = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text

                # Получаем город
                location = vacancy.find('span', class_='vacancy-serp-item__meta-info').text

                # Проверяем, есть ли в описании вакансии ключевые слова "Django" и "Flask"
                vacancy_description = vacancy.find('div', class_='g-user-content').get_text().lower()
                if 'django' in vacancy_description and 'flask' in vacancy_description:
                    # Добавляем вакансию в список подходящих
                    suitable_vacancies.append({
                        'vacancy_link': vacancy_link,
                        'salary_range': f'{min_salary} - {max_salary} USD',
                        'company_name': company_name,
                        'location': location
                    })

    # Записываем данные о подходящих вакансиях в JSON-файл
    with open('suitable_vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(suitable_vacancies, f, ensure_ascii=False, indent=4)

    return suitable_vacancies

if __name__ == '__main__':
    if os.path.exists('suitable_vacancies.log'):
        os.remove('suitable_vacancies.log')

    suitable_vacancies = get_suitable_vacancies(url)
    print(f'Найдено {len(suitable_vacancies)} подходящих вакансий. Данные записаны в файл suitable_vacancies.json.')