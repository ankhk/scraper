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
links = set() # ��������� ���� ������
headers = {
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
response = requests.get(HOST, headers=headers)
# print(response.content)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--user-data-dir=C:/Users/Vadim/PycharmProjects/untitled") # ���������� ���������� �������
dcap = dict(DesiredCapabilities.CHROME)
chrome = webdriver.Chrome('C:\\Users\\Vadim\\Downloads\\chromedriver_win32\\chromedriver.exe')

# ���������� � �������� ����
chrome.get(HOST)
# ������ �������� �������� ������� � ��������
times = []

def add_all_links_recursive(url, maxdepth=1):
    #print('{:>5}'.format(len(links)), url[len(HOST):])

    #������� �������� �� ����� `maxdepth`

    # ������ ������, �� ������� � ����� �� ���������� ����������
    links_to_handle_recursive = []
    #�������� html ��� ��������
    request = requests.get(url, headers=headers)
    # ������ ��� � ������� BeautifulSoup
    soup = BeautifulSoup(request.content, 'lxml')
    # ������������� ��� ���� <a>, ��� ���, ��� href - �� ������
    for tag_a in soup.find_all('a', href=lambda v: v is not None):
        link = tag_a['href']

        # ���� ������ �� ���������� � ������ �� ����������� ���������
        if all(not link.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
            # ���������, �������� �� ������ �������������
            # ��������, `/oplata` - ��� ������������� ������
            # `http://101-rosa.ru/oplata - ��� ���������� ������
            if link.startswith('/') and not link.startswith('//'):
                # ����������� ������������� ������ � ����������
                link = HOST + link
            # ���������, ��� ������ ����� �� ������ �����
            # � ��� �� ���' �� ������������ ����� ������
            if urlparse(link).netloc == DOMAIN and link not in links:
                links.add(link)
                links_to_handle_recursive.append(link)

    if maxdepth > 0:
        for link in links_to_handle_recursive:
            add_all_links_recursive(link, maxdepth=maxdepth - 1)

def main():
    print("\n ���������� �������� ������� ����� " + DOMAIN)
    urls = []
    total_time = 0
    add_all_links_recursive(HOST + '/')
    for link in links:
        start = time()
        # ���������� � �������� ������ �����
        result = chrome.get(link)
        end = time()
        urls.append(link)
        times.append(end - start)
        s = end - start;
        total_time += s

    print("\n")
    # ����������� ������ ����� - �������� 10 000 (����� �� �������� ����������)
    pd.options.display.max_rows = 10000
    df = pd.DataFrame({'�����': urls, '����� ��������, ���': times})
    writer = pd.ExcelWriter('C:/Users/Vadim/Desktop/Data parsing/������.xlsx')
    df.to_excel(writer, '����1')
    writer.save()
    print(" ������ � �������� �� �������� ��������� � ������� Excel � ����� �������.\n ����� ����� �������� ���������", total_time , "���")



if __name__ == '__main__':
    main()