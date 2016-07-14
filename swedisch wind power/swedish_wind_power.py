__author__ = 'Jan'


'''
The original file is located at: http://vindstat.com/files/M%C3%A5nadsrapport-201512.pdf .
With a tool called tabula (http://tabula.technology/) the table was transformed to a csv file.
This script transform the file to nice csv.
'''


import pandas as pd

df = pd.read_csv('tabula-one-header.csv')
print(df)