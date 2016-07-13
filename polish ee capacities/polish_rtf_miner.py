__author__ = 'Jan'
import re
import csv
import logging


# TODO: Encode the names properly!

log = logging.getLogger(__file__)
log.addHandler(logging.StreamHandler())

log.setLevel(logging.INFO)


FILE_NAME = 'polish_power_plants.csv'
file_content = ""

# read file to string
with open('polish.rtf') as rtf:
    file_content = rtf.read()

file_content = file_content.encode('iso-8859-1').decode('utf-8')

# match everything that is comes after ...
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
print(parts[-2])
for part in parts:
    # match power plant name
    power_plant_name = re.findall(reg_exp_power_plant_name, part)
    if len(power_plant_name) == 0:
        pass
    else:
        power_plant_name = power_plant_name[0]
        log.info('Processing: ' + power_plant_name)

        # separate each row
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


log.info('Data set length: ' + str(len(data_set)))

with open(FILE_NAME, 'w', encoding='utf-8') as datacsv:
    log.info('Writing to data.csv')
    column_names = ['name', 'install_type', 'quantity', 'power']

    writer = csv.DictWriter(datacsv, lineterminator='\n', fieldnames=column_names, extrasaction='ignore')
    writer.writeheader()
    for entry in data_set:
        writer.writerow(entry)

