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

START_URL = 'http://www.elektrarny.pro/seznam-elektraren.php?kj=nic&os=nic&vn-od=&vn-do=&nv=&ml=&le=&zobraz=Hledej&stranka='
BASE_URL = 'http://www.elektrarny.pro/'
# source: the page navigation at the bottom
MAX_PAGE = 261

# https://docs.python.org/2/tutorial/datastructures.html#dictionaries
# structure: name_of_power_station: capacity
scraped_power_plant_data = []
scraped_links = set()


def get_power_station_links(page_url):
    log.debug(page_url)
    r = requests.get(page_url)
    if r.status_code != 200:
        log.warning('Error requesting ' + page_url + '\tError code: ' + r.status_code)
        return None

    soup = BeautifulSoup(r.text, 'lxml')
    # search the html element table (there is only one on the page)
    data_table = soup.find('table')
    # the first row contains the table header
    data_rows = data_table.find_all('tr')[1:]
    for row in data_rows:
        link = row.select('td a')[0]['href']
        scraped_links.add(link)


def download_data_from_link(target_url):
    log.debug(target_url)
    r = requests.get(target_url)
    if r.status_code != 200:
        log.warning('Status code: ' + r.status_code + '\t' + target_url)
        return None

    basic_information_header = 'Základní informace o elektrárně'
    plant_owner_header = 'Majitel elektrárny'
    cadastral_information_header = 'Katastrální informace'

    scraped_info = {}

    soup = BeautifulSoup(r.text, 'lxml')
    data_boxes = soup.find_all('div', class_='boxik')
    for box in data_boxes:
        header_text = box.find('h2').text
        table_data = box.find_all('td')
        if header_text == basic_information_header:
            scraped_info['name'] = table_data[0].text
            scraped_info['capacity'] = table_data[1].text
            scraped_info['address'] = table_data[2].text
            scraped_info['start_up_date'] = table_data[3].text
            scraped_info['region'] = table_data[4].text
            scraped_info['district'] = table_data[5].text
        elif header_text == plant_owner_header:
            scraped_info['operator_name'] = table_data[0].text
            # not sure what exactly ICO is
            scraped_info['ICO'] = table_data[1].text
            scraped_info['operator_address'] = table_data[2].text
            scraped_info['operator license'] = table_data[3].text
            scraped_info['operator_region'] = table_data[4].text
            scraped_info['operator_district'] = table_data[5].text
        elif header_text == cadastral_information_header:
            table_data = box.find_all('td')
            scraped_info['cadastre_area'] = table_data[0].text
            scraped_info['cadastre_code'] = table_data[1].text
            scraped_info['cadastre_municipal'] = table_data[2].text
            scraped_info['cadastre_demarcation'] = table_data[3].text
        else:
            pass

    scraped_power_plant_data.append(scraped_info)


# get_power_station_links(BASE_URL)
# for entry in scraped_links:
#     print(entry)
# write_to_csv(
def start_script():
    # from 1 to MAX_PAGE+1
    for i in range(1, MAX_PAGE + 1):
        target_url = START_URL + str(i)
        get_power_station_links(target_url)

    log.info('number of scraped links: ' + str(len(scraped_links)))
    log.info('saving links to csv')

    with open('links.csv', 'w') as linkscsv:
        writer = csv.writer(linkscsv)
        # csv header
        # the writer expects a sequence and will split up the string.
        # wrapping it in a list stops that
        writer.writerow(['links'])
        for entry in list(scraped_links):
            writer.writerow([entry])



    # for links in scraped_links:
    #     download_data_from_link(BASE_URL + links)
    # log.debug(scraped_power_plant_data)


if __name__ == '__main__':
    start_script()
