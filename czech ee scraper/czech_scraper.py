__author__ = 'Jan'
"""
This scraper is for the website http://mapa.czrea.org/instalace.php?TYP_INSTALACE=&OFFSET=0.
The way the urls are structured makes it hard to generate them. Therefore the scraper has to get them from the website.

"""
import logging
from bs4 import BeautifulSoup
import requests
import csv
import traceback
import os

# setting up logger
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

TARGET_NAME = 'mapa.czrea.org'
TARGET_URL = 'http://mapa.czrea.org/instalace.php?TYP_INSTALACE=&OFFSET='
BASE_URL = 'http://mapa.czrea.org/'
# The limit is written on top of the table.
OFFSET_LIMIT = 1267

# https://docs.python.org/3.5/tutorial/datastructures.html?highlight=data%20structure#sets
collected_table_pages = []
collected_links = []
collected_data = []

KEYWORDS_INSTALLATION_TYPE = {'Vodní elektrárny': 'hydroelectric power plant',
                              'Větrné elektrárny': 'wind power plant',
                              'Fototermika - ohřev vody': 'fototermika - hot water',  # solar thermal?
                              'Spalování biomasy': 'burning biomass',
                              'Tepelná čerpadla': 'heat pumps',
                              'Bioplyn': 'biogas'}

KEYWORDS = {'description': 'Popis',

            'installation type': 'Typ instalace',
            'performance': 'Výkon',
            'year of installation': 'Rok instalace',
            'nominal performance': 'Nominální výkon',
            'maximal performance': 'Maximální výkon',

            'system description': 'Popis systému',

            'slope': 'Spád',
            'type of hydro power plant': 'Typ vodní elektrárny',
            'water course': 'Vodní tok',

            'annual production of bio gas': 'Roční produkce bioplynu',
            'source of bio gas': 'Zdroj bioplynu',

            'type of photovoltaic cells': 'Typ fotovoltaických článků',
            'color of photovoltaic cells': 'Barva fotovoltaických článků',

            'collection area': 'Plocha kolektorů',
            'fuel': 'Palivo',

            'Z. length': 'Z. délka',  # gps?
            'Z. width': 'Z. šířka',  # gps?
            'Name accounts. persons': 'Jméno kont. osoby',  # google tranlate
            'owner': 'Vlastník',
            'city': 'Město',
            'region': 'Kraj',
            'street': 'Ulice',
            'Zip': 'PSČ',
            'URL': 'URL',
            'mail': 'Aail',
            'phone': 'Telefon',

            'number of records': 'Celkový počet záznamů',
            'number of daily records': 'Počet dnešních záznamů',
            'oldest record': 'Nejstarší záznam',
            'latest record': 'Nejnovější záznam',
            }


def evaluate_keywords(key, tds):
    return tds[0].text[0:-1] == KEYWORDS[key]


def find_key_value(tds):
    key = ''
    data = None
    if evaluate_keywords('description', tds):
        data = tds[1].text
        key = 'description'
    elif evaluate_keywords('installation type', tds):
        data = tds[1].text
        key = 'installation type'
    elif evaluate_keywords('performance', tds):
        data = tds[1].text
        key = 'performance'
    elif evaluate_keywords('year of installation', tds):
        data = tds[1].text
        key = 'year of installation'
    elif evaluate_keywords('nominal performance', tds):
        data = tds[1].text
        key = 'nominal performance'
    elif evaluate_keywords('maximal performance', tds):
        data = tds[1].text
        key = 'maximal performance'
    elif evaluate_keywords('system description', tds):
        data = tds[1].text
        key = 'system description'
    elif evaluate_keywords('slope', tds):
        data = tds[1].text
        key = 'slope'
    elif evaluate_keywords('type of hydro power plant', tds):
        data = tds[1].text
        key = 'type of hydro power plant'
    elif evaluate_keywords('water course', tds):
        data = tds[1].text
        key = 'water course'
    elif evaluate_keywords('annual production of bio gas', tds):
        data = tds[1].text
        key = 'annual production of bio gas'
    elif evaluate_keywords('source of bio gas', tds):
        data = tds[1].text
        key = 'source of bio gas'
    elif evaluate_keywords('type of photovoltaic cells', tds):
        data = tds[1].text
        key = 'type of photovoltaic cells'
    elif evaluate_keywords('color of photovoltaic cells', tds):
        data = tds[1].text
        key = 'color of photovoltaic cells'
    elif evaluate_keywords('collection area', tds):
        data = tds[1].text
        key = 'collection area'
    elif evaluate_keywords('fuel', tds):
        data = tds[1].text
        key = 'fuel'
    elif evaluate_keywords('Z. length', tds):
        data = tds[1].text
        key = 'Z. length'
    elif evaluate_keywords('Z. width', tds):
        data = tds[1].text
        key = 'Z. width'
    elif evaluate_keywords('Name accounts. persons', tds):
        data = tds[1].text
        key = 'Name accounts. persons'
    elif evaluate_keywords('owner', tds):
        data = tds[1].text
        key = 'owner'
    elif evaluate_keywords('city', tds):
        data = tds[1].text
        key = 'city'
    elif evaluate_keywords('region', tds):
        data = tds[1].text
        key = 'region'
    elif evaluate_keywords('street', tds):
        data = tds[1].text
        key = 'street'
    elif evaluate_keywords('Zip', tds):
        data = tds[1].text
        key = 'Zip'
    elif evaluate_keywords('URL', tds):
        data = tds[1].text
        key = 'URL'
    elif evaluate_keywords('mail', tds):
        data = tds[1].text
        key = 'mail'
    elif evaluate_keywords('phone', tds):
        data = tds[1].text
        key = 'phone'
    elif evaluate_keywords('number of records', tds):
        data = tds[1].text
        key = 'number of records'
    elif evaluate_keywords('number of daily records', tds):
        data = tds[1].text
        key = 'number of daily records'
    elif evaluate_keywords('oldest record', tds):
        data = tds[1].text
        key = 'oldest record'
    elif evaluate_keywords('latest record', tds):
        data = tds[1].text
        key = 'latest record'
    else:
        pass
    return key, data


