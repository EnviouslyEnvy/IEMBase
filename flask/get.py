from bs4 import BeautifulSoup
import pandas as pd
import requests
import rapidfuzz
import sqlite3
import os
from io import StringIO

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
antdf = pd.read_html(StringIO(str(table)), header=0)[0]

# Debug: Print initial shape
print(f"Initial Antdroid data shape: {antdf.shape}")

### Formatting begins here ###
# More defensive column dropping - only drop unnamed columns that actually exist
columns_to_drop = [col for col in antdf.columns if col in ['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 4', 'Unnamed: 11']]
if columns_to_drop:
    antdf = antdf.drop(columns=columns_to_drop)

# Make second row header, then drop first two rows
antdf.columns = antdf.iloc[1]
antdf = antdf.iloc[2:]

# Fix the critical error: Price column was being renamed to 'iefdf' instead of 'Price'
antdf = antdf.rename(columns={
    'Technical Score': 'Tech Grade', 
    'Tonality Score': 'Tone Grade', 
    'Preference Score': 'Preference Grade', 
    'IEM': 'Model', 
    'Price (USD)': 'Price'  # Fixed: was incorrectly renamed to 'iefdf'
})

# Now ensure Model column is string type
antdf['Model'] = antdf['Model'].fillna('').astype(str)
antdf = antdf[~antdf['Model'].str.contains('KZ', na=False)]

# Debug: Print shape after initial filtering
print(f"Antdroid data shape after filtering: {antdf.shape}")

# Create col. called Normalized Grade Float taking value in the Normalized Grade col and turning it into a float.
# Make S+ 10.0, S 9.5, S-, 9... all the way down to F- being 0. That's how their rating system works.
# Handle Score column more defensively - ensure it exists and can be converted
if 'Score' in antdf.columns:
    antdf['Normalized Float'] = pd.to_numeric(antdf['Score'], errors='coerce') / 2
else:
    # Fallback to grade-based conversion if Score column doesn't exist
    print("Warning: Score column not found in Antdroid data, using grade conversion")
    antdf['Normalized Float'] = antdf['Normalized Grade'].replace({
        'S+': 10.0, 'S': 9.5, 'S-': 9.0, 'A+': 8.5, 'A': 8.0, 'A-': 7.5, 
        'B+': 7.0, 'B': 6.5, 'B-': 6.0, 'C+': 5.5, 'C': 5.0, 'C-': 4.5, 
        'D+': 4.0, 'D': 3.5, 'D-': 3.0, 'E+': 2.5, 'E': 2.0, 'E-': 1.5, 
        'F+': 1.0, 'F': 0.5, 'F-': 0
    })

# Also assign a float value to the Tone Grade and Tech Grade
antdf['Tone Float'] = antdf['Tone Grade'].replace({'S+':10.0, 'S':9.5, 'S-':9.0, 'A+':8.5, 'A':8.0, 'A-':7.5, 'B+':7.0, 'B':6.5, 'B-':6.0, 'C+':5.5, 'C':5.0, 'C-':4.5, 'D+':4.0, 'D':3.5, 'D-':3.0, 'E+':2.5, 'E':2.0, 'E-':1.5, 'F+':1.0, 'F':0.5, 'F-':0})
antdf['Tech Float'] = antdf['Tech Grade'].replace({'S+':10.0, 'S':9.5, 'S-':9.0, 'A+':8.5, 'A':8.0, 'A-':7.5, 'B+':7.0, 'B':6.5, 'B-':6.0, 'C+':5.5, 'C':5.0, 'C-':4.5, 'D+':4.0, 'D':3.5, 'D-':3.0, 'E+':2.5, 'E':2.0, 'E-':1.5, 'F+':1.0, 'F':0.5, 'F-':0})
antdf['Preference Float'] = antdf['Preference Grade'].replace({'S+':10.0, 'S':9.5, 'S-':9.0, 'A+':8.5, 'A':8.0, 'A-':7.5, 'B+':7.0, 'B':6.5, 'B-':6.0, 'C+':5.5, 'C':5.0, 'C-':4.5, 'D+':4.0, 'D':3.5, 'D-':3.0, 'E+':2.5, 'E':2.0, 'E-':1.5, 'F+':1.0, 'F':0.5, 'F-':0})

### FLOAT AND GRADE STUFF.
# Create a column that combines combines the Normalized Grade combines the normalized grade and the normalized grade float, putting the float in brackets.
antdf['Normalized Float and Grade'] = antdf['Normalized Float'].astype(str) + ' (' + antdf['Normalized Grade'].astype(str) + ')'
antdf['Tone Float and Grade'] = antdf['Tone Float'].astype(str) + ' (' + antdf['Tone Grade'].astype(str) + ')'
antdf['Tech Float and Grade'] = antdf['Tech Float'].astype(str) + ' (' + antdf['Tech Grade'].astype(str) + ')'
antdf['Preference Float and Grade'] = antdf['Preference Float'].astype(str) + ' (' + antdf['Preference Grade'].astype(str) + ')'

