__author__ = 'Jan'
"""
This scraper is for the website http://mapa.czrea.org/instalace.php?TYP_INSTALACE=&OFFSET=0.
Unfortunately, some of the entries do not have values for the EE capacity
Check out the other czech scraper.


The way the urls are structured makes it hard to generate them. Therefore the scraper has to get them from the website.

"""
import logging
from bs4 import BeautifulSoup
import requests
import csv
import traceback

# TODO: Use queues to speed up download.
# TODO: Next step: Get date from the collected links.

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
collected_table_pages = set()
collected_links = set()


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
        collected_links.add(link)


def extract_data_from_power_station_table(power_station_table_url):
    # Some pages do not have a capacity field..........
    r = requests.get(BASE_URL + power_station_table_url)
    # check if the request was successful
    if r.status_code != 200:
        log.warning('There is a problem with the url. Maybe the resource is not available anymore!')
        # leaves the function, the rest is not executed
        return None

    content = r.text
    soup = BeautifulSoup(content, 'lxml')
    css_selector_power_station_capacity = 'table.detail'
    capacity_describtion = soup.select(css_selector_power_station_capacity)
    # power_station_name = soup.find
    print(capacity_describtion)


def start_script():
    # requesting the webpages with tables
    log.info('Requesting web pages with tables')
    for off in range(0, OFFSET_LIMIT, 50):
        request_pages_with_table(off)

    log.info(str(len(collected_table_pages)) + " pages found.")

    log.info('Extracting links from table pages')
    for table in collected_table_pages:
        extract_links(table)

    log.info(str(len(collected_links)) + ' links found!')

    log.info('writing links to csv')
    with open(TARGET_NAME + 'links.csv', 'w', encoding='utf-8') as linkcsv:
        writer = csv.writer(linkcsv, lineterminator='\n')
        # csv header
        # the writer expects a sequence and will split up the string.
        # wrapping it in a list stops that
        writer.writerow(['links'])
        for entry in list(collected_links):
            writer.writerow([BASE_URL + entry])

    log.info('Extracting data from the links')

    try:
        while len(collected_links) != 0:
            new_target = BASE_URL + collected_links.pop()
            extract_data_from_power_station_table(new_target)

    except Exception as e:
        log.warning(str(e))
        traceback.print_exc()

    log.info('writing data to csv')

    with open(TARGET_NAME + '_data.csv', 'w', encoding='utf-8') as datacsv:
        # csvwriter = csv.DictWriter
        pass


if __name__ == '__main__':
    start_script()