def request_pages_with_table(offset, table_page_url=TARGET_URL):
    new_target_url = table_page_url + str(offset)
    log.debug('Requesting webpage - URL: ' + new_target_url)
    r = requests.get(new_target_url)
    # check if the request was successful
    if r.status_code != 200:
        exit('There is a problem with the url. Maybe the resource is not available anymore!')
    content = r.text
    # pasing the webpage content (text) to BeautifulSoup for parsing
    soup = BeautifulSoup(content, 'lxml')
    # this selector selects a tbody (table body) within a table within a div with the class hlavnipanel-obsah
    css_selector_table = 'div.hlavnipanel-obsah table tbody'
    # find the table with links to the power stations
    collected_table_pages.add(soup.select(css_selector_table)[0])


def extract_links(power_stations_table):
    """
    Extracts all the links from the page by selecting the first td (table data) from each tr (table rows)
    and add them to the collected_links set.
    :param power_stations_table:
    :type power_stations_table:
    :return:
    :rtype:
    """

    table_rows = power_stations_table.find_all('tr')
    for tr in table_rows:
        td = tr.find('td')
        # href contains the link value
        link = td.find('a')['href']
        log.debug('link_found')
        collected_links.add(BASE_URL + link)


def extract_data_from_power_station_table(power_station_table_url):
    # Some pages do not have a capacity field..........
    r = requests.get(power_station_table_url)
    # check if the request was successful
    if r.status_code != 200:
        log.warning('There is a problem with the url. Maybe the resource is not available anymore!')
        # leaves the function, the rest is not executed
        return None

    # stores the collected data from one page
    data = {}

    content = r.text
    soup = BeautifulSoup(content, 'lxml')
    try:
        # selecting the table
        css_selector_power_station_capacity = 'table.detail'
        data_table = soup.select(css_selector_power_station_capacity)[0]

        # select all table rows but the first one
        table_rows = data_table.find_all('tr')[1:]

        for row in table_rows:
            tds = row.select('td')
            # remove the : from the word.
            key, value = find_key_value(tds)
            if value is None:
                pass
            else:
                data[key] = value
        return data
    except:
        traceback.print_exc()
        return None


def read_links_from_file():
    with open(TARGET_NAME + '_links.csv', 'r') as linksCSV:
        reader = csv.reader(linksCSV)
        links_as_lists = list(reader)[1:]
        # reads the first element of the each list (the link) and adds it to the list.
        return [x[0] for x in links_as_lists]


def start_script():
    global collected_links
    log.info('Checking if links are already written to the csv.')
    if not os.path.exists(TARGET_NAME + '_links.csv'):
        log.info('CSV not found -> Requesting web pages with tables')
        for off in range(0, OFFSET_LIMIT, 50):
            request_pages_with_table(off)

        log.info(str(len(collected_table_pages)) + " pages found.")

        log.info('Extracting links from table pages')
        for table in collected_table_pages:
            extract_links(table)

        log.info(str(len(collected_links)) + ' links found!')

        log.info('Writing links to csv')
        with open(TARGET_NAME + '_links.csv', 'w', encoding='utf-8') as linkcsv:
            writer = csv.writer(linkcsv, lineterminator='\n')
            # csv header
            # the writer expects a sequence and will split up the string.
            # wrapping it in a list stops that
            writer.writerow(['links'])
            for entry in list(collected_links):
                writer.writerow([entry])
    else:
        log.info('File found -> Reading from file ')
        links = read_links_from_file()
        collected_links = set(links)

    log.info('Extracting data from the links')
    try:
        while len(collected_links) != 0:
            new_target = collected_links.pop()
            log.info('Scraping ' + new_target)
            data = extract_data_from_power_station_table(new_target)
            if data is not None:
                collected_data.append(data)

    except Exception as e:
        log.warning(str(e))
        traceback.print_exc()

    log.info('writing data to csv')

    with open(TARGET_NAME + '_data.csv', 'w', encoding='utf-8') as datacsv:
        column_names = ['description', 'installation type', 'performance', 'year of installation',
                        'nominal performance', 'ICO', 'maximal performance', 'system description',
                        'slope', 'type of hydro power plant', 'water course',
                        'annual production of bio gas', 'source of bio gas',
                        'type of photovoltaic cells', 'color of photovoltaic cells',
                        'collection area', 'fuel',
                        'Z. length', 'Z. width', 'Name accounts. persons', 'owner', 'city', 'region',
                        'street', 'Zip', 'URL', 'mail', 'phone',
                        'number of records', 'number of daily records', 'oldest record', 'latest record'
                        ]

        writer = csv.DictWriter(datacsv, lineterminator='\n', fieldnames=column_names)
        writer.writeheader()
        for entry in collected_data:
            writer.writerow(entry)


if __name__ == '__main__':
    collected_data = []
    collected_links = set()
    collected_table_pages = set()
    print(KEYWORDS.keys())
    start_script()
