# Data parsing

Создадим парсер внутренних ссылок сайта:
1.	Задаем URL. Парсер должен получить ссылки данной страницы.
2.	Пройти все эти ссылки.
3.	На пройденных страницах снова собрать ссылки.

Для этого предварительно установим драйвер chromedriver для Chrome Selenium: мы должны установить именно ту версию, которая была бы совместима с установленным Google Chrome на нашем ПК или VDS.

Зайдем в настройки Google Chrome, чтобы посмотреть его версию.

Переходим на сайт [установщика](https://sites.google.com/a/chromium.org/chromedriver/downloads) и скачиваем нужную версию.

Устанавливаем необходимые библиотеки через <i>pip</i>:

Для парсинга:

    pip install selenium
    pip install lxml
    pip install url
    pip install bs4
    pip install requests


Для создания датафрейма и добавления туда результатов:

    pip install pandas

Пишем код.

## Код программы:

    from __future__ import division
    from __future__ import absolute_import
    from __future__ import print_function
    from __future__ import unicode_literals
    from selenium import webdriver
    from lxml import html
    from selenium.webdriver import DesiredCapabilities
    from urllib.parse import urlparse
    from bs4 import BeautifulSoup
    import requests
    import pandas as pd
    from time import time

    DOMAIN = 'sbergraduate.ru'
    HOST = 'http://' + DOMAIN
    FORBIDDEN_PREFIXES = ['#', 'tel:', 'mailto:']
    links = set() # множество всех ссылок
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(HOST, headers=headers)
    # print(response.content)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--user-data-dir=C:/Users/Vadim/PycharmProjects/untitled") # директория сохранения профиля
    dcap = dict(DesiredCapabilities.CHROME)
    chrome = webdriver.Chrome('C:\\Users\\Vadim\\Downloads\\chromedriver_win32\\chromedriver.exe')

    # прогружаем в браузере сайт
    chrome.get(HOST)
    # список времнени открытия доменов в секундах
    times = []

    def add_all_links_recursive(url, maxdepth=1):
        #print('{:>5}'.format(len(links)), url[len(HOST):])

        #глубина рекурсии не более `maxdepth`

        # список ссылок, от которых в конце мы рекурсивно запустимся
        links_to_handle_recursive = []
        #получаем html код страницы
        request = requests.get(url, headers=headers)
        # парсим его с помощью BeautifulSoup
        soup = BeautifulSoup(request.content, 'lxml')
        # рассматриваем все теги <a>, при том, что href - не пустые
        for tag_a in soup.find_all('a', href=lambda v: v is not None):
            link = tag_a['href']

            # если ссылка не начинается с одного из запрещенных префиксов
            if all(not link.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
                # проверяем, является ли ссылка относительной
                # например, `/oplata` - это относительная ссылка
                # `http://101-rosa.ru/oplata - это абсолютная ссылка
                if link.startswith('/') and not link.startswith('//'):
                    # преобразуем относительную ссылку в абсолютную
                    link = HOST + link
                # проверяем, что ссылка ведет на нужный домен
                # и что мы еще' не обрабатывали такую ссылку
                if urlparse(link).netloc == DOMAIN and link not in links:
                    links.add(link)
                    links_to_handle_recursive.append(link)

        if maxdepth > 0:
            for link in links_to_handle_recursive:
                add_all_links_recursive(link, maxdepth=maxdepth - 1)

    def main():
        print("\n Происходит выгрузка доменов сайта " + DOMAIN)
        urls = []
        total_time = 0
        add_all_links_recursive(HOST + '/')
        for link in links:
            start = time()
            # прогружаем в браузере каждый домен
            result = chrome.get(link)
            end = time()
            urls.append(link)
            times.append(end - start)
            s = end - start;
            total_time += s

        print("\n")
        # Ограничение вывода строк - максимум 10 000 (чтобы не выводило многоточия)
        pd.options.display.max_rows = 10000
        df = pd.DataFrame({'Домен': urls, 'Время открытия, сек': times})
        writer = pd.ExcelWriter('C:/Users/Vadim/Desktop/Data parsing/домены.xlsx')
        df.to_excel(writer, 'Лист1')
        writer.save()
        print(" Домены с временем их открытия выгружены в таблицу Excel в папке проекта.\n Общее время загрузки составило", total_time , "сек")



    if __name__ == '__main__':
        main()


 ## Резюме
Сделали парсер, который фиксирует время открытия всех страниц сайта, поданного на вход. Для этого использовали библиотеки [Selenium](https://pypi.org/project/selenium/), [BeautifulSoup](https://pypi.org/project/bs4/) для парсинга, time для вычисления времени открытия страниц, [pandas](https://pandas.pydata.org/docs/) для создания датафрейма и добавления туда результатов и последующей выгрузкой в таблицу <i>Excel</i>.