# Convert to string and handle NaN values
antdf['Model'] = antdf['Model'].fillna('').astype(str)
# Use na=False in str.contains
antdf = antdf[~antdf['Model'].str.contains('KZ', na=False)]
antdf = antdf[~antdf['Model'].str.contains('CCA', na=False)]
antdf = antdf[~antdf['Model'].str.contains('Joyodio', na=False)]

# Add list column for antdf
antdf['List'] = 'ant'

# Read Precog's spreadsheet
cogdf = pd.read_csv('https://docs.google.com/spreadsheets/d/1pUCELfWO-G33u82H42J8G_WX1odnOYBJsBNbVskQVt8/export?format=csv')

# Debug: Print initial shape and column info
print(f"Initial Precog data shape: {cogdf.shape}")
print(f"Precog columns: {list(cogdf.columns)}")

# The CSV has some empty rows and metadata - filter to actual data rows
# Remove rows where IEM column is empty or contains non-IEM data
cogdf = cogdf[cogdf['IEM'].notna()]
cogdf = cogdf[cogdf['IEM'] != '']

# Debug: Print shape after filtering empty IEM rows
print(f"After filtering empty IEM rows: {cogdf.shape}")

# Check if expected columns exist before processing
required_cols = ['IEM', 'Final Score', 'Tonality', 'Tech', 'Bias ']
missing_cols = [col for col in required_cols if col not in cogdf.columns]
if missing_cols:
    print(f"Warning: Missing expected columns in Precog data: {missing_cols}")
    print(f"Available columns: {list(cogdf.columns)}")

# Make the "Final Score" column float type
# First remove any rows with a non-float value in the Final Score column
if 'Final Score' in cogdf.columns:
    # If they contain a letter:
    cogdf = cogdf[~cogdf['Final Score'].astype(str).str.contains('[a-zA-Z]', na=False)]
    # If they are empty:
    cogdf = cogdf[cogdf['Final Score'].notna()]
    
    cogdf['Final Score'] = pd.to_numeric(cogdf['Final Score'], errors='coerce')
    
    # Remove rows where Final Score conversion failed
    cogdf = cogdf[cogdf['Final Score'].notna()]
else:
    print("Warning: 'Final Score' column not found in Precog data")

# Convert other score columns to float with error handling
for col in ['Tonality', 'Tech', 'Bias ']:
    if col in cogdf.columns:
        cogdf[col] = pd.to_numeric(cogdf[col], errors='coerce')
    else:
        print(f"Warning: '{col}' column not found in Precog data")

# Debug: Print shape after numeric conversions
print(f"After numeric conversions: {cogdf.shape}")

# Rename 'Final Score' to 'Normalized Float', Tonality to 'Tone Float', Tech to 'Tech Float', and 'Bias ' to 'Preference Float'
# Only rename columns that actually exist
rename_mapping = {}
if 'IEM' in cogdf.columns:
    rename_mapping['IEM'] = 'Model'
if 'Final Score' in cogdf.columns:
    rename_mapping['Final Score'] = 'Normalized Float'
if 'Tonality' in cogdf.columns:
    rename_mapping['Tonality'] = 'Tone Float'
if 'Tech' in cogdf.columns:
    rename_mapping['Tech'] = 'Tech Float'
if 'Bias ' in cogdf.columns:
    rename_mapping['Bias '] = 'Preference Float'

cogdf = cogdf.rename(columns=rename_mapping)

