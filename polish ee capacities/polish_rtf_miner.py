__author__ = 'Jan'
'''
    This script extracts data from the file polish.rtf. The file's origin is this website: http://www.ure.gov.pl/uremapoze/mapa.html .
'''

import re
import csv
import logging

log = logging.getLogger(__file__)
log.addHandler(logging.StreamHandler())

log.setLevel(logging.INFO)

FILE_NAME = 'polish_power_plants.csv'
file_content = ""

# read file to string
with open('polish.rtf', 'r') as rtf:
    file_content = rtf.read()

file_content = file_content.encode('utf-8').decode('iso-8859-2')

# needs more refactoring to propery extract the name (probably manually
reg_exp_power_plant_name = r'(?<=Powiat:).*(?=})'
# a new line is separating all parts
sep_split_into_parts = r'{\fs12 \f1 \line }'
# separates the table rows of each table
sep_data_parts = r'\trql'
# reg_exp_installation_type = r'(?<=\fs12 \f1 \pard \intbl \ql \cbpat(2|3|4) {\fs12 \f1  ).*(?=})'
reg_exp_installation_type = r'(?<=\\fs12 \\f1 \\pard \\intbl \\ql \\cbpat[2|3|4] \{\\fs12 \\f1  ).*(?=\})'
reg_exp_installation_value = r'(?<=\\fs12 \\f1 \\pard \\intbl \\qr \\cbpat3 \{\\fs12 \\f1 ).*(?=})'
# split file into parts. The
parts = file_content.split(sep_split_into_parts)

# list containing the data
data_set = []
for part in parts:
    # match power plant name
    power_plant_name = re.findall(reg_exp_power_plant_name, part)
    if len(power_plant_name) == 0:
        pass
    else:
        power_plant_name = power_plant_name[0]
        log.info('Processing: ' + power_plant_name)
        # separate each part
        data_parts = part.split(sep_data_parts)
        # data structure: data_row = {'name': '', 'install_type': '', 'quantity': '', 'power': ''}
        for data_rows in data_parts:
            wrapper_list = []
            # match each installation type
            installation_type = re.findall(reg_exp_installation_type, data_rows)
            for inst_type in installation_type:
                wrapper_list.append({'name': power_plant_name, 'install_type': inst_type})
            # match data - contains twice as many entries as installation type (quantity, power vs. install type)
            data_values = re.findall(reg_exp_installation_value, data_rows)
            if len(data_values) == 0:
                log.debug('data values empty')
                pass
            else:
                # connect data
                for i, _ in enumerate(wrapper_list):
                    wrapper_list[i]['quantity'] = data_values[(i * 2)]
                    wrapper_list[i]['power'] = data_values[(i * 2) + 1]

                # prepare to write to file
                for data in wrapper_list:
                    data_set.append(data)


# mapping of malformed unicode
polish_truncated_unicode_map = {
    r'\uc0\u322': 'ł',
    r'\uc0\u380': 'ż',
    r'\uc0\u243': 'ó',
    r'\uc0\u347': 'ś',
    r'\uc0\u324': 'ń',
    r'\uc0\u261': 'ą',
    r'\uc0\u281': 'ę',
    r'\uc0\u263': 'ć',
    r'\uc0\u321': 'Ł',
    r'\uc0\u378': 'ź',
    r'\uc0\u346': 'Ś',
    r'\uc0\u379': 'Ż'
}

# changing malformed (?) unicode
for entry in data_set:
    while r'\u' in entry['name']:
        index = entry['name'].index(r'\u')
        offset = index + 9
        log.debug(entry['name'][index:offset])
        to_be_replaced = entry['name'][index:offset]
        if to_be_replaced in polish_truncated_unicode_map.keys():
            log.debug('Found irregular: ' + entry['name'])
            # offset + 1 because there is a trailing whitespace
            entry['name'] = entry['name'].replace(entry['name'][index:offset + 1],
                                                  polish_truncated_unicode_map[to_be_replaced])
            log.debug('Replaced with: ' + entry['name'])
        else:
            break

with open(FILE_NAME, 'w', encoding='utf-8') as datacsv:
    log.info('Writing to data.csv')
    column_names = ['name', 'install_type', 'quantity', 'power']

    writer = csv.DictWriter(datacsv, lineterminator='\n', fieldnames=column_names, extrasaction='ignore')
    writer.writeheader()
    for entry in data_set:
        writer.writerow(entry)


# DEBUGGING AREA
# creates a list of all irregular names, only if in debug level
if log.getEffectiveLevel() == logging.DEBUG:
    # find irregular names
    ls = []
    for name in [x['name'] for x in data_set]:
        while r'\u' in name:
            index = name.index(r'\u')
            offset = index + 9
            log.debug(name[index:offset])
            to_be_replaced = name[index:offset]
            if to_be_replaced in polish_truncated_unicode_map.keys():
                log.debug('Found irregular: ' + name)
                # index:11 because there is a trailing whitespace
                name = name.replace(name[index:offset + 1], polish_truncated_unicode_map[to_be_replaced])
                log.debug('Replaced with: ' + name)
            else:
                ls.append(name)
                break

        # if r'\u' in name and name not in ls:

    log.debug('Writing irregular names to csv')
    with open('iregular_names.txt', 'w', encoding='utf-8') as irreg_file:
        for entry in ls:
            irreg_file.write(entry + ',\n')
