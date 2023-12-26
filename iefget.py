from bs4 import BeautifulSoup
import pandas as pd
import csv
import requests
import sqlite3

# Get crinacle's ranking table
r = requests.get('https://crinacle.com/rankings/iems/')
soup = BeautifulSoup(r.text, 'html.parser')
# Find the table headers
header_row = soup.find('tr')
headers = [th.text for th in header_row.find_all('th')]
rows = soup.find_all('tr') # Find all the table rows
data=[]
for row in rows: # Iterate through rows
    tds = row.find_all('td') # Find all table data (td) elements within each table row 'tr'
    row_data = [td.text for td in tds] # Extract row data from each td
    data.append(row_data)
# Create a pandas DataFrame for crinacle's ranking list.
crindf = pd.DataFrame(data, columns=headers)
crindf=crindf.rename(columns={' Rank':'Normalized Grade'})
crindf = crindf.iloc[1:]
crindf = crindf.reset_index()
crindf = crindf.drop(crindf.index[-1])
crindf=crindf.rename(columns={'Technical Grade':'Tech Grade'})
crindf['Normalized Float'] = crindf['Normalized Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})
crindf['Tone Float']=crindf['Tone Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})
crindf['Tech Float']=crindf['Tech Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})
crindf['Normalized Float and Grade'] = crindf['Normalized Float'].astype(str) + ' (' + crindf['Normalized Grade'].astype(str) + ')'
crindf['Tone Float and Grade'] = crindf['Tone Float'].astype(str) + ' (' + crindf['Tone Grade'].astype(str) + ')'
crindf['Tech Float and Grade'] = crindf['Tech Float'].astype(str) + ' (' + crindf['Tech Grade'].astype(str) + ')'
# remove the index column from crindf as it is redundant, and remove the 'Value Rating' as we will be calculating it ourselves later.
# Also, remove Pricesort, Ranksort, Tonesort, Techsort, 'Based on', columns.
crindf = crindf.drop(columns=['index', 'Value Rating', 'Pricesort', 'Ranksort', 'Tonesort', 'Techsort'])

# Make a request to the antdf sheet
r = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTEdqzrEci3pGaAOu09zmYOhBtlrEPRjds3jXVgOuaN7vWQ7JWM1FNQEBeHqiPq7A/pubhtml")
r_text = r.text
# Create a BeautifulSoup object and specify html parser
soup = BeautifulSoup(r_text, 'html.parser')
tables = soup.find_all('table')
table = tables[0]
antdf = pd.read_html(str(table), header=0)[0]
antdf = antdf.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 10', 'Unnamed: 11'])
# Make the second row the header
antdf.columns = antdf.iloc[1]
antdf=antdf.iloc[2:] # drop the first two rows
# Create new column called Normalized Grade Float that takes the value in the Normalized Grade column and turns it into a float, where S+=9, S=8.7, S-=7.9, A+=7, A=6.5, A-=6, B+=5.5, B=5, B-=4.5, C+=4, C=3.5, C-=3, D+=2.5, D=2, D-=1.5, E+=1, E=0.5, E-=0.2, F+=0.1, F=0
antdf['Normalized Float'] = antdf['Normalized Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0})
# Rename technical score to tech grade and Tonality Score to Tone Grade
antdf = antdf.rename(columns={'Technical Score':'Tech Grade', 'Tonality Score':'Tone Grade', 'Preference Score':'Preference Grade', 'IEM':'Model'})
antdf['Tone Float'] = antdf['Tone Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0})
antdf['Tech Float'] = antdf['Tech Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0})
antdf['Preference Float'] = antdf['Preference Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0})
# Create a column that combines combines the Normalized Grade combines the normalized grade and the normalized grade float, putting the float in brackets.
antdf['Normalized Float and Grade'] = antdf['Normalized Float'].astype(str) + ' (' + antdf['Normalized Grade'].astype(str) + ')'
antdf['Tone Float and Grade'] = antdf['Tone Float'].astype(str) + ' (' + antdf['Tone Grade'].astype(str) + ')'
antdf['Tech Float and Grade'] = antdf['Tech Float'].astype(str) + ' (' + antdf['Tech Grade'].astype(str) + ')'
antdf['Preference Float and Grade'] = antdf['Preference Float'].astype(str) + ' (' + antdf['Preference Grade'].astype(str) + ')'

# Read precog's ranking spreadsheet.
cogdf = pd.read_csv('https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/export?format=csv')
# drop cols 1, 2, 3, 17, 18, 19, 20, 21, 23, 24
cogdf = cogdf.drop(columns=['Unnamed: 0', 'Rank', 'Unnamed: 3', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 'Based On'])
cogdf = cogdf.iloc[:cogdf[cogdf['IEM'].isnull()].index[0]] # Include no rows after the first row with an empty IEM column.
cogdf['Final Score'] = cogdf['Final Score'].astype(float)
cogdf['Tonality'] = cogdf['Tonality'].astype(float)
cogdf['Tech'] = cogdf['Tech'].astype(float)
cogdf['Bias '] = cogdf['Bias '].astype(float)
# Rename 'Final Score' to 'Normalized Float', Tonality to 'Tone Float', Tech to 'Tech Float', and 'Bias ' to 'Preference Float'
cogdf=cogdf.rename(columns={'Final Score':'Normalized Float', 'Tonality':'Tone Float', 'Tech':'Tech Float', 'Bias ':'Preference Float'})
# Add a column named Grade that takes the float in Final Score and assigns it to a grade depending on whether it's greater or equal to 8.7 for S, 7.9 for S-, 7 for A+, 6.5 for A, 6 for A-, 5.5 for B+, 5 for B, 4.5 for B-, 4 for C+, 3.5 for C, 3 for C-, 2.5 for D+, 2 for D, 1.5 for D-, 1 for E+, 0.5 for E, 0.2 for E-, 0.1 for F+, 0 for F
cogdf['Normalized Grade'] = cogdf['Normalized Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
# Do the same for the Tonality column, creating a column named Tone Grade
cogdf['Tone Grade'] = cogdf['Tone Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
# Do the same for the Tech column, creating a column named Tech Grade
cogdf['Tech Grade'] = cogdf['Tech Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
# rename the 'Bias ' column to 'Preference Float'
cogdf['Preference Grade'] = cogdf['Preference Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
# Create column combining the Final Score and Grade, putting the grade in brackets.
cogdf['Normalized Float and Grade'] = cogdf['Normalized Float'].astype(str) + ' (' + cogdf['Normalized Grade'].astype(str) + ')'
# Do the same for the Tonality column
cogdf['Tone Float and Grade'] = cogdf['Tone Float'].astype(str) + ' (' + cogdf['Tone Grade'].astype(str) + ')'
# Do the same for the Tech column
cogdf['Tech Float and Grade'] = cogdf['Tech Float'].astype(str) + ' (' + cogdf['Tech Grade'].astype(str) + ')'
# Do the same for the Bias column
cogdf['Bias Float and Grade'] = cogdf['Preference Float'].astype(str) + ' (' + cogdf['Preference Grade'].astype(str) + ')