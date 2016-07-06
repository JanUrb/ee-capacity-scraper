__author__ = 'Jan'
"""
Since the other source is incomplete, this scraper uses http://www.elektrarny.pro/seznam-elektraren.php?kj=nic&os=nic&vn-od=&vn-do=&nv=&ml=&le=&zobraz=Hledej as source.
"""


from bs4 import BeautifulSoup
import requests
import logging
import csv


log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

BASE_URL = 'http://www.elektrarny.pro/seznam-elektraren.php?kj=nic&os=nic&vn-od=&vn-do=&nv=&ml=&le=&zobraz=Hledej&stranka='
# source: the page navigation at the bottom
MAX_PAGE = 261

# https://docs.python.org/2/tutorial/datastructures.html#dictionaries
# structure: name_of_power_station: capacity
scraped_data = {}


def get_power_station_links(page_url):
    r = requests.get(page_url)
    if r.status_code != 200:
        log.warning('Error requesting '+ page_url + '\tError code: '+r.status_code)
        return None

    soup = BeautifulSoup(r.text, 'lxml')
    # search the html element table (there is only one on the page)
    data_table = soup.find('table')
    # the first row contains the table header
    data_rows = data_table.find_all('tr')[1:]

    # TODO: Some names are double which causes them to overwrite previous entries.
    # new idea: simple list with this structure [{'name': name, 'capcaity':
    # extracting the data
    for row in data_rows:
        name_of_power_station = row.select('td a')[0].text
        capacity_of_power_station = row.select('td:nth-of-type(2)')[0].text
        log.debug('name: '+name_of_power_station+'\t capacity: '+capacity_of_power_station)
        scraped_data[name_of_power_station] = capacity_of_power_station

get_power_station_links(BASE_URL)
for entry in scraped_data:
    print(entry)
# write_to_csv()