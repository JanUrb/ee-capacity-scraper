__author__ = 'Jan'
"""
Since the other source is incomplete, this scraper uses http://www.elektrarny.pro/seznam-elektraren.php?kj=nic&os=nic&vn-od=&vn-do=&nv=&ml=&le=&zobraz=Hledej as source.
"""

from bs4 import BeautifulSoup
import requests
import logging
import csv
import time
import random
import traceback

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

START_URL = 'http://www.elektrarny.pro/seznam-elektraren.php?kj=nic&os=nic&vn-od=&vn-do=&nv=&ml=&le=&zobraz=Hledej&stranka='
BASE_URL = 'http://www.elektrarny.pro/'
# source: the page navigation at the bottom
MAX_PAGE = 261
MAX_NUMBER_ENTRIES = 26088

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


def create_power_station_links():
    url = 'detail.php?id='
    for i in range(1, MAX_NUMBER_ENTRIES + 1):
        scraped_links.add(url + str(i))


def download_data_from_link(target_url):
    log.debug(target_url)
    r = requests.get(target_url)
    if r.status_code != 200:
        log.warning('Status code: ' + str(r.status_code) + '\t' + target_url)
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


def start_script():
    # it seems that this page is blocked/changed
    # with create_power_station_links() werden die links automatisch erstellt.
    # from 1 to MAX_PAGE+1
    # for i in range(1, MAX_PAGE + 1):
    #     target_url = START_URL + str(i)
    #     get_power_station_links(target_url)

    create_power_station_links()

    log.info('number of scraped links: ' + str(len(scraped_links)))
    log.info('saving links to csv')

    with open('links.csv', 'w', encoding='utf-8') as linkcsv:
        writer = csv.writer(linkcsv, lineterminator='\n')
        # csv header
        # the writer expects a sequence and will split up the string.
        # wrapping it in a list stops that
        writer.writerow(['links'])
        for entry in list(scraped_links):
            writer.writerow([BASE_URL + entry])

    download_counter = 0
    delay_flag = 0
    DELAY_MAX = 20
    new_target = None
    reset_counter = 0
    MAX_RESET_COUNTER = 5
    while len(scraped_links) != 0:
        delay_flag += 1

        try:
            # Everytime a link is successfully downloaded, new_target is set to None.
            # This ensures that every entry is downloaded, even if there was an error in a previous try.
            if new_target is None:
                new_target = BASE_URL + scraped_links.pop()

            # Downloading the data, handling connectionError
            try:
                download_data_from_link(new_target)
                new_target = None
                download_counter += 1
                reset_counter = 0
            except requests.exceptions.ConnectionError:
                reset_counter += 1
                if reset_counter == 5:
                    raise Exception('The number of MAX consecutive resets is reached!')

                log.warning('Connection Error - retrying after 1 seconds')
                log.warning('Download Counter: ' + str(download_counter))
                time.sleep(1)


        # Unknown and unhandled Exception. Save current data and exit the script
        except Exception as e:
            log.warn(str(e))
            traceback.print_exc()
            break

        if delay_flag == DELAY_MAX:
            delay_flag = 0

            sleep_timer = random.uniform(0, 2)
            # wait for a while to avoid getting banned by the server
            log.info('sleeping for: ' + str(sleep_timer))
            log.info('Download Counter: ' + str(download_counter))
            time.sleep(sleep_timer)

    with open('data.csv', 'w', encoding='utf-8') as datacsv:
        log.info('Writing to data.csv')
        column_names = ['name', 'capacity', 'address', 'start_up_date', 'region', 'district',
                        'operator_name', 'ICO', 'operator_address', 'operator license', 'operator_region',
                        'operator_district',
                        'cadastre_area', 'cadastre_code', 'cadastre_municipal', 'cadastre_demarcation']

        writer = csv.DictWriter(datacsv, lineterminator='\n', fieldnames=column_names)
        writer.writeheader()
        for entry in scraped_power_plant_data:
            writer.writerow(entry)

            # for links in scraped_links:
            #     download_data_from_link(BASE_URL + links)
            #


if __name__ == '__main__':
    start_script()
