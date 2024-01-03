from bs4 import BeautifulSoup
import pandas as pd
import requests
import rapidfuzz
import sqlite3
import os

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
# Create a pandas DataFrame for the ief ranking list.
iefdf = pd.DataFrame(data, columns=headers)

### Formatting begins here ###
# Remove the space in the ' Rank' column
iefdf=iefdf.rename(columns={' Rank':'Normalized Grade', 'Price (MSRP)':'Price'})

iefdf = iefdf.iloc[1:]
iefdf = iefdf.reset_index()
iefdf = iefdf.drop(iefdf.index[-1]) # drop last row, just blank formatting iirc

iefdf=iefdf.rename(columns={'Technical Grade':'Tech Grade'})
iefdf['Normalized Float'] = iefdf['Normalized Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})
iefdf['Tone Float']=iefdf['Tone Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})

iefdf['Tech Float']=iefdf['Tech Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})

### FLOAT AND GRADE STUFF
iefdf['Normalized Float and Grade'] = iefdf['Normalized Float'].astype(str) + ' (' + iefdf['Normalized Grade'].astype(str) + ')'
iefdf['Tone Float and Grade'] = iefdf['Tone Float'].astype(str) + ' (' + iefdf['Tone Grade'].astype(str) + ')'
iefdf['Tech Float and Grade'] = iefdf['Tech Float'].astype(str) + ' (' + iefdf['Tech Grade'].astype(str) + ')'

# Removal of redundant or unnecessary cols.
iefdf = iefdf.drop(columns=['index', 'Value Rating', 'Pricesort', 'Ranksort', 'Tonesort', 'Techsort'])

# Remove all rows containing 'KZ' or 'CCA' or 'Joyodio'
iefdf['Model']=iefdf['Model'].astype(str)
iefdf = iefdf[~iefdf['Model'].str.contains('KZ')]
iefdf = iefdf[~iefdf['Model'].str.contains('CCA')]
iefdf = iefdf[~iefdf['Model'].str.contains('Joyodio')]

# Add a col. "list" that will be used to identify the list the IEM is from.
# This will be used later to identify the IEMs that are in both lists.
# Use iefdf['list'] = 'ief' to add the list column to the iefdf DataFrame.
iefdf['List'] = 'ief'

# Make a request to the Antdroid's spreadsheet, parse with bs4 and create dataframe
r = requests.get("https://docs.google.com/spreadsheets/d/e/2PACX-1vTEdqzrEci3pGaAOu09zmYOhBtlrEPRjds3jXVgOuaN7vWQ7JWM1FNQEBeHqiPq7A/pubhtml")
r_text = r.text

soup = BeautifulSoup(r_text, 'html.parser')
tables = soup.find_all('table')
table = tables[0]
antdf = pd.read_html(str(table), header=0)[0]

### Formatting begins here ###
antdf = antdf.drop(columns=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 10', 'Unnamed: 11'])
# Make second row header, then drop first two rows
antdf.columns = antdf.iloc[1]
antdf=antdf.iloc[2:]

# Create col. called Normalized Grade Float taking value in the Normalized Grade col and turning it into a float.
# Where S+=9, S=8.7, S-=7.9, A+=7, A=6.5, A-=6, B+=5.5, B=5, B-=4.5, C+=4, C=3.5, C-=3, D+=2.5, D=2, D-=1.5, E+=1, E=0.5, E-=0.2, F+=0.1, F=0, F-=0.
# I didn't put too much thought into the values. I should look into it more.
antdf['Normalized Float'] = antdf['Normalized Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0, 'F-':0})

# Rename technical score to tech grade and Tonality Score to Tone Grade
antdf = antdf.rename(columns={'Technical Score':'Tech Grade', 'Tonality Score':'Tone Grade', 'Preference Score':'Preference Grade', 'IEM':'Model', 'Price (USD)':'iefdf'})

# Also assign a float value to the Tone Grade and Tech Grade
antdf['Tone Float'] = antdf['Tone Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0, 'F-':0})
antdf['Tech Float'] = antdf['Tech Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0, 'F-':0})
antdf['Preference Float'] = antdf['Preference Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0.2, 'F+':0.1, 'F':0, 'F-':0})

### FLOAT AND GRADE STUFF.
# Create a column that combines combines the Normalized Grade combines the normalized grade and the normalized grade float, putting the float in brackets.
antdf['Normalized Float and Grade'] = antdf['Normalized Float'].astype(str) + ' (' + antdf['Normalized Grade'].astype(str) + ')'
antdf['Tone Float and Grade'] = antdf['Tone Float'].astype(str) + ' (' + antdf['Tone Grade'].astype(str) + ')'
antdf['Tech Float and Grade'] = antdf['Tech Float'].astype(str) + ' (' + antdf['Tech Grade'].astype(str) + ')'
antdf['Preference Float and Grade'] = antdf['Preference Float'].astype(str) + ' (' + antdf['Preference Grade'].astype(str) + ')'

antdf = antdf[~antdf['Model'].str.contains('KZ')]
antdf = antdf[~antdf['Model'].str.contains('CCA')]
antdf = antdf[~antdf['Model'].str.contains('Joyodio')]

# Add list column for antdf
antdf['List'] = 'ant'

# Read Precog's spreadsheet
cogdf = pd.read_csv('https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/export?format=csv')

# Make the "Final Score" column float type
# First remove any rows with a non-float value in the Final Score column
# If they contain a letter:
cogdf = cogdf[~cogdf['Final Score'].str.contains('[a-zA-Z]', na=False)]
# If they are empty:
cogdf = cogdf[cogdf['Final Score'].notna()]

cogdf['Final Score'] = cogdf['Final Score'].astype(float)

cogdf['Tonality'] = cogdf['Tonality'].astype(float)
cogdf['Tech'] = cogdf['Tech'].astype(float)
cogdf['Bias '] = cogdf['Bias '].astype(float)

# Rename 'Final Score' to 'Normalized Float', Tonality to 'Tone Float', Tech to 'Tech Float', and 'Bias ' to 'Preference Float'
cogdf=cogdf.rename(columns={'IEM':'Model', 'Final Score':'Normalized Float', 'Tonality':'Tone Float', 'Tech':'Tech Float', 'Bias ':'Preference Float'})

# Adding 'Grade' col that takes the float and assigns it to a grade depending
# on whether it's greater or equal to a value for a grade.
cogdf['Normalized Grade'] = cogdf['Normalized Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
cogdf['Tone Grade'] = cogdf['Tone Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
cogdf['Tech Grade'] = cogdf['Tech Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
cogdf['Preference Grade'] = cogdf['Preference Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')
cogdf['Normalized Float and Grade'] = cogdf['Normalized Float'].astype(str) + ' (' + cogdf['Normalized Grade'].astype(str) + ')'
cogdf['Tone Float and Grade'] = cogdf['Tone Float'].astype(str) + ' (' + cogdf['Tone Grade'].astype(str) + ')'
cogdf['Tech Float and Grade'] = cogdf['Tech Float'].astype(str) + ' (' + cogdf['Tech Grade'].astype(str) + ')'
cogdf['Preference Float and Grade'] = cogdf['Preference Float'].astype(str) + ' (' + cogdf['Preference Grade'].astype(str) + ')'

# Remove " ⭑" at the end of any IEM names
cogdf['Model']=cogdf['Model'].astype(str)
cogdf['Model'] = cogdf['Model'].str.replace(' ⭑', '')

cogdf = cogdf[~cogdf['Model'].str.contains('KZ')]
cogdf = cogdf[~cogdf['Model'].str.contains('CCA')]
cogdf = cogdf[~cogdf['Model'].str.contains('Joyodio')]

# Add list column for cogdf
cogdf['List'] = 'cog'

# Read the Gizaudio spreadsheet
gizdf=pd.read_csv("https://docs.google.com/spreadsheets/d/1HFCuUzWdheP5qbxIJhyezJ53hvwM0wMrptVxKo49AFI/export?format=csv")

### Formatting begins here ###
gizdf.columns = gizdf.iloc[0]
gizdf = gizdf.iloc[1:]
gizdf = gizdf[gizdf['NAME'].notna()]
gizdf = gizdf.reset_index(drop=True)

# For now, I'll only look at the first 6 columns because formatting the rest isn't up my alley right now.
gizdf = gizdf.drop(gizdf.columns[6:], axis=1)
gizdf = gizdf.rename(columns={'NAME':'Model', 'RANKING':'Normalized Grade', 'PRICE (USD)':'Price', "Doesn't effect rank (max 10)":'Preference Float'})

gizdf['Normalized Float'] = gizdf['Normalized Grade'].replace({'S+':9.0, 'S':8.5, 'S-':8.0, 'A+':7.5, 'A':7.0, 'A-':6.5, 'B+':6.0, 'B':5.5, 'B-':5.0, 'C+':4.5, 'C':4.0, 'C-':3.5, 'D+':3.0, 'D':2.5, 'D-':2.0, 'E+':1.5, 'E':1.0, 'E-':0.5, 'F':0})

gizdf['Normalized Float and Grade'] = gizdf['Normalized Float'].astype(str) + ' (' + gizdf['Normalized Grade'].astype(str) + ')'
emoji_pattern = r'([\U00002600-\U000027BF]|\U0001f300-\U0001f64F|\U0001f680-\U0001f6FF|\U0001F700-\U0001F77F|\U0001F780-\U0001F7FF|\U0001F800-\U0001F8FF|\U0001F900-\U0001F9FF|\U0001FA00-\U0001FA6F|\U0001FA70-\U0001FAFF|\U00002B50)'

gizdf['Price'] = gizdf['Price'].str.replace(emoji_pattern, '', regex=True)
gizdf['Preference Float']=gizdf['Preference Float'].str.replace(emoji_pattern, '', regex=True)
gizdf['Preference Float'] = gizdf['Preference Float'].astype(float)
gizdf['Preference Grade'] = gizdf['Preference Float'].apply(lambda x: 'S+' if x>=9.0 else 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

# Combine pros and cons into comments col.
def combine_pros_and_cons(row):
    if pd.isna(row['PROS']) and pd.isna(row['CONS']):
        return 'No comments'
    # If there are only pros or cons, return what is available.
    elif pd.isna(row['PROS']):
        return row['CONS']
    elif pd.isna(row['CONS']):
        return row['PROS']
    # If there are both pros and cons return both.
    else:
        return 'PROS: ' + row['PROS'] + ' CONS: ' + row['CONS']
gizdf['Comments'] = gizdf.apply(combine_pros_and_cons, axis=1)

# remove the first row
gizdf=gizdf.iloc[1:]

gizdf=gizdf.reset_index(drop=True)
gizdf=gizdf.astype(str).apply(lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

# remove any rows where any column contains string "Re-Rank"
gizdf = gizdf[~gizdf['Normalized Grade'].str.contains('Re-Rank')]
gizdf = gizdf[~gizdf['Normalized Grade'].str.contains('Total IEMs Ranked')]

# remove any rows where the model name is "nan" or empty, or grade is ''.
gizdf = gizdf[gizdf['Model'] != 'nan']
gizdf = gizdf[gizdf['Model'] != '']
gizdf = gizdf[gizdf['Normalized Grade'] != '']

gizdf = gizdf[~gizdf['Model'].str.contains('KZ')]
gizdf = gizdf[~gizdf['Model'].str.contains('CCA')]
gizdf = gizdf[~gizdf['Model'].str.contains('Joyodio')]

# Add list column for gizdf
gizdf['List'] = 'giz'

# Congregate all the dataframes into one dataframe
frames = pd.concat([iefdf, antdf, cogdf, gizdf],axis=0)
# Convert 'Model' column to string
frames['Model'] = frames['Model'].astype(str)
# Remove any rows where the 'Model' column is empty
frames = frames[frames['Model'] != 'nan']
frames['Comments'] = frames['Comments'].astype(str)
# Turn "Normalized/Tone/Tech/Preference Float" columns into float type
frames['Normalized Float'] = frames['Normalized Float'].astype(float)
frames['Tone Float'] = frames['Tone Float'].astype(float)
frames['Tech Float'] = frames['Tech Float'].astype(float)
frames['Preference Float'] = frames['Preference Float'].astype(float)

name_variations={
    "Moondrop B2: Dusk":"Moondrop Blessing 2: Dusk",
    "Moondrop Dusk":"Moondrop Blessing 2: Dusk",
    "Moondrop Blessing 2 Dusk":"Moondrop Blessing 2: Dusk",
    "Elysian Annihilator":"Elysian Annihilator 2021",
    "Elysian Annihilator (2021)":"Elysian Annihilator 2021",
    "Campfire Andromeda":"Campfire Andromeda 2019",
    "Campfire Andromeda (2020)":"Campfire Andromeda 2020",
    "Campfire Dorado (2020)":"Campfire Dorado 2020",
    "Campfire Andromeda (S)": "Campfire Andromeda S",
    "QDC Anole VX":"qdc 8SL/Gemini/Anole VX",
    "qdc Anole VX":"qdc 8SL/Gemini/Anole VX",
    "Shuoer S12":"LETSHUOER S12",
    "Apple Airpods Pro 2nd Gen":"Apple Airpods Pro 2",
    "ThieAudio Legacy 2 (L2)":"ThieAudio Legacy 2",
    "ThieAudio Legacy 3 (L3)":"ThieAudio Legacy 3",
    "ThieAudio Legacy 4 (L4)":"ThieAudio Legacy 4",
    "ThieAudio Legacy 5 (L5)":"ThieAudio Legacy 5",
    "ThieAudio Legacy 9 (L9)":"ThieAudio Legacy 9",
    "Nothing Ear (1)": "Nothing Ear 1",
    "Nothing Ear (2)": "Nothing Ear 2",
    "Subtonic Storm ":"Subtonic Storm", # I'll get around to deleting extra spaces after the name later.
    "64 Audio U12T (m15)":"64 Audio U12T",
    "64 Audio U12t":"64 Audio U12T",
    "SeeAudio x Crinacle Yume: Midnight":"SeeAudio Yume Midnight",
    "SeeAudio x Crinacle Yume Midnight":"SeeAudio Yume Midnight",
    "Fiio x Crinacle FHE: Eclipse":"Fiio FHE Eclipse",
    "Fiio x Crinacle FHE Eclipse":"Fiio FHE Eclipse"
    }
frames['Model'] = frames['Model'].replace(name_variations)

# Viento jank
frames['Model'] = frames['Model'].apply(lambda x: "Hidition Viento-B" if x and ("Viento" in x) and ("B" in x) else x)

# Create a column containing the model names without the first word, as it is often the brand name.
frames['Model No Brand'] = frames['Model'].str.split(' ').str[1:].str.join(' ')
def fuzz_match(row):
    model = row['Model No Brand']
    match = rapidfuzz.process.extractOne(model, frames['Model No Brand'], score_cutoff=90)
    if match is not None:
        return match[0]
    else:
        return model
# Apply the fuzz_match function to the Model column
frames['Model No Brand'] = frames.apply(fuzz_match, axis=1)
# Change the everything after the first word in the Model column to the result of the fuzz_match function
frames['Model'] = frames['Model'].str.split(' ').str[0] + ' ' + frames['Model No Brand']

# reset index
frames=frames.reset_index(drop=True)

unique=frames['Model'].unique()
iefmask=frames['List']=='ief'
cogmask=frames['List']=='cog'
antmask=frames['List']=='ant'
gizmask=frames['List']=='giz'

unique_ief = set(frames[iefmask]['Model']) - set(frames[~iefmask]['Model'])
unique_cog = set(frames[cogmask]['Model']) - set(frames[~cogmask]['Model'])
unique_ant = set(frames[antmask]['Model']) - set(frames[~antmask]['Model'])
unique_giz = set(frames[gizmask]['Model']) - set(frames[~gizmask]['Model'])

# Add lists together to get all unique models
all_unique_models = unique_ief.union(unique_cog).union(unique_ant).union(unique_giz)

trimmedframes = frames[~frames['Model'].isin(all_unique_models)]



# Create dataframe 'combined', which has the average 'Normalized Float', 'Tone Float', 'Tech Float', 'Preference Float' for each 'Model', as well as the comments from each list.
combined = trimmedframes.groupby('Model')[['Normalized Float', 'Tone Float', 'Tech Float', 'Preference Float']].mean()
combined.reset_index(inplace=True)

# Remove all uneeded columns
combined = combined.filter(['Model', 'Normalized Float', 'Tone Float', 'Tech Float', 'Preference Float', 'Comments', 'List'])
combined['Normalized Float'] = combined['Normalized Float'].round(2)
combined['Tone Float'] = combined['Tone Float'].round(2)
combined['Tech Float'] = combined['Tech Float'].round(2)
combined['Preference Float'] = combined['Preference Float'].round(2)

maxidx = trimmedframes.groupby('Model')['Normalized Float'].idxmax()

# Use the indices to get the corresponding rows from the DataFrame
maxframe = trimmedframes.loc[maxidx]

minidx = trimmedframes.groupby('Model')['Normalized Float'].idxmin()
minframe = trimmedframes.loc[minidx]

# Map the 'Model' column in 'combined' to fetch corresponding 'Comment'
combined['Max Comments'] = combined['Model'].map(maxframe.set_index('Model')['Comments'])
combined['maxlist'] = combined['Model'].map(maxframe.set_index('Model')['List'])
combined['Min Comments'] = combined['Model'].map(minframe.set_index('Model')['Comments'])
combined['minlist'] = combined['Model'].map(minframe.set_index('Model')['List'])

# If 'Min Comments' is the same as 'Max Comments', then set them to N/A
combined.loc[combined['Min Comments']==combined['Max Comments'], 'Min Comments'] = "N/A"
combined.loc[combined['Max Comments']==combined['Min Comments'], 'Max Comments'] = "N/A"

# If '' or 'nan', then set 'Min Comments' to "N/A"
combined.loc[combined['Min Comments']=='nan', 'Min Comments'] = "N/A"
combined.loc[combined['Max Comments']=='nan', 'Max Comments'] = "N/A"
combined.loc[combined['Min Comments']=='', 'Min Comments'] = "N/A"
combined.loc[combined['Max Comments']=='', 'Max Comments'] = "N/A"


# If 'minlist' is the same as 'maxlist', then set minlist and maxlist to N/A
combined.loc[combined['minlist']==combined['maxlist'], 'minlist'] = "N/A"
combined.loc[combined['maxlist']==combined['minlist'], 'maxlist'] = "N/A"


# Make sure all columns are correct type.
combined['Model'] = combined['Model'].astype(str)
combined['Normalized Float'] = combined['Normalized Float'].astype(float)
combined['Tone Float'] = combined['Tone Float'].astype(float)
combined['Tech Float'] = combined['Tech Float'].astype(float)
combined['Preference Float'] = combined['Preference Float'].astype(float)
combined['Max Comments'] = combined['Max Comments'].astype(str)
combined['maxlist'] = combined['maxlist'].astype(str)
combined['Min Comments'] = combined['Min Comments'].astype(str)
combined['minlist'] = combined['minlist'].astype(str)

# Rename columns to use camelcase because I have no foresight and I'm too lazy to change this earlier.
combined = combined.rename(columns={'Model':'model', 'Normalized Float':'normalizedFloat',
    'Tone Float':'toneFloat', 'Tech Float':'techFloat', 'Preference Float':'preferenceFloat',
    'Max Comments':'maxComments', 'maxlist':'maxList', 'Min Comments':'minComments', 'minlist':'minList'})

# export the combined dataframe to a db file
db_folder = 'db'
if not os.path.exists(db_folder):
    os.makedirs(db_folder)
conn = sqlite3.connect(os.path.join(db_folder, 'combined.db'))
combined.to_sql('combined', conn, if_exists='replace', index=False)
conn.close()