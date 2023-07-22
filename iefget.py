from bs4 import BeautifulSoup
import pandas as pd
import csv
import requests
import sqlite3

# Get the webpage
r = requests.get('https://crinacle.com/rankings/iems/')
soup = BeautifulSoup(r.text, 'html.parser')

# Find the table headers
header_row = soup.find('tr')
headers = [th.text for th in header_row.find_all('th')]

# Find all the table rows
rows = soup.find_all('tr')

data=[]

# Iterate through rows
for row in rows:
    # Find all table data (td) elements within each table row 'tr'
    tds = row.find_all('td')

    # Extract row data from each td
    row_data = [td.text for td in tds]

    data.append(row_data)

# Create a pandas DataFrame
crindf = pd.DataFrame(data, columns=headers)

# Display the DataFrame
print(crindf)

crindf = crindf.iloc[2:]
crindf = crindf.reset_index()
print(crindf)
# add a separate column named 'Rank Int' that uses the value in the "Rank" and turns it into an integer, where S=8.7, S-=7.9, A+=7, A=6.5, A-=6, B+=5.5, B=5, B-=4.5, C+=4, C=3.5, C-=3, D+=2.5, D=2, D-=1.5, E+=1, E=0.5, E-=0, F=0
crindf['Rank Int'] = crindf['Rank'].replace({'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})

# add a separate column named 'Rank and Int' that contains a string of both 'Rank' and 'Rank Int'

crindf['Rank and Int'] = crindf['Rank Int'].astype(str) + ' (' + crindf['Rank'].astype(str) + ')'

# remove the index column from crindf as it is redundant, and remove the 'Value Rating' column as it is not needed
# Also, remove Pricesort, Ranksort, Tonesort, Techsort, Based on columns.
crindf = crindf.drop(columns=['index', 'Value Rating', 'Pricesort', 'Ranksort', 'Tonesort', 'Techsort', 'Based on'])

# save crindf to a csv file for achival purposes
crindf.to_csv('crinacle.csv', index=False)
print(crindf.columns)
cogdf = pd.read_csv('https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/export?format=csv')
print(cogdf)

# Make a request to the website
r = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTEdqzrEci3pGaAOu09zmYOhBtlrEPRjds3jXVgOuaN7vWQ7JWM1FNQEBeHqiPq7A/pubhtml")
r_text = r.text

# Create a BeautifulSoup object and specify the parser
soup = BeautifulSoup(r_text, 'html.parser')

# Find all the tables in the HTML
tables = soup.find_all('table')

# Let's assume that the first table in the list is the one that you want
# you can change this based on your requirement.
table = tables[0]

# Drop the last, first, fourth columns of antdf.
antdf = antdf.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 7', 'Unnamed: 10', 'Unnamed: 11'])
antdf.columns = antdf.iloc[1] # set the column names to the second row
antdf=antdf.iloc[2:] # drop the first two rows


print(antdf)