__author__ = 'Jan'

import logging
from bs4 import BeautifulSoup
import requests

# TODO: Use queues to speed up download.
# TODO: Next step: Get date from the collected links.

# setting up logger
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

TARGET_URL = 'http://mapa.czrea.org/instalace.php?TYP_INSTALACE=&OFFSET='
BASE_URL = 'http://mapa.czrea.org/'
# The limit is written on top of the table.
OFFSET_LIMIT = 1267

# https://docs.python.org/3.5/tutorial/datastructures.html?highlight=data%20structure#sets
collected_table_pages = set()
collected_links = set()

def request_pages_with_table(offset, table_page_url=TARGET_URL):
    # TODO: unglobal this
    global power_station_table
    new_target_url = table_page_url + str(offset)
    log.info('Requesting webpage - URL: '+new_target_url)
    r = requests.get(new_target_url)
    # check if the request was successful
    if r.status_code != 200:
        exit('There is a problem with the url. Maybe the resource is not available anymore!')
    content = r.text
    log.info('Starting extraction of the links')
    # pasing the webpage content (text) to BeautifulSoup for parsing
    soup = BeautifulSoup(content, 'lxml')
    # this selector selects a tbody (table body) within a table within a div with the class hlavnipanel-obsah
    css_selector_table = 'div.hlavnipanel-obsah table tbody'
    # find the table with links to the power stations
    collected_table_pages.add(soup.select(css_selector_table)[0])


# requesting the webpages with tables
log.info('Requesting web pages with tables')
for off in range(0, OFFSET_LIMIT, 50):
    request_pages_with_table(off)

log.info(str(len(collected_table_pages))+ " pages found.")

def extract_links(power_stations_table):
    """
    Extracts all the links from the page by selecting the first td (table data) from each tr (table rows)
    and add them to the collected_links set.
    :param power_stations_table:
    :type power_stations_table:
    :return:
    :rtype:
    """
    log.debug('extract_links')
    table_rows = power_stations_table.find_all('tr')
    for tr in table_rows:
        td = tr.find('td')
        # href contains the link value
        link = td.find('a')['href']
        log.debug('link_found')
        collected_links.add(link)

log.info('Extracting links from table pages')
for table in collected_table_pages:
    extract_links(table)

log.info(str(len(collected_links))+ ' links found!')