# Adding 'Grade' col that takes the float and assigns it to a grade depending
# on whether it's greater or equal to a value for a grade.
# Only create grades for columns that exist
if 'Normalized Float' in cogdf.columns:
    cogdf['Normalized Grade'] = cogdf['Normalized Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

if 'Tone Float' in cogdf.columns:
    cogdf['Tone Grade'] = cogdf['Tone Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

if 'Tech Float' in cogdf.columns:
    cogdf['Tech Grade'] = cogdf['Tech Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

if 'Preference Float' in cogdf.columns:
    cogdf['Preference Grade'] = cogdf['Preference Float'].apply(lambda x: 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

# Create combined float and grade columns only for columns that exist
if 'Normalized Float' in cogdf.columns and 'Normalized Grade' in cogdf.columns:
    cogdf['Normalized Float and Grade'] = cogdf['Normalized Float'].astype(str) + ' (' + cogdf['Normalized Grade'].astype(str) + ')'

if 'Tone Float' in cogdf.columns and 'Tone Grade' in cogdf.columns:
    cogdf['Tone Float and Grade'] = cogdf['Tone Float'].astype(str) + ' (' + cogdf['Tone Grade'].astype(str) + ')'

if 'Tech Float' in cogdf.columns and 'Tech Grade' in cogdf.columns:
    cogdf['Tech Float and Grade'] = cogdf['Tech Float'].astype(str) + ' (' + cogdf['Tech Grade'].astype(str) + ')'

if 'Preference Float' in cogdf.columns and 'Preference Grade' in cogdf.columns:
    cogdf['Preference Float and Grade'] = cogdf['Preference Float'].astype(str) + ' (' + cogdf['Preference Grade'].astype(str) + ')'

# Remove " ⭑" at the end of any IEM names
if 'Model' in cogdf.columns:
    cogdf['Model'] = cogdf['Model'].astype(str)
    cogdf['Model'] = cogdf['Model'].str.replace(' ⭑', '', regex=False)
    
    # Only apply brand filtering if Model column exists and contains valid data
    cogdf = cogdf[~cogdf['Model'].str.contains('KZ', na=False)]
    cogdf = cogdf[~cogdf['Model'].str.contains('CCA', na=False)]
    cogdf = cogdf[~cogdf['Model'].str.contains('Joyodio', na=False)]
else:
    print("Warning: Model column not found in cogdf, skipping brand filtering")

# Debug: Print shape after brand filtering
print(f"Precog data shape after brand filtering: {cogdf.shape}")

# Add list column for cogdf
cogdf['List'] = 'cog'

# Old gizdf logic (deprecated) - kept for reference
'''
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

import re
emoji_pattern = re.compile("["
                       u"\U0001F600-\U0001F64F"  # emoticons
                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                       u"\U0001F700-\U0001F77F"  # alchemical symbols
                       u"\U0001F780-\U0001F7FF"  # Geometric Shapes
                       u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                       u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                       u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                       u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                       u"\U00002702-\U000027B0"  # Dingbats
                       u"\U000024C2-\U0001F251" 
                       "]+", flags=re.UNICODE)

# Remove emojis from the Preference Float column
gizdf['Preference Float']=gizdf['Preference Float'].str.replace(emoji_pattern, '', regex=True)
gizdf['Preference Float'] = gizdf['Preference Float'].astype(float)
gizdf['Preference Grade'] = gizdf['Preference Float'].apply(lambda x: 'S+' if x>=9.0 else 'S' if x >= 8.7 else 'S-' if x >= 7.9 else 'A+' if x >= 7 else 'A' if x >= 6.5 else 'A-' if x >= 6 else 'B+' if x >= 5.5 else 'B' if x >= 5 else 'B-' if x >= 4.5 else 'C+' if x >= 4 else 'C' if x >= 3.5 else 'C-' if x >= 3 else 'D+' if x >= 2.5 else 'D' if x >= 2 else 'D-' if x >= 1.5 else 'E+' if x >= 1 else 'E' if x >= 0.5 else 'E-' if x >= 0.2 else 'F+' if x >= 0.1 else 'F')

gizdf['Normalized Float'] = gizdf['Normalized Grade'].replace({'S+':9.0, 'S':8.7, 'S-':7.9, 'A+':7, 'A':6.5, 'A-':6, 'B+':5.5, 'B':5, 'B-':4.5, 'C+':4, 'C':3.5, 'C-':3, 'D+':2.5, 'D':2, 'D-':1.5, 'E+':1, 'E':0.5, 'E-':0, 'F':0})

# Remove rows that contain 'KZ' or 'CCA' in the Model column
gizdf = gizdf[~gizdf['Model'].str.contains('KZ')]
gizdf = gizdf[~gizdf['Model'].str.contains('CCA')]

# Add list column
gizdf['List'] = 'giz'
'''

# Read Tim Tuned Ranking List (replacing deprecated gizdf)
timdf = pd.read_csv("https://docs.google.com/spreadsheets/d/1lvI0ucbqjPXZLQKzqdycBD9ZKBuMSdd0e_bPzhJpJKo/export?format=csv")

### Formatting begins here ###
# The CSV has metadata rows at the top - actual data starts on row 7+
# First, filter out rows that don't contain actual IEM data
# Find rows where RANKING column contains a valid rank (S, S-, A+, etc.)
valid_ranks = ['S+', 'S', 'S-', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E+', 'E', 'E-', 'F']
# First get column name for RANKING by index position (it's the first column)
ranking_col = timdf.columns[0]
# Filter rows with valid ranks in the first column
timdf = timdf[timdf[ranking_col].isin(valid_ranks)]
timdf = timdf.reset_index(drop=True)

# Now rename the columns - the NAME column (second column) contains the model names
timdf = timdf.rename(columns={
    timdf.columns[0]: 'Normalized Grade',  # RANKING
    timdf.columns[1]: 'Model',             # NAME
    timdf.columns[2]: 'Pros',              # PROS
    timdf.columns[3]: 'Cons',              # CONS
    timdf.columns[4]: 'Price'              # PRICE (USD)
})

# Remove rows with empty Model names (now that we've renamed)
timdf = timdf[timdf['Model'].notna()]
timdf = timdf.reset_index(drop=True)

# Clean price column
timdf['Price'] = timdf['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
timdf['Price'] = pd.to_numeric(timdf['Price'], errors='coerce')

# Create Normalized Float from the Normalized Grade
timdf['Normalized Float'] = timdf['Normalized Grade'].replace({
    'S+': 13, 'S': 12, 'S-': 11, 
    'A+': 10, 'A': 9, 'A-': 8, 
    'B+': 7, 'B': 6, 'B-': 5, 
    'C+': 4, 'C': 3, 'C-': 2, 
    'D+': 1, 'D': 0.5, 'D-': 0
})

# Extract BASS, MID, TREBLE, TECHNICAL columns if they exist
# These are likely in columns 6-9
if len(timdf.columns) > 9:
    timdf = timdf.rename(columns={
        timdf.columns[6]: 'Bass',     # BASS
        timdf.columns[7]: 'Mid',      # MID
        timdf.columns[8]: 'Treble',   # TREBLE
        timdf.columns[9]: 'Technical' # TECHNICAL
    })
    
    # Convert to float
    timdf['Tone Float'] = pd.to_numeric(timdf['Mid'], errors='coerce')
    timdf['Tech Float'] = pd.to_numeric(timdf['Technical'], errors='coerce')
else:
    # Create default values if columns don't exist
    timdf['Tone Float'] = 0
    timdf['Tech Float'] = 0

# Combine pros/cons for Comments
timdf['Comments'] = timdf['Pros'].astype(str) + ' | ' + timdf['Cons'].astype(str)
timdf['Comments'] = timdf['Comments'].str.replace('nan | nan', '', regex=False)
timdf['Comments'] = timdf['Comments'].str.replace('nan |', '', regex=False)
timdf['Comments'] = timdf['Comments'].str.replace('| nan', '', regex=False)

# Set the list identifier
timdf['List'] = 'tim'

# Read Jaytiss Ranking List 
jaytdf = pd.read_csv('https://docs.google.com/spreadsheets/d/1aBAj-f2iaNSzTCcN4yoPQyBhFiEFooM-7WM9CHUS-Cs/export?format=csv')

### Formatting begins here ###
print(f"\n=== JAYTDF DEBUG ===")
print(f"Initial jaytdf shape: {jaytdf.shape}")
print(f"Column names: {list(jaytdf.columns)}")
print(f"First few rows of column 1: {list(jaytdf.iloc[:10, 1])}")

# The CSV has header rows and metadata - find rows with actual ranking data
# Jaytiss uses rankings like S+, S, S-, A+, A, A-, etc. in the second column
valid_ranks = ['S+', 'S', 'S-', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E+', 'E', 'E-', 'F']

# Filter rows where the second column (index 1) contains valid ranks
# First convert to string and handle NaN values
jaytdf.iloc[:, 1] = jaytdf.iloc[:, 1].astype(str)
valid_rank_mask = jaytdf.iloc[:, 1].isin(valid_ranks)

print(f"Rows with valid ranks in column 1: {valid_rank_mask.sum()}")

# If no valid ranks in column 1, try column 2 (index 2)
if valid_rank_mask.sum() == 0:
    print("No valid ranks in column 1, trying column 2...")
    jaytdf.iloc[:, 2] = jaytdf.iloc[:, 2].astype(str)
    valid_rank_mask = jaytdf.iloc[:, 2].isin(valid_ranks)
    print(f"Rows with valid ranks in column 2: {valid_rank_mask.sum()}")
    rank_column = 2
else:
    rank_column = 1

jaytdf = jaytdf[valid_rank_mask]
jaytdf = jaytdf.reset_index(drop=True)

print(f"After filtering for valid ranks: {jaytdf.shape}")

# Rename columns based on structure observed in CSV
# Adjust column mapping based on which column has the ranks
if rank_column == 1:
    jaytdf = jaytdf.rename(columns={
        jaytdf.columns[0]: 'Model',           # IEM model name
        jaytdf.columns[1]: 'Normalized Grade', # Letter grade (S+, S, etc.)
        jaytdf.columns[2]: 'Normalized Float', # Overall numeric score
        jaytdf.columns[4]: 'Price',           # Price in USD
        jaytdf.columns[5]: 'Tone Float',      # Average of Bass, Mids, Highs
        jaytdf.columns[9]: 'Tech Float',      # Average of technical qualities
        jaytdf.columns[13]: 'Comments'        # Hot take/comments
    })
else:
    jaytdf = jaytdf.rename(columns={
        jaytdf.columns[0]: 'Model',           # IEM model name
        jaytdf.columns[1]: 'Normalized Float', # Overall numeric score
        jaytdf.columns[2]: 'Normalized Grade', # Letter grade (S+, S, etc.)
        jaytdf.columns[4]: 'Price',           # Price in USD
        jaytdf.columns[5]: 'Tone Float',      # Average of Bass, Mids, Highs
        jaytdf.columns[9]: 'Tech Float',      # Average of technical qualities
        jaytdf.columns[13]: 'Comments'        # Hot take/comments
    })

# Clean up the data
jaytdf = jaytdf[jaytdf['Model'].notna()]
jaytdf = jaytdf[jaytdf['Model'] != '']
jaytdf = jaytdf.reset_index(drop=True)

# Clean model names - remove numbering prefixes like "#1) ", "#2) ", etc.
jaytdf['Model'] = jaytdf['Model'].astype(str)
jaytdf['Model'] = jaytdf['Model'].str.replace(r'^#?\d+\)\s*', '', regex=True)

# Clean price column - remove $ and commas, convert to numeric
if 'Price' in jaytdf.columns:
    jaytdf['Price'] = jaytdf['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    jaytdf['Price'] = pd.to_numeric(jaytdf['Price'], errors='coerce')

# Convert score columns to numeric with error handling
jaytdf['Normalized Float'] = pd.to_numeric(jaytdf['Normalized Float'], errors='coerce')
jaytdf['Tone Float'] = pd.to_numeric(jaytdf['Tone Float'], errors='coerce') 
jaytdf['Tech Float'] = pd.to_numeric(jaytdf['Tech Float'], errors='coerce')

# Clean comments
if 'Comments' in jaytdf.columns:
    jaytdf['Comments'] = jaytdf['Comments'].fillna('').astype(str)

# Remove brand filtering (KZ, CCA, etc.) like other lists
jaytdf = jaytdf[~jaytdf['Model'].str.contains('KZ', na=False)]
jaytdf = jaytdf[~jaytdf['Model'].str.contains('CCA', na=False)]
jaytdf = jaytdf[~jaytdf['Model'].str.contains('Joyodio', na=False)]

# Debug: Print final jaytdf shape
print(f"Final jaytdf shape after processing: {jaytdf.shape}")
print(f"Sample jaytdf models: {list(jaytdf['Model'].head(10))}")

# Set the list identifier
jaytdf['List'] = 'jayt'

# Congregate all the dataframes into one dataframe
# Ensure each DataFrame has required columns before concatenation
# Note: Making Price optional since some lists might not have price data
required_columns = ['Model', 'List']  # Removed 'Price' as it's not essential for scoring
frames_list = []

# Add each DataFrame to the frames list if it has the required columns
if all(col in iefdf.columns for col in required_columns):
    print(f"Adding iefdf with {iefdf.shape[0]} rows")
    frames_list.append(iefdf)
else:
    print(f"Warning: iefdf missing required columns: {[col for col in required_columns if col not in iefdf.columns]}")

if all(col in antdf.columns for col in required_columns):
    print(f"Adding antdf with {antdf.shape[0]} rows")
    frames_list.append(antdf)
else:
    print(f"Warning: antdf missing required columns: {[col for col in required_columns if col not in antdf.columns]}")

if all(col in cogdf.columns for col in required_columns):
    print(f"Adding cogdf with {cogdf.shape[0]} rows")
    frames_list.append(cogdf)
else:
    print(f"Warning: cogdf missing required columns: {[col for col in required_columns if col not in cogdf.columns]}")

if all(col in timdf.columns for col in required_columns):
    print(f"Adding timdf with {timdf.shape[0]} rows")
    frames_list.append(timdf)
else:
    print(f"Warning: timdf missing required columns: {[col for col in required_columns if col not in timdf.columns]}")

if all(col in jaytdf.columns for col in required_columns):
    print(f"Adding jaytdf with {jaytdf.shape[0]} rows")
    frames_list.append(jaytdf)
else:
    print(f"Warning: jaytdf missing required columns: {[col for col in required_columns if col not in jaytdf.columns]}")

if not frames_list:
    print("ERROR: No dataframes meet the requirements for concatenation!")
    
frames = pd.concat(frames_list, axis=0)

# Debug: Print concatenated frames info
print(f"\n=== CONCATENATED FRAMES DEBUG ===")
print(f"Total concatenated frames: {frames.shape}")
print(f"Frames by list:")
for list_name in frames['List'].unique():
    count = len(frames[frames['List'] == list_name])
    print(f"  {list_name}: {count} rows")

# Convert 'Model' column to string
frames['Model'] = frames['Model'].astype(str)

# If 'Preference Float' column doesn't exist in some data sources, we need to handle it gracefully
# when creating compound columns or performing operations that depend on it
if 'Preference Float' in frames.columns:
    # Create a new column that is the average of the 3 scores
    frames['All Three Score'] = (frames['Normalized Float'] + frames['Tech Float'] + frames['Preference Float']) / 3
    # Create a combined score column for Tone and Preference
    frames['Tone and Preference'] = (frames['Tone Float'] + frames['Preference Float']) / 2
else:
    # If Preference Float is not available, use only the available scores
    if 'Tech Float' in frames.columns and 'Normalized Float' in frames.columns:
        frames['All Three Score'] = (frames['Normalized Float'] + frames['Tech Float']) / 2
    
    # Skip creating 'Tone and Preference' column as it requires Preference Float
    
# Remove any rows where the 'Model' column is empty
before_empty_filter = frames.shape[0]
frames = frames[frames['Model'] != 'nan']
frames = frames[frames['Model'].notna()]  # Also remove actual NaN values
frames = frames[frames['Model'] != '']  # Remove empty strings
after_empty_filter = frames.shape[0]

# Debug: Print after empty model removal
print(f"Removed {before_empty_filter - after_empty_filter} rows with empty models")
print(f"After empty model removal: {frames.shape}")

frames['Comments'] = frames['Comments'].astype(str)

# Turn "Normalized/Tone/Tech/Preference Float" columns into float type with error handling
print(f"\n=== FLOAT CONVERSION DEBUG ===")
print(f"Converting float columns - initial shape: {frames.shape}")

# Convert with error handling to prevent data loss
frames['Normalized Float'] = pd.to_numeric(frames['Normalized Float'], errors='coerce')
frames['Tone Float'] = pd.to_numeric(frames['Tone Float'], errors='coerce')
frames['Tech Float'] = pd.to_numeric(frames['Tech Float'], errors='coerce')

if 'Preference Float' in frames.columns:
    frames['Preference Float'] = pd.to_numeric(frames['Preference Float'], errors='coerce')

# Count rows with missing critical scoring data
missing_normalized = frames['Normalized Float'].isna().sum()
missing_tone = frames['Tone Float'].isna().sum()
missing_tech = frames['Tech Float'].isna().sum()

print(f"Rows with missing Normalized Float: {missing_normalized}")
print(f"Rows with missing Tone Float: {missing_tone}")  
print(f"Rows with missing Tech Float: {missing_tech}")

# Only remove rows that are missing ALL scoring data (keep partial data)
before_filter = frames.shape[0]
frames = frames[frames['Normalized Float'].notna() | frames['Tone Float'].notna() | frames['Tech Float'].notna()]
after_filter = frames.shape[0]

print(f"Removed {before_filter - after_filter} rows with no scoring data")
print(f"Remaining rows after float conversion: {after_filter}")

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
    "Fiio x Crinacle FHE Eclipse":"Fiio FHE Eclipse",
    "Blessing 3 Dusk":"Moondrop Blessing 3 Dusk",
    "Moondrop Dusk 2":"Moondrop Blessing 3 Dusk",
    "Truthear Zero Red":"Truthear Zero: Red",
    "Truthear Zero Blue":"Truthear Zero",
    "Truthear Red":"Truthear Zero: Red",
    "Truthear Blue":"Truthear Zero",
    "Truthears Hexa":"Truthear Hexa",
    "Truthear x Crinacle Zero":"Truthear Zero",
    "Truthear x Crinacle Zero Red":"Truthear Zero: Red",
    "Truthear x Crinacle Zero Blue":"Truthear Zero",
    "Truthears Zero:Red":"Truthear Zero: Red",
    "Truthears Hola":"Truthear Hola"
    }
frames['Model'] = frames['Model'].replace(name_variations)

# Debug: Print after name variations replacement
print(f"\n=== NAME PROCESSING DEBUG ===")
print(f"After name variations replacement: {frames.shape}")

# Viento jank
frames['Model'] = frames['Model'].apply(lambda x: "Hidition Viento-B" if x and ("Viento" in x) and ("B" in x) else x)

# Create a column containing the model names without the first word, as it is often the brand name.
frames['Model No Brand'] = frames['Model'].str.split(' ').str[1:].str.join(' ')

# Debug: Print before fuzzy matching
print(f"Before fuzzy matching - unique models: {len(frames['Model'].unique())}")
print(f"Sample models before fuzzy matching: {list(frames['Model'].head(10))}")

# Store original models to track changes
original_models = frames['Model'].copy()

# TOGGLE: Set to False to disable fuzzy matching for comparison
USE_FUZZY_MATCHING = True

if USE_FUZZY_MATCHING:
    def fuzz_match(row):
        model = row['Model No Brand']
        match = rapidfuzz.process.extractOne(model, frames['Model No Brand'], score_cutoff=80)
        if match is not None:
            return match[0]
        else:
            return model
    # Apply the fuzz_match function to the Model column
    frames['Model No Brand'] = frames.apply(fuzz_match, axis=1)
    # Change the everything after the first word in the Model column to the result of the fuzz_match function
    frames['Model'] = frames['Model'].str.split(' ').str[0] + ' ' + frames['Model No Brand']
    
    print("Fuzzy matching applied")
else:
    print("Fuzzy matching disabled")

# Debug: Analyze fuzzy matching changes
changed_models = frames[original_models != frames['Model']]
print(f"\n=== FUZZY MATCHING ANALYSIS ===")
print(f"Models changed by fuzzy matching: {len(changed_models)}")

if len(changed_models) > 0:
    print("Examples of fuzzy matching changes:")
    for i in range(min(10, len(changed_models))):
        idx = changed_models.index[i]
        old_name = original_models.iloc[idx]
        new_name = frames['Model'].iloc[idx]
        list_name = frames['List'].iloc[idx]
        print(f"  {list_name}: '{old_name}' -> '{new_name}'")
    
    # Check if fuzzy matching improved model overlap
    original_frames = frames.copy()
    original_frames['Model'] = original_models
    
    # Count overlaps with original names
    original_overlap_count = 0
    for model in original_frames['Model'].unique():
        lists_with_model = original_frames[original_frames['Model'] == model]['List'].nunique()
        if lists_with_model > 1:
            original_overlap_count += 1
    
    # Count overlaps with fuzzy matched names
    fuzzy_overlap_count = 0
    for model in frames['Model'].unique():
        lists_with_model = frames[frames['Model'] == model]['List'].nunique()
        if lists_with_model > 1:
            fuzzy_overlap_count += 1
    
    print(f"\nFuzzy matching impact on model overlap:")
    print(f"  Models with overlap before fuzzy matching: {original_overlap_count}")
    print(f"  Models with overlap after fuzzy matching: {fuzzy_overlap_count}")
    print(f"  Net change: {fuzzy_overlap_count - original_overlap_count}")
else:
    print("No models were changed by fuzzy matching")

# Debug: Print after fuzzy matching
print(f"After fuzzy matching - unique models: {len(frames['Model'].unique())}")
print(f"Sample models after fuzzy matching: {list(frames['Model'].head(10))}")

# reset index
frames = frames.reset_index(drop=True)

# Debug: Print total data before filtering
print(f"Total frames before filtering: {frames.shape}")

unique = frames['Model'].unique()
iefmask = frames['List'] == 'ief'
cogmask = frames['List'] == 'cog'
antmask = frames['List'] == 'ant'
timmask = frames['List'] == 'tim'
jaytmask = frames['List'] == 'jayt'

unique_ief = set(frames[iefmask]['Model']) - set(frames[~iefmask]['Model'])
unique_cog = set(frames[cogmask]['Model']) - set(frames[~cogmask]['Model'])
unique_ant = set(frames[antmask]['Model']) - set(frames[~antmask]['Model'])
unique_tim = set(frames[timmask]['Model']) - set(frames[~timmask]['Model'])
unique_jayt = set(frames[jaytmask]['Model']) - set(frames[~jaytmask]['Model'])

# Debug: Print counts of single-list models
print(f"Models only in ief: {len(unique_ief)}")
print(f"Models only in cog: {len(unique_cog)}")
print(f"Models only in ant: {len(unique_ant)}")
print(f"Models only in tim: {len(unique_tim)}")
print(f"Models only in jayt: {len(unique_jayt)}")

# Debug: Show some example models from each list to check for naming issues
print(f"\nSample ief models: {list(frames[iefmask]['Model'].head(10))}")
print(f"Sample cog models: {list(frames[cogmask]['Model'].head(10))}")
print(f"Sample ant models: {list(frames[antmask]['Model'].head(10))}")
print(f"Sample tim models: {list(frames[timmask]['Model'].head(10))}")

# Debug: Check for models that appear in multiple lists
models_in_multiple_lists = []
all_models = set(frames['Model'])
for model in all_models:
    lists_containing_model = []
    if model in set(frames[iefmask]['Model']):
        lists_containing_model.append('ief')
    if model in set(frames[cogmask]['Model']):
        lists_containing_model.append('cog')
    if model in set(frames[antmask]['Model']):
        lists_containing_model.append('ant')
    if model in set(frames[timmask]['Model']):
        lists_containing_model.append('tim')
    if model in set(frames[jaytmask]['Model']):
        lists_containing_model.append('jayt')
    
    if len(lists_containing_model) > 1:
        models_in_multiple_lists.append((model, lists_containing_model))

print(f"\n=== MODEL OVERLAP ANALYSIS ===")
print(f"Total unique models across all lists: {len(all_models)}")
print(f"Models appearing in multiple lists: {len(models_in_multiple_lists)}")
if models_in_multiple_lists:
    print("Examples of multi-list models:")
    for model, lists in models_in_multiple_lists[:10]:
        print(f"  '{model}' in {lists}")
    
    # Count models by number of lists they appear in
    overlap_counts = {}
    for model, lists in models_in_multiple_lists:
        count = len(lists)
        overlap_counts[count] = overlap_counts.get(count, 0) + 1
    
    print(f"\nModels by overlap count:")
    for count in sorted(overlap_counts.keys()):
        print(f"  {count} lists: {overlap_counts[count]} models")
else:
    print("WARNING: NO MODELS appear in multiple lists!")
    print("This suggests model name matching is failing between lists.")

# Add lists together to get all unique models (INTENTIONAL: removing models that appear in only one list)
all_unique_models = unique_ief.union(unique_cog).union(unique_ant).union(unique_tim).union(unique_jayt)

print(f"\n=== FINAL FILTERING DEBUG ===")
print(f"Models appearing in only one list (will be removed): {len(all_unique_models)}")

# Keep only models that appear in multiple lists
trimmedframes = frames[~frames['Model'].isin(all_unique_models)]

# Debug: Print final count after filtering
print(f"Final trimmed frames: {trimmedframes.shape}")
print(f"Unique models in final dataset: {len(trimmedframes['Model'].unique())}")

if len(trimmedframes['Model'].unique()) > 0:
    print(f"Final models retained: {list(trimmedframes['Model'].unique())}")
else:
    print("ERROR: No models retained after filtering!")

# Create dataframe 'combined', which has the average 'Normalized Float', 'Tone Float', 'Tech Float', 'Preference Float' for each 'Model', as well as the comments from each list.
# Use only columns that exist in the DataFrame
available_columns = ['Normalized Float', 'Tone Float', 'Tech Float']
if 'Preference Float' in frames.columns:
    available_columns.append('Preference Float')

combined = trimmedframes.groupby('Model')[available_columns].mean()
combined['Comments'] = trimmedframes.groupby('Model')['Comments'].first()
combined['List'] = trimmedframes.groupby('Model')['List'].first()
combined = combined.reset_index()

# Select only columns that exist
combined_columns = ['Model', 'Normalized Float', 'Tone Float', 'Tech Float', 'Comments', 'List']
if 'Preference Float' in combined.columns:
    combined_columns.insert(4, 'Preference Float')
combined = combined[combined_columns]

# Round values to 2 decimal places
combined['Normalized Float'] = combined['Normalized Float'].round(2)
combined['Tone Float'] = combined['Tone Float'].round(2)
combined['Tech Float'] = combined['Tech Float'].round(2)
if 'Preference Float' in combined.columns:
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
if 'Preference Float' in combined.columns:
    combined['Preference Float'] = combined['Preference Float'].astype(float)
combined['Max Comments'] = combined['Max Comments'].astype(str)
combined['maxlist'] = combined['maxlist'].astype(str)
combined['Min Comments'] = combined['Min Comments'].astype(str)
combined['minlist'] = combined['minlist'].astype(str)

# Rename columns to use camelcase because I have no foresight and I'm too lazy to change this earlier.
column_renames = {
    'Model':'model', 
    'Normalized Float':'normalizedFloat',
    'Tone Float':'toneFloat', 
    'Tech Float':'techFloat', 
    'Max Comments':'maxComments', 
    'maxlist':'maxList', 
    'Min Comments':'minComments', 
    'minlist':'minList'
}

# Add Preference Float renaming only if the column exists
if 'Preference Float' in combined.columns:
    column_renames['Preference Float'] = 'preferenceFloat'

# Apply all renamings at once
combined = combined.rename(columns=column_renames)

# For testing, export the combined dataframe to a csv file
# combined.to_csv('combined.csv', index=False)

# export the combined dataframe to a db file
print(f"\n=== DATABASE WRITING DEBUG ===")
print(f"Combined dataframe shape: {combined.shape}")
print(f"Combined dataframe columns: {list(combined.columns)}")

db_folder = 'db'
if not os.path.exists(db_folder):
    print(f"Creating db folder: {db_folder}")
    os.makedirs(db_folder)
else:
    print(f"DB folder already exists: {db_folder}")

db_path = os.path.join(db_folder, 'combined.db')
print(f"Database path: {db_path}")

# Check if file exists before writing
if os.path.exists(db_path):
    print(f"Database file exists, size: {os.path.getsize(db_path)} bytes")
else:
    print("Database file does not exist, will be created")

try:
    conn = sqlite3.connect(db_path)
    print("Successfully connected to database")
    
    # Check if table exists before replacement
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='combined';")
    table_exists = cursor.fetchone() is not None
    print(f"Table 'combined' exists before writing: {table_exists}")
    
    # Write the data
    combined.to_sql('combined', conn, if_exists='replace', index=False)
    print("Successfully wrote data to database")
    
    # Verify the write
    cursor.execute("SELECT COUNT(*) FROM combined;")
    row_count = cursor.fetchone()[0]
    print(f"Rows in database after writing: {row_count}")
    
    conn.close()
    print("Database connection closed")
    
    # Check file size after writing
    if os.path.exists(db_path):
        print(f"Database file size after writing: {os.path.getsize(db_path)} bytes")
        
except Exception as e:
    print(f"ERROR writing to database: {e}")
    import traceback
    traceback.print_exc()
    if 'conn' in locals():
        conn.close()

# Convert data to list of dictionaries (records) format
result = combined.to_dict('records')